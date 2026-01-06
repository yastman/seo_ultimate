# PRD: SEO Workflow — Skills + Scripts

**Дата:** 2025-12-10
**Версия:** 4.0
**Статус:** ЗАВЕРШЕНО

---

## Архитектура

```
┌─────────────────────────────────────────────────────────────────────────┐
│                           ВХОДНЫЕ ДАННЫЕ                                │
├─────────────────────────────────────────────────────────────────────────┤
│ data/Структура Ultimate финал - Лист2.csv  ← Keywords + volumes (L1/L2/L3) │
│ data/поисковая_выдача_топ_10.csv           ← SERP URLs конкурентов      │
│ data/mega/mega_competitors.csv             ← Scraped данные конкурентов │
└─────────────────────────────────────────────────────────────────────────┘
                                    │
                                    ▼
┌─────────────────────────────────────────────────────────────────────────┐
│                    ORCHESTRATOR (Opus 4.5) + Skills                     │
│                                                                         │
│  Skill вызывает → Script выполняет → Результат в файл                  │
│                                                                         │
│  task_{slug}.json = CHECKPOINT (переживает контекст)                   │
└─────────────────────────────────────────────────────────────────────────┘
```

---

## Data Flow: Skills + Scripts

```
STAGE    SKILL              SCRIPT                      OUTPUT
────────────────────────────────────────────────────────────────────────────

0        seo-init           (нет скрипта)               categories/{slug}/
                                                        task_{slug}.json

-3       seo-urls           extract_competitor_urls_v2.py   urls_raw.txt

-2       seo-urls           url_preparation_filter.py       urls.txt

5        seo-competitors    filter_mega_competitors.py      meta_patterns.json
                                                            meta_competitors.csv

4+6      seo-data           parse_semantics_to_json.py      {slug}.json (полный)
                                                            с variations

7        seo-research       (MCP Perplexity)                perplexity_research.md

8        seo-content        (LLM генерация)                 {slug}_ru.md

8.1      seo-validate       quality_runner.py               quality_report.json
                            check_simple_v2_md.py           validation.json

10       seo-meta           (LLM генерация)                 {slug}_meta.json

11       seo-package        (копирование)                   deliverables/
```

---

## SEO 2025 v7.0 — Content Standards

| Параметр | Значение | Примечание |
|----------|----------|------------|
| **Символы** | **4000-4500** | Единый для всех tier |
| Слова | 600-680 | |
| H2 | 3-5 | Tier A: 4-5, B/C: 3-4 |
| FAQ | 4-8 | Tier A: 6-8, B: 5-6, C: 4-5 |
| Density | 1-2% | |
| LSI Ratio | ≥5:1 | |

---

## Skills (9 штук)

| Skill | Stage | Script | Input | Output |
|-------|-------|--------|-------|--------|
| **seo-init** | 0 | - | slug, tier | папки, task file |
| **seo-urls** | -3,-2 | `extract_competitor_urls_v2.py`, `url_preparation_filter.py` | SERP CSV | urls.txt |
| **seo-competitors** | 5 | `filter_mega_competitors.py` | mega CSV | meta_patterns.json |
| **seo-data** | 4,6 | `parse_semantics_to_json.py` | семантика CSV + meta_patterns | {slug}.json с variations |
| **seo-research** | 7 | MCP Perplexity | keywords | research.md |
| **seo-content** | 8 | - | keywords JSON | {slug}_ru.md |
| **seo-validate** | 8.1 | `quality_runner.py` | MD + JSON | report |
| **seo-meta** | 10 | - | content | meta JSON |
| **seo-package** | 11 | - | all files | deliverables/ |

---

## Задачи — ВСЕ ЗАВЕРШЕНЫ

### Phase 1: Core Skills ✅

- [x] 1.1 Создать `.claude/skills/` структуру
- [x] 1.2-1.9 Все 9 skills созданы

### Phase 2: Scripts Update ✅

- [x] 2.1 Обновить `seo_utils.py` → v7.0 (4000-4500)
- [x] 2.2 Обновить `check_simple_v2_md.py` → v7.0
- [x] 2.3 Fix density bug (unique positions)
- [x] 2.4 Тесты пройдены

### Phase 3: Missing Pieces ✅

- [x] 3.1 `seo-competitors` skill
- [x] 3.2 `parse_semantics_to_json.py` + TDD тесты
- [x] 3.3 `seo-data` skill v2.0

### Phase 4: Integration Test ✅

- [x] 4.1-4.3 Workflow протестирован

### Phase 5: Cleanup ✅

- [x] 5.1 Старые agents → `.claude/agents_archive/`
- [x] 5.2 Старые docs → `docs/archive/`
- [x] 5.3 INDEX.md, README.md обновлены

---

## Финальный статус

```
Skills:     9/9 ✅
Scripts:    v7.0 ✅
Cleanup:    Завершён ✅
Docs:       Актуализированы ✅
```

---

## Структура после cleanup

```
.claude/
├── skills/           # 9 skills (АКТИВНЫЕ)
│   ├── seo-init/
│   ├── seo-data/
│   ├── seo-competitors/
│   ├── seo-urls/
│   ├── seo-research/
│   ├── seo-content/
│   ├── seo-validate/
│   ├── seo-meta/
│   └── seo-package/
├── agents_archive/   # Старые agents (АРХИВ)
└── commands/

docs/
├── PRD_SKILLS_OPTIMIZATION.md  # Этот файл
├── README.md
├── SCREAMING_FROG_GUIDE.md
└── archive/                     # Старые docs
```

---

## Следующий шаг

**Генерация контента** — запустить полный workflow для категории:

```
"полный workflow для antimoshka tier C"
```

---

**Автор:** Claude Opus 4.5
**Версия:** 4.0
**Обновлено:** 2025-12-10
