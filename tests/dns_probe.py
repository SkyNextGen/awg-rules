"""Local sing-box DNS matcher reproduction; no external DNS or VPN needed."""
import json
import socket
import struct
import subprocess
import sys
import tempfile
import threading
import time
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parents[1] / 'src'))
from routing_rules import split_rule

def stub(answer):
    sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    sock.bind(('127.0.0.1', 0))
    sock.settimeout(.2)
    stop = threading.Event()
    def serve():
        while not stop.is_set():
            try:
                data, client = sock.recvfrom(4096)
            except socket.timeout:
                continue
            end = 12
            while data[end]:
                end += data[end] + 1
            end += 5
            response = data[:2] + struct.pack('!HHHHH', 0x8180, 1, 1, 0, 0) + data[12:end]
            response += b'\xc0\x0c' + struct.pack('!HHIH', 1, 1, 30, 4) + socket.inet_aton(answer)
            sock.sendto(response, client)
    worker = threading.Thread(target=serve)
    worker.start()
    return sock, stop, worker

def probe(exe, split):
    servers = [stub('127.0.0.1'), stub('203.0.113.42')]
    try:
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            mixed = {'domain_suffix': ['themoviedb.org'], 'ip_cidr': ['1.1.1.0/24']}
            rules = split_rule(mixed) if split else [mixed]
            source = root / 'rules.json'
            source.write_text(json.dumps({'version': 1, 'rules': rules}))
            binary = root / 'rules.srs'
            subprocess.run([exe, 'rule-set', 'compile', '--output', str(binary), str(source)], check=True, capture_output=True)
            listener = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
            listener.bind(('127.0.0.1', 0))
            port = listener.getsockname()[1]
            listener.close()
            config = {
                'log': {'level': 'debug'},
                'dns': {'servers': [{'type': 'udp', 'tag': tag, 'server': '127.0.0.1', 'server_port': item[0].getsockname()[1]} for tag, item in zip(('direct', 'tunnel'), servers)],
                        'rules': [{'rule_set': ['routing'], 'rule_set_ip_cidr_match_source': True, 'server': 'tunnel'}], 'final': 'direct', 'strategy': 'ipv4_only'},
                'inbounds': [{'type': 'direct', 'listen': '127.0.0.1', 'listen_port': port, 'network': 'udp'}],
                'outbounds': [{'type': 'direct', 'tag': 'direct'}],
                'route': {'default_domain_resolver': 'direct', 'rules': [{'network': 'udp', 'action': 'hijack-dns'}],
                          'rule_set': [{'type': 'local', 'tag': 'routing', 'format': 'binary', 'path': str(binary)}]}}
            cfg = root / 'config.json'
            cfg.write_text(json.dumps(config))
            proc = subprocess.Popen([exe, 'run', '-c', str(cfg)], stdout=subprocess.PIPE, stderr=subprocess.STDOUT)
            try:
                query = struct.pack('!HHHHHH', 123, 0x100, 1, 0, 0, 0)
                query += b''.join(bytes([len(label)]) + label.encode() for label in 'www.themoviedb.org'.split('.')) + b'\0' + struct.pack('!HH', 1, 1)
                client = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
                client.settimeout(.3)
                for attempt in range(30):
                    if proc.poll() is not None:
                        raise RuntimeError(proc.stdout.read().decode(errors='replace'))
                    client.sendto(query, ('127.0.0.1', port))
                    try:
                        data = client.recv(4096)
                        return socket.inet_ntoa(data[-4:])
                    except (socket.timeout, ConnectionResetError):
                        time.sleep(.05)
                raise RuntimeError('DNS probe timed out')
            finally:
                client.close()
                proc.terminate()
                proc.wait(timeout=5)
    finally:
        for sock, stop, worker in servers:
            stop.set()
            worker.join()
            sock.close()

if __name__ == '__main__':
    before, after = probe(sys.argv[1], False), probe(sys.argv[1], True)
    print('Mixed rule:', before, '| Split rules:', after)
    expected_before = sys.argv[2]
    assert before == expected_before and after == '203.0.113.42', (before, after)
