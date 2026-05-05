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


if __name__ == "__main__":
    sql_file = Path(
        r"c:\Users\user\Documents\Сайты\Ultimate.net.ua\сео_для_категорий_ультимейт\data\dumps\ultimate_net_ua_backup.sql"
    )
    categories = extract_categories(sql_file)
    print("ID | Name")
    print("---|---")
    for cid in sorted(categories.keys()):
        print(f"{cid} | {categories[cid]}")
