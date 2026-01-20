# Meta Audit Implementation Plan

> **For Claude:** REQUIRED SUB-SKILL: Use superpowers:executing-plans to implement this plan task-by-task.

**Goal:** Создать скрипт `audit_meta.py` для комплексного аудита мета-тегов всех категорий с генерацией JSON и Markdown отчётов.

**Architecture:** Расширяем существующий `validate_meta.py` новым скриптом `audit_meta.py`. Скрипт собирает все `*_meta.json`, применяет 9 правил валидации (техническая + SEO-качество + полнота), генерирует отчёты в `reports/`.

**Tech Stack:** Python 3, stdlib only (json, pathlib, re, datetime)

---

## Task 1: Создать базовую структуру скрипта

**Files:**
- Create: `scripts/audit_meta.py`

**Step 1: Создать файл с импортами и константами**

```python
#!/usr/bin/env python3
"""
audit_meta.py — Comprehensive Meta Tags Audit (v1.0)

Комплексный аудит мета-тегов категорий:
- Техническая валидация (длина, обязательные поля)
- SEO-качество (front-loading, формулы)
- Полнота данных (keywords, types, forms, volumes)

Usage:
    python scripts/audit_meta.py                    # Full audit
    python scripts/audit_meta.py --json             # JSON only
    python scripts/audit_meta.py --slug aktivnaya-pena  # Single category
    python scripts/audit_meta.py --min-severity warning  # Skip INFO
"""

import json
import re
from datetime import datetime
from pathlib import Path
from typing import Any

# Severity levels
CRITICAL = "CRITICAL"
WARNING = "WARNING"
INFO = "INFO"

# Length limits (from CONTENT_GUIDE.md)
TITLE_MIN = 50
TITLE_MAX = 60
DESC_MIN = 120
DESC_MAX = 160
```

**Step 2: Проверить синтаксис**

Run: `python -m py_compile scripts/audit_meta.py`
Expected: No output (success)

**Step 3: Commit**

```bash
git add scripts/audit_meta.py
git commit -m "feat(audit): create audit_meta.py skeleton"
```

---

## Task 2: Реализовать MetaLoader

**Files:**
- Modify: `scripts/audit_meta.py`

**Step 1: Добавить функцию загрузки всех meta файлов**

```python
def find_all_meta_files(base_path: Path = Path(".")) -> list[dict[str, Any]]:
    """
    Find all *_meta.json files in categories/.

    Returns list of dicts with:
    - path: Path to meta file
    - slug: Category slug
    - parent_path: Path to category folder
    """
    results = []

    for meta_file in base_path.glob("categories/**/meta/*_meta.json"):
        slug = meta_file.stem.replace("_meta", "")
        parent_path = meta_file.parent.parent

        results.append({
            "path": meta_file,
            "slug": slug,
            "parent_path": parent_path,
        })

    return sorted(results, key=lambda x: x["slug"])


def load_meta(meta_info: dict[str, Any]) -> dict[str, Any] | None:
    """Load and parse meta JSON file."""
    try:
        with open(meta_info["path"], encoding="utf-8") as f:
            data = json.load(f)
            data["_file_path"] = str(meta_info["path"])
            data["_slug"] = meta_info["slug"]
            return data
    except Exception as e:
        return {"_error": str(e), "_file_path": str(meta_info["path"])}
```

**Step 2: Добавить тестовый вывод в main**

```python
def main():
    meta_files = find_all_meta_files()
    print(f"Found {len(meta_files)} meta files")
    for mf in meta_files[:3]:
        print(f"  - {mf['slug']}: {mf['path']}")


if __name__ == "__main__":
    main()
```

**Step 3: Запустить и проверить**

Run: `python scripts/audit_meta.py`
Expected: `Found 49 meta files` (примерно) и список первых 3

**Step 4: Commit**

```bash
git add scripts/audit_meta.py
git commit -m "feat(audit): add MetaLoader - find and load meta files"
```

---

## Task 3: Реализовать технические проверки

**Files:**
- Modify: `scripts/audit_meta.py`

**Step 1: Добавить функции технических проверок**

