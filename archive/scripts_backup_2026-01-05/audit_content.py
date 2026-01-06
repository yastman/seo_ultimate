#!/usr/bin/env python3
"""
audit_content.py — Комплексный аудит контента и мета-тегов.

Проверяет:
1. Meta Tags: наличие, длина, коммерческие маркеры.
2. Content Quality: наличие таблиц (для buying guides), слова-паразиты.
3. Structure: корректность H1 (синхронизация уже сделана, но проверим наличие).

Использование:
    python3 scripts/audit_content.py
"""

import json
import re
import sys
from pathlib import Path

# Добавляем путь для импорта config
sys.path.insert(0, str(Path(__file__).parent))

try:
    from config import AI_FLUFF_PATTERNS, CATEGORIES_DIR, COMMERCIAL_MODIFIERS
except ImportError:
    # Fallback
    PROJECT_ROOT = Path(__file__).parent.parent
    CATEGORIES_DIR = PROJECT_ROOT / "categories"
    COMMERCIAL_MODIFIERS = ["купить", "цена", "заказать", "интернет-магазин"]
    AI_FLUFF_PATTERNS = [r"в современном мире", r"давайте разберемся"]


def check_meta_quality(meta_path: Path) -> dict:
    """Проверка качества мета-тегов."""
    if not meta_path.exists():
        return {"status": "MISSING", "issues": ["Файл не найден"]}

    try:
        data = json.loads(meta_path.read_text(encoding="utf-8"))
    except json.JSONDecodeError:
        return {"status": "ERROR", "issues": ["Invalid JSON"]}

    meta = data.get("meta", {})
    title = meta.get("title", "")
    desc = meta.get("description", "")

    issues = []

    # Title checks
    if not title:
        issues.append("Empty Title")
    elif len(title) < 30:
        issues.append(f"Short Title ({len(title)} chars)")
    elif len(title) > 70:
        issues.append(f"Long Title ({len(title)} chars)")

    # Title commercial markers
    title_lower = title.lower()
    has_marker = any(m in title_lower for m in COMMERCIAL_MODIFIERS)
    if not has_marker:
        issues.append("Title: Нет коммерческих маркеров (купить, цена...)")

    # Description checks
    if not desc:
        issues.append("Empty Description")
    elif len(desc) < 120:
        issues.append(f"Short Description ({len(desc)} chars)")
    elif len(desc) > 170:  # Google часто режет после 160, но 170 допустимо
        issues.append(f"Long Description ({len(desc)} chars)")

    return {
        "status": "FAIL" if issues else "OK",
        "issues": issues,
        "title": title,
        "desc_len": len(desc),
    }


def check_content_quality(md_path: Path) -> dict:
    """Проверка качества контента (таблицы, слова-паразиты)."""
    if not md_path.exists():
        return {"status": "MISSING", "issues": ["Файл не найден"]}

    text = md_path.read_text(encoding="utf-8")
    text_lower = text.lower()
    issues = []

    # 1. Таблицы (Markdown table row syntax: | ... | ... |)
    # Note: `|` in regex is alternation, so it must be escaped.
    has_table = bool(re.search(r"^\|.+\|.+\|\s*$", text, re.MULTILINE))
    if not has_table:
        # Не блокируем, но отмечаем как инфо (для многих категорий таблица полезна)
        pass  # issues.append("Нет таблиц (рекомендуется для сравнения)")

    # 2. Слова-паразиты (AI Fluff)
    fluff_found = []
    for pattern in AI_FLUFF_PATTERNS:
        if re.search(pattern, text_lower):
            fluff_found.append(pattern.replace(r"\b", "").replace("\\", ""))

    if fluff_found:
        issues.append(f"Найдены стоп-фразы: {', '.join(fluff_found[:3])}")

    return {"status": "WARNING" if issues else "OK", "issues": issues, "has_table": has_table}


def main():
    print(f"📊 Аудит контента в {CATEGORIES_DIR}...\n")

    results = []

    for cat_dir in sorted(CATEGORIES_DIR.iterdir()):
        if not cat_dir.is_dir() or cat_dir.name.startswith("."):
            continue

        slug = cat_dir.name
        md_file = cat_dir / "content" / f"{slug}_ru.md"
        meta_file = cat_dir / "meta" / f"{slug}_meta.json"

        meta_res = check_meta_quality(meta_file)
        content_res = check_content_quality(md_file)

        results.append({"slug": slug, "meta": meta_res, "content": content_res})

    # Вывод отчета
    print(f"{'Slug':<25} {'Meta':<10} {'Content':<10} {'Issues'}")
    print("-" * 80)

    ok_count = 0
    issues_count = 0

    for r in results:
        slug = r["slug"]
        meta_status = r["meta"]["status"]
        content_status = r["content"]["status"]

        issues = r["meta"]["issues"] + r["content"]["issues"]
        if not issues:
            issues_str = "✅ OK"
            ok_count += 1
        else:
            issues_str = "; ".join(issues)
            issues_count += 1

        # Цветной вывод для статусов (символами)
        m_icon = "✅" if meta_status == "OK" else "❌"
        c_icon = "✅" if content_status == "OK" else "⚠️"

        # Если issues слишком длинные, обрезаем
        if len(issues_str) > 40:
            issues_str = issues_str[:37] + "..."

        print(f"{slug:<25} {m_icon} {meta_status:<6} {c_icon} {content_status:<6} {issues_str}")

    print("-" * 80)
    print(f"Итог: {ok_count} категорий OK, {issues_count} с замечаниями.")


if __name__ == "__main__":
    main()
