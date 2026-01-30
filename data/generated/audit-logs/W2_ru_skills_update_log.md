# W2: RU Skills Update Log

**Дата:** 2026-01-30
**Задача:** Обновить RU скиллы для интеграции audit_coverage.py

## Обновлённые скиллы

### 1. content-reviewer (v2.0 → v2.1)

**Файл:** `.claude/skills/content-reviewer/SKILL.md`

**Изменения:**
- Step 3 Keywords Coverage заменён на `audit_coverage.py --slug {slug} --lang ru --verbose`
- Добавлены динамические пороги: ≤5 ключей → 70%, 6-15 → 60%, >15 → 50%
- Добавлены статусы покрытия: EXACT, NORM, LEMMA, SYNONYM
- Добавлена диагностика: TOKENIZATION (pH-, 1:10), PARTIAL (≥50% лемм), ABSENT
- Verdict table: "primary X/X, secondary X/X" → "coverage X% (threshold Y%)"

### 2. quality-gate (v3.0 → v3.1)

**Файл:** `.claude/skills/quality-gate/skill.md`

**Изменения:**
- Section 3 Content Validation: добавлен `audit_coverage.py --slug {slug} --lang ru --verbose`
- Добавлен чек "Keywords coverage ≥ threshold"
- Добавлено описание порогов и статусов

### 3. verify-content (v1.0 → v1.1)

**Файл:** `.claude/skills/verify-content/SKILL.md`

**Изменения:**
- Phase 4 Keywords Coverage полностью переписан
- Заменён ручной поиск на `audit_coverage.py --slug {slug} --lang ru --verbose`
- Добавлен детальный формат вывода с группировкой по статусам
- Добавлены динамические пороги

## Статистика изменений

```
.claude/skills/content-reviewer/SKILL.md | 34 ++++++++++++++++++++------
.claude/skills/quality-gate/skill.md     | 22 ++++++++++++-----
.claude/skills/verify-content/SKILL.md   | 42 ++++++++++++++++++++++++--------
3 files changed, 75 insertions(+), 23 deletions(-)
```

## Примечания

- quality-gate был уже частично обновлён другим воркером (W1)
- verify-content пришлось пересоздать из-за проблем с WSL metadata
- Коммит НЕ выполнялся — оставлено для оркестратора
