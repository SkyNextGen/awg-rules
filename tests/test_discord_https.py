"""Regression checks for HTTPS with a hidden or unavailable Discord domain."""
import copy
from pathlib import Path
import sys
import unittest

sys.path.insert(0, str(Path(__file__).parents[1] / 'src'))
import build as b
from discord_https import collect_https, verify_https
from routing_rules import unrestricted
from meta_sources import TemporaryDNSFailure


class DiscordHTTPS(unittest.TestCase):
    def cfg(self):
        return {'hosts': ['cdn.discordapp.com', 'media.discordapp.net'],
                'resolver': 'https://dns.google/resolve', 'max_ips': 64}

    def answer(self, host, kind, resolver):
        return {'status': 0, 'ips': ['162.159.134.233'] if kind == 'A' else [],
                'ttl': 300, 'resolver': resolver}

    def test_exact_ips_are_scoped_to_both_transports_and_443(self):
        rule, stats = collect_https(self.cfg(), b.domain, query=self.answer)
        self.assertEqual(rule, {'network': ['tcp', 'udp'],
                                'ip_cidr': ['162.159.134.233/32'], 'port': [443]})
        self.assertEqual(stats['ips'], 1)
        self.assertEqual(stats['ipv6'], 0)  # No invented IPv6 or required AAAA.
        self.assertEqual(stats['observations']['cdn.discordapp.com']['A']['ttl'], 300)
        self.assertIn('checked_at', stats)

    def test_adjacent_addresses_are_kept_exact_and_ipv6_is_supported(self):
        def query(host, kind, resolver):
            return {'status': 0, 'ips': ['162.159.134.232', '162.159.134.233']
                    if kind == 'A' else ['2606:4700::1111'], 'ttl': 60}
        rule, _ = collect_https(self.cfg(), b.domain, query=query)
        self.assertEqual(rule['ip_cidr'],
                         ['162.159.134.232/32', '162.159.134.233/32', '2606:4700::1111/128'])

    def test_unreviewed_host_resolver_or_limit_fails_before_network(self):
        for update in ({'hosts': ['cloudflare-ech.com']},
                       {'hosts': ['cdn.discordapp.com.evil.test']},
                       {'hosts': []},
                       {'hosts': ['cdn.discordapp.com', 'cdn.discordapp.com']},
                       {'resolver': 'http://dns.google/resolve'},
                       {'max_ips': 65}, {'max_ips': True}):
            def unexpected(*args):
                self.fail('Invalid config must not issue DNS queries')
            with self.subTest(update=update), self.assertRaises(ValueError):
                collect_https(self.cfg() | update, b.domain, query=unexpected)

    def test_temporary_failure_never_returns_partial_or_old_addresses(self):
        for kind_failed in ('A', 'AAAA'):
            def query(host, kind, resolver):
                if host == 'media.discordapp.net' and kind == kind_failed:
                    raise TemporaryDNSFailure('offline')
                return self.answer(host, kind, resolver)
            with self.subTest(kind=kind_failed), self.assertRaises(TemporaryDNSFailure):
                collect_https(self.cfg(), b.domain, query=query)

    def test_empty_host_or_excessive_inventory_blocks_build(self):
        with self.assertRaises(ValueError):
            collect_https(self.cfg(), b.domain,
                          query=lambda *args: {'status': 3, 'ips': [], 'ttl': None})
        def query(host, kind, resolver):
            return {'status': 0, 'ips': ['162.159.134.232', '162.159.134.233']
                    if kind == 'A' else [], 'ttl': 60}
        with self.assertRaises(ValueError):
            collect_https(self.cfg() | {'max_ips': 1}, b.domain, query=query)

    def test_private_multicast_wrong_family_and_cidr_answers_are_rejected(self):
        for value in ('127.0.0.1', '10.0.0.1', '224.0.0.1', 'ff00::1',
                      '2606:4700::1111', '162.159.134.0/24'):
            with self.subTest(value=value), self.assertRaises(ValueError):
                collect_https(self.cfg(), b.domain,
                              query=lambda *args: {'ips': [value], 'status': 0, 'ttl': 30})

    def test_scoped_cdn_is_not_exported_as_unrestricted_srs_or_ndms_ip(self):
        rule, _ = collect_https(self.cfg(), b.domain, query=self.answer)
        payload = {'version': 1, 'rules': [{'domain_suffix': ['discordapp.com']}, rule]}
        before = copy.deepcopy(payload)
        self.assertEqual(unrestricted(payload)['ip_cidr'], [])
        text, summary = b.ndms_text(payload, 'same')
        self.assertEqual(b.lines(text), ['discordapp.com'])
        self.assertEqual(summary['excluded_scoped_rules'], 1)
        b.verify_ndms(text, payload)
        self.assertEqual(payload, before)

    def test_coverage_rejects_removed_port_protocol_or_widened_network(self):
        rule, _ = collect_https(self.cfg(), b.domain, query=self.answer)
        verify_https({'rules': [rule]}, rule['ip_cidr'])
        for altered in ({'ip_cidr': rule['ip_cidr']},
                        rule | {'network': ['udp']},
                        rule | {'port': [80, 443]},
                        rule | {'ip_cidr': ['162.159.134.0/24']},
                        rule | {'domain_suffix': ['discordapp.com']}):
            with self.subTest(altered=altered), self.assertRaises(ValueError):
                verify_https({'rules': [altered]}, rule['ip_cidr'])

    def test_roundtrip_accepts_only_equivalent_cidr_aggregation(self):
        rule = {'network': ['tcp', 'udp'], 'port': [443],
                'ip_cidr': ['162.159.134.232/32', '162.159.134.233/32']}
        compact = rule | {'port': 443, 'ip_cidr': ['162.159.134.232/31']}
        canonical = b.canonical({'rules': [rule]})
        self.assertEqual(canonical, b.canonical({'rules': [compact]}))
        for altered in (compact | {'ip_cidr': ['162.159.134.0/24']},
                        compact | {'port': 8443},
                        compact | {'network': ['udp']},
                        {'ip_cidr': compact['ip_cidr']}):
            with self.subTest(altered=altered):
                self.assertNotEqual(canonical, b.canonical({'rules': [altered]}))
