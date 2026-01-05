#!/usr/bin/env python3
"""
batch_generate.py — Batch Content Generation Orchestrator

Масштабирование генерации контента на 50+ категорий.

Features:
- Batch processing of multiple categories
- Progress logging (batch_log.json)
- Self-healing loop (auto-fix on validation errors)
- Resume from last failed category

Workflow per category:
1. analyze_category.py → context for LLM
2. (External) LLM generation
3. validate_content.py → quality check
4. If FAIL → retry with fixes

Usage:
    python3 scripts/batch_generate.py --list              # Show all categories
    python3 scripts/batch_generate.py --analyze-all       # Analyze all pending
    python3 scripts/batch_generate.py <slug>              # Process single category
    python3 scripts/batch_generate.py --all               # Process all categories
    python3 scripts/batch_generate.py --pending           # Process only pending
    python3 scripts/batch_generate.py --resume            # Resume from last failure
"""

import json
import subprocess
import sys
from datetime import UTC, datetime
from pathlib import Path


# =============================================================================
# Configuration
# =============================================================================

SCRIPT_DIR = Path(__file__).parent
PROJECT_ROOT = SCRIPT_DIR.parent
CATEGORIES_DIR = PROJECT_ROOT / "categories"
TASKS_DIR = PROJECT_ROOT / "data" / "tasks"
BATCH_LOG = TASKS_DIR / "batch_log.json"
SEMANTICS_CSV = PROJECT_ROOT / "data" / "Структура  Ultimate финал - Лист2.csv"

# Import from seo_utils (SSOT)
try:
    from scripts.seo_utils import L3_TO_SLUG, SLUG_TO_L3, slugify
except ImportError:
    try:
        from seo_utils import L3_TO_SLUG, SLUG_TO_L3, slugify
    except ImportError:
        print("Warning: seo_utils not found, using fallback")
        L3_TO_SLUG = {}
        SLUG_TO_L3 = {}

# =============================================================================
# Batch Log Management
# =============================================================================


def load_batch_log() -> dict:
    """Load batch processing log."""
    if BATCH_LOG.exists():
        with open(BATCH_LOG, encoding="utf-8") as f:
            return json.load(f)
    return {
        "created_at": datetime.now(UTC).isoformat(),
        "last_updated": None,
        "total_processed": 0,
        "total_success": 0,
        "total_failed": 0,
        "categories": {},
    }


def save_batch_log(log: dict):
    """Save batch processing log."""
    log["last_updated"] = datetime.now(UTC).isoformat()
    TASKS_DIR.mkdir(parents=True, exist_ok=True)
    with open(BATCH_LOG, "w", encoding="utf-8") as f:
        json.dump(log, f, ensure_ascii=False, indent=2)


def update_category_status(
    log: dict, slug: str, stage: str, status: str, details: dict | None = None
):
    """Update category status in batch log."""
    if slug not in log["categories"]:
        log["categories"][slug] = {"first_run": datetime.now(UTC).isoformat(), "runs": []}

    run = {
        "timestamp": datetime.now(UTC).isoformat(),
        "stage": stage,
        "status": status,
        "details": details or {},
    }

    log["categories"][slug]["runs"].append(run)
    log["categories"][slug]["last_status"] = status
    log["categories"][slug]["last_stage"] = stage

    save_batch_log(log)


# =============================================================================
# Category Discovery
# =============================================================================


