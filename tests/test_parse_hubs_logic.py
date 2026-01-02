import json
import sys
from pathlib import Path


# Add scripts directory to path
sys.path.insert(0, str(Path(__file__).parent.parent / "scripts"))

from parse_hubs_logic import generate_hub_tasks, parse_structure, slugify


class TestParseHubsLogic:
    def test_slugify(self):
        assert slugify("Тест") == "test"
        assert slugify("Тест Пробел") == "test-probel"
        assert (
            slugify("L1: Категория") == "l1-kategoriya"
        )  # colons are replaced by dash in map but slugify iterates char by char
        # ':' is in map as '-'
        # ' ' is '-'
        # so 'l1' + '-' + '-' + 'kategoriya' -> 'l1--kategoriya' -> 'l1-kategoriya' (regex)
        assert slugify("Test/Slash") == "test-slash"
        # Preserve explicit hyphens.
        assert slugify("a-b") == "a-b"

    def test_parse_structure(self, tmp_path):
        csv_content = """L1: Category One
L2: Sub Cat One
L3: Item One
L3: Item Two

   
L2: Sub Cat Two
L3: Item Three
L1: Category Two
L2: Sub Cat Three
"""
        csv_file = tmp_path / "structure.csv"
        csv_file.write_text(csv_content, encoding="utf-8")

        tree = parse_structure(csv_file)

        # Check L1
        assert "Category One" in tree
        assert tree["Category One"]["slug"] == "category-one"

        # Check L2
        cat1_children = tree["Category One"]["children"]
        assert "Sub Cat One" in cat1_children

        # Check L3
        subcat1_children = cat1_children["Sub Cat One"]["children"]
        assert "Item One" in subcat1_children
        assert "Item Two" in subcat1_children

        # Check L1 Two
        assert "Category Two" in tree
        assert "Sub Cat Three" in tree["Category Two"]["children"]

    def test_generate_hub_tasks(self, tmp_path):
        tree = {
            "Cat One": {
                "slug": "cat-one",
                "children": {"Sub One": {"slug": "sub-one", "children": ["Item A", "Item B"]}},
            }
        }

        generate_hub_tasks(tree, tmp_path)

        # Check files created
        l1_file = tmp_path / "task_cat-one.json"
        l2_file = tmp_path / "task_sub-one.json"

        assert l1_file.exists()
        assert l2_file.exists()

        # Check content
        with open(l1_file, encoding="utf-8") as f:
            data = json.load(f)
            assert data["page_type"] == "hub"
            assert data["category_name"] == "Cat One"
            assert "Sub One" in data["keywords"]  # Primary + subcats
            assert "Sub One" in data["structure"]["subcategories"]

        with open(l2_file, encoding="utf-8") as f:
            data = json.load(f)
            assert data["page_type"] == "hub"
            assert data["category_name"] == "Sub One"
            assert "Item A" in data["keywords"]
