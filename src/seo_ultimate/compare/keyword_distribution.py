#!/usr/bin/env python3
"""
Показывает таблицу распределения ключей по ролям для категории.

Поддерживает обе структуры:
- OLD: `keywords_detailed`
- NEW: `keywords.primary/secondary/supporting`
"""

from __future__ import annotations

import argparse
import json
from collections import Counter
from pathlib import Path
from typing import Any

ROLE_PLACEMENT = {
    "primary": "Title, H1",
    "secondary": "H2, Description",
    "supporting": "Текст, FAQ",
    "long_tail": "Фильтры, Карточки товаров",
}


def _parse_density_percent(value: Any) -> float:
    if value is None:
        return 0.0
    if isinstance(value, (int, float)):
        return float(value)
    text = str(value).strip()
    if text.endswith("%"):
        text = text[:-1].strip()
    try:
        return float(text)
    except ValueError:
        return 0.0


def load_keywords(data: dict) -> tuple[str, list[dict]]:
    """
    Returns:
        (structure_label, keywords)
        keywords: list[{"keyword","volume","relative_freq","role"}]
    """
    if "keywords_detailed" in data:
        keywords_raw = data["keywords_detailed"]
        keywords = [
            {
                "keyword": kw.get("phrase", ""),
                "volume": kw.get("volume", 0),
                "relative_freq": kw.get("relative_freq", 0.0),
                "role": kw.get("role", "unknown"),
            }
            for kw in keywords_raw
            if isinstance(kw, dict)
        ]
        return ("OLD structure (keywords_detailed)", keywords)

    if "keywords" in data and isinstance(data["keywords"], dict):
        keywords_dict = data["keywords"]
        keywords: list[dict] = []
        for role in ["primary", "secondary", "supporting"]:
            for kw_obj in keywords_dict.get(role, []):
                if not isinstance(kw_obj, dict):
                    continue
                keywords.append(
                    {
                        "keyword": kw_obj.get("keyword", ""),
                        "volume": kw_obj.get("occurrences_target", 0),
                        "relative_freq": _parse_density_percent(kw_obj.get("density_target", "0%")),
                        "role": role,
                    }
                )
        return ("NEW structure (keywords.primary/secondary/supporting)", keywords)

    raise ValueError("Unknown JSON structure. Expected 'keywords_detailed' or 'keywords' field.")


def format_table(category_name: str, tier: str, keywords: list[dict]) -> str:
    lines = []
    lines.append(f"\n📊 Таблица распределения ключей: {category_name} (Tier {tier})")
    lines.append("=" * 120)
    lines.append(
        f"{'Ключевое слово':<45} {'Freq':>6} {'Rel.Freq':>9} {'Role':<12} {'Куда вставлять':<30}"
    )
    lines.append("-" * 120)

    for kw in keywords:
        phrase = kw.get("keyword") or kw.get("phrase", "")
        volume = int(kw.get("volume", 0) or 0)
        rel_freq = float(kw.get("relative_freq", 0.0) or 0.0)
        role = kw.get("role", "unknown")
        placement = ROLE_PLACEMENT.get(role, "—")
        lines.append(f"{phrase:<45} {volume:>6} {rel_freq:>9.2f} {role:<12} {placement:<30}")

    lines.append("=" * 120)
    return "\n".join(lines) + "\n"


def format_stats(data: dict, keywords: list[dict]) -> str:
    if not keywords:
        return "⚠️  No keywords found in JSON\n"

    role_counts = Counter(kw["role"] for kw in keywords if kw.get("role"))
    total = len(keywords)
    lines = ["📈 Статистика по ролям:"]
    for role in ["primary", "secondary", "supporting", "long_tail"]:
        count = role_counts.get(role, 0)
        pct = (count / total * 100) if total else 0.0
        label = role.capitalize() if role != "long_tail" else "Long-tail"
        lines.append(f"   {label:<11} {count:>3} ({pct:.0f}%)")
    lines.append(f"\n   Всего ключей: {total}")

    if "max_volume" in data:
        lines.append(f"   Max volume: {data['max_volume']}")

    if "competitor_metadata" in data and isinstance(data["competitor_metadata"], dict):
        lines.append(
            f"\n🔗 Primary SERP URLs: {data['competitor_metadata'].get('primary_serp_count', 0)}"
        )

    return "\n".join(lines) + "\n"


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description="Show keyword distribution for a category JSON file"
    )
    parser.add_argument("category_json", help="Path to category JSON")
    return parser


def main(argv: list[str] | None = None) -> int:
    parser = build_parser()
    args = parser.parse_args(argv)

    json_file = Path(args.category_json)
    if not json_file.exists():
        print(f"❌ File not found: {json_file}")
        return 1

    data = json.loads(json_file.read_text(encoding="utf-8"))

    try:
        structure_label, keywords = load_keywords(data)
    except ValueError as e:
        print(f"❌ {e}")
        return 1

    print(f"ℹ️  Detected {structure_label}")

    category_name = data.get("category_name_ru") or data.get("category") or "Unknown"
    tier = data.get("tier", "N/A")

    print(format_table(category_name, tier, keywords), end="")
    print(format_stats(data, keywords), end="")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
