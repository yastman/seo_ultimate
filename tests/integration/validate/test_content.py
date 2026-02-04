"""Integration tests for seo_ultimate.validate.content module."""

from pathlib import Path


class TestCheckStructure:
    """Tests for check_structure function."""

    def test_valid_structure_passes(self, tmp_path: Path):
        """Content with H1, intro, and H2s should pass."""
        from seo_ultimate.validate.content import check_structure

        content = """# Активная пена для авто

Активная пена — это современное средство для бесконтактной мойки автомобиля.
Она эффективно удаляет грязь и дорожную пыль без механического воздействия.
Использование активной пены позволяет сократить время мойки и улучшить результат.

## Как выбрать активную пену

Выбор зависит от типа загрязнений и материала кузова.

## Применение

Разведите концентрат согласно инструкции.
"""
        result = check_structure(content)

        assert result["h1"]["passed"]
        assert result["h1"]["value"] == "Активная пена для авто"
        assert result["intro"]["passed"]
        assert result["h2_count"]["passed"]
        assert result["overall"] == "PASS"

    def test_missing_h1_fails(self, tmp_path: Path):
        """Content without H1 should fail."""
        from seo_ultimate.validate.content import check_structure

        content = """## Раздел без H1

Текст без заголовка первого уровня.
"""
        result = check_structure(content)

        assert not result["h1"]["passed"]
        assert result["overall"] == "FAIL"

    def test_short_intro_fails(self, tmp_path: Path):
        """Content with short intro should fail."""
        from seo_ultimate.validate.content import check_structure

        content = """# Заголовок

Короткое intro.

## Раздел
"""
        result = check_structure(content)

        assert not result["intro"]["passed"]
        assert result["intro"]["words"] < 30


class TestCheckPrimaryKeyword:
    """Tests for check_primary_keyword function."""

    def test_keyword_in_h1_and_intro(self):
        """Keyword found in both H1 and intro should pass."""
        from seo_ultimate.validate.content import check_primary_keyword

        content = """# Активная пена для авто

Активная пена — это современное средство для бесконтактной мойки.
Она эффективно удаляет грязь без механического воздействия.
Использование активной пены позволяет сократить время мойки.

## Как выбрать
"""
        result = check_primary_keyword(content, "активная пена")

        assert result["in_h1"]["passed"]
        assert result["in_intro"]["passed"]
        assert result["overall"] == "PASS"

    def test_keyword_missing_fails(self):
        """Content without keyword should fail."""
        from seo_ultimate.validate.content import check_primary_keyword

        content = """# Моющее средство

Моющее средство для автомобиля. Удаляет грязь и пыль.
Использование позволяет сократить время мойки.

## Как выбрать
"""
        result = check_primary_keyword(content, "активная пена")

        assert not result["in_h1"]["passed"]
        assert result["overall"] == "FAIL"


class TestCheckKeywordCoverage:
    """Tests for check_keyword_coverage function."""

    def test_full_coverage(self):
        """All keywords found should result in high coverage."""
        from seo_ultimate.validate.content import check_keyword_coverage

        content = """
        Активная пена для мойки автомобиля. Бесконтактная мойка позволяет
        быстро очистить кузов. Автошампунь и пена работают вместе.
        """
        keywords = ["активная пена", "бесконтактная мойка", "автошампунь"]

        result = check_keyword_coverage(content, keywords)

        assert result["found"] >= 2
        assert result["coverage_percent"] >= 60

    def test_no_keywords(self):
        """Empty keywords list should pass."""
        from seo_ultimate.validate.content import check_keyword_coverage

        result = check_keyword_coverage("Текст без ключей", [])

        assert result["passed"]
        assert result["total"] == 0


class TestValidateContent:
    """Tests for main validate_content function."""

    def test_valid_content_passes(self, tmp_path: Path):
        """Valid content should pass all checks."""
        from seo_ultimate.validate.content import validate_content

        content_file = tmp_path / "test.md"
        content = """# Активная пена для авто

Активная пена — это современное средство для бесконтактной мойки автомобиля.
Она эффективно удаляет грязь и дорожную пыль без механического воздействия.
Использование активной пены позволяет сократить время мойки и улучшить результат.
Активная пена безопасна для лакокрасочного покрытия.

## Как выбрать активную пену

1. Определите тип загрязнений
2. Выберите концентрацию
3. Проверьте совместимость

## Важно

Никогда не используйте пену на горячем кузове. Расход составляет 50 мл на 1 литр воды.
"""
        content_file.write_text(content, encoding="utf-8")

        result = validate_content(str(content_file), "активная пена", mode="seo")

        assert result["summary"]["overall"] in ["PASS", "WARNING"]
        assert "structure" not in result["summary"]["blockers"]

    def test_missing_file_returns_error(self, tmp_path: Path):
        """Non-existent file should return error."""
        from seo_ultimate.validate.content import validate_content

        result = validate_content("/nonexistent/file.md", "keyword")

        assert "error" in result

    def test_seo_mode_disables_quality(self, tmp_path: Path):
        """SEO mode should skip quality checks."""
        from seo_ultimate.validate.content import validate_content

        content_file = tmp_path / "test.md"
        content = """# Заголовок

Текст контента для проверки режима SEO валидации текста.
Текст должен быть достаточно длинным для прохождения проверок.
Добавляем больше текста чтобы было минимум тридцать слов.

## Раздел
"""
        content_file.write_text(content, encoding="utf-8")

        result = validate_content(str(content_file), "заголовок", mode="seo")

        assert result["checks"]["quality"]["overall"] == "SKIPPED"


class TestCheckContentStandards:
    """Tests for check_content_standards function."""

    def test_safety_block_detected(self):
        """Content with safety section should pass."""
        from seo_ultimate.validate.content import check_content_standards

        content = """# Заголовок

Intro текст.

## Важно

Не используйте на горячем кузове.

1. Шаг первый
2. Шаг второй

Расход: 50 мл на литр.
"""
        result = check_content_standards(content, lang="ru")

        assert result["safety_block"]
        assert result["howto_steps"]
        assert result["evergreen_math"]

    def test_uk_patterns(self):
        """Ukrainian patterns should be detected."""
        from seo_ultimate.validate.content import check_content_standards

        content = """# Заголовок

## Важливо

Ніколи не наносьте на гарячий кузов.

1. Крок перший
2. Крок другий

Витрата: 50 мл на літр.
"""
        result = check_content_standards(content, lang="uk")

        assert result["safety_block"]
        assert result["warnings_present"]
        assert result["evergreen_math"]
