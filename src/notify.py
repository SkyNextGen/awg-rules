"""Never log request URLs, Telegram responses, or credentials."""
import json
import os
from pathlib import Path
import subprocess
from urllib.parse import urlencode
from urllib.request import Request, urlopen
from report import telegram_text

STEP_FAILURES = {
    'checkout': 'Не удалось получить код репозитория с GitHub.',
    'baseline': 'Не удалось загрузить предыдущую версию списка для сравнения.',
    'python': 'Не удалось подготовить Python для сборки.',
    'tests': 'Один из автоматических тестов сборщика завершился ошибкой.',
    'compiler': 'Не удалось скачать или проверить компилятор sing-box.',
    'replay': 'Не прошла контрольная пересборка предыдущей версии списка.',
    'dns_probe': 'Не прошла подготовка или проверка DNS в sing-box.',
    'build': 'Ошибка при сборке или проверке списка маршрутов. Подробности есть в журнале.',
    'coverage': 'Итоговый список не прошёл проверку покрытия сервисов.',
    'routing_probe': 'Не прошла подготовка или проверка правил на движках sing-box и AWGM.',
    'report': 'Не удалось подготовить отчёт сборки.',
    'publish': 'Не удалось завершить публикацию списка на GitHub.',
}


def failure_reason(steps, status):
    for name, reason in STEP_FAILURES.items():
        step = steps.get(name, {})
        if step.get('outcome') == 'failure':
            if name == 'build':
                return step.get('outputs', {}).get('reason') or reason
            return reason
    if status == 'cancelled':
        return 'Запуск отменён или остановлен до завершения.'
    return 'Не удалось определить этап сбоя. Подробности есть в журнале запуска.'


def published_list(initial_sha, publish_outcome):
    """Confirm the public branch before claiming that an older list remains."""
    if not initial_sha:
        return 'unknown'
    try:
        remote = subprocess.check_output(
            ['git', 'ls-remote', 'origin', 'refs/heads/main'],
            text=True, stderr=subprocess.DEVNULL, timeout=10).split()
        if not remote:
            return 'unknown'
        if remote[0] == initial_sha:
            version, state = initial_sha, 'previous'
        elif publish_outcome == 'success':
            version = subprocess.check_output(
                ['git', 'rev-parse', 'HEAD'], text=True, stderr=subprocess.DEVNULL, timeout=5).strip()
            if version != remote[0]:
                return 'unknown'
            state = 'new'
        else:
            return 'unknown'
        entry = subprocess.check_output(
            ['git', 'ls-tree', version, '--', 'dist/routing.srs'],
            text=True, stderr=subprocess.DEVNULL, timeout=5)
        return state if entry.strip() else 'absent'
    except (OSError, subprocess.SubprocessError):
        return 'unknown'


def main():
    token, chat = os.getenv('TG_BOT_TOKEN'), os.getenv('TG_CHAT_ID')
    if not token or not chat:
        print('Telegram skipped: configure both GitHub Secrets')
        return
    url = f"https://github.com/{os.environ['GITHUB_REPOSITORY']}/actions/runs/{os.environ['GITHUB_RUN_ID']}"
    status = os.getenv('BUILD_STATUS', 'unknown')
    report = {}
    path = Path('dist/report.json')
    if path.exists() and status == 'success':
        report = json.loads(path.read_text(encoding='utf-8'))
    if status == 'success':
        text = telegram_text(report, run_url=url)
    else:
        steps = json.loads(os.getenv('BUILD_STEPS', '{}'))
        publication = published_list(os.getenv('GITHUB_SHA'), steps.get('publish', {}).get('outcome'))
        text = telegram_text(report, status=status, run_url=url,
                             reason=failure_reason(steps, status), publication=publication)
    try:
        body = urlencode({'chat_id': chat, 'text': text, 'disable_web_page_preview': 'true'}).encode()
        with urlopen(Request(f'https://api.telegram.org/bot{token}/sendMessage', data=body), timeout=20) as response:
            if not json.load(response).get('ok'):
                print('Telegram delivery failed')
    except Exception:
        print('Telegram delivery failed; credentials and response suppressed')


if __name__ == '__main__':
    main()
