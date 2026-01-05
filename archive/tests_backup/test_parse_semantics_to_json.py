#!/usr/bin/env python3
"""
TDD тесты для parse_semantics_to_json.py

Run:
    pytest tests/test_parse_semantics_to_json.py -v
    python3 -m pytest tests/test_parse_semantics_to_json.py -v
"""

import json
import sys
from pathlib import Path

import pytest

# Add scripts to path
sys.path.insert(0, str(Path(__file__).parent.parent / "scripts"))

from parse_semantics_to_json import (
    L3_TO_SLUG,
    SLUG_TO_L3,
    calculate_density_target,
    calculate_occurrences_target,
    classify_keywords,
    extract_word_roots,
    generate_full_json,
    generate_variations,
    get_tier_targets,
    read_semantics_csv,
)

# =============================================================================
# Test Data Fixtures
# =============================================================================


@pytest.fixture
def sample_keywords():
    """Sample keywords for testing."""
    return [
        {"keyword": "активная пена", "volume": 720},
        {"keyword": "пена для мойки авто", "volume": 1300},
        {"keyword": "купить пену для авто", "volume": 150},
        {"keyword": "бесконтактная пена", "volume": 50},
        {"keyword": "активная пена цена", "volume": 10},
    ]


@pytest.fixture
def temp_csv(tmp_path):
    """Create temporary CSV for testing."""
    csv_content = """Фраза,кол-во,Запросы сред. [GA]
L1: Мойка и Экстерьер,23/338,
L2: Автошампуни,5/59,
L3: Тестовая категория,5,
тестовый keyword один,,500
тестовый keyword два,,100
тестовый keyword три,,50
L3: Другая категория,2,
другой keyword,,200
"""
    csv_path = tmp_path / "test_semantics.csv"
    csv_path.write_text(csv_content, encoding="utf-8")
    return str(csv_path)


# =============================================================================
# Test: Classification
# =============================================================================


class TestClassifyKeywords:
    """Tests for keyword classification by volume."""

    def test_classify_primary(self, sample_keywords):
        """PRIMARY: volume > 500."""
        result = classify_keywords(sample_keywords)
        primary_kws = [kw["keyword"] for kw in result["primary"]]

        assert "пена для мойки авто" in primary_kws  # 1300
        assert "активная пена" in primary_kws  # 720

    def test_classify_secondary(self, sample_keywords):
        """SECONDARY: volume 100-500."""
        result = classify_keywords(sample_keywords)
        secondary_kws = [kw["keyword"] for kw in result["secondary"]]

        assert "купить пену для авто" in secondary_kws  # 150

    def test_classify_supporting(self, sample_keywords):
        """SUPPORTING: volume < 100."""
        result = classify_keywords(sample_keywords)
        supporting_kws = [kw["keyword"] for kw in result["supporting"]]

        assert "бесконтактная пена" in supporting_kws  # 50
        assert "активная пена цена" in supporting_kws  # 10

    def test_classify_sorted_by_volume(self, sample_keywords):
        """Keywords should be sorted by volume descending."""
        result = classify_keywords(sample_keywords)

        # Primary should be sorted: 1300, 720
        volumes = [kw["volume"] for kw in result["primary"]]
        assert volumes == sorted(volumes, reverse=True)

    def test_classify_empty_list(self):
        """Empty list should return empty categories."""
        result = classify_keywords([])

        assert result["primary"] == []
        assert result["secondary"] == []
        assert result["supporting"] == []


# =============================================================================
# Test: Word Roots Extraction
# =============================================================================


class TestExtractWordRoots:
    """Tests for Russian word root extraction."""

    def test_extract_basic_roots(self):
        """Should extract roots from Russian words."""
        roots = extract_word_roots("активная пена для мойки")

        # "активная" -> "активн", "мойки" -> "мойк"
        assert any("актив" in r for r in roots)

    def test_skip_short_words(self):
        """Words < 4 chars should be skipped."""
        roots = extract_word_roots("для в на из")

        assert len(roots) == 0

    def test_preserve_long_roots(self):
        """Roots >= 3 chars should be preserved."""
        roots = extract_word_roots("бесконтактная мойка")

        assert len(roots) > 0
        assert all(len(r) >= 3 for r in roots)


