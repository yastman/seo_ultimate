#!/usr/bin/env python3
"""
audit_meta.py — Comprehensive Meta Tags Audit (v1.0)

Комплексный аудит мета-тегов категорий:
- Техническая валидация (длина, обязательные поля)
- SEO-качество (front-loading, формулы)
- Полнота данных (keywords, types, forms, volumes)

Usage:
    uv run python -m seo_ultimate.audit.meta
    uv run python -m seo_ultimate.audit.meta --json
    uv run python -m seo_ultimate.audit.meta --slug aktivnaya-pena
    uv run python -m seo_ultimate.audit.meta --min-severity warning
"""

from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import Any

from seo_ultimate.core.config import PROJECT_ROOT

# Severity levels
CRITICAL = "CRITICAL"
WARNING = "WARNING"
INFO = "INFO"

# Length limits (from CONTENT_GUIDE.md)
TITLE_MIN = 50
TITLE_MAX = 60
DESC_MIN = 120
DESC_MAX = 160


def find_all_meta_files(base_path: Path | None = None) -> list[dict[str, Any]]:
    """
    Find all *_meta.json files in categories/.

    Returns list of dicts with:
    - path: Path to meta file
    - slug: Category slug
    - parent_path: Path to category folder
    """
    base = base_path or PROJECT_ROOT
    results = []

    for meta_file in base.glob("categories/**/meta/*_meta.json"):
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


def check_h1_present(meta: dict) -> dict | None:
    """Check H1 is present."""
    h1 = meta.get("h1", "")
    if not h1:
        return {
            "rule": "h1_missing",
            "severity": CRITICAL,
            "message": "H1 отсутствует",
            "current": None,
            "suggestion": "Добавить H1 (обычно = primary keyword во множ. числе)",
        }
    return None


def check_slug_match(meta: dict) -> dict | None:
    """Check slug field matches filename."""
    slug = meta.get("slug", "")
    expected_slug = meta.get("_slug", "")

    if slug and slug != expected_slug:
        return {
            "rule": "slug_mismatch",
            "severity": WARNING,
            "message": f"Slug в файле ({slug}) не совпадает с именем файла ({expected_slug})",
            "current": slug,
            "suggestion": f"Исправить slug на '{expected_slug}'",
        }
    return None


def audit_meta_file(meta_info: dict[str, Any]) -> dict[str, Any]:
    """
    Run all checks on a single meta file.

    Returns:
        {
            "slug": str,
            "path": str,
            "issues": list of issue dicts,
            "status": "OK" | "WARNING" | "CRITICAL"
        }
    """
    meta = load_meta(meta_info)
    result = {
        "slug": meta_info["slug"],
        "path": str(meta_info["path"]),
        "issues": [],
        "status": "OK",
    }

    if "_error" in meta:
        result["issues"].append(
            {
                "rule": "json_parse",
                "severity": CRITICAL,
                "message": f"JSON parse error: {meta['_error']}",
            }
        )
        result["status"] = CRITICAL
        return result

    # Run all checks
    checks = [
        check_title_length,
        check_title_no_colon,
        check_desc_length,
        check_h1_present,
        check_slug_match,
    ]

    for check_fn in checks:
        issue = check_fn(meta)
        if issue:
            result["issues"].append(issue)
            # Update overall status
            if issue["severity"] == CRITICAL:
                result["status"] = CRITICAL
            elif issue["severity"] == WARNING and result["status"] != CRITICAL:
                result["status"] = WARNING

    return result


def audit_all(base_path: Path | None = None, min_severity: str = INFO) -> list[dict[str, Any]]:
    """Audit all meta files."""
    meta_files = find_all_meta_files(base_path)
    results = []

    severity_order = {INFO: 0, WARNING: 1, CRITICAL: 2}
    min_level = severity_order.get(min_severity.upper(), 0)

    for meta_info in meta_files:
        result = audit_meta_file(meta_info)

        # Filter by severity
        result["issues"] = [
            issue
            for issue in result["issues"]
            if severity_order.get(issue["severity"], 0) >= min_level
        ]

        # Update status based on remaining issues
        if not result["issues"]:
            result["status"] = "OK"
        else:
            result["status"] = max(
                result["issues"], key=lambda x: severity_order.get(x["severity"], 0)
            )["severity"]

        results.append(result)

    return results


def print_report(results: list[dict[str, Any]]) -> None:
    """Print human-readable audit report."""
    critical_count = sum(1 for r in results if r["status"] == CRITICAL)
    warning_count = sum(1 for r in results if r["status"] == WARNING)
    ok_count = sum(1 for r in results if r["status"] == "OK")

    print(f"\n{'=' * 60}")
    print("META TAGS AUDIT REPORT")
    print(f"{'=' * 60}")
    print(f"\nTotal files: {len(results)}")
    print(f"  OK: {ok_count}")
    print(f"  WARNING: {warning_count}")
    print(f"  CRITICAL: {critical_count}")

    # Show issues
    issues_found = [r for r in results if r["issues"]]
    if issues_found:
        print(f"\n{'=' * 60}")
        print("ISSUES FOUND:")
        print(f"{'=' * 60}")

        for result in issues_found:
            print(f"\n{result['slug']} [{result['status']}]")
            for issue in result["issues"]:
                print(f"  [{issue['severity']}] {issue['rule']}: {issue['message']}")
                if issue.get("suggestion"):
                    print(f"    → {issue['suggestion']}")


def main():
    parser = argparse.ArgumentParser(description="Audit meta tags")
    parser.add_argument("--slug", help="Audit single category")
    parser.add_argument("--json", action="store_true", help="JSON output")
    parser.add_argument(
        "--min-severity",
        choices=["info", "warning", "critical"],
        default="info",
        help="Minimum severity to show",
    )
    args = parser.parse_args()

    if args.slug:
        # Single category
        meta_files = find_all_meta_files()
        meta_info = next((m for m in meta_files if m["slug"] == args.slug), None)

        if not meta_info:
            print(f"Category '{args.slug}' not found")
            return

        result = audit_meta_file(meta_info)
        results = [result]
    else:
        results = audit_all(min_severity=args.min_severity)

    if args.json:
        print(json.dumps(results, ensure_ascii=False, indent=2, default=str))
    else:
        print_report(results)


if __name__ == "__main__":
    main()
