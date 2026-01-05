#!/usr/bin/env python3
"""
Загрузка контента категорий в БД OpenCart
"""

import json
import re

import mysql.connector

# Маппинг slug → category_id
CATEGORY_IDS = {
    "aktivnaya-pena": 415,
    "dlya-ruchnoy-moyki": 412,
    "ochistiteli-stekol": 418,
    "glina-i-avtoskraby": 423,
    "antimoshka": 417,
    "antibitum": 426,
    "cherniteli-shin": 421,
    "ochistiteli-diskov": 419,
    "ochistiteli-shin": 420,
}

# Language IDs
LANG_RU = 3
LANG_UK = 1


def md_to_html(md_content):
    """Конвертация Markdown в HTML"""

    html = md_content

    # Удаляем H1 (первая строка)
    html = re.sub(r"^# .+\n\n", "", html, count=1, flags=re.MULTILINE)

    # Заголовки
    html = re.sub(r"^### (.+)$", r"<h3>\1</h3>", html, flags=re.MULTILINE)
    html = re.sub(r"^## (.+)$", r"<h2>\1</h2>", html, flags=re.MULTILINE)

    # Жирный и курсив
    html = re.sub(r"\*\*(.+?)\*\*", r"<strong>\1</strong>", html)

    # Таблицы
    html = convert_tables(html)

    # Списки
    html = convert_lists(html)

    # Параграфы
    html = wrap_paragraphs(html)

    # Убираем лишние переводы строк
    html = re.sub(r"\n{3,}", "\n\n", html)

    return html.strip()


def convert_tables(text):
    """Markdown таблицы → HTML"""
    lines = text.split("\n")
    result = []
    i = 0

    while i < len(lines):
        line = lines[i].strip()

        # Начало таблицы
        if "|" in line and i + 1 < len(lines) and "|" in lines[i + 1]:
            table_lines = [line]
            i += 1

            # Собираем все строки таблицы
            while i < len(lines) and "|" in lines[i]:
                table_lines.append(lines[i].strip())
                i += 1

            result.append(build_html_table(table_lines))
        else:
            result.append(lines[i])
            i += 1

    return "\n".join(result)


def build_html_table(lines):
    """Строит HTML таблицу"""
    if len(lines) < 2:
        return "\n".join(lines)

    # Header
    header = lines[0]
    # Пропускаем разделитель (вторая строка с ---|---)
    rows = [line for line in lines[2:] if "|" in line]

    html = [
        '<table border="1" cellpadding="8" cellspacing="0" style="border-collapse: collapse; width: 100%;">'
    ]

    # Заголовок
    cols = [c.strip() for c in header.split("|") if c.strip()]
    html.append("<thead><tr>")
    for col in cols:
        html.append(f'<th style="background: #f5f5f5; padding: 8px;">{col}</th>')
    html.append("</tr></thead>")

    # Тело
    html.append("<tbody>")
    for row in rows:
        cols = [c.strip() for c in row.split("|") if c.strip()]
        html.append("<tr>")
        for col in cols:
            html.append(f'<td style="padding: 8px;">{col}</td>')
        html.append("</tr>")
    html.append("</tbody>")
    html.append("</table>")

    return "\n".join(html)


def convert_lists(text):
    """Markdown списки → HTML"""
    lines = text.split("\n")
    result = []
    in_list = False

    for line in lines:
        stripped = line.strip()

        if stripped.startswith("- "):
            if not in_list:
                result.append("<ul>")
                in_list = True
            item = stripped[2:]
            result.append(f"<li>{item}</li>")
        elif stripped.startswith("→ "):
            # Продолжение предыдущего пункта
            result.append(f"{stripped}")
        else:
            if in_list:
                result.append("</ul>")
                in_list = False
            result.append(line)

    if in_list:
        result.append("</ul>")

    return "\n".join(result)


