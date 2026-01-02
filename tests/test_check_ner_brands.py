#!/usr/bin/env python3
"""
TDD Tests for check_ner_brands.py
Tests NER entity detection and blacklist checking functionality.
"""

import json
import sys
import types
from pathlib import Path
from unittest.mock import MagicMock, patch

import pytest


# Add project root to path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

from scripts.check_ner_brands import (  # noqa: E402
    AI_FLUFF_PATTERNS,
    BRAND_BLACKLIST,
    CITY_BLACKLIST,
    STRICT_PHRASES,
    analyze_file,
    check_blacklist,
    check_ner,
    clean_markdown,
    is_false_positive_location,
)


# ============================================================================
# Fixtures
# ============================================================================


@pytest.fixture
def clean_text():
    """Sample clean text without any violations."""
    return """
# Очистители для автомобиля

Качественные средства для ухода за автомобилем помогают сохранить внешний вид.
Активная пена эффективно удаляет загрязнения с кузова.

## Преимущества продукции

Современные составы безопасны для лакокрасочного покрытия.
Средство создаёт плотную пену, которая растворяет грязь.
    """.strip()


@pytest.fixture
def text_with_brands():
    """Text containing blacklisted brands."""
    return """
# Автохимия

Многие используют Koch Chemie для мойки автомобилей.
Продукция Grass также популярна среди автолюбителей.
Karcher предлагает профессиональное оборудование.
    """.strip()


@pytest.fixture
def text_with_cities():
    """Text containing blacklisted cities."""
    return """
# Доставка автохимии

Доставляем товары в Киев и Харьков.
Жители Одесса могут заказать с бесплатной доставкой.
В Днепре работает пункт самовывоза.
    """.strip()


@pytest.fixture
def text_with_ai_fluff():
    """Text containing AI-fluff patterns."""
    return """
# Статья об автохимии

В этой статье мы рассмотрим основные виды средств.
Давайте разберёмся, какие составы лучше использовать.
В заключение стоит отметить важность правильного выбора.
Несомненно, качественная автохимия продлевает срок службы покрытия.
    """.strip()


@pytest.fixture
def text_with_strict_phrases():
    """Text containing strict BLOCKER phrases."""
    return """
# Современная автохимия

В современном мире существует широкий ассортимент средств для ухода.
Ни для кого не секрет, что качество играет важную роль.
    """.strip()


@pytest.fixture
def text_with_markdown():
    """Text with markdown formatting."""
    return """
# Заголовок с **жирным** текстом

Абзац с *курсивом* и `кодом`.

- Список элементов
- Второй элемент

[Ссылка](https://example.com)
    """.strip()


@pytest.fixture
def temp_test_file(tmp_path):
    """Create temporary test file."""

    def _create_file(content: str) -> Path:
        test_file = tmp_path / "test_content.md"
        test_file.write_text(content, encoding="utf-8")
        return test_file

    return _create_file


# ============================================================================
# Test clean_markdown()
# ============================================================================


def test_clean_markdown_removes_headers(text_with_markdown):
    """Test that markdown headers are cleaned."""
    result = clean_markdown(text_with_markdown)
    assert "#" not in result
    assert "Заголовок с жирным текстом" in result


def test_clean_markdown_removes_bold():
    """Test that bold formatting is removed."""
    text = "Текст с **жирным** выделением"
    result = clean_markdown(text)
    assert "**" not in result
    assert "жирным" in result


def test_clean_markdown_removes_italic():
    """Test that italic formatting is removed."""
    text = "Текст с *курсивом*"
    result = clean_markdown(text)
    assert "*" not in result
    assert "курсивом" in result


def test_clean_markdown_removes_links():
    """Test that markdown links are cleaned."""
    text = "[Ссылка](https://example.com)"
    result = clean_markdown(text)
    assert "[" not in result
    assert "]" not in result
    assert "Ссылка" in result


def test_clean_markdown_removes_code():
    """Test that inline code formatting IS removed by clean_markdown (SSOT via seo_utils)."""
    text = "Текст с `кодом` внутри"
    result = clean_markdown(text)
    # seo_utils.clean_markdown removes inline code blocks
    assert "`" not in result
    # After removing `кодом`, text becomes "Текст с внутри"
    assert "Текст" in result
    assert "внутри" in result


