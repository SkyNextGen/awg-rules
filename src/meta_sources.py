"""Fresh Meta feeds and bounded WhatsApp DNS inventory; no stale DNS fallback."""
from concurrent.futures import ThreadPoolExecutor, as_completed
from datetime import datetime, timezone
import csv
import io
import ipaddress
import json
import re
import time
from urllib.parse import urlencode
from urllib.request import Request, urlopen

APPROVED_ROOTS = ('whatsapp.com', 'whatsapp.net', 'whatsapp.biz', 'wa.me', 'wl.co',
                  'facebook.com', 'facebook.net', 'fbcdn.net', 'fbsbx.com')


def matches(host, roots=APPROVED_ROOTS):
    return any(host == root or host.endswith('.' + root) for root in roots)


def feed_prefixes(text, source, network, collapse, now=None):
    now = now or datetime.now(timezone.utc)
    if source['format'] == 'geofeed':
        date = re.search(r'^# Publication date: (.+)$', text, re.MULTILINE)
        if not date:
            raise ValueError('Meta geofeed publication date missing')
        published = datetime.strptime(date[1].strip(), '%a %b %d %Y').replace(tzinfo=timezone.utc)
        age = (now - published).total_seconds() / 86400
        if not 0 <= age <= source['max_age_days']:
            raise ValueError('Meta geofeed publication expired or in future')
        rows = list(csv.reader(io.StringIO(text)))
        values = []
        for row in rows:
            if not row or row[0].strip().startswith('#'):
                continue
            if len(row) < 4:
                raise ValueError('Truncated Meta geofeed row')
            values.append(str(network(row[0].strip())))
    elif source['format'] == 'cidr':
        values = [str(network(row.split('#', 1)[0].strip())) for row in text.splitlines()
                  if row.split('#', 1)[0].strip()]
    else:
        raise ValueError('Unknown Meta feed format')
    if not source['min_entries'] <= len(values) <= source['max_entries']:
        raise ValueError('Meta feed empty, truncated or excessive: ' + source['name'])
    families = {ipaddress.ip_network(p).version for p in values}
    if families != set(source['families']):
        raise ValueError('Meta feed missing/unexpected IP family: ' + source['name'])
    return collapse(values)


def collect_feeds(cfg, fetch, network, collapse):
    result = {}
    for source in cfg:
        if not source['url'].startswith('https://'):
            raise ValueError('Meta feeds require HTTPS')
        if source['name'] in result:
            raise ValueError('Duplicate Meta feed name')
        result[source['name']] = feed_prefixes(fetch(source['url']), source, network, collapse)
    return result


def dns_answer(payload, host, kind):
    """Accept only records linked to the requested question, not unrelated answers."""
    number = {'A': 1, 'AAAA': 28}[kind]
    question = payload.get('Question', [])
    if len(question) != 1 or question[0].get('name', '').lower().rstrip('.') != host or question[0].get('type') != number:
        raise ValueError('DNS question differs from requested host/family')
    status = payload.get('Status')
    if status not in (0, 3):
        raise ValueError('Temporary/invalid DNS status: ' + str(status))
    answers = payload.get('Answer', [])
    if not isinstance(answers, list) or len(answers) > 100:
        raise ValueError('Invalid DNS answer size')
    if status == 3:
        if any(a.get('type') in (1, 28) for a in answers):
            raise ValueError('NXDOMAIN with address records')
        return {'status': status, 'ips': [], 'ttl': None}
    current, seen = host, set()
    for _ in range(16):
        if current in seen:
            raise ValueError('DNS CNAME loop')
        seen.add(current)
        aliases = [a['data'].lower().rstrip('.') for a in answers
                   if a.get('type') == 5 and a.get('name', '').lower().rstrip('.') == current]
        if len(set(aliases)) > 1:
            raise ValueError('Conflicting DNS aliases')
        if not aliases:
            break
        current = aliases[0]
    else:
        raise ValueError('DNS CNAME chain too long')
    ips, ttls = set(), []
    for answer in answers:
        if answer.get('type') != number or answer.get('name', '').lower().rstrip('.') != current:
            continue
        ip = ipaddress.ip_address(answer['data'])
        if ip.version != (4 if kind == 'A' else 6) or not ip.is_global or ip.is_multicast:
            raise ValueError('Unsafe DNS address for ' + host)
        ttl = answer.get('TTL')
        if not isinstance(ttl, int) or ttl < 0:
            raise ValueError('Invalid DNS TTL')
        ips.add(str(ip)); ttls.append(ttl)
    return {'status': status, 'ips': sorted(ips), 'ttl': min(ttls) if ttls else None}


