# Semantic Audit Design

**Дата:** 2026-01-29
**Статус:** Draft

---

## Проблема

Семантика категорий обновлена (новые ключи, актуальная частотность), но:

1. **keywords[]** может содержать не все уникальные интенты
2. **synonyms[]** может содержать ключи которые должны быть в keywords
3. **variant_of** не везде проставлен
4. **Контент и мета** могут не использовать топовые ключи

**Пример aktivnaya-pena:**
- Сейчас в keywords: 4 ключа
- Должно быть: 6 ключей (+ "шампунь для бесконтактной мойки", "пена для минимойки")

---

## Цель

1. Провести аудит всех 53 RU категорий
2. Исправить структуру _clean.json (keywords vs synonyms)
3. Обновить _meta.json (keywords_in_content)
4. Создать отчёт для обновления контента

---

## Принцип распределения (из semantic-cluster v2.0)

### keywords[] — уникальные интенты

| Критерий | Пример |
|----------|--------|
| Другое слово | "шампунь" vs "пена" |
| Другой сценарий | "для минимойки" vs "для АВД" |
| Другой модификатор | "активная пена" vs "пена для бесконтактной" |

### synonyms[] — варианты

| Критерий | Пример |
|----------|--------|
| Словоформа | авто/автомобиль/машина |
| Diminutive | машина/машинка |
| Коммерческий | "купить X", "X цена" → meta_only |

### Тест

> "Если человек ищет 'шампунь для мойки', удовлетворит ли его страница только со словом 'пена'?"
> - НЕТ → keywords
> - ДА → synonyms

---

## Архитектура аудита

### Фаза 1: Автоматический анализ

Скрипт `scripts/audit_semantic_structure.py`:

```
Input:  categories/{path}/data/{slug}_clean.json
Output: reports/SEMANTIC_AUDIT_2026-01-29.md
```

**Что проверяет:**

1. **Уникальные интенты в synonyms** — ключи которые должны быть в keywords:
   - Другое слово (шампунь vs пена)
   - Другой сценарий (минимойка, АВД)
   - Volume ≥ 50 без variant_of

2. **Отсутствие variant_of** — synonyms без разметки

3. **Покрытие в контенте** — keywords которых нет в тексте

4. **meta_only в Title/Description** — коммерческие ключи не используются

### Фаза 2: Ручная валидация + исправление воркерами

**Распределение по воркерам (10 категорий на воркер):**

| Worker | Категории | Файлы |
|--------|-----------|-------|
| W1 | aksessuary, glavnaya, moyka-i-eksterer (L1) | 3 |
| W2 | avtoshampuni/* | 5-7 |
| W3 | sredstva-dlya-diskov-i-shin/* | 5-7 |
| W4 | ochistiteli-kuzova/* | 5-7 |
| W5 | polirovka/* | 5-7 |
| W6-W10 | остальные | 5-7 каждый |

**Каждый воркер:**
1. Читает отчёт аудита для своих категорий
2. Применяет `/semantic-cluster {slug}`
3. Обновляет _clean.json
4. Обновляет _meta.json → keywords_in_content
5. Логирует в `data/generated/audit-logs/W{N}_semantic.md`

### Фаза 3: Финальный отчёт

```
reports/SEMANTIC_AUDIT_FINAL.md
├── Статистика (было/стало keywords)
├── Категории требующие обновления контента
└── Категории требующие обновления мета
```

---

## Структура отчёта аудита

```markdown
# Semantic Audit Report

## Summary

| Метрика | Значение |
|---------|----------|
| Всего категорий | 53 |
| С проблемами в keywords | X |
| С проблемами в synonyms | Y |
| Требуют обновления контента | Z |

## Critical (keywords неполные)

### aktivnaya-pena

**Проблемы:**
- ❌ "шампунь для бесконтактной мойки" (110) — в synonyms, должен быть в keywords
- ❌ "пена для минимойки" (70) — в synonyms, должен быть в keywords

**Действие:** /semantic-cluster aktivnaya-pena

### cherniteli-shin
...

## Warning (variant_of отсутствует)

### ...

## OK (структура корректна)

- voski
- silanty
...
```

---

## Скрипт аудита

### Логика определения "уникальный интент"

```python
def is_unique_intent(keyword: str, existing_keywords: list[str]) -> bool:
    """
    Проверяет, является ли ключ уникальным интентом.
    """
    kw_lower = keyword.lower()

    # 1. Другое слово (шампунь vs пена)
    unique_words = ["шампунь", "средство", "химия", "состав"]
    for word in unique_words:
        if word in kw_lower:
            # Проверить есть ли уже ключ с этим словом
            if not any(word in ek.lower() for ek in existing_keywords):
                return True

    # 2. Другой сценарий
    scenarios = ["минимойк", "авд", "высокого давления", "ручн", "бесконтакт"]
    for scenario in scenarios:
        if scenario in kw_lower:
            if not any(scenario in ek.lower() for ek in existing_keywords):
                return True

    # 3. Словоформы — НЕ уникальный
    variants = [
        ("авто", "автомобил", "машин"),
        ("мойк", "мыть", "мытьё"),
    ]
    for group in variants:
        matches = [v for v in group if v in kw_lower]
        if matches:
            # Проверить есть ли уже canonical
            for ek in existing_keywords:
                if any(v in ek.lower() for v in group):
                    return False  # Уже есть canonical

    return False  # По умолчанию — не уникальный
```

---

## Workflow выполнения

### День 1: Подготовка

1. [ ] Создать `scripts/audit_semantic_structure.py`
2. [ ] Запустить на всех категориях
3. [ ] Сгенерировать `reports/SEMANTIC_AUDIT_2026-01-29.md`
4. [ ] Review отчёта вручную

### День 2: Исправление (параллельные воркеры)

5. [ ] Распределить категории по воркерам
6. [ ] Каждый воркер: `/semantic-cluster {slug}` для своих категорий
7. [ ] Merge логов воркеров

### День 3: Финализация

8. [ ] Re-run аудита (должно быть 0 Critical)
9. [ ] Создать список категорий для обновления контента
10. [ ] Создать план обновления контента (отдельный дизайн)

---

## Связь с другими процессами

```
semantic-cluster (этот план)
       ↓
_clean.json + _meta.json обновлены
       ↓
content-reviewer (проверка покрытия keywords)
       ↓
content-generator (перегенерация если нужно)
```

---

## Риски

| Риск | Митигация |
|------|-----------|
| Субъективность определения "уникальный интент" | Тест "удовлетворит ли страница?" |
| Много ручной работы | Автоматизация через скрипт + воркеры |
| Поломка существующего контента | Сначала только _clean.json, контент — отдельно |

---

## Acceptance Criteria

1. ✅ Все keywords[] содержат только уникальные интенты
2. ✅ Все synonyms с variant_of имеют разметку родителя
3. ✅ Все meta_only ключи в synonyms
4. ✅ keywords_in_content в _meta.json соответствует keywords[]
5. ✅ Отчёт с категориями для обновления контента

---

**Version:** 1.0
**Author:** Claude + User brainstorming session
