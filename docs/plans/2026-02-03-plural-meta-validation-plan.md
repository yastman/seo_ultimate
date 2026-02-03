# Plural Meta Validation — Implementation Plan

> **For Claude:** REQUIRED SUB-SKILL: Use superpowers:executing-plans to implement this plan task-by-task.

**Goal:** Fix 16 UK meta validation failures by adding plural support to keyword_utils and validate_meta.

**Architecture:** Add `to_plural()` and `phrase_to_plural()` to MorphAnalyzer, update validate_meta.py to check plural forms, update skills to clarify Title = H1 = plural formula.

**Tech Stack:** Python, pymorphy3, pytest

---

## Task 1: Add to_plural() to MorphAnalyzer

**Files:**
- Modify: `scripts/keyword_utils.py:220-230`
- Test: `tests/unit/test_keyword_utils.py`

**Step 1: Write the failing test**

```python
# tests/unit/test_keyword_utils.py

def test_to_plural_ru():
    """Test Russian singular to plural conversion."""
    from scripts.keyword_utils import MorphAnalyzer

    morph = MorphAnalyzer("ru")

    assert morph.to_plural("очиститель") == "очистители"
    assert morph.to_plural("набор") == "наборы"
    assert morph.to_plural("губка") == "губки"
    assert morph.to_plural("ведро") == "вёдра"
    assert morph.to_plural("воск") == "воски"
    assert morph.to_plural("шампунь") == "шампуни"


def test_to_plural_uk():
    """Test Ukrainian singular to plural conversion."""
    from scripts.keyword_utils import MorphAnalyzer

    morph = MorphAnalyzer("uk")

    assert morph.to_plural("очищувач") == "очищувачі"
    assert morph.to_plural("набір") == "набори"
    assert morph.to_plural("губка") == "губки"
    assert morph.to_plural("відро") == "відра"
    assert morph.to_plural("шампунь") == "шампуні"


def test_to_plural_preserves_capitalization():
    """Test that capitalization is preserved."""
    from scripts.keyword_utils import MorphAnalyzer

    morph = MorphAnalyzer("ru")

    assert morph.to_plural("Очиститель") == "Очистители"
    assert morph.to_plural("Губка") == "Губки"
```

**Step 2: Run test to verify it fails**

Run: `pytest tests/unit/test_keyword_utils.py::test_to_plural_ru -v`
Expected: FAIL with "AttributeError: 'MorphAnalyzer' object has no attribute 'to_plural'"

**Step 3: Write minimal implementation**

Add to `scripts/keyword_utils.py` after `get_all_forms()` method (around line 206):

```python
    # Fallback plural dictionaries for words pymorphy can't inflect
    _PLURAL_FALLBACK_RU: dict[str, str] = {
        "набор": "наборы",
        "губка": "губки",
        "ведро": "вёдра",
        "средство": "средства",
        "ведро": "вёдра",
    }

    _PLURAL_FALLBACK_UK: dict[str, str] = {
        "набір": "набори",
        "губка": "губки",
        "відро": "відра",
        "засіб": "засоби",
        "віск": "воски",
        "круг": "круги",
        "торнадор": "торнадори",
        "машинка": "машинки",
        "щітка": "щітки",
        "рукавичка": "рукавички",
        "ганчірка": "ганчірки",
        "ємність": "ємності",
        "пензель": "пензлі",
    }

    @lru_cache(maxsize=1000)
    def to_plural(self, word: str) -> str:
        """
        Convert word to plural nominative case.

        очиститель → очистители
        губка → губки
        набір → набори

        Returns original word if conversion fails.
        """
        word_lower = word.lower()

        # Check fallback dictionary first
        fallback = self._PLURAL_FALLBACK_UK if self.lang == "uk" else self._PLURAL_FALLBACK_RU
        if word_lower in fallback:
            result = fallback[word_lower]
            if word[0].isupper():
                return result.capitalize()
            return result

        # Try pymorphy inflection
        if self._use_pymorphy and self._morph:
            parsed = self._morph.parse(word_lower)
            if parsed:
                non_surname = [p for p in parsed if "Surn" not in p.tag]
                p = non_surname[0] if non_surname else parsed[0]

                try:
                    plural = p.inflect({"plur", "nomn"})
                    if plural:
                        result = plural.word
                        if word[0].isupper():
                            return result.capitalize()
                        return result
                except Exception:
                    pass

        return word
```

**Step 4: Run test to verify it passes**

Run: `pytest tests/unit/test_keyword_utils.py::test_to_plural_ru tests/unit/test_keyword_utils.py::test_to_plural_uk tests/unit/test_keyword_utils.py::test_to_plural_preserves_capitalization -v`
Expected: 3 passed