def get_all_categories() -> list[dict]:
    """Get all categories from CSV with metadata."""
    import csv

    categories = []
    current_l3 = None
    current_keywords = []

    with open(SEMANTICS_CSV, encoding="utf-8") as f:
        reader = csv.reader(f)
        for row in reader:
            if not row or not row[0].strip():
                continue

            phrase = row[0].strip()

            # Detect L3 category
            if phrase.startswith("L3:"):
                # Save previous category
                if current_l3 and current_keywords:
                    slug = L3_TO_SLUG.get(current_l3) or slugify(current_l3)
                    categories.append(
                        {
                            "slug": slug,
                            "name": current_l3,
                            "keywords_count": len(current_keywords),
                            "total_volume": sum(kw.get("volume", 0) for kw in current_keywords),
                        }
                    )

                current_l3 = phrase.replace("L3:", "").strip()
                current_keywords = []
                continue

            # Skip L1, L2 headers
            if phrase.startswith("L1:") or phrase.startswith("L2:"):
                if current_l3 and current_keywords:
                    slug = L3_TO_SLUG.get(current_l3) or slugify(current_l3)
                    categories.append(
                        {
                            "slug": slug,
                            "name": current_l3,
                            "keywords_count": len(current_keywords),
                            "total_volume": sum(kw.get("volume", 0) for kw in current_keywords),
                        }
                    )
                current_l3 = None
                current_keywords = []
                continue

            # Parse keyword
            if current_l3:
                volume_str = row[2].strip() if len(row) > 2 else ""
                if volume_str.isdigit():
                    current_keywords.append({"keyword": phrase, "volume": int(volume_str)})

    # Don't forget the last category
    if current_l3 and current_keywords:
        slug = L3_TO_SLUG.get(current_l3) or slugify(current_l3)
        categories.append(
            {
                "slug": slug,
                "name": current_l3,
                "keywords_count": len(current_keywords),
                "total_volume": sum(kw.get("volume", 0) for kw in current_keywords),
            }
        )

    return categories


def get_category_status(slug: str, log: dict) -> dict:
    """Get current status of a category."""
    cat_log = log.get("categories", {}).get(slug, {})

    # Check files existence
    category_dir = CATEGORIES_DIR / slug
    has_clean_json = (category_dir / "data" / f"{slug}_clean.json").exists()
    has_raw_json = (category_dir / "data" / f"{slug}.json").exists()
    has_content = (category_dir / "content" / f"{slug}_ru.md").exists()
    has_meta = (category_dir / "meta" / f"{slug}_meta.json").exists()

    # Determine stage
    if has_content and has_meta:
        stage = "completed"
    elif has_content:
        stage = "content_generated"
    elif has_clean_json or has_raw_json:
        stage = "data_ready"
    else:
        stage = "pending"

    return {
        "slug": slug,
        "stage": stage,
        "has_clean_json": has_clean_json,
        "has_raw_json": has_raw_json,
        "has_content": has_content,
        "has_meta": has_meta,
        "last_status": cat_log.get("last_status", "unknown"),
        "runs_count": len(cat_log.get("runs", [])),
    }


# =============================================================================
# Pipeline Steps
# =============================================================================


def run_analyze(slug: str) -> tuple[bool, dict]:
    """Run analyze_category.py for a slug."""
    script = SCRIPT_DIR / "analyze_category.py"

    try:
        result = subprocess.run(  # noqa: S603
            ["python3", str(script), slug, "--json"],  # noqa: S607
            capture_output=True,
            text=True,
            timeout=60,
        )

        if result.returncode == 0:
            try:
                analysis = json.loads(result.stdout)
                return True, analysis
            except json.JSONDecodeError:
                return True, {"output": result.stdout}
        else:
            return False, {"error": result.stderr}

    except subprocess.TimeoutExpired:
        return False, {"error": "Timeout"}
    except Exception as e:
        return False, {"error": str(e)}