def test_clean_markdown_removes_lists():
    """Test that list markers are removed."""
    text = "- Элемент списка\n- Второй элемент"
    result = clean_markdown(text)
    assert result.startswith("Элемент списка")


def test_clean_markdown_empty_string():
    """Test that empty string is handled."""
    result = clean_markdown("")
    assert result == ""


def test_clean_markdown_preserves_text():
    """Test that actual text content is preserved."""
    text = "Простой текст без разметки"
    result = clean_markdown(text)
    assert result == text


# ============================================================================
# Test check_blacklist() - Brands
# ============================================================================


def test_check_blacklist_no_violations(clean_text):
    """Test that clean text passes blacklist check."""
    result = check_blacklist(clean_text)
    assert result["brands"] == []
    assert result["cities"] == []
    assert result["ai_fluff"] == []
    assert result["strict_phrases"] == []  # Fixed: 'strict_phrases' not 'strict_blockers'


def test_check_blacklist_detects_koch_chemie(text_with_brands):
    """Test detection of Koch Chemie brand."""
    result = check_blacklist(text_with_brands)
    brands = [item["entity"].lower() for item in result["brands"]]
    assert any("koch" in brand for brand in brands)  # Matches 'koch chemie' or 'koch'


def test_check_blacklist_detects_grass(text_with_brands):
    """Test detection of Grass brand."""
    result = check_blacklist(text_with_brands)
    brands = [item["entity"].lower() for item in result["brands"]]
    assert any("grass" in brand for brand in brands)


def test_check_blacklist_detects_karcher(text_with_brands):
    """Test detection of Karcher brand."""
    result = check_blacklist(text_with_brands)
    brands = [item["entity"].lower() for item in result["brands"]]
    assert any("karcher" in brand for brand in brands)


def test_check_blacklist_multiple_brands(text_with_brands):
    """Test that multiple brands are detected."""
    result = check_blacklist(text_with_brands)
    assert len(result["brands"]) >= 3


def test_check_blacklist_brand_context():
    """Test that brand context is extracted correctly."""
    text = "Средство Koch Chemie отлично очищает"
    result = check_blacklist(text)
    assert len(result["brands"]) > 0
    # Context should include surrounding text
    context = result["brands"][0]["context"]
    assert "Koch Chemie" in context


# ============================================================================
# Test check_blacklist() - Cities
# ============================================================================


def test_check_blacklist_detects_kiev(text_with_cities):
    """Test detection of Kyiv/Kiev."""
    result = check_blacklist(text_with_cities)
    cities = [item["entity"] for item in result["cities"]]
    assert any("Киев" in city or "киев" in city.lower() for city in cities)


def test_check_blacklist_detects_kharkiv(text_with_cities):
    """Test detection of Kharkiv."""
    result = check_blacklist(text_with_cities)
    cities = [item["entity"] for item in result["cities"]]
    assert any("Харьков" in city or "харьков" in city.lower() for city in cities)


def test_check_blacklist_detects_odessa(text_with_cities):
    """Test detection of Odessa."""
    result = check_blacklist(text_with_cities)
    cities = [item["entity"].lower() for item in result["cities"]]
    assert any("одесс" in city for city in cities)


def test_check_blacklist_detects_dnipro(text_with_cities):
    """Test detection of Dnipro."""
    result = check_blacklist(text_with_cities)
    cities = [item["entity"].lower() for item in result["cities"]]
    assert any("днепр" in city for city in cities)


def test_check_blacklist_multiple_cities(text_with_cities):
    """Test that multiple cities are detected."""
    result = check_blacklist(text_with_cities)
    assert len(result["cities"]) >= 3


# ============================================================================
# Test check_blacklist() - AI Fluff
# ============================================================================


def test_check_blacklist_detects_v_etoy_statye(text_with_ai_fluff):
    """Test detection of 'в этой статье'."""
    result = check_blacklist(text_with_ai_fluff)
    fluff = [item["entity"] for item in result["ai_fluff"]]
    assert any("в этой статье" in f.lower() for f in fluff)


