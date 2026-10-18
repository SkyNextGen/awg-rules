"""Post-build coverage checks against fresh sources and the generated service sets."""
import ipaddress
import json
from pathlib import Path
from routing_rules import MATCH_KEYS, scoped_rules, unrestricted
from build import verify_ndms, custom_discord_voice
from discord_https import verify_https

ROOT = Path(__file__).resolve().parents[1]
HOSTS = (
    'discord.com', 'gateway.discord.gg', 'cdn.discordapp.com',
    'media.discordapp.net', 'images-ext-1.discordapp.net', 'images-ext-2.discordapp.net',
    'voice-region.discord.media', 'nexusmods.com', 'api.nexusmods.com',
    'users.nexusmods.com', 'staticdelivery.nexusmods.com', 'files.nexus-cdn.com',
    'supporter-files.nexus-cdn.com', 'premium-files.nexus-cdn.com',
    'signal.art', 'signal.group', 'signal.link', 'signal.me', 'signal.tube',
    'signal.org', 'signalusers.org', 'whispersystems.org',
    'telegram.org', 't.me', 'whatsapp.com', 'whatsapp.net', 'wa.me',
    'mmg.whatsapp.net', 'mmg-fallback.whatsapp.net', 'g-fallback.whatsapp.net',
    'lookaside.fbsbx.com', 'media.fopo2-2.fna.whatsapp.net',
    'gameloft.com', 'asphalt9.assets.gameloft.com', 'vgold.gameloft.com',
    'asphaltlegends.com', 'asphaltlegendsunite.com', 'gameloft.helpshift.com',
)


def covered_suffix(value, suffixes):
    return any(value == suffix or value.endswith('.' + suffix) for suffix in suffixes)


def covers_network(value, prefixes):
    wanted = ipaddress.ip_network(value)
    return any(wanted.version == net.version and wanted.subnet_of(net)
               for net in map(ipaddress.ip_network, prefixes))


def verify(root=ROOT):
    payload = json.loads((root / 'dist/routing.json').read_text(encoding='utf-8'))
    verify_ndms((root / 'dist/routing.txt').read_text(encoding='utf-8'), payload)
    snapshot = json.loads((root / 'dist/source-snapshot.json').read_text(encoding='utf-8'))
    base = unrestricted(payload)
    for host in HOSTS:
        if not covered_suffix(host, base['domain_suffix']):
            raise ValueError('Missing generated service coverage: ' + host)
    # BGP routes include connections without an observable DNS name or TLS SNI.
    for prefix in snapshot['BGP:AS11807']:
        if not covers_network(prefix, base['ip_cidr']):
            raise ValueError('Gameloft BGP prefix missing from final output: ' + prefix)
    upstream_suffixes = {
        value.split(':', 1)[1] for name, values in snapshot.items()
        if name == 'itdog' or name.startswith(('v2fly:', 'ITDog:service:', 'WhatsApp:cdn-hosts'))
        for value in values if value.startswith('domain_suffix:')}
    custom = [value.split('#', 1)[0].strip()
              for value in (root / 'config/custom-domains.txt').read_text(encoding='utf-8').splitlines()]
    overlaps = [value for value in custom if value and covered_suffix(value, upstream_suffixes)]
    # Notify when a personal addition has become redundant; do not silently rewrite user config.
    if overlaps:
        print('Custom domains now covered by upstream: ' + ', '.join(sorted(overlaps)))
    for service in ('telegram', 'whatsapp', 'discord'):
        data = json.loads((root / ('dist/custom/' + service + '.json')).read_text(encoding='utf-8'))
        if not data['rules']:
            raise ValueError('Empty generated service set: ' + service)
        for rule in data['rules']:
            for suffix in rule.get('domain_suffix', []):
                if not covered_suffix(suffix, base['domain_suffix']):
                    raise ValueError('Service domain missing from final output: ' + suffix)
            if set(rule) - set(MATCH_KEYS):
                if service != 'discord' or rule not in scoped_rules(payload):
                    raise ValueError('Scoped service conditions differ from final output')
                continue
            for prefix in rule.get('ip_cidr', []):
                if not covers_network(prefix, base['ip_cidr']):
                    raise ValueError('Service IP missing from final output: ' + prefix)
        if service != 'discord' and not unrestricted(data)['ip_cidr']:
            raise ValueError('Missing generated service IPs: ' + service)
    if 'Discord:cdn-dns:https' in snapshot:
        prefixes = snapshot['Discord:cdn-dns:https']
        verify_https(payload, prefixes)
        discord = json.loads((root / 'dist/custom/discord.json').read_text(encoding='utf-8'))
        verify_https(discord, prefixes)
    cfg = json.loads((root / 'config/sources.json').read_text(encoding='utf-8'))
    custom_voice = cfg['discord_voice'].get('custom_rules_file')
    if custom_voice:
        discord = json.loads((root / 'dist/custom/discord.json').read_text(encoding='utf-8'))
        for rule in custom_discord_voice(root / custom_voice):
            if rule not in scoped_rules(payload) or rule not in scoped_rules(discord):
                raise ValueError('Custom Discord UDP coverage missing or constraints changed')
    telegram = json.loads((root / 'dist/custom/telegram.json').read_text(encoding='utf-8'))
    for prefix in snapshot['telegram:official-cidr']:
        if not covers_network(prefix, unrestricted(telegram)['ip_cidr']):
            raise ValueError('Official Telegram prefix missing from generated source: ' + prefix)
    whatsapp = unrestricted(json.loads((root / 'dist/custom/whatsapp.json').read_text(encoding='utf-8')))
    for name, prefixes in snapshot.items():
        if name.startswith('Meta:') or name == 'WhatsApp:cdn-dns':
            for prefix in prefixes:
                if not covers_network(prefix, whatsapp['ip_cidr']):
                    raise ValueError('Meta/CDN IP missing from WhatsApp source: ' + prefix)
    dns_file = root / 'dist/whatsapp-dns.json'
    if 'WhatsApp:cdn-dns' in snapshot:
        dns = json.loads(dns_file.read_text(encoding='utf-8'))
        report = json.loads((root / 'dist/report.json').read_text(encoding='utf-8'))
        if dns['summary'] != report['whatsapp_dns']:
            raise ValueError('WhatsApp DNS snapshot and report differ')
        for host, row in dns['observations'].items():
            if not covered_suffix(host, base['domain_suffix']):
                raise ValueError('WhatsApp observed host missing from output: ' + host)
            for family in row.values():
                for ip in family['ips']:
                    address = ipaddress.ip_address(ip)
                    if not covers_network(str(address) + '/' + str(address.max_prefixlen), base['ip_cidr']):
                        raise ValueError('WhatsApp observed IP missing from output: ' + ip)
    print('Service coverage OK: Gameloft domains/BGP, Discord media/HTTPS/UDP, Nexus, Signal, Telegram official CIDR and all custom service sets')


if __name__ == '__main__':
    verify()


