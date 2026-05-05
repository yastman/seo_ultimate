#!/usr/bin/env python3
"""
check_semantic_coverage.py — Semantic coverage check.

Compares keywords in source files vs _clean.json files.

Usage:
    uv run python -m llm_keywords_pipeline.audit.semantic --lang ru
    uv run python -m llm_keywords_pipeline.audit.semantic --lang uk
"""

from __future__ import annotations

import argparse
import json
import re
from pathlib import Path

from llm_keywords_pipeline.core.config import CATEGORIES_DIR, PROJECT_ROOT


def scan_json_keywords(base_path: Path) -> dict[str, str]:
    """
    Builds a map: Keyword -> Slug based on current JSON files.
    """
    kw_map: dict[str, str] = {}

    for clean_file in base_path.rglob("*_clean.json"):
        try:
            with open(clean_file, encoding="utf-8") as f:
                data = json.load(f)

            slug = data.get("id") or data.get("slug")
            if not slug:
                continue

            keywords: list[str] = []
            # V2 format
            if isinstance(data.get("keywords"), list):
                keywords = [k["keyword"] for k in data["keywords"] if isinstance(k, dict)]
            # Legacy format
            elif isinstance(data.get("keywords"), dict):
                for group in data["keywords"].values():
                    for k in group:
                        if isinstance(k, dict):
                            keywords.append(k["keyword"])

            for kw in keywords:
                kw_norm = kw.strip().lower()
                kw_map[kw_norm] = slug

        except Exception:
            pass

    return kw_map


def parse_structure_md_keywords(structure_path: Path) -> dict[str, list[str]]:
    """
    Parses STRUCTURE.md to capture (Cluster Name -> [Keywords]).
    """
    if not structure_path.exists():
        return {}

    cluster_kws: dict[str, list[str]] = {}
    current_cluster = "Unknown"

    table_row_re = re.compile(r"^\|\s*(.+?)\s*\|\s*(\d+)\s*\|")

    with open(structure_path, encoding="utf-8") as f:
        for line in f:
            line = line.strip()

            if line.startswith("#"):
                clean_header = line.lstrip("#").strip()
                if (
                    "Cluster:" in clean_header
                    or "L3:" in clean_header
                    or "Filter:" in clean_header
                    or "Direct Keywords" in clean_header
                ):
                    current_cluster = re.sub(r"\(Vol:.*?\)", "", clean_header).strip()
                    if current_cluster not in cluster_kws:
                        cluster_kws[current_cluster] = []
                continue

            if line.startswith("|"):
                if "---" in line:
                    continue
                if "Keyword" in line and "Volume" in line:
                    continue

                match = table_row_re.match(line)
                if match:
                    kw = match.group(1).strip().lower()
                    if current_cluster:
                        if current_cluster not in cluster_kws:
                            cluster_kws[current_cluster] = []
                        cluster_kws[current_cluster].append(kw)

    return cluster_kws


def analyze_ru_coverage() -> str:
    """Analyze RU coverage: STRUCTURE.md vs _clean.json files."""
    structure_path = PROJECT_ROOT / "data" / "generated" / "STRUCTURE.md"
    json_map = scan_json_keywords(CATEGORIES_DIR)
    structure_clusters = parse_structure_md_keywords(structure_path)

    report = []
    report.append("# Сверка Семантики: STRUCTURE.md vs JSONs")
    report.append("")

    total_structure_kws = 0
    missing_kws = []

    for cluster in sorted(structure_clusters.keys()):
        kws = structure_clusters[cluster]
        if not kws:
            continue

        cluster_missing = []
        for kw in kws:
            total_structure_kws += 1
            if kw not in json_map:
                cluster_missing.append(kw)

        if cluster_missing:
            report.append(f"### ❌ Cluster: {cluster}")
            report.append(f"Потеряно ключей: {len(cluster_missing)} / {len(kws)}")
            for m in cluster_missing:
                report.append(f"- {m}")
            report.append("")
            missing_kws.extend(cluster_missing)

    report.append("## Итог")
    report.append(f"- Всего ключей в `STRUCTURE.md`: **{total_structure_kws}**")
    report.append(f"- Найдено в JSON-файлах: **{len(json_map)}**")
    report.append(f"- Потеряно/Не распределено: **{len(missing_kws)}**")

    if len(missing_kws) == 0 and total_structure_kws > 0:
        report.append("\n✅ **ALL CLEAR:** Все ключи из STRUCTURE.md находятся в JSON-файлах.")
    elif total_structure_kws == 0:
        report.append("\n⚠️ **ERROR:** Не удалось прочитать ключи из STRUCTURE.md")
    else:
        report.append("\n⚠️ **ATTENTION:** Есть потерянные ключи.")

    return "\n".join(report)


