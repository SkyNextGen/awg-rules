"""Russian Markdown and plain-text Telegram reports from verified build data."""
from datetime import datetime, timedelta, timezone
import ipaddress
import json
from pathlib import Path

REPORT_URL = 'https://github.com/SkyNextGen/awg-rules/blob/main/dist/report.md'
KEYS = ('domain_suffix', 'domain', 'domain_keyword', 'domain_regex')


def records(rule):
    return sorted(f'{key}:{value}' for key in KEYS for value in rule.get(key, []))


def delta(current, previous):
    if previous is None:
        return {'baseline': False, 'added': [], 'removed': [], 'added_count': None, 'removed_count': None}
    added, removed = sorted(set(current) - set(previous)), sorted(set(previous) - set(current))
    return {'baseline': True, 'added': added, 'removed': removed, 'added_count': len(added), 'removed_count': len(removed)}


def change_text(change):
    return f"+{change['added_count']} / -{change['removed_count']}" if change['baseline'] else 'первый снимок — сравнение со следующего запуска'


def moscow_time(value):
    return datetime.fromisoformat(value.replace('Z', '+00:00')).astimezone(timezone(timedelta(hours=3))).strftime('%d.%m.%Y, %H:%M МСК')


def write_report(report, payload, source_records, staging, dist, old):
    previous_payload = json.loads((dist / 'routing.json').read_text(encoding='utf-8')) if (dist / 'routing.json').exists() else None
    previous_rule = previous_payload['rules'][0] if previous_payload else None
    prior_sources = json.loads((dist / 'source-snapshot.json').read_text(encoding='utf-8')) if (dist / 'source-snapshot.json').exists() else {}
    current_rule = payload['rules'][0]
    changes = {'domains': delta(records(current_rule), records(previous_rule) if previous_rule else None)}
    for version in (4, 6):
        current = [p for p in current_rule['ip_cidr'] if ipaddress.ip_network(p).version == version]
        before = [p for p in previous_rule['ip_cidr'] if ipaddress.ip_network(p).version == version] if previous_rule else None
        changes['ipv' + str(version)] = delta(current, before)
    source_changes = {name: delta(values, prior_sources.get(name)) for name, values in source_records.items()}
    for name in prior_sources.keys() - source_records.keys():
        source_changes[name] = delta([], prior_sources[name])
    report['changes'] = changes
    report['source_changes'] = source_changes
    report['compared_to'] = old.get('built_at')
    history_path = dist / 'history.json'
    history = json.loads(history_path.read_text(encoding='utf-8')) if history_path.exists() else []
    if not history and old.get('built_at'):
        history.append({k: old[k] for k in ('built_at', 'domains', 'ipv4', 'ipv6')})
    prior = history[-1] if history else None
    history.append({k: report[k] for k in ('built_at', 'domains', 'ipv4', 'ipv6')})
    history = history[-52:]
    recent = history[-7:]
    trend = {k: {'average': round(sum(x[k] for x in recent) / len(recent), 1), 'delta': report[k] - prior[k] if prior else None} for k in ('domains', 'ipv4', 'ipv6')}
    report['trend'] = {'runs': len(recent), 'metrics': trend}
    body = [
        '# 📊 Отчёт сборки правил AWG', '', '## 🧭 Общая информация', '',
        f"> 🕒 **Сборка:** {moscow_time(report['built_at'])}  ",
        '> 📦 **Репозиторий:** SkyNextGen/awg-rules  ',
        '> 📄 **Файлы:** `dist/routing.json` и `dist/routing.srs`  ',
        '> 🗓 **Расписание:** понедельник, 06:23 МСК; также вручную и после изменения кода/настроек  ',
        f"> 🔄 **Сравнение со сборкой:** {moscow_time(report['compared_to']) if report['compared_to'] else 'первый запуск'}", '',
        '---', '', '## 🧮 Итог сборки', '',
        '| Показатель | Всего | Добавлено / удалено |', '|---|---:|---|',
        f"| Доменные правила | {report['domains']} | {change_text(changes['domains'])} |",
        f"| IPv4-префиксы | {report['ipv4']} | {change_text(changes['ipv4'])} |",
        f"| IPv6-префиксы | {report['ipv6']} | {change_text(changes['ipv6'])} |", '',
        f"Другие доменные условия (keyword/regexp): **{sum(report['matchers'].get(k, 0) for k in ('domain_keyword', 'domain_regex'))}**. Они также учитываются в списке изменений.", '',
        '**Обрезка:** НЕТ. Проверены допустимые размеры, сети и обратное преобразование JSON → SRS → JSON.', '',
        'Изменения показывают записи правил: укрупнение CIDR или замена поддоменов одним suffix может изменить счётчики без потери покрытия.', '',
        '## 🚦 Статус', '', '### ✅ Сборка завершена', '',
    ]
    warnings = report['warnings']
    body += ['### ⚠️ Предупреждения', ''] + ['- ' + x for x in warnings] if warnings else ['### 🟢 Предупреждений нет']
    body += ['', '## 📌 Сводка источников', '', '| Источник | Уникальных записей до объединения | Добавлено / удалено |', '|---|---:|---|']
    for name in sorted(source_changes):
        body.append(f"| {name} | {len(source_records.get(name, []))} | {change_text(source_changes[name])} |")
    body += ['', 'Записи разных источников могут пересекаться, поэтому сумма строк этой таблицы не равна итоговому числу правил. Для нового формата источников первый запуск сохраняет базу сравнения.', '',
             '## 📈 Тренд за последние успешные запуски', '',
             f"Использовано запусков: **{len(recent)} из 7**. Сравнение выполняется с предыдущей успешной сборкой, включая ручные запуски.", '',
             '| Показатель | Среднее | Δ к прошлой |', '|---|---:|---:|']
    for key, label in (('domains', 'Домены'), ('ipv4', 'IPv4'), ('ipv6', 'IPv6')):
        item = trend[key]
        body.append(f"| {label} | {item['average']} | {item['delta']:+d} |" if item['delta'] is not None else f"| {label} | {item['average']} | — |")
    body += ['', '| Сборка (МСК) | Домены | IPv4 | IPv6 |', '|---|---:|---:|---:|']
    for row in recent:
        body.append(f"| {moscow_time(row['built_at'])} | {row['domains']} | {row['ipv4']} | {row['ipv6']} |")
    body += ['', '## 🌐 BGP и fallback', '', '| ASN | Источник | Префиксов до общего объединения | Получено (МСК) |', '|---|---|---:|---|']
    for asn, row in report['asns'].items():
        body.append(f"| AS{asn} | {row['source']} | {len(row['prefixes'])} | {moscow_time(row['fetched_at'])} |")
    body += ['', '## 🔐 SHA256', '']
    for name, sha in report['sha256'].items():
        body.append(f'- `{name}`: `{sha}`')
    body += ['', '<details>', '<summary>🔄 Изменения — первые 20 записей в каждой группе</summary>', '']
    for name, change in list(changes.items()) + sorted(source_changes.items()):
        body += [f'### {name}', '']
        if not change['baseline']:
            body += ['Первый снимок; предыдущего набора нет.', '']
            continue
        for key, label in (('added', '➕ Добавлено'), ('removed', '➖ Удалено')):
            values = change[key]
            body += [f'**{label}: {len(values)}**', '']
            body += ['- `' + x.replace('`', '\\`') + '`' for x in values[:20]] or ['- —']
            if len(values) > 20:
                body.append(f'- … ещё {len(values) - 20}; полный список в `dist/report.json`.')
            body.append('')
    body += ['</details>', '']
    (staging / 'report.md').write_text('\n'.join(body), encoding='utf-8')
    (staging / 'report.json').write_text(json.dumps(report, indent=2, ensure_ascii=False) + '\n', encoding='utf-8')
    (staging / 'source-snapshot.json').write_text(json.dumps(source_records, indent=2) + '\n', encoding='utf-8')
    (staging / 'history.json').write_text(json.dumps(history, indent=2) + '\n', encoding='utf-8')
    (staging / 'tg_message.txt').write_text(telegram_text(report), encoding='utf-8')


