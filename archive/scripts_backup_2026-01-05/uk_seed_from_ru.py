#!/usr/bin/env python3
"""
uk_seed_from_ru.py — Hybrid bootstrap for UK *_clean.json from RU source.

Goal: keep UK as a separate version (write-from-scratch), but bootstrap the data model
from RU and let an LLM translate/adapt keywords + H1/main_keyword quickly.

What it does:
- Reads: categories/{slug}/data/{slug}_clean.json (RU)
- Writes: uk/categories/{slug}/data/{slug}_clean.json (UK skeleton) [optional]
- Writes: uk/categories/{slug}/research/KEYWORDS_TRANSLATION_PROMPT.md [optional]
- Prints: an LLM prompt to translate only what needs translating.

This script is intentionally light: translation is performed by an LLM (Claude/ChatGPT),
then the human/LLM pastes results back into the generated UK JSON.
"""

from __future__ import annotations

import argparse
import json
from dataclasses import dataclass
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parent.parent


@dataclass(frozen=True)
class Paths:
    slug: str
    ru_clean_json: Path
    uk_root: Path
    uk_category_root: Path
    uk_clean_json: Path
    uk_prompt_md: Path


def get_paths(slug: str) -> Paths:
    ru_clean_json = ROOT / "categories" / slug / "data" / f"{slug}_clean.json"
    uk_root = ROOT / "uk"
    uk_category_root = uk_root / "categories" / slug
    uk_clean_json = uk_category_root / "data" / f"{slug}_clean.json"
    uk_prompt_md = uk_category_root / "research" / "KEYWORDS_TRANSLATION_PROMPT.md"
    return Paths(
        slug=slug,
        ru_clean_json=ru_clean_json,
        uk_root=uk_root,
        uk_category_root=uk_category_root,
        uk_clean_json=uk_clean_json,
        uk_prompt_md=uk_prompt_md,
    )


def _deepcopy_json(data: Any) -> Any:
    return json.loads(json.dumps(data, ensure_ascii=False))


def build_uk_clean_json(ru: dict[str, Any]) -> dict[str, Any]:
    """
    Build UK skeleton JSON from RU clean.json.

    Keeps the overall schema stable, but:
    - sets language to 'uk'
    - moves seo_titles.{h1,main_keyword} into *_ru fields and blanks the UK fields
    - keeps keywords arrays but adds keyword_ru and blanks keyword for LLM fill-in
    """
    uk = _deepcopy_json(ru)

    uk["language"] = "uk"
    uk["category_name_uk"] = uk.get("category_name_uk") or ""

    seo_titles = uk.get("seo_titles") or {}
    if seo_titles:
        if "h1" in seo_titles and "h1_ru" not in seo_titles:
            seo_titles["h1_ru"] = seo_titles.get("h1", "")
        if "main_keyword" in seo_titles and "main_keyword_ru" not in seo_titles:
            seo_titles["main_keyword_ru"] = seo_titles.get("main_keyword", "")
        seo_titles["h1"] = ""
        seo_titles["main_keyword"] = ""
        seo_titles.setdefault("note", "UK seed: fill h1/main_keyword in Ukrainian; keep *_ru for traceability.")
        # meta is optional; keep, but encourage UK rewrite
        if "meta" in seo_titles and "meta_ru" not in seo_titles:
            seo_titles["meta_ru"] = _deepcopy_json(seo_titles.get("meta", {}))
            seo_titles["meta"] = {
                "title": "",
                "description": "",
                "note": "UK seed: fill Ukrainian meta; do not copy RU blindly.",
            }
    uk["seo_titles"] = seo_titles

    keywords = uk.get("keywords") or {}
    for bucket in ("primary", "secondary", "supporting"):
        items = keywords.get(bucket) or []
        normalized: list[dict[str, Any]] = []
        for item in items:
            if isinstance(item, str):
                normalized.append({"keyword": "", "keyword_ru": item})
                continue
            if isinstance(item, dict):
                entry = _deepcopy_json(item)
                entry.setdefault("keyword_ru", entry.get("keyword", ""))
                entry["keyword"] = ""
                normalized.append(entry)
                continue
            normalized.append({"keyword": "", "keyword_ru": str(item)})
        keywords[bucket] = normalized
    uk["keywords"] = keywords

    # Keep entity_dictionary for structure, but save a RU snapshot for translation decisions.
    entity = uk.get("entity_dictionary") or {}
    if entity and "entity_dictionary_ru" not in uk:
        uk["entity_dictionary_ru"] = _deepcopy_json(entity)
        # Create empty containers of the same shape (lists only), so LLM can fill.
        empty_entity: dict[str, Any] = {}
        for k, v in entity.items():
            empty_entity[k] = [] if isinstance(v, list) else {}
        uk["entity_dictionary"] = empty_entity

    uk.setdefault("content_rules", {})
    uk["content_rules"]["note_uk_seed"] = (
        "UK seed from RU: write Ukrainian content from scratch using translated keywords; "
        "no Latin in headings; category != product label; exact numbers depend on specific product."
    )

    return uk


