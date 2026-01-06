import glob
import json
import os

# Configuration
SEARCH_DIR = "categories"
RULES = [
    {"pattern": "автохимия", "target": "glavnaya", "exclude_slugs": ["glavnaya"]},
    {"pattern": "детейлинг", "target": "glavnaya", "exclude_slugs": ["glavnaya"]},
    {"pattern": "автошампунь", "target": "avtoshampuni", "exclude_slugs": ["avtoshampuni"]},
    {
        "pattern": "шампунь",
        "target": "avtoshampuni",
        "exclude_slugs": ["avtoshampuni", "kislotnyy-shampun", "s-voskom", "dlya-ruchnoy-moyki"],
    },
    {
        "pattern": "мойка авто",
        "target": "moyka-i-eksteryer",
        "exclude_slugs": [
            "moyka-i-eksteryer",
            "aktivnaya-pena",
            "dlya-ruchnoy-moyki",
            "nabory-dlya-moyki",
        ],
    },
    {
        "pattern": "полировка",
        "target": "polirovka",
        "exclude_slugs": [
            "polirovka",
            "polirovalnye-pasty",
            "polirovalnye-krugi",
            "polirovalnye-mashinki",
        ],
    },
    {
        "pattern": "для кожи",
        "target": "ukhod-za-kozhey",
        "exclude_slugs": ["ukhod-za-kozhey", "sredstva-dlya-kozhi", "chistka-kozhi"],
    },
]


def check_file(filepath):
    try:
        with open(filepath, encoding="utf-8") as f:
            data = json.load(f)
    except Exception as e:
        print(f"Error reading {filepath}: {e}")
        return []

    slug = data.get("slug", "")
    issues = []

    sections = ["primary", "secondary", "supporting", "commercial"]
    keywords_data = data.get("keywords", {})

    for section in sections:
        kws = keywords_data.get(section, [])
        for kw_obj in kws:
            keyword = kw_obj.get("keyword", "").lower()

            for rule in RULES:
                if rule["pattern"] in keyword:
                    # Check exclusions
                    if slug in rule["exclude_slugs"]:
                        continue

                    # Specific check for "shampun" in active foam if it implies "contactless"
                    # User rule: "avtoshampun" in active foam -> avtoshampuni
                    # But active foam IS contactless shampoo.
                    # Let's flag it strictly as requested, but maybe add a note.

                    issues.append(
                        {
                            "from_category": slug,
                            "keyword": keyword,
                            "volume": kw_obj.get("volume", 0),
                            "to_category": rule["target"],
                            "reason": f"Contains '{rule['pattern']}' -> {rule['target']}",
                            "filepath": filepath,
                            "section": section,
                        }
                    )
                    break  # Only match one rule per keyword

    return issues


def main():
    root_dir = os.path.join(os.getcwd(), SEARCH_DIR)
    pattern = os.path.join(root_dir, "*", "data", "*_clean.json")
    files = glob.glob(pattern)

    all_issues = []
    for f in files:
        all_issues.extend(check_file(f))

    # Print Report
    print(f"| {'Из категории':<20} | {'Ключ':<40} | {'Volume':<6} | {'В категорию':<20} | {'Причина':<30} |")
    print(f"|{'-' * 21}|{'-' * 42}|{'-' * 8}|{'-' * 22}|{'-' * 32}|")

    for issue in all_issues:
        print(
            f"| {issue['from_category']:<20} | {issue['keyword']:<40} | {issue['volume']:<6} | {issue['to_category']:<20} | {issue['reason']:<30} |"
        )


if __name__ == "__main__":
    main()
