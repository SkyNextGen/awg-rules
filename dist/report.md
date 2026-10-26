# 📊 Отчёт сборки правил AWG

## 🧭 Общая информация

> 🕒 **Сборка:** 26.10.2026, 16:37 МСК  
> 📦 **Репозиторий:** SkyNextGen/awg-rules  
> 📄 **Файлы:** `dist/routing.json`, `dist/routing.srs` и `dist/routing.txt`  
> 🗓 **Расписание:** ежедневно, 23:17 МСК; также вручную и после изменения кода/настроек  
> 🔄 **Сравнение со сборкой:** 26.10.2026, 01:36 МСК

---

## 🧮 Итог сборки

| Показатель | Всего | Добавлено / удалено |
|---|---:|---|
| Доменные правила | 4293 | +5 / -2 |
| IPv4-префиксы | 1151 | +0 / -0 |
| IPv6-префиксы | 788 | +0 / -0 |

Другие доменные условия (keyword/regexp): **7**. Они также учитываются в списке изменений.

**Обрезка SRS:** НЕТ. Проверены допустимые размеры, сети и обратное преобразование JSON → SRS → JSON.

Изменения показывают записи правил: укрупнение CIDR или замена поддоменов одним suffix может изменить счётчики без потери покрытия.

## 🚦 Статус

### ✅ Сборка завершена

### 📄 NDMS / routing.txt

Домены: **4291**, IPv4: **1151**, IPv6: **788**.
Точные домены становятся суффиксами: **88** исходных правил. Исключены правила с протоколами/портами: **4**; keyword/regexp: **7**. Оба формата собраны из одного снимка источников.

### 💬 WhatsApp / свежий DNS CDN

Проверено имён: **2269**; с публичными адресами: **1466**. Наблюдалось IP: **1893** (IPv4: 1188, IPv6: 705).

Пропущено запросов: **0**; ответов резервного Cloudflare: **53**. 

Google Public DNS и резервный Cloudflare через DoH используются только при сборке. DNS роутера не меняется. Точные адреса узлов вне ASN Meta входят в общие IP-правила SRS и TXT. TTL и ответы сохранены в `whatsapp-dns.json`; старые DNS-адреса при ошибке не подмешиваются.

### 🟢 Предупреждений нет

### ℹ️ Постоянные ограничения

- WhatsApp: свежие BGP/geofeed Meta и DNS известных CDN-узлов не гарантируют все региональные адреса. Корпоративные сети Meta не подтверждены как необходимые медиасети. DNS-адреса меняются; рабочая загрузка файлов проверяется на устройстве.
- Discord: голосовые IP меняются; покрытие IPv6 для UDP 19000–20000 не подтверждено. Общие подсети ограничены UDP-портами. Точные DNS-адреса CDN ограничены TCP/UDP 443, но тоже могут обслуживать другие сайты. ECH скрывает имя; DNS при сборке не гарантирует все региональные IP.

## 📌 Сводка источников

