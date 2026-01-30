# Sync Volume from Master — Design

## Цель

Обновить частотность (volume) в 50 RU категориях из `data/ru_semantics_master.csv` через 6 параллельных воркеров.

## Архитектура

```
┌─────────────────────────────────────────────────────────────┐
│  Оркестратор                                                │
│  1. Запустить 6 воркеров параллельно                        │
│  2. Дождаться завершения                                    │
│  3. Прочитать логи + валидировать JSON                      │
│  4. Сформировать отчёт пользователю                         │
│  5. После одобрения — git commit                            │
└─────────────────────────────────────────────────────────────┘
         │
         ▼
┌────────┬────────┬────────┬────────┬────────┬────────┐
│  W1    │  W2    │  W3    │  W4    │  W5    │  W6    │
│ 8 cat  │ 8 cat  │ 8 cat  │ 9 cat  │ 8 cat  │ 9 cat  │
└────────┴────────┴────────┴────────┴────────┴────────┘
```

## Распределение категорий (алфавитно)

### W1 (8 категорий)
akkumulyatornaya, aksessuary, aksessuary-dlya-naneseniya-sredstv, aktivnaya-pena, antibitum, antidozhd, antimoshka, apparaty-tornador

### W2 (8 категорий)
avtoshampuni, cherniteli-shin, glina-i-avtoskraby, gubki-i-varezhki, keramika-dlya-diskov, keramika-i-zhidkoe-steklo, kisti-dlya-deteylinga, kvik-deteylery

### W3 (8 категорий)
malyarniy-skotch, mekhovye, mikrofibra-i-tryapki, moyka-i-eksterer, nabory, neytralizatory-zapakha, obezzhirivateli, oborudovanie

### W4 (9 категорий)
ochistiteli-diskov, ochistiteli-dvigatelya, ochistiteli-kozhi, ochistiteli-shin, ochistiteli-stekol, omyvatel, opt-i-b2b, polirol-dlya-stekla, poliroli-dlya-plastika

### W5 (8 категорий)
polirovalnye-pasty, polirovka, pyatnovyvoditeli, raspyliteli-i-penniki, shampuni-dlya-ruchnoy-moyki, shchetka-dlya-moyki-avto, silanty, sredstva-dlya-khimchistki-salona

### W6 (9 категорий)
sredstva-dlya-kozhi, tverdyy-vosk, ukhod-za-intererom, ukhod-za-kozhey, ukhod-za-naruzhnym-plastikom, vedra-i-emkosti, voski, zashchitnye-pokrytiya, zhidkiy-vosk

## Что делает каждый воркер

1. Запускает `python3 scripts/sync_semantics.py --categories=X,Y,Z --apply`
2. Записывает лог в `data/generated/audit-logs/W{N}_sync_log.md`

### Формат лога воркера

```markdown
# W{N} Sync Log

## Статистика
- Категорий обработано: N
- Keywords изменено: +X / -Y
- Synonyms изменено: +X / -Y

## Детали по категориям

### {slug}
- keywords: 5 → 6 (+1)
- synonyms: 12 → 15 (+3)

### {slug}
- keywords: 3 → 3 (без изменений)
- synonyms: 8 → 8 (без изменений)

---
**Статус:** ✅ Успешно / ❌ Ошибка
```

## Проверки оркестратора после завершения

1. **Все воркеры завершились** — проверить наличие 6 логов
2. **JSON валидны** — `python3 -c "import json; json.load(open(f))"` для каждого _clean.json
3. **Нет аномалий:**
   - volume не стал 0 ни у одного ключа
   - количество keywords не упало более чем на 50%
4. **Сводный отчёт** — агрегировать статистику из всех логов

## Критерии успеха

- Все 50 категорий синхронизированы
- Все JSON файлы валидны
- Нет потери данных (preserved fields сохранены)
- Пользователь получил понятный отчёт

## Откат при проблемах

```bash
git checkout -- categories/
```
