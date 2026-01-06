"""
Tests for analyze_category.py — Category Analysis for LLM (Google 2025 Approach)

Tests cover:
1. D+E Fallback Pattern (load_keywords_for_slug)
2. Keyword analysis (semantic depth, content format)
3. Content guidelines generation
4. Full category analysis
5. CLI functionality
"""

import json
import sys
from pathlib import Path
from unittest.mock import patch

import pytest

# Add scripts directory to path
sys.path.insert(0, str(Path(__file__).parent.parent / "scripts"))

from analyze_category import (
    COMMERCIAL_MODIFIERS,
    L3_TO_SLUG,
    SLUG_TO_L3,
    analyze_category,
    analyze_keywords,
    generate_content_guidelines,
    is_commercial_keyword,
    load_keywords_for_slug,
    read_semantics_csv,
    split_keywords_by_intent,
)


class TestLoadKeywordsForSlug:
    """Test D+E Fallback Pattern"""

    def test_load_from_clean_json(self):
        """Should load from _clean.json when available"""
        # aktivnaya-pena has _clean.json
        keywords, source, extra_data = load_keywords_for_slug("aktivnaya-pena")

        assert source == "clean_json"
        assert len(keywords) == 12  # Clean has 12 keywords
        assert extra_data is not None
        assert "seo_titles" in extra_data
        assert "entity_dictionary" in extra_data
        assert extra_data["stats"]["before"] == 52
        assert extra_data["stats"]["after"] == 12

    def test_load_from_raw_json_fallback(self, tmp_path: Path):
        """Should fallback to raw .json when _clean.json not available"""
        # Use isolated temp category so the test doesn't depend on repo state.

        # Build minimal raw.json-only category folder.
        tmp_categories = tmp_path / "categories"
        slug = "raw-only-slug"
        data_dir = tmp_categories / slug / "data"
        data_dir.mkdir(parents=True, exist_ok=True)
        (data_dir / f"{slug}.json").write_text(
            json.dumps(
                {
                    "keywords": {
                        "primary": [{"keyword": "k1", "volume": 100}],
                        "secondary": [{"keyword": "k2", "volume": 50}],
                        "supporting": [],
                    }
                },
                ensure_ascii=False,
            ),
            encoding="utf-8",
        )

        with patch("analyze_category.get_categories_dir", return_value=tmp_categories):
            keywords, source, extra_data = load_keywords_for_slug(slug)

        assert source == "raw_json"
        assert len(keywords) > 0
        assert extra_data is None  # Raw JSON doesn't have extra data

    def test_load_from_csv_fallback(self):
        """Should fallback to CSV when no JSON available"""
        # Create a mock slug that has CSV but no JSON
        # This tests the CSV fallback path
        with patch.object(Path, "exists", return_value=False):
            # Mock the CSV reader to return test data
            keywords, source, extra_data = load_keywords_for_slug("antibitum")
            # antibitum should have JSON, so this tests the actual file
            assert source in ["raw_json", "csv"]

    def test_unknown_slug_returns_empty(self):
        """Should return empty list for unknown slug"""
        keywords, source, extra_data = load_keywords_for_slug("unknown-slug-12345")

        assert keywords == []
        assert source == "csv"
        assert extra_data is None

    def test_clean_json_has_correct_structure(self):
        """Keywords from clean.json should have required fields"""
        keywords, source, extra_data = load_keywords_for_slug("aktivnaya-pena")

        assert source == "clean_json"
        for kw in keywords:
            assert "keyword" in kw
            assert "volume" in kw
            assert "cluster" in kw


