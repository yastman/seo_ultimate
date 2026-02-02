# UK Quality Gate Report: aktivnaya-pena

**Дата:** 2026-02-02
**Статус:** ❌ FAIL

---

## Validation Results

| Перевірка | Статус | Деталі |
|-----------|--------|--------|
| Data JSON | ✅ | Valid, 11 keywords, primary: "активна піна для авто" |
| Meta tags | ✅ | Title: 42 chars, Desc: 124 chars |
| Title містить "Купити" | ❌ | Missing "Купити" in title |
| H1 БЕЗ "Купити" | ✅ | H1: "Активна піна для авто" |
| H1 ≠ Title | ✅ | Different |
| UK Terminology | ✅ | No RU terms found |
| Keyword Density | ✅ | Stem max 1.82% (авт*), всі в нормі |
| Classic Nausea | ✅ | 3.46 (≤3.5) |
| Academic Nausea | ⚠️ | 3.5% (<7% — сухий текст) |
| Water | ⚠️ | 36.2% (<40% мінімум) |
| Word Count | ❌ | 753 слів (>700 ліміт) |
| H2 з keyword | ✅ | 4 з 6 H2 містять "піна/мийка" |
| Патерни "Якщо X→Y" | ✅ | 3+ знайдено |
| Primary in H1 | ❌ | H1="Піна для миття авто", primary="Активна піна для авто" |
| Primary in Intro | ❌ | "активна піна для авто" не в перших 150 символах |

---

## Keywords Coverage (audit_coverage.py)

| Джерело | Статус | Результат |
|---------|--------|-----------|
| Keywords (primary) | ❌ | 1/2 (50%) — BLOCKER |
| Keywords (secondary) | ⚠️ | 3/4 (75%) |
| Keywords (supporting) | ❌ | 1/4 (25%) |
| Keywords (semantic) | ❌ | 3/11 (27.3%) |

### NOT COVERED Keywords:

**Primary (BLOCKER):**
- "активна піна для авто" (1600 vol) — SYNONYM match only → NOT COVERED

**Secondary:**
- "активна піна для автомийки" — PARTIAL (100% lemmas)

**Supporting:**
- "активна піна купити" — PARTIAL (66%)
- "активна піна ціна" — PARTIAL (66%)
- "активна піна для авто відгуки" — PARTIAL (80%)

**Semantic (keywords[]):**
- "хімія для миття авто" (1000 vol) — PARTIAL
- "автохімія для миття авто" (390 vol) — PARTIAL
- "засоби для миття авто" (320 vol) — PARTIAL
- "хімія для безконтактної мийки" (140 vol) — PARTIAL
- "хімія для мийки самообслуговування" (110 vol) — PARTIAL
- "засоби для мийки самообслуговування" (90 vol) — PARTIAL
- "гель для миття авто" (90 vol) — PARTIAL

---

## Issues Found (BLOCKERS)

1. **Title missing "Купити"** — комерційний модифікатор відсутній
2. **H1 не збігається з primary keyword** — H1: "Піна для миття авто", meta H1: "Активна піна для авто"
3. **Primary keyword не в intro** — "активна піна для авто" має бути в перших 150 символах
4. **Primary keyword coverage 50%** — головний ключ "активна піна для авто" має статус SYNONYM (NOT COVERED)
5. **Word count 753** — перевищує ліміт 700 слів

---

## Issues Found (WARNINGS)

1. **Academic nausea 3.5%** — занизька (<7%), текст "сухий"
2. **Water 36.2%** — нижче мінімуму 40%
3. **Supporting coverage 25%** — нижче 80% threshold
4. **Semantic coverage 27.3%** — нижче 60% threshold (для 11 ключів)

---

## Recommendations

1. **Виправити Title:** додати "Купити" → "Активна піна для авто — купити, ціни | Ultimate"
2. **Синхронізувати H1:** змінити H1 в контенті з "Піна для миття авто" на "Активна піна для авто"
3. **Додати primary в intro:** переписати перший абзац, включивши точну фразу "активна піна для авто"
4. **Скоротити текст:** прибрати зайві деталі, скоротити до 500-700 слів
5. **Збільшити water:** додати звернення "вам", "якщо ви", більше зв'язуючих слів
6. **Покрити непокриті ключі:** інтегрувати "хімія для миття авто", "засоби для миття авто" в текст

---

## Decision

**❌ FAIL** — Виправити BLOCKERS:
- Title без "Купити"
- H1 mismatch
- Primary keyword відсутній в intro
- Primary coverage <100%
- Word count >700

Після виправлень запустити: `/uk-quality-gate aktivnaya-pena`

---

**Валідатор:** W1
**Версія скілла:** UK Quality Gate v3.3
