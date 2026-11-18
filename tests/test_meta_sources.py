import json
from pathlib import Path
import sys
import unittest
import threading
import time
from unittest.mock import patch, MagicMock
from datetime import datetime, timedelta, timezone

sys.path.insert(0, str(Path(__file__).parents[1] / 'src'))
import build as b
import meta_sources as m


class MetaSourceTests(unittest.TestCase):
    def test_feed_snapshot_is_bounded_and_invalid_live_data_is_fatal(self):
        cfg = [{'name': 'test', 'url': 'https://source.example/cidr', 'format': 'cidr',
                'min_entries': 2, 'max_entries': 10, 'families': [4, 6]}]
        snapshot, warnings = {}, []
        valid = '8.8.8.0/24\n2606:4700::/32'
        expected = m.collect_feeds(cfg, lambda url: valid, b.network, b.collapse, snapshot, warnings)
        original_timestamp = snapshot['test']['fetched_at']
        def offline(url):
            raise RuntimeError('test outage')
        self.assertEqual(m.collect_feeds(cfg, offline, b.network, b.collapse, snapshot, warnings), expected)
        self.assertEqual(snapshot['test']['fetched_at'], original_timestamp)
        self.assertIn('Не удалось скачать список сетей Meta (test)', warnings[0])
        self.assertIn('Взяли проверенную копию', warnings[0])
        with self.assertRaises(ValueError):
            m.collect_feeds(cfg, lambda url: '10.0.0.0/8', b.network, b.collapse, snapshot)
        snapshot['test']['expires_at'] = (datetime.now(timezone.utc) - timedelta(seconds=1)).isoformat()
        with self.assertRaises(ValueError):
            m.collect_feeds(cfg, offline, b.network, b.collapse, snapshot)
        with self.assertRaises(ValueError):
            m.collect_feeds(cfg, offline, b.network, b.collapse)

    def test_geofeed_snapshot_does_not_extend_publication_lifetime(self):
        now = datetime.now(timezone.utc)
        published = now - timedelta(days=7)
        cfg = [{'name': 'test', 'url': 'https://source.example/feed', 'format': 'geofeed',
                'min_entries': 2, 'max_entries': 10, 'families': [4, 6], 'max_age_days': 8}]
        raw = '# Publication date: ' + published.strftime('%a %b %d %Y') + '\n'
        raw += '8.8.8.0/24,US,,City,\n2606:4700::/32,US,,City,\n'
        snapshot = {}
        m.collect_feeds(cfg, lambda url: raw, b.network, b.collapse, snapshot)
        self.assertLess(datetime.fromisoformat(snapshot['test']['expires_at']) - now, timedelta(days=1))

    def test_inventory_deadline_does_not_wait_for_running_workers(self):
        cfg = self.cfg(); cfg['deadline_seconds'] = .02
        release, started = threading.Event(), threading.Event()
        def query(*args):
            started.set()
            release.wait(2)
            return {'status': 3, 'ips': [], 'ttl': None}
        start = time.monotonic()
        try:
            with self.assertRaises(TimeoutError):
                m.collect_dns(cfg, lambda url: 'mmg.whatsapp.net', b.domain, b.collapse, query=query)
            self.assertTrue(started.is_set())
            self.assertLess(time.monotonic() - start, .5)
        finally:
            release.set()

    def test_query_does_not_start_a_request_after_deadline(self):
        with patch.object(m.DNS_OPENER, 'open') as opened, self.assertRaises(m.TemporaryDNSFailure):
            m.query_dns('mmg.whatsapp.net', 'A', 'https://dns.google/resolve', deadline=time.monotonic() - 1)
        opened.assert_not_called()

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

    def test_small_transport_failure_is_reported_but_poison_is_fatal(self):
        cfg=self.cfg();cfg.update(max_failed_questions=1,max_failed_ratio=0.25)
        def query(host,kind,endpoint):
            if host=='g.whatsapp.net' and kind=='AAAA':raise m.TemporaryDNSFailure('timeout')
            return {'status':0,'ips':['8.8.8.8' if kind=='A' else '2606:4700::1111'],'ttl':60}
        fetch=lambda url:'g.whatsapp.net\nmmg.whatsapp.net'
        hosts,ips,stats,observations=m.collect_dns(cfg,fetch,b.domain,b.collapse,query=query)
        self.assertEqual(stats['failed_questions'],1)
        self.assertEqual(observations['g.whatsapp.net']['AAAA']['ips'],[])
        cfg['max_failed_ratio']=0.1
        with self.assertRaises(RuntimeError):m.collect_dns(cfg,fetch,b.domain,b.collapse,query=query)
        def poison(*args):raise ValueError('unsafe answer')
        with self.assertRaises(ValueError):m.collect_dns(self.cfg(),fetch,b.domain,b.collapse,query=poison)

    def test_query_uses_fresh_fallback_and_never_retries_poison(self):
        payload=self.answer()
        response=MagicMock();response.__enter__.return_value.read.return_value=json.dumps(payload)
        with patch.object(m.DNS_OPENER,'open',side_effect=[OSError('offline'), response]) as opened, patch.object(m.time,'sleep') as sleep:
            result=m.query_dns('mmg.whatsapp.net','A','https://dns.google/resolve')
            self.assertEqual(result['resolver'],'https://cloudflare-dns.com/dns-query')
            self.assertEqual(opened.call_count,2)
            self.assertEqual(opened.call_args_list[0].kwargs['timeout'], 3)
            self.assertEqual(opened.call_args_list[1].kwargs['timeout'], 10)
            sleep.assert_not_called()
        response.__enter__.return_value.read.return_value=json.dumps(self.answer('127.0.0.1'))
        with patch.object(m.DNS_OPENER,'open',return_value=response) as opened:
            with self.assertRaises(ValueError):m.query_dns('mmg.whatsapp.net','A','https://dns.google/resolve')
            self.assertEqual(opened.call_count,1)

    def response(self, payload):
        result = MagicMock()
        result.__enter__.return_value.read.return_value = json.dumps(payload)
        return result

    def test_unavailable_resolvers_still_get_three_attempts_each(self):
        with patch.object(m.DNS_OPENER, 'open', side_effect=OSError('offline')) as opened, patch.object(m.time, 'sleep'):
            with self.assertRaises(m.TemporaryDNSFailure):
                m.query_dns('mmg.whatsapp.net', 'A', 'https://dns.google/resolve')
        self.assertEqual([call.args[0].host for call in opened.call_args_list],
                         ['dns.google', 'cloudflare-dns.com'] * 3)
        self.assertEqual([call.kwargs['timeout'] for call in opened.call_args_list], [3, 10, 10, 10, 10, 10])

    def test_transport_backoff_is_shared_and_expires(self):
        state = m.DNSResolverState()
        positive = self.response(self.answer())
        with patch.object(m.time, 'monotonic', return_value=100), patch.object(
                m.DNS_OPENER, 'open', side_effect=[OSError('offline'), positive]) as opened:
            m.query_dns('mmg.whatsapp.net', 'A', 'https://dns.google/resolve', state=state)
            self.assertEqual(opened.call_count, 2)
        with patch.object(m.time, 'monotonic', return_value=101), patch.object(
                m.DNS_OPENER, 'open', return_value=positive) as opened:
            m.query_dns('mmg.whatsapp.net', 'A', 'https://dns.google/resolve', state=state)
            self.assertEqual(opened.call_args.args[0].host, 'cloudflare-dns.com')
        with patch.object(m.time, 'monotonic', return_value=161), patch.object(
                m.DNS_OPENER, 'open', return_value=positive) as opened:
            m.query_dns('mmg.whatsapp.net', 'A', 'https://dns.google/resolve', state=state)
            self.assertEqual(opened.call_args.args[0].host, 'dns.google')

    def test_servfail_does_not_disable_primary_for_other_hosts(self):
        state = m.DNSResolverState()
        failure = self.response({'Status': 2, 'Question': [{'name': 'mmg.whatsapp.net', 'type': 1}]})
        with patch.object(m.DNS_OPENER, 'open', side_effect=[failure, self.response(self.answer())]):
            m.query_dns('mmg.whatsapp.net', 'A', 'https://dns.google/resolve', state=state)
        self.assertEqual(state.fallback_until, 0)

    def test_empty_fallback_cannot_hide_a_positive_primary(self):
        empty = self.response({'Status': 3, 'Question': [{'name': 'mmg.whatsapp.net', 'type': 1}]})
        with patch.object(m.DNS_OPENER, 'open', side_effect=[OSError('offline'), empty,
                          self.response(self.answer())]) as opened, patch.object(m.time, 'sleep'):
            result = m.query_dns('mmg.whatsapp.net', 'A', 'https://dns.google/resolve')
        self.assertEqual(result['ips'], ['8.8.8.8'])
        self.assertEqual(result['resolver'], 'https://dns.google/resolve')
        self.assertEqual(opened.call_count, 3)

    def test_valid_empty_fallback_is_kept_if_primary_stays_unavailable(self):
        empty = self.response({'Status': 3, 'Question': [{'name': 'mmg.whatsapp.net', 'type': 1}]})
        with patch.object(m.DNS_OPENER, 'open', side_effect=[OSError('offline'), empty] * 3) as opened, patch.object(m.time, 'sleep'):
            result = m.query_dns('mmg.whatsapp.net', 'A', 'https://dns.google/resolve')
        self.assertEqual(result['ips'], [])
        self.assertEqual(result['status'], 3)
        self.assertEqual(opened.call_count, 6)

    def test_fast_fallback_still_checks_every_host_and_both_families(self):
        cfg = self.cfg()
        source = 'mmg.whatsapp.net\ng.whatsapp.net'
        questions, primary_questions = [], []
        lock = threading.Lock()
        def respond(request, **kwargs):
            from urllib.parse import parse_qs, urlsplit
            params = parse_qs(urlsplit(request.full_url).query)
            host, kind = params['name'][0], params['type'][0]
            if request.host == 'dns.google':
                with lock:
                    primary_questions.append((host, kind))
                raise OSError('primary offline')
            with lock:
                questions.append((host, kind))
            number = 1 if kind == 'A' else 28
            if host == 'g.whatsapp.net':
                return self.response({'Status': 3, 'Question': [{'name': host, 'type': number}]})
            return self.response({'Status': 0, 'Question': [{'name': host, 'type': number}],
                                 'Answer': [{'name': host, 'type': number, 'TTL': 30,
                                             'data': '8.8.8.8' if kind == 'A' else '2606:4700::1111'}]})
        with patch.object(m.DNS_OPENER, 'open', side_effect=respond):
            hosts, prefixes, stats, observations = m.collect_dns(cfg, lambda url: source, b.domain, b.collapse)
        self.assertEqual(set(questions), {(host, kind) for host in hosts for kind in ('A', 'AAAA')})
        self.assertEqual(stats['questions'], 4)
        self.assertEqual(stats['failed_questions'], 0)
        self.assertEqual(stats['fallback_answers'], 4)
        self.assertEqual(stats['resolved_hosts'], 1)
        self.assertEqual(observations['g.whatsapp.net']['A']['status'], 3)
        self.assertLessEqual(len(primary_questions), cfg['workers'])
        self.assertEqual(set(prefixes), {'8.8.8.8/32', '2606:4700::1111/128'})

    def test_poisoned_fallback_is_fatal_and_not_retried(self):
        poisoned = self.response(self.answer('127.0.0.1'))
        with patch.object(m.DNS_OPENER, 'open', side_effect=[OSError('offline'), poisoned]) as opened:
            with self.assertRaises(ValueError):
                m.query_dns('mmg.whatsapp.net', 'A', 'https://dns.google/resolve')
        self.assertEqual(opened.call_count, 2)


if __name__ == '__main__':unittest.main()
