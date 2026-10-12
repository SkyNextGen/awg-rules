import json
from pathlib import Path
import sys
import tempfile
import unittest

sys.path.insert(0, str(Path(__file__).parents[1] / 'src'))
from routing_rules import split_rule, unrestricted, scoped_rules
from report import write_report
import test_report


class RoutingRules(unittest.TestCase):
    def test_split_preserves_matchers_and_scopes(self):
        mixed = {'domain_suffix': ['example.com'], 'domain': ['exact.test'],
                 'domain_keyword': ['keyword'], 'domain_regex': ['^regex'],
                 'ip_cidr': ['1.1.1.0/24', '2606:4700::/32']}
        udp = {'network': ['udp'], 'port_range': ['50000:65535'], 'ip_cidr': ['66.22.192.0/18']}
        before = {'rules': [mixed, udp]}
        after = {'rules': split_rule(mixed) + [udp]}
        self.assertEqual(unrestricted(before), unrestricted(after))
        self.assertEqual(scoped_rules(before), scoped_rules(after))
        self.assertNotIn('ip_cidr', after['rules'][0])
        self.assertEqual(set(after['rules'][1]), {'ip_cidr'})
        with self.assertRaises(ValueError):
            split_rule(udp)

    def test_migration_has_no_false_report_deltas(self):
        with tempfile.TemporaryDirectory() as directory:
            dist, stage = Path(directory) / 'dist', Path(directory) / 'stage'
            dist.mkdir()
            stage.mkdir()
            mixed = {'domain_suffix': ['a.com', 'b.com'], 'ip_cidr': ['1.1.1.0/24', '2606:4700::/32']}
            udp = {'network': ['udp'], 'port_range': ['50000:65535'], 'ip_cidr': ['66.22.192.0/18']}
            before = {'version': 1, 'rules': [mixed, udp]}
            after = {'version': 1, 'rules': split_rule(mixed) + [udp]}
            (dist / 'routing.json').write_text(json.dumps(before))
            report = test_report.Reports().sample()
            write_report(report, after, {}, stage, dist, {})
            for change in report['changes'].values():
                self.assertEqual(change['added_count'], 0)
                self.assertEqual(change['removed_count'], 0)