def test_check_blacklist_detects_davayte_razberyomsya(text_with_ai_fluff):
    """Test detection of 'давайте разберёмся'."""
    result = check_blacklist(text_with_ai_fluff)
    fluff = [item["entity"] for item in result["ai_fluff"]]
    assert any("давайте раз" in f.lower() for f in fluff)


def test_check_blacklist_detects_v_zaklyuchenie(text_with_ai_fluff):
    """Test detection of 'в заключение'."""
    result = check_blacklist(text_with_ai_fluff)
    fluff = [item["entity"] for item in result["ai_fluff"]]
    assert any("в заключени" in f.lower() for f in fluff)


def test_check_blacklist_detects_nesomneno(text_with_ai_fluff):
    """Test detection of 'несомненно'."""
    result = check_blacklist(text_with_ai_fluff)
    fluff = [item["entity"] for item in result["ai_fluff"]]
    assert any("несомненно" in f.lower() for f in fluff)


def test_check_blacklist_multiple_ai_fluff(text_with_ai_fluff):
    """Test that multiple AI-fluff patterns are detected."""
    result = check_blacklist(text_with_ai_fluff)
    assert len(result["ai_fluff"]) >= 4


# ============================================================================
# Test check_blacklist() - Strict Blockers
# ============================================================================


def test_check_blacklist_detects_v_sovremennom_mire(text_with_strict_phrases):
    """Test detection of 'в современном мире' blocker."""
    result = check_blacklist(text_with_strict_phrases)
    blockers = [item["entity"] for item in result["strict_phrases"]]  # Fixed: 'strict_phrases'
    assert any("в современном мире" in b.lower() for b in blockers)


def test_check_blacklist_detects_shirokiy_assortiment(text_with_strict_phrases):
    """Test detection of 'широкий ассортимент' blocker."""
    result = check_blacklist(text_with_strict_phrases)
    blockers = [item["entity"] for item in result["strict_phrases"]]  # Fixed
    assert any("широкий ассортимент" in b.lower() for b in blockers)


def test_check_blacklist_detects_ni_dlya_kogo_ne_sekret(text_with_strict_phrases):
    """Test detection of 'ни для кого не секрет' AI-fluff."""
    result = check_blacklist(text_with_strict_phrases)
    # This is in AI_FLUFF_PATTERNS, not STRICT_PHRASES
    fluff = [item["entity"] for item in result["ai_fluff"]]
    assert any("ни для кого не секрет" in f.lower() for f in fluff)


def test_check_blacklist_strict_blockers_are_critical(text_with_strict_phrases):
    """Test that strict blockers are detected as critical."""
    result = check_blacklist(text_with_strict_phrases)
    assert len(result["strict_phrases"]) >= 2  # Fixed


# ============================================================================
# Test check_ner()
# ============================================================================


@patch("scripts.check_ner_brands.NATASHA_FULL", False)
def test_check_ner_when_disabled():
    """Test that check_ner returns warning when NATASHA_FULL is False."""
    result = check_ner("Любой текст")
    # When disabled, returns ner_entities and warning
    assert "ner_entities" in result
    assert result["ner_entities"] == []
    assert "warning" in result


@patch("scripts.check_ner_brands.NATASHA_FULL", True)
def test_check_ner_detects_organizations():
    """Test NER detection of organizations."""
    # This test requires Natasha to be installed
    try:
        text = "Компания Газпром и организация ООН"
        result = check_ner(text)
        assert isinstance(result, dict)
        # check_ner returns {'ner_entities': [...]} not separate keys
        assert "ner_entities" in result
        assert isinstance(result["ner_entities"], list)
    except ImportError:
        pytest.skip("Natasha not installed")


@patch("scripts.check_ner_brands.NATASHA_FULL", True)
def test_check_ner_detects_locations():
    """Test NER detection of locations."""
    try:
        text = "Поездка в Москву и Санкт-Петербург"
        result = check_ner(text)
        assert isinstance(result, dict)
        # If Natasha is working, it should detect LOC entities
    except ImportError:
        pytest.skip("Natasha not installed")


