#!/usr/bin/env python3
"""
parse_semantics_to_json.py — SEO Keywords Parser

Читает CSV семантики и создаёт полный JSON с keywords для валидатора.

Input:
    - data/Структура Ultimate финал - Лист2.csv (семантика с L1/L2/L3 и volumes)
    - categories/{slug}/competitors/meta_patterns.json (optional, для semantic_entities)

Output:
    - categories/{slug}/data/{slug}.json (полный формат с variations)

Usage:
    python3 scripts/parse_semantics_to_json.py aktivnaya-pena B
    python3 scripts/parse_semantics_to_json.py --list  # показать все L3 категории

Classification by volume:
    - PRIMARY: >500
    - SECONDARY: 100-500
    - SUPPORTING: <100

Variations Generation:
    - Группирует похожие keywords (Levenshtein distance или общие слова)
    - exact: основная форма
    - partial: корни слов для partial matching
"""

import csv
import json
import sys
from datetime import datetime
from pathlib import Path

if __name__ == "__main__" and __package__ is None:
    sys.path.insert(0, str(Path(__file__).resolve().parent.parent))


# =============================================================================
# Configuration
# =============================================================================

SCRIPT_DIR = Path(__file__).parent
PROJECT_ROOT = SCRIPT_DIR.parent
SEMANTICS_CSV = PROJECT_ROOT / "data" / "Структура  Ultimate финал - Лист2.csv"

# Volume thresholds for classification
VOLUME_PRIMARY = 500  # >500 = PRIMARY
VOLUME_SECONDARY = 100  # 100-500 = SECONDARY
# <100 = SUPPORTING

# L3 name to slug mapping - imported from seo_utils.py (SSOT)
try:
    from scripts.seo_utils import L3_TO_SLUG, SLUG_TO_L3, get_l3_slug
except ImportError:
    try:
        from seo_utils import L3_TO_SLUG, SLUG_TO_L3, get_l3_slug
    except ImportError:
        # Fallback for standalone execution
        L3_TO_SLUG = {
            "Активная пена": "aktivnaya-pena",
            "Для ручной мойки": "dlya-ruchnoy-moyki",
            "Очистители стекол": "ochistiteli-stekol",
            "Глина и автоскрабы": "glina-i-avtoskraby",
            "Антимошка": "antimoshka",
            "Антибитум": "antibitum",
            "Чернители шин": "cherniteli-shin",
            "Очистители дисков": "ochistiteli-diskov",
            "Очистители шин": "ochistiteli-shin",
            "Аппараты Tornador": "apparaty-tornador",
            "Меховые": "mekhovye",
            "Поролоновые": "porolonovye",
            "Наборы для мойки": "nabory-dlya-moyki",
            "Наборы для полировки": "nabory-dlya-polirovki",
            "Наборы для ухода за кожей": "nabory-dlya-ukhoda-za-kozhey",
            "Наборы для химчистки": "nabory-dlya-khimchistki",
            "Подарочные наборы": "podarochnye-nabory",
        }
        SLUG_TO_L3 = {v: k for k, v in L3_TO_SLUG.items()}

        def get_l3_slug(name):
            return L3_TO_SLUG.get(name, name.lower().replace(" ", "-"))


# =============================================================================
# Core Functions
# =============================================================================