def query_dns(host, kind, endpoint):
    url = endpoint + '?' + urlencode({'name': host, 'type': kind})
    error = None
    for attempt in range(3):
        try:
            request = Request(url, headers={'User-Agent': 'awg-rules WhatsApp inventory',
                                            'Accept': 'application/dns-json'})
            with urlopen(request, timeout=10) as response:
                return dns_answer(json.load(response), host, kind)
        except Exception as exc:
            error = exc
            if attempt < 2:
                time.sleep(0.5 * (attempt + 1))
    raise RuntimeError('WhatsApp DNS failed: ' + host + ' / ' + kind + ': ' + str(error))


def collect_dns(cfg, fetch, domain, collapse, previous=None, query=query_dns):
    if cfg['resolver'] != 'https://dns.google/resolve':
        raise ValueError('Unreviewed DNS resolver')
    # Domain validation happens before filtering, so malformed source lines fail closed.
    hosts = sorted({domain(row.split('#', 1)[0].strip()) for row in fetch(cfg['hosts_url']).splitlines()
                    if row.split('#', 1)[0].strip()})
    hosts = [host for host in hosts if matches(host)]
    if not cfg['min_hosts'] <= len(hosts) <= cfg['max_hosts']:
        raise ValueError('WhatsApp host inventory empty, truncated or excessive')
    observations = {host: {} for host in hosts}
    tasks = [(host, kind) for host in hosts for kind in ('A', 'AAAA')]
    with ThreadPoolExecutor(max_workers=cfg['workers']) as executor:
        futures = {executor.submit(query, host, kind, cfg['resolver']): (host, kind)
                   for host, kind in tasks}
        try:
            for future in as_completed(futures, timeout=cfg['deadline_seconds']):
                host, kind = futures[future]
                observations[host][kind] = future.result()
        except BaseException:
            for future in futures:
                future.cancel()
            raise
    ips = {ip for row in observations.values() for family in row.values() for ip in family['ips']}
    # Run the same strict network validator used by the rest of the build.
    prefixes = collapse(ip + '/' + str(ipaddress.ip_address(ip).max_prefixlen) for ip in ips)
    resolved = sum(any(family['ips'] for family in row.values()) for row in observations.values())
    if resolved < cfg['min_resolved_hosts'] or not cfg['min_ips'] <= len(ips) <= cfg['max_ips']:
        raise ValueError('WhatsApp DNS inventory lost coverage or is excessive')
    if {ipaddress.ip_address(ip).version for ip in ips} != {4, 6}:
        raise ValueError('WhatsApp DNS inventory missing address family')
    stats = {'hosts': len(hosts), 'resolved_hosts': resolved, 'ips': len(ips),
             'ipv4': sum(ipaddress.ip_address(ip).version == 4 for ip in ips),
             'ipv6': sum(ipaddress.ip_address(ip).version == 6 for ip in ips),
             'resolver': cfg['resolver'], 'transport': 'DoH',
             'checked_at': datetime.now(timezone.utc).isoformat()}
    if previous:
        for metric in ('hosts', 'resolved_hosts', 'ips'):
            if previous.get(metric) and not cfg['min_previous_ratio'] <= stats[metric] / previous[metric] <= cfg['max_previous_ratio']:
                raise ValueError('WhatsApp DNS ' + metric + ' changed beyond safety threshold')
    return hosts, prefixes, stats, observations
