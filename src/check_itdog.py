"""Report upstream workflow health; source data is validated by the builder."""
import json
from datetime import datetime, timedelta, timezone

RUNS_URL = 'https://api.github.com/repos/itdoginfo/allow-domains/actions/runs?per_page=100'


def publication_warnings(runs, now):
    monday = (now - timedelta(days=now.weekday())).replace(hour=0, minute=0, second=0, microsecond=0)
    warnings = []
    for path in ('.github/workflows/create-lists.yml', '.github/workflows/create-subnets.yml'):
        candidates = [r for r in runs if r['path'] == path and r['event'] == 'schedule'
                      and r['head_branch'] == 'main']
        if not candidates:
            warnings.append('ITDog scheduled run missing; source data will be checked independently: ' + path)
            continue
        latest = max(candidates, key=lambda r: r['created_at'])
        successful = []
        for run in candidates:
            start = datetime.fromisoformat(run['created_at'].replace('Z', '+00:00'))
            finish = datetime.fromisoformat(run['updated_at'].replace('Z', '+00:00'))
            if (run['status'] == 'completed' and run['conclusion'] == 'success'
                    and now - timedelta(days=8) <= start <= finish <= now - timedelta(minutes=10)):
                successful.append(run)
        if not successful:
            warnings.append('ITDog has no successful publication within 8 days; source data will be checked independently: ' + path)
            continue
        accepted = max(successful, key=lambda r: r['created_at'])
        if accepted is not latest or datetime.fromisoformat(accepted['created_at'].replace('Z', '+00:00')) < monday:
            warnings.append('ITDog delayed/failed weekly publication; source data will be checked independently: ' + path)
    return warnings


def check_publication(fetch, now):
    try:
        data = json.loads(fetch(RUNS_URL))
        return publication_warnings(data['workflow_runs'], now)
    except (OSError, RuntimeError, ValueError, KeyError, TypeError) as error:
        return ['ITDog workflow status unavailable; source data will be checked independently: ' + str(error)]


if __name__ == '__main__':
    from build import fetch
    for warning in check_publication(fetch, datetime.now(timezone.utc)):
        print(warning)
    print('ITDog workflow status is advisory; source validation is performed by the builder')