def read_semantics_csv(csv_path: str) -> dict[str, list[dict]]:
    """
    Читает CSV семантики и возвращает keywords по категориям L3.

    Returns:
        {
            "Активная пена": [
                {"keyword": "...", "volume": 1300},
                ...
            ],
            ...
        }
    """
    categories: dict[str, list[dict]] = {}
    current_l3: str | None = None
    # expected_keywords: int | None = None
    # collected_keywords = 0

    with open(csv_path, encoding="utf-8") as f:
        reader = csv.reader(f)
        for row in reader:
            # Empty rows are common in the real export and may appear *inside* an L3 block.
            # They should not reset the current context; just skip them.
            if not row or all((not cell) or (not cell.strip()) for cell in row):
                continue

            if not row[0] or not row[0].strip():
                continue

            phrase = row[0].strip()
            volume_str = row[2].strip() if len(row) > 2 else ""

            # Detect L3 category
            if phrase.startswith("L3:"):
                current_l3 = phrase.replace("L3:", "").strip()

                if current_l3 not in categories:
                    categories[current_l3] = []
                continue

            # Skip L1, L2 headers
            if phrase.startswith("L1:") or phrase.startswith("L2:"):
                current_l3 = None
                continue

            # Skip SEO filter / section headers inside blocks
            if phrase.startswith("SEO-Фильтр:"):
                continue

            # Real CSV sometimes has unprefixed boundary rows like: "категория,16,"
            # If we are inside an L3 block, treat this as the end of the block.
            count_str = row[1].strip() if len(row) > 1 else ""
            if current_l3 and phrase.lower() == "категория" and count_str.isdigit() and not volume_str:
                current_l3 = None
                continue

            if not current_l3:
                continue

            # Skip subsection headers like: "Омыватель,35," or "Защитные ... ,2,"
            count_str = row[1].strip() if len(row) > 1 else ""
            if count_str and not volume_str:
                # Do not treat as keyword
                continue

            # Regular keyword requires numeric volume (including 0)
            if not volume_str.isdigit():
                continue

            volume = int(volume_str)
            categories[current_l3].append({"keyword": phrase, "volume": volume})

    return categories


def classify_keywords(keywords: list[dict]) -> dict[str, list[dict]]:
    """
    Классифицирует keywords по volume в PRIMARY/SECONDARY/SUPPORTING.
    """
    result = {"primary": [], "secondary": [], "supporting": []}

    # Sort by volume descending
    sorted_kws = sorted(keywords, key=lambda x: -x["volume"])

    for kw in sorted_kws:
        vol = kw["volume"]
        if vol > VOLUME_PRIMARY:
            result["primary"].append(kw)
        elif vol >= VOLUME_SECONDARY:
            result["secondary"].append(kw)
        else:
            result["supporting"].append(kw)

    # Ensure at least one PRIMARY keyword only when everything is supporting.
    if not result["primary"] and not result["secondary"] and result["supporting"]:
        promoted_kw = result["supporting"][0]
        result["primary"].append(promoted_kw)
        # Remove from supporting to avoid double-counting
        result["supporting"] = [kw for kw in result["supporting"] if kw != promoted_kw]

    return result


def extract_word_roots(keyword: str) -> list[str]:
    """
    Извлекает корни слов для partial matching.
    Убирает окончания русских слов.
    """
    words = keyword.lower().split()
    roots = []

    # Common Russian word endings to remove
    endings = [
        "ой",
        "ый",
        "ая",
        "ое",
        "ые",
        "ых",
        "ом",
        "ем",
        "ам",
        "ям",
        "ов",
        "ев",
        "ей",
        "ию",
        "ью",
        "ия",
        "ья",
        "ье",
        "ий",
        "ать",
        "ять",
        "еть",
        "ить",
        "уть",
        "ыть",
        "ка",
        "ки",
        "ку",
        "ке",
        "ок",
        "ек",
        "ик",
        "ого",
        "его",
        "ому",
        "ему",
        "ими",
        "ыми",
    ]

    for word in words:
        if len(word) < 4:
            continue

        root = word
        for ending in endings:
            if word.endswith(ending) and len(word) - len(ending) >= 3:
                root = word[: -len(ending)]
                break

        if len(root) >= 3:
            roots.append(root)

    return roots


def generate_variations(keyword: str, all_keywords: list[str]) -> dict[str, list[str]]:
    """
    Генерирует variations для keyword:
    - exact: сам keyword + похожие формы (падежи)
    - partial: корни для partial matching
    """
    exact = [keyword]
    partial = []

    # Find similar keywords (same root words)
    kw_words = set(keyword.lower().split())

    for other_kw in all_keywords:
        if other_kw == keyword:
            continue

        other_words = set(other_kw.lower().split())

        # If >70% words overlap, consider it a variation
        common = kw_words & other_words
        if len(common) >= len(kw_words) * 0.7 and other_kw not in exact:
            exact.append(other_kw)

    # Extract roots for partial matching
    roots = extract_word_roots(keyword)
    for root in roots:
        if root not in partial and len(root) >= 4:
            partial.append(root)

    return {
        "exact": exact[:5],  # Limit to 5 exact forms
        "partial": partial[:5],  # Limit to 5 partial forms
    }