def wrap_paragraphs(text):
    """Оборачивает текст в <p>"""
    lines = text.split("\n")
    result = []
    current_p = []
    in_table = False
    in_list = False

    for line in lines:
        stripped = line.strip()

        # Отслеживаем блоки таблиц и списков
        if stripped.startswith("<table"):
            in_table = True
        elif stripped.startswith("</table>"):
            in_table = False
        elif stripped.startswith("<ul>"):
            in_list = True
        elif stripped.startswith("</ul>"):
            in_list = False

        # Пропускаем блоки (таблицы, списки, заголовки)
        if (
            in_table
            or in_list
            or any(
                stripped.startswith(x)
                for x in [
                    "<table",
                    "</table>",
                    "<ul>",
                    "</ul>",
                    "<h2>",
                    "<h3>",
                    "<li>",
                    "<thead",
                    "<tbody",
                    "<tr>",
                    "<th",
                    "<td",
                ]
            )
        ):
            if current_p:
                result.append("<p>" + " ".join(current_p) + "</p>")
                current_p = []
            result.append(line)
        elif stripped == "":
            if current_p:
                result.append("<p>" + " ".join(current_p) + "</p>")
                current_p = []
            # Не добавляем пустую строку
        else:
            current_p.append(stripped)

    if current_p:
        result.append("<p>" + " ".join(current_p) + "</p>")

    return "\n".join(result)


def load_category_data(slug, lang="ru"):
    """Загружает MD и JSON для категории"""
    base_path = "uk/categories" if lang == "uk" else "categories"

    # Читаем MD файл
    md_file = f"{base_path}/{slug}/content/{slug}_{lang}.md"
    with open(md_file, encoding="utf-8") as f:
        md_content = f.read()

    # Читаем meta JSON
    meta_file = f"{base_path}/{slug}/meta/{slug}_meta.json"
    with open(meta_file, encoding="utf-8") as f:
        meta_data = json.load(f)

    # Конвертируем MD → HTML
    html_content = md_to_html(md_content)

    return {
        "slug": slug,
        "category_id": CATEGORY_IDS[slug],
        "language_id": LANG_UK if lang == "uk" else LANG_RU,
        "description": html_content,
        "meta_title": meta_data["meta"]["title"],
        "meta_description": meta_data["meta"]["description"],
        "meta_h1": meta_data.get("h1", ""),
    }


def update_database(data, dry_run=False):
    """Обновляет БД"""
    if dry_run:
        print(
            f"\n[DRY RUN] Категория {data['slug']} (ID={data['category_id']}, lang_id={data['language_id']})"
        )
        print(f"  meta_h1: {data['meta_h1']}")
        print(f"  meta_title: {data['meta_title'][:60]}...")
        print(f"  description: {len(data['description'])} символов")
        return

    conn = mysql.connector.connect(
        host="localhost",
        user="ultimate",
        password="ultimate123",  # noqa: S106
        database="yastman_test",
        charset="utf8mb4",
    )

    cursor = conn.cursor()

    query = """
        UPDATE oc_category_description
        SET
            description = %s,
            meta_title = %s,
            meta_description = %s,
            meta_h1 = %s
        WHERE category_id = %s AND language_id = %s
    """

    cursor.execute(
        query,
        (
            data["description"],
            data["meta_title"],
            data["meta_description"],
            data["meta_h1"],
            data["category_id"],
            data["language_id"],
        ),
    )

    conn.commit()
    cursor.close()
    conn.close()

    print(f"✓ {data['slug']} ({'RU' if data['language_id'] == 3 else 'UK'}) обновлено")


def main(slug=None, dry_run=False):
    """Главная функция"""

    slugs = [slug] if slug else list(CATEGORY_IDS.keys())

    for s in slugs:
        # RU версия
        try:
            data_ru = load_category_data(s, "ru")
            update_database(data_ru, dry_run)
        except Exception as e:
            print(f"✗ Ошибка RU {s}: {e}")

        # UK версия
        try:
            data_uk = load_category_data(s, "uk")
            update_database(data_uk, dry_run)
        except Exception as e:
            print(f"✗ Ошибка UK {s}: {e}")


if __name__ == "__main__":
    import sys

    slug = sys.argv[1] if len(sys.argv) > 1 else None
    dry_run = "--dry-run" in sys.argv

    main(slug, dry_run)
