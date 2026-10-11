# 📊 Отчёт сборки правил AWG

## 🧭 Общая информация

> 🕒 **Сборка:** 11.10.2026, 19:35 МСК  
> 📦 **Репозиторий:** SkyNextGen/awg-rules  
> 📄 **Файлы:** `dist/routing.json` и `dist/routing.srs`  
> 🗓 **Расписание:** ежедневно, 23:17 МСК; также вручную и после изменения кода/настроек  
> 🔄 **Сравнение со сборкой:** 11.10.2026, 18:31 МСК

---

## 🧮 Итог сборки

| Показатель | Всего | Добавлено / удалено |
|---|---:|---|
| Доменные правила | 3616 | +7 / -0 |
| IPv4-префиксы | 84 | +0 / -0 |
| IPv6-префиксы | 43 | +0 / -0 |

Другие доменные условия (keyword/regexp): **7**. Они также учитываются в списке изменений.

**Обрезка:** НЕТ. Проверены допустимые размеры, сети и обратное преобразование JSON → SRS → JSON.

Изменения показывают записи правил: укрупнение CIDR или замена поддоменов одним suffix может изменить счётчики без потери покрытия.

## 🚦 Статус

### ✅ Сборка завершена

### 🟢 Предупреждений нет

### ℹ️ Постоянные ограничения

- Ежедневная пересборка получает проверяемые upstream-источники, но не обнаруживает автоматически все новые домены в интернете. WhatsApp использует общие сети Meta, а не отдельный полный реестр WhatsApp-IP.
- Discord: голосовые IP меняются; покрытие IPv6 для UDP 19000–20000 не подтверждено. Общие подсети ограничены UDP-портами, но могут захватывать сторонний трафик на тех же портах.

## 📌 Сводка источников

| Источник | Уникальных записей до объединения | Добавлено / удалено |
|---|---:|---|
| BGP:AS211157 | 3 | +0 / -0 |
| BGP:AS32934 | 36 | +0 / -0 |
| BGP:AS44907 | 2 | +0 / -0 |
| BGP:AS59930 | 3 | +0 / -0 |
| BGP:AS62014 | 4 | +0 / -0 |
| BGP:AS62041 | 6 | +0 / -0 |
| BGP:AS63293 | 79 | +0 / -0 |
| ITDog:discord:scoped-udp | 2 | +0 / -0 |
| ITDog:service:discord | 20 | +0 / -0 |
| ITDog:service:telegram | 20 | +0 / -0 |
| custom-domains.txt | 32 | +0 / -92 |
| custom-ip-cidrs.txt | 0 | +0 / -4 |
| itdog | 1181 | +0 / -0 |
| service-cdn.json | 0 | +0 / -0 |
| service-domains.txt | 0 | +0 / -32 |
| telegram:official-cidr | 11 | первый снимок — сравнение со следующего запуска |
| v2fly:anthropic | 9 | +0 / -0 |
| v2fly:category-ai-!cn | 190 | +0 / -0 |
| v2fly:category-ai-chat-!cn | 190 | +0 / -0 |
| v2fly:category-ai-cn | 115 | +0 / -0 |
| v2fly:category-ai-ru | 12 | +0 / -0 |
| v2fly:deepseek | 2 | +0 / -0 |
| v2fly:discord | 28 | +0 / -0 |
| v2fly:doubao | 32 | +0 / -0 |
| v2fly:facebook | 397 | +0 / -0 |
| v2fly:google | 1122 | +0 / -0 |
| v2fly:google-deepmind | 46 | +0 / -0 |
| v2fly:google-gemini | 46 | +0 / -0 |
| v2fly:google-play | 10 | +0 / -0 |
| v2fly:googlefcm | 12 | +0 / -0 |
| v2fly:instagram | 74 | +0 / -0 |
| v2fly:meta | 555 | +0 / -0 |
| v2fly:microsoft | 754 | +0 / -0 |
| v2fly:microsoft-dev | 74 | +0 / -0 |
| v2fly:netflix | 28 | +0 / -0 |
| v2fly:nexusmods | 2 | +0 / -0 |
| v2fly:nvidia | 66 | +0 / -0 |
| v2fly:openai | 23 | +0 / -0 |
| v2fly:patreon | 4 | +0 / -0 |
| v2fly:perplexity | 5 | +0 / -0 |
| v2fly:playstation | 4 | +0 / -0 |
| v2fly:signal | 8 | первый снимок — сравнение со следующего запуска |
| v2fly:soundcloud | 3 | +0 / -0 |
| v2fly:spotify | 28 | +0 / -0 |
| v2fly:telegram | 21 | +0 / -0 |
| v2fly:threads | 2 | +0 / -0 |
| v2fly:tiktok | 37 | +0 / -0 |
| v2fly:ubisoft | 31 | +0 / -0 |
| v2fly:wbgames | 6 | +0 / -0 |
| v2fly:whatsapp | 11 | +0 / -0 |
| v2fly:youtube | 178 | +0 / -0 |