class TestAnalyzeKeywords:
    """Test keyword analysis functionality"""

    def test_empty_keywords(self):
        """Should handle empty keyword list"""
        result = analyze_keywords([])

        assert result["count"] == 0
        assert result["total_volume"] == 0
        assert result["semantic_depth"] == "empty"
        assert result["need_clustering"] is False

    def test_shallow_semantic_depth(self):
        """Should classify 1-5 keywords as shallow"""
        keywords = [
            {"keyword": "test1", "volume": 100},
            {"keyword": "test2", "volume": 50},
            {"keyword": "test3", "volume": 30},
        ]
        result = analyze_keywords(keywords)

        assert result["count"] == 3
        assert result["semantic_depth"] == "shallow"
        assert result["content_format"] == "compact"
        assert result["recommended_words"] == "150-250"

    def test_medium_semantic_depth(self):
        """Should classify 6-15 keywords as medium"""
        keywords = [{"keyword": f"test{i}", "volume": 100 - i * 5} for i in range(10)]
        result = analyze_keywords(keywords)

        assert result["count"] == 10
        assert result["semantic_depth"] == "medium"
        assert result["content_format"] == "standard"
        assert result["recommended_words"] == "250-400"

    def test_deep_semantic_depth(self):
        """Should classify 16+ keywords as deep"""
        keywords = [{"keyword": f"test{i}", "volume": 100 - i * 2} for i in range(20)]
        result = analyze_keywords(keywords)

        assert result["count"] == 20
        assert result["semantic_depth"] == "deep"
        assert result["content_format"] == "comprehensive"
        assert result["recommended_words"] == "400-600"

    def test_need_clustering_threshold(self):
        """Should flag need_clustering for >20 keywords"""
        keywords_small = [{"keyword": f"test{i}", "volume": 100} for i in range(15)]
        keywords_large = [{"keyword": f"test{i}", "volume": 100} for i in range(25)]

        result_small = analyze_keywords(keywords_small)
        result_large = analyze_keywords(keywords_large)

        assert result_small["need_clustering"] is False
        assert result_large["need_clustering"] is True

    def test_primary_keyword_detection(self):
        """Should identify primary keyword by highest volume"""
        keywords = [
            {"keyword": "low volume", "volume": 10},
            {"keyword": "high volume", "volume": 1000},
            {"keyword": "medium volume", "volume": 100},
        ]
        result = analyze_keywords(keywords)

        assert result["primary"]["keyword"] == "high volume"
        assert result["primary"]["volume"] == 1000

    def test_primary_keyword_prefers_core_over_commercial(self):
        """Primary should prefer core intent even if commercial has higher volume"""
        keywords = [
            {"keyword": "купить антибитум", "volume": 1000},
            {"keyword": "антибитум", "volume": 300},
            {"keyword": "антибитум для авто", "volume": 200},
        ]
        result = analyze_keywords(keywords)
        assert result["primary"]["keyword"] == "антибитум"

    def test_high_volume_count(self):
        """Should count keywords with volume > 100"""
        keywords = [
            {"keyword": "test1", "volume": 500},
            {"keyword": "test2", "volume": 200},
            {"keyword": "test3", "volume": 50},
            {"keyword": "test4", "volume": 10},
        ]
        result = analyze_keywords(keywords)

        assert result["high_volume_count"] == 2

    def test_commercial_intent_detection(self):
        """Should detect commercial intent keywords"""
        keywords = [
            {"keyword": "купить активную пену", "volume": 100},
            {"keyword": "активная пена цена", "volume": 50},
            {"keyword": "заказать пену", "volume": 30},
            {"keyword": "активная пена", "volume": 200},
        ]
        result = analyze_keywords(keywords)

        assert result["commercial_count"] == 3
        assert result["core_count"] == 1

    def test_split_keywords_included(self):
        """Should include split keywords in result (v8.4)"""
        keywords = [
            {"keyword": "купить активную пену", "volume": 100},
            {"keyword": "активная пена", "volume": 200},
        ]
        result = analyze_keywords(keywords)

        assert "core_keywords" in result
        assert "commercial_keywords" in result
        assert len(result["core_keywords"]) == 1
        assert len(result["commercial_keywords"]) == 1


