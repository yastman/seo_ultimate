#!/usr/bin/env python3
"""
export_uk_category_texts.py — Export Ukrainian category content to a single CSV.

Reads:
  - uk/categories/{slug}/data/{slug}_clean.json
  - uk/categories/{slug}/content/{slug}_uk.md

Writes:
  - uk/data/output/uk_category_texts.csv (by default)
"""

from __future__ import annotations

import argparse
import csv
import json
from pathlib import Path
from typing import Dict, Iterable, List, Optional


ROOT = Path(__file__).resolve().parent.parent
SEMANTICS_CSV = ROOT / "data" / "Структура  Ultimate финал - Лист2.csv"
UK_CATEGORIES_DIR = ROOT / "uk" / "categories"


def _load_json(path: Path) -> Dict:
    return json.loads(path.read_text(encoding="utf-8"))


def _read_text(path: Path) -> str:
    return path.read_text(encoding="utf-8").strip() + "\n"


def _slugify_l3(l3_name: str) -> str:
    try:
        from scripts.seo_utils import L3_TO_SLUG, slugify  # type: ignore
    except Exception:  # pragma: no cover
        from seo_utils import L3_TO_SLUG, slugify  # type: ignore

    return L3_TO_SLUG.get(l3_name) or slugify(l3_name)


def iter_slugs_from_semantics_csv(csv_path: Path) -> Iterable[str]:
    if not csv_path.exists():
        return

    with csv_path.open("r", encoding="utf-8", newline="") as f:
        reader = csv.reader(f)
        for row in reader:
            if not row:
                continue
            phrase = (row[0] or "").strip()
            if phrase.startswith("L3:"):
                l3 = phrase.replace("L3:", "").strip()
                if l3:
                    yield _slugify_l3(l3)


def get_slugs_in_order() -> List[str]:
    slugs: List[str] = []
    seen = set()

    for slug in iter_slugs_from_semantics_csv(SEMANTICS_CSV):
        if slug in seen:
            continue
        if (UK_CATEGORIES_DIR / slug).is_dir():
            slugs.append(slug)
            seen.add(slug)

    # Fallback: whatever exists on disk.
    if not slugs:
        for p in sorted(UK_CATEGORIES_DIR.glob("*")):
            if p.is_dir():
                slugs.append(p.name)

    return slugs


def build_rows(slugs: List[str]) -> List[Dict[str, str]]:
    rows: List[Dict[str, str]] = []
    for slug in slugs:
        json_path = UK_CATEGORIES_DIR / slug / "data" / f"{slug}_clean.json"
        md_path = UK_CATEGORIES_DIR / slug / "content" / f"{slug}_uk.md"

        if not json_path.exists():
            raise SystemExit(f"Missing JSON: {json_path}")
        if not md_path.exists():
            raise SystemExit(f"Missing content: {md_path}")

        data = _load_json(json_path)
        seo = data.get("seo_titles") or {}
        meta = seo.get("meta") or {}

        rows.append(
            {
                "slug": slug,
                "language": (data.get("language") or "uk"),
                "category_name_uk": (data.get("category_name_uk") or ""),
                "h1": (seo.get("h1") or ""),
                "main_keyword": (seo.get("main_keyword") or ""),
                "meta_title": (meta.get("title") or ""),
                "meta_description": (meta.get("description") or ""),
                "text_md": _read_text(md_path),
            }
        )
    return rows


def write_csv_file(path: Path, rows: List[Dict[str, str]]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)

    fieldnames = [
        "slug",
        "language",
        "category_name_uk",
        "h1",
        "main_keyword",
        "meta_title",
        "meta_description",
        "text_md",
    ]

    with path.open("w", encoding="utf-8", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames, quoting=csv.QUOTE_ALL)
        writer.writeheader()
        writer.writerows(rows)


def main(argv: Optional[List[str]] = None) -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument(
        "--output",
        default=str(ROOT / "uk" / "data" / "output" / "uk_category_texts.csv"),
        help="Output CSV path (UTF-8).",
    )
    args = ap.parse_args(argv)

    slugs = get_slugs_in_order()
    if not slugs:
        raise SystemExit(f"No categories found in: {UK_CATEGORIES_DIR}")

    rows = build_rows(slugs)
    write_csv_file(Path(args.output), rows)
    print(f"✅ Wrote {len(rows)} rows: {args.output}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

