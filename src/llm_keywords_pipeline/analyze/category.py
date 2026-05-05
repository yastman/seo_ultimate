#!/usr/bin/env python3
"""
analyze_category.py — Category Analysis for LLM (Google 2025 Approach)

Анализирует категорию и выдаёт рекомендации для LLM.
НЕ использует tier-based подход. Вместо этого — адаптивный анализ.

D+E Fallback Pattern:
1. Сначала ищет _clean.json (12 clustered keywords)
2. Затем ищет raw .json (52 keywords)
3. Fallback на CSV если JSON нет

Принцип (Google December 2025):
- Depth over length
- Editorial content = buying guide
- Intent matching > keyword density
- Relative usefulness

Output:
- JSON с метриками и рекомендациями для LLM
- LLM решает длину контента на основе семантической глубины

Usage:
    python3 scripts/analyze_category.py <slug>
    python3 scripts/analyze_category.py <slug> --json
    python3 scripts/analyze_category.py --list
"""

import csv
import json
import sys
from datetime import UTC, datetime
from pathlib import Path

# =============================================================================
# Configuration
# =============================================================================

SCRIPT_DIR = Path(__file__).parent
PROJECT_ROOT = SCRIPT_DIR.parent
SEMANTICS_CSV = PROJECT_ROOT / "Структура _Ultimate.csv"
CATEGORIES_DIR = PROJECT_ROOT / "categories"


# Language-specific paths
def get_categories_dir(lang: str = "ru") -> Path:
    """Get categories directory based on language."""
    if lang == "uk":
        return PROJECT_ROOT / "uk" / "categories"
    return PROJECT_ROOT / "categories"


# Current language (set by main)
CURRENT_LANG = "ru"

# =============================================================================
# D+E Fallback: Load keywords from best available source
# =============================================================================


def load_keywords_for_slug(slug: str, lang: str = "ru") -> tuple[list[dict], str, dict | None]:
    """
    D+E Fallback Pattern: Load keywords from best available source.

    Priority:
    1. {slug}_clean.json — clustered (12 keywords)
    2. {slug}.json — raw parsed (52 keywords)
    3. CSV fallback

    Args:
        slug: Category slug
        lang: Language code ("ru" or "uk")

    Returns:
        Tuple[List[Dict], str, Optional[Dict]]:
            - keywords list (normalized to {keyword, volume})
            - source: "clean_json", "raw_json", or "csv"
            - extra_data: seo_titles, entity_dictionary, content_rules (from clean.json)
    """
    categories_dir = get_categories_dir(lang)
    category_dir = categories_dir / slug / "data"

    # 1. Try _clean.json first (preferred)
    clean_json = category_dir / f"{slug}_clean.json"
    if clean_json.exists():
        with open(clean_json, encoding="utf-8") as f:
            data = json.load(f)

        # Extract keywords from clean format (clustered).
        # Clean JSON in this project includes 12 keywords total:
        # primary + secondary + supporting + commercial (meta-only).
        keywords = []
        for category in ["primary", "secondary", "supporting", "commercial"]:
            for kw in data.get("keywords", {}).get(category, []):
                # Commercial keywords are meta-only by convention.
                use_in = kw.get("use_in")
                target = 0 if use_in == "meta_only" else kw.get("target", 1)
                keywords.append(
                    {
                        "keyword": kw["keyword"],
                        "volume": kw.get("volume", 0),
                        "cluster": kw.get("cluster", "unknown"),
                        "target": target,
                    }
                )

        extra_data = {
            "seo_titles": data.get("seo_titles"),
            "entity_dictionary": data.get("entity_dictionary"),
            "content_rules": data.get("content_rules"),
            "stats": data.get("stats"),
        }

        return keywords, "clean_json", extra_data

    # 2. Try raw .json
    raw_json = category_dir / f"{slug}.json"
    if raw_json.exists():
        with open(raw_json, encoding="utf-8") as f:
            data = json.load(f)

        # Extract keywords from raw format
        keywords = []
        for category in ["primary", "secondary", "supporting"]:
            for kw in data.get("keywords", {}).get(category, []):
                keywords.append({"keyword": kw["keyword"], "volume": kw.get("volume", 0)})

        return keywords, "raw_json", None

    # 3. Fallback to CSV
    l3_name = SLUG_TO_L3.get(slug)
    if not l3_name:
        return [], "csv", None

    categories = read_semantics_csv(str(SEMANTICS_CSV))
    keywords = categories.get(l3_name, [])

    return keywords, "csv", None


