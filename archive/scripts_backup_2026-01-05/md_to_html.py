#!/usr/bin/env python3
"""
Конвертация Markdown → HTML для OpenCart категорий
"""

import re
import sys


def md_to_html(md_content):
    """Конвертирует Markdown в HTML для description поля БД"""

    html = md_content

    # Удаляем H1 (первая строка с #)
    html = re.sub(r"^# .+\n\n", "", html, count=1)

    # H2 ## → <h2>
    html = re.sub(r"^## (.+)$", r"<h2>\1</h2>", html, flags=re.MULTILINE)

    # H3 ### → <h3>
    html = re.sub(r"^### (.+)$", r"<h3>\1</h3>", html, flags=re.MULTILINE)

    # Жирный текст **text** → <strong>
    html = re.sub(r"\*\*(.+?)\*\*", r"<strong>\1</strong>", html)

    # Курсив *text* → <em> (только одиночные *)
    html = re.sub(r"(?<!\*)\*(?!\*)(.+?)(?<!\*)\*(?!\*)", r"<em>\1</em>", html)

    # Таблицы: простая конвертация
    html = convert_tables(html)

    # Параграфы: пустые строки разделяют <p>
    paragraphs = []
    current_p = []
    in_table = False

    for line in html.split("\n"):
        stripped = line.strip()

        # Проверяем начало/конец таблицы
        if stripped.startswith("<table"):
            in_table = True
            if current_p:
                paragraphs.append("<p>" + " ".join(current_p) + "</p>")
                current_p = []
            paragraphs.append(line)
            continue
        elif stripped.startswith("</table>"):
            in_table = False
            paragraphs.append(line)
            continue
        elif in_table:
            paragraphs.append(line)
            continue

        # Если заголовок или пустая строка
        if stripped.startswith("<h2>") or stripped.startswith("<h3>"):
            if current_p:
                paragraphs.append("<p>" + " ".join(current_p) + "</p>")
                current_p = []
            paragraphs.append(line)
        elif stripped == "":
            if current_p:
                paragraphs.append("<p>" + " ".join(current_p) + "</p>")
                current_p = []
        elif stripped.startswith("- ") or stripped.startswith("→"):
            # Списки оставляем как есть пока
            if current_p:
                paragraphs.append("<p>" + " ".join(current_p) + "</p>")
                current_p = []
            paragraphs.append(stripped)
        else:
            current_p.append(stripped)

    if current_p:
        paragraphs.append("<p>" + " ".join(current_p) + "</p>")

    html = "\n".join(paragraphs)

    # Списки: - item → <li>
    html = convert_lists(html)

    return html.strip()


def convert_tables(text):
    """Конвертирует Markdown таблицы в HTML"""

    lines = text.split("\n")
    result = []
    in_table = False
    table_lines = []

    for line in lines:
        stripped = line.strip()

        # Начало таблицы (строка с |)
        if "|" in stripped and not in_table:
            in_table = True
            table_lines = [stripped]
        elif "|" in stripped and in_table:
            table_lines.append(stripped)
        else:
            # Конец таблицы
            if in_table:
                result.append(build_html_table(table_lines))
                table_lines = []
                in_table = False
            result.append(line)

    # Если таблица в конце
    if in_table and table_lines:
        result.append(build_html_table(table_lines))

    return "\n".join(result)


def build_html_table(lines):
    """Строит HTML таблицу из Markdown строк"""

    if len(lines) < 2:
        return "\n".join(lines)

    # Убираем разделитель (вторая строка)
    header = lines[0]
    rows = [line for line in lines[1:] if not re.match(r"^\|[\s\-:|]+\|$", line)]

    html = ['<table border="1" cellpadding="5" cellspacing="0">']

    # Header
    cols = [c.strip() for c in header.split("|") if c.strip()]
    html.append("<thead><tr>")
    for col in cols:
        html.append(f"<th>{col}</th>")
    html.append("</tr></thead>")

    # Body
    html.append("<tbody>")
    for row in rows:
        cols = [c.strip() for c in row.split("|") if c.strip()]
        html.append("<tr>")
        for col in cols:
            html.append(f"<td>{col}</td>")
        html.append("</tr>")
    html.append("</tbody>")
    html.append("</table>")

    return "\n".join(html)


def convert_lists(text):
    """Конвертирует списки - item в <ul><li>"""

    lines = text.split("\n")
    result = []
    in_list = False

    for line in lines:
        stripped = line.strip()

        if stripped.startswith("- "):
            if not in_list:
                result.append("<ul>")
                in_list = True
            item = stripped[2:]  # Убираем "- "
            result.append(f"<li>{item}</li>")
        elif stripped.startswith("→"):
            # Стрелка → как продолжение пункта
            result.append(stripped)
        else:
            if in_list:
                result.append("</ul>")
                in_list = False
            result.append(line)

    if in_list:
        result.append("</ul>")

    return "\n".join(result)


if __name__ == "__main__":
    if len(sys.argv) > 1:
        with open(sys.argv[1], encoding="utf-8") as f:
            md = f.read()
        print(md_to_html(md))
    else:
        print("Usage: python md_to_html.py file.md")
