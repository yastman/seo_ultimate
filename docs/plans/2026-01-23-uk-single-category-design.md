# UK Single Category Pipeline Design

**Дата:** 2026-01-23
**Цель:** Создание UK контента для одной категории через последовательность UK скиллов

---

## Текущее состояние

- **Готово:** 3 категории (aktivnaya-pena, antibitum, antimoshka)
- **Следующая:** antidozhd
- **Всего осталось:** 47 категорий
- **База ключей:** `uk/data/uk_keywords.json` (50 категорий)

---

## Pipeline

```
/uk-content-init {slug}
       ↓
/uk-generate-meta {slug}
       ↓
/uk-seo-research {slug}
       ↓
[Perplexity Deep Research — ручной шаг]
       ↓
/uk-content-generator {slug}
       ↓
uk-content-reviewer {slug}
       ↓
/uk-quality-gate {slug}
       ↓
/uk-deploy {slug}
```

---

## Детали шагов

### 1. /uk-content-init {slug}

**Вход:** slug категории, `uk/data/uk_keywords.json`
**Выход:**
- `uk/categories/{slug}/data/{slug}_clean.json`
- `uk/categories/{slug}/meta/` (пустая)
- `uk/categories/{slug}/content/` (пустая)
- `uk/categories/{slug}/research/CONTEXT.md` (ссылка на RU research)

**Действия:**
- Создаёт структуру папок
- Копирует семантику из RU `categories/{slug}/data/{slug}_clean.json`
- Заменяет RU ключи на UK из `uk_keywords.json`

---

### 2. /uk-generate-meta {slug}

**Вход:** `uk/categories/{slug}/data/{slug}_clean.json`
**Выход:** `uk/categories/{slug}/meta/{slug}_meta.json`

**Формат meta.json:**
```json
{
  "slug": "antidozhd",
  "language": "uk",
  "meta": {
    "title": "... | Ultimate",
    "description": "..."
  },
  "h1": "...",
  "keywords_in_content": {
    "primary": [],
    "secondary": [],
    "supporting": []
  }
}
```

**Правила:**
- Title: до 60 символов, главный ключ + бренд
- Description: 120-160 символов, CTA
- H1: уникальный, содержит главный ключ

---

### 3. /uk-seo-research {slug}

**Вход:**
- `uk/categories/{slug}/data/{slug}_clean.json`
- `categories/{slug}/data/PRODUCTS_LIST.md` (RU, для контекста товаров)

**Выход:** `uk/categories/{slug}/research/RESEARCH_PROMPT.md`

**Назначение:** Генерирует промпт для Perplexity Deep Research с:
- Типами товаров в категории
- Характеристиками (формы, базы, эффекты)
- Вопросами для исследования

---

### 4. Perplexity Deep Research (ручной)

**Действия:**
1. Скопировать содержимое `RESEARCH_PROMPT.md`
2. Запустить в Perplexity Deep Research
3. Сохранить результат в `uk/categories/{slug}/research/RESEARCH_DATA.md`

**Альтернатива:** Использовать RU research из `categories/{slug}/research/RESEARCH_DATA.md` если UK-специфика не критична.

---

### 5. /uk-content-generator {slug}

**Вход:**
- `uk/categories/{slug}/data/{slug}_clean.json`
- `uk/categories/{slug}/meta/{slug}_meta.json`
- `uk/categories/{slug}/research/RESEARCH_DATA.md` (или RU fallback)

**Выход:** `uk/categories/{slug}/content/{slug}_uk.md`

**Формат контента:**
- Buyer guide стиль
- H1 из meta
- 2-4 секции H2 с ключами
- 400-700 слов
- Без ссылок и цитат в тексте
- Academic vocabulary ≥7%

---

### 6. uk-content-reviewer {slug}

**Вход:** `uk/categories/{slug}/content/{slug}_uk.md`
**Выход:** Исправленный `{slug}_uk.md`

**Проверки:**
- Плотность ключевых слов (1-3%)
- H2 содержат ключи (мин. 2)
- Нет запрещённых паттернов
- Украинская терминология корректна

**Валидация:** `python scripts/check_keyword_density.py ... --lang uk`

---

### 7. /uk-quality-gate {slug}

**Проверки:**
- [ ] `{slug}_clean.json` валиден
- [ ] `{slug}_meta.json` валиден (Title ≤60, Desc 120-160)
- [ ] `{slug}_uk.md` существует (400-700 слов)
- [ ] SEO структура OK (`check_seo_structure.py --lang uk`)
- [ ] H1 синхронизирован между meta и content

**Выход:** PASS/FAIL с отчётом

---

### 8. /uk-deploy {slug}

**Вход:**
- `uk/categories/{slug}/meta/{slug}_meta.json`
- `uk/categories/{slug}/content/{slug}_uk.md`

**Действия:**
- Обновляет OpenCart через API/SQL
- `language_id=1` (украинский)
- Обновляет: meta_title, meta_description, meta_h1, description

---

## Чеклист для категории

```markdown
## {slug}

- [ ] /uk-content-init
- [ ] /uk-generate-meta
- [ ] /uk-seo-research
- [ ] Perplexity research (или RU fallback)
- [ ] /uk-content-generator
- [ ] uk-content-reviewer
- [ ] /uk-quality-gate — PASS
- [ ] /uk-deploy
- [ ] Отметить в TODO_UK_CONTENT.md
```

---

## Следующие действия

1. Начать с `antidozhd`
2. Выполнить pipeline
3. После успеха — следующая категория по списку

---

## Порядок категорий (L3 первые)

1. antidozhd
2. akkumulyatornaya
3. cherniteli-shin
4. glina-i-avtoskraby
5. gubki-i-varezhki
6. keramika-dlya-diskov
7. kisti-dlya-deteylinga
8. malyarniy-skotch
9. mekhovye
10. nabory
... (полный список в TODO_UK_CONTENT.md)
