Attempting to perform the InitializeDefaultDrives operation on the 'FileSystem' provider failed.
"""Exercise the generated SRS with real TCP/UDP traffic, entirely on loopback."""
import argparse
from contextlib import ExitStack
import json
from pathlib import Path
import socket
import subprocess
import tempfile
import threading
import time

ROOT = Path(__file__).resolve().parents[1]


def reserve_listener(network, reservations):
    kind = socket.SOCK_STREAM if network == 'tcp' else socket.SOCK_DGRAM
    listener = reservations.enter_context(socket.socket(socket.AF_INET, kind))
    listener.bind(('127.0.0.1', 0))
    return listener.getsockname()[1]


def probe(exe, source):
    stop = threading.Event()
    sockets, workers = [], []
    process = None
    reservations = ExitStack()

    def sink(label):
        tcp = socket.socket()
        tcp.bind(('127.0.0.1', 0))
        tcp.listen()
        udp = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        udp.bind(tcp.getsockname())
        sockets.extend((tcp, udp))
        for sock in (tcp, udp):
            sock.settimeout(.1)

        def serve(sock):
            while not stop.is_set():
                try:
                    if sock is tcp:
                        client, _ = sock.accept()
                        with client:
                            client.settimeout(1)
                            client.recv(32)
                            client.sendall(label.encode())
                    else:
                        _, address = sock.recvfrom(100)
                        sock.sendto(label.encode(), address)
                except socket.timeout:
                    continue
        for sock in (tcp, udp):
            worker = threading.Thread(target=serve, args=(sock,))
            worker.start()
            workers.append(worker)
        return tcp.getsockname()[1]

    try:
        ports = {tag: sink(tag) for tag in ('matched', 'fallback')}
        destinations = [('35.224.0.1', port) for port in
                        (443, 19199, 19200, 19400, 19401, 49999, 50000, 50099, 50100, 65535)]
        destinations += [('35.240.0.1', 50000), ('66.22.192.1', 19200), ('35.248.0.1', 50000)]
        cases = [(network, ip, port) for network in ('tcp', 'udp') for ip, port in destinations]
        inbounds = []
        for index, (network, ip, port) in enumerate(cases):
            listen = reserve_listener(network, reservations)
            inbounds.append({'type': 'direct', 'tag': str(index), 'listen': '127.0.0.1',
                             'listen_port': listen, 'network': network,
                             'override_address': ip, 'override_port': port})
        with tempfile.TemporaryDirectory() as directory:
            config = Path(directory) / 'config.json'
            config.write_text(json.dumps({
                'log': {'level': 'error'}, 'inbounds': inbounds,
                'outbounds': [{'type': 'direct', 'tag': tag} for tag in ports],
                'route': {'rule_set': [{'type': 'local', 'tag': 'routing', 'format': 'binary',
                                        'path': str(source.resolve())}],
                          'rules': [{'rule_set': ['routing'], 'action': 'route', 'outbound': 'matched',
                                     'override_address': '127.0.0.1', 'override_port': ports['matched']},
                                    {'action': 'route', 'outbound': 'fallback',
                                     'override_address': '127.0.0.1', 'override_port': ports['fallback']}],
                          'final': 'fallback'}}))
            # Hold each port in its actual protocol until the engine takes over.
            reservations.close()
            process = subprocess.Popen([exe, 'run', '-c', str(config)],
                                       stdout=subprocess.PIPE, stderr=subprocess.STDOUT)
            for case, inbound in zip(cases, inbounds):
                network, ip, port = case
                expected = ('matched' if network == 'udp' and ip != '35.248.0.1'
                            and port in (19200, 19400, 50000, 50099) else 'fallback')
                for attempt in range(30):
                    if process.poll() is not None:
                        raise RuntimeError(process.stdout.read().decode(errors='replace'))
                    kind = socket.SOCK_STREAM if network == 'tcp' else socket.SOCK_DGRAM
                    with socket.socket(socket.AF_INET, kind) as client:
                        client.settimeout(.3)
                        try:
                            client.connect(('127.0.0.1', inbound['listen_port']))
                            client.sendall(b'probe')
                            actual = client.recv(100).decode()
                            break
                        except (ConnectionRefusedError, ConnectionResetError, socket.timeout):
                            time.sleep(.05)
                else:
                    raise RuntimeError(f'Routing probe timed out: {case}')
                if actual != expected:
                    raise AssertionError(f'{case}: expected {expected}, got {actual}')
            print(f'Routing OK: {len(cases)} TCP/UDP cases on {exe}')
    finally:
        reservations.close()
        if process is not None:
            process.terminate()
            process.communicate(timeout=5)
        stop.set()
        for worker in workers:
            worker.join(timeout=2)
        for sock in sockets:
            sock.close()


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('exe')
    parser.add_argument('--source', type=Path, default=ROOT / 'dist/routing.srs')
    args = parser.parse_args()
    probe(args.exe, args.source)
