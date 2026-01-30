# Semantic Audit Implementation Plan

> **For Claude:** REQUIRED SUB-SKILL: Use superpowers:executing-plans to implement this plan task-by-task.

**Goal:** Провести аудит и исправить структуру keywords/synonyms во всех 53 RU категориях.

**Architecture:** Скрипт аудита анализирует _clean.json, находит уникальные интенты в synonyms, генерирует отчёт. Воркеры параллельно применяют /semantic-cluster для исправления.

**Tech Stack:** Python 3, JSON, параллельные Claude воркеры

---

## Task 1: Создать скрипт аудита

**Files:**
- Create: `scripts/audit_semantic_structure.py`
- Test: `python3 scripts/audit_semantic_structure.py --help`

**Step 1: Создать файл скрипта**

```python
#!/usr/bin/env python3
"""Аудит структуры keywords/synonyms в RU категориях."""

import argparse
import json
from collections import defaultdict
from datetime import date
from pathlib import Path

ROOT = Path(__file__).parent.parent
CATEGORIES_DIR = ROOT / "categories"
REPORTS_DIR = ROOT / "reports"

# Уникальные слова — если есть в synonym, должен быть в keywords
UNIQUE_WORDS = [
    "шампунь", "средство", "химия", "состав", "жидкость",
    "очиститель", "полироль", "воск", "керамика"
]

# Уникальные сценарии
UNIQUE_SCENARIOS = [
    "минимойк", "авд", "высокого давления", "ручн", "бесконтакт",
    "аккумулятор", "сетев", "проводн", "беспроводн"
]

# Группы словоформ (варианты одного слова)
VARIANT_GROUPS = [
    ("авто", "автомобил", "машин"),
    ("мойк", "мыть", "мытьё", "миття"),
    ("полиров", "поліруван"),
    ("очист", "чист"),
]


def load_clean_json(path: Path) -> dict | None:
    """Загружает _clean.json файл."""
    try:
        with open(path, "r", encoding="utf-8") as f:
            return json.load(f)
    except Exception as e:
        print(f"Error loading {path}: {e}")
        return None


def get_all_categories() -> list[tuple[str, Path]]:
    """Находит все категории с _clean.json."""
    categories = []
    for path in CATEGORIES_DIR.rglob("*_clean.json"):
        slug = path.stem.replace("_clean", "")
        categories.append((slug, path))
    return sorted(categories, key=lambda x: x[0])


def extract_keywords(data: dict) -> list[str]:
    """Извлекает список keywords из JSON."""
    keywords = []
    for k in data.get("keywords", []):
        if isinstance(k, dict):
            keywords.append(k.get("keyword", "").lower())
        else:
            keywords.append(str(k).lower())
    return keywords


def extract_synonyms(data: dict) -> list[dict]:
    """Извлекает synonyms с метаданными."""
    synonyms = []
    for s in data.get("synonyms", []):
        if isinstance(s, dict):
            synonyms.append({
                "keyword": s.get("keyword", "").lower(),
                "volume": s.get("volume", 0),
                "variant_of": s.get("variant_of"),
                "use_in": s.get("use_in"),
            })
    return synonyms


def has_word_in_list(word: str, keywords: list[str]) -> bool:
    """Проверяет есть ли слово в списке ключей."""
    return any(word in kw for kw in keywords)


def is_unique_intent(keyword: str, existing_keywords: list[str]) -> tuple[bool, str]:
    """
    Проверяет является ли ключ уникальным интентом.
    Возвращает (is_unique, reason).
    """
    kw_lower = keyword.lower()

    # 1. Уникальное слово
    for word in UNIQUE_WORDS:
        if word in kw_lower:
            if not has_word_in_list(word, existing_keywords):
                return True, f"unique_word:{word}"

    # 2. Уникальный сценарий
    for scenario in UNIQUE_SCENARIOS:
        if scenario in kw_lower:
            if not has_word_in_list(scenario, existing_keywords):
                return True, f"unique_scenario:{scenario}"

    return False, ""


def is_variant(keyword: str, existing_keywords: list[str]) -> tuple[bool, str]:
    """
    Проверяет является ли ключ вариантом существующего.
    Возвращает (is_variant, canonical).
    """
    kw_lower = keyword.lower()

    for group in VARIANT_GROUPS:
        # Проверяем есть ли в ключе слово из группы
        kw_matches = [v for v in group if v in kw_lower]
        if not kw_matches:
            continue

        # Ищем canonical среди existing
        for ek in existing_keywords:
            if any(v in ek for v in group):
                return True, ek

    return False, ""


def audit_category(slug: str, data: dict) -> dict:
    """Аудит одной категории."""
    keywords = extract_keywords(data)
    synonyms = extract_synonyms(data)

    issues = {
        "critical": [],  # synonyms которые должны быть в keywords
        "warning": [],   # synonyms без variant_of
        "info": [],      # meta_only без использования
    }

    for syn in synonyms:
        kw = syn["keyword"]
        volume = syn["volume"]
        variant_of = syn.get("variant_of")
        use_in = syn.get("use_in")

        # Пропускаем meta_only
        if use_in == "meta_only":
            continue

        # Пропускаем низкочастотные
        if volume < 50:
            continue

        # Проверяем уникальный интент
        is_unique, reason = is_unique_intent(kw, keywords)
        if is_unique:
            issues["critical"].append({
                "keyword": kw,
                "volume": volume,
                "reason": reason,
                "action": "move to keywords[]"
            })
            continue

        # Проверяем есть ли variant_of
        if not variant_of:
            is_var, canonical = is_variant(kw, keywords)
            if is_var:
                issues["warning"].append({
                    "keyword": kw,
                    "volume": volume,
                    "suggested_variant_of": canonical,
                    "action": "add variant_of"
                })

    return {
        "slug": slug,
        "keywords_count": len(keywords),
        "synonyms_count": len(synonyms),
        "issues": issues,
        "has_critical": len(issues["critical"]) > 0,
        "has_warning": len(issues["warning"]) > 0,
    }


def generate_report(results: list[dict]) -> str:
    """Генерирует Markdown отчёт."""
    today = date.today().isoformat()

    critical = [r for r in results if r["has_critical"]]
    warning = [r for r in results if r["has_warning"] and not r["has_critical"]]
    ok = [r for r in results if not r["has_critical"] and not r["has_warning"]]

    lines = [
        f"# Semantic Audit Report",
        f"",
        f"**Date:** {today}",
        f"",
        f"## Summary",
        f"",
        f"| Метрика | Значение |",
        f"|---------|----------|",
        f"| Всего категорий | {len(results)} |",
        f"| Critical (keywords неполные) | {len(critical)} |",
        f"| Warning (variant_of отсутствует) | {len(warning)} |",
        f"| OK | {len(ok)} |",
        f"",
    ]

    # Critical
    if critical:
        lines.append("## Critical (keywords неполные)")
        lines.append("")
        for r in critical:
            lines.append(f"### {r['slug']}")
            lines.append("")
            lines.append(f"**Keywords:** {r['keywords_count']} | **Synonyms:** {r['synonyms_count']}")
            lines.append("")
            lines.append("**Проблемы:**")
            for issue in r["issues"]["critical"]:
                lines.append(f"- ❌ `{issue['keyword']}` (vol: {issue['volume']}) — {issue['reason']}")
            lines.append("")
            lines.append(f"**Действие:** `/semantic-cluster {r['slug']}`")
            lines.append("")

    # Warning
    if warning:
        lines.append("## Warning (variant_of отсутствует)")
        lines.append("")
        for r in warning:
            lines.append(f"### {r['slug']}")
            lines.append("")
            for issue in r["issues"]["warning"]:
                lines.append(f"- ⚠️ `{issue['keyword']}` → suggested variant_of: `{issue['suggested_variant_of']}`")
            lines.append("")

    # OK
    if ok:
        lines.append("## OK (структура корректна)")
        lines.append("")
        for r in ok:
            lines.append(f"- ✅ {r['slug']} ({r['keywords_count']} keywords)")
        lines.append("")

    return "\n".join(lines)


def main():
    parser = argparse.ArgumentParser(description="Аудит структуры keywords/synonyms")
    parser.add_argument("--output", "-o", help="Output file path")
    parser.add_argument("--category", "-c", help="Audit single category")
    args = parser.parse_args()

    categories = get_all_categories()

    if args.category:
        categories = [(s, p) for s, p in categories if s == args.category]
        if not categories:
            print(f"Category not found: {args.category}")
            return

    print(f"Auditing {len(categories)} categories...")

    results = []
    for slug, path in categories:
        data = load_clean_json(path)
        if data:
            result = audit_category(slug, data)
            results.append(result)
            status = "❌" if result["has_critical"] else ("⚠️" if result["has_warning"] else "✅")
            print(f"  {status} {slug}")

    report = generate_report(results)

    if args.output:
        output_path = Path(args.output)
    else:
        today = date.today().isoformat()
        output_path = REPORTS_DIR / f"SEMANTIC_AUDIT_{today}.md"

    output_path.parent.mkdir(parents=True, exist_ok=True)
    with open(output_path, "w", encoding="utf-8") as f:
        f.write(report)

    print(f"\nReport saved to: {output_path}")

    # Summary
    critical = len([r for r in results if r["has_critical"]])
    warning = len([r for r in results if r["has_warning"]])
    print(f"\nSummary: {critical} critical, {warning} warning, {len(results) - critical - warning} ok")


if __name__ == "__main__":
    main()
```