def calculate_density_target(volume: int, total_volume: int, tier: str) -> str:
    """
    Рассчитывает target density на основе volume.
    """
    if total_volume == 0:
        return "0.10%"

    # Relative importance
    ratio = volume / total_volume

    if ratio > 0.15:
        return "0.20%"
    elif ratio > 0.08:
        return "0.15%"
    elif ratio > 0.03:
        return "0.10%"
    else:
        return "0.05%"


def calculate_occurrences_target(volume: int, tier: str) -> int:
    """
    Рассчитывает target occurrences на основе volume и tier.
    """
    if volume > 1000:
        return 5
    elif volume > 500:
        return 4
    elif volume > 100:
        return 3
    elif volume > 50:
        return 2
    else:
        return 1


def build_keyword_object(
    keyword: str, volume: int, kw_type: str, all_keywords: list[str], total_volume: int, tier: str
) -> dict:
    """
    Создаёт полный объект keyword для JSON.
    """
    variations = generate_variations(keyword, all_keywords)

    return {
        "keyword": keyword,
        "volume": volume,
        "intent": "commercial" if "купить" in keyword.lower() else "informational",
        "density_target": calculate_density_target(volume, total_volume, tier),
        "occurrences_target": calculate_occurrences_target(volume, tier),
        "variations": variations,
    }


def read_meta_patterns(slug: str) -> dict | None:
    """
    Читает meta_patterns.json если существует.
    """
    path = Path(f"categories/{slug}/competitors/meta_patterns.json")
    if path.exists():
        with open(path, encoding="utf-8") as f:
            return json.load(f)
    return None


# Validating imports
try:
    # Try importing if running as module or from root with scripts in path
    from scripts.seo_utils import get_tier_requirements
except ImportError:
    try:
        # Try direct import if running from scripts dir
        from seo_utils import get_tier_requirements
    except ImportError:
        # Fallback: Add script dir to path
        sys.path.append(str(Path(__file__).parent))
        from seo_utils import get_tier_requirements


def get_tier_targets(tier: str) -> dict:
    """
    Возвращает targets по tier из seo_utils (v7.3 Shop Mode).
    Wrapper for compatibility.
    """
    reqs = get_tier_requirements(tier)

    # Map seo_utils keys to JSON format keys if different
    # seo_utils: char_min, char_max, h2_range=(min, max), faq_range=(min, max)

    # Convert ranges to strings "min-max"
    h2_min, h2_max = reqs.get("h2_range", (3, 5))
    faq_min, faq_max = reqs.get("faq_range", (3, 6))

    return {
        "char_min": reqs.get("char_min", 2000),
        "char_max": reqs.get("char_max", 2500),
        "h2": f"{h2_min}-{h2_max}",
        "faq": f"{faq_min}-{faq_max}",
    }


