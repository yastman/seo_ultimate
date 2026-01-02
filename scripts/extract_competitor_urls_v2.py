#!/usr/bin/env python3
"""
Извлечение конкурентов из SERP топ-10 для ВЧ ключей каждого L3 кластера.

ЛОГИКА:
1) Берём только ВЧ ключи (топ по частотности в кластере)
2) Собираем топ-10 URL для этих ВЧ ключей из SERP
3) Фильтруем маркетплейсы (blacklist)
4) Ранжируем по score (частота × позиция)
5) Лимитируем URL на домен (разнообразие источников)
6) Сохраняем финальный список + логи
"""

from __future__ import annotations

import argparse
import csv
from collections import defaultdict
from datetime import datetime
from pathlib import Path
from urllib.parse import urlparse

import pandas as pd


BASE_DIR = Path(__file__).resolve().parent.parent

BLACKLIST_DOMAINS = [
    "prom.ua",
    "rozetka.com.ua",
    "epicentrk.ua",
    "olx.ua",
    "m.olx.ua",
    "youtube.com",
    "youtu.be",
]


def transliterate_slug(text: str) -> str:
    """Транслитерация украинского/русского текста в латиницу для slug."""
    import re

    translit_map = {
        "а": "a",
        "б": "b",
        "в": "v",
        "г": "g",
        "д": "d",
        "е": "e",
        "ё": "yo",
        "ж": "zh",
        "з": "z",
        "и": "i",
        "й": "y",
        "к": "k",
        "л": "l",
        "м": "m",
        "н": "n",
        "о": "o",
        "п": "p",
        "р": "r",
        "с": "s",
        "т": "t",
        "у": "u",
        "ф": "f",
        "х": "kh",
        "ц": "ts",
        "ч": "ch",
        "ш": "sh",
        "щ": "shch",
        "ъ": "",
        "ы": "y",
        "ь": "",
        "э": "e",
        "ю": "yu",
        "я": "ya",
        "і": "i",
        "ї": "yi",
        "є": "ye",
        "ґ": "g",
    }

    text = text.lower()
    result = []
    for char in text:
        if char in translit_map:
            result.append(translit_map[char])
        elif char.isalnum() or char == "-":
            result.append(char)
        elif char in (" ", "_", "/"):
            result.append("-")

    slug = "".join(result)
    slug = re.sub(r"-+", "-", slug)
    slug = slug.strip("-")
    return slug


def is_blacklisted(url: str) -> bool:
    """Проверка, что URL принадлежит blacklisted доменам."""
    try:
        domain = urlparse(url).netloc.lower()
        domain = domain.replace("www.", "")
        return any(blacklist_domain in domain for blacklist_domain in BLACKLIST_DOMAINS)
    except Exception:
        return False


def resolve_path(path_str: str) -> Path:
    path = Path(path_str)
    if path.is_absolute():
        return path
    return (BASE_DIR / path).resolve()


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Извлечение конкурентов из SERP для ВЧ ключей")
    parser.add_argument("--slug", type=str, required=True, help="Категория для обработки (L3 slug)")
    parser.add_argument("--top-n", type=int, default=3, help="Количество ВЧ ключей (default: 3)")
    parser.add_argument(
        "--max-urls", type=int, default=10, help="Максимум URL на категорию (default: 10)"
    )
    parser.add_argument(
        "--max-per-domain", type=int, default=2, help="Максимум URL на домен (default: 2)"
    )
    parser.add_argument(
        "--serp-file",
        type=str,
        default="data/поисковая_выдача_топ_10.csv",
        help="SERP CSV (default: data/поисковая_выдача_топ_10.csv)",
    )
    parser.add_argument(
        "--clusters-file",
        type=str,
        default="data/Структура  Ultimate финал - Лист2.csv",
        help="Clusters CSV (default: data/Структура  Ultimate финал - Лист2.csv)",
    )
    parser.add_argument(
        "--output-dir",
        type=str,
        default="data/output",
        help="Output directory (default: data/output)",
    )
    parser.add_argument(
        "--categories-dir",
        type=str,
        default="categories",
        help="Categories directory (default: categories)",
    )
    parser.add_argument(
        "--output",
        type=str,
        help="Кастомный путь для сохранения финального списка URL (default: categories/{slug}/urls.txt)",
    )
    return parser