| Источник | Уникальных записей до объединения | Добавлено / удалено |
|---|---:|---|
| BGP:AS11807 | 4 | +0 / -0 |
| BGP:AS211157 | 3 | +0 / -0 |
| BGP:AS32934 | 36 | +0 / -0 |
| BGP:AS44907 | 2 | +0 / -0 |
| BGP:AS54115 | 3 | +0 / -0 |
| BGP:AS59930 | 3 | +0 / -0 |
| BGP:AS62014 | 4 | +0 / -0 |
| BGP:AS62041 | 6 | +0 / -0 |
| BGP:AS63293 | 81 | +0 / -0 |
| Custom:discord:scoped-udp | 1 | +0 / -0 |
| Discord:cdn-dns:https | 10 | +0 / -0 |
| ITDog:discord:scoped-udp | 2 | +0 / -0 |
| ITDog:service:discord | 20 | +0 / -0 |
| ITDog:service:telegram | 20 | +0 / -0 |
| ITDog:service:whatsapp | 18 | +0 / -0 |
| Meta:ITDog-IPv4 | 79 | +0 / -0 |
| Meta:ITDog-IPv6 | 40 | +0 / -0 |
| Meta:Loyalsoldier | 118 | +0 / -0 |
| Meta:MetaCubeX | 118 | +0 / -0 |
| Meta:geofeed | 373 | +0 / -0 |
| Meta:geofeed-corp | 153 | +0 / -0 |
| WhatsApp:cdn-dns | 1890 | +38 / -32 |
| WhatsApp:cdn-hosts | 2269 | +0 / -0 |
| custom-domains.txt | 87 | +2 / -0 |
| custom-ip-cidrs.txt | 23 | +0 / -0 |
| itdog | 1181 | +0 / -0 |
| telegram:official-cidr | 11 | +0 / -0 |
| v2fly:anthropic | 19 | +0 / -0 |
| v2fly:autodesk | 558 | +0 / -0 |
| v2fly:canva | 6 | +0 / -0 |
| v2fly:category-ai-!cn | 208 | +3 / -0 |
| v2fly:category-ai-chat-!cn | 208 | +3 / -0 |
| v2fly:category-ai-cn | 116 | +1 / -0 |
| v2fly:category-ai-ru | 12 | +0 / -0 |
| v2fly:deepseek | 2 | +0 / -0 |
| v2fly:discord | 28 | +0 / -0 |
| v2fly:doubao | 32 | +0 / -0 |
| v2fly:facebook | 397 | +0 / -0 |
| v2fly:google | 1125 | +3 / -0 |
| v2fly:google-deepmind | 49 | +3 / -0 |
| v2fly:google-gemini | 49 | +3 / -0 |
| v2fly:google-play | 10 | +0 / -0 |
| v2fly:googlefcm | 12 | +0 / -0 |
| v2fly:hdrezka | 16 | +0 / -0 |
| v2fly:instagram | 74 | +0 / -0 |
| v2fly:jetbrains | 25 | +0 / -0 |
| v2fly:mega | 7 | +0 / -0 |
| v2fly:meta | 555 | +0 / -0 |
| v2fly:microsoft | 758 | +7 / -0 |
| v2fly:microsoft-dev | 76 | +2 / -0 |
| v2fly:netflix | 28 | +1 / -1 |
| v2fly:nexusmods | 2 | +0 / -0 |
| v2fly:notion | 7 | +0 / -0 |
| v2fly:nvidia | 66 | +0 / -0 |
| v2fly:openai | 25 | +0 / -0 |
| v2fly:patreon | 4 | +0 / -0 |
| v2fly:perplexity | 5 | +0 / -0 |
| v2fly:playstation | 5 | +0 / -0 |
| v2fly:protonmail | 9 | +0 / -0 |
| v2fly:rutracker | 9 | +0 / -0 |
| v2fly:signal | 8 | +0 / -0 |
| v2fly:soundcloud | 3 | +0 / -0 |
| v2fly:spotify | 28 | +1 / -1 |
| v2fly:telegram | 21 | +0 / -0 |
| v2fly:threads | 2 | +0 / -0 |
| v2fly:tiktok | 37 | +0 / -0 |
| v2fly:tmdb | 4 | +0 / -0 |
| v2fly:twitter | 24 | +0 / -0 |
| v2fly:ubisoft | 31 | +0 / -0 |
| v2fly:unity | 10 | +0 / -0 |
| v2fly:wbgames | 6 | +0 / -0 |
| v2fly:whatsapp | 11 | +0 / -0 |
| v2fly:youtube | 178 | +0 / -0 |

Записи разных источников могут пересекаться, поэтому сумма строк этой таблицы не равна итоговому числу правил. Для нового формата источников первый запуск сохраняет базу сравнения.

## 📈 Тренд за последние успешные запуски

