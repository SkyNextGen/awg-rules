"""Russian Markdown and plain-text Telegram reports from verified build data."""
from datetime import datetime, timedelta, timezone
import ipaddress
import json
from pathlib import Path
from routing_rules import scoped_rules, unrestricted

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
    previous_rule = unrestricted(previous_payload) if previous_payload else None
    prior_sources = json.loads((dist / 'source-snapshot.json').read_text(encoding='utf-8')) if (dist / 'source-snapshot.json').exists() else {}
    current_rule = unrestricted(payload)
    changes = {'domains': delta(records(current_rule), records(previous_rule) if previous_rule else None)}
    scoped_records = lambda obj: [json.dumps(r, sort_keys=True) for r in scoped_rules(obj)]
    changes['scoped_udp'] = delta(scoped_records(payload), scoped_records(previous_payload) if previous_payload else None)
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
        '> 📄 **Файлы:** `dist/routing.json`, `dist/routing.srs` и `dist/routing.txt`  ',
        '> 🗓 **Расписание:** ежедневно, 23:17 МСК; также вручную и после изменения кода/настроек  ',
        f"> 🔄 **Сравнение со сборкой:** {moscow_time(report['compared_to']) if report['compared_to'] else 'первый запуск'}", '',
        '---', '', '## 🧮 Итог сборки', '',
        '| Показатель | Всего | Добавлено / удалено |', '|---|---:|---|',
        f"| Доменные правила | {report['domains']} | {change_text(changes['domains'])} |",
        f"| IPv4-префиксы | {report['ipv4']} | {change_text(changes['ipv4'])} |",
        f"| IPv6-префиксы | {report['ipv6']} | {change_text(changes['ipv6'])} |", '',
        f"Другие доменные условия (keyword/regexp): **{sum(report['matchers'].get(k, 0) for k in ('domain_keyword', 'domain_regex'))}**. Они также учитываются в списке изменений.", '',
        '**Обрезка SRS:** НЕТ. Проверены допустимые размеры, сети и обратное преобразование JSON → SRS → JSON.', '',
        'Изменения показывают записи правил: укрупнение CIDR или замена поддоменов одним suffix может изменить счётчики без потери покрытия.', '',
        '## 🚦 Статус', '', '### ✅ Сборка завершена', '',
    ]
    if report.get('ndms'):
        ndms = report['ndms']
        body += ['### 📄 NDMS / routing.txt', '',
                 f"Домены: **{ndms['domains']}**, IPv4: **{ndms['ipv4']}**, IPv6: **{ndms['ipv6']}**.",
                 f"Точные домены становятся суффиксами: **{ndms['exact_to_suffix']}** исходных правил. "
                 f"Исключены портовые UDP-правила: **{ndms['excluded_scoped_rules']}**; "
                 f"keyword/regexp: **{sum(ndms['excluded_matchers'].values())}**. "
                 'Оба формата собраны из одного снимка источников.', '']
    if report.get('whatsapp_dns'):
        dns = report['whatsapp_dns']
        body += ['### 💬 WhatsApp / свежий DNS CDN', '',
                 f"Проверено имён: **{dns['hosts']}**; с публичными адресами: **{dns['resolved_hosts']}**. "
                 f"Наблюдалось IP: **{dns['ips']}** (IPv4: {dns['ipv4']}, IPv6: {dns['ipv6']}).", '',
                 f"Пропущено запросов: **{dns['failed_questions']}**; ответов резервного Cloudflare: **{dns['fallback_answers']}**. ", '',
                 'Google Public DNS и резервный Cloudflare через DoH используются только при сборке. DNS роутера не меняется. '
                 'Точные адреса узлов вне ASN Meta входят в общие IP-правила SRS и TXT. '
                 'TTL и ответы сохранены в `whatsapp-dns.json`; старые DNS-адреса при ошибке не подмешиваются.', '']
    warnings = report['warnings']
    body += ['### ⚠️ Предупреждения', ''] + ['- ' + x for x in warnings] if warnings else ['### 🟢 Предупреждений нет']
    if report.get('limitations'):
        body += ['', '### ℹ️ Постоянные ограничения', ''] + ['- ' + x for x in report['limitations']]
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
    if report.get('scoped_rules'):
        body += ['', '## Discord: scoped UDP', '',
                 '| Network | Destination ports | IPv4 CIDRs | IPv6 CIDRs |',
                 '|---|---|---:|---:|']
        for rule in report['scoped_rules']:
            body.append('| udp | ' + ', '.join(rule['port_range']) + ' | ' + str(sum(ipaddress.ip_network(p).version == 4 for p in rule['ip_cidr'])) + ' | ' + str(sum(ipaddress.ip_network(p).version == 6 for p in rule['ip_cidr'])) + ' |')
        body += ['', 'These shared CIDRs are restricted by BOTH UDP and destination ports; they are excluded from the unrestricted IP rule.', 'Counts above for ordinary IPv4/IPv6 prefixes exclude scoped UDP rules.', '']
    (staging / 'report.md').write_text('\n'.join(body), encoding='utf-8')
    (staging / 'report.json').write_text(json.dumps(report, indent=2, ensure_ascii=False) + '\n', encoding='utf-8')
    (staging / 'source-snapshot.json').write_text(json.dumps(source_records, indent=2) + '\n', encoding='utf-8')
    (staging / 'history.json').write_text(json.dumps(history, indent=2) + '\n', encoding='utf-8')
    (staging / 'tg_message.txt').write_text(telegram_text(report), encoding='utf-8')


