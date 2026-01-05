import sys
from pathlib import Path

import pytest

# Добавляем корень проекта в sys.path, чтобы тесты видели пакет scripts
PROJECT_ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(PROJECT_ROOT))


@pytest.fixture
def sample_text_ru():
    return "Привет, мир! Это тестовый текст."


@pytest.fixture
def sample_text_uk():
    return "Привіт, світ! Це тестовий текст."


@pytest.fixture
def sample_html():
    return "<h1>Title</h1><p>Paragraph</p>"
