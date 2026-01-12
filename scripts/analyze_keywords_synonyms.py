#!/usr/bin/env python3
"""Анализ keywords и synonyms согласно CONTENT_GUIDE.md."""

import json
from datetime import datetime
from pathlib import Path

ROOT = Path(__file__).parent.parent
CATEGORIES_DIR = ROOT / "categories"
OUTPUT_FILE = ROOT / "tasks" / "active" / "KEYWORDS_SYNONYMS_TZ.md"

# Требования из CONTENT_GUIDE.md
REQUIREMENTS = {
    "keywords_min": 1,  # Минимум 1 keyword (главный)
    "synonyms_min": 3,  # Минимум 3 синонима
    "synonyms_meta_only": 1,  # Минимум 1 коммерческий (meta_only)
    "entities_min": 5,  # Минимум 5 entities
    "micro_intents_min": 3,  # Минимум 3 micro_intents
}


def analyze_category(clean_file: Path) -> dict:
    """Анализирует _clean.json на соответствие требованиям."""
    data = json.loads(clean_file.read_text(encoding="utf-8"))
    slug = data.get("id", clean_file.stem.replace("_clean", ""))
    name = data.get("name", slug)

    keywords = data.get("keywords", [])
    synonyms = data.get("synonyms", [])
    entities = data.get("entities", [])
    micro_intents = data.get("micro_intents", [])

    # Разделяем synonyms
    regular_synonyms = [s for s in synonyms if s.get("use_in") != "meta_only"]
    meta_only_synonyms = [s for s in synonyms if s.get("use_in") == "meta_only"]

    # Проверяем volume=0
    zero_keywords = [k for k in keywords if k.get("volume", 0) == 0]
    zero_synonyms = [s for s in regular_synonyms if s.get("volume", 0) == 0]

    issues = []
    warnings = []

    # Keywords checks
    if len(keywords) < REQUIREMENTS["keywords_min"]:
        issues.append(f"keywords: {len(keywords)} < {REQUIREMENTS['keywords_min']} (нет главного ключа)")
    if zero_keywords:
        warnings.append(f"keywords с volume=0: {len(zero_keywords)}")

    # Synonyms checks
    if len(regular_synonyms) < REQUIREMENTS["synonyms_min"]:
        issues.append(f"synonyms: {len(regular_synonyms)} < {REQUIREMENTS['synonyms_min']}")
    if len(meta_only_synonyms) < REQUIREMENTS["synonyms_meta_only"]:
        issues.append(
            f"meta_only synonyms: {len(meta_only_synonyms)} < {REQUIREMENTS['synonyms_meta_only']} (нет коммерческих)"
        )
    if zero_synonyms:
        warnings.append(f"synonyms с volume=0: {len(zero_synonyms)}")

    # Entities checks
    if len(entities) < REQUIREMENTS["entities_min"]:
        issues.append(f"entities: {len(entities)} < {REQUIREMENTS['entities_min']}")

    # Micro-intents checks
    if len(micro_intents) < REQUIREMENTS["micro_intents_min"]:
        issues.append(f"micro_intents: {len(micro_intents)} < {REQUIREMENTS['micro_intents_min']}")

    return {
        "slug": slug,
        "name": name,
        "file": str(clean_file.relative_to(ROOT)),
        "keywords": keywords,
        "keywords_count": len(keywords),
        "synonyms_count": len(regular_synonyms),
        "meta_only_count": len(meta_only_synonyms),
        "entities_count": len(entities),
        "micro_intents_count": len(micro_intents),
        "entities": entities,
        "micro_intents": micro_intents,
        "issues": issues,
        "warnings": warnings,
        "score": calculate_score(
            len(keywords), len(regular_synonyms), len(meta_only_synonyms), len(entities), len(micro_intents)
        ),
    }