Использовано запусков: **7 из 7**. Сравнение выполняется с предыдущей успешной сборкой, включая ручные запуски.

| Показатель | Среднее | Δ к прошлой |
|---|---:|---:|
| Домены | 4286.1 | +3 |
| IPv4 | 1150.4 | +0 |
| IPv6 | 788.0 | +0 |

| Сборка (МСК) | Домены | IPv4 | IPv6 |
|---|---:|---:|---:|
| 21.10.2026, 02:12 МСК | 4276 | 1150 | 788 |
| 22.10.2026, 02:24 МСК | 4286 | 1150 | 788 |
| 23.10.2026, 02:26 МСК | 4286 | 1150 | 788 |
| 24.10.2026, 02:11 МСК | 4286 | 1150 | 788 |
| 25.10.2026, 01:31 МСК | 4286 | 1151 | 788 |
| 26.10.2026, 01:36 МСК | 4290 | 1151 | 788 |
| 26.10.2026, 16:37 МСК | 4293 | 1151 | 788 |

## 🌐 BGP и fallback

| ASN | Источник | Префиксов до общего объединения | Получено (МСК) |
|---|---|---:|---|
| AS11807 | RIPEstat | 4 | 26.10.2026, 16:37 МСК |
| AS32934 | RIPEstat | 36 | 26.10.2026, 16:37 МСК |
| AS44907 | RIPEstat | 2 | 26.10.2026, 16:37 МСК |
| AS54115 | RIPEstat | 3 | 26.10.2026, 16:37 МСК |
| AS59930 | RIPEstat | 3 | 26.10.2026, 16:37 МСК |
| AS62014 | RIPEstat | 4 | 26.10.2026, 16:37 МСК |
| AS62041 | RIPEstat | 6 | 26.10.2026, 16:37 МСК |
| AS63293 | RIPEstat | 81 | 26.10.2026, 16:37 МСК |
| AS211157 | RIPEstat | 3 | 26.10.2026, 16:37 МСК |

## 🔐 SHA256

- `routing.json`: `59959ccf6d3998e1dfc20c4067c1be9a63a6b4cb0d6a89734d32b1495f1db3f3`
- `routing.srs`: `59bf14cef6c48dff660b59cf58afca7761d6e3a5aa68daebc824011e986ea5fe`
- `routing.txt`: `f00042bc06770448576da93977bfd8a2482f29e1bd46127c68a5e1df55fa195a`

<details>
<summary>🔄 Изменения — первые 20 записей в каждой группе</summary>

### domains

**➕ Добавлено: 5**

- `domain_suffix:kakaxing.com`
- `domain_suffix:netflix.com.edgesuite.net`
- `domain_suffix:spicyapi.ai`
- `domain_suffix:spicyapi.com`
- `domain_suffix:spotify.com.edgesuite.net`

**➖ Удалено: 2**

- `domain:netflix.com.edgesuite.net`
- `domain:spotify.com.edgesuite.net`

### scoped_udp

**➕ Добавлено: 0**

- —

**➖ Удалено: 0**

- —

### scoped_https

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

### BGP:AS11807

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

### BGP:AS54115

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

### Custom:discord:scoped-udp

**➕ Добавлено: 0**

- —

**➖ Удалено: 0**

- —

### Discord:cdn-dns:https

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

### ITDog:service:whatsapp

**➕ Добавлено: 0**

- —

**➖ Удалено: 0**

- —

### Meta:ITDog-IPv4

**➕ Добавлено: 0**

- —

**➖ Удалено: 0**

- —

### Meta:ITDog-IPv6

**➕ Добавлено: 0**

- —

**➖ Удалено: 0**

- —

### Meta:Loyalsoldier

**➕ Добавлено: 0**

- —

**➖ Удалено: 0**

- —

### Meta:MetaCubeX

**➕ Добавлено: 0**

- —

**➖ Удалено: 0**

- —

### Meta:geofeed

