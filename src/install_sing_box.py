"""Download a pinned official release and verify its published SHA256."""
import hashlib
import io
import json
import os
from pathlib import Path
import platform
import tarfile
from urllib.request import Request, urlopen
import zipfile

ROOT = Path(__file__).resolve().parents[1]


def download(url):
    with urlopen(Request(url, headers={'User-Agent': 'awg-rules-builder'}), timeout=120) as r:
        return r.read()


def install():
    version = json.loads((ROOT / 'config/sources.json').read_text())['sing_box_version']
    system = {'Windows': 'windows', 'Linux': 'linux'}[platform.system()]
    arch = {'AMD64': 'amd64', 'x86_64': 'amd64', 'aarch64': 'arm64', 'ARM64': 'arm64'}[platform.machine()]
    name = f'sing-box-{version}-{system}-{arch}'
    archive = name + ('.zip' if system == 'windows' else '.tar.gz')
    base = f'https://github.com/SagerNet/sing-box/releases/download/v{version}/'
    release = json.loads(download(f'https://api.github.com/repos/SagerNet/sing-box/releases/tags/v{version}'))
    asset = next(a for a in release['assets'] if a['name'] == archive)
    digest = asset.get('digest', '')
    if not digest.startswith('sha256:'):
        raise ValueError('Official release lacks SHA256 digest')
    expected = digest.split(':', 1)[1]
    data = download(base + archive)
    if hashlib.sha256(data).hexdigest() != expected:
        raise ValueError('Official release checksum mismatch')
    target = ROOT / '.tools'
    target.mkdir(exist_ok=True)
    binary = 'sing-box.exe' if system == 'windows' else 'sing-box'
    member = name + '/' + binary
    if system == 'windows':
        with zipfile.ZipFile(io.BytesIO(data)) as z:
            content = z.read(member)
    else:
        with tarfile.open(fileobj=io.BytesIO(data), mode='r:gz') as t:
            content = t.extractfile(member).read()
    path = target / binary
    path.write_bytes(content)
    if system == 'linux':
        os.chmod(path, 0o755)
    print(path)


if __name__ == '__main__':
    install()
