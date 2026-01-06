import json
import os
import re

PROJECT_ROOT = r"c:\Users\user\Documents\Сайты\Ultimate.net.ua\сео_для_категорий_ультимейт"
STRUCTURE_MD_PATH = os.path.join(PROJECT_ROOT, "data", "generated", "STRUCTURE.md")
CATEGORIES_DIR = os.path.join(PROJECT_ROOT, "categories")


def scan_json_keywords():
    """Builds a map: Keyword -> Slug based on current JSON files."""
    kw_map = {}
    for root, _dirs, files in os.walk(CATEGORIES_DIR):
        for file in files:
            if file.endswith("_clean.json"):
                path = os.path.join(root, file)
                try:
                    with open(path, "r", encoding="utf-8") as f:
                        data = json.load(f)
                    slug = data.get("id") or data.get("slug")

                    keywords = []
                    # V2
                    if isinstance(data.get("keywords"), list):
                        keywords = [k["keyword"] for k in data["keywords"]]
                    # Legacy
                    elif isinstance(data.get("keywords"), dict):
                        for group in data["keywords"].values():
                            for k in group:
                                keywords.append(k["keyword"])

                    for kw in keywords:
                        kw_norm = kw.strip().lower()
                        kw_map[kw_norm] = slug
                except Exception:
                    pass
    return kw_map


def parse_structure_md_keywords():
    """Parses STRUCTURE.md to capture (Cluster Name -> [Keywords]).
    Recognizes Keywords in Tables | kw | vol |"""
    cluster_kws = {}
    current_cluster = "Unknown"

    # Pre-compiled regex for table row: | keyword | volume | ...
    # Exclude header row matches
    table_row_re = re.compile(r"^\|\s*(.+?)\s*\|\s*(\d+)\s*\|")

    with open(STRUCTURE_MD_PATH, "r", encoding="utf-8") as f:
        for line in f:
            line = line.strip()

            # 1. Detect Cluster Header (###... Name)
            # Matches: #### 📦 Cluster: ...  OR  ##### 🏷️ L3: ...
            if line.startswith("#"):
                # Extract text after hashtags
                clean_header = line.lstrip("#").strip()
                # Skip main headers like "Структура..." or "L1..." if they don't look like clusters
                # But actually, clusters often follow L2 headers immediately.
                # Let's use specific markers "Cluster:" or "L3:" or just assume table follows semantic header.

                # Use simplified logic: if it mentions "Cluster" or "L3" or even "L2" (if holds keys)
                if (
                    "Cluster:" in clean_header
                    or "L3:" in clean_header
                    or "Filter:" in clean_header
                    or "Direct Keywords" in clean_header
                ):
                    # Remove (Vol: 123) suffix
                    current_cluster = re.sub(r"\(Vol:.*?\)", "", clean_header).strip()
                    if current_cluster not in cluster_kws:
                        cluster_kws[current_cluster] = []
                continue

            # 2. Detect Table Row
            if line.startswith("|"):
                # Skip structure separators like |---|
                if "---" in line:
                    continue
                # Skip header row
                if "Keyword" in line and "Volume" in line:
                    continue

                match = table_row_re.match(line)
                if match:
                    kw = match.group(1).strip().lower()
                    if current_cluster:
                        if current_cluster not in cluster_kws:
                            cluster_kws[current_cluster] = []
                        cluster_kws[current_cluster].append(kw)

    return cluster_kws


def analyze_coverage():
    json_map = scan_json_keywords()  # kw -> slug
    structure_clusters = parse_structure_md_keywords()  # cluster_name -> [kws]

    report = []
    report.append("# Сверка Семантики: STRUCTURE.md vs JSONs (Table Mode)")
    report.append("")

    total_structure_kws = 0
    missing_kws = []

    # Sort clusters for checking
    for cluster in sorted(structure_clusters.keys()):
        kws = structure_clusters[cluster]
        if not kws:
            continue

        cluster_missing = []
        for kw in kws:
            total_structure_kws += 1
            if kw not in json_map:
                cluster_missing.append(kw)

        if cluster_missing:
            report.append(f"### ❌ Cluster: {cluster}")
            report.append(f"Потеряно ключей: {len(cluster_missing)} / {len(kws)}")
            for m in cluster_missing:
                report.append(f"- {m}")
            report.append("")
            missing_kws.extend(cluster_missing)

    report.append("## Итог")
    report.append(f"- Всего ключей в `STRUCTURE.md`: **{total_structure_kws}**")
    report.append(f"- Найдено в JSON-файлах: **{len(json_map)}**")
    report.append(f"- Потеряно/Не распределено: **{len(missing_kws)}**")

    # Note: JSONs might have duplicates if same kW used in meta vs content?
    # Usually clean json has unique list.

    if len(missing_kws) == 0 and total_structure_kws > 0:
        report.append("\n✅ **ALL CLEAR:** Все ключи из STRUCTURE.md находятся в JSON-файлах.")
    elif total_structure_kws == 0:
        report.append("\n⚠️ **ERROR:** Не удалось прочитать ключи из STRUCTURE.md (проблемы парсинга?)")
    else:
        report.append("\n⚠️ **ATTENTION:** Есть потерянные ключи.")

    output_path = os.path.join(PROJECT_ROOT, "tasks", "reports", "SEMANTIC_COVERAGE_CHECK.md")
    with open(output_path, "w", encoding="utf-8") as f:
        f.write("\n".join(report))

    print(f"Coverage report generated at {output_path}")


if __name__ == "__main__":
    analyze_coverage()
