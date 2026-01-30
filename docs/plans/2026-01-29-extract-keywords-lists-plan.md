# Extract Keywords Lists (RU/UK) Implementation Plan

> **For Claude:** REQUIRED SUB-SKILL: Use superpowers:executing-plans to implement this plan task-by-task.

**Goal:** Создать два скрипта для извлечения всех ключей из RU и UK категорий в MD файлы.

**Architecture:** Два независимых скрипта с общей логикой извлечения. Каждый сканирует свою директорию (`categories/` или `uk/categories/`), собирает ключи из `_clean.json`, дедуплицирует и сохраняет в MD.

**Tech Stack:** Python 3.10+, стандартная библиотека (json, pathlib)

---

### Task 1: Создать extract_ru_keywords_list.py

**Files:**
- Create: `scripts/extract_ru_keywords_list.py`

**Step 1: Создать скрипт**

```python
#!/usr/bin/env python3
"""Извлечение всех ключей из RU категорий в MD файл."""

import json
from pathlib import Path

ROOT = Path(__file__).parent.parent
CATEGORIES_DIR = ROOT / "categories"
OUTPUT_FILE = ROOT / "data" / "generated" / "RU_KEYWORDS.md"


def extract_keywords_from_file(filepath: Path) -> set[str]:
    """Извлекает все ключи из _clean.json файла."""
    keywords = set()

    try:
        data = json.loads(filepath.read_text(encoding="utf-8"))
    except (json.JSONDecodeError, FileNotFoundError) as e:
        print(f"⚠️  {filepath.name}: {e}")
        return keywords

    keywords_data = data.get("keywords", [])
    synonyms_data = data.get("synonyms", [])
    variations_data = data.get("variations", [])

    # Handle legacy format: keywords is dict with groups
    if isinstance(keywords_data, dict):
        for group_items in keywords_data.values():
            if isinstance(group_items, list):
                for item in group_items:
                    if "keyword" in item:
                        keywords.add(item["keyword"].lower().strip())
    else:
        # New format: keywords is list
        for item in keywords_data:
            if "keyword" in item:
                keywords.add(item["keyword"].lower().strip())

    # Synonyms
    if isinstance(synonyms_data, list):
        for item in synonyms_data:
            if "keyword" in item:
                keywords.add(item["keyword"].lower().strip())

    # Variations
    if isinstance(variations_data, list):
        for item in variations_data:
            if "keyword" in item:
                keywords.add(item["keyword"].lower().strip())

    return keywords


def main():
    all_keywords = set()
    files_count = 0

    for clean_file in sorted(CATEGORIES_DIR.rglob("*_clean.json")):
        keywords = extract_keywords_from_file(clean_file)
        all_keywords.update(keywords)
        files_count += 1

    # Sort and save
    sorted_keywords = sorted(all_keywords)

    OUTPUT_FILE.parent.mkdir(parents=True, exist_ok=True)
    OUTPUT_FILE.write_text("\n".join(sorted_keywords), encoding="utf-8")

    print(f"Найдено {files_count} файлов _clean.json")
    print(f"Извлечено {len(sorted_keywords)} уникальных ключей")
    print(f"✅ Сохранено → {OUTPUT_FILE}")


if __name__ == "__main__":
    main()
```

**Step 2: Запустить и проверить**

Run: `python3 scripts/extract_ru_keywords_list.py`

Expected:
```
Найдено 53 файлов _clean.json
Извлечено ~1100 уникальных ключей
✅ Сохранено → data/generated/RU_KEYWORDS.md
```

**Step 3: Проверить выходной файл**

Run: `head -20 data/generated/RU_KEYWORDS.md && wc -l data/generated/RU_KEYWORDS.md`

Expected: Список ключей по алфавиту, ~1100 строк

---

### Task 2: Создать extract_uk_keywords_list.py

**Files:**
- Create: `scripts/extract_uk_keywords_list.py`

**Step 1: Создать скрипт**

```python
#!/usr/bin/env python3
"""Извлечение всех ключей из UK категорий в MD файл."""

import json
from pathlib import Path

ROOT = Path(__file__).parent.parent
CATEGORIES_DIR = ROOT / "uk" / "categories"
OUTPUT_FILE = ROOT / "data" / "generated" / "UK_KEYWORDS.md"


def extract_keywords_from_file(filepath: Path) -> set[str]:
    """Извлекает все ключи из _clean.json файла."""
    keywords = set()

    try:
        data = json.loads(filepath.read_text(encoding="utf-8"))
    except (json.JSONDecodeError, FileNotFoundError) as e:
        print(f"⚠️  {filepath.name}: {e}")
        return keywords

    keywords_data = data.get("keywords", [])
    synonyms_data = data.get("synonyms", [])
    variations_data = data.get("variations", [])

    # Handle legacy format: keywords is dict with groups
    if isinstance(keywords_data, dict):
        for group_items in keywords_data.values():
            if isinstance(group_items, list):
                for item in group_items:
                    if "keyword" in item:
                        keywords.add(item["keyword"].lower().strip())
    else:
        # New format: keywords is list
        for item in keywords_data:
            if "keyword" in item:
                keywords.add(item["keyword"].lower().strip())

    # Synonyms
    if isinstance(synonyms_data, list):
        for item in synonyms_data:
            if "keyword" in item:
                keywords.add(item["keyword"].lower().strip())

    # Variations
    if isinstance(variations_data, list):
        for item in variations_data:
            if "keyword" in item:
                keywords.add(item["keyword"].lower().strip())

    return keywords


def main():
    all_keywords = set()
    files_count = 0

    for clean_file in sorted(CATEGORIES_DIR.rglob("*_clean.json")):
        keywords = extract_keywords_from_file(clean_file)
        all_keywords.update(keywords)
        files_count += 1

    # Sort and save
    sorted_keywords = sorted(all_keywords)

    OUTPUT_FILE.parent.mkdir(parents=True, exist_ok=True)
    OUTPUT_FILE.write_text("\n".join(sorted_keywords), encoding="utf-8")

    print(f"Найдено {files_count} файлов _clean.json")
    print(f"Извлечено {len(sorted_keywords)} уникальных ключей")
    print(f"✅ Сохранено → {OUTPUT_FILE}")


if __name__ == "__main__":
    main()
```

**Step 2: Запустить и проверить**

Run: `python3 scripts/extract_uk_keywords_list.py`

Expected:
```
Найдено 53 файлов _clean.json
Извлечено ~450 уникальных ключей
✅ Сохранено → data/generated/UK_KEYWORDS.md
```

**Step 3: Проверить выходной файл**

Run: `head -20 data/generated/UK_KEYWORDS.md && wc -l data/generated/UK_KEYWORDS.md`

Expected: Список ключей по алфавиту, ~450 строк

---

### Task 3: Коммит

**Step 1: Добавить файлы и закоммитить**

```bash
git add scripts/extract_ru_keywords_list.py scripts/extract_uk_keywords_list.py
git commit -m "feat: add scripts to extract RU/UK keywords to MD files"
```
