import importlib.util
import json
from pathlib import Path
import unittest
import tempfile
import sys
from datetime import datetime, timezone, timedelta
from unittest.mock import patch

sys.path.insert(0, str(Path(__file__).parents[1] / 'src'))
spec = importlib.util.spec_from_file_location('builder', Path(__file__).parents[1] / 'src/build.py')
b = importlib.util.module_from_spec(spec)
spec.loader.exec_module(b)


class SafetyTests(unittest.TestCase):
    def test_domains(self):
        self.assertEqual(b.domain('*.EXAMPLE.com.'), 'example.com')
        for d in ['com', 'http://example.com', '1.2.3.4', '-bad.com', '']:
            with self.assertRaises(ValueError):
                b.domain(d)

    def test_networks(self):
        for n in ['0.0.0.0/0', '::/0', '10.0.0.0/8', '127.0.0.0/8', 'fc00::/7',
                  '224.0.0.0/4', '224.0.0.0/8', '239.1.2.0/24', 'ff00::/19', 'ff02::/32']:
            with self.assertRaises(ValueError):
                b.network(n)

    def test_ip_coverage_checks_addresses_in_both_families(self):
        before = ['8.8.8.0/24', '2606:4700::/32']
        b.verify_ip_coverage(before, before, .8, 1.5)
        b.verify_ip_coverage(['8.8.8.0/25', '8.8.8.128/25', '2606:4700::/32'], before, .8, 1.5)
        for after in (['8.0.0.0/8', before[1]], [before[0], '2600::/19'],
                      ['8.8.8.0/25', before[1]], [before[0]]):
            with self.subTest(after=after), self.assertRaises(ValueError):
                b.verify_ip_coverage(after, before, .8, 1.5)

    def test_bgp_rejects_expansion_and_keeps_the_validated_snapshot(self):
        old = {'1': {'prefixes': ['8.8.8.0/24', '2606:4700::/32'],
                     'fetched_at': datetime.now(timezone.utc).isoformat()}}
        response = json.dumps({'status': 'ok', 'data': {'prefixes': [
            {'prefix': '8.0.0.0/8'}, {'prefix': '2606:4700::/32'}]}})
        cfg = {'max_prefixes': 100, 'max_snapshot_age_days': 8,
               'min_previous_ratio': .8, 'max_previous_ratio': 1.5}
        report = {'warnings': []}
        with patch.object(b, 'fetch', return_value=response), patch.object(b, 'urlopen', side_effect=OSError('offline')):
            result = b.bgp([1], old, cfg, report)
        self.assertEqual(result['1']['source'], 'snapshot')
        self.assertEqual(result['1']['prefixes'], old['1']['prefixes'])
        self.assertTrue(any('address coverage' in warning for warning in report['warnings']))

    def test_source_error_preserves_the_failure_reason(self):
        with patch.object(b, 'urlopen', side_effect=OSError('test timeout')), patch.object(b.time, 'sleep'):
            with self.assertRaisesRegex(RuntimeError, 'test timeout') as caught:
                b.fetch('https://source.example/list')
        self.assertIsInstance(caught.exception.__cause__, OSError)

    def test_publish_failure_keeps_all_previous_files(self):
        with tempfile.TemporaryDirectory() as d:
            root = Path(d)
            dist, staging = root / 'dist', root / 'staged'
            dist.mkdir(); staging.mkdir()
            for name in ('routing.srs', 'routing.json'):
                (dist / name).write_bytes(b'old')
                (staging / name).write_bytes(b'new')
            rename = Path.rename
            def fail_replacement(path, target):
                if path.name == 'ready':
                    raise OSError('test disk failure')
                return rename(path, target)
            with patch.object(Path, 'rename', fail_replacement), self.assertRaises(OSError):
                b.publish(staging, dist)
            self.assertEqual({p.name: p.read_bytes() for p in dist.iterdir()},
                             {'routing.srs': b'old', 'routing.json': b'old'})

    def test_publish_preserves_unrelated_files_and_excludes_roundtrip(self):
        with tempfile.TemporaryDirectory() as d:
            root = Path(d)
            dist, staging = root / 'dist', root / 'staged'
            dist.mkdir(); staging.mkdir()
            (dist / 'notes.txt').write_text('user data')
            (staging / 'routing.srs').write_bytes(b'new')
            (staging / 'roundtrip.json').write_text('{}')
            b.publish(staging, dist)
            self.assertEqual((dist / 'notes.txt').read_text(), 'user data')
            self.assertEqual((dist / 'routing.srs').read_bytes(), b'new')
            self.assertFalse((dist / 'roundtrip.json').exists())

    def test_dedup(self):
        self.assertEqual(b.prune(['example.com', 'a.example.com', 'other.com']), ['example.com', 'other.com'])
        self.assertEqual(b.collapse(['1.1.1.0/25', '1.1.1.128/25']), ['1.1.1.0/24'])

    def test_v2fly_semantics(self):
        with patch.object(b, 'fetch', return_value='full:a.example.com\nexample.org\nkeyword:hello\nregexp:^test[.]com$'):
            result = b.V2Fly('test/').category('test')
            self.assertEqual(result['domain'], {'a.example.com'})
            self.assertEqual(result['domain_suffix'], {'example.org'})
            self.assertEqual(result['domain_keyword'], {'hello'})

    def test_v2fly_category_names_can_contain_exclamation(self):
        with patch.object(b, 'fetch', return_value='example.com'):
            self.assertEqual(b.V2Fly('test/').category('category-ai-!cn')['domain_suffix'], {'example.com'})

    def test_include_cycle(self):
        with patch.object(b, 'fetch', return_value='include:test'):
            with self.assertRaises(ValueError):
                b.V2Fly('test/').category('test')

    def test_snapshot_expiry_and_missing_family(self):
        cfg = {'max_prefixes': 100, 'max_snapshot_age_days': 7, 'min_previous_ratio': 0.8, 'max_previous_ratio': 1.5}
        report = {'warnings': []}
        with patch.object(b, 'fetch', side_effect=RuntimeError('offline')), patch.object(b, 'urlopen', side_effect=RuntimeError('offline')):
            old = {'1': {'prefixes': ['1.1.1.0/24', '2606:4700::/32'], 'fetched_at': (datetime.now(timezone.utc) - timedelta(days=8)).isoformat()}}
            with self.assertRaises(ValueError):
                b.bgp([1], old, cfg, report)
            old['1']['fetched_at'] = datetime.now(timezone.utc).isoformat()
            self.assertEqual(b.bgp([1], old, cfg, report)['1']['source'], 'snapshot')
            old['1']['prefixes'] = ['1.1.1.0/24']
            with self.assertRaises(ValueError):
                b.bgp([1], old, cfg, report)

    def test_source_failure_preserves_dist(self):
        with tempfile.TemporaryDirectory() as d:
            root = Path(d)
            (root / 'config').mkdir()
            (root / 'config/sources.json').write_text((b.ROOT / 'config/sources.json').read_text())
            (root / 'dist').mkdir()
            target = root / 'dist/routing.srs'
            target.write_bytes(b'last-good')
            text_target = root / 'dist/routing.txt'
            text_target.write_bytes(b'last-good-txt')
            with patch.object(b, 'ROOT', root), patch.object(b, 'fetch', side_effect=RuntimeError('source unavailable')):
                with self.assertRaises(RuntimeError):
                    b.build()
            self.assertEqual(target.read_bytes(), b'last-good')
            self.assertEqual(text_target.read_bytes(), b'last-good-txt')


if __name__ == '__main__':
    unittest.main()

