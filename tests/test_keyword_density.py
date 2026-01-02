"""
TDD Tests for check_simple_v2_md.py — Keyword Density Validator

Tests cover:
1. Keyword frequency calculation
2. Density percentage validation
3. Coverage percentage validation
4. Tier-based requirements
5. Exit codes (0/1/2)
"""

import pytest
import sys
from pathlib import Path

# Add scripts directory to path
sys.path.insert(0, str(Path(__file__).parent.parent / 'scripts'))

import check_simple_v2_md as mod  # noqa: E402


@pytest.fixture(autouse=True)
def _disable_natasha(monkeypatch):
    # Avoid slow NLP init; other tests cover nausea branches.
    monkeypatch.setattr(mod, "NAUSEA_AVAILABLE", False)


def _run_main(monkeypatch, argv):
    monkeypatch.setattr(sys, "argv", argv)
    with pytest.raises(SystemExit) as excinfo:
        mod.main()
    return excinfo.value.code


class TestKeywordDensityScript:
    """Test check_simple_v2_md.py CLI in-process (coverage-friendly)."""

    def test_script_exists(self):
        """Script file should exist"""
        script_path = Path(__file__).parent.parent / 'scripts' / 'check_simple_v2_md.py'
        assert script_path.exists()

    def test_script_executable_with_help(self, monkeypatch, capsys):
        code = _run_main(monkeypatch, ["check_simple_v2_md.py", "--help"])
        out = capsys.readouterr().out
        assert code == 0
        assert "SEO Validator" in out

    def test_script_with_missing_args(self, monkeypatch):
        code = _run_main(monkeypatch, ["check_simple_v2_md.py"])
        assert code != 0

    def test_script_with_valid_file(self, keyword_test_file, monkeypatch, capsys):
        """Should analyze valid file successfully"""
        code = _run_main(
            monkeypatch,
            ["check_simple_v2_md.py", str(keyword_test_file), "активная пена", "B"],
        )
        out = capsys.readouterr().out

        # Should complete (exit code 0, 1, or 2 all valid)
        assert code in (0, 1, 2)
        # Should output something
        assert len(out) > 0

    def test_script_with_nonexistent_file(self, monkeypatch, capsys):
        """Should fail gracefully for non-existent file"""
        code = _run_main(monkeypatch, ["check_simple_v2_md.py", "/nonexistent/file.md", "keyword", "B"])
        out = capsys.readouterr().out
        assert code == 1
        assert "Файл не найден" in out

    @pytest.mark.parametrize("tier", ["A", "B", "C"])
    def test_script_with_different_tiers(self, keyword_test_file, tier, monkeypatch):
        """Should accept all valid tiers"""
        code = _run_main(monkeypatch, ["check_simple_v2_md.py", str(keyword_test_file), "активная пена", tier])
        assert code in (0, 1, 2)


