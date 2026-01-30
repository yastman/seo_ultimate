# UK Keywords Refresh — Implementation Plan

> **For Claude:** REQUIRED SUB-SKILL: Use superpowers:executing-plans to implement this plan task-by-task.

**Goal:** Обновить UK семантику, мета-теги и контент для 42 категорий с новыми ключами (реальная UK частотность).

**Architecture:**
1. Распределить 355 новых UK ключей по _clean.json файлам
2. Перегенерировать мета-теги с новыми primary keywords
3. Перевалидировать существующий контент (40 категорий) + сгенерировать новый (2 категории)
4. Финальная валидация через quality-gate

**Tech Stack:** Python скрипты, UK skills (/uk-generate-meta, /uk-content-generator, uk-content-reviewer, /uk-quality-gate)

**Input:** `uk/data/uk_keywords.json` — 355 ключей, 42 категории

---

## Task 1: Создать скрипт обновления _clean.json

**Files:**
- Create: `scripts/update_uk_clean_json.py`

**Step 1: Написать скрипт**

```python
#!/usr/bin/env python3
"""
Обновляет uk/categories/{slug}/data/{slug}_clean.json
на основе uk/data/uk_keywords.json
"""
import json
from pathlib import Path

def load_uk_keywords():
    with open('uk/data/uk_keywords.json', 'r', encoding='utf-8') as f:
        return json.load(f)

def group_keywords(keywords: list) -> dict:
    """Группирует ключи по volume: primary >500, secondary 100-500, supporting <100"""
    primary = [k for k in keywords if k['volume'] >= 500]
    secondary = [k for k in keywords if 100 <= k['volume'] < 500]
    supporting = [k for k in keywords if k['volume'] < 100]
    return {
        'primary': primary,
        'secondary': secondary,
        'supporting': supporting
    }

def update_clean_json(slug: str, keywords: list, total_volume: int):
    """Создает/обновляет _clean.json для категории"""
    uk_cat_dir = Path(f'uk/categories/{slug}')
    data_dir = uk_cat_dir / 'data'
    data_dir.mkdir(parents=True, exist_ok=True)

    clean_path = data_dir / f'{slug}_clean.json'

    grouped = group_keywords(keywords)

    # Формируем структуру
    clean_data = {
        'id': slug,
        'language': 'uk',
        'total_volume': total_volume,
        'keywords': grouped['primary'],
        'secondary_keywords': grouped['secondary'],
        'supporting_keywords': grouped['supporting'],
        'all_keywords_count': len(keywords)
    }

    with open(clean_path, 'w', encoding='utf-8') as f:
        json.dump(clean_data, f, ensure_ascii=False, indent=2)

    return clean_path

def main():
    data = load_uk_keywords()

    updated = 0
    for slug, cat_data in data['categories'].items():
        keywords = cat_data['keywords']
        total_volume = cat_data['total_volume']

        path = update_clean_json(slug, keywords, total_volume)
        print(f'✅ {slug}: {len(keywords)} keywords, volume {total_volume}')
        updated += 1

    print(f'\n✅ Обновлено: {updated} категорий')

if __name__ == '__main__':
    main()
```

**Step 2: Запустить скрипт**

Run: `python3 scripts/update_uk_clean_json.py`
Expected: 42 категории обновлены

**Step 3: Проверить результат**

Run: `cat uk/categories/aktivnaya-pena/data/aktivnaya-pena_clean.json | head -20`
Expected: JSON с primary/secondary/supporting ключами

**Step 4: Commit**

```bash
git add scripts/update_uk_clean_json.py uk/categories/*/data/*_clean.json
git commit -m "feat(uk): update _clean.json with new UK keywords (355 keywords, 42 categories)"
```

---

## Task 2: Batch генерация UK мета-тегов

**Files:**
- Modify: `uk/categories/*/meta/*_meta.json` (42 файла)

**Step 1: Создать batch-скрипт для мета**

```python
#!/usr/bin/env python3
"""
Batch генерация UK мета-тегов через агент uk-generate-meta
"""
import json
import subprocess
from pathlib import Path

def get_categories_with_keywords():
    with open('uk/data/uk_keywords.json', 'r', encoding='utf-8') as f:
        data = json.load(f)
    return list(data['categories'].keys())

def main():
    categories = get_categories_with_keywords()
    print(f'Категорий для обработки: {len(categories)}')

    for i, slug in enumerate(categories, 1):
        print(f'\n[{i}/{len(categories)}] {slug}')
        # Здесь будет вызов агента uk-generate-meta

if __name__ == '__main__':
    main()
```

**Step 2: Запустить агент uk-generate-meta для каждой категории**

Использовать Task tool с subagent_type=uk-generate-meta для каждого slug.
Можно batch по 5-10 параллельно.

**Step 3: Проверить результаты**

Run: `python3 scripts/validate_meta.py uk/categories/aktivnaya-pena/meta/aktivnaya-pena_meta.json`
Expected: PASS (Title 50-60, Description 120-160, H1 без "Купити")

**Step 4: Commit**

```bash
git add uk/categories/*/meta/*_meta.json
git commit -m "feat(uk): regenerate meta tags with new UK keywords (42 categories)"
```

