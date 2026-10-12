"""Fail-closed source merger. Only promote output after official SRS compilation."""
import hashlib
import ast
import ipaddress
import json
import os
from pathlib import Path
import re
import shutil
import subprocess
import sys
import time
from datetime import datetime, timezone
from urllib.request import Request, urlopen
from report import records, write_report
from routing_rules import split_rule

ROOT = Path(__file__).resolve().parents[1]
UA = 'awg-rules - https://github.com/SkyNextGen/awg-rules/issues'


def fetch(url):
    cache = os.environ.get('SOURCE_CACHE')
    if cache:
        path = Path(cache) / (hashlib.sha256(url.encode()).hexdigest() + '.txt')
        manifest = json.loads((Path(cache) / 'manifest.json').read_text(encoding='utf-8'))
        timestamp = datetime.fromisoformat(manifest['fetched_at'].replace('Z', '+00:00'))
        age = (datetime.now(timezone.utc) - timestamp).total_seconds()
        expected = {row['url']: row['sha256'] for row in manifest['sources']}
        value = path.read_bytes()
        if not 0 <= age <= 86400 or hashlib.sha256(value).hexdigest() != expected.get(url):
            raise ValueError('Expired or corrupted local source cache: ' + url)
        return value.decode('utf-8')
    for attempt in range(3):
        try:
            with urlopen(Request(url, headers={'User-Agent': UA}), timeout=60) as response:
                return response.read().decode('utf-8')
        except Exception:
            if attempt == 2:
                raise RuntimeError('Source fetch failed: ' + url) from None
            time.sleep(2 ** attempt)


def lines(text):
    return [x.split('#', 1)[0].strip() for x in text.splitlines() if x.split('#', 1)[0].strip()]


def domain(value, allow_tld=False):
    value = value.lower().rstrip('.').removeprefix('*.')
    value = value.encode('idna').decode('ascii')
    if len(value) > 253 or ('.' not in value and not allow_tld) or any(not re.fullmatch(r'[a-z0-9](?:[a-z0-9-]{0,61}[a-z0-9])?', x) for x in value.split('.')):
        raise ValueError('Invalid domain: ' + value)
    try:
        ipaddress.ip_address(value)
    except ValueError:
        return value
    raise ValueError('IP in domain source')


def network(value):
    n = ipaddress.ip_network(value, strict=True)
    if n.prefixlen < (8 if n.version == 4 else 19) or not n.network_address.is_global or not n.broadcast_address.is_global:
        raise ValueError('Unsafe network: ' + value)
    return n


def collapse(values):
    nets = [network(x) for x in values]
    return [str(n) for v in (4, 6) for n in ipaddress.collapse_addresses(n for n in nets if n.version == v)]


def prune(values):
    keep = set()
    for d in sorted(set(values), key=lambda x: (x.count('.'), x)):
        if not any('.'.join(d.split('.')[i:]) in keep for i in range(1, len(d.split('.')))):
            keep.add(d)
    return sorted(keep)


def service_prefixes(source):
    """Fetch a fresh, bounded service-specific CIDR list; never widen DNS/CDN IPs."""
    if not source['url'].startswith('https://'):
        raise ValueError('Service IP source must use HTTPS')
    values = lines(fetch(source['url']))
    if not source['min_prefixes'] <= len(values) <= source['max_prefixes']:
        raise ValueError('Service IP source empty, truncated or excessive')
    prefixes = collapse(values)
    if {network(p).version for p in prefixes} != {4, 6}:
        raise ValueError('Service IP source missing address family')
    return prefixes


