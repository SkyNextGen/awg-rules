"""Offline regression checks for explicitly requested service coverage."""
from pathlib import Path
import sys
import unittest
import json

sys.path.insert(0, str(Path(__file__).parents[1] / 'src'))
from build import ROOT, domain, lines, prune, service_prefixes
from check_service_coverage import covered_suffix, covers_network
from unittest.mock import patch


class ServiceCoverage(unittest.TestCase):
    def test_required_categories_enabled_once(self):
        categories = lines((ROOT / 'config/v2fly-categories.txt').read_text())
        for category in (
            'nexusmods', 'facebook', 'instagram', 'meta', 'threads',
            'google', 'google-play', 'googlefcm', 'youtube', 'microsoft',
            'netflix', 'nvidia', 'openai', 'category-ai-cn',
            'category-ai-!cn', 'category-ai-chat-!cn', 'category-ai-ru',
            'tiktok', 'spotify', 'soundcloud', 'playstation', 'patreon', 'signal',
        ):
            self.assertEqual(categories.count(category), 1, category)

    def test_messaging_services_are_separate_refreshable_sources(self):
        cfg = json.loads((ROOT / 'config/sources.json').read_text())
        sources = cfg['service_sources']
        self.assertEqual(set(sources), {'discord', 'telegram', 'whatsapp'})
        for service, entries in sources.items():
            with self.subTest(service=service):
                self.assertTrue(entries)
                self.assertTrue(all(entry.get('kind') in {'v2fly', 'domains'} for entry in entries))
        self.assertTrue(any(entry.get('category') == 'discord' for entry in sources['discord']))
        self.assertTrue(any(entry.get('url', '').endswith('/Services/discord.lst') for entry in sources['discord']))
        self.assertTrue(any(entry.get('category') == 'telegram' for entry in sources['telegram']))
        self.assertTrue(any(entry.get('url', '').endswith('/Services/telegram.lst') for entry in sources['telegram']))
        self.assertTrue(any(entry.get('category') == 'whatsapp' for entry in sources['whatsapp']))
        self.assertFalse(any('Subnets/' in entry.get('url', '') for entries in sources.values() for entry in entries))


    def test_no_static_service_domain_list(self):
        self.assertFalse((ROOT / 'config/service-domains.txt').exists())
        self.assertEqual(len(lines((ROOT / 'config/custom-domains.txt').read_text())), 32)

    def test_service_ips_are_fresh_and_mapped_to_reviewed_asns(self):
        cfg = json.loads((ROOT / 'config/sources.json').read_text())
        self.assertEqual(cfg['service_ip_sources']['telegram']['url'],
                         'https://core.telegram.org/resources/cidr.txt')
        self.assertEqual(cfg['custom_service_asn_groups'], {'telegram': 'telegram', 'whatsapp': 'meta'})
        self.assertFalse(lines((ROOT / 'config/custom-ip-cidrs.txt').read_text()))

    def test_service_prefix_source_rejects_empty_unsafe_or_missing_family(self):
        source = {'url': 'https://official.test/cidr', 'min_prefixes': 2, 'max_prefixes': 20}
        valid = '1.1.1.0/24\n2606:4700::/32'
        with patch('build.fetch', return_value=valid):
            self.assertEqual(set(service_prefixes(source)), {'1.1.1.0/24', '2606:4700::/32'})
        for value in ('', '1.1.1.0/25\n1.1.1.128/25', '0.0.0.0/0\n2606:4700::/32'):
            with self.subTest(value=value), patch('build.fetch', return_value=value):
                with self.assertRaises(ValueError):
                    service_prefixes(source)

    def test_suffix_overlap_requires_full_subdomain_coverage(self):
        self.assertTrue(covered_suffix('sub.example.com', {'example.com'}))
        self.assertTrue(covered_suffix('example.com', {'example.com'}))
        self.assertFalse(covered_suffix('example.com', {'sub.example.com'}))
        self.assertFalse(covered_suffix('notexample.com', {'example.com'}))
        self.assertTrue(covers_network('149.154.168.0/22', ['149.154.160.0/20']))
        self.assertFalse(covers_network('2a0a:f280::/32', ['149.154.160.0/20']))

    def test_custom_cleanup_audit_has_proven_suffix_matches(self):
        audit = json.loads((ROOT / 'docs/custom-domain-audit.json').read_text())
        self.assertEqual(len(audit['removed_custom']), 92)
        self.assertEqual(len(audit['removed_service_domains']), 32)
        self.assertEqual(set(audit['kept_custom']),
                         set(lines((ROOT / 'config/custom-domains.txt').read_text())))
        for entry in audit['removed_custom'] + audit['removed_service_domains']:
            self.assertTrue(entry['coverage'])
            for match in entry['coverage']:
                self.assertTrue(match['rule'].startswith('domain_suffix:'))
                self.assertTrue(covered_suffix(entry['domain'], {match['rule'].split(':', 1)[1]}))
