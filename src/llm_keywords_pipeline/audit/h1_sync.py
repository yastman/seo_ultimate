#!/usr/bin/env python3
"""
check_h1_sync.py — Проверка синхронизации H1 между Content (MD) и Meta (JSON).

Проблема: H1 в Markdown файле (который видит пользователь) может отличаться от
H1 в JSON файле (который уходит в БД OpenCart в поле meta_h1).

Usage:
    uv run python -m llm_keywords_pipeline.audit.h1_sync
    uv run python -m llm_keywords_pipeline.audit.h1_sync --fix
    uv run python -m llm_keywords_pipeline.audit.h1_sync --lang uk
"""

from __future__ import annotations

import argparse
import json
import re
from pathlib import Path

from llm_keywords_pipeline.core.config import CATEGORIES_DIR, PROJECT_ROOT


def extract_h1_from_md(md_path: Path) -> str | None:
    """Извлекает H1 из Markdown файла."""
    if not md_path.exists():
        return None

    content = md_path.read_text(encoding="utf-8")
    match = re.search(r"^#\s+(.+)$", content, re.MULTILINE)
    if match:
        return match.group(1).strip()
    return None


def get_h1_from_json(json_path: Path) -> str | None:
    """Извлекает H1 из JSON мета-файла."""
    if not json_path.exists():
        return None

    try:
        data = json.loads(json_path.read_text(encoding="utf-8"))
        return data.get("h1") or data.get("meta_h1")
    except json.JSONDecodeError:
        return None


def check_sync(fix: bool = False, lang: str = "ru"):
    """Проверяет все категории на синхронизацию H1."""
    # Select paths based on language
    if lang == "uk":
        categories_dir = PROJECT_ROOT / "uk" / "categories"
        content_suffix = "_uk.md"
    else:
        categories_dir = CATEGORIES_DIR
        content_suffix = "_ru.md"

    print(f"🔍 Проверка синхронизации H1 в {categories_dir} ({lang.upper()})...\n")

    issues_count = 0
    synced_count = 0
    missing_count = 0

    # Проходим по всем папкам категорий
    for category_dir in sorted(categories_dir.iterdir()):
        if not category_dir.is_dir() or category_dir.name.startswith("."):
            continue

        slug = category_dir.name
        md_file = category_dir / "content" / f"{slug}{content_suffix}"
        json_file = category_dir / "meta" / f"{slug}_meta.json"

        # Проверяем наличие файлов
        if not md_file.exists():
            missing_count += 1
            continue

        h1_md = extract_h1_from_md(md_file)
        h1_json = get_h1_from_json(json_file)

        if not h1_md:
            print(f"⚠️  {slug}: H1 не найден в MD файле")
            missing_count += 1
            continue

        if not h1_json:
            missing_count += 1
            continue

        # Нормализация для сравнения (убираем лишние пробелы)
        clean_md = " ".join(h1_md.split())
        clean_json = " ".join(h1_json.split())

        if clean_md != clean_json:
            issues_count += 1
            print(f"❌ {slug}")
            print(f"   MD:   '{clean_md}'")
            print(f"   JSON: '{clean_json}'")

            if fix:
                try:
                    data = json.loads(json_file.read_text(encoding="utf-8"))
                    # Обновляем JSON, так как MD - это мастер-контент
                    old_h1 = data.get("h1", "N/A")
                    data["h1"] = clean_md
                    # Если есть meta_h1, тоже обновляем
                    if "meta_h1" in data:
                        data["meta_h1"] = clean_md

                    json_file.write_text(
                        json.dumps(data, ensure_ascii=False, indent=2), encoding="utf-8"
                    )
                    print(f"   ✅ FIXED: JSON обновлен (было: '{old_h1}')")
                except Exception as e:
                    print(f"   ❌ ERROR fixing: {e}")
            else:
                print("   👉 Используйте --fix для синхронизации (MD -> JSON)")
            print("-" * 40)
        else:
            synced_count += 1

    print("\nИтог:")
    print(f"✅ Синхронизировано: {synced_count}")
    print(f"❌ Рассинхрон:      {issues_count}")
    print(f"⚠️  Пропущено (нет файлов): {missing_count}")

    return issues_count


def main():
    parser = argparse.ArgumentParser(description="Check H1 sync between MD and JSON")
    parser.add_argument("--fix", action="store_true", help="Update JSON to match Markdown H1")
    parser.add_argument(
        "--lang", choices=["ru", "uk"], default="ru", help="Language: ru (default) or uk"
    )
    args = parser.parse_args()

    issues = check_sync(args.fix, args.lang)
    return 1 if issues > 0 else 0


if __name__ == "__main__":
    raise SystemExit(main())