**➕ Добавлено: 0**

- —

**➖ Удалено: 0**

- —

### Meta:geofeed-corp

**➕ Добавлено: 0**

- —

**➖ Удалено: 0**

- —

### WhatsApp:cdn-dns

**➕ Добавлено: 38**

- `157.240.234.60/32`
- `157.240.241.1/32`
- `157.240.241.200/32`
- `157.240.241.60/31`
- `157.240.254.12/32`
- `2a03:2880:f012:10c:face:b00c:0:3/128`
- `2a03:2880:f012:1d2:face:b00c:0:69e0/128`
- `2a03:2880:f212:1c4:face:b00c:0:7260/128`
- `2a03:2880:f212:1d1:face:b00c:0:167/128`
- `2a03:2880:f307:120:face:b00c:0:167/128`
- `2a03:2880:f322:120:face:b00c:0:167/128`
- `2a03:2880:f366:120:face:b00c:0:167/128`
- `2a03:2880:f367:120:face:b00c:0:167/128`
- `2a03:2880:f381:120:face:b00c:0:167/128`
- `2a03:2880:f381:121:face:b00c:0:7260/128`
- `2a03:2880:f381:195:face:b00c:0:4619/128`
- `2a03:2880:f381:196:face:b00c:0:69e0/128`
- `2a03:2880:f381:1:face:b00c:0:25de/128`
- `2a03:2880:f381:80:face:b00c:0:3/128`
- `2a03:2880:f381:8d:face:b00c:0:2/128`
- … ещё 18; полный список в `dist/report.json`.

**➖ Удалено: 32**

- `2a03:2880:f31a:120:face:b00c:0:167/128`
- `2a03:2880:f32a:120:face:b00c:0:167/128`
- `2a03:2880:f346:120:face:b00c:0:167/128`
- `2a03:2880:f36b:120:face:b00c:0:167/128`
- `2a03:2880:f36e:120:face:b00c:0:167/128`
- `2a03:2880:f36e:121:face:b00c:0:7260/128`
- `2a03:2880:f36e:195:face:b00c:0:4619/128`
- `2a03:2880:f36e:196:face:b00c:0:69e0/128`
- `2a03:2880:f36e:1:face:b00c:0:25de/128`
- `2a03:2880:f36e:80:face:b00c:0:3/128`
- `2a03:2880:f36e:8d:face:b00c:0:2/128`
- `2a03:2880:f389:120:face:b00c:0:167/128`
- `2a03:2880:f38a:120:face:b00c:0:167/128`
- `2a03:2880:f38a:121:face:b00c:0:7260/128`
- `2a03:2880:f38a:196:face:b00c:0:69e0/128`
- `2a03:2880:f38a:80:face:b00c:0:3/128`
- `31.13.78.60/32`
- `57.144.103.32/32`
- `57.144.105.32/32`
- `57.144.143.32/32`
- … ещё 12; полный список в `dist/report.json`.

### WhatsApp:cdn-hosts

**➕ Добавлено: 0**

- —

**➖ Удалено: 0**

- —

### custom-domains.txt

**➕ Добавлено: 2**

- `domain_suffix:spicyapi.ai`
- `domain_suffix:spicyapi.com`

**➖ Удалено: 0**

- —

### custom-ip-cidrs.txt

**➕ Добавлено: 0**

- —

**➖ Удалено: 0**

- —

### itdog

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

### v2fly:autodesk

**➕ Добавлено: 0**

- —

**➖ Удалено: 0**

- —

### v2fly:canva

**➕ Добавлено: 0**

- —

**➖ Удалено: 0**

- —

### v2fly:category-ai-!cn

**➕ Добавлено: 3**

- `domain:appsgenaiserver-pa.clients.google.com`
- `domain:appsgenaiserver-pa.clients6.google.com`
- `domain:appsgenaiserver-pa.googleapis.com`

**➖ Удалено: 0**

