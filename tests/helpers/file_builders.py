import json
from pathlib import Path
from typing import Any, Dict, Optional

import yaml  # type: ignore


class CategoryBuilder:
    """
    Builder для создания тестовой структуры категории.
    Позволяет создавать папки, meta.json, clean.json и контент-файлы.
    
    Example:
        path = CategoryBuilder() \
            .with_slug("test-cat") \
            .with_meta(title="Test") \
            .build(tmp_path)
    """

    def __init__(self):
        self._slug = "test-category"
        self._lang = "ru"
        self._meta: Dict[str, Any] = {
            "title": "Default Title | Brand",
            "description": "Default description.",
            "h1": "Default H1",
        }
        self._keywords: Any = {"primary": [{"keyword": "main keyword", "volume": 100}]}
        self._content: Optional[str] = None
        self._research: Optional[str] = None
        self._clean_json_extra: Dict[str, Any] = {}

    def with_slug(self, slug: str) -> "CategoryBuilder":
        self._slug = slug
        return self

    def with_lang(self, lang: str) -> "CategoryBuilder":
        self._lang = lang
        return self

    def with_meta(self, title: str, description: str, h1: str) -> "CategoryBuilder":
        self._meta = {"title": title, "description": description, "h1": h1}
        return self

    def with_keywords(self, keywords: Any) -> "CategoryBuilder":
        """
        Принимает:
        - Список строк или словарей (авто-конвертация в {"primary": [...]})
        - Словарь {cluster: [keywords]} (используется как есть)
        """
        if isinstance(keywords, dict):
            self._keywords = keywords
            return self

        # Normalize list elements
        normalized = []
        for k in keywords:
            if isinstance(k, str):
                normalized.append({"keyword": k, "volume": 10})
            else:
                normalized.append(k)

        # Default to "primary" cluster if flat list provided
        self._keywords = {"primary": normalized}
        return self

    def with_content(self, markdown_text: str) -> "CategoryBuilder":
        self._content = markdown_text
        return self

    def with_research(self, markdown_text: str) -> "CategoryBuilder":
        self._research = markdown_text
        return self

    def build(self, root_path: Path) -> Path:
        """
        Создает структуру файлов в root_path.
        Возвращает путь к папке категории.
        """
        cat_dir = root_path / "categories" / self._slug
        cat_dir.mkdir(parents=True, exist_ok=True)

        # 1. Create meta/
        meta_dir = cat_dir / "meta"
        meta_dir.mkdir(exist_ok=True)
        meta_file = meta_dir / f"{self._slug}_meta.json"
        meta_file.write_text(json.dumps(self._meta, ensure_ascii=False, indent=2), encoding="utf-8")

        # 2. Create data/ (clean.json)
        data_dir = cat_dir / "data"
        data_dir.mkdir(exist_ok=True)
        clean_data = {
            "slug": self._slug,
            "name": self._meta.get("h1", "Name"),
            "keywords": self._keywords,
            "meta": self._meta,
            **self._clean_json_extra,
        }
        clean_file = data_dir / f"{self._slug}_clean.json"
        clean_file.write_text(json.dumps(clean_data, ensure_ascii=False, indent=2), encoding="utf-8")

        # 3. Create content/
        if self._content is not None:
            content_dir = cat_dir / "content"
            content_dir.mkdir(exist_ok=True)
            content_file = content_dir / f"{self._slug}_{self._lang}.md"

            # Если нет frontmatter, добавляем дефолтный
            if not self._content.startswith("---"):
                fm = {"title": self._meta["title"], "description": self._meta["description"]}
                fm_text = yaml.dump(fm, allow_unicode=True)
                full_text = f"---\n{fm_text}---\n\n{self._content}"
            else:
                full_text = self._content

            content_file.write_text(full_text, encoding="utf-8")

        # 4. Create research/
        if self._research is not None:
            res_dir = cat_dir / "research"
            res_dir.mkdir(exist_ok=True)
            res_file = res_dir / "RESEARCH_DATA.md"
            res_file.write_text(self._research, encoding="utf-8")

        return cat_dir
