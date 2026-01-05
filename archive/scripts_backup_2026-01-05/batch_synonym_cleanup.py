import glob
import json
import os
import re
from collections import defaultdict

# Base directory
BASE_DIR = r"c:/Users/user/Documents/Сайты/Ultimate.net.ua/сео_для_категорий_ультимейт/categories"

# Replacements for normalization (Fingerprinting)
# (Regex pattern, Replacement)
NORMALIZATION_RULES = [
    (r"\bавтомобил[а-я]*\b", "авто"),
    (r"\bмашин[а-я]*\b", "авто"),
    (r"\bполировальн[а-я]*\b", "полир"),
    (r"\bполировочн[а-я]*\b", "полир"),
    (r"\bполировк[а-я]*\b", "полир"),
    (r"\bкузов[а-я]*\s+авто\b", "кузов"),
    (r"\bкузов[а-я]*\b", "кузов"),
    (r"\bдля\b", " "),
    (r"\bна\b", " "),
    (r"\s+", " "),
]

STOP_WORDS = {"для", "на", "в", "под", "с", "от"}


def normalize_keyword(keyword):
    """Creates a fingerprint for the keyword to identify synonyms."""
    text = keyword.lower()

    # 1. Apply regex substitutions
    for pattern, repl in NORMALIZATION_RULES:
        text = re.sub(pattern, repl, text)

    # 2. Tokenize and remove stop words
    tokens = text.split()
    tokens = [t for t in tokens if t not in STOP_WORDS]

    # 3. Sort tokens to handle word order
    tokens.sort()

    return " ".join(tokens)


def is_commercial(keyword):
    """Checks if keyword has commercial intent."""
    comm_words = ["купить", "цена", "ціна", "купити", "стоимость", "заказать"]
    return any(w in keyword.lower() for w in comm_words)


def process_category(file_path):
    with open(file_path, encoding="utf-8") as f:
        data = json.load(f)

    keywords = data.get("keywords", {})
    primary = keywords.get("primary", [])
    secondary = keywords.get("secondary", [])
    supporting = keywords.get("supporting", [])
    commercial = keywords.get("commercial", [])

    # 1. Collect all informational keywords
    # We treat primary, secondary, supporting as a single pool for deduplication checks,
    # but we want to preserve their section assignment preference.
    # Actually, the prompt says "Review JSON... Merge synonyms".
    # Strategy: Group all info keywords. Pick winner. Assign winner to the highest priority section it appeared in.

    all_info_items = []

    # Helper to add items with section priority
    # Priority: 0=primary, 1=secondary, 2=supporting

    def add_items(items, section_name, priority):
        for item in items:
            kw = item.get("keyword", "")
            if not kw:
                continue

            # Check commercial intent
            if is_commercial(kw):
                # Move to commercial if not already there?
                # The prompt says commercial is ONLY meta.
                # We'll collect them to add to commercial list later.
                commercial.append(item)
                continue

            # Add to info list
            all_info_items.append(
                {
                    "data": item,
                    "section": section_name,
                    "priority": priority,
                    "fingerprint": normalize_keyword(kw),
                }
            )

    add_items(primary, "primary", 0)
    add_items(secondary, "secondary", 1)
    add_items(supporting, "supporting", 2)

    # Group by fingerprint
    groups = defaultdict(list)
    for entry in all_info_items:
        groups[entry["fingerprint"]].append(entry)

    # Process groups and pick winners
    final_primary = []
    final_secondary = []
    final_supporting = []

    merged_log = []

    for _fingerprint, group in groups.items():
        if not group:
            continue

        # Select winner
        # Rules:
        # 1. Max volume
        # 2. Shorter length
        # 3. Prefer 'авто' over others (implicitly handled by shorter length usually, but let's be safe)

        def sort_key(entry):
            item = entry["data"]
            vol = item.get("volume", 0)
            length = len(item.get("keyword", ""))
            return (-vol, length)  # Descending volume, Ascending length

        group.sort(key=sort_key)
        winner_entry = group[0]
        winner_kw = winner_entry["data"]["keyword"]

        # Determine target section (highest priority in the group)
        min_prio = min(e["priority"] for e in group)
        target_section = (
            "primary" if min_prio == 0 else "secondary" if min_prio == 1 else "supporting"
        )

        # Add to target list
        # We construct a new item to be safe, or use the winner's data
        final_item = winner_entry["data"]

        if target_section == "primary":
            final_primary.append(final_item)
        elif target_section == "secondary":
            final_secondary.append(final_item)
        else:
            final_supporting.append(final_item)

        # Log merges if there were losers
        losers = [e["data"]["keyword"] for e in group if e["data"]["keyword"] != winner_kw]
        if losers:
            # unique losers
            losers = sorted(set(losers))
            merged_log.append(f"{'/'.join(losers)} -> {winner_kw}")

    # Process Commercial (Deduplicate only)
    # Commercial keywords shouldn't be merged with info, but should be deduped among themselves
    # e.g. "купить автошампунь" (100) vs "автошампунь купить" (100) -> merge

    comm_groups = defaultdict(list)
    for item in commercial:
        kw = item.get("keyword", "")
        fp = normalize_keyword(kw)
        comm_groups[fp].append(item)

    final_commercial = []
    for _fp, group in comm_groups.items():
        # Pick best commercial variant (same logic: max vol, min len)
        group.sort(key=lambda x: (-x.get("volume", 0), len(x.get("keyword", ""))))
        winner = group[0]
        final_commercial.append(winner)
        # We don't log commercial merges aggressively usually, but let's stick to the prompt's focus on info merges.

    # Update Data
    data["keywords"]["primary"] = final_primary
    data["keywords"]["secondary"] = final_secondary
    data["keywords"]["supporting"] = final_supporting
    data["keywords"]["commercial"] = final_commercial

    # Update clustering notes
    if "clustering_notes" not in data:
        data["clustering_notes"] = {}

    data["clustering_notes"]["cleaned_at"] = "2026-01-01"

    # Add new merges to existing ones or replace?
    # Prompt implies adding. "После очистки добавить..."
    # Let's append if exists.
    existing_merges = data["clustering_notes"].get("merged", [])
    if isinstance(existing_merges, list):
        existing_merges.extend(merged_log)
    else:
        existing_merges = merged_log

    # Deduplicate logs
    data["clustering_notes"]["merged"] = sorted(set(existing_merges))

    # Update Stats
    data["stats"]["after"] = (
        len(final_primary) + len(final_secondary) + len(final_supporting) + len(final_commercial)
    )
    # Recalculate total volume? Might be nice but not strictly requested.

    # Save file
    with open(file_path, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=2, ensure_ascii=False)

    return len(merged_log)


def main():
    # Find all _clean.json files
    pattern = os.path.join(BASE_DIR, "**", "*_clean.json")
    files = glob.glob(pattern, recursive=True)

    print(f"Found {len(files)} files to process.")

    total_merges = 0
    processed_count = 0

    for file_path in files:
        try:
            merges = process_category(file_path)
            if merges > 0:
                print(f"Propessed {os.path.basename(file_path)}: {merges} merges.")
            total_merges += merges
            processed_count += 1
        except Exception as e:
            print(f"Error processing {file_path}: {e}")

    print(f"Done. Processed {processed_count} files. Total inconsistencies fixed: {total_merges}")


if __name__ == "__main__":
    main()