# L3 name to slug mapping - imported from seo_utils.py (SSOT)
try:
    from scripts.seo_utils import L3_TO_SLUG, SLUG_TO_L3, get_commercial_modifiers, get_l3_slug
except ImportError:
    try:
        from seo_utils import L3_TO_SLUG, SLUG_TO_L3, get_commercial_modifiers, get_l3_slug
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

        _COMMERCIAL_MODIFIERS_FALLBACK = [
            "купить",
            "цена",
            "стоимость",
            "заказать",
            "в наличии",
            "доставка",
            "недорого",
            "дёшево",
            "дешево",
            "интернет-магазин",
            "магазин",
            "каталог",
        ]
        _COMMERCIAL_MODIFIERS_UK_FALLBACK = [
            "купити",
            "ціна",
            "вартість",
            "замовити",
            "в наявності",
            "доставка",
            "недорого",
            "дешево",
            "інтернет-магазин",
            "магазин",
            "каталог",
        ]

        def get_commercial_modifiers(lang="ru"):
            return (
                _COMMERCIAL_MODIFIERS_UK_FALLBACK
                if lang == "uk"
                else _COMMERCIAL_MODIFIERS_FALLBACK
            )


# Backwards-compatible exports for tests/legacy imports.
COMMERCIAL_MODIFIERS = get_commercial_modifiers("ru")
COMMERCIAL_MODIFIERS_UK = get_commercial_modifiers("uk")

# Coverage targets (SSOT)
try:
    from scripts.config import get_guidelines_coverage_target
except ImportError:
    from config import get_guidelines_coverage_target


# =============================================================================
# CSV Parser
# =============================================================================


def read_semantics_csv(csv_path: str) -> dict[str, list[dict]]:
    """
    Читает CSV семантики и возвращает keywords по категориям L3.
    """
    categories: dict[str, list[dict]] = {}
    current_l3: str | None = None

    with open(csv_path, encoding="utf-8") as f:
        reader = csv.reader(f)
        for row in reader:
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

            # Skip SEO filter headers
            if phrase.startswith("SEO-Фильтр:"):
                continue

            # Skip boundary rows
            count_str = row[1].strip() if len(row) > 1 else ""
            if (
                current_l3
                and phrase.lower() == "категория"
                and count_str.isdigit()
                and not volume_str
            ):
                current_l3 = None
                continue

            if not current_l3:
                continue

            # Skip subsection headers
            if count_str and not volume_str:
                continue

            # Regular keyword requires numeric volume
            if not volume_str.isdigit():
                continue

            volume = int(volume_str)
            categories[current_l3].append({"keyword": phrase, "volume": volume})

    return categories


# =============================================================================
# Intent-based Keyword Split (v8.4)
# =============================================================================


def is_commercial_keyword(keyword: str, lang: str = "ru") -> bool:
    """Check if keyword has commercial intent (купить, цена, etc.)."""
    kw_lower = keyword.lower()
    modifiers = get_commercial_modifiers(lang)
    return any(mod in kw_lower for mod in modifiers)


def split_keywords_by_intent(
    keywords: list[dict], lang: str = "ru"
) -> tuple[list[dict], list[dict]]:
    """
    Split keywords into core (topic/editorial) and commercial (transactional).

    Core keywords: topic keywords without commercial modifiers
    Commercial keywords: contain купить/цена/заказать/etc.

    Returns:
        Tuple[core_keywords, commercial_keywords]
    """
    core = []
    commercial = []

    for kw in keywords:
        if is_commercial_keyword(kw["keyword"], lang):
            commercial.append(kw)
        else:
            core.append(kw)

    return core, commercial


# =============================================================================
# Analysis Functions (Google 2025 Approach)
# =============================================================================