def load_serp_df(serp_file: Path) -> pd.DataFrame:
    serp_data: list[dict] = []
    current_phrase: str | None = None

    with serp_file.open(encoding="utf-8-sig", newline="") as f:
        reader = csv.DictReader(f, delimiter=";")
        for row in reader:
            phrase = row.get("Phrase")
            url = (row.get("URL") or "").strip()
            position_raw = (row.get("Position") or "").strip()

            phrase_clean = phrase.strip() if phrase else None
            if phrase_clean:
                current_phrase = phrase_clean

            if not (current_phrase and url and position_raw):
                continue

            try:
                position = int(position_raw)
            except ValueError:
                continue

            serp_data.append({"keyword": current_phrase, "url": url, "position": position})

    return pd.DataFrame(serp_data)


def load_clusters_df(clusters_file: Path) -> pd.DataFrame:
    clusters_raw = pd.read_csv(clusters_file, encoding="utf-8-sig")

    clusters: list[dict] = []
    current_l1: str | None = None
    current_l2: str | None = None
    current_l3: str | None = None

    for _idx, row in clusters_raw.iterrows():
        phrase = str(row.get("Фраза", "")).strip()
        volume_raw = row.get("Запросы сред. [GA]")

        if not phrase or phrase == "nan":
            continue

        if phrase.startswith("L1:"):
            current_l1 = phrase.replace("L1:", "").strip()
            continue
        if phrase.startswith("L2:"):
            current_l2 = phrase.replace("L2:", "").strip()
            continue
        if phrase.startswith("L3:"):
            current_l3 = phrase.replace("L3:", "").strip()
            continue

        if not (current_l1 and current_l2 and current_l3):
            continue

        volume = int(volume_raw) if pd.notna(volume_raw) and str(volume_raw).strip() else 0
        clusters.append(
            {
                "l1": current_l1,
                "l2": current_l2,
                "l3": current_l3,
                "keyword": phrase,
                "volume": volume,
            }
        )

    return pd.DataFrame(clusters)


def select_vch_keywords(clusters_df: pd.DataFrame, top_n: int) -> pd.DataFrame:
    vch_keywords_list = []
    for l3_name, group in clusters_df.groupby("l3"):
        group_sorted = group.sort_values("volume", ascending=False)
        selected = group_sorted.head(top_n)
        vch_keywords_list.append(selected)
        keywords_preview = ", ".join(
            [f"{row['keyword']} ({row['volume']})" for _, row in selected.iterrows()]
        )
        print(f"   ✓ {l3_name}: топ-{len(selected)} ВЧ ключей")
        print(f"      {keywords_preview}")

    if not vch_keywords_list:
        return pd.DataFrame([])
    return pd.concat(vch_keywords_list).drop_duplicates()