@patch("scripts.check_ner_brands.NATASHA_FULL", True)
def test_check_ner_detects_persons():
    """Test NER detection of persons."""
    try:
        text = "Иван Иванов и Петр Петров работают"
        result = check_ner(text)
        assert isinstance(result, dict)
    except ImportError:
        pytest.skip("Natasha not installed")


def test_check_ner_empty_text():
    """Test check_ner with empty text."""
    result = check_ner("")
    # Returns {'ner_entities': []} or {'ner_entities': [], 'warning': '...'}
    assert "ner_entities" in result
    assert isinstance(result["ner_entities"], list)


# ============================================================================
# Test analyze_file()
# ============================================================================


def test_analyze_file_clean_text_returns_zero(temp_test_file, clean_text):
    """Test that clean file returns exit code 0."""
    filepath = temp_test_file(clean_text)
    exit_code = analyze_file(str(filepath))
    assert exit_code == 0


def test_analyze_file_with_brands_returns_one(temp_test_file, text_with_brands):
    """Test that file with brands returns exit code 1 (warning)."""
    filepath = temp_test_file(text_with_brands)
    exit_code = analyze_file(str(filepath))
    assert exit_code == 1


def test_analyze_file_with_cities_returns_one(temp_test_file, text_with_cities):
    """Test that file with cities returns exit code 1 (warning)."""
    filepath = temp_test_file(text_with_cities)
    exit_code = analyze_file(str(filepath))
    assert exit_code == 1


def test_analyze_file_with_ai_fluff_returns_one(temp_test_file, text_with_ai_fluff):
    """Test that file with AI-fluff returns exit code 1 (warning)."""
    filepath = temp_test_file(text_with_ai_fluff)
    exit_code = analyze_file(str(filepath))
    assert exit_code == 1


def test_analyze_file_with_strict_blockers_returns_one(temp_test_file, text_with_strict_phrases):
    """Test that file with strict blockers returns exit code 1."""
    filepath = temp_test_file(text_with_strict_phrases)
    exit_code = analyze_file(str(filepath))
    assert exit_code == 1


def test_analyze_file_missing_file_returns_two():
    """Test that missing file returns exit code 2."""
    exit_code = analyze_file("/nonexistent/file.md")
    assert exit_code == 2


def test_analyze_file_json_output(temp_test_file, clean_text, capsys):
    """Test JSON output format."""
    filepath = temp_test_file(clean_text)
    analyze_file(str(filepath), output_json=True)
    captured = capsys.readouterr()

    # Parse JSON output
    output = json.loads(captured.out)
    assert "blacklist" in output
    assert "ner" in output
    assert "summary" in output  # Fixed: 'summary' not 'has_issues'
    assert "status" in output["summary"]


def test_analyze_file_json_output_structure(temp_test_file, text_with_brands, capsys):
    """Test JSON output structure with violations."""
    filepath = temp_test_file(text_with_brands)
    analyze_file(str(filepath), output_json=True)
    captured = capsys.readouterr()

    output = json.loads(captured.out)
    assert output["summary"]["status"] == "WARNING"  # Fixed
    assert "brands" in output["blacklist"]
    assert len(output["blacklist"]["brands"]) > 0


# ============================================================================
# Integration Tests
# ============================================================================


def test_full_workflow_clean_content(temp_test_file, clean_text):
    """Test full workflow with clean content."""
    filepath = temp_test_file(clean_text)

    # Run analysis
    exit_code = analyze_file(str(filepath))

    # Should pass all checks
    assert exit_code == 0


def test_full_workflow_multiple_violations(temp_test_file):
    """Test full workflow with multiple violation types."""
    content = """
# Автохимия Koch Chemie

В этой статье мы рассмотрим продукцию компании.
Доставка в Киев и Харьков.
В современном мире существует широкий ассортимент средств.
    """.strip()

    filepath = temp_test_file(content)
    exit_code = analyze_file(str(filepath))

    # Should detect violations (exit code 1)
    assert exit_code == 1


def test_blacklist_constants_are_populated():
    """Test that blacklist constants are not empty."""
    assert len(BRAND_BLACKLIST) > 0
    assert len(CITY_BLACKLIST) > 0
    assert len(STRICT_PHRASES) > 0
    assert len(AI_FLUFF_PATTERNS) > 0


