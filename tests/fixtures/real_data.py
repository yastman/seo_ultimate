# tests/fixtures/real_data.py
"""Real data fixtures for smoke and integration tests."""

from pathlib import Path

# Paths to real category data
PROJECT_ROOT = Path(__file__).parent.parent.parent
CATEGORIES_DIR = PROJECT_ROOT / "categories"
UK_CATEGORIES_DIR = PROJECT_ROOT / "uk" / "categories"

# Sample RU categories for testing
SAMPLE_RU_CATEGORIES = [
    "aktivnaya-pena",
    "polirovalnye-pasty",
    "ochistiteli-stekol",
]

# Sample UK categories for testing
SAMPLE_UK_CATEGORIES = [
    "aktivnaya-pena",
    "cherniteli-shin",
]


def get_ru_content_path(slug: str) -> Path:
    """Get path to RU content file."""
    return CATEGORIES_DIR / slug / "content" / f"{slug}_ru.md"


def get_uk_content_path(slug: str) -> Path:
    """Get path to UK content file."""
    return UK_CATEGORIES_DIR / slug / "content" / f"{slug}_uk.md"


def get_ru_meta_path(slug: str) -> Path:
    """Get path to RU meta file."""
    return CATEGORIES_DIR / slug / "meta" / f"{slug}_meta.json"


def get_uk_meta_path(slug: str) -> Path:
    """Get path to UK meta file."""
    return UK_CATEGORIES_DIR / slug / "meta" / f"{slug}_meta.json"


def get_ru_clean_path(slug: str) -> Path:
    """Get path to RU clean JSON file."""
    return CATEGORIES_DIR / slug / "data" / f"{slug}_clean.json"


# Real content samples for unit tests
SAMPLE_RU_MARKDOWN = """---
title: Активная пена
---

# Активная пена для бесконтактной мойки

Активная пена — современное моющее средство для бесконтактной мойки автомобиля.

## Как выбрать активную пену

При выборе активной пены обратите внимание на концентрацию и pH-уровень.

## Как правильно использовать

1. Разведите средство согласно инструкции
2. Нанесите на кузов снизу вверх
3. Подождите 2-3 минуты
4. Смойте водой

## Частые ошибки

Никогда не наносите пену на горячий кузов. Не давайте высохнуть.
"""

SAMPLE_UK_MARKDOWN = """---
title: Активна піна
---

# Активна піна для безконтактної мийки

Активна піна — сучасний миючий засіб для безконтактної мийки автомобіля.

## Як обрати активну піну

При виборі активної піни зверніть увагу на концентрацію та pH-рівень.

## Як правильно використовувати

1. Розведіть засіб згідно з інструкцією
2. Нанесіть на кузов знизу вгору
3. Зачекайте 2-3 хвилини
4. Змийте водою

## Часті помилки

Ніколи не наносьте піну на гарячий кузов. Не давайте висохнути.
"""