**Step 5: Commit**

```bash
git add scripts/keyword_utils.py tests/unit/test_keyword_utils.py
git commit -m "feat(keyword_utils): add to_plural() for singular to plural conversion"
```

---

## Task 2: Add phrase_to_plural() to MorphAnalyzer

**Files:**
- Modify: `scripts/keyword_utils.py`
- Test: `tests/unit/test_keyword_utils.py`

**Step 1: Write the failing test**

```python
def test_phrase_to_plural_ru():
    """Test Russian phrase plural conversion (first word only)."""
    from scripts.keyword_utils import MorphAnalyzer

    morph = MorphAnalyzer("ru")

    assert morph.phrase_to_plural("очиститель дисков") == "Очистители дисков"
    assert morph.phrase_to_plural("губка для авто") == "Губки для авто"
    assert morph.phrase_to_plural("набор для детейлинга") == "Наборы для детейлинга"


def test_phrase_to_plural_uk():
    """Test Ukrainian phrase plural conversion (first word only)."""
    from scripts.keyword_utils import MorphAnalyzer

    morph = MorphAnalyzer("uk")

    assert morph.phrase_to_plural("очищувач слідів комах") == "Очищувачі слідів комах"
    assert morph.phrase_to_plural("губка для авто") == "Губки для авто"
    assert morph.phrase_to_plural("набір для миття авто") == "Набори для миття авто"
```

**Step 2: Run test to verify it fails**

Run: `pytest tests/unit/test_keyword_utils.py::test_phrase_to_plural_ru -v`
Expected: FAIL with "AttributeError: 'MorphAnalyzer' object has no attribute 'phrase_to_plural'"

**Step 3: Write minimal implementation**

Add to `scripts/keyword_utils.py` after `to_plural()` method:

```python
    def phrase_to_plural(self, phrase: str) -> str:
        """
        Convert phrase to plural (first word only).

        "очиститель дисков" → "Очистители дисков"
        "губка для авто" → "Губки для авто"
        """
        words = phrase.split()
        if not words:
            return phrase

        first_word = words[0]
        plural_first = self.to_plural(first_word)

        # Capitalize first word
        if plural_first:
            plural_first = plural_first.capitalize()

        return " ".join([plural_first] + words[1:])
```

**Step 4: Run test to verify it passes**

Run: `pytest tests/unit/test_keyword_utils.py::test_phrase_to_plural_ru tests/unit/test_keyword_utils.py::test_phrase_to_plural_uk -v`
Expected: 2 passed

**Step 5: Commit**

```bash
git add scripts/keyword_utils.py tests/unit/test_keyword_utils.py
git commit -m "feat(keyword_utils): add phrase_to_plural() for phrase conversion"
```

---

## Task 3: Update validate_meta.py to accept plural forms

**Files:**
- Modify: `scripts/validate_meta.py:425-460`
- Test: `tests/unit/test_validate_meta.py`

**Step 1: Write the failing test**

```python
def test_validate_title_accepts_plural():
    """Title with plural form of primary_keyword should PASS."""
    from scripts.validate_meta import validate_title

    # primary_keyword = "очищувач слідів комах" (singular)
    # Title uses plural = "Очищувачі слідів комах"
    result = validate_title(
        "Очищувачі слідів комах — купити, ціни | Ultimate",
        primary_keywords=["очищувач слідів комах"],
        lang="uk"
    )

    assert result["checks"]["primary_keyword"]["passed"] is True


def test_validate_description_accepts_singular():
    """Description with singular form should still PASS."""
    from scripts.validate_meta import validate_description

    result = validate_description(
        "Очищувач слідів комах від виробника Ultimate. Засоби для видалення комах. Опт і роздріб.",
        primary_keywords=["очищувач слідів комах"],
        lang="uk"
    )

    assert result["checks"]["primary_keyword"]["passed"] is True
```

**Step 2: Run test to verify it fails**

Run: `pytest tests/unit/test_validate_meta.py::test_validate_title_accepts_plural -v`
Expected: FAIL — current validator doesn't find plural in title

**Step 3: Write minimal implementation**

Modify `scripts/validate_meta.py` `validate_title()` function, around line 238-244:

```python
# 3. Primary keyword check (with stem matching, language-aware)
# Also check plural form
if primary_keywords:
    from scripts.keyword_utils import MorphAnalyzer
    morph = MorphAnalyzer(lang)

    found = []
    for kw in primary_keywords:
        # Check original form
        if keyword_matches(kw, title, lang=lang):
            found.append(kw)
        # Check plural form
        elif keyword_matches(morph.phrase_to_plural(kw), title, lang=lang):
            found.append(morph.phrase_to_plural(kw))

    if found:
        results["checks"]["primary_keyword"]["passed"] = True
        results["checks"]["primary_keyword"]["message"] = f"Found: {found[0]}"
    else:
        results["checks"]["primary_keyword"]["message"] = "Missing primary keyword"
else:
    results["checks"]["primary_keyword"]["passed"] = True
    results["checks"]["primary_keyword"]["message"] = "No keywords to check"
```

