# 📊 Отчёт сборки правил AWG

## 🧭 Общая информация

> 🕒 **Сборка:** 11.10.2026, 19:50 МСК  
> 📦 **Репозиторий:** SkyNextGen/awg-rules  
> 📄 **Файлы:** `dist/routing.json` и `dist/routing.srs`  
> 🗓 **Расписание:** ежедневно, 23:17 МСК; также вручную и после изменения кода/настроек  
> 🔄 **Сравнение со сборкой:** 11.10.2026, 19:35 МСК

---

## 🧮 Итог сборки

| Показатель | Всего | Добавлено / удалено |
|---|---:|---|
| Доменные правила | 3651 | +35 / -0 |
| IPv4-префиксы | 107 | +23 / -0 |
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
| custom-domains.txt | 67 | +35 / -0 |
| custom-ip-cidrs.txt | 23 | +23 / -0 |
| itdog | 1181 | +0 / -0 |
| service-cdn.json | 0 | +0 / -0 |
| telegram:official-cidr | 11 | +0 / -0 |
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
| v2fly:signal | 8 | +0 / -0 |
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
| Домены | 3132.6 | +35 |
| IPv4 | 87.3 | +23 |
| IPv6 | 43.0 | +0 |

| Сборка (МСК) | Домены | IPv4 | IPv6 |
|---|---:|---:|---:|
| 11.10.2026, 01:27 МСК | 1917 | 84 | 43 |
| 11.10.2026, 01:29 МСК | 1917 | 84 | 43 |
| 11.10.2026, 17:06 МСК | 3609 | 84 | 43 |
| 11.10.2026, 17:54 МСК | 3609 | 84 | 43 |
| 11.10.2026, 18:31 МСК | 3609 | 84 | 43 |
| 11.10.2026, 19:35 МСК | 3616 | 84 | 43 |
| 11.10.2026, 19:50 МСК | 3651 | 107 | 43 |

## 🌐 BGP и fallback

| ASN | Источник | Префиксов до общего объединения | Получено (МСК) |
|---|---|---:|---|
| AS32934 | RIPEstat | 36 | 11.10.2026, 19:51 МСК |
| AS44907 | RIPEstat | 2 | 11.10.2026, 19:51 МСК |
| AS59930 | RIPEstat | 3 | 11.10.2026, 19:51 МСК |
| AS62014 | RIPEstat | 4 | 11.10.2026, 19:51 МСК |
| AS62041 | RIPEstat | 6 | 11.10.2026, 19:51 МСК |
| AS63293 | RIPEstat | 79 | 11.10.2026, 19:51 МСК |
| AS211157 | RIPEstat | 3 | 11.10.2026, 19:51 МСК |

## 🔐 SHA256

- `routing.json`: `19a2627ad81868cf3af3395853fbaa5b1ae084372b9d9cb9b4e93b250a9561b8`
- `routing.srs`: `e2fd1d479b9f865d31e6d7dcedf4d0c4b63b26d1c67681739d0d45d77f560464`

<details>
<summary>🔄 Изменения — первые 20 записей в каждой группе</summary>

### domains

**➕ Добавлено: 35**

- `domain_suffix:nicegram.app`
- `domain_suffix:teleg.xyz`
- `domain_suffix:telegram.ai`
- `domain_suffix:telegram.asia`
- `domain_suffix:telegram.biz`
- `domain_suffix:telegram.cloud`
- `domain_suffix:telegram.cn`
- `domain_suffix:telegram.co`
- `domain_suffix:telegram.com`
- `domain_suffix:telegram.de`
- `domain_suffix:telegram.dev`
- `domain_suffix:telegram.eu`
- `domain_suffix:telegram.fr`
- `domain_suffix:telegram.host`
- `domain_suffix:telegram.in`
- `domain_suffix:telegram.info`
- `domain_suffix:telegram.io`
- `domain_suffix:telegram.jp`
- `domain_suffix:telegram.net`
- `domain_suffix:telegram.qa`
- … ещё 15; полный список в `dist/report.json`.

**➖ Удалено: 0**

- —

### scoped_udp

**➕ Добавлено: 0**

- —

**➖ Удалено: 0**

- —

### ipv4

**➕ Добавлено: 23**

- `142.250.0.0/15`
- `147.75.0.0/16`
- `15.197.206.217/32`
- `15.197.210.208/32`
- `163.114.0.0/16`
- `164.163.191.64/26`
- `173.194.10.0/24`
- `173.194.222.0/24`
- `192.186.226.0/24`
- `199.201.0.0/16`
- `213.102.128.0/24`
- `3.33.221.48/32`
- `3.33.252.61/32`
- `34.192.181.12/32`
- `34.193.38.112/32`
- `34.194.255.230/32`
- `34.194.71.217/32`
- `45.130.4.0/24`
- `45.43.186.0/24`
- `77.240.43.0/24`
- … ещё 3; полный список в `dist/report.json`.

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

**➕ Добавлено: 35**

- `domain_suffix:nicegram.app`
- `domain_suffix:teleg.xyz`
- `domain_suffix:telegram.ai`
- `domain_suffix:telegram.asia`
- `domain_suffix:telegram.biz`
- `domain_suffix:telegram.cloud`
- `domain_suffix:telegram.cn`
- `domain_suffix:telegram.co`
- `domain_suffix:telegram.com`
- `domain_suffix:telegram.de`
- `domain_suffix:telegram.dev`
- `domain_suffix:telegram.eu`
- `domain_suffix:telegram.fr`
- `domain_suffix:telegram.host`
- `domain_suffix:telegram.in`
- `domain_suffix:telegram.info`
- `domain_suffix:telegram.io`
- `domain_suffix:telegram.jp`
- `domain_suffix:telegram.net`
- `domain_suffix:telegram.qa`
- … ещё 15; полный список в `dist/report.json`.

**➖ Удалено: 0**

- —

### custom-ip-cidrs.txt

**➕ Добавлено: 23**

- `142.250.0.0/15`
- `147.75.0.0/16`
- `15.197.206.217/32`
- `15.197.210.208/32`
- `163.114.0.0/16`
- `164.163.191.64/26`
- `173.194.10.0/24`
- `173.194.222.0/24`
- `192.186.226.0/24`
- `199.201.0.0/16`
- `213.102.128.0/24`
- `3.33.221.48/32`
- `3.33.252.61/32`
- `34.192.181.12/32`
- `34.193.38.112/32`
- `34.194.255.230/32`
- `34.194.71.217/32`
- `45.130.4.0/24`
- `45.43.186.0/24`
- `77.240.43.0/24`
- … ещё 3; полный список в `dist/report.json`.

**➖ Удалено: 0**

- —

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

### telegram:official-cidr

**➕ Добавлено: 0**

- —

**➖ Удалено: 0**

- —

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

**➕ Добавлено: 0**

- —

**➖ Удалено: 0**

- —

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