def telegram_text(report, status='success', run_url=''):
    if status != 'success':
        label = '❌ AWG · ОШИБКА СБОРКИ' if status == 'failure' else '⚠️ AWG · Сборка не завершена'
        return '\n'.join([label, 'Новый набор не опубликован. Сохранён последний проверенный.',
                          '🔗 Actions: ' + run_url if run_url else 'Подробности — в GitHub Actions.'])
    warnings = report.get('warnings', [])
    changes = report['changes']
    text = ['⚠️ AWG · Сборка успешна, есть предупреждения' if warnings else '✅ AWG · Сборка успешна',
            '🕒 ' + moscow_time(report['built_at']), '', '📊 Итог · добавлено / удалено']
    changed = False
    first = False
    for key, label in (('domains', 'Домены'), ('ipv4', 'IPv4'), ('ipv6', 'IPv6')):
        item = changes[key]
        first |= not item['baseline']
        changed |= bool(item['added_count'] or item['removed_count'])
        summary = change_text(item) if item['baseline'] else 'первый снимок'
        text.append(f"{label}: {report[key]} ({summary})")
    udp = changes.get('scoped_udp')
    if udp:
        first |= not udp['baseline']
        if udp['baseline'] and (udp['added_count'] or udp['removed_count']):
            changed = True
            text.append('UDP-правила ' + change_text(udp))
    source_changes = report.get('source_changes', {})
    active = [(name, item) for name, item in sorted(source_changes.items())
              if not item['baseline'] or item['added_count'] or item['removed_count']]
    labels = {'itdog': 'ITDog', 'custom-domains.txt': 'Custom-домены',
              'custom-ip-cidrs.txt': 'Custom-IP', 'telegram:official-cidr': 'Telegram / официальный CIDR',
              'ITDog:discord:scoped-udp': 'Discord UDP'}
    if active:
        text += ['', '📌 Где изменилось']
        for name, item in active[:12]:
            label = labels.get(name, name.replace('v2fly:', 'V2Fly / ').replace('BGP:', 'BGP / ')
                               .replace('ITDog:service:', 'ITDog / '))
            count = report.get('sources', {}).get(name, 0)
            summary = change_text(item) if item['baseline'] else 'новый источник'
            text.append(f"• {label}: {count} ({summary})")
        if len(active) > 12:
            text.append(f'Ещё источников: {len(active) - 12} — в полном отчёте.')
        text.append('Дельты источников до объединения; записи могут пересекаться.')
    elif not changed:
        text += ['', 'Первый снимок — сравнение со следующей сборки.' if first else 'Изменений нет']
    trend = report.get('trend', {})
    metrics = trend.get('metrics', {})
    domain_trend = metrics.get('domains', {})
    if domain_trend.get('delta') is not None:
        text += ['', f"📈 Домены: Δ {domain_trend['delta']:+d} к прошлой сборке · "
                     f"среднее за {trend['runs']} запусков: {domain_trend['average']}"]
    if warnings:
        # Operational warnings stay visible; permanent limitations live in the full report.
        text += ['', '⚠️ Предупреждения']
        text += ['• ' + x.replace('\n', ' ')[:160] for x in warnings[:2]]
        if len(warnings) > 2:
            text.append(f'Ещё предупреждений: {len(warnings) - 2} — в отчёте.')
    footer = '\n\n🔗 Отчёт: ' + REPORT_URL
    if run_url:
        footer += '\n🔗 Actions: ' + run_url
    # Keep the links intact even if many source names or warnings are long.
    budget = max(0, 3900 - len(footer.encode('utf-16-le')) // 2)
    body = '\n'.join(text).encode('utf-16-le')[:budget * 2].decode('utf-16-le', errors='ignore')
    return body + footer