**Step 2: Сделать скрипт исполняемым**

Run: `chmod +x scripts/audit_semantic_structure.py`

**Step 3: Проверить help**

Run: `python3 scripts/audit_semantic_structure.py --help`

Expected:
```
usage: audit_semantic_structure.py [-h] [--output OUTPUT] [--category CATEGORY]

Аудит структуры keywords/synonyms
```

**Step 4: Commit**

```bash
git add scripts/audit_semantic_structure.py
git commit -m "feat: add semantic structure audit script"
```

---

## Task 2: Тест на одной категории

**Files:**
- Read: `categories/moyka-i-eksterer/avtoshampuni/aktivnaya-pena/data/aktivnaya-pena_clean.json`

**Step 1: Запустить аудит для aktivnaya-pena**

Run: `python3 scripts/audit_semantic_structure.py --category aktivnaya-pena`

Expected output:
```
Auditing 1 categories...
  ❌ aktivnaya-pena

Report saved to: reports/SEMANTIC_AUDIT_2026-01-29.md
```

**Step 2: Проверить отчёт**

Run: `cat reports/SEMANTIC_AUDIT_2026-01-29.md`

Expected: Должны быть Critical issues для "шампунь для бесконтактной мойки" и "пена для минимойки"

**Step 3: Если результат неверный — отладить скрипт**