def analyze_keywords(keywords: list[dict], lang: str = "ru") -> dict:
    """
    Анализирует семантику категории.

    Args:
        keywords: List of keyword dicts
        lang: Language code ("ru" or "uk")

    Returns:
        Dict с метриками и рекомендациями
    """
    if not keywords:
        return {
            "count": 0,
            "total_volume": 0,
            "semantic_depth": "empty",
            "content_format": "none",
            "recommended_words": "0",
            "need_clustering": False,
            "all_keywords": [],
            "core_keywords": [],
            "commercial_keywords": [],
        }

    count = len(keywords)
    total_volume = sum(kw["volume"] for kw in keywords)

    # Sort by volume
    sorted_kws = sorted(keywords, key=lambda x: -x["volume"])

    # High volume keywords (>100)
    high_volume = [kw for kw in keywords if kw["volume"] > 100]

    # Split by intent (v8.4)
    core_keywords, commercial_keywords = split_keywords_by_intent(keywords, lang)

    # Primary keyword (topic-first): prefer core intent over commercial modifiers.
    if core_keywords:
        primary = sorted(core_keywords, key=lambda x: -x["volume"])[0]
    else:
        primary = sorted_kws[0]

    # Determine semantic depth
    if count <= 5:
        semantic_depth = "shallow"
        content_format = "compact"
        recommended_words = "150-250"
    elif count <= 15:
        semantic_depth = "medium"
        content_format = "standard"
        recommended_words = "250-400"
    else:
        semantic_depth = "deep"
        content_format = "comprehensive"
        recommended_words = "400-600"

    # Need clustering?
    need_clustering = count > 20

    return {
        "count": count,
        "total_volume": total_volume,
        "primary": primary,
        "high_volume_count": len(high_volume),
        "commercial_count": len(commercial_keywords),
        "core_count": len(core_keywords),
        "semantic_depth": semantic_depth,
        "content_format": content_format,
        "recommended_words": recommended_words,
        "need_clustering": need_clustering,
        "all_keywords": sorted_kws,
        # v8.4: Split by intent
        "core_keywords": core_keywords,
        "commercial_keywords": commercial_keywords,
    }


def generate_content_guidelines(analysis: dict) -> dict:
    """
    Генерирует рекомендации для контента на основе анализа.

    Google 2025 подход:
    - Editorial content (buying guide)
    - Depth over length
    - Intent matching
    """
    depth = analysis["semantic_depth"]
    count = analysis["count"]

    # Base structure (всегда)
    structure = {
        "h1": True,
        "intro": {
            "required": True,
            "purpose": "Что это + зачем нужно",
            "length": "2-4 предложения",
        },
        "buying_advice": {
            "required": True,
            "purpose": "Как выбрать / на что смотреть",
            "format": "буллеты",
        },
        "trust_signals": {"required": True, "items": ["доставка", "наличие", "оплата"]},
    }

    # Adaptive elements based on semantic depth
    if depth == "shallow":
        structure["faq"] = {
            "required": False,
            "count": "0-1",
            "note": "Только если есть практический вопрос",
        }
        structure["comparison_table"] = {"required": False}
        structure["types_section"] = {"required": False}

    elif depth == "medium":
        structure["faq"] = {"required": True, "count": "2-3", "note": "Практические вопросы"}
        structure["comparison_table"] = {"required": False}
        structure["types_section"] = {
            "required": count > 10,
            "note": "Если есть подтипы товаров",
        }

    else:  # deep
        structure["faq"] = {"required": True, "count": "3-5", "note": "Практические вопросы"}
        structure["comparison_table"] = {"required": True, "note": "Сравнение типов/характеристик"}
        structure["types_section"] = {"required": True, "note": "Виды товаров с описанием"}

    # Keyword requirements
    coverage_target = get_guidelines_coverage_target(count)
    keyword_requirements = {
        "primary_in_h1": True,
        "primary_in_intro": True,
        "coverage_target": f"{coverage_target}%",
        "density": "не контролируем (natural writing)",
        "note": "Если тема раскрыта — ключи появятся естественно",
    }

    # Quality requirements (Google 2025)
    quality = {
        "water_percent": {"min": 40, "max": 65},
        "nausea_classic": {"max": 3.5},
        "blacklist_phrases": 0,
        "unique_content": True,
        "editorial_tone": "эксперт авто-детейлинга",
    }

    return {
        "structure": structure,
        "keyword_requirements": keyword_requirements,
        "quality": quality,
        "length_note": "LLM определяет длину по теме. Не фиксированный объём.",
    }


