#!/usr/bin/env python3
"""
check_h1_sync.py — Проверка синхронизации H1 между Content (MD) и Meta (JSON).

Проблема: H1 в Markdown файле (который видит пользователь) может отличаться от
H1 в JSON файле (который уходит в БД OpenCart в поле meta_h1).

Это приводит к тому, что на сайте может отображаться не тот заголовок, который
ожидается, или дублирование заголовков.

Использование:
    python3 scripts/check_h1_sync.py
    python3 scripts/check_h1_sync.py --fix  # Автоматически обновить JSON из MD
"""

import argparse
import json
import re
from pathlib import Path

# Импорт конфигурации
try:
    from config import CATEGORIES_DIR
except ImportError:
    # Fallback если запуск не из корня
    PROJECT_ROOT = Path(__file__).parent.parent
    CATEGORIES_DIR = PROJECT_ROOT / "categories"


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


def check_sync(fix: bool = False):
    """Проверяет все категории на синхронизацию H1."""
    print(f"🔍 Проверка синхронизации H1 в {CATEGORIES_DIR}...\n")

    issues_count = 0
    synced_count = 0
    missing_count = 0

    # Проходим по всем папкам категорий
    for category_dir in sorted(CATEGORIES_DIR.iterdir()):
        if not category_dir.is_dir() or category_dir.name.startswith("."):
            continue

        slug = category_dir.name
        md_file = category_dir / "content" / f"{slug}_ru.md"
        json_file = category_dir / "meta" / f"{slug}_meta.json"

        # Проверяем наличие файлов
        if not md_file.exists():
            # print(f"⚠️  {slug}: Нет MD файла")
            missing_count += 1
            continue

        h1_md = extract_h1_from_md(md_file)
        h1_json = get_h1_from_json(json_file)

        if not h1_md:
            print(f"⚠️  {slug}: H1 не найден в MD файле")
            missing_count += 1
            continue

        if not h1_json:
            # Если JSON нет, это не ошибка синхронизации, а отсутствие меты
            # print(f"ℹ️  {slug}: Нет JSON меты (или поля h1)")
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


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Check H1 sync between MD and JSON")
    parser.add_argument("--fix", action="store_true", help="Update JSON to match Markdown H1")
    args = parser.parse_args()

    check_sync(args.fix)