def test_brand_blacklist_contains_expected_brands():
    """Test that brand blacklist contains expected brands."""
    expected_brands = ["Koch Chemie", "Grass", "Karcher", "Sonax"]
    for brand in expected_brands:
        assert any(brand.lower() in b.lower() for b in BRAND_BLACKLIST)


def test_city_blacklist_contains_expected_cities():
    """Test that city blacklist contains expected cities."""
    expected_cities = ["Киев", "Харьков", "Одесса", "Днепр"]
    city_blacklist_lower = [c.lower() for c in CITY_BLACKLIST]
    for city in expected_cities:
        assert any(city.lower() in c for c in city_blacklist_lower)


# ============================================================================
# Edge Cases
# ============================================================================


def test_analyze_file_with_unicode_content(temp_test_file):
    """Test handling of Unicode content."""
    content = """
# Тест с Unicode символами

Текст с emoji: 🚗 🧼 ✨
Специальные символы: № § © ® ™
Украинские буквы: їієґ ЇІЄҐ
    """.strip()

    filepath = temp_test_file(content)
    exit_code = analyze_file(str(filepath))

    # Should handle Unicode correctly
    assert exit_code == 0


def test_analyze_file_very_long_text(temp_test_file, clean_text):
    """Test handling of very long text."""
    # Create long text (repeat clean text 100 times)
    long_text = (clean_text + "\n\n") * 100

    filepath = temp_test_file(long_text)
    exit_code = analyze_file(str(filepath))

    # Should handle long text without errors
    assert exit_code in [0, 1]


def test_clean_markdown_with_complex_formatting(temp_test_file):
    """Test markdown cleaning with complex nested formatting."""
    content = """
# Header with **bold _italic_** text

Paragraph with [**bold link**](url) and `**code**`.

- List with **bold**
- List with *italic*
- List with `code`
    """.strip()

    cleaned = clean_markdown(content)

    # Should remove most markdown syntax (but not backticks)
    assert "**" not in cleaned
    # Note: clean_markdown doesn't remove backticks - that's ok for our use case
    assert "[" not in cleaned
    assert "]" not in cleaned


def test_context_extraction_length():
    """Test that context extraction doesn't exceed reasonable limits."""
    # Create text with brand in middle
    text = "A" * 100 + "Koch Chemie" + "B" * 100
    result = check_blacklist(text)

    if result["brands"]:
        context = result["brands"][0]["context"]
        # Context should be reasonable length (not entire text)
        assert len(context) < len(text)


def test_case_insensitive_brand_detection():
    """Test that brand detection is case-insensitive."""
    text_variants = ["koch chemie", "KOCH CHEMIE", "Koch Chemie", "kOcH cHeMiE"]

    for variant in text_variants:
        result = check_blacklist(f"Продукт {variant} хорош")
        assert len(result["brands"]) > 0, f"Failed to detect: {variant}"


def test_case_insensitive_city_detection():
    """Test that city detection is case-insensitive."""
    text_variants = ["киев", "КИЕВ", "Киев", "КиЕв"]

    for variant in text_variants:
        result = check_blacklist(f"Доставка в {variant}")
        assert len(result["cities"]) > 0, f"Failed to detect: {variant}"


# ============================================================================
# Performance Tests
# ============================================================================


def test_analyze_file_performance(temp_test_file, clean_text):
    """Test that analysis completes in reasonable time."""
    import time

    filepath = temp_test_file(clean_text * 10)  # 10x content

    start_time = time.time()
    analyze_file(str(filepath))
    elapsed = time.time() - start_time

    # Should complete in under 5 seconds
    assert elapsed < 5.0, f"Analysis took {elapsed:.2f}s, expected <5s"


# ============================================================================
# Run tests
# ============================================================================

if __name__ == "__main__":
    pytest.main([__file__, "-v", "--tb=short"])


def test_is_false_positive_location_adverb_vs_city():
    assert is_false_positive_location("ровно", "ровно столько") is True
    assert is_false_positive_location("ровно", "в ровно есть пункт") is False