def analyze_category(slug: str, lang: str = "ru") -> dict:
    """
    Полный анализ категории для LLM.
    Uses D+E Fallback Pattern to load keywords.

    Args:
        slug: Category slug
        lang: Language code ("ru" or "uk")
    """
    # Get L3 name for display (use correct mapping for lang)
    try:
        from scripts.seo_utils import get_mappings_for_lang
    except ImportError:
        from seo_utils import get_mappings_for_lang
    _, slug_to_l3 = get_mappings_for_lang(lang)
    l3_name = slug_to_l3.get(slug, slug)

    # Load keywords using D+E Fallback
    keywords_raw, source, extra_data = load_keywords_for_slug(slug, lang)

    if not keywords_raw:
        return {
            "error": f"No keywords found for slug: {slug} (lang={lang}). Run seo-clean or parse CSV first."
        }

    # Analyze
    keyword_analysis = analyze_keywords(keywords_raw, lang)
    content_guidelines = generate_content_guidelines(keyword_analysis)

    # Determine if clustering is needed (only for raw sources)
    needs_clean = source in ["raw_json", "csv"] and keyword_analysis["count"] > 15

    # Build result
    result = {
        "meta": {
            "slug": slug,
            "category_name": l3_name,
            "analyzed_at": datetime.now(UTC).isoformat(),
            "approach": "Google 2025 (Depth over Length)",
            "source": source,
            "needs_clean": needs_clean,
        },
        "keywords": {
            "count": keyword_analysis["count"],
            "total_volume": keyword_analysis["total_volume"],
            "primary": keyword_analysis["primary"],
            "high_volume_count": keyword_analysis["high_volume_count"],
            "commercial_count": keyword_analysis["commercial_count"],
            "core_count": keyword_analysis["core_count"],
            "semantic_depth": keyword_analysis["semantic_depth"],
            "need_clustering": keyword_analysis["need_clustering"],
            "all_keywords": keyword_analysis["all_keywords"][:20],  # Top 20 for display
            # v8.4: Split by intent for coverage calculation
            "core_keywords": [kw["keyword"] for kw in keyword_analysis["core_keywords"]],
            "commercial_keywords": [
                kw["keyword"] for kw in keyword_analysis["commercial_keywords"]
            ],
        },
        "content": {
            "format": keyword_analysis["content_format"],
            "recommended_words": keyword_analysis["recommended_words"],
            "structure": content_guidelines["structure"],
            "keyword_requirements": content_guidelines["keyword_requirements"],
            "quality": content_guidelines["quality"],
            "length_note": content_guidelines["length_note"],
        },
        "llm_prompt_hints": {
            "page_type": "категория интернет-магазина",
            "content_type": "buying guide (не SEO-текст)",
            "tone": "эксперт авто-детейлинга",
            "goal": "помочь выбрать товар",
            "avoid": ["вода ради объёма", "универсальные фразы", "история категории", "AI-fluff"],
        },
    }

    # Add extra data from clean.json if available
    if extra_data:
        result["seo_titles"] = extra_data.get("seo_titles")
        result["entity_dictionary"] = extra_data.get("entity_dictionary")
        result["content_rules"] = extra_data.get("content_rules")
        result["clustering_stats"] = extra_data.get("stats")

    return result


# =============================================================================
# CLI
# =============================================================================


def list_all_categories():
    """Показать все категории с анализом."""
    print("=" * 70)
    print("АНАЛИЗ ВСЕХ КАТЕГОРИЙ (Google 2025 Approach)")
    print("=" * 70)
    print()

    categories = read_semantics_csv(str(SEMANTICS_CSV))

    # Analyze all
    results = []
    for l3_name, keywords in categories.items():
        slug = L3_TO_SLUG.get(l3_name, "???")
        analysis = analyze_keywords(keywords)
        results.append(
            {
                "slug": slug,
                "name": l3_name,
                "count": analysis["count"],
                "volume": analysis["total_volume"],
                "depth": analysis["semantic_depth"],
                "format": analysis["content_format"],
                "words": analysis["recommended_words"],
                "clustering": analysis["need_clustering"],
            }
        )

    # Sort by keyword count
    results.sort(key=lambda x: -x["count"])

    # Print table
    print(
        f"{'Slug':<25} {'Keywords':>8} {'Volume':>7} {'Depth':<10} {'Format':<12} {'Words':<10} {'Cluster'}"
    )
    print("-" * 90)

    for r in results:
        cluster = "YES" if r["clustering"] else "no"
        print(
            f"{r['slug']:<25} {r['count']:>8} {r['volume']:>7} {r['depth']:<10} {r['format']:<12} {r['words']:<10} {cluster}"
        )

    print("-" * 90)
    print(f"Total: {len(results)} categories")
    print()
    print("Semantic Depth:")
    print("  shallow (≤5 kw)  → compact format, 150-250 words")
    print("  medium (6-15 kw) → standard format, 250-400 words")
    print("  deep (16+ kw)    → comprehensive format, 400-600 words")


