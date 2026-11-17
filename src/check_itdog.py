"""Require a recent successful ITDog publication; report delayed weekly runs."""
import json
from datetime import datetime, timedelta, timezone


def verify(runs, now):
    monday = (now - timedelta(days=now.weekday())).replace(hour=0, minute=0, second=0, microsecond=0)
    warnings = []
    for path in ('.github/workflows/create-lists.yml', '.github/workflows/create-subnets.yml'):
        candidates = [r for r in runs if r['path'] == path and r['event'] == 'schedule'
                      and r['head_branch'] == 'main']
        if not candidates:
            raise ValueError('ITDog scheduled run missing: ' + path)
        latest = max(candidates, key=lambda r: r['created_at'])
        successful = []
        for run in candidates:
            start = datetime.fromisoformat(run['created_at'].replace('Z', '+00:00'))
            finish = datetime.fromisoformat(run['updated_at'].replace('Z', '+00:00'))
            if (run['status'] == 'completed' and run['conclusion'] == 'success'
                    and now - timedelta(days=8) <= start <= finish <= now - timedelta(minutes=10)):
                successful.append(run)
        if not successful:
            raise ValueError('ITDog has no successful publication within 8 days: ' + path)
        accepted = max(successful, key=lambda r: r['created_at'])
        if accepted is not latest or datetime.fromisoformat(accepted['created_at'].replace('Z', '+00:00')) < monday:
            warnings.append('ITDog delayed/failed weekly publication; using recent successful publication: ' + path)
    return warnings


if __name__ == '__main__':
    from build import fetch
    data = json.loads(fetch('https://api.github.com/repos/itdoginfo/allow-domains/actions/runs?per_page=100'))
    for warning in verify(data['workflow_runs'], datetime.now(timezone.utc)):
        print(warning)
    print('ITDog lists and subnets: recent successful scheduled publications')