def generate_full_json(slug: str, tier: str, keywords_raw: list[dict]) -> dict:
    """
    Генерирует полный JSON для категории.
    """
    # Classify keywords
    classified = classify_keywords(keywords_raw)

    # Get all keyword strings for variation matching
    all_kw_strings = [kw["keyword"] for kw in keywords_raw]

    # Calculate total volume
    total_volume = sum(kw["volume"] for kw in keywords_raw)

    # Build keyword objects
    keywords = {"primary": [], "secondary": [], "supporting": []}

    for kw_type in ["primary", "secondary", "supporting"]:
        for kw in classified[kw_type]:
            kw_obj = build_keyword_object(kw["keyword"], kw["volume"], kw_type, all_kw_strings, total_volume, tier)
            keywords[kw_type].append(kw_obj)

    # Read meta_patterns if available
    meta_patterns = read_meta_patterns(slug)
    semantic_entities = []

    if meta_patterns and "h2_themes" in meta_patterns:
        # Convert h2_themes to semantic entities
        for theme in meta_patterns["h2_themes"]:
            if isinstance(theme, str) and len(theme) > 5:
                semantic_entities.append({"main": theme, "related": [], "source": "competitors_h2_themes"})

    # Get tier targets
    tier_targets = get_tier_targets(tier)

    # Build full JSON
    result = {
        "schema_version": "3.0.0",
        "generated_at": datetime.utcnow().isoformat() + "Z",
        "generator_script": "parse_semantics_to_json.py",
        "slug": slug,
        "category_name_ru": SLUG_TO_L3.get(slug, slug),
        "tier": tier.upper(),
        "language": "ru",
        "keywords": keywords,
        "semantic_entities": semantic_entities,
        "content_targets": {
            "char_count_no_spaces": f"{tier_targets['char_min']}-{tier_targets['char_max']}",
            "h2_count": tier_targets["h2"],
            "faq_count": tier_targets["faq"],
            "coverage_target": 50,  # v7.3: minimum 50%, ideal 50-60%
            "density_target": "1-2%",
            "lsi_ratio": ">=5:1",
        },
        "stats": {
            "total_keywords": len(keywords_raw),
            "total_volume": total_volume,
            "primary_count": len(keywords["primary"]),
            "secondary_count": len(keywords["secondary"]),
            "supporting_count": len(keywords["supporting"]),
        },
    }

    return result


# =============================================================================
# CLI
# =============================================================================


def list_categories():
    """Показать все доступные L3 категории."""
    print("=== Доступные категории (L3) ===\n")

    categories = read_semantics_csv(SEMANTICS_CSV)

    for l3_name, keywords in sorted(categories.items(), key=lambda x: -len(x[1])):
        slug = L3_TO_SLUG.get(l3_name, "???")
        total_vol = sum(kw["volume"] for kw in keywords)
        print(f"  {slug:25s} ({l3_name})")
        print(f"    Keywords: {len(keywords):3d}, Volume: {total_vol:5d}")
        print()


def main():
    if len(sys.argv) < 2:
        print("Usage:")
        print("  python3 scripts/parse_semantics_to_json.py <slug> <tier>")
        print("  python3 scripts/parse_semantics_to_json.py --list")
        print()
        print("Example:")
        print("  python3 scripts/parse_semantics_to_json.py aktivnaya-pena B")
        sys.exit(1)

    if sys.argv[1] == "--list":
        list_categories()
        sys.exit(0)

    slug = sys.argv[1]
    tier = sys.argv[2] if len(sys.argv) > 2 else "B"

    # Get L3 name from slug
    l3_name = SLUG_TO_L3.get(slug)
    if not l3_name:
        print(f"❌ Unknown slug: {slug}")
        print(f"   Available: {list(SLUG_TO_L3.keys())}")
        sys.exit(1)

    # Read semantics
    print(f"📖 Reading: {SEMANTICS_CSV}")
    categories = read_semantics_csv(SEMANTICS_CSV)

    if l3_name not in categories:
        print(f"❌ Category not found: {l3_name}")
        sys.exit(1)

    keywords_raw = categories[l3_name]
    print(f"✅ Found {len(keywords_raw)} keywords for '{l3_name}'")

    # Generate JSON
    print(f"🔧 Generating JSON (tier={tier})...")
    result = generate_full_json(slug, tier, keywords_raw)

    # Output path
    output_dir = Path(f"categories/{slug}/data")
    output_dir.mkdir(parents=True, exist_ok=True)
    output_path = output_dir / f"{slug}.json"

    # Write JSON
    with open(output_path, "w", encoding="utf-8") as f:
        json.dump(result, f, ensure_ascii=False, indent=2)

    print(f"✅ Written: {output_path}")
    print()
    print("📊 Stats:")
    print(f"   PRIMARY:    {result['stats']['primary_count']} keywords")
    print(f"   SECONDARY:  {result['stats']['secondary_count']} keywords")
    print(f"   SUPPORTING: {result['stats']['supporting_count']} keywords")
    print(f"   Total:      {result['stats']['total_keywords']} keywords, volume {result['stats']['total_volume']}")


if __name__ == "__main__":
    main()