```python
def check_title_length(meta: dict) -> dict | None:
    """Check title length is 50-60 chars."""
    title = meta.get("meta", {}).get("title", "")
    # Remove brand suffix for length check
    title_clean = title.split("|")[0].strip() if "|" in title else title
    length = len(title_clean)

    if length < TITLE_MIN:
        return {
            "rule": "title_length",
            "severity": WARNING,
            "message": f"Title слишком короткий ({length} < {TITLE_MIN})",
            "current": title_clean,
            "suggestion": f"Добавить уточнение, целевая длина {TITLE_MIN}-{TITLE_MAX}"
        }
    elif length > TITLE_MAX:
        return {
            "rule": "title_length",
            "severity": WARNING,
            "message": f"Title слишком длинный ({length} > {TITLE_MAX})",
            "current": title_clean,
            "suggestion": f"Сократить до {TITLE_MAX} символов"
        }
    return None


def check_title_no_colon(meta: dict) -> dict | None:
    """Check title has no colon (Google replaces with dash)."""
    title = meta.get("meta", {}).get("title", "")
    if ": " in title:
        return {
            "rule": "title_colon",
            "severity": CRITICAL,
            "message": "Title содержит двоеточие (Google заменяет на дефис в 41%)",
            "current": title,
            "suggestion": "Заменить ':' на '—' или 'для'"
        }
    return None


def check_desc_length(meta: dict) -> dict | None:
    """Check description length is 120-160 chars."""
    desc = meta.get("meta", {}).get("description", "")
    length = len(desc)

    if length < DESC_MIN:
        return {
            "rule": "desc_length",
            "severity": WARNING,
            "message": f"Description слишком короткий ({length} < {DESC_MIN})",
            "current": desc[:80] + "...",
            "suggestion": f"Добавить типы товаров/объёмы, целевая длина {DESC_MIN}-{DESC_MAX}"
        }
    elif length > DESC_MAX:
        return {
            "rule": "desc_length",
            "severity": WARNING,
            "message": f"Description слишком длинный ({length} > {DESC_MAX})",
            "current": desc[:80] + "...",
            "suggestion": f"Сократить до {DESC_MAX} символов"
        }
    return None
```

**Step 2: Проверить синтаксис**

Run: `python -m py_compile scripts/audit_meta.py`
Expected: No output (success)

**Step 3: Commit**

```bash
git add scripts/audit_meta.py
git commit -m "feat(audit): add technical checks (title/desc length, colon)"
```

---

## Task 4: Реализовать SEO-проверки

**Files:**
- Modify: `scripts/audit_meta.py`

**Step 1: Добавить проверку front-loading**

```python
def check_title_front_loading(meta: dict) -> dict | None:
    """Check that primary keyword is at the beginning of title."""
    title = meta.get("meta", {}).get("title", "").lower()
    keywords = meta.get("keywords_in_content", {}).get("primary", [])

    if not keywords:
        return None  # No keywords to check

    primary_kw = keywords[0].lower()

    # Check if title starts with primary keyword (or close variant)
    # Allow some flexibility: "Пена для мойки" matches "пена для мойки авто"
    primary_words = primary_kw.split()[:3]  # First 3 words
    title_start = " ".join(title.split()[:3])

    # Check if first words match
    if not any(word in title_start for word in primary_words[:2]):
        return {
            "rule": "title_front_loading",
            "severity": CRITICAL,
            "message": f"ВЧ '{primary_kw}' не в начале title",
            "current": title[:50] + "...",
            "suggestion": f"Переместить '{primary_kw}' в начало title"
        }
    return None


def check_title_kupiti_position(meta: dict) -> dict | None:
    """Check that 'купить/купити' is not the first word."""
    title = meta.get("meta", {}).get("title", "").lower()
    first_word = title.split()[0] if title else ""

    if first_word in ["купить", "купити", "купуйте"]:
        return {
            "rule": "title_kupiti_first",
            "severity": CRITICAL,
            "message": "'Купить' первым словом — неправильный порядок",
            "current": title[:50] + "...",
            "suggestion": "Формула: {ВЧ Ключ} — купить | Ultimate"
        }
    return None


def check_h1_no_kupiti(meta: dict) -> dict | None:
    """Check that H1 doesn't contain 'купить'."""
    h1 = meta.get("h1", "").lower()

    if "купить" in h1 or "купити" in h1:
        return {
            "rule": "h1_kupiti",
            "severity": CRITICAL,
            "message": "H1 содержит 'купить' — должен быть чистым",
            "current": h1,
            "suggestion": "H1 = название категории без коммерческих слов"
        }
    return None
```

