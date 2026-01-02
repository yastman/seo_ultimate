"""
Pytest configuration and fixtures for Stage 8.1 Quality Checks

Provides shared fixtures for:
- Test markdown files
- Mock data
- Temporary directories
"""

import pytest
from pathlib import Path
import tempfile
import shutil


@pytest.fixture
def test_data_dir():
    """Returns path to test fixtures directory"""
    return Path(__file__).parent / 'fixtures'


@pytest.fixture
def valid_markdown_file(tmp_path):
    """Creates a valid markdown file for testing"""
    content = """# Тестовая категория

Это тестовый текст для проверки quality checks. Активная пена для мойки автомобилей.

## Преимущества

Активная пена обеспечивает эффективную мойку благодаря активным компонентам.

## FAQ

**Вопрос 1?**
Ответ 1.

**Вопрос 2?**
Ответ 2.
"""
    file_path = tmp_path / "test_valid.md"
    file_path.write_text(content, encoding='utf-8')
    return file_path


@pytest.fixture
def invalid_markdown_file(tmp_path):
    """Creates an invalid markdown file with long lines"""
    content = """# Test

This is a very long line that exceeds the MD013 limit of 80 characters and should trigger a markdown lint warning during testing.
"""
    file_path = tmp_path / "test_invalid.md"
    file_path.write_text(content, encoding='utf-8')
    return file_path


@pytest.fixture
def keyword_test_file(tmp_path):
    """Creates a file for keyword density testing"""
    content = """# Активная пена

Активная пена для мойки автомобилей.
Активная пена эффективна.
Мойка с активной пеной проста.
Активная пена - лучший выбор.

## Преимущества активной пены

Активная пена обеспечивает:
- Эффективную мойку
- Безопасность для покрытия
- Экономичность использования

## FAQ

**Как использовать активную пену?**
Активную пену наносят на поверхность автомобиля перед мойкой.
"""
    file_path = tmp_path / "test_keywords.md"
    file_path.write_text(content, encoding='utf-8')
    return file_path


@pytest.fixture
def russian_text_sample():
    """Sample Russian text for NLP testing"""
    return """
Активная пена для бесконтактной мойки автомобилей представляет собой
концентрированное средство, которое эффективно удаляет загрязнения.
Пена образуется при смешивании с водой в пеногенераторе или минимойке.
"""


@pytest.fixture
def mock_json_data():
    """Mock JSON data for tier-based validation"""
    return {
        "tier": "B",
        "keywords": [
            {"keyword": "активная пена", "exact_target": 0.8, "total_target": 1.5},
            {"keyword": "бесконтактная мойка", "exact_target": 0.3, "total_target": 0.6}
        ],
        "density_limit": 2.0,
        "coverage_target": 70
    }


@pytest.fixture
def temp_output_dir(tmp_path):
    """Temporary directory for output files"""
    output_dir = tmp_path / "output"
    output_dir.mkdir()
    yield output_dir
    # Cleanup after test
    if output_dir.exists():
        shutil.rmtree(output_dir)
