from __future__ import annotations

import builtins
import importlib.util
import sys
import types
from pathlib import Path

import scripts.seo_utils as su


def test_import_fallback_from_config_module(monkeypatch):
    module_path = Path(__file__).parent.parent / "scripts" / "seo_utils.py"
    spec = importlib.util.spec_from_file_location("seo_utils_import_fallback", module_path)
    assert spec
    assert spec.loader

    dummy = types.ModuleType("config")
    dummy.QUALITY_THRESHOLDS = {"x": 1}
    dummy.COMMERCIAL_MODIFIERS = ["купить"]
    dummy.L3_TO_SLUG = {"A": "a"}
    dummy.SLUG_TO_L3 = {"a": "A"}
    monkeypatch.setitem(sys.modules, "config", dummy)

    real_import = builtins.__import__

    def fail_scripts_config(name, globals=None, locals=None, fromlist=(), level=0):
        if name == "scripts.config":
            raise ImportError("forced")
        return real_import(name, globals, locals, fromlist, level)

    monkeypatch.setattr(builtins, "__import__", fail_scripts_config)

    mod = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = mod
    try:
        spec.loader.exec_module(mod)  # type: ignore[union-attr]
    finally:
        sys.modules.pop(spec.name, None)

    assert mod.QUALITY_THRESHOLDS == {"x": 1}


def test_language_specific_helpers_cover_uk_branches():
    l3_to_slug, slug_to_l3 = su.get_mappings_for_lang("uk")
    assert "Активна піна" in l3_to_slug
    assert slug_to_l3[l3_to_slug["Активна піна"]] == "Активна піна"

    assert "купити" in su.get_commercial_modifiers("uk")


def test_get_commercial_modifiers_default_returns_ru_list():
    assert su.get_commercial_modifiers("ru") == su.COMMERCIAL_MODIFIERS


def test_slugify_replaces_special_chars_with_spaces():
    assert su.slugify("test!@#$%") == "test"


def test_get_l3_slug_uses_static_mapping():
    assert su.get_l3_slug("Активная пена") == "aktivnaya-pena"


def test_get_l3_slug_dynamic_generation_for_unknown_name():
    assert su.get_l3_slug("Тест Категория") == "test-kategoriya"


def test_get_l3_name_returns_none_when_missing():
    assert su.get_l3_name("missing") is None


def test_check_url_accessibility_generic_exception_returns_false(monkeypatch):
    monkeypatch.setattr(
        su.requests, "head", lambda *_a, **_k: (_ for _ in ()).throw(RuntimeError("boom"))
    )
    assert su.check_url_accessibility("https://example.com") is False


def test_check_url_accessibility_returns_false_when_no_retries():
    assert su.check_url_accessibility("https://example.com", max_retries=0) is False


def test_get_protected_zones_intro_else_branch():
    md = "# H1\nintro line\n## H2\ntext\n"
    zones = su.get_protected_zones(md)
    assert zones["intro"]


def test_is_blacklisted_domain_exception_returns_false():
    assert su.is_blacklisted_domain(None) is False  # type: ignore[arg-type]


def test_fix_ua_in_url_endswith_branch():
    assert su.fix_ua_in_url("https://x.com/ua") == "https://x.com/ru"


def test_is_category_page_short_path_branch():
    ok, reason = su.is_category_page("https://x.com/ru/pena/aktivnaya")
    assert ok is True
    assert "Short path" in reason
