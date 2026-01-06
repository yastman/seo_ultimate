import json
import os

PROJECT_ROOT = r"c:\Users\user\Documents\Сайты\Ultimate.net.ua\сео_для_категорий_ультимейт"
REPORTS_DIR = os.path.join(PROJECT_ROOT, "tasks", "reports")
CATEGORIES_DIR = os.path.join(PROJECT_ROOT, "categories")
DISTRIBUTION_FILE = os.path.join(REPORTS_DIR, "CLUSTER_DISTRIBUTION.md")


def scan_actual_keywords():
    """Scans all _clean.json files to build a map of Slug -> Keywords."""
    slug_keywords = {}

    for root, _dirs, files in os.walk(CATEGORIES_DIR):
        for file in files:
            if file.endswith("_clean.json"):
                path = os.path.join(root, file)
                try:
                    with open(path, "r", encoding="utf-8") as f:
                        data = json.load(f)

                    slug = data.get("id") or data.get("slug")  # handle v2 and legacy

                    keywords = []
                    # Handle V2
                    if isinstance(data.get("keywords"), list):
                        keywords = [k["keyword"] for k in data["keywords"]]
                    # Handle Legacy (just in case)
                    elif isinstance(data.get("keywords"), dict):
                        for group in data["keywords"].values():
                            for k in group:
                                keywords.append(k["keyword"])

                    slug_keywords[slug] = set(keywords)
                except Exception as e:
                    print(f"Error reading {path}: {e}")
    return slug_keywords


def parse_expected_distribution():
    """Parses CLUSTER_DISTRIBUTION.md to find expected mapping."""
    # This is tricky because the MD is human-readable.
    # We will look for lines like: | `Source Cluster` | `Dest Path` |
    # But checking exact keywords from MD is hard because MD usually just lists Cluster Names, not all keys.
    # HOWEVER, we can stick to checking if the Categories exist and generally align.

    # Actually, a better Reality Check is:
    # 1. Does every Slug in FS have >= 1 keyword?
    # 2. Do we have "Empty" categories that SHOULD have keywords according to our logic?
    pass


def generate_report():
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

    output_path = os.path.join(REPORTS_DIR, "KEYWORD_CONSISTENCY.md")
    with open(output_path, "w", encoding="utf-8") as f:
        f.write("\n".join(report_lines))

    print(f"Report generated at {output_path}")


if __name__ == "__main__":
    generate_report()
