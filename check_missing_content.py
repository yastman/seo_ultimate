#!/usr/bin/env python3
"""Скрипт для проверки наличия контента в категориях."""

from pathlib import Path

# Базовая директория
BASE_DIR = Path(__file__).parent / "categories"

# Минимальная длина контента (в символах)
MIN_CONTENT_LENGTH = 500


def is_placeholder_content(content: str) -> bool:
    """Проверяет, является ли контент заглушкой."""
    if not content or len(content.strip()) < MIN_CONTENT_LENGTH:
        return True

    # Проверка на типичные заглушки
    placeholder_markers = [
        "TODO",
        "placeholder",
        "заглушка",
        "coming soon",
        "в разработке",
    ]

    content_lower = content.lower()
    if any(marker in content_lower for marker in placeholder_markers):
        return True

    return False


def check_categories():
    """Проверяет все категории на наличие контента."""
    missing_content = []
    placeholder_content = []
    has_content = []

    # Находим все папки content
    for content_dir in BASE_DIR.rglob("content"):
        if not content_dir.is_dir():
            continue

        category_path = content_dir.parent
        category_name = category_path.relative_to(BASE_DIR)

        # Ищем файл *_ru.md
        md_files = list(content_dir.glob("*_ru.md"))

        if not md_files:
            missing_content.append(str(category_name))
        else:
            # Читаем содержимое файла
            md_file = md_files[0]
            try:
                content = md_file.read_text(encoding="utf-8")

                if is_placeholder_content(content):
                    placeholder_content.append(
                        {"category": str(category_name), "file": md_file.name, "length": len(content.strip())}
                    )
                else:
                    has_content.append(
                        {"category": str(category_name), "file": md_file.name, "length": len(content.strip())}
                    )
            except Exception as e:
                print(f"Ошибка чтения {md_file}: {e}")

    # Выводим результаты
    print("=" * 80)
    print("КАТЕГОРИИ БЕЗ ФАЙЛОВ КОНТЕНТА")
    print("=" * 80)
    if missing_content:
        for cat in sorted(missing_content):
            print(f"  - {cat}")
        print(f"\nВсего: {len(missing_content)}")
    else:
        print("Все категории имеют файлы контента!")

    print("\n" + "=" * 80)
    print("КАТЕГОРИИ С ЗАГЛУШКАМИ (< 500 символов или содержат маркеры)")
    print("=" * 80)
    if placeholder_content:
        for item in sorted(placeholder_content, key=lambda x: x["category"]):
            print(f"  - {item['category']}")
            print(f"    Файл: {item['file']}, Длина: {item['length']} символов")
        print(f"\nВсего: {len(placeholder_content)}")
    else:
        print("Заглушек не найдено!")

    print("\n" + "=" * 80)
    print("КАТЕГОРИИ С КОНТЕНТОМ")
    print("=" * 80)
    if has_content:
        for item in sorted(has_content, key=lambda x: x["category"]):
            print(f"  - {item['category']} ({item['length']} символов)")
        print(f"\nВсего: {len(has_content)}")

    print("\n" + "=" * 80)
    print("ИТОГО")
    print("=" * 80)
    total = len(missing_content) + len(placeholder_content) + len(has_content)
    print(f"Всего категорий: {total}")
    print(f"Без контента: {len(missing_content)}")
    print(f"С заглушками: {len(placeholder_content)}")
    print(f"С контентом: {len(has_content)}")
    print(f"Нужно создать/дополнить: {len(missing_content) + len(placeholder_content)}")


if __name__ == "__main__":
    check_categories()
