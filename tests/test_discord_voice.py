import copy
import ipaddress
import json
from pathlib import Path
import sys
import unittest
import tempfile
from unittest.mock import Mock, patch
from datetime import datetime, timedelta, timezone

sys.path.insert(0, str(Path(__file__).parents[1] / 'src'))
import build as b
from check_itdog import check_publication, publication_warnings
from routing_rules import scoped_rules, unrestricted

UPSTREAM = {'version': 3, 'rules': [
    {'domain_suffix': ['discord.com']},
    {'network': 'udp', 'ip_cidr': ['104.16.0.0/12', '66.22.192.0/18'], 'port_range': '50000:65535'},
    {'network': 'udp', 'ip_cidr': '104.16.0.0/12', 'port_range': '19000:20000'},
]}


class DiscordVoice(unittest.TestCase):
    def run_source(self, source=UPSTREAM, v6='2606:4700::/32', v4='104.16.0.0/12\n66.22.192.0/18'):
        cfg = {'rule_source': 'rules', 'ipv4_url': 'v4', 'ipv6_url': 'v6'}
        with patch.object(b, 'published_discord_rules', return_value=source), patch.object(
                b, 'fetch', side_effect={'v4': v4, 'v6': v6}.__getitem__):
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
        for mutation in ({'network': 'tcp'}, {'port_range': '1:65535'},
                         {'ip_cidr': '0.0.0.0/0'}, {'ip_cidr': '104.16.0.0/13'}):
            source = copy.deepcopy(UPSTREAM)
            source['rules'][1].update(mutation)
            with self.subTest(mutation=mutation), self.assertRaises(ValueError):
                self.run_source(source)
        for key in ('network', 'port_range'):
            source = copy.deepcopy(UPSTREAM)
            source['rules'][1].pop(key)
            with self.assertRaises(ValueError):
                self.run_source(source)
        with self.assertRaises(ValueError):
            self.run_source(v6='1.1.1.0/24')
        with self.assertRaises(ValueError):
            self.run_source(v4='104.16.0.0/12\n66.22.192.0/19')

    def test_rule_order_and_scalar_or_list_encoding_do_not_matter(self):
        source = copy.deepcopy(UPSTREAM)
        source['rules'].reverse()
        for rule in source['rules']:
            for key in ('network', 'port_range'):
                if key in rule:
                    rule[key] = [rule[key]]
        self.assertEqual(self.run_source(source), self.run_source())

    def test_rejects_added_logical_or_unrestricted_rules(self):
        for rule in ({'ip_cidr': ['66.22.192.0/18']},
                     {'type': 'logical', 'mode': 'or', 'rules': []}):
            source = copy.deepcopy(UPSTREAM)
            source['rules'][1] = rule
            with self.assertRaises(ValueError):
                self.run_source(source)

    def test_release_is_verified_and_decompiled_with_the_pinned_binary(self):
        release = {'tag_name': 'test', 'published_at': datetime.now(timezone.utc).isoformat(),
                   'assets': [{'name': 'discord.srs', 'size': 429}]}
        def decompile(args, **kwargs):
            Path(args[args.index('--output') + 1]).write_text(json.dumps(UPSTREAM))
        with patch.object(b, 'fetch', return_value=json.dumps(release)), patch.object(
                b, 'verified_asset', return_value=b'SRS') as asset, patch.object(
                b.subprocess, 'run', side_effect=decompile) as run:
            self.assertEqual(b.published_discord_rules({'rule_source': 'release'}), UPSTREAM)
        asset.assert_called_once_with('itdoginfo/allow-domains', 'test', 'discord.srs', release=release)
        self.assertEqual(run.call_args.args[0][1:3], ['rule-set', 'decompile'])
        self.assertEqual(run.call_args.kwargs['timeout'], 30)
        for date in (datetime.now(timezone.utc) - timedelta(days=9),
                     datetime.now(timezone.utc) + timedelta(days=1)):
            release['published_at'] = date.isoformat()
            with patch.object(b, 'fetch', return_value=json.dumps(release)), patch.object(
                    b, 'verified_asset') as asset, self.assertRaises(ValueError):
                b.published_discord_rules({'rule_source': 'release'})
            asset.assert_not_called()

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

    def test_voice_port_validation_is_shared_and_keeps_bands_bounded(self):
        for ranges in (['19200:19400'], ['19000:20000', '50000:65535']):
            b.verify_voice_ports(ranges)
        for ranges in ([], ['1:65535'], ['443:443'], ['20000:50000'], ['50099:50000'], [True]):
            with self.subTest(ranges=ranges), self.assertRaises(ValueError):
                b.verify_voice_ports(ranges)

    def test_ndms_does_not_flatten_shared_voice_prefixes(self):
        rules = b.custom_discord_voice(self.path)
        payload = {'version': 1, 'rules': [{'domain_suffix': ['discord.com']}] + rules}
        text, summary = b.ndms_text(payload, '2026-10-18T00:00:00+00:00')
        self.assertEqual(summary['excluded_scoped_rules'], len(rules))
        self.assertEqual(b.lines(text), ['discord.com'])


