import argparse
import re
import sys
from pathlib import Path

# Force UTF-8 for output
if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8")


def extract_categories(sql_file: Path) -> dict[int, str]:
    """Extract category names from SQL dump."""
    categories = {}
    with open(sql_file, encoding="utf-8", errors="ignore") as f:
        in_insert = False
        for line in f:
            if "INSERT INTO `oc_category_description` VALUES" in line:
                in_insert = True
                matches = re.findall(r"\((\d+),1,'([^']*)'", line)
                for cid, name in matches:
                    categories[int(cid)] = name
            elif in_insert:
                if line.strip().startswith("("):
                    matches = re.findall(r"\((\d+),1,'([^']*)'", line)
                    for cid, name in matches:
                        categories[int(cid)] = name
                if ";" in line:
                    in_insert = False
    return categories


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Extract category names from an OpenCart SQL dump.")
    parser.add_argument("sql_file", type=Path, help="Path to SQL dump")
    args = parser.parse_args(argv)

    sql_file = args.sql_file
    if not sql_file.exists():
        print(f"SQL dump not found: {sql_file}", file=sys.stderr)
        return 2

    categories = extract_categories(sql_file)
    print("ID | Name")
    print("---|---")
    for cid in sorted(categories.keys()):
        print(f"{cid} | {categories[cid]}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
