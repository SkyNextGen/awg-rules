import copy
import ipaddress
import json
from pathlib import Path
import sys
import unittest
import tempfile
from unittest.mock import patch
from datetime import datetime, timezone

sys.path.insert(0, str(Path(__file__).parents[1] / 'src'))
import build as b
from check_itdog import verify
from routing_rules import scoped_rules, unrestricted

UPSTREAM = '''
discord_cf_subnets = ["104.16.0.0/12"]
srs_rule('discord', [
 {"domain_suffix": discord_domains},
 {"network": ["udp"], "ip_cidr": discord_subnets, "port_range": ["50000:65535"]},
 {"network": ["udp"], "ip_cidr": discord_cf_subnets, "port_range": ["19000:20000"]}])
'''


class DiscordVoice(unittest.TestCase):
    def run_source(self, source=UPSTREAM, v6='2606:4700::/32'):
        cfg = {'rule_source': 'rules', 'ipv4_url': 'v4', 'ipv6_url': 'v6'}
        with patch.object(b, 'fetch', side_effect={'rules': source, 'v4': '104.16.0.0/12\n66.22.192.0/18', 'v6': v6}.__getitem__):
            return b.discord_voice(cfg)

    def test_ports_and_network_stay_on_every_ip_rule(self):
        rules = self.run_source()
        self.assertEqual(rules[0]['port_range'], ['50000:65535'])
        self.assertEqual(rules[1]['port_range'], ['19000:20000'])
        self.assertEqual({b.network(p).version for p in rules[0]['ip_cidr']}, {4, 6})
        for rule in rules:
            self.assertEqual(rule['network'], ['udp'])
            self.assertTrue(rule['port_range'])

    def test_rejects_removed_constraints_and_changed_cidr(self):
        for source in (UPSTREAM.replace('"network": ["udp"], ', ''),
                       UPSTREAM.replace('"50000:65535"', '"1:65535"'),
                       UPSTREAM.replace('104.16.0.0/12', '0.0.0.0/0')):
            with self.assertRaises(ValueError):
                self.run_source(source)
        with self.assertRaises(ValueError):
            self.run_source(v6='1.1.1.0/24')

    def test_final_output_preserves_scopes(self):
        # If a built artifact exists, verify it cannot accidentally contain
        # Discord shared CIDRs in the unrestricted rule during refactoring.
        target = b.ROOT / 'dist/routing.json'
        if not target.exists():
            self.skipTest('No built artifact')
        payload = json.loads(target.read_text())
        if len(payload['rules']) == 1:
            self.skipTest('Pre-migration artifact')
        for rule in scoped_rules(payload):
            if rule.get('port') == [443]:
                continue
            self.assertEqual(rule['network'], ['udp'])
            self.assertTrue(rule['port_range'])
            for value in rule['ip_cidr']:
                net = b.network(value)
                self.assertFalse(any(net.overlaps(b.network(p)) for p in unrestricted(payload)['ip_cidr'] if b.network(p).version == net.version))


class CustomDiscordVoice(unittest.TestCase):
    def setUp(self):
        self.path = b.ROOT / 'config/custom-discord-voice.json'
        self.payload = json.loads(self.path.read_text(encoding='utf-8'))

    def test_new_voice_networks_and_relay_ports_are_covered(self):
        rules = b.custom_discord_voice(self.path)
        for address in ('35.224.0.1', '35.239.255.254', '35.240.0.1',
                        '35.247.255.254', '66.22.192.1', '104.29.0.1'):
            for port in (19200, 19400, 50000, 50099):
                self.assertTrue(any(
                    any(ipaddress.ip_address(address) in b.network(p) for p in rule['ip_cidr'])
                    and any(int(lo) <= port <= int(hi) for lo, hi in
                            (p.split(':') for p in rule['port_range']))
                    for rule in rules), (address, port))
        for rule in rules:
            self.assertEqual(rule['network'], ['udp'])
            for port in (443, 19199, 19401, 49999, 50100, 65535):
                self.assertFalse(any(int(lo) <= port <= int(hi) for lo, hi in
                                     (p.split(':') for p in rule['port_range'])))
            self.assertFalse(any(ipaddress.ip_address('35.248.0.1') in b.network(p)
                                 for p in rule['ip_cidr']))

    def test_rejects_unrestricted_tcp_and_unsafe_network_changes(self):
        mutations = [dict(network=['tcp']), dict(network=['tcp', 'udp']),
                     dict(port_range=['1:65535']), dict(port_range=[]),
                     dict(ip_cidr=['0.0.0.0/0']), dict(ip_cidr=['35.0.0.0/8']),
                     dict(ip_cidr=['192.168.0.0/16']), dict(ip_cidr=[])]
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / 'custom.json'
            for changes in mutations:
                payload = copy.deepcopy(self.payload)
                payload['rules'][0].update(changes)
                path.write_text(json.dumps(payload), encoding='utf-8')
                with self.subTest(changes=changes), self.assertRaises(ValueError):
                    b.custom_discord_voice(path)
            for key in ('network', 'port_range'):
                payload = copy.deepcopy(self.payload)
                payload['rules'][0].pop(key)
                path.write_text(json.dumps(payload), encoding='utf-8')
                with self.subTest(removed=key), self.assertRaises(ValueError):
                    b.custom_discord_voice(path)

    def test_ndms_does_not_flatten_shared_voice_prefixes(self):
        rules = b.custom_discord_voice(self.path)
        payload = {'version': 1, 'rules': [{'domain_suffix': ['discord.com']}] + rules}
        text, summary = b.ndms_text(payload, '2026-10-18T00:00:00+00:00')
        self.assertEqual(summary['excluded_scoped_rules'], len(rules))
        self.assertEqual(b.lines(text), ['discord.com'])


class UpstreamReadiness(unittest.TestCase):
    def test_fresh_success_both_workflows_required(self):
        now = datetime(2026, 10, 5, 20, 17, tzinfo=timezone.utc)
        runs = [dict(path='.github/workflows/' + p, event='schedule', head_branch='main',
                     created_at='2026-10-05T17:18:16Z', updated_at='2026-10-05T17:18:56Z',
                     status='completed', conclusion='success')
                for p in ('create-lists.yml', 'create-subnets.yml')]
        verify(runs, now)
        for field, value in (('conclusion', 'failure'), ('status', 'in_progress'),
                             ('created_at', '2026-09-28T17:18:16Z'),
                             ('updated_at', '2026-10-05T20:16:56Z')):
            changed = copy.deepcopy(runs)
            changed[1][field] = value
            with self.assertRaises(ValueError):
                verify(changed, now)
        with self.assertRaises(ValueError):
            verify(runs[:1], now)