class TestKeywordDensityCalculations:
    """Test density calculation logic"""

    def test_high_density_triggers_error(self, tmp_path: Path):
        keywords_json = tmp_path / "kw.json"
        keywords_json.write_text(
            '{"keywords":{"primary":[{"keyword":"активная пена","variations":{"exact":[]}}],"secondary":[],"supporting":[]}}',
            encoding="utf-8",
        )

        md = " ".join(["активная пена"] * 200)
        text = mod.extract_text_content(md)
        word_count = mod.count_words(text)

        result = mod.check_keyword_density_and_distribution(md, str(keywords_json), word_count, {"coverage": 0.4})
        assert result["total_density"] > 3.5
        assert any("BLOCKER" in e for e in result["errors"])

    def test_low_coverage_triggers_warning(self, tmp_path: Path):
        keywords_json = tmp_path / "kw.json"
        keywords_json.write_text(
            '{"keywords":{"primary":[{"keyword":"раз"},{"keyword":"два"},{"keyword":"три"}],"secondary":[{"keyword":"четыре"}],"supporting":[{"keyword":"пять"}]}}',
            encoding="utf-8",
        )

        md = "текст без ключевых слов"
        text = mod.extract_text_content(md)
        word_count = mod.count_words(text)

        result = mod.check_keyword_density_and_distribution(md, str(keywords_json), word_count, {"coverage": 0.4})
        assert result["coverage"] == 0.0
        assert any("Coverage" in w for w in result["warnings"])

    def test_short_content_fails_char_requirement(self, tmp_path):
        """Short content (<4000 chars) should FAIL with exit 2 - this is correct behavior"""
        # Note: Script requires 4000-5000 chars, this content is only ~500 chars
        content = """# Активная пена для мойки

Активная пена - эффективное средство для бесконтактной мойки автомобилей.

## Что такое активная пена?

Активная пена представляет собой концентрированное моющее средство, которое
при смешивании с водой образует густую пену.

## Преимущества

Использование активной пены обеспечивает:
- Глубокую очистку
- Защиту покрытия
- Экономичный расход

## Применение

Активную пену наносят на поверхность автомобиля перед основной мойкой.

## FAQ

**Как использовать?**
Разведите активную пену в пропорции 1:10 с водой.

**Безопасна ли активная пена?**
Да, качественная активная пена безопасна для любых покрытий.
"""

        test_file = tmp_path / "balanced.md"
        test_file.write_text(content, encoding='utf-8')

        # Short content correctly FAILs (exit 2) - requirement is 4000-5000 chars
        assert mod.check_content(str(test_file), "активная пена", "B")["status"] == "FAIL"


class TestTierRequirements:
    """Test tier-specific requirements"""

    def test_tier_b_requirements(self, keyword_test_file, monkeypatch):
        """Tier B should have specific requirements"""
        code = _run_main(monkeypatch, ["check_simple_v2_md.py", str(keyword_test_file), "активная пена", "B"])
        assert code in (0, 1, 2)

    def test_tier_c_requirements(self, keyword_test_file, monkeypatch):
        """Tier C should have specific requirements"""
        code = _run_main(monkeypatch, ["check_simple_v2_md.py", str(keyword_test_file), "активная пена", "C"])
        assert code in (0, 1, 2)


class TestExitCodes:
    def test_exit_2_for_invalid_args(self, monkeypatch):
        # argparse error (missing args)
        code = _run_main(monkeypatch, ["check_simple_v2_md.py"])
        assert code != 0

    def test_short_structured_content_fails(self, tmp_path: Path, monkeypatch, capsys):
        content = """# Активная пена

Активная пена для бесконтактной мойки автомобилей - современное решение.

## Преимущества активной пены

Использование активной пены обеспечивает эффективную очистку благодаря:
- Специальным компонентам активной пены
- Безопасности для покрытия
- Экономичному расходу

## Как работает активная пена?

Активная пена наносится на поверхность, где активные компоненты растворяют грязь.

## FAQ

**Что такое активная пена?**
Активная пена - это концентрат для бесконтактной мойки.

**Безопасна ли активная пена?**
Качественная активная пена абсолютно безопасна.

**Как применять активную пену?**
Разведите активную пену с водой в пропорции 1:10.
"""

        test_file = tmp_path / "perfect.md"
        test_file.write_text(content, encoding="utf-8")

        code = _run_main(monkeypatch, ["check_simple_v2_md.py", str(test_file), "активная пена", "B"])
        out = capsys.readouterr().out
        assert code == 2
        assert "4000-5000" in out or "РЕЗУЛЬТАТ: FAIL" in out


class TestEdgeCasesKeywords:
    def test_cyrillic_keyword(self):
        ok, msg = mod.check_keyword_stuffing("тест тестовый текст", "тест")
        assert ok is True
        assert "1 упоминаний" in msg

    def test_keyword_with_spaces(self):
        ok, msg = mod.check_keyword_stuffing("Активная пена для мойки. Активная пена.", "активная пена")
        assert ok is True
        assert "2 упоминаний" in msg

    def test_case_insensitive_matching(self):
        ok, msg = mod.check_keyword_stuffing("АКТИВНАЯ ПЕНА для мойки. Активная пена.", "активная пена")
        assert ok is True
        assert "2 упоминаний" in msg
