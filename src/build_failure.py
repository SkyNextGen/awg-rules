"""Public descriptions of failures. Raw exceptions belong in the Actions log."""
import re
from subprocess import CalledProcessError, TimeoutExpired
from urllib.parse import urlsplit
from freshness import FreshnessError


def build_reason(error):
    message = str(error)
    if isinstance(error, FreshnessError):
        return message
    if message.startswith('Source fetch failed: '):
        url = message.removeprefix('Source fetch failed: ').partition(': ')[0]
        try:
            host = urlsplit(url).hostname
        except ValueError:
            host = None
        if host in {'raw.githubusercontent.com', 'api.github.com', 'stat.ripe.net',
                    'www.meta.com', 'core.telegram.org'}:
            return f'Не удалось скачать обязательный источник с {host} после повторных попыток.'
        return 'Не удалось скачать обязательный источник после повторных попыток.'
    asn = re.fullmatch(r'(AS[0-9]+): no valid live data or fresh snapshot', message)
    if asn:
        return f'Для {asn[1]} не удалось получить проверенные IP-подсети. Подходящей резервной копии тоже нет.'
    if message.startswith('Meta feed has no fresh validated snapshot'):
        return 'Не удалось скачать один из списков сетей Meta. Подходящей проверенной копии нет.'
    if message.startswith(('Meta geofeed', 'Meta feed', 'Invalid Meta feed', 'Truncated Meta geofeed')):
        return 'Список сетей Meta не прошёл проверку формата, полноты или срока обновления.'
    if message.startswith('WhatsApp DNS failures exceed'):
        return 'Для WhatsApp слишком много DNS-запросов осталось без ответа. Список IP получился неполным.'
    if message.startswith('DNS inventory deadline') or (
            isinstance(error, TimeoutError) and 'futures unfinished' in message):
        return 'Сборщик не успел получить все DNS-ответы за отведённое время.'
    if message.startswith('DNS failed:'):
        return 'Оба DNS-сервера не смогли вернуть подходящий ответ для одного из обязательных доменов.'
    if message.startswith(('WhatsApp DNS inventory', 'WhatsApp host inventory', 'WhatsApp DNS ')):
        return 'Список доменов или IP для WhatsApp не прошёл проверку полноты.'
    if message.startswith(('Unsafe DNS', 'Invalid DNS', 'DNS question', 'DNS CNAME',
                           'Conflicting DNS', 'NXDOMAIN', 'Temporary/invalid DNS')):
        return 'Сборщик получил некорректный DNS-ответ и остановил обновление.'
    if message.startswith('ITDog truncated'):
        return 'Основной список доменов ITDog оказался пустым или слишком коротким.'
    if message.startswith('Discord release is expired'):
        return 'Дата релиза Discord от ITDog не прошла проверку свежести.'
    if message.startswith(('Discord', 'Published Discord', 'Invalid Discord', 'Missing Discord',
                           'Unexpected published Discord', 'Unsafe Discord', 'Invalid custom Discord')):
        return 'Правила или IP-адреса Discord не прошли проверку.'
    if 'checksum mismatch' in message or 'SHA256 digest' in message:
        return 'Не удалось подтвердить контрольную сумму загруженного файла.'
    if isinstance(error, (CalledProcessError, TimeoutExpired)):
        return 'sing-box не смог обработать файл правил. Подробности есть в журнале сборки.'
    if 'changed beyond safety threshold' in message or message.startswith('Output size outside'):
        return 'Число доменов или покрытие IP изменилось сильнее допустимого. Сборщик остановил обновление.'
    if message.startswith(('SRS round-trip', 'NDMS text', 'Duplicate NDMS', 'Unsupported rule conditions')):
        return 'Проверка выявила расхождение или ошибку в итоговом формате правил.'
    if message.startswith(('Missing generated service', 'Missing generated service IPs',
                           'Empty generated service', 'Service domain missing', 'Service IP missing',
                           'Scoped service', 'Gameloft BGP', 'Custom Discord UDP', 'Official Telegram',
                           'Meta/CDN IP missing', 'WhatsApp DNS snapshot', 'WhatsApp observed')):
        return 'Проверка покрытия обнаружила, что итоговый список потерял обязательные адреса, домены или условия.'
    if message.startswith(('Unsafe network', 'Invalid domain', 'IP in domain source')):
        return 'Один из источников содержит недопустимый домен или IP-сеть.'
    return 'Сборка прервалась при обработке источников или проверке правил. Точная ошибка указана в журнале.'
