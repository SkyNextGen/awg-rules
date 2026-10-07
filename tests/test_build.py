import importlib.util
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
        for n in ['0.0.0.0/0', '::/0', '10.0.0.0/8', '127.0.0.0/8', 'fc00::/7', '224.0.0.0/4']:
            with self.assertRaises(ValueError):
                b.network(n)

    def test_dedup(self):
        self.assertEqual(b.prune(['example.com', 'a.example.com', 'other.com']), ['example.com', 'other.com'])
        self.assertEqual(b.collapse(['1.1.1.0/25', '1.1.1.128/25']), ['1.1.1.0/24'])

    def test_v2fly_semantics(self):
        with patch.object(b, 'fetch', return_value='full:a.example.com\nexample.org\nkeyword:hello\nregexp:^test[.]com$'):
            result = b.V2Fly('test/').category('test')
            self.assertEqual(result['domain'], {'a.example.com'})
            self.assertEqual(result['domain_suffix'], {'example.org'})
            self.assertEqual(result['domain_keyword'], {'hello'})

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
            with patch.object(b, 'ROOT', root), patch.object(b, 'fetch', side_effect=RuntimeError('source unavailable')):
                with self.assertRaises(RuntimeError):
                    b.build()
            self.assertEqual(target.read_bytes(), b'last-good')


if __name__ == '__main__':
    unittest.main()