# =============================================================================
# Test: Variations Generation
# =============================================================================


class TestGenerateVariations:
    """Tests for keyword variations generation."""

    def test_exact_includes_keyword(self):
        """exact should include the keyword itself."""
        all_kws = ["активная пена", "пена для авто"]
        variations = generate_variations("активная пена", all_kws)

        assert "активная пена" in variations["exact"]

    def test_exact_finds_similar(self):
        """exact should find similar keywords."""
        all_kws = [
            "активная пена для мойки авто",
            "активная пена для мойки автомобиля",
            "пена для мойки авто",
        ]
        variations = generate_variations("активная пена для мойки авто", all_kws)

        # Should find overlapping keywords
        assert len(variations["exact"]) >= 1

    def test_partial_has_roots(self):
        """partial should have word roots."""
        all_kws = ["активная пена"]
        variations = generate_variations("активная пена", all_kws)

        # Should have at least one root
        assert len(variations["partial"]) > 0

    def test_limits_variations(self):
        """Should limit to 5 exact and 5 partial."""
        all_kws = ["kw" + str(i) for i in range(20)]
        variations = generate_variations("kw1", all_kws)

        assert len(variations["exact"]) <= 5
        assert len(variations["partial"]) <= 5


# =============================================================================
# Test: Density/Occurrences Targets
# =============================================================================


class TestCalculateTargets:
    """Tests for target calculations."""

    def test_density_high_volume(self):
        """High relative volume should get 0.20%."""
        density = calculate_density_target(1000, 5000, "B")  # 20% of total
        assert density == "0.20%"

    def test_density_low_volume(self):
        """Low relative volume should get 0.05%."""
        density = calculate_density_target(10, 5000, "B")  # 0.2% of total
        assert density == "0.05%"

    def test_density_zero_total(self):
        """Zero total should return 0.10%."""
        density = calculate_density_target(100, 0, "B")
        assert density == "0.10%"

    def test_occurrences_high_volume(self):
        """Volume > 1000 should get 5 occurrences."""
        occ = calculate_occurrences_target(1500, "B")
        assert occ == 5

    def test_occurrences_low_volume(self):
        """Volume < 50 should get 1 occurrence."""
        occ = calculate_occurrences_target(30, "B")
        assert occ == 1


# =============================================================================
# Test: Tier Targets
# =============================================================================


class TestTierTargets:
    """Tests for tier-based requirements (now uses adaptive approach).

    Note: get_tier_targets() wraps the deprecated get_tier_requirements()
    which maps tiers to keyword counts for adaptive requirements.

    Mapping:
    - Tier A → 30 keywords (deep) → words 400-600 → chars 2400-3600
    - Tier B → 15 keywords (medium) → words 250-400 → chars 1500-2400
    - Tier C → 5 keywords (shallow) → words 150-250 → chars 900-1500
    """

    def test_tier_a_chars(self):
        """Tier A: deep semantic depth (30 keywords) → 2400-3600 chars."""
        targets = get_tier_targets("A")
        assert targets["char_min"] == 2400
        assert targets["char_max"] == 3600

    def test_tier_b_chars(self):
        """Tier B: medium semantic depth (15 keywords) → 1500-2400 chars."""
        targets = get_tier_targets("B")
        assert targets["char_min"] == 1500
        assert targets["char_max"] == 2400

    def test_tier_c_chars(self):
        """Tier C: shallow semantic depth (5 keywords) → 900-1500 chars."""
        targets = get_tier_targets("C")
        assert targets["char_min"] == 900
        assert targets["char_max"] == 1500

    def test_tier_case_insensitive(self):
        """Tier should be case-insensitive."""
        targets_upper = get_tier_targets("B")
        targets_lower = get_tier_targets("b")
        assert targets_upper == targets_lower

    def test_tier_unknown_defaults_b(self):
        """Unknown tier should default to B (medium)."""
        targets = get_tier_targets("X")
        assert targets["char_min"] == 1500


