import json
from pathlib import Path
import sys
import unittest
from unittest.mock import patch, MagicMock
from datetime import datetime, timezone

sys.path.insert(0, str(Path(__file__).parents[1] / 'src'))
import build as b
import meta_sources as m


class MetaSourceTests(unittest.TestCase):
    def test_doh_transport_uses_ipv4_without_changing_aaaa_queries(self):
        sock = MagicMock()
        with patch.object(m.socket, 'getaddrinfo', return_value=[(m.socket.AF_INET, m.socket.SOCK_STREAM, 6, '', ('8.8.8.8', 443))]) as lookup, patch.object(m.socket, 'socket', return_value=sock):
            self.assertIs(m.ipv4_connection(('dns.google',443),10), sock)
            self.assertEqual(lookup.call_args.args[2],m.socket.AF_INET)
            sock.connect.assert_called_once_with(('8.8.8.8',443))
        payload=self.answer('2606:4700::1111',number=28)
        response=MagicMock();response.__enter__.return_value.read.return_value=json.dumps(payload)
        with patch.object(m.DNS_OPENER,'open',return_value=response) as opened:
            self.assertEqual(m.query_dns('mmg.whatsapp.net','AAAA','https://dns.google/resolve')['ips'],['2606:4700::1111'])
            self.assertIn('type=AAAA',opened.call_args.args[0].full_url)

    def test_geofeed_date_cidr_and_family_are_checked(self):
        cfg = {'name': 'geofeed', 'format': 'geofeed', 'min_entries': 2,
               'max_entries': 10, 'families': [4, 6], 'max_age_days': 8}
        raw = '# Publication date: Mon Oct 12 2026\n8.8.8.0/24,US,,City,\n2606:4700::/32,US,,City,\n'
        now = datetime(2026, 10, 12, tzinfo=timezone.utc)
        self.assertEqual(m.feed_prefixes(raw, cfg, b.network, b.collapse, now), ['8.8.8.0/24', '2606:4700::/32'])
        for bad in (raw.replace('Mon Oct 12', 'Thu Oct 01'), raw.replace('8.8.8.0/24','8.8.8.1/24'),
                    raw.replace('8.8.8.0/24','10.0.0.0/24'), raw.replace('# Publication date:', '# Date:'),
                    raw.replace('2606:4700::/32,US,,City,\n',''), raw.replace('US,,City,','US,')):
            with self.assertRaises(ValueError):m.feed_prefixes(bad, cfg, b.network, b.collapse, now)

    def answer(self, ip='8.8.8.8', name='mmg.whatsapp.net', number=1):
        return {'Status': 0, 'Question': [{'name': 'mmg.whatsapp.net.', 'type': number}],
                'Answer': [{'name': name, 'type': number, 'TTL': 30, 'data': ip}]}

    def test_dns_follows_alias_and_ignores_unrelated_records(self):
        payload = self.answer(name='media.example.net')
        payload['Answer'] += [{'name':'mmg.whatsapp.net','type':5,'TTL':60,'data':'media.example.net.'},
                              {'name':'unrelated.example','type':1,'TTL':60,'data':'1.1.1.1'}]
        self.assertEqual(m.dns_answer(payload,'mmg.whatsapp.net','A')['ips'], ['8.8.8.8'])

    def test_dns_rejects_wrong_question_poison_and_temporary_failure(self):
        for ip in ('127.0.0.1','0.0.0.0','10.1.2.3','224.0.0.1'):
            with self.assertRaises(ValueError):m.dns_answer(self.answer(ip),'mmg.whatsapp.net','A')
        for payload in ({'Status':2,'Question':[{'name':'mmg.whatsapp.net','type':1}]},
                        {'Status':0,'Question':[{'name':'other.example','type':1}]},
                        self.answer('::1',number=28)):
            with self.assertRaises(ValueError):m.dns_answer(payload,'mmg.whatsapp.net','A')

    def test_nxdomain_alias_is_valid_but_addresses_are_not(self):
        p={'Status':3,'Question':[{'name':'mmg.whatsapp.net','type':1}],
           'Answer':[{'name':'mmg.whatsapp.net','type':5,'TTL':10,'data':'dead.example'}]}
        self.assertEqual(m.dns_answer(p,'mmg.whatsapp.net','A')['ips'], [])
        p['Answer'].append({'name':'dead.example','type':1,'TTL':10,'data':'8.8.8.8'})
        with self.assertRaises(ValueError):m.dns_answer(p,'mmg.whatsapp.net','A')

    def test_alias_cycle(self):
        p=self.answer();p['Answer']=[{'name':'mmg.whatsapp.net','type':5,'data':'a.example'},
                                   {'name':'a.example','type':5,'data':'mmg.whatsapp.net'}]
        with self.assertRaises(ValueError):m.dns_answer(p,'mmg.whatsapp.net','A')

    def cfg(self):
        return {'hosts_url':'https://source.example/hosts','resolver':'https://dns.google/resolve',
                'workers':2,'deadline_seconds':5,'min_hosts':1,'max_hosts':10,'min_resolved_hosts':1,
                'min_ips':2,'max_ips':10,'min_previous_ratio':0.75,'max_previous_ratio':1.5}

    def test_inventory_filters_roots_and_preserves_host_addresses(self):
        def query(host,kind,endpoint):
            return {'status':0,'ips':['8.8.8.8' if kind=='A' else '2606:4700::1111'],'ttl':30}
        fetch=lambda url:'mmg.whatsapp.net\nwa.com\nwhatsapp.net.evil.example\nmedia.facebook.com\n'
        hosts,ips,stats,observations=m.collect_dns(self.cfg(),fetch,b.domain,b.collapse,query=query)
        self.assertEqual(hosts,['media.facebook.com','mmg.whatsapp.net'])
        self.assertEqual(ips,['8.8.8.8/32','2606:4700::1111/128'])
        self.assertEqual(stats['resolved_hosts'],2)
        self.assertEqual(set(observations['mmg.whatsapp.net']), {'A','AAAA'})
        with self.assertRaises(ValueError):
            m.collect_dns(self.cfg(),fetch,b.domain,b.collapse,{'hosts':20},query=query)

    def test_inventory_failure_does_not_return_partial_result(self):
        def query(*args):raise RuntimeError('offline')
        with self.assertRaises(RuntimeError):
            m.collect_dns(self.cfg(),lambda url:'mmg.whatsapp.net',b.domain,b.collapse,query=query)
        def empty(*args):return {'status':3,'ips':[],'ttl':None}
        with self.assertRaises(ValueError):
            m.collect_dns(self.cfg(),lambda url:'mmg.whatsapp.net',b.domain,b.collapse,query=empty)


if __name__ == '__main__':unittest.main()