def main():
    if len(sys.argv) < 2:
        print("Usage:")
        print("  python3 scripts/analyze_category.py <slug>")
        print("  python3 scripts/analyze_category.py <slug> --json")
        print("  python3 scripts/analyze_category.py <slug> --lang uk")
        print("  python3 scripts/analyze_category.py --list")
        print()
        print("Example:")
        print("  python3 scripts/analyze_category.py antibitum")
        print("  python3 scripts/analyze_category.py aktivnaya-pena --json")
        print("  python3 scripts/analyze_category.py aktivnaya-pena --lang uk --json")
        sys.exit(1)

    if sys.argv[1] == "--list":
        list_all_categories()
        sys.exit(0)

    slug = sys.argv[1]
    output_json = "--json" in sys.argv

    # Parse --lang parameter
    lang = "ru"
    if "--lang" in sys.argv:
        lang_idx = sys.argv.index("--lang")
        if lang_idx + 1 < len(sys.argv):
            lang = sys.argv[lang_idx + 1]

    result = analyze_category(slug, lang)

    if "error" in result:
        print(f"❌ {result['error']}")
        sys.exit(1)

    if output_json:
        print(json.dumps(result, ensure_ascii=False, indent=2))
    else:
        # Human-readable output
        print()
        print("=" * 60)
        print(f"АНАЛИЗ КАТЕГОРИИ: {result['meta']['category_name']}")
        print(f"Slug: {result['meta']['slug']}")
        print("=" * 60)
        print()

        # Source info
        meta = result["meta"]
        source_emoji = {"clean_json": "✓", "raw_json": "○", "csv": "△"}
        source_label = {
            "clean_json": "Clean JSON (clustered)",
            "raw_json": "Raw JSON",
            "csv": "CSV fallback",
        }
        print(
            f"📂 SOURCE: {source_emoji.get(meta['source'], '?')} {source_label.get(meta['source'], meta['source'])}"
        )
        if meta.get("needs_clean"):
            print(f"   ⚠️  Рекомендуется: clean {result['meta']['slug']}")
        print()

        kw = result["keywords"]
        print("📊 KEYWORDS:")
        print(f"   Count: {kw['count']}")
        print(f"   Total Volume: {kw['total_volume']}")
        print(f'   Primary: "{kw["primary"]["keyword"]}" (vol: {kw["primary"]["volume"]})')
        print(f"   High Volume (>100): {kw['high_volume_count']}")
        print(f"   ┌─ Core (topic): {kw['core_count']} ← target coverage")
        print(f"   └─ Commercial: {kw['commercial_count']} (INFO only)")
        print(f"   Semantic Depth: {kw['semantic_depth']}")
        print(f"   Need Clustering: {'Yes' if kw['need_clustering'] else 'No'}")
        print()

        # Show clustering stats if from clean.json
        if result.get("clustering_stats"):
            stats = result["clustering_stats"]
            print("🔄 CLUSTERING STATS:")
            print(f"   Before: {stats['before']} → After: {stats['after']} keywords")
            if "reduction_percent" in stats:
                print(f"   Reduction: {stats['reduction_percent']}%")
            if "clusters_count" in stats:
                print(f"   Clusters: {stats['clusters_count']}")
            print()

        # Show SEO titles if available
        if result.get("seo_titles"):
            titles = result["seo_titles"]
            print("📌 SEO TITLES:")
            print(f'   H1: "{titles["h1"]}" (vol: {titles["h1_volume"]})')
            print(
                f'   Main keyword: "{titles["main_keyword"]}" (vol: {titles["main_keyword_volume"]})'
            )
            print()

        content = result["content"]
        print("📝 CONTENT RECOMMENDATIONS:")
        print(f"   Format: {content['format']}")
        print(f"   Words: {content['recommended_words']}")
        print(f"   Coverage Target: {content['keyword_requirements']['coverage_target']}")
        print()

        struct = content["structure"]
        print("📋 STRUCTURE:")
        print("   H1: Required")
        print(f"   Intro: {struct['intro']['length']}")
        print("   Buying Advice: буллеты")
        if struct.get("faq", {}).get("required"):
            print(f"   FAQ: {struct['faq']['count']} вопросов")
        if struct.get("comparison_table", {}).get("required"):
            print("   Таблица: Required")
        if struct.get("types_section", {}).get("required"):
            print("   Виды товаров: Required")
        print()

        # Show entity dictionary if available
        if result.get("entity_dictionary"):
            print("📖 ENTITY DICTIONARY:")
            for key, values in result["entity_dictionary"].items():
                print(f"   {key}: {', '.join(values[:3])}{'...' if len(values) > 3 else ''}")
            print()

        print(f"⚠️  NOTE: {content['length_note']}")
        print()


if __name__ == "__main__":
    main()
