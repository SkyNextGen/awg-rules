# 📊 Отчёт сборки правил AWG

## 🧭 Общая информация

> 🕒 **Сборка:** 11.10.2026, 17:06 МСК  
> 📦 **Репозиторий:** SkyNextGen/awg-rules  
> 📄 **Файлы:** `dist/routing.json` и `dist/routing.srs`  
> 🗓 **Расписание:** понедельник, 23:17 МСК; также вручную и после изменения кода/настроек  
> 🔄 **Сравнение со сборкой:** 11.10.2026, 01:29 МСК

---

## 🧮 Итог сборки

| Показатель | Всего | Добавлено / удалено |
|---|---:|---|
| Доменные правила | 3609 | +1720 / -22 |
| IPv4-префиксы | 84 | +0 / -0 |
| IPv6-префиксы | 43 | +0 / -0 |

Другие доменные условия (keyword/regexp): **7**. Они также учитываются в списке изменений.

**Обрезка:** НЕТ. Проверены допустимые размеры, сети и обратное преобразование JSON → SRS → JSON.

Изменения показывают записи правил: укрупнение CIDR или замена поддоменов одним suffix может изменить счётчики без потери покрытия.

## 🚦 Статус

### ✅ Сборка завершена

### ⚠️ Предупреждения

- Local review build from explicitly fetched SOURCE_CACHE; not a live Python HTTP build
- Discord voice CIDRs are community-derived shared networks, limited to upstream UDP ports; dynamic endpoints and IPv6 low-port Cloudflare coverage are not guaranteed

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
| ITDog:discord:scoped-udp | 2 | первый снимок — сравнение со следующего запуска |
| ITDog:service:discord | 20 | первый снимок — сравнение со следующего запуска |
| ITDog:service:telegram | 20 | первый снимок — сравнение со следующего запуска |
| custom-domains.txt | 124 | +0 / -0 |
| custom-ip-cidrs.txt | 4 | +0 / -0 |
| itdog | 1181 | +0 / -0 |
| service-cdn.json | 0 | +0 / -0 |
| service-domains.txt | 32 | +0 / -0 |
| v2fly:anthropic | 9 | первый снимок — сравнение со следующего запуска |
| v2fly:category-ai-!cn | 190 | первый снимок — сравнение со следующего запуска |
| v2fly:category-ai-chat-!cn | 190 | первый снимок — сравнение со следующего запуска |
| v2fly:category-ai-cn | 115 | первый снимок — сравнение со следующего запуска |
| v2fly:category-ai-ru | 12 | первый снимок — сравнение со следующего запуска |
| v2fly:deepseek | 2 | первый снимок — сравнение со следующего запуска |
| v2fly:discord | 28 | +0 / -0 |
| v2fly:doubao | 32 | первый снимок — сравнение со следующего запуска |
| v2fly:facebook | 397 | +0 / -0 |
| v2fly:google | 1122 | первый снимок — сравнение со следующего запуска |
| v2fly:google-deepmind | 46 | первый снимок — сравнение со следующего запуска |
| v2fly:google-gemini | 46 | первый снимок — сравнение со следующего запуска |
| v2fly:google-play | 10 | первый снимок — сравнение со следующего запуска |
| v2fly:googlefcm | 12 | первый снимок — сравнение со следующего запуска |
| v2fly:instagram | 74 | +0 / -0 |
| v2fly:meta | 555 | первый снимок — сравнение со следующего запуска |
| v2fly:microsoft | 754 | первый снимок — сравнение со следующего запуска |
| v2fly:microsoft-dev | 74 | первый снимок — сравнение со следующего запуска |
| v2fly:netflix | 28 | первый снимок — сравнение со следующего запуска |
| v2fly:nexusmods | 2 | +0 / -0 |
| v2fly:nvidia | 66 | первый снимок — сравнение со следующего запуска |
| v2fly:openai | 23 | +0 / -0 |
| v2fly:patreon | 4 | первый снимок — сравнение со следующего запуска |
| v2fly:perplexity | 5 | первый снимок — сравнение со следующего запуска |
| v2fly:playstation | 4 | первый снимок — сравнение со следующего запуска |
| v2fly:pornhub | 0 | +0 / -9 |
| v2fly:soundcloud | 3 | первый снимок — сравнение со следующего запуска |
| v2fly:spotify | 28 | первый снимок — сравнение со следующего запуска |
| v2fly:telegram | 21 | +0 / -0 |
| v2fly:threads | 2 | первый снимок — сравнение со следующего запуска |
| v2fly:tiktok | 37 | первый снимок — сравнение со следующего запуска |
| v2fly:ubisoft | 31 | +0 / -0 |
| v2fly:wbgames | 6 | +0 / -0 |
| v2fly:whatsapp | 11 | +0 / -0 |
| v2fly:youtube | 178 | +0 / -0 |

