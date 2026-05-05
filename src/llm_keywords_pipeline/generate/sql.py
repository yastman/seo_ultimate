#!/usr/bin/env python3
"""
Generate OpenCart SQL updates for category SEO content.

This module is intentionally test-first friendly:
- Pure helpers for Markdown → HTML conversion
- Safe SQL escaping
- File-based orchestration in `main()`
"""

from __future__ import annotations

import json
from dataclasses import dataclass
from datetime import datetime
from pathlib import Path

import markdown

PROJECT_DIR = Path(__file__).resolve().parents[1]
OUTPUT_FILE = PROJECT_DIR / "content_updates.sql"

# Can be overridden in tests/usage.
CATEGORY_MAP: dict[str, int] = {}

# OpenCart defaults for this project (RU content).
LANGUAGE_ID = 3


def escape_sql(value: str) -> str:
    return value.replace("\\", "\\\\").replace("'", "\\'").replace('"', '\\"')


def _is_table_line(line: str) -> bool:
    stripped = line.strip()
    return stripped.startswith("|") and stripped.endswith("|") and stripped.count("|") >= 2


def _is_table_separator(line: str) -> bool:
    stripped = line.strip().strip("|").replace(" ", "")
    if not stripped:
        return False
    parts = stripped.split("|")
    return all(part and set(part) <= {"-", ":"} and "-" in part for part in parts)


def build_html_table(lines: list[str]) -> str:
    if len(lines) < 3:
        return "\n".join(lines)

    header = lines[0].strip()
    sep = lines[1].strip()
    if not (_is_table_line(header) and _is_table_separator(sep)):
        return "\n".join(lines)

    headers = [cell.strip() for cell in header.strip("|").split("|")]
    rows = []
    for line in lines[2:]:
        if not _is_table_line(line):
            return "\n".join(lines)
        rows.append([cell.strip() for cell in line.strip().strip("|").split("|")])

    out: list[str] = ["<table>", "<tr>"]
    out.extend([f"<th>{markdown.util.AtomicString(h)}</th>" for h in headers])
    out.append("</tr>")
    for row in rows:
        out.append("<tr>")
        out.extend([f"<td>{markdown.util.AtomicString(c)}</td>" for c in row])
        out.append("</tr>")
    out.append("</table>")
    return "\n".join(out)


def convert_tables(content: str) -> str:
    lines = content.splitlines()
    out: list[str] = []
    buf: list[str] = []

    def flush() -> None:
        nonlocal buf
        if not buf:
            return
        out.append(build_html_table(buf))
        buf = []

    for line in lines:
        if _is_table_line(line) or (buf and _is_table_separator(line)):
            buf.append(line)
            continue
        flush()
        out.append(line)
    flush()
    return "\n".join(out)


def convert_lists(content: str) -> str:
    lines = content.splitlines()
    out: list[str] = []
    mode: str | None = None  # "ul" | "ol" | None

    def close() -> None:
        nonlocal mode
        if mode == "ul":
            out.append("</ul>")
        elif mode == "ol":
            out.append("</ol>")
        mode = None

    for line in lines:
        stripped = line.strip()
        is_ul = stripped.startswith("- ") or stripped.startswith("* ")
        is_ol = False
        item_text = ""
        if is_ul:
            item_text = stripped[2:].strip()
        else:
            # 1. item
            dot = stripped.find(". ")
            if dot > 0 and stripped[:dot].isdigit():
                is_ol = True
                item_text = stripped[dot + 2 :].strip()

        if is_ul:
            if mode == "ol":
                close()
            if mode is None:
                out.append("<ul>")
                mode = "ul"
            out.append(f"<li>{item_text}</li>")
            continue

        if is_ol:
            if mode == "ul":
                close()
            if mode is None:
                out.append("<ol>")
                mode = "ol"
            out.append(f"<li>{item_text}</li>")
            continue

        if mode is not None and stripped:
            close()
        out.append(line)

    close()
    return "\n".join(out)