def discord_voice(cfg):
    """Preserve ITDog's network AND CIDR AND destination-port semantics."""
    source = cfg['rule_source']
    tree = ast.parse(fetch(source))
    calls = [n for n in ast.walk(tree) if isinstance(n, ast.Call)
             and isinstance(n.func, ast.Name) and n.func.id == 'srs_rule'
             and len(n.args) == 2 and isinstance(n.args[0], ast.Constant)
             and n.args[0].value == 'discord']
    if len(calls) != 1 or not isinstance(calls[0].args[1], ast.List):
        raise ValueError('Discord upstream rule structure changed')
    ports = {}
    for item in calls[0].args[1].elts:
        if not isinstance(item, ast.Dict):
            raise ValueError('Unexpected Discord rule')
        values = {ast.literal_eval(k): v for k, v in zip(item.keys, item.values)}
        if 'ip_cidr' not in values:
            continue
        if set(values) != {'network', 'ip_cidr', 'port_range'} or ast.literal_eval(values['network']) != ['udp']:
            raise ValueError('Discord rule must retain UDP and port restrictions')
        name = values['ip_cidr']
        if not isinstance(name, ast.Name) or name.id not in {'discord_subnets', 'discord_cf_subnets'}:
            raise ValueError('Unexpected Discord subnet source')
        ranges = ast.literal_eval(values['port_range'])
        if not isinstance(ranges, list) or not ranges:
            raise ValueError('Missing Discord ports')
        for value in ranges:
            if not re.fullmatch(r'\d+:\d+', value):
                raise ValueError('Invalid Discord port range')
            lo, hi = map(int, value.split(':'))
            if not 1 <= lo <= hi <= 65535 or (lo == 1 and hi == 65535):
                raise ValueError('Unsafe Discord ports')
        ports[name.id] = ranges
    if set(ports) != {'discord_subnets', 'discord_cf_subnets'}:
        raise ValueError('Missing Discord scoped upstream rules')
    prefixes = []
    for family in (4, 6):
        values = lines(fetch(cfg['ipv' + str(family) + '_url']))
        if not values or len(values) > 2000 or any(network(p).version != family for p in values):
            raise ValueError('Invalid Discord IPv' + str(family) + ' source')
        prefixes.extend(values)
    assignments = [n for n in ast.walk(tree) if isinstance(n, ast.Assign)
                   and any(isinstance(t, ast.Name) and t.id == 'discord_cf_subnets' for t in n.targets)]
    if len(assignments) != 1:
        raise ValueError('Missing Discord Cloudflare source')
    cloudflare = collapse(ast.literal_eval(assignments[0].value))
    if cloudflare != ['104.16.0.0/12']:
        raise ValueError('Discord Cloudflare prefixes changed; review required')
    return [dict(network=['udp'], ip_cidr=collapse(prefixes), port_range=ports['discord_subnets']),
            dict(network=['udp'], ip_cidr=cloudflare, port_range=ports['discord_cf_subnets'])]


class V2Fly:
    def __init__(self, base):
        self.base, self.cache = base, {}

    def category(self, name, stack=()):
        if not re.fullmatch(r'[a-z0-9_!-]+', name):
            raise ValueError('Invalid category')
        if name in stack:
            raise ValueError('V2Fly include cycle')
        if name in self.cache:
            return self.cache[name]
        out = {'domain': set(), 'domain_suffix': set(), 'domain_keyword': set(), 'domain_regex': set()}
        for line in lines(fetch(self.base + name)):
            parts = line.split()
            token, attrs = parts[0], set(parts[1:])
            kind, sep, value = token.partition(':')
            if not sep:
                kind, value = 'domain', token
            if kind == 'include':
                included = self.category(value, stack + (name,))
                # Attribute-filtered includes must preserve their upstream semantics.
                if attrs:
                    raise ValueError('Unsupported attribute-filtered include: ' + line)
                for k in out:
                    out[k].update(included[k])
            elif kind in ('domain', 'full'):
                out['domain' if kind == 'full' else 'domain_suffix'].add(domain(value, allow_tld=kind == 'domain'))
            elif kind in ('keyword', 'regexp'):
                if kind == 'regexp':
                    re.compile(value)
                if not value:
                    raise ValueError('Empty matcher')
                out['domain_keyword' if kind == 'keyword' else 'domain_regex'].add(value)
            else:
                raise ValueError('Unknown V2Fly record: ' + line)
        if not any(out.values()):
            raise ValueError('Empty V2Fly category: ' + name)
        self.cache[name] = out
        return out