Записи разных источников могут пересекаться, поэтому сумма строк этой таблицы не равна итоговому числу правил. Для нового формата источников первый запуск сохраняет базу сравнения.

## 📈 Тренд за последние успешные запуски

Использовано запусков: **7 из 7**. Сравнение выполняется с предыдущей успешной сборкой, включая ручные запуски.

| Показатель | Среднее | Δ к прошлой |
|---|---:|---:|
| Домены | 2153.4 | +1692 |
| IPv4 | 84.0 | +0 |
| IPv6 | 43.0 | +0 |

| Сборка (МСК) | Домены | IPv4 | IPv6 |
|---|---:|---:|---:|
| 07.10.2026, 15:44 МСК | 1901 | 84 | 43 |
| 07.10.2026, 16:08 МСК | 1901 | 84 | 43 |
| 07.10.2026, 16:17 МСК | 1914 | 84 | 43 |
| 07.10.2026, 17:39 МСК | 1915 | 84 | 43 |
| 11.10.2026, 01:27 МСК | 1917 | 84 | 43 |
| 11.10.2026, 01:29 МСК | 1917 | 84 | 43 |
| 11.10.2026, 17:06 МСК | 3609 | 84 | 43 |

## 🌐 BGP и fallback

| ASN | Источник | Префиксов до общего объединения | Получено (МСК) |
|---|---|---:|---|
| AS32934 | RIPEstat | 36 | 11.10.2026, 17:06 МСК |
| AS44907 | RIPEstat | 2 | 11.10.2026, 17:06 МСК |
| AS59930 | RIPEstat | 3 | 11.10.2026, 17:06 МСК |
| AS62014 | RIPEstat | 4 | 11.10.2026, 17:06 МСК |
| AS62041 | RIPEstat | 6 | 11.10.2026, 17:06 МСК |
| AS63293 | RIPEstat | 79 | 11.10.2026, 17:06 МСК |
| AS211157 | RIPEstat | 3 | 11.10.2026, 17:06 МСК |

## 🔐 SHA256

- `routing.json`: `05ed1bcd0016a32a1ad40c5dc20b1ecc547a9292b524269b5003a9c730005cb9`
- `routing.srs`: `7fa1f4f97dcaeee780f57f474d32bb74642afa621f64d91443d4cb4405c7c5d4`

<details>
<summary>🔄 Изменения — первые 20 записей в каждой группе</summary>

### domains

**➕ Добавлено: 1720**

- `domain:ai.zhaomi.cn`
- `domain:apps5.oingo.com`
- `domain:audio-ak-spotify-com.akamaized.net`
- `domain:audio4-ak-spotify-com.akamaized.net`
- `domain:avail.googleflights.net`
- `domain:cdn-spotify-experiments.conductrics.com`
- `domain:clickserve.cc-dt.com`
- `domain:cueme-api.quark.cn`
- `domain:dartsearch-cn.net`
- `domain:github-api.arkoselabs.com`
- `domain:github-cloud.s3.amazonaws.com`
- `domain:github-production-release-asset-2e65be.s3.amazonaws.com`
- `domain:github-production-repository-file-5c1aeb.s3.amazonaws.com`
- `domain:github-production-repository-image-32fea6.s3.amazonaws.com`
- `domain:github-production-upload-manifest-file-7fdce7.s3.amazonaws.com`
- `domain:github-production-user-asset-6210df.s3.amazonaws.com`
- `domain:gongyichuangyi.net`
- `domain:google-ohttp-relay-safebrowsing.fastly-edge.com`
- `domain:googleapis-cn.com`
- `domain:googleapps-cn.com`
- … ещё 1700; полный список в `dist/report.json`.

**➖ Удалено: 22**

