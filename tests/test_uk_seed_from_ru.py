import json
from pathlib import Path

import pytest


def _import_module():
    # Local import to avoid accidental side-effects when tests are collected.
    import sys
    from pathlib import Path as _Path
    sys.path.insert(0, str((_Path(__file__).parent.parent / "scripts").resolve()))
    import uk_seed_from_ru as m  # type: ignore
    return m


def test_build_uk_clean_json_seeds_language_and_seo_titles():
    m = _import_module()
    ru = {
        "slug": "x",
        "language": "ru",
        "category_name_ru": "Категория",
        "seo_titles": {"h1": "H1 RU", "main_keyword": "ключ"},
        "keywords": {
            "primary": [{"keyword": "ключ", "volume": 10, "cluster": "main"}],
            "secondary": [{"keyword": "вторичный"}],
            "supporting": ["строкой"],
        },
        "entity_dictionary": {"equipment": ["пенокомплект"], "time": ["2-3 минуты"]},
    }
    uk = m.build_uk_clean_json(ru)
    assert uk["language"] == "uk"
    assert uk["seo_titles"]["h1"] == ""
    assert uk["seo_titles"]["main_keyword"] == ""
    assert uk["seo_titles"]["h1_ru"] == "H1 RU"
    assert uk["seo_titles"]["main_keyword_ru"] == "ключ"

    assert uk["keywords"]["primary"][0]["keyword"] == ""
    assert uk["keywords"]["primary"][0]["keyword_ru"] == "ключ"
    assert uk["keywords"]["primary"][0]["volume"] == 10

    assert uk["keywords"]["secondary"][0]["keyword"] == ""
    assert uk["keywords"]["secondary"][0]["keyword_ru"] == "вторичный"

    assert uk["keywords"]["supporting"][0]["keyword"] == ""
    assert uk["keywords"]["supporting"][0]["keyword_ru"] == "строкой"

    assert "entity_dictionary_ru" in uk
    assert uk["entity_dictionary_ru"]["equipment"] == ["пенокомплект"]
    assert uk["entity_dictionary"]["equipment"] == []


def test_build_translation_prompt_contains_payload_json():
    m = _import_module()
    ru = {
        "slug": "x",
        "language": "ru",
        "seo_titles": {"h1": "H1 RU", "main_keyword": "ключ"},
        "keywords": {"primary": [{"keyword": "ключ"}], "secondary": [], "supporting": []},
        "entity_dictionary": {"equipment": ["пенокомплект"]},
    }
    uk = m.build_uk_clean_json(ru)
    prompt = m.build_translation_prompt("x", uk)
    assert "SLUG: x" in prompt
    assert "H1/H2/H3 ТІЛЬКИ українською" in prompt
    assert "\"keyword_ru\": \"ключ\"" in prompt
    # Must contain a parseable JSON payload at the end (multi-line).
    # Don't use rfind("{") because JSON contains nested objects.
    marker = "Вихід: поверни JSON точно у форматі нижче, заповнивши порожні поля."
    assert marker in prompt
    tail = prompt.split(marker, 1)[1]
    start = tail.find("{")
    assert start != -1
    payload_str = tail[start:].strip()
    json.loads(payload_str)

def test_build_uk_clean_json_seeds_meta_ru_and_clears_meta():
    m = _import_module()
    ru = {
        "slug": "x",
        "language": "ru",
        "seo_titles": {
            "h1": "H1 RU",
            "main_keyword": "ключ",
            "meta": {"title": "RU title", "description": "RU desc"},
        },
        "keywords": {"primary": [], "secondary": [], "supporting": []},
    }
    uk = m.build_uk_clean_json(ru)
    assert uk["seo_titles"]["meta_ru"]["title"] == "RU title"
    assert uk["seo_titles"]["meta"]["title"] == ""
    assert "note" in uk["seo_titles"]["meta"]


def test_build_uk_clean_json_normalizes_non_string_keyword_items():
    m = _import_module()
    ru = {
        "slug": "x",
        "language": "ru",
        "seo_titles": {"h1": "H1 RU", "main_keyword": "ключ"},
        "keywords": {"primary": [123], "secondary": [], "supporting": []},
    }
    uk = m.build_uk_clean_json(ru)
    assert uk["keywords"]["primary"][0]["keyword"] == ""
    assert uk["keywords"]["primary"][0]["keyword_ru"] == "123"


def test_main_happy_path_writes_and_prints_prompt(tmp_path, monkeypatch, capsys):
    m = _import_module()
    monkeypatch.setattr(m, "ROOT", tmp_path)
    slug = "demo"
    ru_path = tmp_path / "categories" / slug / "data" / f"{slug}_clean.json"
    ru_path.parent.mkdir(parents=True, exist_ok=True)
    ru_path.write_text(
        json.dumps(
            {
                "slug": slug,
                "language": "ru",
                "seo_titles": {"h1": "H1 RU", "main_keyword": "ключ"},
                "keywords": {"primary": [{"keyword": "ключ"}], "secondary": [], "supporting": []},
            },
            ensure_ascii=False,
        ),
        encoding="utf-8",
    )

    import sys

    monkeypatch.setattr(sys, "argv", ["prog", slug, "--write", "--print-prompt"])
    rc = m.main()
    assert rc == 0
    out = capsys.readouterr().out
    assert "SLUG: demo" in out

    paths = m.get_paths(slug)
    assert paths.uk_clean_json.exists()
    assert paths.uk_prompt_md.exists()


def test_main_errors_when_ru_missing(tmp_path, monkeypatch):
    m = _import_module()
    monkeypatch.setattr(m, "ROOT", tmp_path)
    import sys

    monkeypatch.setattr(sys, "argv", ["prog", "missing"])
    with pytest.raises(SystemExit):
        m.main()


def test_script_writes_files(tmp_path, monkeypatch):
    m = _import_module()
    # Redirect ROOT to tmp
    monkeypatch.setattr(m, "ROOT", tmp_path)
    slug = "demo"
    ru_path = tmp_path / "categories" / slug / "data" / f"{slug}_clean.json"
    ru_path.parent.mkdir(parents=True, exist_ok=True)
    ru_path.write_text(json.dumps({
        "slug": slug,
        "language": "ru",
        "seo_titles": {"h1": "H1 RU", "main_keyword": "ключ"},
        "keywords": {"primary": [{"keyword": "ключ"}], "secondary": [], "supporting": []},
        "entity_dictionary": {"equipment": ["пенокомплект"]},
    }, ensure_ascii=False), encoding="utf-8")

    paths = m.get_paths(slug)
    ru = m.read_json(paths.ru_clean_json)
    uk = m.build_uk_clean_json(ru)
    prompt = m.build_translation_prompt(slug, uk)

    m.write_json(paths.uk_clean_json, uk)
    m.write_prompt(paths.uk_prompt_md, prompt)

    assert paths.uk_clean_json.exists()
    assert paths.uk_prompt_md.exists()
    assert "SLUG: demo" in paths.uk_prompt_md.read_text(encoding="utf-8")
