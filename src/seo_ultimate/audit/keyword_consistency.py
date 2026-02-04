#!/usr/bin/env python3
"""
audit_keyword_consistency.py — Audit Keywords Consistency

Scans all _clean.json files to verify keyword distribution across categories.

Usage:
    uv run python -m seo_ultimate.audit.keyword_consistency
"""

from __future__ import annotations

import json

from seo_ultimate.core.config import CATEGORIES_DIR, PROJECT_ROOT


def scan_actual_keywords() -> dict[str, set[str]]:
    """Scans all _clean.json files to build a map of Slug -> Keywords."""
    slug_keywords: dict[str, set[str]] = {}

    for clean_file in CATEGORIES_DIR.rglob("*_clean.json"):
        try:
            with open(clean_file, encoding="utf-8") as f:
                data = json.load(f)

            slug = data.get("id") or data.get("slug")
            if not slug:
                continue

            keywords: list[str] = []
            # Handle V2: {"keywords": [{"keyword": "...", "volume": N}, ...]}
            if isinstance(data.get("keywords"), list):
                keywords = [k["keyword"] for k in data["keywords"] if isinstance(k, dict)]
            # Handle Legacy: {"keywords": {"primary": [...], ...}}
            elif isinstance(data.get("keywords"), dict):
                for group in data["keywords"].values():
                    for k in group:
                        if isinstance(k, dict):
                            keywords.append(k["keyword"])

            slug_keywords[slug] = set(keywords)
        except Exception as e:
            print(f"Error reading {clean_file}: {e}")

    return slug_keywords


def generate_report() -> str:
    """Generate keyword consistency report."""
    actual_data = scan_actual_keywords()

    report_lines = []
    report_lines.append("# Аудит Ключевых Слов (Fact vs Expectation)")
    report_lines.append("")
    report_lines.append("## 1. Категории без ключей (Empty Semantics)")

    empty_slugs = [slug for slug, kws in actual_data.items() if not kws]
    if empty_slugs:
        for slug in sorted(empty_slugs):
            report_lines.append(f"- [ ] warning: **{slug}** is empty.")
    else:
        report_lines.append("Все категории имеют хотя бы один ключ.")

    report_lines.append("")
    report_lines.append("## 2. Статистика по категориям")
    report_lines.append("| Category (Slug) | Keywords Count |")
    report_lines.append("| --- | --- |")

    total_kws = 0
    for slug in sorted(actual_data.keys()):
        count = len(actual_data[slug])
        total_kws += count
        report_lines.append(f"| {slug} | {count} |")

    report_lines.append("")
    report_lines.append(f"**Total Keywords Found:** {total_kws}")

    return "\n".join(report_lines)


def main():
    """Main function."""
    report = generate_report()

    # Write to reports directory
    reports_dir = PROJECT_ROOT / "reports"
    reports_dir.mkdir(exist_ok=True)
    output_path = reports_dir / "KEYWORD_CONSISTENCY.md"

    output_path.write_text(report, encoding="utf-8")
    print(f"Report generated at {output_path}")

    # Also print summary
    actual_data = scan_actual_keywords()
    total_cats = len(actual_data)
    empty_cats = sum(1 for kws in actual_data.values() if not kws)
    total_kws = sum(len(kws) for kws in actual_data.values())

    print("\nSummary:")
    print(f"  Total categories: {total_cats}")
    print(f"  Empty categories: {empty_cats}")
    print(f"  Total keywords: {total_kws}")


if __name__ == "__main__":
    main()
