<div align="center">

# 🧭 AWG Rules

### Выбранные сервисы через VPN — в одном наборе

Автоматически обновляемые правила для **AWG Manager · TProxy · sing-box**

[![Сборка](https://github.com/SkyNextGen/awg-rules/actions/workflows/build.yml/badge.svg)](https://github.com/SkyNextGen/awg-rules/actions/workflows/build.yml)

**[Подключить набор](#-подключение) · [Сервисы](#-что-внутри) · [Отчёт сборки](dist/report.md)**

</div>

---

## ✨ Возможности

| 🌐 Готовый набор | 🔄 Автоматическое обновление | 🧩 Компактные правила |
|---|---|---|
| Домены и IP для выбранных сервисов | Ежедневная сборка из актуальных источников | Удаление повторений и объединение поддоменов и сетей |

**AWG Rules** помогает направлять трафик нужных сервисов через VPN. В одном файле объединены ITDog, выбранные категории V2Fly и личные дополнения. Направление трафика и VPN-подключение задаются в AWG Manager.

## 🎯 Что внутри

| | Сервисы |
|---|---|
| 💬 Общение | Telegram, WhatsApp, Discord, Signal |
| 📱 Социальные сети | Meta, Facebook, Instagram, Threads, TikTok, Twitter/X |
| 🔎 Google и Microsoft | Google, YouTube, Google Play, FCM, Microsoft и инструменты разработчика |
| 🤖 Нейросети | OpenAI, Anthropic, Gemini, DeepMind, Perplexity, DeepSeek, Doubao и категории AI Китая, России и других стран |
| 🎬 Видео и музыка | Netflix, HDRezka, TMDB, Spotify, SoundCloud |
| 🎮 Игры | PlayStation, NVIDIA, Ubisoft, WB Games, Nexus Mods |
| 💼 Работа и облако | Autodesk, Canva, JetBrains, Notion, MEGA, Proton |
| 🌍 Сообщества и дополнения | Patreon, RuTracker, весь ITDog Russia inside и личные домены/IP |

Покрытие сервисов определяется составом источников. Полный выбор категорий — в [v2fly-categories.txt](config/v2fly-categories.txt).

---

## 🚀 Подключение

**1.** Добавьте удалённый rule-set в AWG Manager / sing-box.  
**2.** Выберите формат **binary** и укажите URL:

```text
https://raw.githubusercontent.com/SkyNextGen/awg-rules/main/dist/routing.srs
```

**3.** Направьте совпадающий трафик в нужный VPN outbound и включите обновление набора.

| [📦 routing.srs](https://raw.githubusercontent.com/SkyNextGen/awg-rules/main/dist/routing.srs) | [📄 routing.json](dist/routing.json) | [📊 Отчёт](dist/report.md) |
|---|---|---|
| Файл для подключения | Правила в читаемом виде | Статус, изменения и источники |

> Для доменных правил нужно определение имени через DNS/sniffing. В режиме TProxy сохраняйте UDP-порты Discord вместе с IP-условиями. Работу IPv6 и звонков проверяйте на своём устройстве.

## 🔄 Обновление и контроль

**Каждый день в 23:17 МСК** GitHub Actions выполняет сборку. Запуск также доступен вручную и после изменений кода или настроек. Возможны задержки расписания GitHub.

| ① Получение | ② Объединение | ③ Проверка | ④ Публикация |
|---|---|---|---|
| Загрузка доменов и IP | Удаление повторений, сокращение суффиксов и сетей | Тесты, формат SRS, покрытие сервисов | Готовый файл и отчёт в Telegram |

**При ошибке проверки остаётся последний успешно опубликованный набор.** Отчёт показывает изменения по источникам, дельты доменов и IP, а также динамику сборок. Ошибка доставки Telegram не отменяет публикацию.

## 🌐 Источники

| Источник | Что добавляет |
|---|---|
| [ITDog](https://github.com/itdoginfo/allow-domains) | Весь Russia inside; дополнительные списки Telegram и Discord; UDP-правила Discord |
| [V2Fly](https://github.com/v2fly/domain-list-community) | Домены выбранных сервисов и категорий |
| [Официальный список Telegram](https://core.telegram.org/resources/cidr.txt) | IP-сети Telegram |
| [RIPEstat](https://stat.ripe.net/) / [bgp.tools](https://bgp.tools/) | Опубликованные IP-маршруты Telegram и Meta |
| Личные списки | Дополнительные домены и IP, заданные вручную |

Telegram, WhatsApp и Discord пересобираются на каждом запуске. Их отдельные JSON находятся в [dist/custom](dist/custom) и уже входят в общий `routing.srs`.

Сети Meta общие для компании. Личные IP могут включать общий хостинг/CDN и направлять через VPN сторонние сервисы. Домены с названием мессенджера в личном списке не обязательно принадлежат этому мессенджеру.

---

## 🛠️ Настройка состава

| Что добавить | Где изменить |
|---|---|
| Сервис или категорию V2Fly | [v2fly-categories.txt](config/v2fly-categories.txt) |
| Личный домен | [custom-domains.txt](config/custom-domains.txt) |
| Личный IP или сеть | [custom-ip-cidrs.txt](config/custom-ip-cidrs.txt) |
| Источники и параметры сборки | [sources.json](config/sources.json) |

**Домены добавляются с поддоменами:** `google.com` уже покрывает `clients6.google.com`. Повторять обе записи не требуется. Для одного IP используйте `/32` у IPv4 или `/128` у IPv6.

<details>
<summary><b>⚙️ Технические подробности</b></summary>

### Обработка правил

Суффикс совпадает с самим доменом и его поддоменами по границам имени. `example.com` покрывает `a.example.com`, но не `notexample.com`. Точные совпадения, ключевые слова и регулярные выражения V2Fly сохраняют свой тип. Вложенные категории загружаются рекурсивно. CIDR объединяются без добавления новых адресов.

### Discord UDP

| Порты назначения | Сети |
|---|---|
| `50000–65535` | Списки Discord IPv4/IPv6 ITDog |
| `19000–20000` | `104.16.0.0/12`, только IPv4 |

Условия **UDP + IP + порт** применяются одновременно. Верхний диапазон для IPv6 — допущение проекта: преобразователь ITDog использует IPv4. Полного покрытия голосовых серверов список не гарантирует; общие подсети могут захватывать сторонний UDP на тех же портах.

### IP и проверка сборки

IP не создаются из DNS-ответов. Автоматический BGP ограничен ASN Telegram **62041, 62014, 59930, 44907, 211157** и Meta **32934, 63293**. При сбое RIPEstat используется bgp.tools, затем проверенный BGP-снимок возрастом до 8 дней с предупреждением.

Сборка проверяет размеры, безопасность сетей, ключевые сервисы и преобразование JSON → SRS → JSON. Используется sing-box **1.12.12**, rule-set **version 1**. Плановый запуск дополнительно проверяет успешные недельные публикации ITDog и 10 минут на распространение. PR выполняет проверки без публикации и Telegram.

### Файлы проекта

| Папка | Назначение |
|---|---|
| `config/` | Состав набора и источники |
| `src/` | Сборщик, проверки и отчёты |
| `tests/` | Автоматические тесты |
| `dist/` | Готовые правила, отчёты и снимки источников |
| `.github/workflows/` | Расписание и публикация |

Готовые файлы в `dist` создаются автоматически. Для Telegram задайте `TG_BOT_TOKEN` и `TG_CHAT_ID` в GitHub Actions Secrets. Ручной запуск: **Actions → Build routing rules → Run workflow**.

</details>

---

<div align="center">

**[📦 Подключить SRS](https://raw.githubusercontent.com/SkyNextGen/awg-rules/main/dist/routing.srs) · [📊 Посмотреть отчёт](dist/report.md) · [🔄 Открыть Actions](https://github.com/SkyNextGen/awg-rules/actions)**

</div>