**Step 2: Добавить проверки description**

```python
def check_desc_producer(meta: dict) -> dict | None:
    """Check description contains 'от производителя' or equivalent."""
    desc = meta.get("meta", {}).get("description", "").lower()

    patterns = [
        "от производителя",
        "від виробника",
        "производителя ultimate",
        "виробника ultimate",
        "в интернет-магазине ultimate",
        "в інтернет-магазині ultimate"
    ]

    if not any(p in desc for p in patterns):
        return {
            "rule": "desc_producer",
            "severity": WARNING,
            "message": "Description не содержит 'от производителя Ultimate'",
            "current": desc[:80] + "...",
            "suggestion": "Добавить 'от производителя Ultimate' или 'в интернет-магазине Ultimate'"
        }
    return None


def check_desc_wholesale(meta: dict) -> dict | None:
    """Check description contains wholesale indicator."""
    desc = meta.get("meta", {}).get("description", "").lower()

    # Skip if shop pattern (not producer)
    if "в интернет-магазине" in desc or "в інтернет-магазині" in desc:
        return None

    patterns = ["опт", "розница", "роздріб", "оптом"]

    if not any(p in desc for p in patterns):
        return {
            "rule": "desc_wholesale",
            "severity": WARNING,
            "message": "Description не содержит 'Опт и розница'",
            "current": desc[:80] + "...",
            "suggestion": "Добавить 'Опт и розница.' в конец"
        }
    return None
```

**Step 3: Commit**

```bash
git add scripts/audit_meta.py
git commit -m "feat(audit): add SEO checks (front-loading, kupiti, producer, wholesale)"
```

---

## Task 5: Реализовать проверки полноты данных

**Files:**
- Modify: `scripts/audit_meta.py`

**Step 1: Добавить проверки полноты**

```python
def check_keywords_primary(meta: dict) -> dict | None:
    """Check that keywords_in_content.primary exists and not empty."""
    kic = meta.get("keywords_in_content", {})
    primary = kic.get("primary", [])

    if not primary:
        return {
            "rule": "keywords_primary",
            "severity": INFO,
            "message": "Отсутствует keywords_in_content.primary",
            "current": "[]",
            "suggestion": "Добавить primary keywords из семантики"
        }
    return None


def check_slug_consistency(meta: dict) -> dict | None:
    """Check that slug in JSON matches folder name."""
    json_slug = meta.get("slug", "")
    file_slug = meta.get("_slug", "")

    if json_slug and file_slug and json_slug != file_slug:
        return {
            "rule": "slug_mismatch",
            "severity": CRITICAL,
            "message": f"slug в JSON '{json_slug}' не совпадает с папкой '{file_slug}'",
            "current": json_slug,
            "suggestion": f"Исправить slug на '{file_slug}'"
        }
    return None
```

**Step 2: Commit**

```bash
git add scripts/audit_meta.py
git commit -m "feat(audit): add completeness checks (keywords, slug)"
```

---

## Task 6: Собрать все проверки в audit функцию

**Files:**
- Modify: `scripts/audit_meta.py`

**Step 1: Создать главную функцию аудита**