def bgp(asns, previous, cfg, report):
    result, missing = {}, []
    now = datetime.now(timezone.utc)
    def accept(asn, prefixes, source, timestamp):
        prefixes = collapse(prefixes)
        if not prefixes or len(prefixes) > cfg['max_prefixes']:
            raise ValueError('Empty or excessive BGP response')
        # Every tracked service ASN must have both families.
        if {network(x).version for x in prefixes} != {4, 6}:
            raise ValueError('BGP response missing address family')
        old = previous.get(str(asn), {}).get('prefixes', [])
        if old and not cfg['min_previous_ratio'] <= len(prefixes) / len(old) <= cfg['max_previous_ratio']:
            raise ValueError('BGP size changed beyond safety threshold')
        result[str(asn)] = {'prefixes': prefixes, 'source': source, 'fetched_at': timestamp}
    for asn in asns:
        try:
            data = json.loads(fetch(f'https://stat.ripe.net/data/announced-prefixes/data.json?resource=AS{asn}'))
            if data['status'] != 'ok':
                raise ValueError('RIPEstat status')
            accept(asn, [x['prefix'] for x in data['data']['prefixes']], 'RIPEstat', now.isoformat())
        except Exception:
            missing.append(asn)
    if missing:
        try:
            found = {a: [] for a in missing}
            # Stream the official table once; never scrape HTML or fetch once per ASN.
            with urlopen(Request('https://bgp.tools/table.jsonl', headers={'User-Agent': UA}), timeout=120) as response:
                for line in response:
                    row = json.loads(line)
                    a = int(row['ASN'])
                    if a in found:
                        found[a].append(row['CIDR'])
            for asn in missing:
                try:
                    accept(asn, found[asn], 'bgp.tools', now.isoformat())
                    report['warnings'].append(f'AS{asn}: bgp.tools fallback')
                except Exception:
                    pass
        except Exception:
            pass
    for asn in missing:
        if str(asn) in result:
            continue
        old = previous.get(str(asn), {})
        age = (now - datetime.fromisoformat(old['fetched_at'])).total_seconds() / 86400 if old else float('inf')
        if age < 0 or age > cfg['max_snapshot_age_days']:
            raise ValueError(f'AS{asn}: no valid live data or fresh snapshot')
        accept(asn, old['prefixes'], 'snapshot', old['fetched_at'])
        report['warnings'].append(f'AS{asn}: snapshot age {age:.1f} days')
    return result