**Step 4: Run test to verify it passes**

Run: `pytest tests/unit/test_validate_meta.py::test_validate_title_accepts_plural tests/unit/test_validate_meta.py::test_validate_description_accepts_singular -v`
Expected: 2 passed

**Step 5: Commit**

```bash
git add scripts/validate_meta.py tests/unit/test_validate_meta.py
git commit -m "feat(validate_meta): accept plural forms of primary_keyword in Title"
```

---

## Task 4: Run full validation to verify fixes

**Step 1: Run all meta validation**

Run: `python3 scripts/validate_meta.py --all`
Expected: More categories should PASS now (plural matching)

**Step 2: Check specific failing category**

Run: `python3 scripts/validate_meta.py uk/categories/antimoshka/meta/antimoshka_meta.json --keywords uk/categories/antimoshka/data/antimoshka_clean.json`

If still FAIL — the meta file itself needs regeneration (wrong phrase, not just plural issue).

**Step 3: Document remaining failures**

List categories that still FAIL and why (wrong phrase vs missing plural).

---

## Task 5: Update uk-generate-meta SKILL.md

**Files:**
- Modify: `.claude/skills/uk-generate-meta/SKILL.md`

**Step 1: Update Title/H1 formula section**

Replace the ambiguous formula with clear one:

```markdown
## Title та H1 Формула

**КРИТИЧНО:** Title і H1 використовують **множину**, бо це категорія магазину з багатьма товарами.

```
title_phrase = category_title ?? primary_keyword
H1 = phrase_to_plural(title_phrase)   # множина першого слова
Title = H1 + " — купити..."           # той самий H1
```

**Приклад:**
```
_clean.json: primary_keyword = "очищувач слідів комах"

H1: "Очищувачі слідів комах"      ✅ (множина)
Title: "Очищувачі слідів комах — купити, ціни | Ultimate"  ✅

НЕ ПРАВИЛЬНО:
H1: "Очищувачі від комах"          ❌ (інша фраза!)
```

### IRON RULE (уточнено)

title_phrase використовується **ДОСЛІВНО**.

**Дозволено ТІЛЬКИ:**
1. Капіталізація першої літери
2. Конвертація першого слова в множину

**НЕ ДОЗВОЛЕНО:**
- Скорочувати фразу ("слідів комах" → "від комах")
- Міняти слова
- "Оптимізувати"
```

**Step 2: Update version**

```markdown
**Version:** 17.2 — February 2026

**Changelog v17.2:**
- 🔧 **Чітка формула**: Title = H1 = phrase_to_plural(title_phrase)
- 📋 **IRON RULE уточнено**: дозволено тільки капіталізація + множина
- ❌ **Заборонено**: скорочувати або змінювати фразу
```

**Step 3: Commit**

```bash
git add .claude/skills/uk-generate-meta/SKILL.md
git commit -m "docs(uk-generate-meta): clarify Title = H1 = plural formula"
```

---

## Task 6: Update generate-meta SKILL.md (RU)

**Files:**
- Modify: `.claude/skills/generate-meta/SKILL.md`

**Step 1: Apply same changes as UK skill**

Same formula and IRON RULE updates.

**Step 2: Commit**

```bash
git add .claude/skills/generate-meta/SKILL.md
git commit -m "docs(generate-meta): clarify Title = H1 = plural formula"
```

---

## Task 7: Fix remaining UK meta files

**Step 1: Identify files that need regeneration**

Run: `python3 scripts/validate_meta.py --all --lang uk 2>&1 | grep "❌"`

**Step 2: For each failing file, regenerate with /uk-generate-meta**

Use the skill to regenerate meta with correct plural formula.

**Step 3: Validate all pass**

Run: `python3 scripts/validate_meta.py --all`
Expected: All PASS

**Step 4: Final commit**

```bash
git add uk/categories/*/meta/*_meta.json
git commit -m "fix(uk-meta): regenerate with correct plural formula"
```

---

## Validation Checklist

- [ ] `to_plural()` tests pass
- [ ] `phrase_to_plural()` tests pass
- [ ] `validate_meta.py` accepts plural forms
- [ ] UK skill updated to v17.2
- [ ] RU skill updated to v17.2
- [ ] All meta files PASS validation

---

**Version:** 1.0 — February 2026