def build_translation_prompt(slug: str, uk: dict[str, Any]) -> str:
    # seo = uk.get("seo_titles") or {}
    kw = uk.get("keywords") or {}
    primary_ru = [x.get("keyword_ru", "") for x in (kw.get("primary") or []) if isinstance(x, dict)]
    secondary_ru = [x.get("keyword_ru", "") for x in (kw.get("secondary") or []) if isinstance(x, dict)]
    supporting_ru = [x.get("keyword_ru", "") for x in (kw.get("supporting") or []) if isinstance(x, dict)]

    entity_ru = uk.get("entity_dictionary_ru") or {}

    payload = {
        "seo_titles": {
            "h1": "",
            "main_keyword": "",
            "meta": {"title": "", "description": ""},
        },
        "keywords": {
            "primary": [{"keyword_ru": k, "keyword": ""} for k in primary_ru],
            "secondary": [{"keyword_ru": k, "keyword": ""} for k in secondary_ru],
            "supporting": [{"keyword_ru": k, "keyword": ""} for k in supporting_ru],
        },
        "entity_dictionary": entity_ru,
    }

    return (
        "Ти SEO‑копірайтер/детейлер. Задача: підготувати UK‑семантику для категорії.\n"
        f"SLUG: {slug}\n\n"
        "ПРАВИЛА:\n"
        "- НЕ перекладай RU текст. UK контент пишеться з нуля.\n"
        "- Переклади тільки ключі/терміни та запропонуй UK H1 + main_keyword.\n"
        "- H1/H2/H3 ТІЛЬКИ українською (без латиниці).\n"
        "- Англ. терміни можна 1 раз у body як пояснення в дужках, але НЕ в заголовках.\n"
        "- Не вигадуй цифри/пропорції: якщо залежить від товару — діапазон + умови + 'див. етикетку'.\n"
        "- Не додавай бренди/міста/ціни/посилання.\n\n"
        "Вихід: поверни JSON точно у форматі нижче, заповнивши порожні поля.\n\n"
        + json.dumps(payload, ensure_ascii=False, indent=2)
        + "\n"
    )


def read_json(path: Path) -> dict[str, Any]:
    return json.loads(path.read_text(encoding="utf-8"))


def write_json(path: Path, data: dict[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(data, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")


def write_prompt(path: Path, prompt: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(prompt, encoding="utf-8")


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("slug")
    ap.add_argument("--write", action="store_true", help="Write uk *_clean.json + prompt file")
    ap.add_argument("--print-prompt", action="store_true", help="Print prompt to stdout")
    args = ap.parse_args()

    paths = get_paths(args.slug)
    if not paths.ru_clean_json.exists():
        raise SystemExit(f"RU clean.json not found: {paths.ru_clean_json}")

    ru = read_json(paths.ru_clean_json)
    uk = build_uk_clean_json(ru)
    prompt = build_translation_prompt(args.slug, uk)

    if args.write:
        (paths.uk_category_root / "content").mkdir(parents=True, exist_ok=True)
        (paths.uk_category_root / "research").mkdir(parents=True, exist_ok=True)
        write_json(paths.uk_clean_json, uk)
        write_prompt(paths.uk_prompt_md, prompt)

    if args.print_prompt or not args.write:
        print(prompt)

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
