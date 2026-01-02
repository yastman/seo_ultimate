
import pytest
import sys
import os
import json
import yaml
from pathlib import Path

# Add scripts directory to path
sys.path.insert(0, str(Path(__file__).parent.parent / 'scripts'))

from check_simple_v2_md import (
    parse_markdown_file,
    extract_text_content,
    check_intro_structure,
    check_h2_intent_structure,
    check_faq,
    check_keyword_stuffing,
    check_internal_links,
    check_content,
    check_keyword_density_and_distribution
)

class TestCheckSimpleV2MD:
    @pytest.fixture
    def valid_md_content(self):
        long_intro = "В этой статье мы подробно рассмотрим, как выбрать лучший товар для вашего автомобиля. Это введение специально написано достаточно длинным, чтобы успешно пройти автоматическую проверку на количество слов, так как мы стараемся соответствовать всем стандартам SEO. Вам нужно набрать минимум 100 слов в вводной части, чтобы алгоритм посчитал текст качественным. Поэтому мы продолжаем писать этот текст, добавляя всё больше полезных слов и оборотов, чтобы убедиться, что проверка интро проходит абсолютно успешно. Важно использовать естественный язык, избегать явных шаблонов и спама, а также давать читателю реальную пользу с первых строк. Мы ценим ваше время и предлагаем только проверенную информацию."
        
        filler_text = " ".join(["Это очень полезный текст о товарах."] * 100) # + ~600 words

        return f"""---
title: "Valid Title With Adequate Length 50-70 Chars"
description: "This is a valid description that has enough characters to pass the check. It needs to be between 140 and 170 characters long so adding some more filler text here."
---

# H1 Header

{long_intro}

{filler_text}

## Как выбрать товар
Текст о выборе... {filler_text[:500]}

## Преимущества
Текст о преимуществах... {filler_text[:500]}

## Типы товаров
Текст о типах... {filler_text[:500]}

## Часто задаваемые вопросы
Текст перед FAQ...

### Вопрос первый?
Ответ первый.

### Вопрос второй?
Ответ второй.

### Вопрос третий?
Ответ третий.

[Внутренняя ссылка](/category/item1) с хорошим анкором.
[Вторая ссылка](/category/item2) тоже нормальная.
"""

    @pytest.fixture
    def mock_json_data(self, tmp_path):
        data = {
            "keywords": {
                "primary": [{"keyword": "товар", "density_target": "0.2%", "occurrences_target": 5}],
                "secondary": [],
                "supporting": []
            }
        }
        json_file = tmp_path / "test_data.json"
        with open(json_file, "w", encoding="utf-8") as f:
            json.dump(data, f)
        return json_file

    def test_parse_markdown_file(self, tmp_path, valid_md_content):
        md_file = tmp_path / "test.md"
        md_file.write_text(valid_md_content, encoding="utf-8")
        
        metadata, content = parse_markdown_file(str(md_file))
        
        assert metadata["title"] == "Valid Title With Adequate Length 50-70 Chars"
        assert "# H1 Header" in content

    def test_extract_text_content(self):
        md = "# Header\nText with [link](url) and **bold**."
        text = extract_text_content(md)
        assert "Header" in text  # Headers might be stripped depending on impl, checking logic
        # Implementation strips headers: re.sub(r"^#{1,6}\s+", "", text, flags=re.MULTILINE)
        # But wait, does it strip the line or just the #?
        # code: re.sub(r"^#{1,6}\s+", "", text, flags=re.MULTILINE) -> removes '#' but keeps text "Header"
        # Wait, let's re-read the code.
        # text = re.sub(r"^#{1,6}\s+", "", text, flags=re.MULTILINE)
        # So "# Header" becomes "Header".
        assert "Header" in text
        assert "Text with link and bold." in text

    def test_check_intro_structure_short(self):
        text_words = ["word"] * 50
        ok, msg = check_intro_structure("", text_words)
        assert not ok
        assert "Интро слишком короткое" in msg

    def test_check_intro_structure_ai_pattern(self):
        text_words = ["В", "этой", "статье", "мы", "рассмотрим"] + ["word"] * 100
        # "в этой статье мы рассмотрим" is in ai_patterns
        # But split words logic passes list of words. Function reconstructs string.
        # " ".join(words[:150])
        
        ok, msg = check_intro_structure("", text_words)
        assert not ok
        assert "AI-шаблоны" in msg

    def test_check_h2_intent_structure(self):
        md_good = "## Как выбрать\n## Преимущества\n"
        ok, msg = check_h2_intent_structure(md_good)
        assert ok
        
        md_bad = "## Заголовок 1\n## Заголовок 2\n"
        ok, msg = check_h2_intent_structure(md_bad)
        assert not ok
        assert "нет intent-ориентированных" in msg

    def test_check_faq(self):
        md_good = "### Вопрос 1?\n### Вопрос 2?\n### Вопрос 3?\n"
        ok, msg = check_faq(md_good)
        assert ok
        
        md_bad = "### Вопрос 1\n### Вопрос 2\n" # No question mark
        ok, msg = check_faq(md_bad)
        assert not ok
        
        md_few = "### Вопрос 1?\n"
        ok, msg = check_faq(md_few)
        assert not ok

    def test_check_internal_links(self):
        md_good = "[Link 1](/path1) [Link 2](/path2)"
        ok, msg = check_internal_links(md_good)
        assert ok
        
        md_bad_count = "[Link 1](/path1)"
        ok, msg = check_internal_links(md_bad_count)
        assert ok
        assert "WARNING" in msg or "⚠️" in msg
        
        md_bad_anchor = "[тут](/path1) [Link 2](/path2)"
        ok, msg = check_internal_links(md_bad_anchor)
        assert not ok
        assert "неописательные анкоры" in msg

    def test_check_keyword_density_and_distribution(self, mock_json_data):
        # Create a text with some keywords
        md_content = "Товар " * 10 + "другие слова " * 500
        # 10 occurrences in ~1000 words -> ~1%
        
        result = check_keyword_density_and_distribution(md_content, str(mock_json_data), 1000)
        
        assert result["keywords_found"] > 0
        assert "total_density" in result
        
    def test_check_content_integration(self, tmp_path, valid_md_content, mock_json_data):
        # Setup folder structure for density check to work: categories/slug/content/file.md and categories/slug/data/slug.json
        cat_dir = tmp_path / "categories" / "test-cat"
        content_dir = cat_dir / "content"
        data_dir = cat_dir / "data"
        content_dir.mkdir(parents=True)
        data_dir.mkdir(parents=True)
        
        md_file = content_dir / "test-cat_ru.md"
        md_file.write_text(valid_md_content, encoding="utf-8")
        
        json_file = data_dir / "test-cat.json"
        # Copy mock data
        with open(mock_json_data, 'r') as f:
            data = json.load(f)
        with open(json_file, 'w', encoding='utf-8') as f:
            json.dump(data, f)
            
        # Run check
        result = check_content(str(md_file), "товар", "B")
        
        assert result["status"] in ["PASS", "REVIEW", "FAIL"]
        assert "checks" in result
        assert result["checks"]["h1"]["pass"] is True
        assert result["checks"]["intro"]["pass"] is True