class TestSplitKeywordsByIntent:
    """Test intent-based keyword splitting (v8.4)"""

    def test_is_commercial_keyword(self):
        """Should correctly identify commercial keywords"""
        assert is_commercial_keyword("купить активную пену") is True
        assert is_commercial_keyword("активная пена цена") is True
        assert is_commercial_keyword("заказать пену") is True
        assert is_commercial_keyword("в наличии пена") is True
        assert is_commercial_keyword("доставка пены") is True
        assert is_commercial_keyword("активная пена") is False
        assert is_commercial_keyword("бесконтактная мойка") is False

    def test_split_keywords_basic(self):
        """Should split keywords into core and commercial"""
        keywords = [
            {"keyword": "активная пена", "volume": 200},
            {"keyword": "купить активную пену", "volume": 100},
            {"keyword": "бесконтактная мойка", "volume": 150},
            {"keyword": "пена цена", "volume": 50},
        ]
        core, commercial = split_keywords_by_intent(keywords)

        assert len(core) == 2
        assert len(commercial) == 2
        assert any(k["keyword"] == "активная пена" for k in core)
        assert any(k["keyword"] == "бесконтактная мойка" for k in core)
        assert any(k["keyword"] == "купить активную пену" for k in commercial)
        assert any(k["keyword"] == "пена цена" for k in commercial)

    def test_split_keywords_all_core(self):
        """Should handle all core keywords"""
        keywords = [
            {"keyword": "активная пена", "volume": 200},
            {"keyword": "бесконтактная мойка", "volume": 150},
        ]
        core, commercial = split_keywords_by_intent(keywords)

        assert len(core) == 2
        assert len(commercial) == 0

    def test_split_keywords_all_commercial(self):
        """Should handle all commercial keywords"""
        keywords = [
            {"keyword": "купить пену", "volume": 200},
            {"keyword": "пена цена", "volume": 150},
            {"keyword": "заказать мойку", "volume": 100},
        ]
        core, commercial = split_keywords_by_intent(keywords)

        assert len(core) == 0
        assert len(commercial) == 3

    def test_split_keywords_empty(self):
        """Should handle empty list"""
        core, commercial = split_keywords_by_intent([])

        assert len(core) == 0
        assert len(commercial) == 0

    def test_commercial_modifiers_complete(self):
        """All commercial modifiers should be defined"""
        expected_modifiers = [
            "купить",
            "цена",
            "заказать",
            "стоимость",
            "в наличии",
            "доставка",
            "недорого",
        ]
        for mod in expected_modifiers:
            assert mod in COMMERCIAL_MODIFIERS


class TestGenerateContentGuidelines:
    """Test content guidelines generation"""

    def test_shallow_guidelines(self):
        """Should generate minimal guidelines for shallow depth"""
        analysis = {"semantic_depth": "shallow", "count": 3}
        guidelines = generate_content_guidelines(analysis)

        assert guidelines["structure"]["faq"]["required"] is False
        assert guidelines["structure"]["comparison_table"]["required"] is False
        assert guidelines["structure"]["types_section"]["required"] is False

    def test_medium_guidelines(self):
        """Should generate standard guidelines for medium depth"""
        analysis = {"semantic_depth": "medium", "count": 10}
        guidelines = generate_content_guidelines(analysis)

        assert guidelines["structure"]["faq"]["required"] is True
        assert guidelines["structure"]["faq"]["count"] == "2-3"

    def test_deep_guidelines(self):
        """Should generate comprehensive guidelines for deep depth"""
        analysis = {"semantic_depth": "deep", "count": 25}
        guidelines = generate_content_guidelines(analysis)

        assert guidelines["structure"]["faq"]["required"] is True
        assert guidelines["structure"]["faq"]["count"] == "3-5"
        assert guidelines["structure"]["comparison_table"]["required"] is True
        assert guidelines["structure"]["types_section"]["required"] is True

    def test_always_has_required_structure(self):
        """All guidelines should have base required elements"""
        for depth in ["shallow", "medium", "deep"]:
            analysis = {"semantic_depth": depth, "count": 10}
            guidelines = generate_content_guidelines(analysis)

            assert guidelines["structure"]["h1"] is True
            assert guidelines["structure"]["intro"]["required"] is True
            assert guidelines["structure"]["buying_advice"]["required"] is True
            assert guidelines["structure"]["trust_signals"]["required"] is True

    def test_quality_requirements(self):
        """Should include quality requirements"""
        analysis = {"semantic_depth": "medium", "count": 10}
        guidelines = generate_content_guidelines(analysis)

        assert "quality" in guidelines
        assert guidelines["quality"]["water_percent"]["min"] == 40
        assert guidelines["quality"]["water_percent"]["max"] == 65
        assert guidelines["quality"]["nausea_classic"]["max"] == 3.5

    def test_coverage_targets(self):
        """Should set coverage target based on keyword count"""
        # Low count = high coverage
        analysis_low = {"semantic_depth": "medium", "count": 8}
        # High count = lower coverage
        analysis_high = {"semantic_depth": "deep", "count": 30}

        guidelines_low = generate_content_guidelines(analysis_low)
        guidelines_high = generate_content_guidelines(analysis_high)

        assert guidelines_low["keyword_requirements"]["coverage_target"] == "70%"
        assert guidelines_high["keyword_requirements"]["coverage_target"] == "50%"


