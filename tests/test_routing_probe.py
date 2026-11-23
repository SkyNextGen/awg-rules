from contextlib import ExitStack
import socket
import unittest

from routing_probe import reserve_listener


class ListenerReservationTests(unittest.TestCase):
    def test_ports_remain_reserved_in_the_requested_protocol(self):
        with ExitStack() as reservations:
            for network, kind in (('tcp', socket.SOCK_STREAM), ('udp', socket.SOCK_DGRAM)):
                ports = [reserve_listener(network, reservations) for _ in range(26)]
                self.assertEqual(len(set(ports)), len(ports))
                for port in ports:
                    with socket.socket(socket.AF_INET, kind) as other:
                        with self.assertRaises(OSError):
                            other.bind(('127.0.0.1', port))

    def test_reservations_are_released_before_engine_start(self):
        for network, kind in (('tcp', socket.SOCK_STREAM), ('udp', socket.SOCK_DGRAM)):
            with ExitStack() as reservations:
                port = reserve_listener(network, reservations)
            with socket.socket(socket.AF_INET, kind) as listener:
                listener.bind(('127.0.0.1', port))
