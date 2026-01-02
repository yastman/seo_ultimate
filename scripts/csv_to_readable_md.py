#!/usr/bin/env python3
"""
csv_to_readable_md.py — Advanced CSV to Markdown Converter

Converts structure CSV to a readable Markdown file with advanced analysis:
- Catches explicit L1/L2/L3 hierarchy
- Detects implicit clusters (Name, Count pattern)
- Parses SEO-Filters as sub-blocks
- Identifies "Orphan" keywords (no category) by auto-clustering them into 'General' blocks if possible.
- Detects "Real Orphans" (keywords in CSV but missing from _clean.json files)
- Detects Duplicates (keywords in multiple categories)

Usage:
    python3 scripts/csv_to_readable_md.py
"""

import csv
import sys
from collections import defaultdict
from pathlib import Path
from typing import Any, Dict, List, Optional, Set


# Add scripts dir to path to allow importing config
sys.path.append(str(Path(__file__).parent))

try:
    import config
    from config import PROJECT_ROOT, SEMANTICS_CSV
except ImportError:
    print("Warning: config.py not found, using default paths.")
    PROJECT_ROOT = Path(__file__).parent.parent
    SEMANTICS_CSV = PROJECT_ROOT / "Структура _Ultimate.csv"

OUTPUT_FILE = PROJECT_ROOT / "data" / "STRUCTURE.md"


class Node:
    def __init__(self, name: str, level: str):
        self.name = name
        self.level = level  # 'L1', 'L2', 'L3', 'Cluster', 'Filter'
        self.children: List[Node] = []
        self.keywords: List[Dict[str, Any]] = []
        self.total_volume = 0
        self.keyword_count = 0

    def add_keyword(self, keyword: str, volume: int):
        self.keywords.append({"keyword": keyword, "volume": volume})
        self.total_volume += volume
        self.keyword_count += 1

    def add_child(self, node: "Node"):
        self.children.append(node)