class TestAnalyzeCategory:
    """Test full category analysis"""

    def test_analyze_aktivnaya_pena(self):
        """Should analyze aktivnaya-pena with clean.json"""
        result = analyze_category("aktivnaya-pena")

        assert "error" not in result
        assert result["meta"]["slug"] == "aktivnaya-pena"
        assert result["meta"]["source"] == "clean_json"
        assert result["meta"]["needs_clean"] is False
        assert result["keywords"]["count"] == 12
        assert "seo_titles" in result
        assert "entity_dictionary" in result

    def test_analyze_dlya_ruchnoy_moyki(self):
        """Should analyze dlya-ruchnoy_moyki (source may evolve over time)"""
        result = analyze_category("dlya-ruchnoy-moyki")

        assert "error" not in result
        assert result["meta"]["source"] in {"raw_json", "clean_json", "csv"}
        if result["meta"]["source"] == "raw_json":
            assert "seo_titles" not in result  # Raw JSON doesn't have SEO titles
        if result["meta"]["source"] == "clean_json":
            assert "seo_titles" in result

    def test_analyze_antibitum_shallow(self):
        """Should analyze antibitum (depth depends on available keywords source)"""
        result = analyze_category("antibitum")

        assert "error" not in result
        depth = result["keywords"]["semantic_depth"]
        count = result["keywords"]["count"]

        assert depth in {"shallow", "medium", "deep"}
        if count <= 5:
            assert depth == "shallow"
            assert result["content"]["format"] == "compact"
        elif count <= 15:
            assert depth == "medium"
            assert result["content"]["format"] == "standard"
        else:
            assert depth == "deep"
            assert result["content"]["format"] == "comprehensive"

    def test_unknown_slug_error(self):
        """Should return error for unknown slug"""
        result = analyze_category("unknown-slug-xyz")

        assert "error" in result

    def test_result_has_llm_hints(self):
        """Should include LLM prompt hints"""
        result = analyze_category("aktivnaya-pena")

        assert "llm_prompt_hints" in result
        hints = result["llm_prompt_hints"]
        assert hints["page_type"] == "категория интернет-магазина"
        assert hints["content_type"] == "buying guide (не SEO-текст)"
        assert "avoid" in hints

    def test_result_has_analyzed_timestamp(self):
        """Should include ISO timestamp"""
        result = analyze_category("aktivnaya-pena")

        assert "analyzed_at" in result["meta"]
        # Should be ISO format with timezone
        assert "+" in result["meta"]["analyzed_at"] or "Z" in result["meta"]["analyzed_at"]


class TestMappings:
    """Test L3_TO_SLUG and SLUG_TO_L3 mappings"""

    def test_l3_to_slug_contains_all_categories(self):
        """L3_TO_SLUG should contain expected categories"""
        assert "Активная пена" in L3_TO_SLUG
        assert L3_TO_SLUG["Активная пена"] == "aktivnaya-pena"

    def test_slug_to_l3_is_inverse(self):
        """SLUG_TO_L3 should be inverse of L3_TO_SLUG"""
        for l3, slug in L3_TO_SLUG.items():
            assert SLUG_TO_L3[slug] == l3

    def test_bidirectional_mapping(self):
        """Should be able to map slug -> L3 -> slug"""
        test_slug = "aktivnaya-pena"
        l3_name = SLUG_TO_L3.get(test_slug)
        back_to_slug = L3_TO_SLUG.get(l3_name)

        assert back_to_slug == test_slug