---

## Task 3: Генерация контента для 2 категорий без текстов

**Files:**
- Create: `uk/categories/ochistiteli-kuzova/content/ochistiteli-kuzova_uk.md`
- Create: `uk/categories/polirovalnye-mashinki/content/polirovalnye-mashinki_uk.md`

**Step 1: Запустить uk-content-generator для ochistiteli-kuzova**

Task tool с subagent_type=uk-content-generator, prompt: `ochistiteli-kuzova`

**Step 2: Запустить uk-content-generator для polirovalnye-mashinki**

Task tool с subagent_type=uk-content-generator, prompt: `polirovalnye-mashinki`

**Step 3: Проверить результаты**

Run: `python3 scripts/check_seo_structure.py uk/categories/ochistiteli-kuzova/content/ochistiteli-kuzova_uk.md "очищувач кузова"`
Expected: H2 keyword ≥2, intro keyword OK

**Step 4: Commit**

```bash
git add uk/categories/ochistiteli-kuzova/content/ uk/categories/polirovalnye-mashinki/content/
git commit -m "feat(uk): generate content for ochistiteli-kuzova, polirovalnye-mashinki"
```

---

## Task 4: Перевалидация существующего контента (40 категорий)

**Files:**
- Modify: `uk/categories/*/content/*_uk.md` (40 файлов)

**Step 1: Создать скрипт проверки ключей в контенте**

```python
#!/usr/bin/env python3
"""
Проверяет какие ключи из _clean.json присутствуют/отсутствуют в контенте
"""
import json
import re
from pathlib import Path

def check_keywords_in_content(slug: str):
    clean_path = Path(f'uk/categories/{slug}/data/{slug}_clean.json')
    content_path = Path(f'uk/categories/{slug}/content/{slug}_uk.md')

    if not clean_path.exists() or not content_path.exists():
        return None

    with open(clean_path, 'r', encoding='utf-8') as f:
        clean_data = json.load(f)

    with open(content_path, 'r', encoding='utf-8') as f:
        content = f.read().lower()

    all_keywords = (
        clean_data.get('keywords', []) +
        clean_data.get('secondary_keywords', []) +
        clean_data.get('supporting_keywords', [])
    )

    found = []
    missing = []

    for kw_data in all_keywords:
        kw = kw_data['keyword'].lower()
        if kw in content:
            found.append(kw_data)
        else:
            missing.append(kw_data)

    return {
        'slug': slug,
        'total': len(all_keywords),
        'found': len(found),
        'missing': len(missing),
        'missing_keywords': missing[:5]  # Top 5 by volume
    }

def main():
    with open('uk/data/uk_keywords.json', 'r', encoding='utf-8') as f:
        data = json.load(f)

    results = []
    for slug in data['categories'].keys():
        result = check_keywords_in_content(slug)
        if result:
            results.append(result)
            coverage = result['found'] / result['total'] * 100 if result['total'] > 0 else 0
            status = '✅' if coverage >= 50 else '⚠️' if coverage >= 30 else '❌'
            print(f"{status} {slug}: {result['found']}/{result['total']} ({coverage:.0f}%)")
            if result['missing_keywords']:
                print(f"   Missing top: {[k['keyword'] for k in result['missing_keywords'][:3]]}")

if __name__ == '__main__':
    main()
```

**Step 2: Запустить проверку**

Run: `python3 scripts/check_uk_keyword_coverage.py`
Expected: Список категорий с % покрытия ключей

**Step 3: Запустить uk-content-reviewer для категорий с низким покрытием**

Для каждой категории с покрытием <50%:
- Task tool с subagent_type=uk-content-reviewer
- Агент найдёт и вставит недостающие ключи

**Step 4: Commit после каждого batch**

```bash
git add uk/categories/*/content/*_uk.md
git commit -m "fix(uk): update content with new keywords - batch N"
```

---

## Task 5: Финальная валидация через quality-gate

**Files:**
- Create: `uk/categories/*/QUALITY_REPORT.md` (42 файла)

**Step 1: Запустить uk-quality-gate для всех категорий**

Batch по 5-10 категорий:
- Task tool с subagent_type=uk-quality-gate

**Step 2: Проверить отчёты**

Run: `grep -l "FAIL" uk/categories/*/QUALITY_REPORT.md`
Expected: Пустой вывод (все PASS)

**Step 3: Исправить FAIL категории**

Для каждой FAIL:
- Прочитать QUALITY_REPORT.md
- Запустить uk-content-reviewer для исправления
- Повторить quality-gate

**Step 4: Финальный commit**

```bash
git add uk/categories/*/QUALITY_REPORT.md
git commit -m "feat(uk): quality-gate PASS for all 42 categories"
```

---

## Summary

| Task | Категорий | Действие |
|------|-----------|----------|
| 1 | 42 | Обновить _clean.json |
| 2 | 42 | Перегенерировать мета |
| 3 | 2 | Сгенерировать новый контент |
| 4 | 40 | Перевалидировать контент |
| 5 | 42 | Quality-gate |

**Estimated batches:** ~15-20 (по 5-10 категорий за batch)