def load_uk_keywords() -> dict[str, str]:
    """Load keywords from uk_keywords.json."""
    uk_keywords_path = PROJECT_ROOT / "uk" / "data" / "uk_keywords.json"
    if not uk_keywords_path.exists():
        return {}

    with open(uk_keywords_path, encoding="utf-8") as f:
        data = json.load(f)

    kw_map: dict[str, str] = {}
    for slug, cat_data in data.get("categories", {}).items():
        for kw_item in cat_data.get("keywords", []):
            kw_map[kw_item["keyword"].strip().lower()] = slug
    return kw_map


def scan_uk_json_keywords() -> dict[str, str]:
    """Scan uk/categories/ for keywords in _clean.json files."""
    uk_categories_dir = PROJECT_ROOT / "uk" / "categories"
    kw_map: dict[str, str] = {}

    for clean_file in uk_categories_dir.rglob("*_clean.json"):
        try:
            with open(clean_file, encoding="utf-8") as f:
                data = json.load(f)

            slug = data.get("id") or data.get("slug")
            if not slug:
                continue

            keywords: list[str] = []
            if isinstance(data.get("keywords"), list):
                keywords.extend([k["keyword"] for k in data["keywords"] if isinstance(k, dict)])
            if isinstance(data.get("secondary_keywords"), list):
                keywords.extend(
                    [k["keyword"] for k in data["secondary_keywords"] if isinstance(k, dict)]
                )
            if isinstance(data.get("supporting_keywords"), list):
                keywords.extend(
                    [k["keyword"] for k in data["supporting_keywords"] if isinstance(k, dict)]
                )

            for kw in keywords:
                kw_map[kw.strip().lower()] = slug

        except Exception:
            pass

    return kw_map


def analyze_uk_coverage() -> str:
    """Analyze UK coverage: uk_keywords.json vs _clean.json files."""
    source_kws = load_uk_keywords()
    json_kws = scan_uk_json_keywords()

    report = []
    report.append("# UK Semantic Coverage: uk_keywords.json vs _clean.json")
    report.append("")

    missing_in_json = []
    for kw, slug in source_kws.items():
        if kw not in json_kws:
            missing_in_json.append((kw, slug))

    if missing_in_json:
        report.append("## ❌ Keywords in uk_keywords.json but NOT in _clean.json files:")
        for kw, slug in sorted(missing_in_json, key=lambda x: x[1]):
            report.append(f"- `{kw}` (should be in {slug})")
        report.append("")

    report.append("## Итог")
    report.append(f"- Всего в uk_keywords.json: **{len(source_kws)}**")
    report.append(f"- Найдено в _clean.json: **{len(json_kws)}**")
    report.append(f"- Потеряно: **{len(missing_in_json)}**")

    if len(missing_in_json) == 0:
        report.append("\n✅ **ALL CLEAR:** Все UK ключи распределены.")
    else:
        report.append("\n⚠️ **ATTENTION:** Есть нераспределённые UK ключи.")

    return "\n".join(report)


def main():
    parser = argparse.ArgumentParser(description="Check semantic coverage")
    parser.add_argument(
        "--lang", choices=["ru", "uk"], default="ru", help="Language: ru (default) or uk"
    )
    args = parser.parse_args()

    if args.lang == "uk":
        report = analyze_uk_coverage()
        output_path = PROJECT_ROOT / "reports" / "SEMANTIC_COVERAGE_CHECK_UK.md"
    else:
        report = analyze_ru_coverage()
        output_path = PROJECT_ROOT / "reports" / "SEMANTIC_COVERAGE_CHECK.md"

    output_path.parent.mkdir(exist_ok=True)
    output_path.write_text(report, encoding="utf-8")

    print(report)
    print(f"\nReport saved to: {output_path}")


if __name__ == "__main__":
    main()