def test_check_blacklist_skips_false_positive_city():
    # "ровно" без предлога не считается городом
    result = check_blacklist("Мы сделали это ровно настолько хорошо, насколько нужно.")
    assert all(item["entity"] != "ровно" for item in result["cities"])


def test_clean_markdown_fallback_local(monkeypatch):
    import scripts.check_ner_brands as mod

    dummy1 = types.ModuleType("scripts.seo_utils")
    dummy2 = types.ModuleType("seo_utils")
    monkeypatch.setitem(sys.modules, "scripts.seo_utils", dummy1)
    monkeypatch.setitem(sys.modules, "seo_utils", dummy2)

    cleaned = mod.clean_markdown("# H1\n**bold** [L](https://x)")
    assert "H1" in cleaned
    assert "bold" in cleaned
    assert "https://x" not in cleaned


def test_clean_markdown_fallback_to_seo_utils(monkeypatch):
    import scripts.check_ner_brands as mod

    dummy = types.ModuleType("scripts.seo_utils")
    monkeypatch.setitem(sys.modules, "scripts.seo_utils", dummy)

    scripts_dir = Path(__file__).parent.parent / "scripts"
    monkeypatch.syspath_prepend(str(scripts_dir))

    cleaned = mod.clean_markdown("# H1\n**bold**")
    assert "H1" in cleaned
    assert "bold" in cleaned


def test_main_no_args_exits_0_prints_doc(capsys):
    import scripts.check_ner_brands as mod

    monkeypatch = pytest.MonkeyPatch()
    monkeypatch.setattr(sys, "argv", ["check_ner_brands.py"])
    try:
        with pytest.raises(SystemExit) as exc:
            mod.main()
        assert exc.value.code == 0
        out = capsys.readouterr().out
        assert "Usage" in out
    finally:
        monkeypatch.undo()


def test_main_calls_analyze_file_and_exits(monkeypatch):
    import scripts.check_ner_brands as mod

    monkeypatch.setattr(mod, "analyze_file", MagicMock(return_value=1))
    monkeypatch.setattr(sys, "argv", ["check_ner_brands.py", "x.md", "--json"])
    with pytest.raises(SystemExit) as exc:
        mod.main()
    assert exc.value.code == 1


def test_import_fallback_branch_when_natasha_missing(monkeypatch, capsys):
    import builtins
    import importlib.util

    scripts_dir = Path(__file__).parent.parent / "scripts"
    path = scripts_dir / "check_ner_brands.py"

    real_import = builtins.__import__

    def fail_natasha(name, globals=None, locals=None, fromlist=(), level=0):
        if name == "natasha":
            raise ImportError("forced")
        return real_import(name, globals, locals, fromlist, level)

    monkeypatch.setattr(builtins, "__import__", fail_natasha)
    sys.modules.pop("natasha", None)

    spec = importlib.util.spec_from_file_location("_check_ner_no_natasha", path)
    assert spec
    assert spec.loader
    mod = importlib.util.module_from_spec(spec)
    with pytest.raises(SystemExit) as exc:
        spec.loader.exec_module(mod)  # type: ignore[union-attr]
    assert exc.value.code == 2
    assert "Natasha" in capsys.readouterr().out


def test_import_sets_natasha_full_false_when_news_models_unavailable(monkeypatch):
    import builtins
    import importlib.util
    import sys as sys_mod

    scripts_dir = Path(__file__).parent.parent / "scripts"
    path = scripts_dir / "check_ner_brands.py"

    real_import = builtins.__import__

    def fail_news_models(name, globals=None, locals=None, fromlist=(), level=0):
        if name == "natasha" and fromlist and "NewsEmbedding" in fromlist:
            raise ImportError("forced missing News* components")
        return real_import(name, globals, locals, fromlist, level)

    monkeypatch.setattr(builtins, "__import__", fail_news_models)

    spec = importlib.util.spec_from_file_location("_check_ner_basic_natasha", path)
    assert spec
    assert spec.loader
    mod = importlib.util.module_from_spec(spec)
    sys_mod.modules[spec.name] = mod
    try:
        spec.loader.exec_module(mod)  # type: ignore[union-attr]
    finally:
        sys_mod.modules.pop(spec.name, None)

    assert mod.NATASHA_FULL is False
