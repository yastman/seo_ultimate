"""Public packaging and repository hygiene checks."""

import tomllib
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parents[2]


def test_console_scripts_expose_fixture_runnable_tools() -> None:
    """Public package metadata should expose the documented CLI tools."""
    pyproject = tomllib.loads((PROJECT_ROOT / "pyproject.toml").read_text(encoding="utf-8"))

    scripts = pyproject["project"]["scripts"]

    assert scripts == {
        "llm-keywords-check-seo": "llm_keywords_pipeline.validate.seo:main",
        "llm-keywords-density": "llm_keywords_pipeline.validate.density:main",
        "llm-keywords-audit-brands": "llm_keywords_pipeline.audit.ner_brands:main",
        "llm-keywords-audit-water": "llm_keywords_pipeline.audit.water:main",
    }


def test_internal_superpowers_notes_are_not_tracked_public_docs() -> None:
    """Internal agent plans should not ship as public project documentation."""
    assert not (PROJECT_ROOT / "docs" / "superpowers").exists()


def test_source_tree_does_not_ship_machine_specific_paths() -> None:
    """Source files should not contain local workstation paths or private hostnames."""
    forbidden = ("C:/Users/", r"c:\Users", "/home/", "Ultimate.net.ua")

    hits = []
    for path in (PROJECT_ROOT / "src").rglob("*.py"):
        text = path.read_text(encoding="utf-8")
        if any(pattern in text for pattern in forbidden):
            hits.append(path.relative_to(PROJECT_ROOT).as_posix())

    assert hits == []


def test_package_does_not_advertise_typed_api_until_mypy_is_green() -> None:
    """Do not ship a PEP 561 marker before the exported package is typed."""
    assert not (PROJECT_ROOT / "src" / "llm_keywords_pipeline" / "py.typed").exists()
