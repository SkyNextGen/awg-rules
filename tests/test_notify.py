from datetime import timedelta
import subprocess
import sys
import unittest
from pathlib import Path
from unittest.mock import patch

sys.path.insert(0, str(Path(__file__).parents[1] / 'src'))
from build_failure import build_reason
from freshness import FreshnessError, age_detail
from notify import failure_reason, published_list
from report import telegram_text


class FailureNotificationTests(unittest.TestCase):
    def test_freshness_error_reports_elapsed_time_in_telegram(self):
        reason = build_reason(FreshnessError('Копия устарела. ' + age_detail(timedelta(days=14, hours=2))))
        text = telegram_text({}, status='failure', reason=reason, publication='previous')
        self.assertIn('Копия устарела. Возраст данных — 14 дней 2 ч.', text)
        self.assertEqual(age_detail(timedelta(minutes=-17)), 'Дата на 17 мин позже текущего времени.')

    def test_build_error_reaches_telegram_without_raw_exception_details(self):
        reason = build_reason(RuntimeError(
            'Source fetch failed: https://www.meta.com/peering/geofeed/?secret=redacted: HTTP 503'))
        steps = {'build': {'outcome': 'failure', 'outputs': {'reason': reason}},
                 'publish': {'outcome': 'skipped'}}
        text = telegram_text({}, status='failure', reason=failure_reason(steps, 'failure'),
                             publication='previous')
        self.assertIn('Не удалось скачать обязательный источник с www.meta.com', text)
        self.assertIn('На GitHub остался предыдущий опубликованный список.', text)
        self.assertNotIn('secret=', text)

    def test_common_build_failures_explain_why_processing_stopped(self):
        cases = [
            (RuntimeError('WhatsApp DNS failures exceed allowed threshold'), 'список ip получился неполным'),
            (TimeoutError('10 (of 4538) futures unfinished'), 'за отведённое время'),
            (ValueError('AS32934: no valid live data or fresh snapshot'), 'резервной копии тоже нет'),
            (ValueError('Missing generated service coverage: discord.example'), 'потерял обязательные'),
        ]
        for error, expected in cases:
            with self.subTest(error=error):
                self.assertIn(expected, build_reason(error).lower())

    def test_failure_outside_build_names_the_step(self):
        steps = {'tests': {'outcome': 'success'}, 'publish': {'outcome': 'failure'}}
        self.assertIn('публикацию', failure_reason(steps, 'failure'))
        self.assertIn('автоматических тестов', failure_reason({'tests': {'outcome': 'failure'}}, 'failure'))
        self.assertIn('отменён', failure_reason({}, 'cancelled'))

    def test_publication_status_uses_remote_ref_and_artifact(self):
        scenarios = [
            ('skipped', ['aaa refs/heads/main\n', '100644 blob abc\tdist/routing.srs\n'], 'previous'),
            ('failure', ['aaa refs/heads/main\n', '100644 blob abc\tdist/routing.srs\n'], 'previous'),
            ('failure', ['bbb refs/heads/main\n'], 'unknown'),
            ('skipped', ['aaa refs/heads/main\n', ''], 'absent'),
            ('success', ['bbb refs/heads/main\n', 'bbb\n', '100644 blob abc\tdist/routing.srs\n'], 'new'),
            ('failure', [subprocess.TimeoutExpired('git ls-remote', 10)], 'unknown'),
        ]
        for outcome, responses, expected in scenarios:
            with self.subTest(outcome=outcome, expected=expected), patch(
                    'notify.subprocess.check_output', side_effect=responses):
                self.assertEqual(published_list('aaa', outcome), expected)

    def test_unconfirmed_publication_does_not_claim_old_list_is_available(self):
        text = telegram_text({}, status='failure', publication='unknown')
        self.assertIn('Не удалось подтвердить', text)
        self.assertNotIn('остался предыдущий', text)
