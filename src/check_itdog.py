"""Fail a scheduled build if either ITDog publication is missing this week."""
import json
from datetime import datetime, timedelta, timezone
from build import fetch


def verify(runs, now):
    monday = (now - timedelta(days=now.weekday())).replace(hour=0, minute=0, second=0, microsecond=0)
    for path in ('.github/workflows/create-lists.yml', '.github/workflows/create-subnets.yml'):
        candidates = [r for r in runs if r['path'] == path and r['event'] == 'schedule'
                      and r['head_branch'] == 'main']
        if not candidates:
            raise ValueError('ITDog scheduled run missing: ' + path)
        latest = max(candidates, key=lambda r: r['created_at'])
        start = datetime.fromisoformat(latest['created_at'].replace('Z', '+00:00'))
        finish = datetime.fromisoformat(latest['updated_at'].replace('Z', '+00:00'))
        if not monday <= start <= finish <= now or latest['status'] != 'completed' or latest['conclusion'] != 'success':
            raise ValueError('ITDog publication not successfully completed this week: ' + path)
        # Leave a ten-minute window for raw content/CDN propagation.
        if now - finish < timedelta(minutes=10):
            raise ValueError('ITDog publication too recent; wait for propagation')


if __name__ == '__main__':
    data = json.loads(fetch('https://api.github.com/repos/itdoginfo/allow-domains/actions/runs?per_page=100'))
    verify(data['workflow_runs'], datetime.now(timezone.utc))
    print('ITDog lists and subnets: successful scheduled publications this week')
