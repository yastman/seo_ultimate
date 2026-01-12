#!/usr/bin/env python3
"""Сбор всех основных ключевых слов из категорий."""

import json
from pathlib import Path

ROOT = Path(__file__).parent.parent
CATEGORIES_DIR = ROOT / "categories"
OUTPUT_FILE = ROOT / "data" / "generated" / "ALL_KEYWORDS.txt"


def collect_keywords() -> list:
    """Собирает keywords из всех _clean.json файлов."""
    unique = {}

    for clean_file in sorted(CATEGORIES_DIR.rglob("*_clean.json")):
        try:
            data = json.loads(clean_file.read_text(encoding="utf-8"))
            for kw in data.get("keywords", []):
                key = kw["keyword"]
                vol = kw.get("volume", 0)
                if key not in unique or vol > unique[key]["volume"]:
                    unique[key] = {"keyword": key, "volume": vol}
        except Exception as e:
            print(f"⚠️  {clean_file.name}: {e}")

    return sorted(unique.values(), key=lambda x: x["volume"], reverse=True)


def main():
    keywords = collect_keywords()
    just_keywords = [k["keyword"] for k in keywords]

    OUTPUT_FILE.parent.mkdir(parents=True, exist_ok=True)
    OUTPUT_FILE.write_text("\n".join(just_keywords), encoding="utf-8")

    print(f"✅ {len(just_keywords)} ключей → {OUTPUT_FILE}")


if __name__ == "__main__":
    main()