- `domain:openaiapi-site.azureedge.net`
- `domain:openaiassets.blob.core.windows.net`
- `domain:openaicom-api-bdcpf8c6d2e9atf6.z01.azurefd.net`
- `domain:openaicomproductionae4b.blob.core.windows.net`
- `domain_suffix:api.jetbrains.ai`
- `domain_suffix:connectivitycheck.android.com`
- `domain_suffix:copilot.microsoft.com`
- `domain_suffix:designer.microsoft.com`
- `domain_suffix:developer.nvidia.com`
- `domain_suffix:elements.envato.com`
- `domain_suffix:firebase-settings.crashlytics.com`
- `domain_suffix:gaytube.com`
- `domain_suffix:install.launcher.omniverse.nvidia.com`
- `domain_suffix:mbk-news.appspot.com`
- `domain_suffix:ntp.msn.com`
- `domain_suffix:phprcdn.com`
- `domain_suffix:porngub.com`
- `domain_suffix:pornhub-deutsch.net`
- `domain_suffix:pornhubapparel.com`
- `domain_suffix:pornhubpremium.com`
- … ещё 2; полный список в `dist/report.json`.

### scoped_udp

**➕ Добавлено: 2**

- `{"ip_cidr": ["104.16.0.0/12"], "network": ["udp"], "port_range": ["19000:20000"]}`
- `{"ip_cidr": ["5.200.14.128/25", "34.0.0.0/14", "35.192.0.0/11", "66.22.192.0/18", "104.16.0.0/12", "138.128.136.0/21", "162.158.0.0/15", "172.64.0.0/13", "2606:4700::/32"], "network": ["udp"], "port_range": ["50000:65535"]}`

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

Первый снимок; предыдущего набора нет.

### ITDog:service:discord

Первый снимок; предыдущего набора нет.

### ITDog:service:telegram

Первый снимок; предыдущего набора нет.

### custom-domains.txt

**➕ Добавлено: 0**

- —

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

### service-cdn.json

**➕ Добавлено: 0**

- —

**➖ Удалено: 0**

- —

### service-domains.txt

**➕ Добавлено: 0**

- —

**➖ Удалено: 0**

- —

### v2fly:anthropic

Первый снимок; предыдущего набора нет.

### v2fly:category-ai-!cn

Первый снимок; предыдущего набора нет.

### v2fly:category-ai-chat-!cn

Первый снимок; предыдущего набора нет.

### v2fly:category-ai-cn

Первый снимок; предыдущего набора нет.

### v2fly:category-ai-ru

Первый снимок; предыдущего набора нет.

### v2fly:deepseek

Первый снимок; предыдущего набора нет.

### v2fly:discord

**➕ Добавлено: 0**

- —

**➖ Удалено: 0**

- —

### v2fly:doubao

Первый снимок; предыдущего набора нет.

### v2fly:facebook

**➕ Добавлено: 0**

- —

**➖ Удалено: 0**

- —

### v2fly:google

Первый снимок; предыдущего набора нет.

### v2fly:google-deepmind

Первый снимок; предыдущего набора нет.

### v2fly:google-gemini

Первый снимок; предыдущего набора нет.

### v2fly:google-play

Первый снимок; предыдущего набора нет.

### v2fly:googlefcm

Первый снимок; предыдущего набора нет.

### v2fly:instagram

**➕ Добавлено: 0**

- —

**➖ Удалено: 0**

- —

### v2fly:meta

Первый снимок; предыдущего набора нет.

### v2fly:microsoft

Первый снимок; предыдущего набора нет.

### v2fly:microsoft-dev

Первый снимок; предыдущего набора нет.

### v2fly:netflix

Первый снимок; предыдущего набора нет.

### v2fly:nexusmods

**➕ Добавлено: 0**

- —

**➖ Удалено: 0**

- —

### v2fly:nvidia

Первый снимок; предыдущего набора нет.

### v2fly:openai

**➕ Добавлено: 0**

- —

**➖ Удалено: 0**

- —

### v2fly:patreon

Первый снимок; предыдущего набора нет.

### v2fly:perplexity

Первый снимок; предыдущего набора нет.

### v2fly:playstation

Первый снимок; предыдущего набора нет.

### v2fly:pornhub

**➕ Добавлено: 0**

- —

**➖ Удалено: 9**

- `domain_suffix:gaytube.com`
- `domain_suffix:phncdn.com`
- `domain_suffix:phprcdn.com`
- `domain_suffix:porngub.com`
- `domain_suffix:pornhub-deutsch.net`
- `domain_suffix:pornhub.com`
- `domain_suffix:pornhub.org`
- `domain_suffix:pornhubapparel.com`
- `domain_suffix:pornhubpremium.com`

### v2fly:soundcloud

Первый снимок; предыдущего набора нет.

### v2fly:spotify

Первый снимок; предыдущего набора нет.

### v2fly:telegram

**➕ Добавлено: 0**

- —

**➖ Удалено: 0**

- —

### v2fly:threads

Первый снимок; предыдущего набора нет.

### v2fly:tiktok

Первый снимок; предыдущего набора нет.

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