def build_competitors_df(
    serp_df: pd.DataFrame,
    vch_keywords: pd.DataFrame,
    max_urls_per_category: int,
    max_urls_per_domain: int,
) -> pd.DataFrame:
    serp_df = serp_df.copy()
    vch_keywords = vch_keywords.copy()

    serp_df["keyword_lower"] = serp_df["keyword"].str.lower().str.strip()
    vch_keywords["keyword_lower"] = vch_keywords["keyword"].str.lower().str.strip()

    merged = serp_df.merge(
        vch_keywords[["l1", "l2", "l3", "keyword", "keyword_lower", "volume"]],
        on="keyword_lower",
        how="inner",
    )

    merged["is_blacklisted"] = merged["url"].apply(is_blacklisted)
    filtered = merged[~merged["is_blacklisted"]].copy()

    l3_competitors_list: list[dict] = []
    for (l1, l2, l3), group in filtered.groupby(["l1", "l2", "l3"]):
        url_frequency = group["url"].value_counts()
        url_avg_position = group.groupby("url")["position"].mean()

        url_scores: dict[str, float] = {}
        for url in url_frequency.index:
            frequency = int(url_frequency[url])
            avg_pos = float(url_avg_position[url])
            url_scores[url] = frequency * (11 - avg_pos)

        sorted_urls = sorted(url_scores.items(), key=lambda x: x[1], reverse=True)

        domain_counts: dict[str, int] = defaultdict(int)
        top_urls_list: list[str] = []
        for url, _score in sorted_urls:
            domain = urlparse(url).netloc.replace("www.", "").lower()
            if domain_counts[domain] >= max_urls_per_domain:
                continue
            top_urls_list.append(url)
            domain_counts[domain] += 1
            if len(top_urls_list) >= max_urls_per_category:
                break

        l3_competitors_list.append(
            {
                "l1": l1,
                "l2": l2,
                "l3": l3,
                "competitor_urls": top_urls_list,
                "vch_keywords_count": group["keyword_lower"].nunique(),
                "total_volume": int(group["volume"].sum()),
                "competitors_count": len(top_urls_list),
            }
        )

    return pd.DataFrame(l3_competitors_list)


def write_outputs(
    l3_competitors: pd.DataFrame,
    categories_dir: Path,
    output_dir: Path,
    top_n_keywords: int,
    max_urls_per_category: int,
    max_urls_per_domain: int,
    output_override: str | None,
) -> None:
    output_dir.mkdir(parents=True, exist_ok=True)
    categories_dir.mkdir(parents=True, exist_ok=True)

    sf_urls_dir = output_dir / "sf_urls_by_category"
    sf_urls_dir.mkdir(exist_ok=True)

    print("\n📁 Создаём отдельные файлы URL для каждой категории...")

    for _idx, row in l3_competitors.iterrows():
        category_slug = transliterate_slug(row["l3"])
        filename = f"{category_slug}_urls.txt"

        if output_override:
            main_output_file = Path(output_override)
        else:
            main_output_file = categories_dir / category_slug / "urls.txt"
        main_output_file.parent.mkdir(parents=True, exist_ok=True)
        main_output_file.write_text("\n".join(row["competitor_urls"]) + "\n", encoding="utf-8")

        (sf_urls_dir / filename).write_text(
            "\n".join(row["competitor_urls"]) + "\n", encoding="utf-8"
        )

        category_source_dir = categories_dir / category_slug / "competitors" / ".source"
        category_source_dir.mkdir(parents=True, exist_ok=True)
        (category_source_dir / "urls.txt").write_text(
            "\n".join(row["competitor_urls"]) + "\n", encoding="utf-8"
        )

        logs_dir = categories_dir / category_slug / "competitors" / ".logs"
        logs_dir.mkdir(parents=True, exist_ok=True)
        log_file = logs_dir / "urls.final.txt"

        lines = [
            f"# Generated: {datetime.now().isoformat()}",
            f"# Category: {row['l3']}",
            f"# VCH keywords: {row['vch_keywords_count']}",
            f"# Total volume: {row['total_volume']}",
            f"# Top-{top_n_keywords} VCH keywords used for extraction",
            f"# Max URLs per category: {max_urls_per_category}",
            f"# Max URLs per domain: {max_urls_per_domain}",
            "#",
            *row["competitor_urls"],
        ]
        log_file.write_text("\n".join(lines) + "\n", encoding="utf-8")

        output_location = f"custom: {main_output_file}" if output_override else "default"
        print(
            f"   ✅ {filename} ({len(row['competitor_urls'])} URLs, {row['vch_keywords_count']} ВЧ ключей, volume: {row['total_volume']}) [{output_location}]"
        )

    all_unique_urls = sorted({url for urls in l3_competitors["competitor_urls"] for url in urls})
    (output_dir / "screaming_frog_urls_ALL.txt").write_text(
        "\n".join(all_unique_urls) + "\n", encoding="utf-8"
    )

    competitors_detailed = l3_competitors.copy()
    competitors_detailed["competitor_urls_str"] = competitors_detailed["competitor_urls"].apply(
        lambda x: "\n".join(x)
    )
    competitors_detailed[
        [
            "l1",
            "l2",
            "l3",
            "vch_keywords_count",
            "total_volume",
            "competitors_count",
            "competitor_urls_str",
        ]
    ].to_csv(output_dir / "cluster_competitors.csv", index=False, encoding="utf-8-sig")

    preview = l3_competitors.head(5).copy()
    preview["top_5_competitors"] = preview["competitor_urls"].apply(lambda x: "\n".join(x[:5]))
    preview[
        [
            "l1",
            "l2",
            "l3",
            "vch_keywords_count",
            "total_volume",
            "competitors_count",
            "top_5_competitors",
        ]
    ].to_csv(output_dir / "competitor_analysis_preview.csv", index=False, encoding="utf-8-sig")