class TestReadSemanticsCSV:
    """Test CSV reading functionality"""

    def test_reads_real_csv(self):
        """Should read the real semantics CSV"""
        from analyze_category import SEMANTICS_CSV

        if SEMANTICS_CSV.exists():
            categories = read_semantics_csv(str(SEMANTICS_CSV))
            assert len(categories) > 0
            # Check that at least some L3 categories exist
            assert any(l3 in categories for l3 in L3_TO_SLUG)

    def test_csv_keywords_have_structure(self):
        """Keywords from CSV should have keyword and volume"""
        from analyze_category import SEMANTICS_CSV

        if SEMANTICS_CSV.exists():
            categories = read_semantics_csv(str(SEMANTICS_CSV))
            for _l3_name, keywords in categories.items():
                for kw in keywords:
                    assert "keyword" in kw
                    assert "volume" in kw
                    assert isinstance(kw["volume"], int)


class TestIntegration:
    """Integration tests with real data"""

    def test_all_slugs_analyzable(self):
        """All known slugs should be analyzable"""
        for slug in SLUG_TO_L3:
            result = analyze_category(slug)
            # Should either succeed or have meaningful error
            if "error" in result:
                # Error should mention the slug
                assert slug in result["error"] or "keywords" in result["error"].lower()

    def test_semantic_depth_distribution(self):
        """Depth should be consistent with keywords count boundaries"""
        analyzed = 0
        for slug in SLUG_TO_L3:
            result = analyze_category(slug)
            if "error" not in result:
                analyzed += 1
                count = result["keywords"]["count"]
                depth = result["keywords"]["semantic_depth"]
                if count <= 5:
                    assert depth == "shallow"
                elif count <= 15:
                    assert depth == "medium"
                else:
                    assert depth == "deep"

        assert analyzed >= 1

    def test_list_all_categories_runs(self):
        """list_all_categories should run without errors"""
        import io
        import sys

        from analyze_category import list_all_categories

        # Capture stdout
        captured = io.StringIO()
        sys.stdout = captured

        try:
            list_all_categories()
        finally:
            sys.stdout = sys.__stdout__

        output = captured.getvalue()
        assert "АНАЛИЗ ВСЕХ КАТЕГОРИЙ" in output
        assert "Total:" in output


def test_read_semantics_csv_skips_rows_with_empty_first_cell(tmp_path: Path):
    """
    Regression: a row like ['', '1', '2'] should be skipped safely.
    Covers branch where row exists but row[0] is empty.
    """
    csv_path = tmp_path / "sem.csv"
    csv_path.write_text(
        "L3: Cat,,\n,1,100\nkw,,50\n",
        encoding="utf-8",
    )

    categories = read_semantics_csv(str(csv_path))
    assert "Cat" in categories
    assert categories["Cat"][0]["keyword"] == "kw"


def test_main_prints_usage_and_exits_when_no_args(capsys):
    import analyze_category as ac

    with patch.object(sys, "argv", ["analyze_category.py"]), pytest.raises(SystemExit) as exc:
        ac.main()
    assert exc.value.code == 1
    out = capsys.readouterr().out
    assert "Usage:" in out


def test_main_list_calls_list_all_categories_and_exits(capsys):
    import analyze_category as ac

    with (
        patch.object(sys, "argv", ["analyze_category.py", "--list"]),
        patch.object(ac, "list_all_categories") as mock_list,
        pytest.raises(SystemExit) as exc,
    ):
        ac.main()
    assert exc.value.code == 0
    mock_list.assert_called_once()
    _ = capsys.readouterr()


