"""Report upstream workflow health; source data is validated by the builder."""
import json
import logging
from datetime import datetime, timedelta, timezone
from freshness import format_age
from report import moscow_time

API = 'https://api.github.com/repos/itdoginfo/allow-domains/actions/runs'
RUNS_URL = API + '?branch=main&event=schedule&per_page=100'


def confirmed_finish(fetch, run, job_name, now):
    run_id, attempt = run['id'], run['run_attempt']
    jobs = json.loads(fetch(f'{API}/{run_id}/attempts/{attempt}/jobs'))['jobs']
    for job in jobs:
        if (job['name'] == job_name and job['run_id'] == run_id and job['run_attempt'] == attempt
                and job['conclusion'] == 'success' and job.get('completed_at')):
            start = datetime.fromisoformat(run['created_at'])
            finish = datetime.fromisoformat(job['completed_at'])
            if start <= datetime.fromisoformat(job['started_at']) <= finish <= now:
                return finish
    return None


def publication_warnings(runs, now, finish_of):
    monday = (now - timedelta(days=now.weekday())).replace(hour=0, minute=0, second=0, microsecond=0)
    warnings = []
    for path, list_name, job_name in (
            ('.github/workflows/create-lists.yml', 'доменных списков', 'generate-lists'),
            ('.github/workflows/create-subnets.yml', 'IP-подсетей', 'generate-subnet')):
        candidates = [r for r in runs if r['path'] == path and r['event'] == 'schedule'
                      and r['head_branch'] == 'main']
        if not candidates:
            warnings.append(f'В истории ITDog нет плановых запусков для обновления {list_name}.')
            continue
        latest = max(candidates, key=lambda r: r['created_at'])
        successful = max((r for r in candidates if r['status'] == 'completed' and r['conclusion'] == 'success'),
                         key=lambda r: r['created_at'], default=None)
        if successful is None:
            message = f'В истории ITDog нет успешной сборки {list_name}.'
        else:
            try:
                finish = finish_of(successful, job_name, now)
            except (OSError, RuntimeError, ValueError, KeyError, TypeError) as error:
                logging.warning('Could not verify ITDog job completion: %s', error)
                finish = None
            if finish is None:
                message = f'Не удалось подтвердить дату успешной сборки {list_name} у ITDog.'
            else:
                start = datetime.fromisoformat(successful['created_at'])
                if (successful is latest and start >= monday and now - timedelta(days=8) <= start
                        and finish <= now - timedelta(minutes=10)):
                    continue
                message = (f'У ITDog успешная сборка {list_name} №{successful["id"]} завершилась '
                           f'{moscow_time(finish.isoformat())} ({format_age(now - finish)} назад).')
        if latest['conclusion'] == 'failure':
            message += ' Последняя попытка завершилась ошибкой.'
        warnings.append(message)
    return warnings


def check_publication(fetch, now):
    try:
        data = json.loads(fetch(RUNS_URL))
        return [message + ' Сами списки проверяются отдельно.'
                for message in publication_warnings(
                    data['workflow_runs'], now, lambda run, name, at: confirmed_finish(fetch, run, name, at))]
    except (OSError, RuntimeError, ValueError, KeyError, TypeError) as error:
        logging.warning('Could not check ITDog workflow history: %s', error)
        return ['Не удалось проверить, когда ITDog обновлял свои списки. Сами списки проверяются отдельно.']


if __name__ == '__main__':
    from build import fetch
    for warning in check_publication(fetch, datetime.now(timezone.utc)):
        print(warning)
    print('ITDog workflow status is advisory; source validation is performed by the builder')
