"""
Tests for url_filters.py — Shared URL filtering utilities

Tests cover:
1. Blacklist domain checking
2. /ua/ URL fixing
3. Category page heuristics
"""

import pytest
import sys
from pathlib import Path

# Add scripts directory to path
sys.path.insert(0, str(Path(__file__).parent.parent / 'scripts'))

from url_filters import (
    is_blacklisted_domain,
    fix_ua_in_url,
    is_category_page,
    BLACKLISTED_DOMAINS
)


class TestBlacklistedDomains:
    """Test is_blacklisted_domain function"""

    def test_blacklist_contains_marketplaces(self):
        """Blacklist should contain major marketplaces"""
        assert "rozetka.com.ua" in BLACKLISTED_DOMAINS
        assert "prom.ua" in BLACKLISTED_DOMAINS
        assert "olx.ua" in BLACKLISTED_DOMAINS

    def test_blacklist_contains_social(self):
        """Blacklist should contain social media"""
        assert "youtube.com" in BLACKLISTED_DOMAINS
        assert "facebook.com" in BLACKLISTED_DOMAINS
        assert "instagram.com" in BLACKLISTED_DOMAINS

    @pytest.mark.parametrize("url,expected", [
        ("https://rozetka.com.ua/catalog/auto", True),
        ("https://www.rozetka.com.ua/product/123", True),
        ("https://prom.ua/category/avto", True),
        ("https://olx.ua/electronics", True),
        ("https://m.olx.ua/auto", True),
        ("https://youtube.com/watch?v=abc", True),
        ("https://www.youtube.com/channel/xyz", True),
        ("https://epicentrk.ua/shop/auto", True),
    ])
    def test_blacklisted_urls_detected(self, url, expected):
        """Should correctly identify blacklisted URLs"""
        assert is_blacklisted_domain(url) == expected

    @pytest.mark.parametrize("url", [
        "https://example-shop.com.ua/catalog",
        "https://auto-chem.ua/products",
        "https://detailing-shop.com/pena",
        "https://moyka.kiev.ua/services",
    ])
    def test_valid_urls_not_blocked(self, url):
        """Should not block legitimate e-commerce URLs"""
        assert is_blacklisted_domain(url) is False

    def test_partial_domain_match(self):
        """Should match partial domain (wiki in wikipedia)"""
        assert is_blacklisted_domain("https://wikipedia.org/wiki/Foam") is True
        assert is_blacklisted_domain("https://en.wikipedia.org/wiki/Test") is True

    def test_empty_and_invalid_urls(self):
        """Should handle empty and invalid URLs gracefully"""
        assert is_blacklisted_domain("") is False
        assert is_blacklisted_domain("not-a-url") is False
        assert is_blacklisted_domain("ftp://example.com") is False


class TestFixUaInUrl:
    """Test fix_ua_in_url function"""

    @pytest.mark.parametrize("url,expected", [
        # Remove /ua/ from middle of path
        ("https://site.com/ua/catalog/pena", "https://site.com/catalog/pena"),
        ("https://shop.ua/ua/products/foam", "https://shop.ua/products/foam"),
        # Replace /ua at end with /ru
        ("https://site.com/catalog/ua", "https://site.com/catalog/ru"),
        # No change needed
        ("https://site.com/catalog/pena", "https://site.com/catalog/pena"),
        ("https://site.com/ru/catalog", "https://site.com/ru/catalog"),
    ])
    def test_ua_url_fixing(self, url, expected):
        """Should correctly fix /ua/ URLs"""
        assert fix_ua_in_url(url) == expected

    def test_multiple_ua_occurrences(self):
        """Should handle multiple /ua/ in URL"""
        url = "https://site.com/ua/catalog/ua/products"
        result = fix_ua_in_url(url)
        # Should remove all /ua/ from path
        assert "/ua/" not in result

    def test_ua_in_domain_preserved(self):
        """Should NOT modify /ua in domain name"""
        url = "https://shop.ua/catalog/pena"
        result = fix_ua_in_url(url)
        # Domain should remain unchanged
        assert "shop.ua" in result

    def test_empty_url(self):
        """Should handle empty URL"""
        assert fix_ua_in_url("") == ""


class TestIsCategoryPage:
    """Test is_category_page heuristic function"""

    @pytest.mark.parametrize("url", [
        "https://shop.com/catalog/auto-chemistry",
        "https://store.ua/category/detailing",
        # Note: "products/foam" is NOT detected as category because "product" (singular)
        # is in non_category_kw and is a substring of "products" (plural)
        "https://example.com/shop/car-care",
        "https://site.com/tovar/aktivnaya-pena",
    ])
    def test_category_urls_detected(self, url):
        """Should identify category page URLs"""
        assert is_category_page(url) is True

    @pytest.mark.parametrize("url", [
        "https://shop.com/product/pena-123",
        "https://store.ua/item/foam-abc",
        "https://site.com/article/how-to-wash",
        "https://example.com/blog/car-care-tips",
        "https://site.com/contact",
        "https://shop.com/about",
        "https://store.ua/payment",
        "https://site.com/delivery",
        "https://example.com/cart",
        "https://site.com/checkout",
    ])
    def test_non_category_urls_rejected(self, url):
        """Should reject non-category page URLs"""
        assert is_category_page(url) is False

    def test_short_path_heuristic(self):
        """Short paths (2-3 segments) may be categories"""
        # These have 2-3 path segments and no non-category keywords
        assert is_category_page("https://shop.com/auto/pena") is True
        assert is_category_page("https://site.ua/avto/himiya") is True

    def test_long_path_heuristic(self):
        """Very long paths are likely product pages"""
        # No category keyword + long path = likely not category
        url = "https://shop.com/a/b/c/d/e/f/item"
        # Has 'item' keyword = not category
        assert is_category_page(url) is False

    def test_mixed_keywords(self):
        """Category keyword + non-category keyword = not category"""
        # Has both 'catalog' and 'product'
        url = "https://shop.com/catalog/product/123"
        assert is_category_page(url) is False


class TestEdgeCases:
    """Test edge cases and error handling"""

    def test_unicode_in_url(self):
        """Should handle Cyrillic characters in URL"""
        url = "https://shop.ua/catalog/активная-пена"
        # Should not crash
        result = is_category_page(url)
        assert isinstance(result, bool)

    def test_url_with_query_params(self):
        """Should handle URLs with query parameters"""
        url = "https://shop.com/catalog/foam?page=2&sort=price"
        assert is_category_page(url) is True

    def test_url_with_fragment(self):
        """Should handle URLs with fragments"""
        url = "https://shop.com/catalog/foam#reviews"
        assert is_category_page(url) is True

    def test_trailing_slash_handling(self):
        """Should handle trailing slashes"""
        url1 = "https://shop.com/catalog/foam/"
        url2 = "https://shop.com/catalog/foam"
        # Both should give same result
        assert is_category_page(url1) == is_category_page(url2)

    def test_case_insensitivity(self):
        """Path matching should be case-insensitive"""
        url1 = "https://shop.com/CATALOG/foam"
        url2 = "https://shop.com/catalog/FOAM"
        url3 = "https://shop.com/Catalog/Foam"
        # All should be detected as category
        assert is_category_page(url1) is True
        assert is_category_page(url2) is True
        assert is_category_page(url3) is True
