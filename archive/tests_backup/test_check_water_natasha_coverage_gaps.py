from __future__ import annotations

import builtins
import importlib.util
import sys
import types
from pathlib import Path

import pytest

sys.path.insert(0, str(Path(__file__).parent.parent / "scripts"))


def test_script_standalone_inserts_project_root(monkeypatch):
    script_path = Path(__file__).parent.parent / "scripts" / "check_water_natasha.py"
    monkeypatch.setattr(sys, "argv", ["check_water_natasha.py"])
    monkeypatch.setattr(sys, "path", ["__sentinel__"])

    code = script_path.read_text(encoding="utf-8")
    compiled = compile(code, str(script_path), "exec")
    globals_dict = {"__name__": "__main__", "__package__": None, "__file__": str(script_path)}
    with pytest.raises(SystemExit):
        exec(compiled, globals_dict)  # noqa: S102

    assert sys.path[0] == str(script_path.resolve().parent.parent)


def test_import_error_when_natasha_missing_exits_1(monkeypatch, capsys):
    script_path = Path(__file__).parent.parent / "scripts" / "check_water_natasha.py"
    real_import = builtins.__import__

    def fail_natasha(name, globals=None, locals=None, fromlist=(), level=0):
        if name == "natasha":
            raise ImportError("forced")
        return real_import(name, globals, locals, fromlist, level)

    monkeypatch.setattr(builtins, "__import__", fail_natasha)
    sys.modules.pop("natasha", None)

    spec = importlib.util.spec_from_file_location("_water_no_natasha", script_path)
    assert spec
    assert spec.loader
    mod = importlib.util.module_from_spec(spec)
    with pytest.raises(SystemExit) as exc:
        spec.loader.exec_module(mod)  # type: ignore[union-attr]
    assert exc.value.code == 1
    out = capsys.readouterr().out
    assert "Установите зависимости" in out


def test_partial_natasha_import_sets_natasha_full_false(monkeypatch):
    script_path = Path(__file__).parent.parent / "scripts" / "check_water_natasha.py"

    fake_natasha = types.ModuleType("natasha")

    class Segmenter:  # noqa: D401
        pass

    class MorphVocab:  # noqa: D401
        pass

    class Doc:  # noqa: D401
        def __init__(self, _text: str):
            self.tokens = []

    fake_natasha.Segmenter = Segmenter
    fake_natasha.MorphVocab = MorphVocab
    fake_natasha.Doc = Doc
    # Intentionally omit NewsEmbedding/NewsMorphTagger to make the "full" import fail.

    monkeypatch.setitem(sys.modules, "natasha", fake_natasha)

    spec = importlib.util.spec_from_file_location("_water_partial_natasha", script_path)
    assert spec
    assert spec.loader
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)  # type: ignore[union-attr]

    assert mod.NATASHA_FULL is False


def test_get_nlp_pipeline_sets_morph_tagger_none_when_natasha_basic(monkeypatch):
    import check_water_natasha as mod

    original_full = mod.NATASHA_FULL
    original_cache = dict(mod._NLP_CACHE)
    try:
        mod._NLP_CACHE.clear()
        monkeypatch.setattr(mod, "NATASHA_FULL", False)
        pipeline = mod.get_nlp_pipeline()
        assert pipeline["morph_tagger"] is None
    finally:
        mod._NLP_CACHE.clear()
        mod._NLP_CACHE.update(original_cache)
        mod.NATASHA_FULL = original_full


def test_load_stopwords_uk_uses_uk_dir_fallback(tmp_path: Path, monkeypatch):
    import check_water_natasha as mod

    scripts_dir = tmp_path / "scripts"
    scripts_dir.mkdir(exist_ok=True)
    fake_file = scripts_dir / "check_water_natasha.py"
    fake_file.write_text("# placeholder\n", encoding="utf-8")

    uk_stopwords = tmp_path / "uk" / "data" / "stopwords" / "stopwords-uk.txt"
    uk_stopwords.parent.mkdir(parents=True, exist_ok=True)
    uk_stopwords.write_text("слово1\nслово2\n", encoding="utf-8")

    monkeypatch.setattr(mod, "__file__", str(fake_file))
    stopwords = mod.load_stopwords("uk")
    assert "слово1" in stopwords


def test_load_stopwords_uk_hardcoded_when_stop_words_missing(monkeypatch):
    import check_water_natasha as mod

    monkeypatch.setattr(Path, "exists", lambda _self: False, raising=False)

    real_import = builtins.__import__

    def fail_stop_words(name, globals=None, locals=None, fromlist=(), level=0):
        if name == "stop_words":
            raise ImportError("forced")
        return real_import(name, globals, locals, fromlist, level)

    monkeypatch.setattr(builtins, "__import__", fail_stop_words)

    stopwords = mod.load_stopwords("uk")
    assert "і" in stopwords


def test_calculate_metrics_from_text_uses_token_text_when_lemma_missing(monkeypatch):
    import check_water_natasha as mod

    class FakeToken:
        def __init__(self, text: str):
            self.text = text
            self.pos = "NOUN"
            self.lemma = None

        def lemmatize(self, _morph_vocab):
            self.lemma = None

    class FakeDoc:
        def __init__(self, _text: str):
            self.tokens = [FakeToken("тест")]

        def segment(self, _segmenter):
            return None

        def tag_morph(self, _morph_tagger):
            return None

    monkeypatch.setattr(mod, "Doc", FakeDoc)
    monkeypatch.setattr(mod, "clean_markdown", lambda t: t)
    monkeypatch.setattr(mod, "load_stopwords", lambda _lang="ru": set())
    monkeypatch.setattr(
        mod,
        "get_nlp_pipeline",
        lambda: {"segmenter": object(), "morph_vocab": object(), "morph_tagger": object()},
    )

    metrics = mod.calculate_metrics_from_text("тест", lang="ru")
    assert metrics is not None
    assert metrics["most_common_lemma"] == "тест"