Проверить что UNIQUE_WORDS и UNIQUE_SCENARIOS корректны.

---

## Task 3: Полный аудит всех категорий

**Files:**
- Create: `reports/SEMANTIC_AUDIT_2026-01-29.md`

**Step 1: Запустить полный аудит**

Run: `python3 scripts/audit_semantic_structure.py`

Expected: ~53 категории проанализированы

**Step 2: Проверить отчёт**

Run: `head -50 reports/SEMANTIC_AUDIT_2026-01-29.md`

**Step 3: Commit отчёт**

```bash
git add reports/SEMANTIC_AUDIT_2026-01-29.md
git commit -m "docs: add semantic audit report"
```

---

## Task 4: Подготовить промпты для воркеров

**Files:**
- Create: `data/generated/worker-prompts/semantic-audit-W1.md`
- Create: `data/generated/worker-prompts/semantic-audit-W2.md`
- ...

**Step 1: Создать директорию**

Run: `mkdir -p data/generated/worker-prompts`

**Step 2: Распределить категории по воркерам**

Читать отчёт, выбрать Critical категории, распределить по 5-7 на воркер.

**Step 3: Создать промпт для каждого воркера**

Формат:
```markdown
# Worker N: Semantic Cluster

Твоя задача: исправить структуру keywords/synonyms для следующих категорий.

## Категории

1. {slug-1} — {path}
2. {slug-2} — {path}
...

## Workflow для каждой категории

1. Read `categories/{path}/data/{slug}_clean.json`
2. Применить логику из `/semantic-cluster`:
   - Уникальные интенты → keywords[]
   - Словоформы → synonyms[] с variant_of
   - Коммерческие → meta_only
3. Update JSON
4. Update `_meta.json` → keywords_in_content
5. Log в `data/generated/audit-logs/W{N}_semantic.md`

## НЕ делать

- НЕ коммитить
- НЕ трогать контент (_ru.md)
- НЕ менять файлы других категорий
```

