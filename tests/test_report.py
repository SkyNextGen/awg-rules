import copy
import json
from pathlib import Path
import sys
import tempfile
import unittest

sys.path.insert(0, str(Path(__file__).parents[1] / 'src'))
from report import delta, telegram_text, write_report


class Reports(unittest.TestCase):
    def sample(self):
        return {'built_at': '2026-10-12T03:23:00+00:00', 'domains': 2, 'ipv4': 1, 'ipv6': 1, 'warnings': [], 'sources': {'itdog': 2}, 'asns': {}, 'matchers': {'domain_suffix': 2}, 'sha256': {'routing.json': 'a' * 64, 'routing.srs': 'b' * 64}}

    def test_same_count_replacement_is_visible(self):
        self.assertEqual(delta(['b.com'], ['a.com'])['added'], ['b.com'])
        self.assertEqual(delta(['b.com'], ['a.com'])['removed'], ['a.com'])
        self.assertFalse(delta(['b.com'], None)['baseline'])

    def test_real_diff_and_history_migration(self):
        with tempfile.TemporaryDirectory() as d:
            dist, stage = Path(d) / 'dist', Path(d) / 'stage'
            dist.mkdir()
            stage.mkdir()
            old = {'built_at': '2026-10-05T03:23:00+00:00', 'domains': 2, 'ipv4': 1, 'ipv6': 1}
            prior = {'version': 1, 'rules': [{'domain_suffix': ['a.com', 'same.com'], 'ip_cidr': ['1.1.1.0/24', '2606:4700::/32']}]}
            (dist / 'routing.json').write_text(json.dumps(prior))
            current = copy.deepcopy(prior)
            current['rules'][0]['domain_suffix'] = ['b.com', 'same.com']
            report = self.sample()
            write_report(report, current, {'itdog': ['domain_suffix:b.com', 'domain_suffix:same.com']}, stage, dist, old)
            self.assertEqual(report['changes']['domains']['added'], ['domain_suffix:b.com'])
            self.assertEqual(report['changes']['domains']['removed'], ['domain_suffix:a.com'])
            self.assertFalse(report['source_changes']['itdog']['baseline'])
            self.assertEqual(report['trend']['runs'], 2)
            self.assertEqual(report['trend']['metrics']['domains']['delta'], 0)
            self.assertIn('06:23 МСК', (stage / 'report.md').read_text(encoding='utf-8'))
            self.assertIn('+1 / -1', (stage / 'tg_message.txt').read_text(encoding='utf-8'))
            # Subsequent run has a real source baseline, not invented zero changes.
            for f in stage.iterdir():
                (dist / f.name).write_bytes(f.read_bytes())
            (dist / 'routing.json').write_text(json.dumps(current))
            next_report = self.sample()
            next_report['built_at'] = '2026-10-19T03:23:00+00:00'
            write_report(next_report, current, {'itdog': ['domain_suffix:b.com', 'domain_suffix:same.com']}, stage, dist, report)
            self.assertEqual(next_report['source_changes']['itdog']['added_count'], 0)
            self.assertEqual(next_report['trend']['runs'], 3)

    def test_telegram_failure_ignores_stale_success(self):
        text = telegram_text({}, 'failure', 'https://github.com/run/1')
        self.assertIn('ОШИБКА', text)
        self.assertNotIn('завершена успешно', text)

    def test_telegram_limit_keeps_links(self):
        report = self.sample()
        report['warnings'] = ['😀' * 6000]
        report['changes'] = {k: delta([], []) for k in ('domains', 'ipv4', 'ipv6')}
        report['source_changes'] = {}
        report['trend'] = {'runs': 1, 'metrics': {'domains': {'average': 2, 'delta': 0}}}
        text = telegram_text(report, run_url='https://github.com/run/1')
        self.assertLessEqual(len(text.encode('utf-16-le')) // 2, 4096)
        self.assertIn('https://github.com/run/1', text)
        self.assertIn('dist/report.md', text)
