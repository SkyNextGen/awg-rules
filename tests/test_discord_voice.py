import copy
import json
from pathlib import Path
import sys
import unittest
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

