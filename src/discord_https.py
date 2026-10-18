"""Bounded HTTPS fallback for Discord CDN when DNS/SNI is unavailable."""
import ipaddress
from datetime import datetime, timezone
from meta_sources import query_dns

CDN_HOSTS = frozenset((
    'cdn.discordapp.com', 'media.discordapp.net',
    'images-ext-1.discordapp.net', 'images-ext-2.discordapp.net',
))


def collect_https(cfg, domain, query=None):
    """Refresh exact public hosts; never widen DNS answers to shared CDN subnets."""
    query = query or query_dns
    hosts = [domain(value) for value in cfg['hosts']]
    if not hosts or len(hosts) != len(set(hosts)) or not set(hosts) <= CDN_HOSTS:
        raise ValueError('Unreviewed or duplicate Discord CDN host')
    if cfg['resolver'] != 'https://dns.google/resolve':
        raise ValueError('Unreviewed Discord DNS resolver')
    limit = cfg['max_ips']
    if type(limit) is not int or not 1 <= limit <= 64:
        raise ValueError('Discord CDN IP limit must be between 1 and 64')
    observations, ips = {}, set()
    for host in sorted(hosts):
        observations[host] = {}
        for kind, version in (('A', 4), ('AAAA', 6)):
            answer = query(host, kind, cfg['resolver'])
            observations[host][kind] = answer
            for value in answer['ips']:
                address = ipaddress.ip_address(value)
                if address.version != version or not address.is_global or address.is_multicast:
                    raise ValueError('Unsafe Discord CDN DNS address: ' + value)
                ips.add(address)
            if len(ips) > limit:
                raise ValueError('Discord CDN DNS inventory is excessive')
        if not any(answer['ips'] for answer in observations[host].values()):
            raise ValueError('Discord CDN host has no public address: ' + host)
    # Keep /32 and /128 even when adjacent hosts could be collapsed.
    prefixes = [str(ip) + '/' + str(ip.max_prefixlen)
                for ip in sorted(ips, key=lambda ip: (ip.version, int(ip)))]
    rule = {'network': ['tcp', 'udp'], 'ip_cidr': prefixes, 'port': [443]}
    stats = {'checked_at': datetime.now(timezone.utc).isoformat(),
             'resolver': cfg['resolver'], 'transport': 'DoH',
             'ips': len(ips), 'ipv4': sum(ip.version == 4 for ip in ips),
             'ipv6': sum(ip.version == 6 for ip in ips), 'observations': observations}
    return rule, stats


def verify_https(payload, prefixes):
    """Require the exact scoped rule, not an unrestricted or widened substitute."""
    expected = {'network': ['tcp', 'udp'], 'ip_cidr': prefixes, 'port': [443]}
    if expected not in payload['rules']:
        raise ValueError('Discord CDN HTTPS conditions differ from DNS snapshot')
