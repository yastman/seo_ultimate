import csv
import os
import re

# Simple transliteration map (Cyrillic to Latin)
TRANS_MAP = {
    "а": "a",
    "б": "b",
    "в": "v",
    "г": "g",
    "д": "d",
    "е": "e",
    "ё": "yo",
    "ж": "zh",
    "з": "z",
    "и": "i",
    "й": "y",
    "к": "k",
    "л": "l",
    "м": "m",
    "н": "n",
    "о": "o",
    "п": "p",
    "р": "r",
    "с": "s",
    "т": "t",
    "у": "u",
    "ф": "f",
    "х": "kh",
    "ц": "ts",
    "ч": "ch",
    "ш": "sh",
    "щ": "shch",
    "ъ": "",
    "ы": "y",
    "ь": "",
    "э": "e",
    "ю": "yu",
    "я": "ya",
    " ": "-",
    "-": "-",
    "/": "-",
    "\\": "-",
    ":": "",
}


def transliterate(text):
    text = text.lower()
    res = []
    for char in text:
        if char in TRANS_MAP:
            res.append(TRANS_MAP[char])
        elif char.isalnum():
            res.append(char)
        # trim duplicate dashes
    return re.sub(r"-+", "-", "".join(res)).strip("-")


def get_project_categories(base_path):
    cats = []
    if os.path.exists(base_path):
        for item in os.listdir(base_path):
            if os.path.isdir(os.path.join(base_path, item)):
                cats.append(item)
    return set(cats)


def parse_csv(file_path):
    categories = []
    with open(file_path, encoding="utf-8") as f:
        reader = csv.reader(f)
        for row in reader:
            if not row:
                continue

            # Check for L-headers
            stripped_cell = row[0].strip()

            # Pattern for "L1: Name", "L2: Name", "SEO-Фильтр: Name"
            if ":" in stripped_cell and (stripped_cell.startswith("L") or stripped_cell.startswith("SEO")):
                parts = stripped_cell.split(":", 1)
                cat_name = (
                    parts[1].strip().split(",")[0]
                )  # Handle case where comma might be in line? No CSV reader handles commas.
                # Actually row[0] is the cell.
                # If the cell content itself has a comma inside, csv reader handles it.
                # But here we just split by colon.
                cat_name = parts[1].strip()
                categories.append({"name": cat_name, "source": stripped_cell})
                # print(f"Found L-cat: {cat_name}")
                continue

            # Check for other headers (Name, Count, ...)
            # Logic: Col 0 has text, Col 1 has data (count), Col 2 might be empty or traffic.
            # And it's not a keyword line (usually keywords have empty Col 1 in this file, judging by lines 9-60).
            # Wait, lines 9-60: "пена для мойки автомобиля,,1300" -> Col 0: text, Col 1: empty, Col 2: traffic.
            # Lines 4: "L1: ...", "24/338", ""
            # Line 8: "L3: ...", "52", ""
            # Line 80: "Омыватель", "35", ""

            if len(row) > 1:
                col1 = row[1].strip()
                if col1:  # If column 1 (count) is NOT empty, it's likely a category
                    cat_name = row[0].strip()
                    # Filter out "total" summary lines if any, or things that don't look like categories.
                    if cat_name.lower() not in ["фраза", "категория"]:
                        categories.append({"name": cat_name, "source": cat_name})
                        # print(f"Found other-cat: {cat_name}")

    return categories


def main():
    project_categories_path = r"c:\Users\user\Documents\Сайты\Ultimate.net.ua\сео_для_категорий_ультимейт\categories"
    csv_path = r"c:\Users\user\Documents\Сайты\Ultimate.net.ua\сео_для_категорий_ультимейт\Структура _Ultimate.csv"

    existing_categories = get_project_categories(project_categories_path)
    csv_categories = parse_csv(csv_path)

    print(f"Found {len(existing_categories)} existing project categories.")
    print(f"Found {len(csv_categories)} categories in CSV.")

    missing_categories = []
    mapped_categories = []

    # Manual overrides for tricky matches
    MANUAL_MAP = {
        "sredstva-dlya-diskov-i-shin": ["средства для дисков и шин"],
        "keramika-i-zhidkoe-steklo": ["керамика и жидкое стекло"],
        "apparaty-tornador": ["аппараты tornador"],
        "gubki-i-varezhki": ["губки и варежки"],
        "raspyliteli-i-penniki": ["распылители и пенники"],
        "mikrofibra-i-tryapki": ["микрофибра и тряпки"],
        "shchetki-i-kisti": ["щетки и кисти"],
        "vedra-i-emkosti": ["ведра и емкости"],
        "aksessuary-dlya-naneseniya": ["аксессуары для нанесения средств"],
        "dlya-vneshnego-plastika": ["для внешнего пластика и резины"],
        "dlya-khimchistki-salona": ["для химчистки салона"],
        "sredstva-dlya-kozhi": [
            "средства для кожи",
            "уход за кожей",
        ],  # Mapping multiple CSV cats to one folder? Or vice versa.
        "polirol-dlya-stekla": ["полироль для стекла"],
        "tverdyy-vosk": ["твердый"],
        "zhidkiy-vosk": ["жидкий (быстрый)", "жидкий воск"],
        "s-voskom": ["с воском"],
        "kislotnyy-shampun": ["кислотный"],
    }

    # Reverse manual map for check
    REVERSE_MANUAL = {}
    for slug, names in MANUAL_MAP.items():
        for name in names:
            REVERSE_MANUAL[name.lower()] = slug

    print("\n--- Analysis ---")

    found_slugs = set()

    for item in csv_categories:
        name = item["name"]
        slug = transliterate(name)

        # Check exact match
        match = None

        if slug in existing_categories:
            match = slug

        # Check manual map
        if not match:
            lower_name = name.lower()
            if lower_name in REVERSE_MANUAL:
                match = REVERSE_MANUAL[lower_name]

        # Check partial/fuzzy? (Simple check: if slug is contained in an existing category or vice-versa, but risk of false positive)
        # Let's stick to strict first.

        if match:
            # print(f"[OK] '{name}' -> {match}")
            mapped_categories.append((name, match))
            found_slugs.add(match)
        else:
            # Try to find if any existing category "looks like" this one
            found_fuzzy = False
            for ex_cat in existing_categories:
                if ex_cat.replace("-", "") == slug.replace("-", ""):
                    mapped_categories.append((name, ex_cat))
                    found_slugs.add(ex_cat)
                    found_fuzzy = True
                    break

            if not found_fuzzy:
                missing_categories.append(item)

    print(f"\nMapped {len(mapped_categories)} categories.")
    print(f"Missing {len(missing_categories)} categories (Present in CSV, not found in Project).")

    print("\n--- Missing Categories (Potential Action Items) ---")
    seen_names = set()
    for item in missing_categories:
        if item["name"] not in seen_names:
            print(f"- {item['name']} (Slug: {transliterate(item['name'])})")
            seen_names.add(item["name"])

    print("\n--- Unused Project Categories (In Project, not in CSV analysis) ---")
    unused = existing_categories - found_slugs
    for u in unused:
        print(f"- {u}")


if __name__ == "__main__":
    main()
