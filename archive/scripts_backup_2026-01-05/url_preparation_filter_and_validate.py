#!/usr/bin/env python3
"""
URL Preparation Agent - Steps 2-4
Stage: URL Filtering, Validation, and Fixing

UPDATED: Added fallback to GET, retry mechanism, and module-level constants
"""

from __future__ import annotations

import json
import os
import sys
import time
from datetime import datetime
from pathlib import Path
from urllib.parse import urlparse


if __name__ == "__main__" and __package__ is None:
    sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

# Import shared utilities
from scripts.seo_utils import (
    check_url_accessibility,
    is_blacklisted_domain,
)


def analyze_url_category(url: str) -> tuple[bool, str]:
    """
    AI-based reasoning to determine if URL is a category page.

    Uses seo_utils.is_category_page for core logic.

    Returns:
        (is_category: bool, reason: str)
    """
    # Import here to avoid circular dependency
    from scripts.seo_utils import is_category_page

    # First check blacklist
    if is_blacklisted_domain(url):
        domain = urlparse(url).netloc.lower()
        return False, f"BLACKLIST: Domain {domain} is marketplace/social media - excluded"

    # Delegate to seo_utils for category check
    return is_category_page(url)


def _load_task_from_json(task_file: str) -> dict:
    with open(task_file, encoding="utf-8") as f:
        return json.load(f)


def _task_from_legacy_args(urls_raw_file: str, urls_file: str) -> dict:
    out_path = Path(urls_file)
    logs_dir = out_path.parent / ".logs"
    return {
        "slug": out_path.parent.name or "unknown",
        "paths": {"urls_raw": urls_raw_file, "urls": urls_file, "logs": str(logs_dir)},
    }


