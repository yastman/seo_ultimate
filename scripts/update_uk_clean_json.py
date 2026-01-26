#!/usr/bin/env python3
"""
Обновляет uk/categories/{slug}/data/{slug}_clean.json
на основе uk/data/uk_keywords.json
"""

import json
from pathlib import Path


def load_uk_keywords():
    with open("uk/data/uk_keywords.json", "r", encoding="utf-8") as f:
        return json.load(f)


def group_keywords(keywords: list) -> dict:
    """Группирует ключи по volume: primary >500, secondary 100-500, supporting <100"""
    primary = [k for k in keywords if k["volume"] >= 500]
    secondary = [k for k in keywords if 100 <= k["volume"] < 500]
    supporting = [k for k in keywords if k["volume"] < 100]
    return {"primary": primary, "secondary": secondary, "supporting": supporting}


def update_clean_json(slug: str, keywords: list, total_volume: int):
    """Создает/обновляет _clean.json для категории"""
    uk_cat_dir = Path(f"uk/categories/{slug}")
    data_dir = uk_cat_dir / "data"
    data_dir.mkdir(parents=True, exist_ok=True)

    clean_path = data_dir / f"{slug}_clean.json"

    grouped = group_keywords(keywords)

    # Формируем структуру
    clean_data = {
        "id": slug,
        "language": "uk",
        "total_volume": total_volume,
        "keywords": grouped["primary"],
        "secondary_keywords": grouped["secondary"],
        "supporting_keywords": grouped["supporting"],
        "all_keywords_count": len(keywords),
    }

    with open(clean_path, "w", encoding="utf-8") as f:
        json.dump(clean_data, f, ensure_ascii=False, indent=2)

    return clean_path


def main():
    data = load_uk_keywords()

    updated = 0
    for slug, cat_data in data["categories"].items():
        keywords = cat_data["keywords"]
        total_volume = cat_data["total_volume"]

        update_clean_json(slug, keywords, total_volume)
        print(f"✅ {slug}: {len(keywords)} keywords, volume {total_volume}")
        updated += 1

    print(f"\n✅ Обновлено: {updated} категорий")


if __name__ == "__main__":
    main()