```python
ALL_CHECKS = [
    check_title_length,
    check_title_no_colon,
    check_title_front_loading,
    check_title_kupiti_position,
    check_h1_no_kupiti,
    check_desc_length,
    check_desc_producer,
    check_desc_wholesale,
    check_keywords_primary,
    check_slug_consistency,
]


def audit_meta(meta: dict) -> list[dict]:
    """Run all checks on a single meta file."""
    issues = []

    for check_fn in ALL_CHECKS:
        result = check_fn(meta)
        if result:
            issues.append(result)

    return issues


def audit_all(meta_files: list[dict], min_severity: str = INFO) -> dict:
    """
    Run audit on all meta files.

    Returns:
        {
            "summary": {...},
            "by_severity": {"CRITICAL": [...], "WARNING": [...], "INFO": [...]},
            "by_category": {"slug": {...}, ...}
        }
    """
    severity_order = {CRITICAL: 0, WARNING: 1, INFO: 2}
    min_level = severity_order.get(min_severity, 2)

    results = {
        "summary": {
            "total_categories": len(meta_files),
            "passed": 0,
            "with_critical": 0,
            "with_warning": 0,
            "with_info": 0,
            "timestamp": datetime.now().isoformat(),
        },
        "by_severity": {CRITICAL: [], WARNING: [], INFO: []},
        "by_category": {},
    }

    for meta_info in meta_files:
        meta = load_meta(meta_info)
        if not meta or "_error" in meta:
            continue

        issues = audit_meta(meta)

        # Filter by severity
        issues = [i for i in issues if severity_order.get(i["severity"], 2) <= min_level]

        slug = meta.get("_slug", "unknown")
        file_path = meta.get("_file_path", "")

        if not issues:
            results["summary"]["passed"] += 1
            continue

        # Group by severity
        cat_result = {
            "slug": slug,
            "path": file_path,
            "issues": issues,
        }

        results["by_category"][slug] = cat_result

        has_critical = any(i["severity"] == CRITICAL for i in issues)
        has_warning = any(i["severity"] == WARNING for i in issues)
        has_info = any(i["severity"] == INFO for i in issues)

        if has_critical:
            results["summary"]["with_critical"] += 1
            results["by_severity"][CRITICAL].append(cat_result)
        elif has_warning:
            results["summary"]["with_warning"] += 1
            results["by_severity"][WARNING].append(cat_result)
        elif has_info:
            results["summary"]["with_info"] += 1
            results["by_severity"][INFO].append(cat_result)

    return results
```

**Step 2: Commit**

```bash
git add scripts/audit_meta.py
git commit -m "feat(audit): add audit_meta and audit_all functions"
```

---

## Task 7: Реализовать генерацию отчётов

**Files:**
- Modify: `scripts/audit_meta.py`
- Create: `reports/` directory

**Step 1: Добавить генерацию JSON отчёта**

```python
def generate_json_report(results: dict, output_path: Path) -> None:
    """Save audit results as JSON."""
    output_path.parent.mkdir(parents=True, exist_ok=True)
    with open(output_path, "w", encoding="utf-8") as f:
        json.dump(results, f, ensure_ascii=False, indent=2)
    print(f"JSON report saved: {output_path}")
```

**Step 2: Добавить генерацию Markdown отчёта**

```python
def generate_markdown_report(results: dict, output_path: Path) -> None:
    """Generate human-readable Markdown report."""
    output_path.parent.mkdir(parents=True, exist_ok=True)

    s = results["summary"]
    lines = [
        f"# Meta Tags Audit Report — {datetime.now().strftime('%Y-%m-%d')}",
        "",
        "## Сводка",
        "",
        f"- **Всего категорий:** {s['total_categories']}",
        f"- ✅ **Passed:** {s['passed']}",
        f"- 🔴 **Critical:** {s['with_critical']}",
        f"- ⚠️ **Warning:** {s['with_warning']}",
        f"- ℹ️ **Info:** {s['with_info']}",
        "",
    ]

    # Critical issues
    if results["by_severity"][CRITICAL]:
        lines.append("## 🔴 Critical Issues")
        lines.append("")
        for cat in results["by_severity"][CRITICAL]:
            lines.append(f"### {cat['slug']}")
            lines.append(f"**File:** `{cat['path']}`")
            lines.append("")
            for issue in cat["issues"]:
                if issue["severity"] == CRITICAL:
                    lines.append(f"- **{issue['rule']}:** {issue['message']}")
                    lines.append(f"  - Сейчас: `{issue.get('current', 'N/A')}`")
                    lines.append(f"  - Рекомендация: {issue.get('suggestion', 'N/A')}")
            lines.append("")

    # Warnings
    if results["by_severity"][WARNING]:
        lines.append("## ⚠️ Warnings")
        lines.append("")
        for cat in results["by_severity"][WARNING]:
            lines.append(f"### {cat['slug']}")
            for issue in cat["issues"]:
                if issue["severity"] == WARNING:
                    lines.append(f"- **{issue['rule']}:** {issue['message']}")
            lines.append("")

    # Info
    if results["by_severity"][INFO]:
        lines.append("## ℹ️ Info")
        lines.append("")
        for cat in results["by_severity"][INFO]:
            lines.append(f"- **{cat['slug']}:** " + ", ".join(i["rule"] for i in cat["issues"] if i["severity"] == INFO))
        lines.append("")

    with open(output_path, "w", encoding="utf-8") as f:
        f.write("\n".join(lines))

    print(f"Markdown report saved: {output_path}")
```