def main(argv: list[str] | None = None) -> int:
    parser = build_parser()
    args = parser.parse_args(argv)

    serp_file = resolve_path(args.serp_file)
    clusters_file = resolve_path(args.clusters_file)
    output_dir = resolve_path(args.output_dir)
    categories_dir = resolve_path(args.categories_dir)

    print(f"🎯 Обработка категории: {args.slug}")

    if not serp_file.exists():
        print(f"❌ SERP file not found: {serp_file}")
        print("   Ожидается CSV с разделителем ';' и колонками: Phrase;URL;Position")
        print("   Решение:")
        print("   - передайте файл явно: --serp-file path/to/serp.csv")
        print("   - или положите его по умолчанию: data/поисковая_выдача_топ_10.csv")
        return 2
    if not clusters_file.exists():
        print(f"❌ Clusters file not found: {clusters_file}")
        return 2

    print("📊 Загружаем данные SERP топ-10...")
    serp_df = load_serp_df(serp_file)
    if serp_df.empty:
        print("❌ SERP file parsed as empty")
        return 2

    print(f"✅ Загружено {len(serp_df)} записей SERP")
    print(f"✅ Уникальных ключей: {serp_df['keyword'].nunique()}")
    print(f"✅ Уникальных URL: {serp_df['url'].nunique()}")

    print("\n📋 Загружаем структуру кластеров с частотностью...")
    clusters_df = load_clusters_df(clusters_file)
    if clusters_df.empty:
        print("❌ Clusters file parsed as empty (expected L1/L2/L3 markers)")
        return 2

    clusters_df["l3_slug"] = clusters_df["l3"].apply(transliterate_slug)
    target_category = clusters_df[clusters_df["l3_slug"] == args.slug]
    if target_category.empty:
        print(f"\n❌ Категория '{args.slug}' не найдена!")
        print("   Доступные категории:")
        for l3 in sorted(clusters_df["l3"].unique()):
            print(f"      • {transliterate_slug(l3)} ({l3})")
        return 2

    clusters_df = target_category
    print(
        f"\n✅ Фильтрация: работаем только с категорией '{clusters_df['l3'].iloc[0]}' ({len(clusters_df)} ключей)"
    )

    print(f"\n🔍 Фильтруем топ-{args.top_n} ВЧ ключей для каждой категории...")
    vch_keywords = select_vch_keywords(clusters_df, args.top_n)
    if vch_keywords.empty:
        print("❌ No VCH keywords selected")
        return 2

    print(f"\n✅ Итого уникальных ВЧ ключей: {len(vch_keywords)}")
    print("\n🔗 Объединяем SERP с ВЧ ключами...")

    competitors_df = build_competitors_df(serp_df, vch_keywords, args.max_urls, args.max_per_domain)
    if competitors_df.empty:
        print("❌ No competitors extracted (after merge/filters)")
        return 2

    print("\n💾 Сохраняем результаты...")
    write_outputs(
        competitors_df,
        categories_dir=categories_dir,
        output_dir=output_dir,
        top_n_keywords=args.top_n,
        max_urls_per_category=args.max_urls,
        max_urls_per_domain=args.max_per_domain,
        output_override=args.output,
    )

    print(f"\n✅ Категория '{args.slug}' успешно обработана!")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
