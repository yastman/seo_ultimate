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

        results.append(
            {
                "path": meta_file,
                "slug": slug,
                "parent_path": parent_path,
            }
        )

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
            "suggestion": f"Добавить уточнение, целевая длина {TITLE_MIN}-{TITLE_MAX}",
        }
    elif length > TITLE_MAX:
        return {
            "rule": "title_length",
            "severity": WARNING,
            "message": f"Title слишком длинный ({length} > {TITLE_MAX})",
            "current": title_clean,
            "suggestion": f"Сократить до {TITLE_MAX} символов",
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
            "suggestion": "Заменить ':' на '—' или 'для'",
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
            "current": desc[:80] + "..." if len(desc) > 80 else desc,
            "suggestion": f"Добавить типы товаров/объёмы, целевая длина {DESC_MIN}-{DESC_MAX}",
        }
    elif length > DESC_MAX:
        return {
            "rule": "desc_length",
            "severity": WARNING,
            "message": f"Description слишком длинный ({length} > {DESC_MAX})",
            "current": desc[:80] + "..." if len(desc) > 80 else desc,
            "suggestion": f"Сократить до {DESC_MAX} символов",
        }
    return None


def main():
    meta_files = find_all_meta_files()
    print(f"Found {len(meta_files)} meta files")

    # Test loading
    for mf in meta_files[:3]:
        meta = load_meta(mf)
        print(f"\n{mf['slug']}:")

        # Test technical checks
        for check_fn in [check_title_length, check_title_no_colon, check_desc_length]:
            result = check_fn(meta)
            if result:
                print(f"  {result['severity']}: {result['rule']} - {result['message']}")
            else:
                print(f"  OK: {check_fn.__name__}")


if __name__ == "__main__":
    main()