class SemanticsParser:
    def __init__(self):
        self.tree: List[Node] = []
        self.orphans: List[Dict[str, Any]] = []  # CSV Parsing orphans (structure errors)
        self.keyword_map: Dict[str, Set[str]] = defaultdict(set)
        self.duplicates: List[Dict[str, Any]] = []
        self.csv_total_count: int = 0  # Total keyword lines found in CSV pre-scan
        self.parsed_count: int = 0  # Total keyword lines successfully parsed into tree/orphans

    def parse(self, csv_path: Path) -> None:
        print(f"Reading CSV from: {csv_path}")

        if not csv_path.exists():
            print(f"Error: CSV file not found at {csv_path}")
            return

        # 1. Validation Pre-check: Count actual keywords in file
        self.csv_total_count = self._count_raw_csv_keywords(csv_path)
        print(f"Pre-scan: Found {self.csv_total_count} keyword lines in CSV.")

        # State mapping
        current_l1: Optional[Node] = None
        current_l2: Optional[Node] = None
        current_l3: Optional[Node] = None

        # The active container for keywords (could be L3, Cluster, or Filter)
        active_container: Optional[Node] = None

        # Context for orphans (LAST recognized header)
        last_header = "Start of File"

        with open(csv_path, encoding="utf-8") as f:
            reader = csv.reader(f)
            for row_idx, row in enumerate(reader):
                if not row:
                    continue

                # Safe column access
                col1 = row[0].strip() if len(row) > 0 else ""
                col2 = row[1].strip() if len(row) > 1 else ""
                col3 = row[2].strip() if len(row) > 2 else ""  # Volume

                if not col1:
                    continue

                # --- 1. Detect Hierarchy Markers ---

                # L1
                if col1.startswith("L1:"):
                    name = col1.replace("L1:", "").strip()
                    current_l1 = Node(name, "L1")
                    self.tree.append(current_l1)

                    # Reset lower levels
                    current_l2 = None
                    current_l3 = None
                    active_container = None
                    last_header = f"L1: {name}"
                    continue

                # L2
                if col1.startswith("L2:"):
                    name = col1.replace("L2:", "").strip()
                    current_l2 = Node(name, "L2")

                    # Attach to L1 (or Root if orphan L2)
                    if current_l1:
                        current_l1.add_child(current_l2)
                    else:
                        # Orphan L2 - create implicit L1
                        current_l1 = Node("Implicit Root", "L1")
                        self.tree.append(current_l1)
                        current_l1.add_child(current_l2)

                    # Reset lower levels
                    current_l3 = None
                    active_container = None
                    last_header = f"L2: {name}"
                    continue

                # L3
                if col1.startswith("L3:"):
                    name = col1.replace("L3:", "").strip()
                    class_name = name  # use var to avoiding overwrite loop var if needed
                    current_l3 = Node(class_name, "L3")

                    if current_l2:
                        current_l2.add_child(current_l3)
                    elif current_l1:
                        current_l1.add_child(current_l3)
                    else:
                        # Broken hierarchy
                        dummy = Node("Broken Hierarchy", "L1")
                        self.tree.append(dummy)
                        current_l1 = dummy
                        current_l1.add_child(current_l3)

                    active_container = current_l3
                    last_header = f"L3: {class_name}"
                    continue

                # SEO-Filter
                if col1.startswith("SEO-Фильтр:"):
                    name = col1.replace("SEO-Фильтр:", "").strip()
                    filter_node = Node(name, "Filter")

                    if current_l3:
                        current_l3.add_child(filter_node)
                    elif current_l2:
                        current_l2.add_child(filter_node)
                    elif current_l1:
                        current_l1.add_child(filter_node)

                    active_container = filter_node
                    last_header = f"Filter: {name}"
                    continue

                # Explicit "Category" line
                if col1.lower().startswith("категория") or col1.lower() == "категория":
                    parent_name = (
                        current_l2.name
                        if current_l2
                        else (current_l1.name if current_l1 else "Root")
                    )
                    cluster_name = f"General ({parent_name})"
                    cluster_node = Node(cluster_name, "Cluster")

                    if current_l2:
                        current_l2.add_child(cluster_node)
                    elif current_l1:
                        current_l1.add_child(cluster_node)

                    # This resets L3
                    current_l3 = None
                    active_container = cluster_node
                    last_header = f"Block: Category ({parent_name})"
                    continue

                # --- 2. Detect Implicit Clusters ---
                # Pattern: Name in Col1, Count in Col2 (digit), Col3 is empty or 0.
                is_header = False
                if col2 and (not col3 or col3 == "0"):
                    if any(char.isdigit() for char in col2):
                        is_header = True

                if is_header:
                    name = col1.strip()
                    # Normalize name (Capitalize first letter to match L3 style)
                    if name and name[0].islower():
                        name = name[0].upper() + name[1:]

                    cluster_node = Node(name, "Cluster")

                    # LOGIC CHANGE: Implicit clusters are siblings to L3, children of L2.
                    # They break the current L3 scope.
                    if current_l2:
                        current_l2.add_child(cluster_node)
                    elif current_l1:
                        current_l1.add_child(cluster_node)
                    else:
                        if not current_l1:
                            current_l1 = Node("Misc Root", "L1")
                            self.tree.append(current_l1)
                        current_l1.add_child(cluster_node)

                    # Reset L3 scope
                    current_l3 = None
                    active_container = cluster_node
                    last_header = f"Cluster: {name}"
                    continue

                # --- 3. Detect Keywords ---
                if col3.isdigit():
                    volume = int(col3)
                    self.parsed_count += 1

                    # IMPACT: Auto-create General cluster if we are under a header but have no container
                    if not active_container:
                        if current_l3:
                            active_container = current_l3
                        elif current_l2:
                            # Keywords directly under L2 -> "Direct Keywords"
                            cluster_name = f"🔑 Direct Keywords ({current_l2.name})"
                            if (
                                current_l2.children
                                and current_l2.children[-1].name == cluster_name
                            ):
                                active_container = current_l2.children[-1]
                            else:
                                active_container = Node(cluster_name, "Cluster")
                                current_l2.add_child(active_container)
                        elif current_l1:
                            # Keywords directly under L1
                            cluster_name = f"🔑 Direct Keywords ({current_l1.name})"
                            if (
                                current_l1.children
                                and current_l1.children[-1].name == cluster_name
                            ):
                                active_container = current_l1.children[-1]
                            else:
                                active_container = Node(cluster_name, "Cluster")
                                current_l1.add_child(active_container)

                    if active_container:
                        active_container.add_keyword(col1, volume)
                        self._track_keyword(col1, volume, active_container.name)
                    else:
                        self.orphans.append(
                            {"keyword": col1, "volume": volume, "context": last_header}
                        )
                    continue

    def _count_raw_csv_keywords(self, csv_path: Path) -> int:
        """Count lines that look like keywords (col3 is digits)"""
        count = 0
        with open(csv_path, encoding="utf-8") as f:
            reader = csv.reader(f)
            for row in reader:
                if len(row) > 2 and row[2].strip().isdigit():
                    count += 1
        return count

    def validate(self) -> bool:
        """Ensure all CSV keywords were processed"""
        if self.csv_total_count != self.parsed_count:
            lost = self.csv_total_count - self.parsed_count
            print(
                f"⚠️ VALIDATION FAILED: CSV={self.csv_total_count}, Parsed={self.parsed_count}, Lost={lost}"
            )
            return False
        print(
            f"✅ Validation OK: Parsed {self.parsed_count}/{self.csv_total_count} (100%)"
        )
        return True

    def _track_keyword(self, keyword: str, volume: int, category_name: str) -> None:
        kw_norm = keyword.lower().strip()
        self.keyword_map[kw_norm].add(category_name)

    def analyze_duplicates(self):
        """Find duplicates based on collected map"""
        for kw, categories in self.keyword_map.items():
            if len(categories) > 1:
                self.duplicates.append({"keyword": kw, "categories": list(categories)})

    def generate_markdown(self, output_path: Path) -> None:
        self.analyze_duplicates()

        # Calculate Stats (re-traversal for accuracy)
        total_clusters = 0
        total_volume = 0
        all_keywords_flat: List[Dict[str, Any]] = []

        # Recursively collect stats and flatten keyword list for Top-10
        for l1 in self.tree:
            self._collect_stats_recursive(l1, all_keywords_flat)

        total_keywords = len(all_keywords_flat)
        total_volume = sum(k["volume"] for k in all_keywords_flat)
        orphan_count = len(self.orphans)
        
        # Including Orphans in "Parsed" stats for the report?
        # Typically Orphans are parsed but just not categorized.
        # But if total_keywords + orphan_count != parsed_count, logic error.
        # total_keywords comes from tree. Orphans NOT in tree.
        # So "Total Parsed" = total_keywords (tree) + orphan_count.
        
        real_parsed = total_keywords + orphan_count

        # Count clusters (L3 + Cluster nodes)
        total_clusters = self._count_clusters(self.tree)
        duplicate_count = len(self.duplicates)

        print(
            f"Stats: TreeKWs={total_keywords}, StructOrphans={orphan_count}, TotalParsed={real_parsed}"
        )
        print(f"Writing Markdown to: {output_path}")

        with open(output_path, "w", encoding="utf-8") as f:
            f.write("# Структура Семантики Ultimate.net.ua\n\n")
            f.write(f"Generated from `{SEMANTICS_CSV.name}`\n\n")
            f.write(
                "**Источник Правды**: Единственный источник данных — этот файл CSV. JSON файлы проекта могут быть неактуальны.\n\n"
            )

            validation_icon = "✅" if self.csv_total_count == self.parsed_count else "⚠️"

            f.write("## 📊 Сводка\n\n")
            f.write(
                f"- **Валидация**: {validation_icon} Найдено в CSV: {self.csv_total_count} | Спарсено: {self.parsed_count}\n"
            )
            f.write(
                f"- **Структура**: L1: {len(self.tree)} | Кластеров (L3+): {total_clusters}\n"
            )
            f.write(
                f"- **Ключей в Дереве**: {total_keywords} | **Volume**: {total_volume}\n"
            )
            f.write(f"- **🔄 Дублей в CSV**: {duplicate_count}\n")
            f.write(f"- **⚠️ Ошибки парсинга**: {orphan_count}\n\n")

            # Top 10
            top_10 = sorted(
                all_keywords_flat, key=lambda x: x["volume"], reverse=True
            )[:10]
            f.write("## 🔥 Топ-10 по Volume\n\n")
            f.write("| Keyword | Volume | Block |\n")
            f.write("|---|---|---|\n")
            for kw in top_10:
                f.write(f"| {kw['keyword']} | {kw['volume']} | _(поиск)_ |\n")
            f.write("\n")

            f.write("---\n\n")
            f.write("## 🌳 Дерево Категорий\n\n")

            for l1 in self.tree:
                stats = self._get_node_stats(l1)
                f.write(f"### 📂 L1: {l1.name} (Vol: {stats['vol']})\n\n")

                if not l1.children:
                    f.write("_Пустая категория_\n\n")

                for l2 in l1.children:
                    if l2.level == "L2":
                        self._write_node(f, l2, 4)
                    else:
                        # Direct children of L1 (Clusters)
                        self._write_node(f, l2, 4)

                f.write("---\n\n")

            if self.orphans:
                f.write("## ⚠️ Ошибки Структуры (Без категории)\n\n")
                f.write("| Keyword | Volume | Контекст |\n")
                f.write("|---|---|---|\n")
                sorted_orphans = sorted(
                    self.orphans, key=lambda x: x["volume"], reverse=True
                )
                for o in sorted_orphans:
                    f.write(
                        f"| {o['keyword']} | {o['volume']} | {o['context']} |\n"
                    )

            f.write("\n## 🔄 Дубли (внутри CSV)\n\n")
            if self.duplicates:
                f.write("| Keyword | Категории |\n")
                f.write("|---|---|\n")
                for d in self.duplicates:
                    cats = ", ".join(d["categories"])
                    f.write(f"| {d['keyword']} | {cats} |\n")
            else:
                f.write("_Дублей нет._\n")

    def _collect_stats_recursive(self, node: Node, sink: List[Dict[str, Any]]) -> None:
        for kw in node.keywords:
            sink.append(kw)
        for child in node.children:
            self._collect_stats_recursive(child, sink)

    def _count_clusters(self, nodes: List[Node]) -> int:
        count = 0
        for node in nodes:
            if node.level in ["L3", "Cluster"]:
                count += 1
            count += self._count_clusters(node.children)
        return count

    def _get_node_stats(self, node: Node) -> Dict[str, int]:
        kws = node.keyword_count
        vol = node.total_volume
        for child in node.children:
            s = self._get_node_stats(child)
            kws += s["kws"]
            vol += s["vol"]
        return {"kws": kws, "vol": vol}

    def _write_node(self, f, node: Node, indent_level: int) -> None:
        stats = self._get_node_stats(node)

        icon = "📁" if node.level == "L2" else "🏷️"
        if node.level == "Filter":
            icon = "⚡"
        if node.level == "Cluster":
            icon = "📦"

        prefix = "#" * indent_level
        header_text = f"{prefix} {icon} {node.level}: {node.name} (Vol: {stats['vol']})"
        f.write(f"{header_text}\n\n")

        if node.keywords:
            f.write("| Keyword | Volume |\n")
            f.write("|---|---|\n")
            sorted_kws = sorted(node.keywords, key=lambda k: k["volume"], reverse=True)
            for kw in sorted_kws:
                f.write(f"| {kw['keyword']} | {kw['volume']} |\n")
            f.write("\n")

        for child in node.children:
            self._write_node(f, child, indent_level + 1)


if __name__ == "__main__":
    if not OUTPUT_FILE.parent.exists():
        OUTPUT_FILE.parent.mkdir(parents=True, exist_ok=True)

    parser = SemanticsParser()
    parser.parse(SEMANTICS_CSV)
    
    # 2. Strict Validation Check
    if not parser.validate():
        print("❌ Script aborted due to validation failure.")
        sys.exit(1)
        
    parser.generate_markdown(OUTPUT_FILE)
    print("Done!")