class TestAdditionalCoverage:
    def test_read_semantics_csv_skips_row_without_phrase_cell(self, tmp_path: Path):
        csv_path = tmp_path / "s.csv"
        csv_path.write_text(
            "Фраза,кол-во,Запросы сред. [GA]\nL3: Категория,,\n,x,100\nkw,,200\n",
            encoding="utf-8",
        )
        categories = read_semantics_csv(str(csv_path))
        assert "Категория" in categories
        assert categories["Категория"] == [{"keyword": "kw", "volume": 200}]

    def test_density_target_ratio_mid_branch(self):
        assert calculate_density_target(9, 100, "B") == "0.15%"

    def test_occurrences_target_volume_mid_branch(self):
        assert calculate_occurrences_target(60, "B") == 2

    def test_generate_full_json_adds_semantic_entities_from_meta_patterns(
        self, tmp_path: Path, monkeypatch
    ):
        slug = "test-slug"
        (tmp_path / "categories" / slug / "competitors").mkdir(parents=True)
        (tmp_path / "categories" / slug / "competitors" / "meta_patterns.json").write_text(
            json.dumps({"h2_themes": ["Очень важная тема"]}, ensure_ascii=False),
            encoding="utf-8",
        )
        monkeypatch.chdir(tmp_path)

        result = generate_full_json(slug, "B", [{"keyword": "k", "volume": 100}])
        assert result["semantic_entities"]
        assert result["semantic_entities"][0]["main"] == "Очень важная тема"

    def test_import_fallback_l3_mapping_and_get_tier_targets(self, monkeypatch):
        import builtins
        import importlib.util
        import types

        scripts_dir = Path(__file__).parent.parent / "scripts"
        path = scripts_dir / "parse_semantics_to_json.py"

        dummy = types.ModuleType("seo_utils")
        dummy.get_tier_requirements = lambda _t="B": {
            "char_min": 1500,
            "char_max": 2400,
            "h2_range": (2, 4),
            "faq_range": (2, 3),
        }
        monkeypatch.setitem(sys.modules, "seo_utils", dummy)

        real_import = builtins.__import__

        def custom_import(name, globals=None, locals=None, fromlist=(), level=0):
            if name == "scripts.seo_utils":
                raise ImportError("forced")
            if name == "seo_utils" and ("L3_TO_SLUG" in fromlist or "SLUG_TO_L3" in fromlist):
                raise ImportError("forced")
            return real_import(name, globals, locals, fromlist, level)

        monkeypatch.setattr(builtins, "__import__", custom_import)

        spec = importlib.util.spec_from_file_location("_psj_fallback_l3", path)
        assert spec
        assert spec.loader
        mod = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(mod)  # type: ignore[union-attr]

        assert mod.L3_TO_SLUG["Активная пена"] == "aktivnaya-pena"
        assert mod.get_tier_targets("B")["char_min"] == 1500

    def test_import_fallback_for_get_tier_requirements_appends_sys_path(self, monkeypatch):
        import builtins
        import importlib.util
        import types

        scripts_dir = Path(__file__).parent.parent / "scripts"
        path = scripts_dir / "parse_semantics_to_json.py"

        dummy = types.ModuleType("seo_utils")
        dummy.get_tier_requirements = lambda _t="B": {
            "char_min": 1500,
            "char_max": 2400,
            "h2_range": (2, 4),
            "faq_range": (2, 3),
        }

        calls = {"n": 0}
        real_import = builtins.__import__

        def custom_import(name, globals=None, locals=None, fromlist=(), level=0):
            if name == "scripts.seo_utils":
                raise ImportError("forced")
            if name == "seo_utils" and ("L3_TO_SLUG" in fromlist or "SLUG_TO_L3" in fromlist):
                raise ImportError("forced")
            if name == "seo_utils" and "get_tier_requirements" in fromlist:
                calls["n"] += 1
                if calls["n"] == 1:
                    raise ImportError("forced-first")
                return dummy
            return real_import(name, globals, locals, fromlist, level)

        monkeypatch.setattr(builtins, "__import__", custom_import)

        spec = importlib.util.spec_from_file_location("_psj_fallback_req", path)
        assert spec
        assert spec.loader
        mod = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(mod)  # type: ignore[union-attr]
        assert mod.get_tier_targets("B")["char_max"] == 2400

    def test_main_guard_sys_path_insert_branch_executes(self, monkeypatch):
        import runpy

        scripts_dir = Path(__file__).parent.parent / "scripts"
        path = scripts_dir / "parse_semantics_to_json.py"

        monkeypatch.setattr(sys, "argv", ["prog"])
        with pytest.raises(SystemExit) as exc:
            runpy.run_path(str(path), run_name="__main__")
        assert exc.value.code == 1


