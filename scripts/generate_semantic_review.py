import json
import os

PROJECT_ROOT = r"c:\Users\user\Documents\Сайты\Ultimate.net.ua\сео_для_категорий_ультимейт"
CATEGORIES_DIR = os.path.join(PROJECT_ROOT, "categories")
OUTPUT_JSON = os.path.join(PROJECT_ROOT, "data", "all_keywords.json")
OUTPUT_MD = os.path.join(PROJECT_ROOT, "tasks", "reports", "SEMANTIC_REVIEW.md")


def collect_keywords():
    all_data = []

    for root, _dirs, files in os.walk(CATEGORIES_DIR):
        for file in files:
            if file.endswith("_clean.json"):
                path = os.path.join(root, file)
                try:
                    with open(path, encoding="utf-8") as f:
                        data = json.load(f)

                    slug = data.get("id") or data.get("slug")
                    name = data.get("name", slug)

                    kws = []
                    if isinstance(data.get("keywords"), list):
                        kws = data["keywords"]
                    elif isinstance(data.get("keywords"), dict):
                        for group in data["keywords"].values():
                            kws.extend(group)

                    # Sort by volume
                    kws.sort(key=lambda x: x.get("volume", 0), reverse=True)

                    all_data.append(
                        {
                            "slug": slug,
                            "name": name,
                            "keywords": kws,
                            "total_vol": sum(k.get("volume", 0) for k in kws),
                        }
                    )
                except Exception as e:
                    print(f"Error reading {file}: {e}")

    # Sort categories by ID for stability
    all_data.sort(key=lambda x: x["slug"])
    return all_data


def generate_report(data):
    lines = []
    lines.append("# 🧬 Семантический Ревизор (Semantic Review)")
    lines.append(f"**Total Categories:** {len(data)}")
    lines.append("")
    lines.append(
        "> Этот отчет предназначен для ручной проверки распределения ключей. Проверьте, что ключи соответствуют интенту категории."
    )
    lines.append("")

    for cat in data:
        slug = cat["slug"]
        name = cat["name"]
        vol = cat["total_vol"]
        kws = cat["keywords"]

        lines.append(f"## 📂 [{slug}] {name}")
        lines.append(f"**Volume:** {vol} | **Keywords:** {len(kws)}")
        lines.append("")

        if not kws:
            lines.append("*⚠️ Нет ключей (Empty)*")
        else:
            lines.append("| Keyword | Vol |")
            lines.append("|---|---|")
            # Show top 50 keys to verify intent
            for k in kws[:100]:
                lines.append(f"| {k['keyword']} | {k.get('volume', 0)} |")

            if len(kws) > 100:
                lines.append(f"| *... и еще {len(kws) - 100}* | |")

        lines.append("")
        lines.append("---")
        lines.append("")

    with open(OUTPUT_JSON, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=2, ensure_ascii=False)

    with open(OUTPUT_MD, "w", encoding="utf-8") as f:
        f.write("\n".join(lines))

    print(f"Generated {OUTPUT_JSON}")
    print(f"Generated {OUTPUT_MD}")


if __name__ == "__main__":
    data = collect_keywords()
    generate_report(data)
