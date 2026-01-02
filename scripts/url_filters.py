#!/usr/bin/env python3
"""
Shared URL filtering utilities for SEO workflow.

Used by:
- url_preparation_filter_and_validate.py (Stage -2)
- filter_mega_competitors.py (Stage 5)
"""

from urllib.parse import urlparse


# ===== BLACKLIST DOMAINS =====
BLACKLISTED_DOMAINS = [
    "rozetka.com.ua",
    "epicentrk.ua",
    "epicentr.ua",
    "olx.ua",
    "m.olx.ua",
    "prom.ua",
    "youtube.com",
    "youtu.be",
    "facebook.com",
    "instagram.com",
    "tiktok.com",
    "telegram.org",
    "wiki",
    "wikipedia.org",
]


def is_blacklisted_domain(url: str) -> bool:
    """Check if URL domain is in blacklist"""
    parsed = urlparse(url)
    domain = parsed.netloc.lower()
    return any(blacklist in domain for blacklist in BLACKLISTED_DOMAINS)


def fix_ua_in_url(url: str) -> str:
    """
    Fix /ua/ in URL: remove /ua/ or replace with /ru/

    Examples:
        https://site.com/ua/catalog/ → https://site.com/catalog/
        https://site.com/catalog/ua → https://site.com/catalog/ru
    """
    if "/ua/" not in url and not url.endswith("/ua"):
        return url

    # Remove /ua/ from path
    url_fixed = url.replace("/ua/", "/")

    # If URL ends with /ua, replace with /ru
    if url.endswith("/ua"):
        url_fixed = url.replace("/ua", "/ru")

    return url_fixed


def is_category_page(url: str) -> bool:
    """
    Heuristic check if URL is a category page.

    Category indicators: catalog, category, products, shop
    Non-category indicators: product, item, article, blog, contact
    """
    path = urlparse(url).path.lower()

    # Category indicators
    category_kw = ["catalog", "category", "categories", "products", "shop", "tovar"]

    # Non-category indicators
    non_category_kw = [
        "product", "item", "article", "news", "blog", "contact",
        "about", "payment", "delivery", "dostavka", "oplata",
        "cart", "checkout", "search", "login", "register"
    ]

    has_category = any(kw in path for kw in category_kw)
    has_non_category = any(kw in path for kw in non_category_kw)

    # Heuristic: category if has category keyword AND no non-category keywords
    if has_category and not has_non_category:
        return True

    # Fallback: short paths (2-3 segments) are likely categories
    path_segments = [p for p in path.split("/") if p]
    if 2 <= len(path_segments) <= 3 and not has_non_category:
        return True

    return False
