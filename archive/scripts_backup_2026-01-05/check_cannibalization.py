import glob
import json
import os
from collections import defaultdict


def load_keywords(base_path: str) -> dict[str, dict[str, list[tuple[str, int]]]]:
    # category -> { type -> [(keyword, volume)] }
    # actually better: keyword -> list of (category, type, volume)

    keyword_map = defaultdict(list)

    # glob pattern to find _clean.json files
    # We need to find categories. Structure is base_path/category_name/data/category_name_clean.json

    category_dirs = [d for d in os.listdir(base_path) if os.path.isdir(os.path.join(base_path, d))]

    for cat in category_dirs:
        # Construct path to clean json
        json_path = os.path.join(base_path, cat, "data", f"{cat}_clean.json")
        if not os.path.exists(json_path):
            # Try finding any _clean.json if naming isn't consistent
            # But based on exploration it seems consistent.
            # Let's try to glob if specific file fails
            pattern = os.path.join(base_path, cat, "data", "*_clean.json")
            files = glob.glob(pattern)
            if files:
                json_path = files[0]
            else:
                continue

        try:
            with open(json_path, encoding="utf-8") as f:
                data = json.load(f)

            if "keywords" not in data:
                continue

            for k_type, k_list in data["keywords"].items():
                if isinstance(k_list, list):
                    for item in k_list:
                        kw = item.get("keyword", "").strip().lower()
                        vol = item.get("volume", 0)
                        if kw:
                            keyword_map[kw].append({"category": cat, "type": k_type, "volume": vol})

        except Exception as e:
            print(f"Error loading {json_path}: {e}")

    return keyword_map


def find_intersections(keyword_map: dict[str, list[dict]]) -> tuple[list[dict], list[dict]]:
    full_duplicates = []

    # Check for exact duplicates
    for kw, occurrences in keyword_map.items():
        if len(occurrences) > 1:
            # Check if they are from different categories
            categories = {occ["category"] for occ in occurrences}
            if len(categories) > 1:
                # Group by category
                cat_map = defaultdict(list)
                for occ in occurrences:
                    cat_map[occ["category"]].append(f"{occ['type']} ({occ['volume']})")

                full_duplicates.append({"keyword": kw, "details": dict(cat_map)})

    return full_duplicates


def find_partial_intersections(keyword_map: dict[str, list[dict]]) -> list[dict]:
    # This is more expensive (O(N^2) or similar). verify performance if N is large.
    # We want to find cases where KW_A is a substring of KW_B, and they are in different categories.

    keys = sorted(keyword_map.keys(), key=len)  # sort by length
    partials = []

    # Optimization: Only check relevant collisions?
    # Simple nested loop might be fine for < 10k keywords.
    # Total keywords estimated: 100 cats * ~20 words = 2000 words. fast enough.

    processed_pairs = set()

    for i in range(len(keys)):
        short_kw = keys[i]
        short_cats = {x["category"] for x in keyword_map[short_kw]}

        for j in range(i + 1, len(keys)):
            long_kw = keys[j]

            # optimization: if short_kw not in long_kw, continue
            if short_kw not in long_kw:
                continue

            # Found containment
            long_cats = {x["category"] for x in keyword_map[long_kw]}

            # Intersection of categories is NOT what we want (that would be exact dup inside same cat, or just same cat).
            # We want cases where short_kw is in Cat A, long_kw is in Cat B.

            # If they share a category, it might be fine (hierarchical within detailed page).
            # But the user flagged "voski" (short) vs "kvik-deteylery" (long: cold wax).

            # diff_cats and common_cats were unused

            # If they are completely disjoint categories
            disjoint_cats_short = short_cats - long_cats
            disjoint_cats_long = long_cats - short_cats

            if disjoint_cats_short and disjoint_cats_long:
                # There is a cross-category containment
                for c1 in disjoint_cats_short:
                    for c2 in disjoint_cats_long:
                        pair_key = tuple(sorted((c1, c2)))
                        if pair_key in processed_pairs:
                            # We already logged this CATEGORY pair? No, we need to log specific keywords?
                            # The user wants "Problems found".
                            # Actually let's aggregate by category pair.
                            pass

                        partials.append(
                            {
                                "short_kw": short_kw,
                                "cat_1": c1,
                                "vol_1": max(
                                    [
                                        x["volume"]
                                        for x in keyword_map[short_kw]
                                        if x["category"] == c1
                                    ]
                                ),
                                "long_kw": long_kw,
                                "cat_2": c2,
                                "vol_2": max(
                                    [
                                        x["volume"]
                                        for x in keyword_map[long_kw]
                                        if x["category"] == c2
                                    ]
                                ),
                            }
                        )

    return partials


