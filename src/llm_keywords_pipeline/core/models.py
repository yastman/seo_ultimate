"""Canonical data contract for the automation engine (issue #16).

Single source of truth for all keyword/category data structures.
Supports V1 (keywords_detailed), V2 (keywords dict), V3 (keywords list) → canonical.
"""
from __future__ import annotations

from enum import StrEnum
from typing import Any

from pydantic import BaseModel, Field, model_validator

SCHEMA_VERSION = "1.0"


class Keyword(BaseModel):
    keyword: str
    volume: int = 0
    group: str = "supporting"  # primary | secondary | supporting | commercial


class Meta(BaseModel):
    title: str = ""
    description: str = ""
    h1: str = ""


class CategoryState(StrEnum):
    pending = "pending"
    prepare = "prepare"
    research = "research"
    produce = "produce"
    validate = "validate"
    deliver = "deliver"
    done = "done"
    needs_human = "needs_human"
    failed = "failed"


class Category(BaseModel):
    schema_version: str = SCHEMA_VERSION
    slug: str
    name: str = ""
    lang: str = "ru"
    keywords: list[Keyword] = Field(default_factory=list)
    synonyms: list[Keyword] = Field(default_factory=list)
    meta: Meta = Field(default_factory=Meta)
    state: CategoryState = CategoryState.pending

    @model_validator(mode="before")
    @classmethod
    def adapt_formats(cls, data: Any) -> Any:
        """Normalize V1/V2/V3 keyword formats to flat list[Keyword]."""
        if not isinstance(data, dict):
            return data
        raw = data.get("keywords", [])
        if isinstance(raw, dict):
            # V2: {"primary": [...], "secondary": [...], ...}
            flat: list[dict] = []
            for group in ("primary", "secondary", "supporting", "commercial"):
                for item in raw.get(group, []):
                    if isinstance(item, str):
                        flat.append({"keyword": item, "volume": 0, "group": group})
                    elif isinstance(item, dict):
                        flat.append({**item, "group": item.get("group", group)})
            data = {**data, "keywords": flat}
        elif isinstance(raw, list):
            normalized: list[dict] = []
            for item in raw:
                if isinstance(item, str):
                    # V1 or plain-string list
                    normalized.append({"keyword": item, "volume": 0, "group": "supporting"})
                elif isinstance(item, dict):
                    if "phrase" in item and "keyword" not in item:
                        # V1 keywords_detailed format
                        normalized.append({
                            "keyword": item["phrase"],
                            "volume": item.get("volume", 0),
                            "group": item.get("group", "supporting"),
                        })
                    else:
                        normalized.append(item)
            # Also handle V1 top-level keywords_detailed
            if not normalized and "keywords_detailed" in data:
                for item in data["keywords_detailed"]:
                    if isinstance(item, dict):
                        normalized.append({
                            "keyword": item.get("phrase", item.get("keyword", "")),
                            "volume": item.get("volume", 0),
                            "group": item.get("group", "supporting"),
                        })
            data = {**data, "keywords": normalized}
        return data

    @classmethod
    def from_json(cls, data: dict) -> Category:
        """Load from any supported JSON format."""
        return cls.model_validate(data)

    def keywords_flat(self) -> list[str]:
        """Return all keyword strings (for legacy callers)."""
        return [kw.keyword for kw in self.keywords if kw.keyword]

    def keywords_by_group(self, group: str) -> list[Keyword]:
        return [kw for kw in self.keywords if kw.group == group]
