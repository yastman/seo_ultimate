import json
import os
import re

PROJECT_ROOT = r"c:\Users\user\Documents\Сайты\Ultimate.net.ua\сео_для_категорий_ультимейт"
STRUCTURE_MD_PATH = os.path.join(PROJECT_ROOT, "data", "generated", "STRUCTURE.md")
CATEGORIES_DIR = os.path.join(PROJECT_ROOT, "categories")

# Exact header texts (minus hashes and volume info) mapped to slugs
CLUSTER_TO_SLUG = {
    "📦 Cluster: 🔑 Direct Keywords (Полировальные круги)": "polirovalnye-krugi",
    "🏷️ L3: Очистители стекол": "ochistiteli-stekol",
    "🏷️ L3: Уход за кожей": "ukhod-za-kozhey",
    "🏷️ L3: Шампуни для ручной мойки": "shampuni-dlya-ruchnoy-moyki",
    "📦 Cluster: Тряпка для авто": "tryapka-dlya-avto",
    "📦 Cluster: Щетка для мойки авто": "shchetka-dlya-moyki-avto",
    "📦 Cluster: 🔑 Direct Keywords (Квик-детейлеры)": "kvik-deteylery",
    "📦 Cluster: 🔑 Direct Keywords (Керамика и жидкое стекло)": "keramika-i-zhidkoe-steklo",
    "📦 Cluster: 🔑 Direct Keywords (Полировальные пасты)": "polirovalnye-pasty",
}


def get_keywords_from_structure(target_cluster_name):
    """Parses STRUCTURE.md for a specific cluster."""
    keywords = []
    current_cluster = None
    table_row_re = re.compile(r"^\|\s*(.+?)\s*\|\s*(\d+)\s*\|")

    found = False
    with open(STRUCTURE_MD_PATH, encoding="utf-8") as f:
        for line in f:
            line = line.strip()
            if line.startswith("#"):
                clean_header = line.lstrip("#").strip()
                # Remove (Vol: ...) and trim
                clean_header = re.sub(r"\s*\(Vol:.*?\)", "", clean_header).strip()
                current_cluster = clean_header
                continue

            if current_cluster == target_cluster_name:
                found = True
                if line.startswith("|") and "---" not in line and "Keyword" not in line:
                    match = table_row_re.match(line)
                    if match:
                        kw = match.group(1).strip().lower()
                        vol = int(match.group(2).strip())
                        keywords.append({"keyword": kw, "volume": vol})

    if not found:
        print(f"  [Parser] Header not found: '{target_cluster_name}'")
    return keywords


def update_json_file(slug, structure_kws):
    json_path = os.path.join(CATEGORIES_DIR, slug, "data", f"{slug}_clean.json")
    if not os.path.exists(json_path):
        print(f"File not found: {json_path}")
        return

    with open(json_path, encoding="utf-8") as f:
        data = json.load(f)

    # Existing kws
    existing_kws = set()
    if isinstance(data.get("keywords"), list):
        for k in data["keywords"]:
            existing_kws.add(k["keyword"].lower())
    elif isinstance(data.get("keywords"), dict):
        for group in data["keywords"].values():
            for k in group:
                existing_kws.add(k["keyword"].lower())

    added_count = 0

    # Strategy:
    # If V2 (list), append to list.
    # If Legacy (dict), append to 'primary'.

    if isinstance(data.get("keywords"), list):
        for sk in structure_kws:
            if sk["keyword"] not in existing_kws:
                data["keywords"].append(sk)
                existing_kws.add(sk["keyword"])
                added_count += 1
        data["keywords"].sort(key=lambda x: x["volume"], reverse=True)

    elif isinstance(data.get("keywords"), dict):
        if "primary" not in data["keywords"]:
            data["keywords"]["primary"] = []
        for sk in structure_kws:
            if sk["keyword"] not in existing_kws:
                sk["cluster"] = "restored_from_structure"
                data["keywords"]["primary"].append(sk)
                added_count += 1

    if added_count > 0:
        with open(json_path, "w", encoding="utf-8") as f:
            json.dump(data, f, indent=2, ensure_ascii=False)
        print(f"✅ [{slug}] Added {added_count} keywords.")
    else:
        print(f"✨ [{slug}] Match.")


def main():
    print("Fixing missing keywords...")
    for cluster_name, slug in CLUSTER_TO_SLUG.items():
        kws = get_keywords_from_structure(cluster_name)
        if kws:
            update_json_file(slug, kws)
        else:
            print(f"⚠️ No keywords found for: {cluster_name}")


if __name__ == "__main__":
    main()
