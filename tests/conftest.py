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


@pytest.fixture
def mock_csv_content():
    return """Level1,Level2,Level3,Keyword,Volume
Мойка,Шампуни,Активная пена,активная пена,1000
Мойка,Шампуни,Активная пена,купить пену,500
"""


@pytest.fixture
def mock_clean_json_data():
    return {
        "slug": "aktivnaya-pena",
        "name": "Активная пена",
        "keywords": [
            {"keyword": "активная пена", "volume": 1000},
            {"keyword": "купить пену", "volume": 500},
        ],
        "meta": {
            "title": "Купить активную пену",
            "description": "Лучшая пена.",
            "h1": "Активная пена",
        },
    }
