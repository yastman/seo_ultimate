# UK Skills Sync — Design Document

**Дата:** 2026-01-26
**Статус:** Ready for implementation

---

## Цель

Привести UK скиллы к полному паритету с RU скиллами (эталон).

---

## Принципы

1. **RU = эталон** — UK скиллы должны быть идентичны по структуре и логике
2. **Генерация, не перевод** — UK скиллы генерируют контент на украинском, не переводят
3. **Адаптация путей** — `categories/` → `uk/categories/`
4. **UK терминология** — гума, миття, скло (не резина, мойка, стекло)
5. **Синхронизация версий** — UK версия = RU версия

---

## Таблица адаптации

| RU | UK |
|----|-----|
| `categories/{slug}/` | `uk/categories/{slug}/` |
| `{slug}_ru.md` | `{slug}_uk.md` |
| `/content-generator` | `/uk-content-generator` |
| `language: "ru"` | `language: "uk"` |
| `language_id=3` | `language_id=1` |
| резина | гума |
| мойка | миття |
| стекло | скло |
| чернитель | чорнитель |
| очиститель | очищувач |
| покрытие | покриття |
| поверхность | поверхня |
| защита | захист |

---

## Фаза 1: Основные скиллы (6 файлов)

| # | UK Файл | RU Источник | Версия |
|---|---------|-------------|--------|
| 1 | uk-content-generator/skill.md | content-generator/skill.md | v3.3 |
| 2 | uk-generate-meta/skill.md | generate-meta/skill.md | v15.0 |
| 3 | uk-quality-gate/skill.md | quality-gate/skill.md | v3.0 |
| 4 | uk-seo-research/skill.md | seo-research/SKILL.md | v13.0 |
| 5 | uk-deploy-to-opencart/skill.md | deploy-to-opencart/SKILL.md | v3.0 |
| 6 | uk-content-reviewer/SKILL.md | content-reviewer/SKILL.md | NEW |

---

## Фаза 2: References для uk-content-generator (6 файлов)

| # | UK Файл | RU Источник |
|---|---------|-------------|
| 7 | references/buyer-guide.md | content-generator/references/buyer-guide.md |
| 8 | references/hub-pages.md | content-generator/references/hub-pages.md |
| 9 | references/templates.md | content-generator/references/templates.md |
| 10 | references/validation.md | content-generator/references/validation.md |
| 11 | references/research-mapping.md | content-generator/references/research-mapping.md |
| 12 | references/lsi-synonyms.md | Объединить RU + существующий uk-lsi-synonyms.md |

---

## Фаза 3: References для uk-seo-research (3 файла)

| # | UK Файл | RU Источник |
|---|---------|-------------|
| 13 | references/category-matrix.md | seo-research/references/category-matrix.md |
| 14 | references/example-output.md | seo-research/references/example-output.md |
| 15 | references/perplexity-space-instructions.md | seo-research/references/perplexity-space-instructions.md |

---

## Фаза 4: Дополнительные файлы (1 файл)

| # | UK Файл | RU Источник |
|---|---------|-------------|
| 16 | uk-generate-meta/REFERENCE.md | generate-meta/REFERENCE.md |

---

## Итого: 16 файлов

- **Обновить:** 6 (существующие skill.md)
- **Создать:** 10 (references + новый uk-content-reviewer)

---

## Процесс для каждого файла

```
1. Читаю RU исходник
2. Адаптирую:
   - Язык интерфейса → українська
   - Пути → uk/categories/{slug}/
   - Команды → /uk-*
   - Примеры → украинские
   - Термины → гума, миття, скло
   - Версия → синхронизирую с RU
3. Записываю файл
4. Проверяю структуру
```

---

## Критерий готовности

Каждый UK скилл считается готовым когда:

- [ ] Версия = версия RU аналога
- [ ] Все секции RU присутствуют в UK
- [ ] Пути адаптированы (`uk/categories/`)
- [ ] Команды адаптированы (`/uk-*`)
- [ ] Примеры на украинском
- [ ] Терминология UK (гума, миття, скло)
- [ ] References полные (если есть в RU)

---

## Порядок выполнения

### Batch 1: Основные скиллы
1. uk-content-generator/skill.md
2. uk-generate-meta/skill.md
3. uk-quality-gate/skill.md
4. uk-seo-research/skill.md
5. uk-deploy-to-opencart/skill.md
6. uk-content-reviewer/SKILL.md (новый)

### Batch 2: References uk-content-generator
7-12. references/*.md

### Batch 3: References uk-seo-research
13-15. references/*.md

### Batch 4: Дополнительно
16. uk-generate-meta/REFERENCE.md

---

**Готово к реализации.**