def run_validate(slug: str, primary_keyword: str) -> tuple[bool, dict]:
    """Run validate_content.py for a slug.

    FIX v8.5: Использует --json для надёжного парсинга результата
    вместо поиска строки "PASS" в output.
    """
    script = SCRIPT_DIR / "validate_content.py"
    content_file = CATEGORIES_DIR / slug / "content" / f"{slug}_ru.md"

    if not content_file.exists():
        return False, {"error": f"Content file not found: {content_file}"}

    try:
        # FIX: Используем --json для structured output
        result = subprocess.run(  # noqa: S603
            ["python3", str(script), str(content_file), primary_keyword, "--json"],  # noqa: S607
            capture_output=True,
            text=True,
            timeout=120,
        )  # noqa: S603, S607

        # Пытаемся распарсить JSON output
        try:
            data = json.loads(result.stdout)
            status = data.get("summary", {}).get("overall", "UNKNOWN")
            return status != "FAIL", {"status": status, "data": data}
        except json.JSONDecodeError:
            # Fallback: поиск строки если JSON не распарсился
            output = result.stdout + result.stderr
            if "PASS" in output:
                return True, {"status": "PASS", "output": output}
            elif "WARNING" in output:
                return True, {"status": "WARNING", "output": output}
            else:
                return False, {"status": "FAIL", "output": output}

    except subprocess.TimeoutExpired:
        return False, {"error": "Timeout"}
    except Exception as e:
        return False, {"error": str(e)}


# =============================================================================
# Self-Healing Loop
# =============================================================================

MAX_HEALING_ATTEMPTS = 3


def extract_issues_from_validation(validation: dict) -> list[str]:
    """Extract fixable issues from validation output."""
    issues = []
    data = validation.get("data")
    output = validation.get("output", "")

    if data:
        checks = data.get("checks", {})

        quality = checks.get("quality", {})
        water = quality.get("water", {})
        nausea = quality.get("nausea_classic", {})

        # Water/Nausea thresholds (SSOT)
        try:
            from scripts.config import QUALITY_THRESHOLDS
        except ImportError:
            from config import QUALITY_THRESHOLDS

        water_value = water.get("value")
        if water_value is not None and water_value > QUALITY_THRESHOLDS["water_target_max"]:
            issues.append("water_high")

        nausea_value = nausea.get("value")
        if nausea_value is not None and nausea_value > QUALITY_THRESHOLDS["nausea_classic_target"]:
            issues.append("nausea_high")

        coverage = checks.get("coverage", {})
        if coverage.get("core", {}).get("passed") is False or coverage.get("passed") is False:
            issues.append("coverage_low")

        structure = checks.get("structure", {})
        if not structure.get("h1", {}).get("passed", True):
            issues.append("h1_missing")

        primary_kw = checks.get("primary_keyword", {})
        if not primary_kw.get("in_intro", {}).get("passed", True):
            issues.append("intro_keyword_missing")

        blacklist = checks.get("blacklist", {})
        if blacklist.get("overall") == "FAIL":
            issues.append("blacklist_violation")

        if issues:
            return issues

    # Common issues patterns
    if "Water" in output and (">" in output or "высоко" in output.lower()):
        issues.append("water_high")
    if "Nausea" in output and (">" in output or "высоко" in output.lower()):
        issues.append("nausea_high")
    if "coverage" in output.lower() and ("<" in output or "низ" in output.lower()):
        issues.append("coverage_low")
    if "H1" in output and "не найден" in output.lower():
        issues.append("h1_missing")
    if "intro" in output.lower() and "не найден" in output.lower():
        issues.append("intro_keyword_missing")
    if "blacklist" in output.lower() or "запрещ" in output.lower():
        issues.append("blacklist_violation")

    return issues


def generate_fix_prompt(slug: str, issues: list[str], content: str) -> str:
    """Generate prompt for LLM to fix issues."""
    fix_instructions = []

    if "water_high" in issues:
        fix_instructions.append(
            "- Уменьшить воду: убрать водянистые фразы ('является', 'представляет собой', 'на сегодняшний день')"
        )

    if "nausea_high" in issues:
        fix_instructions.append("- Снизить тошноту: использовать синонимы для самого частого слова")

    if "coverage_low" in issues:
        fix_instructions.append(
            "- Повысить coverage: добавить больше ключевых слов естественно в текст"
        )

    if "h1_missing" in issues:
        fix_instructions.append("- Добавить H1 с primary keyword в начало")

    if "intro_keyword_missing" in issues:
        fix_instructions.append("- Добавить primary keyword в первые 100 слов (intro)")

    if "blacklist_violation" in issues:
        fix_instructions.append("- Удалить запрещённые фразы (бренды, города, AI-fluff)")

    return f"""
## Задача: Исправить контент для категории {slug}

### Обнаруженные проблемы:
{chr(10).join(fix_instructions)}

### Текущий контент:
```markdown
{content[:2000]}...
```

### Инструкции:
1. Исправь указанные проблемы
2. Сохрани структуру (H1, H2, FAQ)
3. Не добавляй новые секции без необходимости
4. Верни ПОЛНЫЙ исправленный markdown
"""