**Step 3: Commit**

```bash
git add scripts/audit_meta.py
git commit -m "feat(audit): add JSON and Markdown report generators"
```

---

## Task 8: Реализовать CLI интерфейс

**Files:**
- Modify: `scripts/audit_meta.py`

**Step 1: Обновить main() с argparse**

```python
import argparse


def main():
    parser = argparse.ArgumentParser(description="Meta Tags Audit")
    parser.add_argument("--json", action="store_true", help="Output JSON only to stdout")
    parser.add_argument("--slug", type=str, help="Audit single category by slug")
    parser.add_argument("--min-severity", type=str, default="info",
                       choices=["critical", "warning", "info"],
                       help="Minimum severity level (default: info)")
    args = parser.parse_args()

    min_severity = args.min_severity.upper()

    # Find meta files
    meta_files = find_all_meta_files()

    if args.slug:
        meta_files = [m for m in meta_files if m["slug"] == args.slug]
        if not meta_files:
            print(f"Category '{args.slug}' not found")
            return 1

    print(f"Auditing {len(meta_files)} categories...")

    # Run audit
    results = audit_all(meta_files, min_severity)

    if args.json:
        print(json.dumps(results, ensure_ascii=False, indent=2))
        return 0

    # Generate reports
    date_str = datetime.now().strftime("%Y-%m-%d")
    reports_dir = Path("reports")

    generate_json_report(results, reports_dir / f"meta-audit-{date_str}.json")
    generate_markdown_report(results, reports_dir / f"meta-audit-{date_str}.md")

    # Print summary
    s = results["summary"]
    print()
    print("=" * 50)
    print("AUDIT COMPLETE")
    print("=" * 50)
    print(f"✅ Passed: {s['passed']}/{s['total_categories']}")
    print(f"🔴 Critical: {s['with_critical']}")
    print(f"⚠️  Warning: {s['with_warning']}")
    print(f"ℹ️  Info: {s['with_info']}")

    return 1 if s["with_critical"] > 0 else 0


if __name__ == "__main__":
    exit(main())
```

**Step 2: Запустить полный аудит**

Run: `python scripts/audit_meta.py`
Expected: Генерация отчётов в `reports/`

**Step 3: Commit**

```bash
git add scripts/audit_meta.py reports/
git commit -m "feat(audit): add CLI interface and run first audit"
```

---

## Task 9: Финальная проверка и документация

**Files:**
- Modify: `scripts/audit_meta.py` (docstring)

**Step 1: Запустить аудит и проверить отчёты**

Run: `python scripts/audit_meta.py`
Run: `cat reports/meta-audit-2026-01-20.md | head -50`

**Step 2: Проверить JSON вывод**

Run: `python scripts/audit_meta.py --json | head -30`

**Step 3: Проверить фильтрацию по severity**

Run: `python scripts/audit_meta.py --min-severity critical`

**Step 4: Финальный коммит**

```bash
git add -A
git commit -m "feat(audit): complete meta audit implementation v1.0"
```

---

## Summary

| Task | Описание | Файлы |
|------|----------|-------|
| 1 | Базовая структура | `scripts/audit_meta.py` |
| 2 | MetaLoader | `scripts/audit_meta.py` |
| 3 | Технические проверки | `scripts/audit_meta.py` |
| 4 | SEO-проверки | `scripts/audit_meta.py` |
| 5 | Проверки полноты | `scripts/audit_meta.py` |
| 6 | Audit функции | `scripts/audit_meta.py` |
| 7 | Генерация отчётов | `scripts/audit_meta.py`, `reports/` |
| 8 | CLI интерфейс | `scripts/audit_meta.py` |
| 9 | Финальная проверка | - |

**Estimated commits:** 9