class UpstreamReadiness(unittest.TestCase):
    def test_previous_week_success_survives_a_failed_new_publication(self):
        now = datetime(2026, 11, 17, 2, 57, tzinfo=timezone.utc)
        previous = [dict(path='.github/workflows/' + name, event='schedule', head_branch='main',
                         created_at='2026-11-09T17:18:16Z', updated_at='2026-11-09T17:18:56Z',
                         status='completed', conclusion='success')
                    for name in ('create-lists.yml', 'create-subnets.yml')]
        failed = dict(previous[1], created_at='2026-11-16T17:02:00Z',
                      updated_at='2026-11-16T17:03:00Z', conclusion='failure')
        self.assertEqual(len(publication_warnings(previous + [failed], now)), 2)
        warnings = publication_warnings(previous + [failed], datetime(2026, 11, 18, tzinfo=timezone.utc))
        self.assertEqual(len(warnings), 2)
        self.assertTrue(any('за последние 8 дней' in message for message in warnings))

    def test_fresh_success_is_quiet_and_workflow_failures_are_advisory(self):
        now = datetime(2026, 10, 5, 20, 17, tzinfo=timezone.utc)
        runs = [dict(path='.github/workflows/' + p, event='schedule', head_branch='main',
                     created_at='2026-10-05T17:18:16Z', updated_at='2026-10-05T17:18:56Z',
                     status='completed', conclusion='success')
                for p in ('create-lists.yml', 'create-subnets.yml')]
        self.assertEqual(publication_warnings(runs, now), [])
        for field, value in (('conclusion', 'failure'), ('status', 'in_progress'),
                             ('created_at', '2026-09-21T17:18:16Z'),
                             ('updated_at', '2026-10-05T20:16:56Z')):
            changed = copy.deepcopy(runs)
            changed[1][field] = value
            self.assertEqual(len(publication_warnings(changed, now)), 1)
        self.assertEqual(len(publication_warnings(runs[:1], now)), 1)

    def test_november_18_failed_subnets_do_not_block_valid_sources(self):
        now = datetime(2026, 11, 18, 2, 27, 54, tzinfo=timezone.utc)
        common = dict(event='schedule', head_branch='main', status='completed')
        runs = [
            dict(common, path='.github/workflows/create-lists.yml', conclusion='success',
                 created_at='2026-11-16T18:48:01Z', updated_at='2026-11-16T18:48:54Z'),
            dict(common, path='.github/workflows/create-subnets.yml', conclusion='failure',
                 created_at='2026-11-16T17:02:26Z', updated_at='2026-11-16T17:03:19Z'),
            dict(common, path='.github/workflows/create-subnets.yml', conclusion='success',
                 created_at='2026-11-09T17:30:40Z', updated_at='2026-11-09T17:31:15Z')]
        messages = check_publication(lambda url: json.dumps({'workflow_runs': runs}), now)
        self.assertEqual(len(messages), 1)
        self.assertEqual(messages[0], 'У ITDog за последние 8 дней не было успешного обновления списка IP-подсетей. '
                         'Последняя попытка завершилась ошибкой. Сами списки проверяются отдельно.')

    def test_metadata_outage_or_invalid_response_is_only_a_warning(self):
        now = datetime(2026, 11, 18, tzinfo=timezone.utc)
        for error in (OSError('timeout'), RuntimeError('API unavailable')):
            with self.subTest(error=error), patch('check_itdog.json.loads') as decode:
                fetch = Mock(side_effect=error)
                with self.assertLogs(level='WARNING'):
                    self.assertIn('Не удалось проверить', check_publication(fetch, now)[0])
                decode.assert_not_called()
        for payload in ('invalid JSON', '{}', '{"workflow_runs": null}'):
            with self.assertLogs(level='WARNING'):
                self.assertIn('Не удалось проверить', check_publication(lambda url: payload, now)[0])

