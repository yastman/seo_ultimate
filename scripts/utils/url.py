import time
from urllib.parse import urlparse

import requests

# ============================================================================
# Check URL Accessibility
# ============================================================================


def check_url_accessibility(url: str, timeout: int = 5, max_retries: int = 3) -> bool:
    """
    Check if URL is accessible (returns 200 OK)

    Args:
        url: URL to check
        timeout: request timeout (seconds)
        max_retries: maximum number of retry attempts

    Returns:
        bool: True if accessible (200 OK)
    """
    # Retry configuration
    RETRY_BACKOFF_FACTOR = 1.5

    for attempt in range(max_retries):
        try:
            # Try HEAD first (lightweight)
            response = requests.head(url, timeout=timeout, allow_redirects=True)
            if response.status_code == 200:
                return True

            # Fallback to GET if HEAD returned non-200
            response = requests.get(url, timeout=timeout, allow_redirects=True, stream=True)
            if response.status_code == 200:
                response.close()
                return True

            return False

        except (requests.exceptions.Timeout, requests.exceptions.ConnectionError):
            # Retry on timeout or connection errors
            if attempt < max_retries - 1:
                wait_time = RETRY_BACKOFF_FACTOR**attempt
                time.sleep(wait_time)
                continue

    return False


# ============================================================================
# URL Validation & Filtering
# ============================================================================

# Default blacklist (can be overridden)
DEFAULT_BLACKLIST_DOMAINS = [
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


def is_blacklisted_domain(url: str, blacklist: list[str] | None = None) -> bool:
    """
    Check if URL domain is in blacklist

    Args:
        url: URL to check
        blacklist: Custom blacklist (defaults to DEFAULT_BLACKLIST_DOMAINS)

    Returns:
        True if domain is blacklisted
    """
    if blacklist is None:
        blacklist = DEFAULT_BLACKLIST_DOMAINS

    try:
        parsed = urlparse(url)
        domain = parsed.netloc.lower().replace("www.", "")
        return any(bl in domain for bl in blacklist)
    except Exception:
        return False


def fix_ua_in_url(url: str) -> str:
    """
    Fix /ua/ in URL: remove /ua/ or replace with /ru/

    Strategy:
    1. Remove /ua/ from path
    2. If URL ends with /ua, replace with /ru

    Args:
        url: URL to fix

    Returns:
        Fixed URL
    """
    if "/ua/" not in url and not url.endswith("/ua"):
        return url

    # Remove /ua/ from path
    url_fixed = url.replace("/ua/", "/")

    # If URL ends with /ua, replace with /ru
    if url.endswith("/ua"):
        url_fixed = url.replace("/ua", "/ru")

    return url_fixed


def is_category_page(url: str) -> tuple[bool, str]:
    """
    Heuristic check if URL is a category page

    Returns:
        (is_category, reason)
    """
    path = urlparse(url).path.lower()

    # Category indicators
    category_kw = ["catalog", "category", "categories", "products", "shop", "tovar", "katalog"]

    # Non-category indicators
    non_category_kw = [
        "product",
        "item",
        "article",
        "news",
        "blog",
        "contact",
        "about",
        "payment",
        "delivery",
        "dostavka",
        "oplata",
        "cart",
        "checkout",
        "search",
        "login",
        "register",
    ]

    has_category = any(kw in path for kw in category_kw)
    has_non_category = any(kw in path for kw in non_category_kw)

    # Heuristic: category if has category keyword AND no non-category keywords
    if has_category and not has_non_category:
        return True, "Has category keyword and no non-category patterns"

    # Fallback: short paths (2-3 segments) are likely categories
    path_segments = [p for p in path.split("/") if p and p not in ("ru", "ua")]
    if 2 <= len(path_segments) <= 3 and not has_non_category:
        return True, "Short path with no non-category indicators"

    return False, "Does not match category patterns"
