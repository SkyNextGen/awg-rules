# Warner Bros. / WB Games

Проверено 2026-10-07. В `config/custom-domains.txt` закреплены `wbinsights.com` и `wbagora.com` по прямому запросу пользователя, хотя они уже присутствуют в V2Fly `wbgames`. Категория `wbgames` остаётся включённой и обновляется при сборке. Дубли сворачиваются; custom обеспечивает сохранение нужных правил при изменении upstream.

Все записи custom — suffix: корневой домен и любые его поддомены, включая API, account, support, content и другие endpoints под тем же корнем. Это покрытие всех поддоменов перечисленных зон, а не утверждение о полном реестре всех зарегистрированных Warner доменов.

| Домены | Проверяемый источник |
|---|---|
| wbinsights.com, wbagora.com, wbgames.com, warnerbrosgames.com, datarouter.apps.netherrealm.com, wb-agora-hydra-file-storage-k1.s3.amazonaws.com | [V2Fly wbgames](https://github.com/v2fly/domain-list-community/blob/master/data/wbgames), два первых дополнительно заданы пользователем |
| warnerbros.com, warnerbros.co.uk | [Warner Bros.](https://www.warnerbros.com/), [Warner Bros. UK](https://www.warnerbros.co.uk/) |
| wbplay.com | [WBPlay](https://www.wbplay.com/) — WB Games logo и ссылки на go.wbgames.com |
| netherrealm.com | Корневая зона endpoint datarouter.apps.netherrealm.com из V2Fly wbgames; включена для всех поддоменов студии |
| mortalkombat.com | [Официальная поддержка Mortal Kombat](https://mortalkombatgamessupport.wbgames.com/hc/ru/articles/16780033877267) |
| injustice.com | [Сайт](https://www.injustice.com/) перенаправляет на warnerbrosgames.com |
| hogwartslegacy.com, legobatmangame.com, gotdragonfire.com, gotconquest.com, dcworldscollidegame.com | Прямые ссылки на [официальной странице WB Games](https://warnerbrosgames.com/) |
| back4blood.com | [Официальная поддержка WB Games](https://wbgamessupport.wbgames.com/hc/en-us/articles/5446494996627-April-2022-Update) |

Один выделенный S3 hostname добавлен узко. Общие зоны `amazonaws.com`, `cloudfront.net`, `ctfassets.net` и общие CDN ASN из этого набора не включаются. Смена владельцев компаний сама по себе не расширяет маршрутизацию до всех соседних брендов.

Проверка: успешный compile/decompile SRS и наличие всех 17 custom записей в итоговом наборе с учётом suffix покрытия. Проверка доступа с реального AWGM остаётся отдельным шагом. Если конкретный endpoint на другом домене не открывается, его нужно подтвердить по имени из сетевого журнала и добавить отдельно.