# =============================================================================
# Test: Full JSON Generation
# =============================================================================


class TestGenerateFullJson:
    """Tests for full JSON generation."""

    def test_json_has_required_fields(self, sample_keywords):
        """JSON should have all required fields."""
        result = generate_full_json("test-slug", "B", sample_keywords)

        assert "schema_version" in result
        assert "slug" in result
        assert "tier" in result
        assert "keywords" in result
        assert "content_targets" in result
        assert "stats" in result

    def test_json_keywords_structure(self, sample_keywords):
        """keywords should have primary/secondary/supporting."""
        result = generate_full_json("test-slug", "B", sample_keywords)

        assert "primary" in result["keywords"]
        assert "secondary" in result["keywords"]
        assert "supporting" in result["keywords"]

    def test_json_keyword_object_structure(self, sample_keywords):
        """Each keyword object should have required fields."""
        result = generate_full_json("test-slug", "B", sample_keywords)

        primary = result["keywords"]["primary"]
        if primary:
            kw = primary[0]
            assert "keyword" in kw
            assert "volume" in kw
            assert "variations" in kw
            assert "exact" in kw["variations"]
            assert "partial" in kw["variations"]

    def test_json_stats_correct(self, sample_keywords):
        """stats should match actual counts."""
        result = generate_full_json("test-slug", "B", sample_keywords)

        total = len(sample_keywords)
        assert result["stats"]["total_keywords"] == total

        counted = (
            result["stats"]["primary_count"]
            + result["stats"]["secondary_count"]
            + result["stats"]["supporting_count"]
        )
        assert counted == total


# =============================================================================
# Test: CSV Reading
# =============================================================================


class TestReadSemanticsCSV:
    """Tests for CSV reading."""

    def test_reads_categories(self, temp_csv):
        """Should read L3 categories."""
        categories = read_semantics_csv(temp_csv)

        assert "Тестовая категория" in categories
        assert "Другая категория" in categories

    def test_reads_keywords_with_volume(self, temp_csv):
        """Should read keywords with volumes."""
        categories = read_semantics_csv(temp_csv)

        kws = categories["Тестовая категория"]
        volumes = {kw["keyword"]: kw["volume"] for kw in kws}

        assert volumes["тестовый keyword один"] == 500
        assert volumes["тестовый keyword два"] == 100

    def test_handles_missing_file(self):
        """Should raise error for missing file."""
        with pytest.raises(FileNotFoundError):
            read_semantics_csv("/nonexistent/path.csv")

    def test_unprefixed_boundary_row_ends_l3_block(self, tmp_path):
        """
        Real export may contain unprefixed boundary rows like: 'категория,16,'.
        Those must end the current L3 block to avoid cross-category keyword mixing.
        """
        csv_content = """Фраза,кол-во,Запросы сред. [GA]
L3: Категория 1,2,
kw1,,10
kw2,,10
,,
категория,16,
unrelated,,590
,,
L3: Категория 2,1,
kw3,,10
"""
        csv_path = tmp_path / "boundary.csv"
        csv_path.write_text(csv_content, encoding="utf-8")

        categories = read_semantics_csv(str(csv_path))

        kws_1 = [kw["keyword"] for kw in categories["Категория 1"]]
        assert kws_1 == ["kw1", "kw2"]

    def test_l3_count_parses_ratio(self, tmp_path):
        """
        L3 count may appear as a ratio like '2/5'.
        We now IGNORE the count and collect ALL keywords until the next section.
        """
        csv_content = """Фраза,кол-во,Запросы сред. [GA]
L3: Категория 1,2/5,
kw1,,10
kw2,,10
kw3_should_be_included,,10
L3: Категория 2,1,
kw4,,10
"""
        csv_path = tmp_path / "ratio.csv"
        csv_path.write_text(csv_content, encoding="utf-8")

        categories = read_semantics_csv(str(csv_path))

        kws_1 = [kw["keyword"] for kw in categories["Категория 1"]]
        # Now we expect ALL keywords, not just 2
        assert kws_1 == ["kw1", "kw2", "kw3_should_be_included"]

    def test_empty_rows_inside_l3_do_not_reset_context(self, tmp_path):
        """Empty rows (',,') may appear inside an L3 block and must not drop keywords."""
        csv_content = """Фраза,кол-во,Запросы сред. [GA]
L3: Для ручной мойки,2/5,
,,
SEO-Фильтр: С воском,,
,,
автошампунь для ручной мойки,,390
пена для ручной мойки,,10
"""
        csv_path = tmp_path / "empty_rows_inside_block.csv"
        csv_path.write_text(csv_content, encoding="utf-8")

        categories = read_semantics_csv(str(csv_path))

        kws = [kw["keyword"] for kw in categories["Для ручной мойки"]]
        assert kws == ["автошампунь для ручной мойки", "пена для ручной мойки"]