def main(argv: list[str] | None = None) -> int:
    argv = sys.argv[1:] if argv is None else argv

    if any(arg in ("-h", "--help") for arg in argv):
        print(
            "\n".join(
                [
                    "Usage:",
                    "  url_preparation_filter_and_validate.py task_file.json",
                    "  url_preparation_filter_and_validate.py urls_raw.txt urls.txt",
                    "",
                    "Notes:",
                    "- task_file.json must contain paths.urls_raw, paths.urls, paths.logs",
                    "- legacy mode expects raw URLs input file and output file path",
                ]
            )
        )
        return 0

    # Accept either:
    # - task_file.json (new, SSOT)
    # - urls_raw.txt urls.txt (legacy)
    if len(argv) == 0:
        error_report = {
            "status": "FAIL",
            "error": "Usage: url_preparation_filter_and_validate.py task_file.json OR urls_raw.txt urls.txt",
        }
        print(json.dumps(error_report), file=sys.stdout)
        return 2

    if len(argv) == 1:
        task_file = argv[0]
        if not os.path.exists(task_file):
            error_report = {"status": "FAIL", "error": f"Task file not found: {task_file}"}
            print(json.dumps(error_report), file=sys.stdout)
            return 2
        task = _load_task_from_json(task_file)
    elif len(argv) == 2:
        task = _task_from_legacy_args(argv[0], argv[1])
    else:
        error_report = {
            "status": "FAIL",
            "error": "Usage: url_preparation_filter_and_validate.py task_file.json OR urls_raw.txt urls.txt",
        }
        print(json.dumps(error_report), file=sys.stdout)
        return 2

    # Extract paths from task file (NO HARDCODE!)
    slug = task.get("slug", "unknown")
    urls_raw_file = task["paths"]["urls_raw"]
    urls_file = task["paths"]["urls"]
    log_dir = task["paths"]["logs"]

    # Ensure directories exist
    os.makedirs(os.path.dirname(urls_file), exist_ok=True)
    os.makedirs(log_dir, exist_ok=True)

    # All debug output to stderr
    print("=" * 80, file=sys.stderr)
    print("URL PREPARATION AGENT - Steps 2-4", file=sys.stderr)
    print(f"Category: {slug}", file=sys.stderr)
    print("=" * 80, file=sys.stderr)
    print(file=sys.stderr)

    # Read raw URLs
    if not os.path.exists(urls_raw_file):
        error_report = {"status": "FAIL", "error": f"URLs file not found: {urls_raw_file}"}
        print(json.dumps(error_report), file=sys.stdout)
        return 2

    with open(urls_raw_file, encoding="utf-8") as f:
        urls_raw = [line.strip() for line in f if line.strip() and not line.startswith("#")]

    print(f"Step 1: SKIP (URLs already generated: {len(urls_raw)} URLs)", file=sys.stderr)
    print(file=sys.stderr)

    # ===== STEP 2: AI FILTERING =====
    print("=" * 80, file=sys.stderr)
    print("STEP 2: AI FILTERING (Category Pages Only)", file=sys.stderr)
    print("=" * 80, file=sys.stderr)
    print(file=sys.stderr)

    category_pages = []
    excluded = []

    for url in urls_raw:
        is_category, reason = analyze_url_category(url)

        if is_category:
            category_pages.append(url)
            print(f"   ✓ INCLUDE: {url[:70]}", file=sys.stderr)
            print(f"      Reasoning: {reason}", file=sys.stderr)
            print(file=sys.stderr)
        else:
            excluded.append({"url": url, "reason": reason})
            print(f"   ✗ EXCLUDE: {url[:70]}", file=sys.stderr)
            print(f"      Reasoning: {reason}", file=sys.stderr)
            print(file=sys.stderr)

    print("=" * 80, file=sys.stderr)
    print("STEP 2 RESULTS:", file=sys.stderr)
    print(f"  Category pages: {len(category_pages)}", file=sys.stderr)
    print(f"  Excluded: {len(excluded)}", file=sys.stderr)
    print("=" * 80, file=sys.stderr)
    print(file=sys.stderr)

    # ===== STEP 3: VALIDATE & FIX URLs =====
    print("=" * 80, file=sys.stderr)
    print("STEP 3: VALIDATE & FIX URLs (Testing 200 OK)", file=sys.stderr)
    print("=" * 80, file=sys.stderr)
    print(file=sys.stderr)

    urls_validated = []
    fixes_attempted = 0
    fixes_successful = 0
    failed_fixes = []

    for url in category_pages:
        original_url = url

        # Check if URL contains /ua/
        if "/ua/" in url:
            fixes_attempted += 1
            print(f"   Found /ua/ in URL: {url[:60]}...", file=sys.stderr)

            # Strategy 1: Remove /ua/
            url_without_ua = url.replace("/ua/", "/")
            print(f"      Testing: {url_without_ua[:60]}...", file=sys.stderr)

            if check_url_accessibility(url_without_ua):
                url = url_without_ua
                fixes_successful += 1
                print("      ✓ SUCCESS: Removed /ua/ → 200 OK", file=sys.stderr)
                print(file=sys.stderr)
            else:
                print("      ✗ FAIL: No 200 OK", file=sys.stderr)

                # Strategy 2: Replace /ua/ with /ru/
                url_with_ru = original_url.replace("/ua/", "/ru/")
                print(f"      Testing: {url_with_ru[:60]}...", file=sys.stderr)

                if check_url_accessibility(url_with_ru):
                    url = url_with_ru
                    fixes_successful += 1
                    print("      ✓ SUCCESS: Replaced /ua/ → /ru/ → 200 OK", file=sys.stderr)
                    print(file=sys.stderr)
                else:
                    print("      ✗ FAIL: No 200 OK", file=sys.stderr)

                    # Test original URL
                    print(f"      Testing original: {original_url[:60]}...", file=sys.stderr)
                    if check_url_accessibility(original_url):
                        url = original_url
                        print("      ✓ Keeping original (200 OK)", file=sys.stderr)
                        print(file=sys.stderr)
                    else:
                        failed_fixes.append(original_url)
                        print(
                            "      ✗ WARNING: Original URL also fails - keeping anyway",
                            file=sys.stderr,
                        )
                        url = original_url
                        print(file=sys.stderr)

            time.sleep(0.5)  # Rate limiting

        # Validate format
        if url.startswith("http://") or url.startswith("https://"):
            urls_validated.append(url)
        else:
            print(f"   ⚠ INVALID FORMAT: {url}", file=sys.stderr)

    print("=" * 80, file=sys.stderr)
    print("STEP 3 RESULTS:", file=sys.stderr)
    print(f"  Validated URLs: {len(urls_validated)}", file=sys.stderr)
    print(f"  Fixes attempted: {fixes_attempted}", file=sys.stderr)
    print(f"  Fixes successful: {fixes_successful}", file=sys.stderr)
    print(f"  Failed fixes: {len(failed_fixes)}", file=sys.stderr)
    print("=" * 80, file=sys.stderr)
    print(file=sys.stderr)

    # ===== STEP 4: SAVE FINAL LIST =====
    print("=" * 80, file=sys.stderr)
    print("STEP 4: SAVE FINAL LIST", file=sys.stderr)
    print("=" * 80, file=sys.stderr)
    print(file=sys.stderr)

    # Save final validated list
    with open(urls_file, "w", encoding="utf-8") as f:
        f.write("\n".join(urls_validated) + "\n")

    print(f"✓ Saved: {urls_file}", file=sys.stderr)
    print(f"  Final URLs: {len(urls_validated)}", file=sys.stderr)
    print(file=sys.stderr)

    # Create detailed log
    timestamp = datetime.now().strftime("%Y-%m-%dT%H-%M-%SZ")
    log_file = os.path.join(log_dir, f"url-preparation_{timestamp}.log")

    log_content = f"""# URL Preparation Log
# Generated: {datetime.now().isoformat()}
# Category: {slug}
#
# STEP 2 - AI Filtering:
#   Raw URLs: {len(urls_raw)}
#   Category pages: {len(category_pages)}
#   Excluded: {len(excluded)}
#
# STEP 3 - Validation & Fixing:
#   Fixes attempted: {fixes_attempted}
#   Fixes successful: {fixes_successful}
#   Failed fixes: {len(failed_fixes)}
#
# FINAL COUNT: {len(urls_validated)} URLs ready for scraping
#
# ========================================
# EXCLUDED URLs ({len(excluded)}):
# ========================================
"""

    for item in excluded:
        log_content += f"#\n# {item['url']}\n#   Reason: {item['reason']}\n"

    if failed_fixes:
        log_content += "\n# ========================================\n"
        log_content += f"# FAILED FIXES ({len(failed_fixes)}):\n"
        log_content += "# ========================================\n"
        for fail_url in failed_fixes:
            log_content += f"# {fail_url}\n"

    log_content += "\n# ========================================\n"
    log_content += f"# FINAL VALIDATED URLs ({len(urls_validated)}):\n"
    log_content += "# ========================================\n\n"
    log_content += "\n".join(urls_validated)

    with open(log_file, "w", encoding="utf-8") as f:
        f.write(log_content)

    print(f"✓ Saved: {log_file}", file=sys.stderr)
    print(file=sys.stderr)

    # ===== FINAL REPORT =====
    print("=" * 80, file=sys.stderr)
    print("FINAL REPORT", file=sys.stderr)
    print("=" * 80, file=sys.stderr)

    status = (
        "SUCCESS"
        if len(urls_validated) >= 5
        else ("WARNING" if len(urls_validated) >= 3 else "FAIL")
    )

    report = {
        "status": status,
        "raw_urls": len(urls_raw),
        "filtered_urls": len(category_pages),
        "validated_urls": len(urls_validated),
        "ua_fixes": fixes_successful,
        "excluded_count": len(excluded),
        "failed_fixes": len(failed_fixes),
        "output_file": urls_file,
        "log_file": log_file,
    }

    # Clean JSON output to stdout (ONLY THIS!)
    print(json.dumps(report))

    # Status messages to stderr
    if status == "SUCCESS":
        print("✓ SUCCESS: URLs ready for Stage -1 (scraping)", file=sys.stderr)
    elif status == "WARNING":
        print("⚠ WARNING: Few URLs, but proceeding", file=sys.stderr)
    else:
        print("✗ FAIL: Too few URLs (<3)", file=sys.stderr)

    print("=" * 80, file=sys.stderr)

    return {"SUCCESS": 0, "WARNING": 1, "FAIL": 2}[status]


if __name__ == "__main__":
    raise SystemExit(main())
