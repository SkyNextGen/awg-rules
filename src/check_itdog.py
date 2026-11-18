"""Report upstream workflow health; source data is validated by the builder."""
import json
import logging
from datetime import datetime, timedelta, timezone

RUNS_URL = 'https://api.github.com/repos/itdoginfo/allow-domains/actions/runs?per_page=100'


def publication_warnings(runs, now):
    monday = (now - timedelta(days=now.weekday())).replace(hour=0, minute=0, second=0, microsecond=0)
    warnings = []
    for path, list_name in (('.github/workflows/create-lists.yml', 'списка доменов'),
                            ('.github/workflows/create-subnets.yml', 'списка IP-подсетей')):
        candidates = [r for r in runs if r['path'] == path and r['event'] == 'schedule'
                      and r['head_branch'] == 'main']
        if not candidates:
            warnings.append(f'В истории ITDog нет плановых запусков для обновления {list_name}.')
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
            message = f'У ITDog за последние 8 дней не было успешного обновления {list_name}.'
            if latest['conclusion'] == 'failure':
                message += ' Последняя попытка завершилась ошибкой.'
            warnings.append(message)
            continue
        accepted = max(successful, key=lambda r: r['created_at'])
        if accepted is not latest or datetime.fromisoformat(accepted['created_at'].replace('Z', '+00:00')) < monday:
            if latest['conclusion'] == 'failure':
                warnings.append(f'Последнее обновление {list_name} у ITDog завершилось ошибкой.')
            else:
                warnings.append(f'Еженедельное обновление {list_name} у ITDog ещё не подтверждено.')
    return warnings


def check_publication(fetch, now):
    try:
        data = json.loads(fetch(RUNS_URL))
        return publication_warnings(data['workflow_runs'], now)
    except (OSError, RuntimeError, ValueError, KeyError, TypeError) as error:
        logging.warning('Could not check ITDog workflow history: %s', error)
        return ['Не удалось проверить, когда ITDog обновлял свои списки.']


if __name__ == '__main__':
    from build import fetch
    for warning in check_publication(fetch, datetime.now(timezone.utc)):
        print(warning)
    print('ITDog workflow status is advisory; source validation is performed by the builder')
