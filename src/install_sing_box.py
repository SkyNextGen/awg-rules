"""Download a pinned official release and verify its published SHA256."""
import hashlib
import argparse
import io
import json
import os
from pathlib import Path
import platform
import tarfile
from urllib.request import Request, urlopen
import zipfile

ROOT = Path(__file__).resolve().parents[1]


def github_headers(url):
    """Use the job token only for GitHub API, never for downloaded assets."""
    token = os.getenv('GITHUB_TOKEN')
    return {'Authorization': 'Bearer ' + token} if token and url.startswith('https://api.github.com/') else {}


def download(url):
    with urlopen(Request(url, headers={'User-Agent': 'awg-rules-builder', **github_headers(url)}), timeout=120) as r:
        return r.read()


def verified_asset(repository, tag, name, release=None):
    if release is None:
        release = json.loads(download(f'https://api.github.com/repos/{repository}/releases/tags/{tag}'))
    asset = next(a for a in release['assets'] if a['name'] == name)
    digest = asset.get('digest', '')
    if not digest.startswith('sha256:'):
        raise ValueError('Release lacks SHA256 digest')
    data = download(asset['browser_download_url'])
    if hashlib.sha256(data).hexdigest() != digest.split(':', 1)[1]:
        raise ValueError('Release checksum mismatch')
    return data


def install(version=None, target=None):
    version = version or json.loads((ROOT / 'config/sources.json').read_text())['sing_box_version']
    system = {'Windows': 'windows', 'Linux': 'linux'}[platform.system()]
    arch = {'AMD64': 'amd64', 'x86_64': 'amd64', 'aarch64': 'arm64', 'ARM64': 'arm64'}[platform.machine()]
    name = f'sing-box-{version}-{system}-{arch}'
    archive = name + ('.zip' if system == 'windows' else '.tar.gz')
    data = verified_asset('SagerNet/sing-box', 'v' + version, archive)
    target = Path(target) if target else ROOT / '.tools'
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


def install_awgm(version, target):
    """Host-only compatibility probe; never installs anything on the router."""
    if platform.system() != 'Linux' or platform.machine() != 'x86_64':
        raise ValueError('AWGM compatibility probes require Linux amd64')
    data = verified_asset('hoaxisr/awgm-box', version, f'awgm-box-{version}-linux-amd64')
    target.mkdir(exist_ok=True)
    path = target / 'sing-box'
    path.write_bytes(data)
    path.chmod(0o755)
    print(path)


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('--version')
    parser.add_argument('--directory', type=Path)
    parser.add_argument('--awgm-version')
    args = parser.parse_args()
    if args.awgm_version:
        install_awgm(args.awgm_version, args.directory or ROOT / '.tools-awgm')
    else:
        install(args.version, args.directory)