Записи разных источников могут пересекаться, поэтому сумма строк этой таблицы не равна итоговому числу правил. Для нового формата источников первый запуск сохраняет базу сравнения.

## 📈 Тренд за последние успешные запуски

Использовано запусков: **7 из 7**. Сравнение выполняется с предыдущей успешной сборкой, включая ручные запуски.

| Показатель | Среднее | Δ к прошлой |
|---|---:|---:|
| Домены | 2884.6 | +7 |
| IPv4 | 84.0 | +0 |
| IPv6 | 43.0 | +0 |

| Сборка (МСК) | Домены | IPv4 | IPv6 |
|---|---:|---:|---:|
| 07.10.2026, 17:39 МСК | 1915 | 84 | 43 |
| 11.10.2026, 01:27 МСК | 1917 | 84 | 43 |
| 11.10.2026, 01:29 МСК | 1917 | 84 | 43 |
| 11.10.2026, 17:06 МСК | 3609 | 84 | 43 |
| 11.10.2026, 17:54 МСК | 3609 | 84 | 43 |
| 11.10.2026, 18:31 МСК | 3609 | 84 | 43 |
| 11.10.2026, 19:35 МСК | 3616 | 84 | 43 |

## 🌐 BGP и fallback

| ASN | Источник | Префиксов до общего объединения | Получено (МСК) |
|---|---|---:|---|
| AS32934 | RIPEstat | 36 | 11.10.2026, 19:36 МСК |
| AS44907 | RIPEstat | 2 | 11.10.2026, 19:36 МСК |
| AS59930 | RIPEstat | 3 | 11.10.2026, 19:36 МСК |
| AS62014 | RIPEstat | 4 | 11.10.2026, 19:36 МСК |
| AS62041 | RIPEstat | 6 | 11.10.2026, 19:36 МСК |
| AS63293 | RIPEstat | 79 | 11.10.2026, 19:36 МСК |
| AS211157 | RIPEstat | 3 | 11.10.2026, 19:36 МСК |

## 🔐 SHA256

- `routing.json`: `b010341575265546f0722ec96e93e671688ef8fa7de1f131e0e4309a0387686c`
- `routing.srs`: `a191d6353b9a9a8f22261a508986196fc341f0e9876c3f9030eec768814c4952`

<details>
<summary>🔄 Изменения — первые 20 записей в каждой группе</summary>

### domains

**➕ Добавлено: 7**

- `domain_suffix:signal.art`
- `domain_suffix:signal.group`
- `domain_suffix:signal.link`
- `domain_suffix:signal.me`
- `domain_suffix:signal.tube`
- `domain_suffix:signalusers.org`
- `domain_suffix:whispersystems.org`

**➖ Удалено: 0**

- —

### scoped_udp

**➕ Добавлено: 0**

- —

**➖ Удалено: 0**

- —

### ipv4

**➕ Добавлено: 0**

- —

**➖ Удалено: 0**

- —

### ipv6

**➕ Добавлено: 0**

- —

**➖ Удалено: 0**

- —

### BGP:AS211157

