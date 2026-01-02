#!/usr/bin/env python3
"""Валидация украинской версии категории."""

import sys
import json
from pathlib import Path


def validate_uk_category(slug: str) -> int:
    """
    Проверяет UK версию категории.

    Returns:
        0 = PASS, 1 = WARNING, 2 = FAIL
    """
    uk_path = Path(f"uk/categories/{slug}")

    errors = []
    warnings = []

    # 1. Проверить существование папки
    if not uk_path.exists():
        print(f"FAIL: UK папка не существует: {uk_path}")
        return 2

    # 2. Проверить структуру
    required_files = [
        f"data/{slug}_clean.json",
        f"meta/{slug}_meta.json",
        f"content/{slug}_uk.md"
    ]

    for file in required_files:
        if not (uk_path / file).exists():
            errors.append(f"Отсутствует: {file}")

    # 3. Проверить meta.json
    meta_path = uk_path / f"meta/{slug}_meta.json"
    if meta_path.exists():
        try:
            with open(meta_path, 'r', encoding='utf-8') as f:
                meta = json.load(f)

            # Проверить UK поля (новая структура: h1, meta.title, meta.description)
            if not meta.get('h1'):
                errors.append("Пустое поле: h1")
            meta_block = meta.get('meta', {})
            if not meta_block.get('title'):
                errors.append("Пустое поле: meta.title")
            if not meta_block.get('description'):
                errors.append("Пустое поле: meta.description")

            # Проверка на русские слова
            fields_to_check = {
                'h1': meta.get('h1', ''),
                'title': meta_block.get('title', ''),
                'description': meta_block.get('description', '')
            }
            russian_words = ['купить', 'доставка', 'цена', 'недорого']
            for field_name, field_value in fields_to_check.items():
                for word in russian_words:
                    if word in field_value.lower():
                        warnings.append(f"Русское слово в {field_name}: '{word}'")
        except json.JSONDecodeError as e:
            errors.append(f"Невалидный JSON: {e}")

    # 4. Проверить контент
    content_path = uk_path / f"content/{slug}_uk.md"
    if content_path.exists():
        with open(content_path, 'r', encoding='utf-8') as f:
            content = f.read()

        # Русские слова-маркеры
        russian_markers = ['который', 'является', 'поэтому', 'также', 'однако', 'необходимо']
        for marker in russian_markers:
            if marker in content.lower():
                warnings.append(f"Возможно русский текст: '{marker}'")

        # Минимальная длина
        if len(content) < 500:
            warnings.append(f"Контент слишком короткий: {len(content)} chars")

    # Результат
    if errors:
        print(f"FAIL: {len(errors)} ошибок")
        for e in errors:
            print(f"  ✗ {e}")
        return 2
    elif warnings:
        print(f"WARNING: {len(warnings)} предупреждений")
        for w in warnings:
            print(f"  ⚠ {w}")
        return 1
    else:
        print(f"PASS: UK версия {slug} валидна")
        return 0


if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: python3 validate_uk.py {slug}")
        sys.exit(1)

    slug = sys.argv[1]
    sys.exit(validate_uk_category(slug))