# =============================================================================
# Test: Slug Mappings
# =============================================================================


class TestSlugMappings:
    """Tests for slug/L3 name mappings."""

    def test_l3_to_slug_complete(self):
        """All expected L3 categories should be mapped."""
        expected = [
            "Активная пена",
            "Для ручной мойки",
            "Очистители стекол",
            "Антимошка",
            "Антибитум",
        ]
        for l3 in expected:
            assert l3 in L3_TO_SLUG

    def test_reverse_mapping_consistent(self):
        """SLUG_TO_L3 should be reverse of L3_TO_SLUG."""
        for l3, slug in L3_TO_SLUG.items():
            assert SLUG_TO_L3[slug] == l3


# =============================================================================
# Test: Edge Cases
# =============================================================================


class TestEdgeCases:
    """Tests for edge cases and error handling."""

    def test_empty_keywords_list(self):
        """Should handle empty keywords list."""
        result = generate_full_json("test", "B", [])

        assert result["stats"]["total_keywords"] == 0
        assert result["keywords"]["primary"] == []

    def test_zero_volume_keyword(self):
        """Should handle keywords with zero volume."""
        kws = [{"keyword": "test", "volume": 0}]
        result = generate_full_json("test", "B", kws)

        # Fallback behavior: ensure we always have at least one PRIMARY keyword
        assert len(result["keywords"]["primary"]) == 1
        assert result["keywords"]["primary"][0]["keyword"] == "test"

    def test_cyrillic_keywords(self):
        """Should handle Cyrillic text correctly."""
        kws = [{"keyword": "активная пена для мойки", "volume": 500}]
        result = generate_full_json("test", "B", kws)

        assert result["keywords"]["secondary"][0]["keyword"] == "активная пена для мойки"


def test_script_standalone_inserts_project_root(monkeypatch):
    import sys as sys_mod
    from pathlib import Path

    script_path = Path(__file__).parent.parent / "scripts" / "parse_semantics_to_json.py"
    monkeypatch.setattr(sys_mod, "argv", ["parse_semantics_to_json.py"])
    monkeypatch.setattr(sys_mod, "path", ["__sentinel__"])

    code = script_path.read_text(encoding="utf-8")
    compiled = compile(code, str(script_path), "exec")
    globals_dict = {"__name__": "__main__", "__package__": None, "__file__": str(script_path)}
    with pytest.raises(SystemExit):
        exec(compiled, globals_dict)  # noqa: S102

    assert sys_mod.path[0] == str(script_path.resolve().parent.parent)


# =============================================================================
# Main
# =============================================================================

if __name__ == "__main__":
    pytest.main([__file__, "-v"])