**➕ Добавлено: 0**

- —

**➖ Удалено: 0**

- —

### BGP:AS32934

**➕ Добавлено: 0**

- —

**➖ Удалено: 0**

- —

### BGP:AS44907

**➕ Добавлено: 0**

- —

**➖ Удалено: 0**

- —

### BGP:AS59930

**➕ Добавлено: 0**

- —

**➖ Удалено: 0**

- —

### BGP:AS62014

**➕ Добавлено: 0**

- —

**➖ Удалено: 0**

- —

### BGP:AS62041

**➕ Добавлено: 0**

- —

**➖ Удалено: 0**

- —

### BGP:AS63293

**➕ Добавлено: 0**

- —

**➖ Удалено: 0**

- —

### ITDog:discord:scoped-udp

**➕ Добавлено: 0**

- —

**➖ Удалено: 0**

- —

### ITDog:service:discord

**➕ Добавлено: 0**

- —

**➖ Удалено: 0**

- —

### ITDog:service:telegram

**➕ Добавлено: 0**

- —

**➖ Удалено: 0**

- —

### custom-domains.txt

**➕ Добавлено: 0**

- —

**➖ Удалено: 92**

- `domain_suffix:1337x.to`
- `domain_suffix:account.google.com`
- `domain_suffix:accounts.google.com`
- `domain_suffix:alt1-mtalk.google.com`
- `domain_suffix:alt2-mtalk.google.com`
- `domain_suffix:alt3-mtalk.google.com`
- `domain_suffix:alt4-mtalk.google.com`
- `domain_suffix:android.apis.google.com`
- `domain_suffix:android.clients.google.com`
- `domain_suffix:android.googleapis.com`
- `domain_suffix:booktracker.org`
- `domain_suffix:cast.googleapis.com`
- `domain_suffix:checkin.gstatic.com`
- `domain_suffix:clients.google.com`
- `domain_suffix:clients.googleapis.com`
- `domain_suffix:clients.l.google.com`
- `domain_suffix:clients1.google.com`
- `domain_suffix:clients2.google.com`
- `domain_suffix:clients3.google.com`
- `domain_suffix:clients4.google.com`
- … ещё 72; полный список в `dist/report.json`.

### custom-ip-cidrs.txt

**➕ Добавлено: 0**

- —

**➖ Удалено: 4**

- `149.154.168.0/22`
- `2001:b28:f23f::/48`
- `2a0a:f280::/32`
- `91.108.16.0/22`

### itdog

**➕ Добавлено: 0**

- —

**➖ Удалено: 0**

- —

### service-cdn.json

**➕ Добавлено: 0**

- —

**➖ Удалено: 0**

- —

### service-domains.txt

**➕ Добавлено: 0**

- —

**➖ Удалено: 32**

- `domain_suffix:cdn-telegram.org`
- `domain_suffix:cdninstagram.com`
- `domain_suffix:discord.com`
- `domain_suffix:discord.gg`
- `domain_suffix:discord.media`
- `domain_suffix:discordapp.com`
- `domain_suffix:discordapp.net`
- `domain_suffix:facebook.com`
- `domain_suffix:facebook.net`
- `domain_suffix:fb.com`
- `domain_suffix:fbcdn.net`
- `domain_suffix:fbsbx.com`
- `domain_suffix:ig.me`
- `domain_suffix:instagram.com`
- `domain_suffix:messenger.com`
- `domain_suffix:meta.com`
- `domain_suffix:nexus-cdn.com`
- `domain_suffix:nexusmods.com`
- `domain_suffix:t.me`
- `domain_suffix:tdesktop.com`
- … ещё 12; полный список в `dist/report.json`.

### telegram:official-cidr

Первый снимок; предыдущего набора нет.

### v2fly:anthropic

**➕ Добавлено: 0**

- —

**➖ Удалено: 0**

- —

### v2fly:category-ai-!cn

**➕ Добавлено: 0**

- —

**➖ Удалено: 0**

- —

### v2fly:category-ai-chat-!cn

