#!/usr/bin/env python3
"""
Apply manual plural mapping to _meta.json files.
Usage: python3 scripts/apply_manual_plural.py --lang uk --dry-run
       python3 scripts/apply_manual_plural.py --lang uk --apply
"""

import argparse
import json
from pathlib import Path


def load_mapping(lang: str) -> dict:
    mapping_file = Path(f"data/generated/plural_manual_{lang}.json")
    if not mapping_file.exists():
        return {}
    with open(mapping_file) as f:
        return json.load(f)


def update_title(old_title: str, old_h1: str, new_h1: str) -> str:
    """Update title: replace old H1 with new H1."""
    if old_h1 in old_title:
        return old_title.replace(old_h1, new_h1)
    # Case-insensitive replacement
    idx = old_title.lower().find(old_h1.lower())
    if idx >= 0:
        return old_title[:idx] + new_h1 + old_title[idx + len(old_h1) :]
    # Fallback: replace beginning before dash
    if " — " in old_title:
        return new_h1 + " — " + old_title.split(" — ", 1)[1]
    return old_title


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--lang", choices=["ru", "uk"], required=True)
    parser.add_argument("--dry-run", action="store_true")
    parser.add_argument("--apply", action="store_true")
    args = parser.parse_args()

    if not args.dry_run and not args.apply:
        print("Error: specify --dry-run or --apply")
        return

    mapping = load_mapping(args.lang)
    if not mapping:
        print(f"No mapping found for {args.lang}")
        return

    base_dir = Path("uk/categories") if args.lang == "uk" else Path("categories")
    changes = []
    not_found = []

    for slug, new_h1 in mapping.items():
        meta_file = base_dir / slug / "meta" / f"{slug}_meta.json"

        if not meta_file.exists():
            not_found.append(slug)
            continue

        with open(meta_file) as f:
            meta = json.load(f)

        old_h1 = meta.get("h1", "")
        old_title = meta.get("meta", {}).get("title", "")
        new_title = update_title(old_title, old_h1, new_h1)

        changes.append(
            {
                "slug": slug,
                "old_h1": old_h1,
                "new_h1": new_h1,
                "old_title": old_title,
                "new_title": new_title,
                "file": str(meta_file),
            }
        )

        if args.apply:
            meta["h1"] = new_h1
            meta["meta"]["title"] = new_title
            with open(meta_file, "w") as f:
                json.dump(meta, f, ensure_ascii=False, indent=2)
                f.write("\n")

    # Report
    mode = "DRY RUN" if args.dry_run else "APPLIED"
    print(f"\n{'=' * 60}")
    print(f"{mode}: {len(changes)} changes for {args.lang.upper()}")
    print(f"{'=' * 60}\n")

    for c in changes:
        print(f"{c['slug']}:")
        print(f"  H1: {c['old_h1']}")
        print(f"   →  {c['new_h1']}")
        print()

    if not_found:
        print(f"\nNot found ({len(not_found)}): {', '.join(not_found)}")


if __name__ == "__main__":
    main()