def md_to_html(md_text: str) -> tuple[str, str]:
    lines = md_text.splitlines()
    h1 = ""
    body_lines = lines
    if lines and lines[0].startswith("# "):
        h1 = lines[0][2:].strip()
        body_lines = lines[1:]
        while body_lines and not body_lines[0].strip():
            body_lines = body_lines[1:]

    # Python-Markdown tends to merge mixed UL/OL blocks unless separated.
    # For our project we want UL and OL to be independent blocks even if the
    # author writes them without blank lines.
    normalized_lines: list[str] = []
    prev_list_kind: str | None = None  # "ul" | "ol" | None
    for line in body_lines:
        stripped = line.lstrip()
        list_kind: str | None = None
        if stripped.startswith(("- ", "* ")):
            list_kind = "ul"
        else:
            dot = stripped.find(". ")
            if dot > 0 and stripped[:dot].isdigit():
                list_kind = "ol"

        if list_kind and prev_list_kind and list_kind != prev_list_kind:
            normalized_lines.append("")

        if list_kind:
            prev_list_kind = list_kind
        elif stripped:
            prev_list_kind = None

        normalized_lines.append(line)

    body_md = "\n".join(normalized_lines).strip() + ("\n" if normalized_lines else "")
    html = markdown.markdown(
        body_md,
        extensions=["tables", "sane_lists"],
        output_format="html",
    )
    return h1, html


@dataclass(frozen=True)
class CategoryMeta:
    title: str = ""
    description: str = ""


def _read_category_md(slug: str) -> str | None:
    path = PROJECT_DIR / "categories" / slug / "content" / f"{slug}_ru.md"
    if not path.exists():
        return None
    return path.read_text(encoding="utf-8")


def _read_category_meta(slug: str) -> CategoryMeta:
    meta_path = PROJECT_DIR / "categories" / slug / "meta" / f"{slug}_meta.json"
    if not meta_path.exists():
        return CategoryMeta()

    data = json.loads(meta_path.read_text(encoding="utf-8"))
    meta = data.get("meta", {}) if isinstance(data, dict) else {}
    return CategoryMeta(
        title=str(meta.get("title", "") or ""),
        description=str(meta.get("description", "") or ""),
    )


def generate_update_sql(slug: str, category_id: int) -> str:
    md_text = _read_category_md(slug)
    if not md_text:
        return f"-- {slug} (category_id: {category_id})\n-- Нет контента\n"

    h1, html = md_to_html(md_text)
    meta = _read_category_meta(slug)

    html_sql = escape_sql(html)
    title_sql = escape_sql(meta.title)
    desc_sql = escape_sql(meta.description)
    h1_sql = escape_sql(h1)

    return "\n".join(
        [
            f"-- {slug} (category_id: {category_id})",
            "UPDATE `oc_category_description`",
            "SET",
            f"    `description` = '{html_sql}',",
            f"    `meta_title` = '{title_sql}',",
            f"    `meta_description` = '{desc_sql}',",
            f"    `meta_h1` = '{h1_sql}'",
            f"WHERE `category_id` = {category_id} AND `language_id` = {LANGUAGE_ID};",
            "",
        ]
    )


def _header_sql() -> str:
    now = datetime.now().strftime("%Y-%m-%d %H:%M")
    return "\n".join(
        [
            "-- Ultimate.net.ua — SEO Content Updates",
            f"-- Сгенерировано: {now}",
            f"-- Категорий: {len(CATEGORY_MAP)}",
            "",
            "SET NAMES utf8mb4;",
            "",
        ]
    )


def main() -> None:
    chunks: list[str] = [_header_sql()]
    for slug, category_id in CATEGORY_MAP.items():
        chunks.append(generate_update_sql(slug, category_id))

    OUTPUT_FILE.parent.mkdir(parents=True, exist_ok=True)
    OUTPUT_FILE.write_text("\n".join(chunks).strip() + "\n", encoding="utf-8")
    print(f"SQL сохранён: {OUTPUT_FILE}")


if __name__ == "__main__":
    main()