**➕ Добавлено: 0**

- —

**➖ Удалено: 0**

- —

### v2fly:category-ai-cn

**➕ Добавлено: 0**

- —

**➖ Удалено: 0**

- —

### v2fly:category-ai-ru

**➕ Добавлено: 0**

- —

**➖ Удалено: 0**

- —

### v2fly:deepseek

**➕ Добавлено: 0**

- —

**➖ Удалено: 0**

- —

### v2fly:discord

**➕ Добавлено: 0**

- —

**➖ Удалено: 0**

- —

### v2fly:doubao

**➕ Добавлено: 0**

- —

**➖ Удалено: 0**

- —

### v2fly:facebook

**➕ Добавлено: 0**

- —

**➖ Удалено: 0**

- —

### v2fly:google

**➕ Добавлено: 0**

- —

**➖ Удалено: 0**

- —

### v2fly:google-deepmind

**➕ Добавлено: 0**

- —

**➖ Удалено: 0**

- —

### v2fly:google-gemini

**➕ Добавлено: 0**

- —

**➖ Удалено: 0**

- —

### v2fly:google-play

**➕ Добавлено: 0**

- —

**➖ Удалено: 0**

- —

### v2fly:googlefcm

**➕ Добавлено: 0**

- —

**➖ Удалено: 0**

- —

### v2fly:instagram

**➕ Добавлено: 0**

- —

**➖ Удалено: 0**

- —

### v2fly:meta

**➕ Добавлено: 0**

- —

**➖ Удалено: 0**

- —

### v2fly:microsoft

**➕ Добавлено: 0**

- —

**➖ Удалено: 0**

- —

### v2fly:microsoft-dev

**➕ Добавлено: 0**

- —

**➖ Удалено: 0**

- —

### v2fly:netflix

**➕ Добавлено: 0**

- —

**➖ Удалено: 0**

- —

### v2fly:nexusmods

**➕ Добавлено: 0**

- —

**➖ Удалено: 0**

- —

### v2fly:nvidia

**➕ Добавлено: 0**

- —

**➖ Удалено: 0**

- —

### v2fly:openai

**➕ Добавлено: 0**

- —

**➖ Удалено: 0**

- —

### v2fly:patreon

**➕ Добавлено: 0**

- —

**➖ Удалено: 0**

- —

### v2fly:perplexity

**➕ Добавлено: 0**

- —

**➖ Удалено: 0**

- —

### v2fly:playstation

**➕ Добавлено: 0**

- —

**➖ Удалено: 0**

- —

### v2fly:signal

Первый снимок; предыдущего набора нет.

### v2fly:soundcloud

**➕ Добавлено: 0**

- —

**➖ Удалено: 0**

- —

### v2fly:spotify

**➕ Добавлено: 0**

- —

**➖ Удалено: 0**

- —

### v2fly:telegram

**➕ Добавлено: 0**

- —

**➖ Удалено: 0**

- —

### v2fly:threads

**➕ Добавлено: 0**

- —

**➖ Удалено: 0**

- —

### v2fly:tiktok

**➕ Добавлено: 0**

- —

**➖ Удалено: 0**

- —

### v2fly:ubisoft

**➕ Добавлено: 0**

- —

**➖ Удалено: 0**

- —

### v2fly:wbgames

**➕ Добавлено: 0**

- —

**➖ Удалено: 0**

- —

### v2fly:whatsapp

**➕ Добавлено: 0**

- —

**➖ Удалено: 0**

- —

### v2fly:youtube

**➕ Добавлено: 0**

- —

**➖ Удалено: 0**

- —

</details>


## Discord: scoped UDP

| Network | Destination ports | IPv4 CIDRs | IPv6 CIDRs |
|---|---|---:|---:|
| udp | 50000:65535 | 8 | 1 |
| udp | 19000:20000 | 1 | 0 |

These shared CIDRs are restricted by BOTH UDP and destination ports; they are excluded from the unrestricted IP rule.
Counts above for ordinary IPv4/IPv6 prefixes exclude scoped UDP rules.