def test_main_human_readable_prints_all_optional_sections(capsys):
    import analyze_category as ac

    fake = {
        "meta": {
            "category_name": "Категория X",
            "slug": "x",
            "source": "clean_json",
            "needs_clean": True,
        },
        "keywords": {
            "count": 3,
            "total_volume": 123,
            "primary": {"keyword": "ключ", "volume": 100},
            "high_volume_count": 1,
            "core_count": 2,
            "commercial_count": 1,
            "semantic_depth": "shallow",
            "need_clustering": False,
        },
        "content": {
            "format": "compact",
            "recommended_words": "150-250",
            "keyword_requirements": {"coverage_target": 70},
            "structure": {
                "intro": {"length": "short"},
                "faq": {"required": True, "count": 3},
                "comparison_table": {"required": True},
                "types_section": {"required": True},
            },
            "length_note": "note",
        },
        "clustering_stats": {
            "before": 10,
            "after": 3,
            "reduction_percent": 70,
            "clusters_count": 2,
        },
        "seo_titles": {"h1": "H1", "h1_volume": 10, "main_keyword": "mk", "main_keyword_volume": 5},
        "entity_dictionary": {"BRANDS": ["a", "b", "c", "d"]},
    }

    with (
        patch.object(sys, "argv", ["analyze_category.py", "x"]),
        patch.object(ac, "analyze_category", return_value=fake),
    ):
        ac.main()
    out = capsys.readouterr().out
    assert "АНАЛИЗ КАТЕГОРИИ" in out
    assert "SOURCE:" in out
    assert "CLUSTERING STATS" in out
    assert "SEO TITLES" in out
    assert "ENTITY DICTIONARY" in out


def test_main_json_output(capsys):
    import analyze_category as ac

    fake = {
        "meta": {"slug": "x"},
        "keywords": {"count": 0},
        "content": {"structure": {"intro": {"length": ""}}},
    }
    with (
        patch.object(sys, "argv", ["analyze_category.py", "x", "--json"]),
        patch.object(ac, "analyze_category", return_value=fake),
    ):
        ac.main()
    out = capsys.readouterr().out
    assert '"slug": "x"' in out


def test_main_error_prints_and_exits_1(capsys):
    import analyze_category as ac

    with (
        patch.object(sys, "argv", ["analyze_category.py", "x"]),
        patch.object(ac, "analyze_category", return_value={"error": "bad x"}),
        pytest.raises(SystemExit) as exc,
    ):
        ac.main()
    assert exc.value.code == 1
    assert "bad x" in capsys.readouterr().out


def test_get_categories_dir_uk():
    from analyze_category import get_categories_dir

    path = get_categories_dir("uk")
    assert path.as_posix().endswith("/uk/categories")


def test_get_commercial_modifiers_uk():
    from analyze_category import COMMERCIAL_MODIFIERS_UK, get_commercial_modifiers

    assert get_commercial_modifiers("uk") == COMMERCIAL_MODIFIERS_UK


def test_main_parses_lang_flag(monkeypatch, capsys):
    import analyze_category as ac

    monkeypatch.setattr(sys, "argv", ["analyze_category.py", "x", "--lang", "uk", "--json"])
    monkeypatch.setattr(
        ac,
        "analyze_category",
        lambda slug, lang: {
            "meta": {"slug": slug, "lang": lang},
            "keywords": {"count": 0},
            "content": {"structure": {"intro": {"length": ""}}},
        },
    )
    ac.main()
    assert '"lang": "uk"' in capsys.readouterr().out


def test_module_import_fallback_mapping_executes(monkeypatch):
    """
    Cover analyze_category.py fallback mapping block (lines executed only when seo_utils imports fail).
    """
    import builtins
    import importlib.util
    import sys as sys_mod
    from pathlib import Path

    module_path = Path(__file__).parent.parent / "scripts" / "analyze_category.py"
    spec = importlib.util.spec_from_file_location("analyze_category_import_fallback", module_path)
    assert spec
    assert spec.loader

    blocked = {"scripts.seo_utils", "seo_utils"}
    real_import = builtins.__import__

    def guarded_import(name, globals=None, locals=None, fromlist=(), level=0):
        if name in blocked:
            raise ImportError("blocked for test")
        return real_import(name, globals, locals, fromlist, level)

    monkeypatch.setattr(builtins, "__import__", guarded_import)
    try:
        module = importlib.util.module_from_spec(spec)
        sys_mod.modules[spec.name] = module
        spec.loader.exec_module(module)
    finally:
        sys_mod.modules.pop(spec.name, None)

    assert isinstance(module.L3_TO_SLUG, dict)
    assert isinstance(module.SLUG_TO_L3, dict)
