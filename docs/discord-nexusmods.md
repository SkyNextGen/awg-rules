# Discord и Nexus Mods: покрытие и ограничения

Проверено 2026-10-11 (МСК). Discord уже был в категориях; добавлена
`nexusmods`. Основные suffix закреплены в `service-domains.txt`, чтобы
сохранить пользовательские требования при изменении upstream.

## Источники

- [V2Fly Discord](https://github.com/v2fly/domain-list-community/blob/master/data/discord):
  26 suffix и 2 exact на дату проверки; blob `ac3be1191519a0f54800dc077f7c5a76d44e4be4`.
- [V2Fly Nexus Mods](https://github.com/v2fly/domain-list-community/blob/master/data/nexusmods):
  `nexusmods.com`, `nexus-cdn.com`; blob `6876c7f52cedbc0a4294876669fbafee1f6d8a22`.
- [Nexus Mods: проблемы загрузки](https://help.nexusmods.com/article/92-im-having-download-issues-what-can-i-do):
  файловые серверы под `nexus-cdn.com`.
- [Discord Voice API](https://docs.discord.com/developers/topics/voice-connections):
  endpoint под `discord.media`; IP/порт UDP передаются клиенту в Ready payload.
- [Discord: перенос голоса и видео на edge](https://discord.com/blog/how-we-moved-discord-voice-to-the-edge):
  публикация от 2026-06-09 описывает использование Cloudflare для более 80% голосового/видеотрафика.

## Покрытие доменов

| Требование | Правило |
|---|---|
| Discord сайт/API | `discord.com` |
| Gateway | `discord.gg` |
| Файлы и вложенные видео | `discordapp.com`, `discordapp.net` |
| Голос/видеосвязь | `discord.media` |
| Загрузка вложений в Google Storage | exact `discord-attachments-uploads-prd.storage.googleapis.com` из V2Fly |
| Nexus сайт, API, авторизация, assets | `nexusmods.com` |
| Nexus CDN, обычные и supporter/premium загрузки | `nexus-cdn.com` |

Suffix включает корневой домен и любые его поддомены. Внешние сайты,
на которые пользователи публикуют ссылки в Discord, не становятся
доменами Discord и не включаются автоматически.

## IPv4/IPv6

Проверены A и AAAA ключевых узлов через Google Public DNS JSON API
`https://dns.google/resolve` (2026-10-10 около 22:25 UTC).
Это один региональный DNS-снимок, **не полный реестр IP**.

| Узел | IPv4 из ответа | IPv6 из ответа |
|---|---|---|
| `discord.com` | `162.159.128.233`, `162.159.135.232`, `162.159.136.232`, `162.159.137.232`, `162.159.138.232` | AAAA нет |
| `cdn.discordapp.com` | `162.159.129.233`, `162.159.130.233`, `162.159.133.233`, `162.159.134.233`, `162.159.135.233` | AAAA нет |
| `media.discordapp.net` | `162.159.128.232`, `162.159.129.232`, `162.159.130.232`, `162.159.133.232`, `162.159.134.232` | AAAA нет |
| `gateway.discord.gg` | `162.159.130.234`, `162.159.133.234`, `162.159.134.234`, `162.159.135.234`, `162.159.136.234` | AAAA нет |
| Discord uploads в Google Storage | `64.233.176.207`, `74.125.21.207`, `74.125.138.207`, `108.177.122.207`, `142.250.9.207`, `142.250.105.207`, `172.253.124.207`, `173.194.219.207` | `2607:f8b0:4002:c02::cf`, `2607:f8b0:4002:c0c::cf`, `2607:f8b0:4002:c10::cf`, `2607:f8b0:4002:c11::cf` |
| `nexusmods.com` | `104.18.42.54`, `172.64.145.202` | AAAA нет |
| `files.nexus-cdn.com`, `supporter-files.nexus-cdn.com` | `185.229.191.156` | AAAA нет |

TTL ответов: 300 секунд для основных узлов, 60 секунд для Nexus CDN.
RIPEstat `network-info` подтвердил origin AS13335 для примеров Discord CDN
и Nexus website, AS15169 для обоих семейств Google Storage и AS60068
для проверенного Nexus CDN IP. Это ASN провайдеров, не выделенные ASN сервисов.
Источник: `https://stat.ripe.net/data/network-info/data.json?resource=<IP>`.
Отсутствие AAAA в конкретном ответе не доказывает отсутствие IPv6 у сервиса.
IP голосовых серверов зависят от текущей сессии и не перечислены здесь.

В отличие от выделенных ASN Telegram/Meta, проверенные источники не дают
полного service-specific списка сетей Discord/Nexus. Поэтому общие ASN
Cloudflare/Google/CDN не добавлены в BGP, а краткоживущие DNS-IP не
закреплены как постоянные CIDR. Принадлежность IP домену в одном DNS-ответе
не доказывает эксклюзивность адреса и не позволяет расширять его до /24
или ASN. Для IP-only/UDP-соединений нужна проверка текущего endpoint
на клиенте и корректного DNS-to-IP routing на потребителе.

## Проверка и применение

- Офлайн-тесты проверяют категории и покрытие важных endpoint suffix-правилами.
- Сборка должна пройти compile/decompile официальным sing-box.
- Изменения предлагаются в отдельной ветке/PR. До слияния URL `main/dist`
  не содержит этих изменений; роутер и сервер не перенастраиваются.
- На реальном Keenetic отдельно проверить скачивание Discord-вложения,
  воспроизведение вложенного видео, голос/видеосвязь и Nexus-загрузку.
  Discord media/voice suffix уже были в опубликованном списке до этого PR:
  это изменение не является доказанным исправлением их неработоспособности.
- Откат после согласованного применения: вернуть прежний URL/проверенный
  список, либо подготовить revert соответствующего PR.