def attempt_self_heal(slug: str, validation: dict, attempt: int = 1) -> tuple[bool, str]:
    """
    Attempt to self-heal content based on validation errors.

    Returns:
        (success, message)
    """
    if attempt > MAX_HEALING_ATTEMPTS:
        return False, f"Max healing attempts ({MAX_HEALING_ATTEMPTS}) reached"

    issues = extract_issues_from_validation(validation)
    if not issues:
        return False, "No fixable issues detected"

    print(f"\n   [SELF-HEAL] Attempt {attempt}/{MAX_HEALING_ATTEMPTS}")
    print(f"   Issues detected: {', '.join(issues)}")

    # Read current content
    content_file = CATEGORIES_DIR / slug / "content" / f"{slug}_ru.md"
    if not content_file.exists():
        return False, "Content file not found"

    content = content_file.read_text(encoding="utf-8")

    # Generate fix prompt
    fix_prompt = generate_fix_prompt(slug, issues, content)

    # Note: Actual LLM call should be done externally
    # This returns the prompt for manual/external execution
    prompt_file = CATEGORIES_DIR / slug / "content" / f"{slug}_fix_prompt.md"
    prompt_file.write_text(fix_prompt, encoding="utf-8")

    print(f"   Fix prompt saved to: {prompt_file.name}")
    print(f"   Run LLM manually or use: 'исправь {slug}'")

    return False, "Fix prompt generated. Manual intervention required."


# =============================================================================
# Batch Processing
# =============================================================================


def process_category(
    slug: str, log: dict, analyze_only: bool = False, self_heal: bool = True
) -> bool:
    """Process a single category through the pipeline."""
    print(f"\n{'=' * 60}")
    print(f"Processing: {slug}")
    print(f"{'=' * 60}")

    # Step 1: Analyze
    print("\n[1/3] Analyzing category...")
    success, analysis = run_analyze(slug)

    if not success:
        print(f"   Analysis FAILED: {analysis.get('error')}")
        update_category_status(log, slug, "analyze", "FAIL", analysis)
        return False

    keywords = analysis.get("keywords", {})
    print(f"   Keywords: {keywords.get('count', 'N/A')}")
    print(f"   Semantic Depth: {keywords.get('semantic_depth', 'N/A')}")
    update_category_status(log, slug, "analyze", "PASS", analysis)

    if analyze_only:
        print("   (analyze-only mode, skipping generation)")
        return True

    # Step 2: Check if content exists (generation is external)
    content_file = CATEGORIES_DIR / slug / "content" / f"{slug}_ru.md"
    if not content_file.exists():
        print("\n[2/3] Content not found. Generate with LLM:")
        print(f"   Use: 'контент для {slug}' command")
        update_category_status(log, slug, "generate", "PENDING")
        return False

    print(f"\n[2/3] Content exists: {content_file.name}")

    # Step 3: Validate
    print("\n[3/3] Validating content...")
    # FIX: Правильный путь к primary keyword в структуре analyze_category.py
    keywords_data = analysis.get("keywords", {})
    primary_data = keywords_data.get("primary", {})
    primary_kw = primary_data.get("keyword", "") or slug.replace("-", " ")
    success, validation = run_validate(slug, primary_kw)

    status = validation.get("status", "UNKNOWN")
    if status == "PASS":
        print("   Validation: PASS")
        update_category_status(log, slug, "validate", "PASS", validation)
        log["total_success"] = log.get("total_success", 0) + 1
        return True
    elif status == "WARNING":
        print("   Validation: WARNING (acceptable)")
        update_category_status(log, slug, "validate", "WARNING", validation)
        return True
    else:
        print("   Validation: FAIL")
        update_category_status(log, slug, "validate", "FAIL", validation)

        # Attempt self-healing
        if self_heal:
            healed, msg = attempt_self_heal(slug, validation)
            if healed:
                # Re-validate after healing
                print("\n   Re-validating after self-heal...")
                success, validation = run_validate(slug, primary_kw)
                if validation.get("status") in ["PASS", "WARNING"]:
                    print("   Self-heal SUCCESSFUL!")
                    update_category_status(log, slug, "self_heal", "PASS", validation)
                    log["total_success"] = log.get("total_success", 0) + 1
                    return True
            else:
                print(f"   Self-heal: {msg}")

        log["total_failed"] = log.get("total_failed", 0) + 1
        return False