def generate_report(ru_path, ua_path):
    report_lines = []

    for lang, path in [("RU", ru_path), ("UA", ua_path)]:
        report_lines.append(f"# Analysis for {lang}")

        kw_map = load_keywords(path)
        full_dups = find_intersections(kw_map)

        if full_dups:
            report_lines.append("\n## ❌ CRITICAL PROBLEM: Full Duplicates\n")

            # Group by category pair
            pair_map = defaultdict(list)
            for dup in full_dups:
                cats = list(dup["details"].keys())
                # pair all combinations
                import itertools

                for c1, c2 in itertools.combinations(cats, 2):
                    pair = tuple(sorted((c1, c2)))
                    pair_map[pair].append(dup)

            for (c1, c2), dups in pair_map.items():
                report_lines.append(f"\n### {c1} ↔ {c2}\n")
                report_lines.append(f"| Key | {c1} | {c2} |")
                report_lines.append("|---|---|---|")
                for d in dups:
                    info1 = d["details"].get(c1, ["-"])[0]
                    info2 = d["details"].get(c2, ["-"])[0]
                    report_lines.append(f'| *"{d["keyword"]}"* | {info1} | {info2} |')

        else:
            report_lines.append("\n✅ No Full Duplicates Found.\n")

        # Partial
        partials = find_partial_intersections(kw_map)
        if partials:
            report_lines.append("\n## ⚠️ PARTIAL INTERSECTIONS\n")

            # Group by category pair
            pair_map_p = defaultdict(list)
            for p in partials:
                pair = tuple(sorted((p["cat_1"], p["cat_2"])))
                pair_map_p[pair].append(p)

            # Set a threshold to avoid spam?
            # Show top pairs with most overlaps

            sorted_pairs = sorted(pair_map_p.items(), key=lambda x: len(x[1]), reverse=True)

            for (c1, c2), issues in sorted_pairs:
                if len(issues) < 1:
                    continue  # filter noise?

                report_lines.append(f"\n### {c1} ↔ {c2}\n")
                report_lines.append(f"| {c1} | {c2} |")
                report_lines.append("|---|---|")

                # Limit to 10 examples per pair to avoid huge report
                for shown, issue in enumerate(issues):
                    if shown >= 10:
                        report_lines.append(f"| ... (+{len(issues) - 10} more) | ... |")
                        break

                    if issue["cat_1"] == c1:
                        left = f'"{issue["short_kw"]}" ({issue["vol_1"]})'
                        right = f'"{issue["long_kw"]}" ({issue["vol_2"]})'
                    else:
                        left = f'"{issue["long_kw"]}" ({issue["vol_2"]})'
                        right = f'"{issue["short_kw"]}" ({issue["vol_1"]})'

                    report_lines.append(f"| {left} | {right} |")

        else:
            report_lines.append("\n✅ No Partial Intersections (Substring matches) Found.\n")

        report_lines.append("\n---\n")

    return "\n".join(report_lines)


if __name__ == "__main__":
    ru_path = (
        r"c:\Users\user\Documents\Сайты\Ultimate.net.ua\сео_для_категорий_ультимейт\categories"
    )
    ua_path = (
        r"c:\Users\user\Documents\Сайты\Ultimate.net.ua\сео_для_категорий_ультимейт\uk\categories"
    )

    report = generate_report(ru_path, ua_path)
    print(report)

    with open("cannibalization_report.md", "w", encoding="utf-8") as f:
        f.write(report)
