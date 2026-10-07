# 📊 Отчёт сборки правил AWG

## 🧭 Общая информация

> 🕒 **Сборка:** 07.10.2026, 16:17 МСК  
> 📦 **Репозиторий:** SkyNextGen/awg-rules  
> 📄 **Файлы:** `dist/routing.json` и `dist/routing.srs`  
> 🗓 **Расписание:** понедельник, 06:23 МСК; также вручную и после изменения кода/настроек  
> 🔄 **Сравнение со сборкой:** 07.10.2026, 16:08 МСК

---

## 🧮 Итог сборки

| Показатель | Всего | Добавлено / удалено |
|---|---:|---|
| Доменные правила | 1914 | +13 / -0 |
| IPv4-префиксы | 84 | +0 / -0 |
| IPv6-префиксы | 43 | +0 / -0 |

Другие доменные условия (keyword/regexp): **1**. Они также учитываются в списке изменений.

**Обрезка:** НЕТ. Проверены допустимые размеры, сети и обратное преобразование JSON → SRS → JSON.

Изменения показывают записи правил: укрупнение CIDR или замена поддоменов одним suffix может изменить счётчики без потери покрытия.

## 🚦 Статус

### ✅ Сборка завершена

### 🟢 Предупреждений нет

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
| custom-domains.txt | 123 | +28 / -0 |
| custom-ip-cidrs.txt | 4 | +0 / -0 |
| itdog | 1181 | +0 / -0 |
| service-cdn.json | 0 | +0 / -0 |
| service-domains.txt | 25 | +0 / -0 |
| v2fly:discord | 28 | +0 / -0 |
| v2fly:facebook | 397 | +0 / -0 |
| v2fly:instagram | 74 | +0 / -0 |
| v2fly:openai | 23 | +0 / -0 |
| v2fly:pornhub | 9 | +0 / -0 |
| v2fly:telegram | 21 | +0 / -0 |
| v2fly:ubisoft | 31 | +0 / -0 |
| v2fly:wbgames | 6 | +0 / -0 |
| v2fly:whatsapp | 13 | +0 / -0 |
| v2fly:youtube | 178 | +0 / -0 |

Записи разных источников могут пересекаться, поэтому сумма строк этой таблицы не равна итоговому числу правил. Для нового формата источников первый запуск сохраняет базу сравнения.

## 📈 Тренд за последние успешные запуски

Использовано запусков: **3 из 7**. Сравнение выполняется с предыдущей успешной сборкой, включая ручные запуски.

| Показатель | Среднее | Δ к прошлой |
|---|---:|---:|
| Домены | 1905.3 | +13 |
| IPv4 | 84.0 | +0 |
| IPv6 | 43.0 | +0 |

| Сборка (МСК) | Домены | IPv4 | IPv6 |
|---|---:|---:|---:|
| 07.10.2026, 15:44 МСК | 1901 | 84 | 43 |
| 07.10.2026, 16:08 МСК | 1901 | 84 | 43 |
| 07.10.2026, 16:17 МСК | 1914 | 84 | 43 |

## 🌐 BGP и fallback

| ASN | Источник | Префиксов до общего объединения | Получено (МСК) |
|---|---|---:|---|
| AS32934 | RIPEstat | 36 | 07.10.2026, 16:17 МСК |
| AS44907 | RIPEstat | 2 | 07.10.2026, 16:17 МСК |
| AS59930 | RIPEstat | 3 | 07.10.2026, 16:17 МСК |
| AS62014 | RIPEstat | 4 | 07.10.2026, 16:17 МСК |
| AS62041 | RIPEstat | 6 | 07.10.2026, 16:17 МСК |
| AS63293 | RIPEstat | 79 | 07.10.2026, 16:17 МСК |
| AS211157 | RIPEstat | 3 | 07.10.2026, 16:17 МСК |

## 🔐 SHA256

- `routing.json`: `0e2a7e0381383d6340052ddfba8b23031d81e822cb3b69954fb920f29acfc48c`
- `routing.srs`: `05ab44d0a73102590005087c926058b3259c5a6debe642d45e61ec154755a04f`

<details>
<summary>🔄 Изменения — первые 20 записей в каждой группе</summary>

### domains

**➕ Добавлено: 13**

- `domain_suffix:booktracker.work`
- `domain_suffix:eu.org`
- `domain_suffix:freetp.org`
- `domain_suffix:newstudio.tv`
- `domain_suffix:rutracker.ru`
- `domain_suffix:rutrc.org`
- `domain_suffix:rutrk.org`
- `domain_suffix:stealth.si`
- `domain_suffix:t-ru.org`
- `domain_suffix:torrent.by`
- `domain_suffix:torrindex.net`
- `domain_suffix:wstracker.online`
- `domain_suffix:ysagin.top`

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

### custom-domains.txt

**➕ Добавлено: 28**

- `domain_suffix:1337x.to`
- `domain_suffix:booktracker.org`
- `domain_suffix:booktracker.work`
- `domain_suffix:eu.org`
- `domain_suffix:filmitorrent.net`
- `domain_suffix:freetp.org`
- `domain_suffix:kinozal.me`
- `domain_suffix:newstudio.tv`
- `domain_suffix:nnmclub.to`
- `domain_suffix:nnmstatic.win`
- `domain_suffix:rustorka.com`
- `domain_suffix:rutor.info`
- `domain_suffix:rutor.is`
- `domain_suffix:rutor.org`
- `domain_suffix:rutracker.cc`
- `domain_suffix:rutracker.net`
- `domain_suffix:rutracker.org`
- `domain_suffix:rutracker.ru`
- `domain_suffix:rutracker.wiki`
- `domain_suffix:rutrc.org`
- … ещё 8; полный список в `dist/report.json`.

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

### v2fly:discord

**➕ Добавлено: 0**

- —

**➖ Удалено: 0**

- —

### v2fly:facebook

**➕ Добавлено: 0**

- —

**➖ Удалено: 0**

- —

### v2fly:instagram

**➕ Добавлено: 0**

- —

**➖ Удалено: 0**

- —

### v2fly:openai

**➕ Добавлено: 0**

- —

**➖ Удалено: 0**

- —

### v2fly:pornhub

**➕ Добавлено: 0**

- —

**➖ Удалено: 0**

- —

### v2fly:telegram

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
