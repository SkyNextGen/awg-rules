"""Fail-closed source merger. Only promote output after official SRS compilation."""
import hashlib
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

ROOT = Path(__file__).resolve().parents[1]
UA = 'awg-rules - https://github.com/SkyNextGen/awg-rules/issues'
SHARED = {'cloudfront.net', 'akamai.net', 'akamaized.net', 'cloudflare.com', 'fastly.net', 'azureedge.net'}


def fetch(url):
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


class V2Fly:
    def __init__(self, base):
        self.base, self.cache = base, {}

    def category(self, name, stack=()):
        if not re.fullmatch(r'[a-z0-9_-]+', name):
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
    for file in ('custom-domains.txt', 'service-domains.txt'):
        domains = {domain(x) for x in lines((ROOT / 'config' / file).read_text())}
        rules['domain_suffix'].update(domains)
        report['sources'][file] = len(domains)
        source_records[file] = sorted('domain_suffix:' + d for d in domains)
    cdn = json.loads((ROOT / 'config/service-cdn.json').read_text())
    for d in cdn['domain_suffix']:
        d = domain(d)
        if d in SHARED or any(x.endswith('.' + d) for x in SHARED):
            raise ValueError('Shared CDN suffix forbidden')
        rules['domain_suffix'].add(d)
    if cdn['ip_cidr'] and not cdn.get('evidence', '').startswith('https://'):
        raise ValueError('Dedicated CDN IPs require a source URL')
    previous = json.loads((dist / 'bgp-snapshot.json').read_text()) if (dist / 'bgp-snapshot.json').exists() else {}
    asns = sorted({x for group in cfg['service_asns'].values() for x in group})
    if not set(asns) <= {62041, 62014, 59930, 44907, 211157, 32934, 63293}:
        raise ValueError('Unreviewed ASN expansion forbidden')
    snapshot = bgp(asns, previous, cfg, report)
    for asn, row in snapshot.items():
        source_records['BGP:AS' + asn] = row['prefixes']
        report['sources']['BGP:AS' + asn] = len(row['prefixes'])
    source_records['service-cdn.json'] = sorted(['domain_suffix:' + d for d in cdn['domain_suffix']] + cdn['ip_cidr'])
    report['sources']['service-cdn.json'] = len(source_records['service-cdn.json'])
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
    prefixes = collapse([p for row in snapshot.values() for p in row['prefixes']] + cdn['ip_cidr'] + custom_ips)
    merged['ip_cidr'] = prefixes
    total = len(suffix) + len(exact)
    if not cfg['min_total_domains'] <= total <= cfg['max_total_domains'] or len(prefixes) > cfg['max_prefixes']:
        raise ValueError('Output size outside safety limits')
    old = json.loads((dist / 'report.json').read_text(encoding='utf-8')) if (dist / 'report.json').exists() else {}
    for key, count in [('domains', total), ('prefixes', len(prefixes))]:
        if old.get(key) and not cfg['min_previous_ratio'] <= count / old[key] <= cfg['max_previous_ratio']:
            raise ValueError(key + ' changed beyond safety threshold')
    payload = {'version': 1, 'rules': [merged]}
    (staging / 'routing.json').write_text(json.dumps(payload, indent=2, ensure_ascii=True) + '\n')
    exe = os.environ.get('SING_BOX', 'sing-box')
    subprocess.run([exe, 'rule-set', 'compile', '--output', str(staging / 'routing.srs'), str(staging / 'routing.json')], check=True)
    subprocess.run([exe, 'rule-set', 'decompile', '--output', str(staging / 'roundtrip.json'), str(staging / 'routing.srs')], check=True)
    roundtrip = json.loads((staging / 'roundtrip.json').read_text())
    def canonical(obj):
        return {k: sorted(v if isinstance(v, list) else [v]) for k, v in obj['rules'][0].items() if k != 'type'}
    if canonical(roundtrip) != canonical(payload):
        raise ValueError('SRS round-trip differs from JSON')
    report.update(domains=total, prefixes=len(prefixes), ipv4=sum(network(p).version == 4 for p in prefixes), ipv6=sum(network(p).version == 6 for p in prefixes), asns=snapshot, matchers={k: len(v) for k, v in merged.items()})
    report['sha256'] = {f: hashlib.sha256((staging / f).read_bytes()).hexdigest() for f in ('routing.json', 'routing.srs')}
    (staging / 'bgp-snapshot.json').write_text(json.dumps(snapshot, indent=2) + '\n')
    write_report(report, payload, source_records, staging, dist, old)
    dist.mkdir(exist_ok=True)
    for f in ('routing.json', 'routing.srs', 'report.json', 'report.md', 'bgp-snapshot.json', 'source-snapshot.json', 'history.json', 'tg_message.txt'):
        shutil.copyfile(staging / f, dist / f)
    print(f'Build OK: {total} domains, {len(prefixes)} prefixes')


if __name__ == '__main__':
    try:
        build()
    except Exception as error:
        print('Build failed; published dist unchanged: ' + str(error), file=sys.stderr)
        sys.exit(1)
