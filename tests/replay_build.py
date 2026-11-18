"""Rebuild published inputs without HTTP and compare the complete routing output."""
import argparse
import copy
import json
import os
from pathlib import Path
import shutil
import sys
import tempfile
from unittest.mock import patch

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / 'src'))
import build as builder
import check_service_coverage
from check_itdog import RUNS_URL


def domain_records(values):
    result = {key: set() for key in builder.MATCH_KEYS if key != 'ip_cidr'}
    for value in values:
        key, data = value.split(':', 1)
        result[key].add(data)
    return result


def file_contents(directory):
    return {str(p.relative_to(directory)): p.read_bytes() for p in directory.rglob('*') if p.is_file()}


def replay(baseline, exe):
    # Configuration comes from the same commit as the published snapshot. A PR
    # may intentionally change current configuration without changing this replay.
    cfg = json.loads((baseline / 'config/sources.json').read_text())
    dist = baseline / 'dist'
    records = json.loads((dist / 'source-snapshot.json').read_text())
    old_report = json.loads((dist / 'report.json').read_text())
    payload = json.loads((dist / 'routing.json').read_text())
    dns = json.loads((dist / 'whatsapp-dns.json').read_text())
    urls = {cfg['itdog_url']: '\n'.join(domain_records(records['itdog'])['domain_suffix'])}
    # Missing upstream job history is advisory even in an offline replay.
    urls[RUNS_URL] = json.dumps({'workflow_runs': []})
    for service, sources in cfg['service_sources'].items():
        for source in sources:
            if source['kind'] == 'domains':
                urls[source['url']] = '\n'.join(domain_records(records['ITDog:service:' + service])['domain_suffix'])
    for service, source in cfg['service_ip_sources'].items():
        urls[source['url']] = '\n'.join(records[service + ':official-cidr'])

    def collect_dns(*args):
        hosts = [v.split(':', 1)[1] for v in records['WhatsApp:cdn-hosts']]
        return hosts, records['WhatsApp:cdn-dns'], copy.deepcopy(dns['summary']), dns['observations']

    with tempfile.TemporaryDirectory(prefix='awg-replay-') as directory:
        root = Path(directory)
        shutil.copytree(baseline / 'config', root / 'config')
        shutil.copytree(dist, root / 'dist')
        before = file_contents(root / 'dist')
        with (patch.object(builder, 'ROOT', root),
              patch('urllib.request.OpenerDirector.open', side_effect=AssertionError('HTTP forbidden in replay')),
              patch.object(builder, 'fetch', side_effect=lambda url: urls[url]),
              patch.object(builder.V2Fly, 'category', side_effect=lambda name: domain_records(records['v2fly:' + name])),
              patch.object(builder, 'bgp', return_value=copy.deepcopy(old_report['asns'])),
              patch.object(builder, 'collect_feeds', return_value={k[5:]: v for k, v in records.items() if k.startswith('Meta:')}),
              patch.object(builder, 'collect_dns', side_effect=collect_dns),
              patch.object(builder, 'discord_voice', side_effect=lambda cfg: [json.loads(r) for r in records['ITDog:discord:scoped-udp']]),
              patch.object(builder, 'collect_https', return_value=(
                  {'network': ['tcp', 'udp'], 'ip_cidr': records['Discord:cdn-dns:https'], 'port': [443]},
                  copy.deepcopy(old_report['discord_https']))),
              patch.dict(os.environ, {'SING_BOX': str(exe), 'SOURCE_CACHE': ''})):
            with patch.object(check_service_coverage, 'verify', side_effect=ValueError('test late validation failure')):
                try:
                    builder.build()
                except ValueError as error:
                    if str(error) != 'test late validation failure':
                        raise
                else:
                    raise AssertionError('Late validation failure was not raised')
            if before != file_contents(root / 'dist'):
                raise AssertionError('Failed build modified published output')
            builder.build()
        generated = root / 'dist'
        if builder.canonical(json.loads((generated / 'routing.json').read_text())) != builder.canonical(payload):
            raise AssertionError('Replayed JSON rules differ from published rules')
        if (generated / 'routing.srs').read_bytes() != (dist / 'routing.srs').read_bytes():
            raise AssertionError('Replayed SRS bytes differ from published SRS')
        if builder.lines((generated / 'routing.txt').read_text()) != builder.lines((dist / 'routing.txt').read_text()):
            raise AssertionError('Replayed TXT routes differ from published routes')
        for path in (dist / 'custom').glob('*.json'):
            if json.loads(path.read_text()) != json.loads((generated / 'custom' / path.name).read_text()):
                raise AssertionError('Replayed service set differs: ' + path.name)
    print('Replay OK: identical SRS bytes, JSON rules, TXT routes and custom sets; failed build preserves dist')


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('--baseline', type=Path, default=ROOT)
    parser.add_argument('--sing-box', type=Path, required=True)
    args = parser.parse_args()
    replay(args.baseline.resolve(), args.sing_box.resolve())
