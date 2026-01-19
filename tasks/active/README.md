# Активные задачи

**Обновлено:** 2026-01-19

---

## Текущий процесс

```
/seo-research → Perplexity → /content-generator
```

1. Создаём `RESEARCH_PROMPT.md` через `/seo-research`
2. Прогоняем через Perplexity Deep Research
3. Сохраняем результат в `RESEARCH_DATA.md`
4. Генерируем контент через `/content-generator`

---

## Статус по категориям

**Детальный отчёт:** [`../CONTENT_STATUS.md`](../CONTENT_STATUS.md)

### Сводка

| Статус | Количество |
|--------|------------|
| Research готов | ~20 категорий |
| Research заглушка | ~27 категорий |
| Content готов | ~31 категорий |
| Content нужен | ~23 категории |

---

## Очередь на Research (заглушки <2KB)

### Высокий приоритет (есть контент, нужен research для обогащения)
1. `antibitum`
2. `antimoshka`
3. `obezzhirivateli`
4. `ochistiteli-dvigatelya`
5. `ochistiteli-diskov`
6. `ochistiteli-shin`
7. `antidozhd`
8. `ochistiteli-stekol`
9. `omyvatel`
10. `pyatnovyvoditeli`
11. `sredstva-dlya-khimchistki-salona`
12. `ochistiteli-kozhi`
13. `keramika-i-zhidkoe-steklo`
14. `aktivnaya-pena`
15. `shampuni-dlya-ruchnoy-moyki`

### Средний приоритет (нет контента, нет research)
1. `kislotnyy`
2. `keramika-dlya-diskov`
3. `polirol-dlya-stekla`
4. `akkumulyatornaya`
5. `neytralizatory-zapakha`
6. `zashchitnye-pokrytiya` (L1)
7. `kvik-deteylery`
8. `silanty`
9. `tverdyy-vosk`
10. `zhidkiy-vosk`
11. `podarochnyy`

---

## Очередь на Content (есть research, нет контента)

1. `malyarniy-skotch` — research 5KB
2. `vedra-i-emkosti` — research 5KB
3. `ukhod-za-naruzhnym-plastikom` — research 6KB
4. `mekhovye` — research 6KB
5. `poliroli-dlya-plastika` — research 5KB
6. `ukhod-za-kozhey` — research 5KB

---

## Справочные файлы

| Файл | Назначение |
|------|------------|
| `all_categories_data.json` | Данные всех категорий |
| `SEO_RESEARCH_BATCH.md` | Batch-обработка research |

---

## Аудит и чеклисты

| Файл | Статус | Назначение |
|------|--------|------------|
| `DEEP_AUDIT_CHECKLIST.md` | Справочник | Глубокий аудит категорий |
| `META_AUDIT_CHECKLIST.md` | Справочник | Аудит мета-тегов |
| `RESEARCH_PROMPT_CHECKLIST.md` | Справочник | Чеклист для research промптов |
| `RESEARCH_CONTENT_AUDIT.md` | Справочник | Аудит research данных |
| `RESEARCH_PROMPT_AUDIT.md` | Справочник | Аудит промптов |
| `SYNONYMS_CLEANUP.md` | Справочник | Чистка синонимов |
| `KEYWORDS_CLUSTERING.md` | Справочник | Кластеризация ключевых слов |