def build():
    cfg = json.loads((ROOT / 'config/sources.json').read_text())
    dist, staging = ROOT / 'dist', ROOT / '.staging'
    staging.mkdir(exist_ok=True)
    report = {'built_at': datetime.now(timezone.utc).isoformat(), 'warnings': [], 'sources': {}}
    if os.environ.get('SOURCE_CACHE'):
        report['warnings'].append('Local review build from explicitly fetched SOURCE_CACHE; not a live Python HTTP build')
    source_records = {}
    itdog = {domain(x) for x in lines(fetch(cfg['itdog_url']))}
    if len(itdog) < cfg['min_itdog_domains']:
        raise ValueError('ITDog truncated or empty')
    rules = {'domain_suffix': set(itdog), 'domain': set(), 'domain_keyword': set(), 'domain_regex': set()}
    report['sources']['itdog'] = len(itdog)
    source_records['itdog'] = sorted('domain_suffix:' + d for d in itdog)
    v2 = V2Fly(cfg['v2fly_base'])
    for cat in lines((ROOT / 'config/v2fly-categories.txt').read_text()):
        parsed = v2.category(cat)
        report['sources']['v2fly:' + cat] = sum(map(len, parsed.values()))
        source_records['v2fly:' + cat] = records(parsed)
        for k in rules:
            rules[k].update(parsed[k])
    service_sources = cfg.get('service_sources', {})
    for service, urls in sorted(service_sources.items()):
        service_records = []
        for source in urls:
            if source.get('kind') == 'v2fly':
                category = source['category']
                parsed = v2.category(category)
                for key, values in parsed.items():
                    rules[key].update(values)
                source_name = 'v2fly:' + category
                source_records[source_name] = records(parsed)
                report['sources'][source_name] = len(source_records[source_name])
            elif source.get('kind') == 'domains' and source.get('url', '').startswith('https://'):
                service_domains = {domain(x) for x in lines(fetch(source['url']))}
                if not service_domains:
                    raise ValueError('Empty custom domain source: ' + source['url'])
                rules['domain_suffix'].update(service_domains)
                source_name = 'ITDog:service:' + service
                source_records[source_name] = sorted('domain_suffix:' + d for d in service_domains)
                report['sources'][source_name] = len(source_records[source_name])
            else:
                raise ValueError('Invalid custom service source: ' + service)
            service_records.extend(source_records[source_name])
        if not service_records:
            raise ValueError('Empty custom service source: ' + service)
        report.setdefault('custom_services', {})[service] = sorted(set(service_records))
    domains = {domain(x) for x in lines((ROOT / 'config/custom-domains.txt').read_text())}
    rules['domain_suffix'].update(domains)
    report['sources']['custom-domains.txt'] = len(domains)
    source_records['custom-domains.txt'] = sorted('domain_suffix:' + d for d in domains)
    previous = json.loads((dist / 'bgp-snapshot.json').read_text()) if (dist / 'bgp-snapshot.json').exists() else {}
    asns = sorted({x for group in cfg['service_asns'].values() for x in group})
    if not set(asns) <= {62041, 62014, 59930, 44907, 211157, 32934, 63293}:
        raise ValueError('Unreviewed ASN expansion forbidden')
    snapshot = bgp(asns, previous, cfg, report)
    for asn, row in snapshot.items():
        source_records['BGP:AS' + asn] = row['prefixes']
        report['sources']['BGP:AS' + asn] = len(row['prefixes'])
    live_service_ips = {}
    for service, source in cfg.get('service_ip_sources', {}).items():
        if service not in service_sources:
            raise ValueError('Unknown service IP source: ' + service)
        live_service_ips[service] = service_prefixes(source)
        source_name = service + ':official-cidr'
        source_records[source_name] = live_service_ips[service]
        report['sources'][source_name] = len(live_service_ips[service])
    service_ip_groups = cfg.get('custom_service_asn_groups', {})
    for service, group in service_ip_groups.items():
        if service not in service_sources or group not in cfg['service_asns']:
            raise ValueError('Unknown custom service ASN mapping: ' + service)
    for service in service_sources:
        group_asns = cfg['service_asns'].get(service_ip_groups.get(service), [])
        values = live_service_ips.get(service, []) + [
            p for asn in group_asns for p in snapshot[str(asn)]['prefixes']]
        report['custom_services'][service] = sorted(set(report['custom_services'][service] +
            ['ip_cidr:' + p for p in collapse(values)]))
    suffix = prune(rules['domain_suffix'])
    exact = sorted(d for d in rules['domain'] if not any(d == x or d.endswith('.' + x) for x in suffix))
    merged = {k: sorted(v) for k, v in rules.items() if v}
    merged['domain_suffix'] = suffix
    if exact:
        merged['domain'] = exact
    else:
        merged.pop('domain', None)
    custom_ips = lines((ROOT / 'config/custom-ip-cidrs.txt').read_text())
    report['sources']['custom-ip-cidrs.txt'] = len(custom_ips)
    source_records['custom-ip-cidrs.txt'] = sorted(set(custom_ips))
    prefixes = collapse([p for row in snapshot.values() for p in row['prefixes']] + custom_ips + [p for values in live_service_ips.values() for p in values])
    merged['ip_cidr'] = prefixes
    total = len(suffix) + len(exact)
    if not cfg['min_total_domains'] <= total <= cfg['max_total_domains'] or len(prefixes) > cfg['max_prefixes']:
        raise ValueError('Output size outside safety limits')
    old = json.loads((dist / 'report.json').read_text(encoding='utf-8')) if (dist / 'report.json').exists() else {}
    added_sources = set(report['sources']) - set(old.get('sources', {}))
    for key, count in [('domains', total), ('prefixes', len(prefixes))]:
        max_ratio = cfg.get('max_source_expansion_ratio', cfg['max_previous_ratio']) if key == 'domains' and added_sources else cfg['max_previous_ratio']
        if old.get(key) and not cfg['min_previous_ratio'] <= count / old[key] <= max_ratio:
            raise ValueError(key + ' changed beyond safety threshold')
    scoped = discord_voice(cfg['discord_voice'])
    source_records['ITDog:discord:scoped-udp'] = [json.dumps(r, sort_keys=True) for r in scoped]
    report['sources']['ITDog:discord:scoped-udp'] = len(scoped)
    report['scoped_rules'] = scoped
    report['limitations'] = [
        'Ежедневная пересборка получает проверяемые upstream-источники, но не обнаруживает автоматически все новые домены в интернете. WhatsApp использует общие сети Meta, а не отдельный полный реестр WhatsApp-IP.',
        'Discord: голосовые IP меняются; покрытие IPv6 для UDP 19000–20000 не подтверждено. '
        'Общие подсети ограничены UDP-портами, но могут захватывать сторонний трафик на тех же портах.'
    ]
    payload = {'version': 1, 'rules': split_rule(merged) + scoped}
    (staging / 'routing.json').write_text(json.dumps(payload, indent=2, ensure_ascii=True) + '\n')
    exe = os.environ.get('SING_BOX', 'sing-box')
    subprocess.run([exe, 'rule-set', 'compile', '--output', str(staging / 'routing.srs'), str(staging / 'routing.json')], check=True)
    subprocess.run([exe, 'rule-set', 'decompile', '--output', str(staging / 'roundtrip.json'), str(staging / 'routing.srs')], check=True)
    roundtrip = json.loads((staging / 'roundtrip.json').read_text())
    def canonical(obj):
        return [{k: sorted(v if isinstance(v, list) else [v]) for k, v in rule.items() if k != 'type'} for rule in obj['rules']]
    if canonical(roundtrip) != canonical(payload):
        raise ValueError('SRS round-trip differs from JSON')
    report.update(domains=total, prefixes=len(prefixes), ipv4=sum(network(p).version == 4 for p in prefixes), ipv6=sum(network(p).version == 6 for p in prefixes), asns=snapshot, matchers={k: len(v) for k, v in merged.items()})
    report['sha256'] = {f: hashlib.sha256((staging / f).read_bytes()).hexdigest() for f in ('routing.json', 'routing.srs')}
    custom_stage = staging / 'custom'
    custom_stage.mkdir(exist_ok=True)
    for service, entries in report['custom_services'].items():
        service_rule = {}
        for entry in entries:
            key, value = entry.split(':', 1)
            service_rule.setdefault(key, []).append(value)
        service_rules = split_rule(service_rule) + (scoped if service == 'discord' else [])
        (custom_stage / (service + '.json')).write_text(json.dumps({'version': 1, 'rules': service_rules}, indent=2) + '\n', encoding='utf-8')
    (staging / 'bgp-snapshot.json').write_text(json.dumps(snapshot, indent=2) + '\n')
    write_report(report, payload, source_records, staging, dist, old)
    dist.mkdir(exist_ok=True)
    for f in ('routing.json', 'routing.srs', 'report.json', 'report.md', 'bgp-snapshot.json', 'source-snapshot.json', 'history.json', 'tg_message.txt'):
        shutil.copyfile(staging / f, dist / f)
    shutil.copytree(custom_stage, dist / 'custom', dirs_exist_ok=True)
    print(f'Build OK: {total} domains, {len(prefixes)} prefixes')


if __name__ == '__main__':
    try:
        build()
    except Exception as error:
        print('Build failed; published dist unchanged: ' + str(error), file=sys.stderr)
        sys.exit(1)