def calculate_score(kw, syn, meta, ent, mi) -> int:
    """Рассчитывает score заполненности (0-100%)."""
    score = 0
    score += min(kw / REQUIREMENTS["keywords_min"], 1) * 20
    score += min(syn / REQUIREMENTS["synonyms_min"], 1) * 20
    score += min(meta / REQUIREMENTS["synonyms_meta_only"], 1) * 20
    score += min(ent / REQUIREMENTS["entities_min"], 1) * 20
    score += min(mi / REQUIREMENTS["micro_intents_min"], 1) * 20
    return int(score)


def generate_tz(results: list) -> str:
    """Генерирует ТЗ в формате Markdown."""
    with_issues = [r for r in results if r["issues"]]
    ok_results = [r for r in results if not r["issues"]]

    lines = [
        "# ТЗ: Аудит keywords и synonyms",
        "",
        f"**Дата создания:** {datetime.now().strftime('%Y-%m-%d %H:%M')}",
        "**Статус:** ⬜ В работе",
        "",
        "---",
        "",
        "## Требования (из CONTENT_GUIDE.md)",
        "",
        "| Поле | Минимум | Назначение |",
        "|------|---------|------------|",
        f"| `keywords` | {REQUIREMENTS['keywords_min']}+ | ТОП ВЧ ключи → Title, H1 |",
        f"| `synonyms` | {REQUIREMENTS['synonyms_min']}+ | Вариации → H2, текст |",
        f"| `meta_only` | {REQUIREMENTS['synonyms_meta_only']}+ | Коммерческие (купить, цена) → Title хвост, Description |",
        f"| `entities` | {REQUIREMENTS['entities_min']}+ | E-E-A-T термины → текст |",
        f"| `micro_intents` | {REQUIREMENTS['micro_intents_min']}+ | Вопросы → FAQ блоки |",
        "",
        "---",
        "",
        "## Статистика",
        "",
        f"- Всего категорий: **{len(results)}**",
        f"- Требуют доработки: **{len(with_issues)}**",
        f"- Полностью заполнены: **{len(ok_results)}**",
        "",
        "### Распределение по score",
        "",
    ]

    # Score distribution
    score_ranges = {"100%": 0, "80-99%": 0, "60-79%": 0, "40-59%": 0, "<40%": 0}
    for r in results:
        if r["score"] == 100:
            score_ranges["100%"] += 1
        elif r["score"] >= 80:
            score_ranges["80-99%"] += 1
        elif r["score"] >= 60:
            score_ranges["60-79%"] += 1
        elif r["score"] >= 40:
            score_ranges["40-59%"] += 1
        else:
            score_ranges["<40%"] += 1

    for range_name, count in score_ranges.items():
        bar = "█" * (count // 2) if count else ""
        lines.append(f"- {range_name}: **{count}** {bar}")

    lines.extend(
        [
            "",
            "---",
            "",
            "## Категории для доработки",
            "",
        ]
    )

    # Сортируем по score (худшие первые)
    for r in sorted(with_issues, key=lambda x: x["score"]):
        status_icon = "🔴" if r["score"] < 40 else "🟡" if r["score"] < 80 else "🟢"
        lines.append(f"### {status_icon} {r['name']} (`{r['slug']}`) — {r['score']}%")
        lines.append("")
        lines.append(f"**Файл:** `{r['file']}`")
        lines.append("")

        # Текущее состояние
        lines.append("**Текущее состояние:**")
        lines.append("| Поле | Есть | Нужно | Статус |")
        lines.append("|------|------|-------|--------|")

        kw_status = "✅" if r["keywords_count"] >= REQUIREMENTS["keywords_min"] else "❌"
        syn_status = "✅" if r["synonyms_count"] >= REQUIREMENTS["synonyms_min"] else "❌"
        meta_status = "✅" if r["meta_only_count"] >= REQUIREMENTS["synonyms_meta_only"] else "❌"
        ent_status = "✅" if r["entities_count"] >= REQUIREMENTS["entities_min"] else "❌"
        mi_status = "✅" if r["micro_intents_count"] >= REQUIREMENTS["micro_intents_min"] else "❌"

        lines.append(f"| keywords | {r['keywords_count']} | {REQUIREMENTS['keywords_min']}+ | {kw_status} |")
        lines.append(f"| synonyms | {r['synonyms_count']} | {REQUIREMENTS['synonyms_min']}+ | {syn_status} |")
        lines.append(f"| meta_only | {r['meta_only_count']} | {REQUIREMENTS['synonyms_meta_only']}+ | {meta_status} |")
        lines.append(f"| entities | {r['entities_count']} | {REQUIREMENTS['entities_min']}+ | {ent_status} |")
        lines.append(
            f"| micro_intents | {r['micro_intents_count']} | {REQUIREMENTS['micro_intents_min']}+ | {mi_status} |"
        )
        lines.append("")

        # Главный ключ
        if r["keywords"]:
            main_kw = r["keywords"][0]
            lines.append(f"**Главный ключ:** `{main_kw['keyword']}` (volume: {main_kw.get('volume', 0)})")
            lines.append("")

        # Проблемы
        if r["issues"]:
            lines.append("**Проблемы:**")
            for issue in r["issues"]:
                lines.append(f"- ❌ {issue}")
            lines.append("")

        if r["warnings"]:
            lines.append("**Предупреждения:**")
            for warn in r["warnings"]:
                lines.append(f"- ⚠️ {warn}")
            lines.append("")

        # Чеклист
        lines.append("**Чеклист:**")
        if r["keywords_count"] < REQUIREMENTS["keywords_min"]:
            lines.append("- [ ] Добавить главный keyword (самый частотный)")
        if r["synonyms_count"] < REQUIREMENTS["synonyms_min"]:
            need = REQUIREMENTS["synonyms_min"] - r["synonyms_count"]
            lines.append(f"- [ ] Добавить {need}+ synonyms (вариации ключа)")
        if r["meta_only_count"] < REQUIREMENTS["synonyms_meta_only"]:
            lines.append("- [ ] Добавить коммерческие synonyms с `use_in: meta_only` (купить X, X цена)")
        if r["entities_count"] < REQUIREMENTS["entities_min"]:
            need = REQUIREMENTS["entities_min"] - r["entities_count"]
            lines.append(f"- [ ] Добавить {need}+ entities (термины, бренды, характеристики)")
        if r["micro_intents_count"] < REQUIREMENTS["micro_intents_min"]:
            need = REQUIREMENTS["micro_intents_min"] - r["micro_intents_count"]
            lines.append(f"- [ ] Добавить {need}+ micro_intents (вопросы пользователей)")
        lines.append("- [ ] Проверить результат")
        lines.append("")
        lines.append("---")
        lines.append("")

    # Категории OK
    if ok_results:
        lines.append("## Категории 100% (полностью заполнены)")
        lines.append("")
        for r in sorted(ok_results, key=lambda x: x["slug"]):
            main_kw = r["keywords"][0]["keyword"] if r["keywords"] else "—"
            lines.append(f"- ✅ **{r['name']}** (`{r['slug']}`) — `{main_kw}`")
        lines.append("")

    return "\n".join(lines)


def main():
    print("🔍 Аудит keywords и synonyms...\n")

    results = []
    for clean_file in sorted(CATEGORIES_DIR.rglob("*_clean.json")):
        result = analyze_category(clean_file)
        results.append(result)
        if result["issues"]:
            print(
                f"{'🔴' if result['score'] < 40 else '🟡'} {result['slug']}: {result['score']}% — {len(result['issues'])} проблем"
            )

    # Генерируем ТЗ
    tz_content = generate_tz(results)
    OUTPUT_FILE.parent.mkdir(parents=True, exist_ok=True)
    OUTPUT_FILE.write_text(tz_content, encoding="utf-8")

    with_issues = [r for r in results if r["issues"]]
    avg_score = sum(r["score"] for r in results) / len(results) if results else 0

    print(f"\n{'=' * 50}")
    print(f"✅ Проанализировано: {len(results)} категорий")
    print(f"⚠️  Требуют доработки: {len(with_issues)}")
    print(f"📊 Средний score: {avg_score:.0f}%")
    print(f"\n📄 ТЗ сохранено: {OUTPUT_FILE}")


if __name__ == "__main__":
    main()