- —

### v2fly:category-ai-chat-!cn

**➕ Добавлено: 3**

- `domain:appsgenaiserver-pa.clients.google.com`
- `domain:appsgenaiserver-pa.clients6.google.com`
- `domain:appsgenaiserver-pa.googleapis.com`

**➖ Удалено: 0**

- —

### v2fly:category-ai-cn

**➕ Добавлено: 1**

- `domain_suffix:kakaxing.com`

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

**➕ Добавлено: 3**

- `domain:appsgenaiserver-pa.clients.google.com`
- `domain:appsgenaiserver-pa.clients6.google.com`
- `domain:appsgenaiserver-pa.googleapis.com`

**➖ Удалено: 0**

- —

### v2fly:google-deepmind

**➕ Добавлено: 3**

- `domain:appsgenaiserver-pa.clients.google.com`
- `domain:appsgenaiserver-pa.clients6.google.com`
- `domain:appsgenaiserver-pa.googleapis.com`

**➖ Удалено: 0**

- —

### v2fly:google-gemini

**➕ Добавлено: 3**

- `domain:appsgenaiserver-pa.clients.google.com`
- `domain:appsgenaiserver-pa.clients6.google.com`
- `domain:appsgenaiserver-pa.googleapis.com`

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

### v2fly:hdrezka

**➕ Добавлено: 0**

- —

**➖ Удалено: 0**

- —

### v2fly:instagram

**➕ Добавлено: 0**

- —

**➖ Удалено: 0**

- —

### v2fly:jetbrains

**➕ Добавлено: 0**

- —

**➖ Удалено: 0**

- —

### v2fly:mega

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

**➕ Добавлено: 7**

- `domain:dc.applicationinsights.azure.com`
- `domain:dc.services.visualstudio.com`
- `domain:live.applicationinsights.azure.com`
- `domain:rt.services.visualstudio.com`
- `domain_suffix:data.microsoft.com`
- `domain_suffix:in.applicationinsights.azure.com`
- `domain_suffix:telemetry.microsoft.com`

**➖ Удалено: 0**

- —

### v2fly:microsoft-dev

**➕ Добавлено: 2**

- `domain:dc.services.visualstudio.com`
- `domain:rt.services.visualstudio.com`

**➖ Удалено: 0**

- —

### v2fly:netflix

**➕ Добавлено: 1**

- `domain_suffix:netflix.com.edgesuite.net`

**➖ Удалено: 1**

- `domain:netflix.com.edgesuite.net`

### v2fly:nexusmods

**➕ Добавлено: 0**

- —

**➖ Удалено: 0**

- —

### v2fly:notion

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

### v2fly:protonmail

**➕ Добавлено: 0**

- —

**➖ Удалено: 0**

- —

### v2fly:rutracker

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

**➕ Добавлено: 1**

- `domain_suffix:spotify.com.edgesuite.net`

**➖ Удалено: 1**

- `domain:spotify.com.edgesuite.net`

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

### v2fly:tmdb

**➕ Добавлено: 0**

- —

**➖ Удалено: 0**

- —

### v2fly:twitter

**➕ Добавлено: 0**

- —

**➖ Удалено: 0**

- —

### v2fly:ubisoft

**➕ Добавлено: 0**

- —

**➖ Удалено: 0**

- —

### v2fly:unity

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


## Discord: правила с протоколами и портами

| Network | Destination ports | IPv4 CIDRs | IPv6 CIDRs |
|---|---|---:|---:|
| udp | 50000:65535 | 8 | 1 |
| udp | 19000:20000 | 1 | 0 |
| udp | 50000:50099, 19200:19400 | 13 | 0 |
| tcp, udp | 443 | 10 | 0 |

Each rule requires BOTH its transport and destination-port conditions; these entries are not promoted to the unrestricted IP rule.
Counts above for ordinary IPv4/IPv6 prefixes exclude all scoped rules.