**Step 4: Commit промпты**

```bash
git add data/generated/worker-prompts/
git commit -m "docs: add worker prompts for semantic audit"
```

---

## Task 5: Запустить параллельных воркеров

**Step 1: Запустить воркеров через spawn-claude**

```bash
spawn-claude "W1: Semantic Cluster

$(cat data/generated/worker-prompts/semantic-audit-W1.md)

Выполни задачу для всех категорий из списка.
НЕ ДЕЛАЙ git commit" "$(pwd)"
```

Повторить для W2, W3, ... WN.

**Step 2: Мониторить прогресс**

Run: `tmux list-windows` — проверить статус окон

**Step 3: Проверить логи воркеров**

Run: `ls data/generated/audit-logs/`

---

## Task 6: Merge результатов

**Step 1: Проверить изменения**

Run: `git status`

Expected: Много изменённых _clean.json и _meta.json файлов

**Step 2: Re-run аудита**

Run: `python3 scripts/audit_semantic_structure.py -o reports/SEMANTIC_AUDIT_AFTER.md`

Expected: Critical = 0

**Step 3: Сравнить отчёты**

Run: `diff reports/SEMANTIC_AUDIT_2026-01-29.md reports/SEMANTIC_AUDIT_AFTER.md | head -30`

**Step 4: Commit всех изменений**

```bash
git add categories/
git add reports/SEMANTIC_AUDIT_AFTER.md
git commit -m "fix: restructure keywords/synonyms in all categories"
```

---

## Task 7: Создать отчёт для обновления контента

**Files:**
- Create: `reports/CONTENT_UPDATE_NEEDED.md`

**Step 1: Скрипт для проверки покрытия keywords в контенте**

Добавить в audit скрипт проверку: каждый keyword из keywords[] есть в _ru.md?

**Step 2: Сгенерировать список**

```markdown
# Content Update Needed

Категории где keywords не покрыты в контенте:

| Категория | Отсутствующие keywords |
|-----------|------------------------|
| aktivnaya-pena | шампунь для бесконтактной мойки, пена для минимойки |
| ... | ... |
```

**Step 3: Commit**

```bash
git add reports/CONTENT_UPDATE_NEEDED.md
git commit -m "docs: list categories needing content update"
```

---

## Acceptance Criteria

- [ ] Скрипт `audit_semantic_structure.py` работает
- [ ] Отчёт аудита сгенерирован
- [ ] Все Critical исправлены (keywords[] полные)
- [ ] variant_of проставлен для словоформ
- [ ] keywords_in_content обновлён
- [ ] Отчёт для обновления контента готов

---

**Estimated Tasks:** 7
**Estimated Time:** 2-3 часа (с воркерами)