def telegram_text(report, status='success', run_url=''):
    if status != 'success':
        return '\n'.join(['📦 BUILD SYSTEM · AWG RULES', '🔴 GitHub Actions', '━━━━━━━━━━━━━━━━━━', '🔥 CRITICAL', '', '🔴 СТАТУС СБОРКИ: ОШИБКА' if status == 'failure' else '🟠 СТАТУС СБОРКИ: ' + status, '', 'Новый список не опубликован. Используется последний проверенный результат.', 'Подробности ошибки — в Actions.', '', '🔗 Actions: ' + run_url])
    warnings = report['warnings']
    change = report['changes']
    trend = report['trend']
    domain_delta = trend['metrics']['domains']['delta']
    direction = '➡️ Стабильно' if domain_delta == 0 else ('📈 Рост' if domain_delta and domain_delta > 0 else ('📉 Падение' if domain_delta is not None else 'Первый запуск'))
    text = ['📦 BUILD SYSTEM · AWG RULES', '🟠 GitHub Actions' if warnings else '🟢 GitHub Actions', '━━━━━━━━━━━━━━━━━━', '⚠️ WARNING' if warnings else '🧩 INFO', '', '🟠 СТАТУС СБОРКИ: ПРЕДУПРЕЖДЕНИЕ' if warnings else '🟢 СТАТУС СБОРКИ: ОК', '', '🚀 Сборка завершена успешно', '🕒 ' + moscow_time(report['built_at']), '',
            '📊 ИТОГ И ИЗМЕНЕНИЯ', f"Домены: {report['domains']} ({change_text(change['domains'])})", f"IPv4: {report['ipv4']} ({change_text(change['ipv4'])})", f"IPv6: {report['ipv6']} ({change_text(change['ipv6'])})", '', '📌 ИСТОЧНИКИ']
    for key, label in (('itdog', 'ITDog'), ('custom-domains.txt', 'Custom домены'), ('service-domains.txt', 'Сервисные домены'), ('custom-ip-cidrs.txt', 'Custom IP')):
        if key in report['source_changes']:
            text.append(f"{label}: {report['sources'][key]} ({change_text(report['source_changes'][key])})")
    cats = [k for k in report['sources'] if k.startswith('v2fly:')]
    text.append(f'V2Fly: {len(cats)} категорий, ошибок нет')
    text += ['', f"📈 ТРЕНД ЗА {trend['runs']} УСПЕШНЫХ ЗАПУСКОВ (до 7)", f"Среднее доменов: {trend['metrics']['domains']['average']}", f"Δ к прошлой: {domain_delta:+d}" if domain_delta is not None else 'Δ к прошлой: —', direction]
    for key, label in (('domains', 'Доменные условия'), ('ipv4', 'IPv4'), ('ipv6', 'IPv6')):
        for field, verb in (('added', '➕'), ('removed', '➖')):
            values = change[key][field]
            if values:
                text += ['', verb + ' ' + label + ':'] + ['• ' + x for x in values[:3]]
                if len(values) > 3:
                    text.append(f'… ещё {len(values) - 3} в отчёте')
    text += ['', '⚠️ Замечания:' if warnings else '✅ Замечаний нет']
    text += ['• ' + x for x in warnings[:5]]
    footer = f"\n\n🔐 sha256 SRS: {report['sha256']['routing.srs'][:8]}…{report['sha256']['routing.srs'][-8:]}\n🔗 Отчёт: {REPORT_URL}"
    if run_url:
        footer += '\n🔗 Actions: ' + run_url
    # Reserve room for links and trim safely by Telegram's UTF-16 length limit.
    budget = 3900 - len(footer.encode('utf-16-le')) // 2
    body = '\n'.join(text).encode('utf-16-le')[:budget * 2].decode('utf-16-le', errors='ignore')
    return body + footer
