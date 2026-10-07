"""Never log request URLs, Telegram responses, or credentials."""
import json
import os
from pathlib import Path
from urllib.parse import urlencode
from urllib.request import Request, urlopen
from report import telegram_text


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
    text = telegram_text(report, status=status, run_url=url)
    try:
        body = urlencode({'chat_id': chat, 'text': text, 'disable_web_page_preview': 'true'}).encode()
        with urlopen(Request(f'https://api.telegram.org/bot{token}/sendMessage', data=body), timeout=20) as response:
            if not json.load(response).get('ok'):
                print('Telegram delivery failed')
    except Exception:
        print('Telegram delivery failed; credentials and response suppressed')


if __name__ == '__main__':
    main()
