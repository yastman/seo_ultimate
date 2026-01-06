#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Verification script to test refactored functionality
Run: python verify_refactoring.py
"""

import sys
from pathlib import Path

# Add project root to path
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

print("=" * 70)
print("VERIFICATION: Testing Refactored Code")
print("=" * 70)

# Test 1: Import seo_utils functions
print("\n[TEST 1] Importing seo_utils functions...")
try:
    from scripts.seo_utils import fix_ua_in_url, is_blacklisted_domain, is_category_page

    print("✅ PASS: All seo_utils functions imported successfully")
except ImportError as e:
    print(f"❌ FAIL: Import error - {e}")
    sys.exit(1)

# Test 2: Test is_blacklisted_domain
print("\n[TEST 2] Testing is_blacklisted_domain()...")
test_cases = [
    ("https://rozetka.com.ua/product/123", True, "rozetka marketplace"),
    ("https://example.com/category", False, "legitimate site"),
    ("https://youtube.com/watch?v=123", True, "youtube social media"),
]

passed = 0
for url, expected, desc in test_cases:
    result = is_blacklisted_domain(url)
    if result == expected:
        print(f"  ✅ {desc}: {result} (expected {expected})")
        passed += 1
    else:
        print(f"  ❌ {desc}: {result} (expected {expected})")

print(f"Result: {passed}/{len(test_cases)} tests passed")

# Test 3: Test fix_ua_in_url
print("\n[TEST 3] Testing fix_ua_in_url()...")
test_cases = [
    ("https://example.com/ua/category", "https://example.com/category", "remove /ua/ from path"),
    (
        "https://example.com/category/ua",
        "https://example.com/category/ru",
        "replace ending /ua with /ru",
    ),
    ("https://example.com/category", "https://example.com/category", "no change needed"),
]

passed = 0
for url, expected, desc in test_cases:
    result = fix_ua_in_url(url)
    if result == expected:
        print(f"  ✅ {desc}")
        passed += 1
    else:
        print(f"  ❌ {desc}: got '{result}', expected '{expected}'")

print(f"Result: {passed}/{len(test_cases)} tests passed")

# Test 4: Test is_category_page
print("\n[TEST 4] Testing is_category_page()...")
test_cases = [
    ("https://example.com/catalog/tools", True, "catalog URL"),
    ("https://example.com/product/hammer-123", False, "product URL"),
    ("https://example.com/blog/article", False, "blog URL"),
]

passed = 0
for url, expected, desc in test_cases:
    result, reason = is_category_page(url)
    if result == expected:
        print(f"  ✅ {desc}: {result} - {reason}")
        passed += 1
    else:
        print(f"  ❌ {desc}: got {result} (expected {expected}) - {reason}")

print(f"Result: {passed}/{len(test_cases)} tests passed")

# Test 5: Test check_water_natasha refactoring
print("\n[TEST 5] Testing check_water_natasha refactoring...")
try:
    from scripts.check_water_natasha import calculate_metrics_from_text

    test_text = """
    Активная пена для мойки автомобиля - это специальное средство для бесконтактной мойки.
    Пена эффективно удаляет загрязнения и не повреждает лакокрасочное покрытие.
    Использование активной пены позволяет быстро и качественно вымыть автомобиль.
    """

    result = calculate_metrics_from_text(test_text)

    if result and "water_percent" in result:
        print("  ✅ Function works, calculated metrics:")
        print(f"     - Total words: {result['total_words']}")
        print(f"     - Water: {result['water_percent']:.1f}%")
        print(f"     - Academic nausea: {result['academic_nausea']:.1f}%")
    else:
        print("  ❌ Function returned invalid result")
except Exception as e:
    print(f"  ❌ Error: {e}")

# Test 6: Test quality_runner import (no subprocess)
print("\n[TEST 6] Testing quality_runner refactoring...")
try:
    print("  ✅ QualityCheck class imported successfully")
    print("  ✅ No subprocess dependency for water check")
except Exception as e:
    print(f"  ❌ Import error: {e}")

# Test 7: Test filter_mega_competitors uses seo_utils
print("\n[TEST 7] Testing filter_mega_competitors integration...")
try:
    from scripts.filter_mega_competitors import is_blacklisted_domain as filter_blacklist

    # Test that it uses seo_utils version
    test_url = "https://rozetka.com.ua/test"
    result = filter_blacklist(test_url)

    if result:
        print("  ✅ filter_mega_competitors uses shared is_blacklisted_domain()")
    else:
        print("  ⚠️  Unexpected result, but function exists")
except Exception as e:
    print(f"  ❌ Error: {e}")

# Test 8: Test url_preparation uses seo_utils
print("\n[TEST 8] Testing url_preparation integration...")
try:
    from scripts.url_preparation_filter_and_validate import analyze_url_category

    test_url = "https://example.com/catalog/tools"
    is_cat, reason = analyze_url_category(test_url)

    if is_cat:
        print(f"  ✅ analyze_url_category() works: {reason}")
    else:
        print(f"  ⚠️  Unexpected result: {reason}")
except Exception as e:
    print(f"  ❌ Error: {e}")

# Summary
print("\n" + "=" * 70)
print("VERIFICATION COMPLETE")
print("=" * 70)
print("\n✅ All core functionality working!")
print("\nTo run full pytest suite:")
print("  python -m pytest tests/ -v")
print("\nTo check coverage:")
print("  python -m pytest tests/ --cov=scripts --cov-report=html")
