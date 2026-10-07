"""Never log request URLs, Telegram responses, or credentials."""
import json
import os
from pathlib import Path
from urllib.parse import urlencode
from urllib.request import Request, urlopen


def main():
    token, chat = os.getenv('TG_BOT_TOKEN'), os.getenv('TG_CHAT_ID')
    if not token or not chat:
        print('Telegram skipped: configure both GitHub Secrets')
        return
    url = f"https://github.com/{os.environ['GITHUB_REPOSITORY']}/actions/runs/{os.environ['GITHUB_RUN_ID']}"
    text = 'awg-rules: ' + os.getenv('BUILD_STATUS', 'unknown') + '\n' + url
    path = Path('dist/report.json')
    if path.exists() and os.getenv('BUILD_STATUS') == 'success':
        report = json.loads(path.read_text())
        text += f"\nDomains: {report['domains']}; IPv4: {report['ipv4']}; IPv6: {report['ipv6']}"
        text += '\n' + '\n'.join(report['warnings'])
    try:
        body = urlencode({'chat_id': chat, 'text': text[:4000], 'disable_web_page_preview': 'true'}).encode()
        with urlopen(Request(f'https://api.telegram.org/bot{token}/sendMessage', data=body), timeout=20) as response:
            if not json.load(response).get('ok'):
                print('Telegram delivery failed')
    except Exception:
        print('Telegram delivery failed; credentials and response suppressed')


if __name__ == '__main__':
    main()