def process_all(only_pending: bool = False, analyze_only: bool = False):
    """Process all categories."""
    log = load_batch_log()
    categories = get_all_categories()

    print(f"\nFound {len(categories)} categories in CSV")
    print("=" * 60)

    processed = 0
    success = 0
    failed = 0

    for cat in categories:
        slug = cat["slug"]
        status = get_category_status(slug, log)

        # Skip completed if only_pending
        if only_pending and status["stage"] == "completed":
            print(f"Skipping {slug} (already completed)")
            continue

        processed += 1
        if process_category(slug, log, analyze_only):
            success += 1
        else:
            failed += 1

        log["total_processed"] = processed

    # Final report
    print("\n" + "=" * 60)
    print("BATCH PROCESSING COMPLETE")
    print("=" * 60)
    print(f"Total processed: {processed}")
    print(f"Success: {success}")
    print(f"Failed/Pending: {failed}")
    print(f"\nLog saved to: {BATCH_LOG}")

    save_batch_log(log)


def list_all_categories():
    """List all categories with status."""
    log = load_batch_log()
    categories = get_all_categories()

    print("\n" + "=" * 80)
    print("ALL CATEGORIES STATUS")
    print("=" * 80)
    print(f"{'Slug':<25} {'Keywords':>8} {'Stage':<18} {'Last Status':<12} {'Clean'}")
    print("-" * 80)

    for cat in sorted(categories, key=lambda x: -x["keywords_count"]):
        slug = cat["slug"]
        status = get_category_status(slug, log)

        clean_mark = "" if status["has_clean_json"] else "" if status["has_raw_json"] else ""

        print(
            f"{slug:<25} {cat['keywords_count']:>8} {status['stage']:<18} {status['last_status']:<12} {clean_mark}"
        )

    print("-" * 80)
    print(f"Total: {len(categories)} categories")

    # Summary
    stages = {}
    for cat in categories:
        slug = cat["slug"]
        status = get_category_status(slug, log)
        stage = status["stage"]
        stages[stage] = stages.get(stage, 0) + 1

    print("\nSummary:")
    for stage, count in sorted(stages.items()):
        print(f"  {stage}: {count}")


# =============================================================================
# CLI
# =============================================================================


def main():
    if len(sys.argv) < 2:
        print(__doc__)
        sys.exit(0)

    arg = sys.argv[1]

    if arg == "--list":
        list_all_categories()

    elif arg == "--analyze-all":
        process_all(only_pending=False, analyze_only=True)

    elif arg == "--all":
        process_all(only_pending=False)

    elif arg == "--pending":
        process_all(only_pending=True)

    elif arg == "--resume":
        log = load_batch_log()
        # Find last failed category
        for slug, cat_log in log.get("categories", {}).items():
            if cat_log.get("last_status") == "FAIL":
                print(f"Resuming from failed category: {slug}")
                process_category(slug, log)
                break
        else:
            print("No failed categories to resume")

    else:
        # Single category
        slug = arg
        log = load_batch_log()
        process_category(slug, log)


if __name__ == "__main__":
    main()
