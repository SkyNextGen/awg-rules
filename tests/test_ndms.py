import copy
from pathlib import Path
import sys
import unittest

sys.path.insert(0, str(Path(__file__).parents[1] / 'src'))
import build as b


class NDMSExport(unittest.TestCase):
    def fixture(self):
        return {'version': 1, 'rules': [
            {'domain_suffix': ['example.com', 'a.example.com', 'example.com'],
             'domain': ['exact.test', 'child.exact.test', 'notexample.com'],
             'domain_keyword': ['keyword'], 'domain_regex': ['^regex[.]test$']},
            {'ip_cidr': ['1.1.1.0/25', '1.1.1.128/25', '2606:4700::/32']},
            {'network': ['udp'], 'port_range': ['19000:20000'], 'ip_cidr': ['104.16.0.0/12']}]}

    def test_suffixes_boundaries_and_scoped_networks(self):
        payload = self.fixture()
        before = copy.deepcopy(payload)
        text, summary = b.ndms_text(payload, '2026-10-12T19:00:00+00:00')
        self.assertEqual(b.lines(text), ['exact.test', 'example.com', 'notexample.com',
                                        '1.1.1.0/24', '2606:4700::/32'])
        self.assertIn('# domain_regex: ^regex[.]test$', text)
        self.assertNotIn('104.16.0.0/12', text)
        self.assertEqual(summary['exact_to_suffix'], 3)
        self.assertEqual(summary['excluded_scoped_rules'], 1)
        self.assertEqual(summary['excluded_matchers'], {'domain_keyword': 1, 'domain_regex': 1})
        self.assertEqual(payload, before)
        b.verify_ndms(text, payload)

    def test_mixed_and_split_source_formats_produce_same_projection(self):
        mixed = {'version': 1, 'rules': [{'domain_suffix': ['example.com'], 'ip_cidr': ['1.1.1.0/24']}]}
        split = {'version': 1, 'rules': b.split_rule(mixed['rules'][0])}
        self.assertEqual(b.ndms_text(mixed, 'same'), b.ndms_text(split, 'same'))

    def test_missing_extra_duplicate_and_unsafe_entries_block_validation(self):
        payload = self.fixture()
        text, _ = b.ndms_text(payload, 'same')
        for invalid in (text.replace('\nexact.test\n', '\n'),
                        text + '104.16.0.0/12\n', text + 'example.com\n',
                        text.replace('1.1.1.0/24', '127.0.0.0/8'),
                        text.replace('exact.test', 'exact.test/path')):
            with self.subTest(invalid=invalid), self.assertRaises(ValueError):
                b.verify_ndms(invalid, payload)

    def test_unknown_conditions_fail_instead_of_silently_widening(self):
        payload = self.fixture()
        payload['rules'].append({'domain_suffix': ['restricted.test'], 'source_ip_cidr': ['1.1.1.0/24']})
        with self.assertRaises(ValueError):
            b.ndms_text(payload, 'same')
