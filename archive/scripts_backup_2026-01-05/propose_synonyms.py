import json
import os
import re
from collections import defaultdict
from datetime import date

# Configuration
CATEGORIES_DIR = r"c:\Users\user\Documents\Сайты\Ultimate.net.ua\сео_для_категорий_ультимейт\categories"

# Synonyms for normalization
AUTO_SYNONYMS = ["авто", "автомобиля", "машины", "машина", "автомобиль", "в авто", "для авто"]
STOP_WORDS = ["для", "в", "на"]


def normalize_keyword(keyword):
    """
    Creates a canonical form of the keyword for comparison.
    """
    text = keyword.lower()
    for syn in AUTO_SYNONYMS:
        text = text.replace(syn, "")
    for sw in STOP_WORDS:
        text = re.sub(rf"\b{sw}\b", "", text)
    words = [w for w in re.split(r"\s+", text) if w.strip()]
    normalized_words = []
    for w in words:
        if w.startswith("полиров") or w.startswith("полирал"):
            normalized_words.append("полир")
        elif w.startswith("очистит"):
            normalized_words.append("очист")
        else:
            normalized_words.append(w)
    normalized_words.sort()
    return " ".join(normalized_words)


def process_category(category_path):
    slug = os.path.basename(category_path)
    clean_json_path = os.path.join(category_path, "data", f"{slug}_clean.json")
    proposed_json_path = os.path.join(category_path, "data", f"{slug}_proposed.json")

    if not os.path.exists(clean_json_path):
        return

    try:
        with open(clean_json_path, encoding="utf-8") as f:
            data = json.load(f)
    except Exception as e:
        print(f"Error reading {clean_json_path}: {e}")
        return

    # Prepare new data structure
    new_data = data.copy()
    new_data["clustered_at"] = str(date.today())
    new_data["clustering_notes"] = data.get("clustering_notes", {})
    if "proposed_changes" not in new_data["clustering_notes"]:
        new_data["clustering_notes"]["proposed_changes"] = []

    # Flatten keywords
    keywords_flat = []
    sections = ["primary", "secondary", "supporting", "commercial"]
    for section in sections:
        if section in data.get("keywords", {}):
            for k in data["keywords"][section]:
                k["original_section"] = section
                keywords_flat.append(k)

    # Group by normalized key
    clusters = defaultdict(list)
    for k in keywords_flat:
        norm = normalize_keyword(k["keyword"])
        if not norm:
            norm = k["keyword"].lower()
        clusters[norm].append(k)

    # Rebuild keyword lists
    kept_keywords = defaultdict(list)
    changes_log = []

    for _norm, group in clusters.items():
        # Select winner
        group.sort(key=lambda x: (-x.get("volume", 0), len(x["keyword"])))
        winner = group[0]
        losers = group[1:]

        # Add winner to its original section (or logic to move it?)
        # For now, keep it in its original section to avoid massive reshuffles
        kept_keywords[winner["original_section"]].append(winner)

        if losers:
            change_msg = f"Kept '{winner['keyword']}' ({winner['volume']}). Dropped: " + ", ".join(
                [f"'{loser['keyword']}' ({loser['volume']})" for loser in losers]
            )
            changes_log.append(change_msg)

    # Sort keywords within sections by volume desc
    for sec in kept_keywords:
        kept_keywords[sec].sort(key=lambda x: -x.get("volume", 0))

    # Update new_data
    new_data["keywords"] = kept_keywords
    new_data["clustering_notes"]["proposed_changes"] = changes_log

    # Recalculate stats
    total_volume = sum(k["volume"] for sec in kept_keywords for k in kept_keywords[sec])
    total_count = sum(len(kept_keywords[sec]) for sec in kept_keywords)
    new_data["stats"] = {
        "before": data.get("stats", {}).get(
            "before", 0
        ),  # Preserve original before count if possible, or use current total
        "after": total_count,
        "total_volume": total_volume,
    }

    # Write proposed file
    with open(proposed_json_path, "w", encoding="utf-8") as f:
        json.dump(new_data, f, ensure_ascii=False, indent=2)

    print(f"Generated {proposed_json_path} (Removed {len(keywords_flat) - total_count} duplicates)")


def main():
    cats = sorted(os.listdir(CATEGORIES_DIR))
    for cat in cats:
        cat_path = os.path.join(CATEGORIES_DIR, cat)
        if os.path.isdir(cat_path):
            process_category(cat_path)


if __name__ == "__main__":
    main()
