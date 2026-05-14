import argparse
import json
from pathlib import Path


def collect_keywords(categories_dir: Path) -> list[dict]:
    all_data = []

    for path in categories_dir.rglob("*_clean.json"):
        try:
            with path.open(encoding="utf-8") as f:
                data = json.load(f)

            slug = data.get("id") or data.get("slug")
            name = data.get("name", slug)

            kws = []
            if isinstance(data.get("keywords"), list):
                kws = data["keywords"]
            elif isinstance(data.get("keywords"), dict):
                for group in data["keywords"].values():
                    kws.extend(group)

            # Sort by volume
            kws.sort(key=lambda x: x.get("volume", 0), reverse=True)

            all_data.append(
                {
                    "slug": slug,
                    "name": name,
                    "keywords": kws,
                    "total_vol": sum(k.get("volume", 0) for k in kws),
                }
            )
        except (OSError, json.JSONDecodeError, AttributeError) as e:
            print(f"Error reading {path}: {e}")

    # Sort categories by ID for stability
    all_data.sort(key=lambda x: x["slug"])
    return all_data


def generate_report(data: list[dict], output_json: Path, output_md: Path) -> None:
    lines = []
    lines.append("# 🧬 Семантический Ревизор (Semantic Review)")
    lines.append(f"**Total Categories:** {len(data)}")
    lines.append("")
    lines.append(
        "> Этот отчет предназначен для ручной проверки распределения ключей. Проверьте, что ключи соответствуют интенту категории."
    )
    lines.append("")

    for cat in data:
        slug = cat["slug"]
        name = cat["name"]
        vol = cat["total_vol"]
        kws = cat["keywords"]

        lines.append(f"## 📂 [{slug}] {name}")
        lines.append(f"**Volume:** {vol} | **Keywords:** {len(kws)}")
        lines.append("")

        if not kws:
            lines.append("*⚠️ Нет ключей (Empty)*")
        else:
            lines.append("| Keyword | Vol |")
            lines.append("|---|---|")
            # Show top 50 keys to verify intent
            for k in kws[:100]:
                lines.append(f"| {k['keyword']} | {k.get('volume', 0)} |")

            if len(kws) > 100:
                lines.append(f"| *... и еще {len(kws) - 100}* | |")

        lines.append("")
        lines.append("---")
        lines.append("")

    output_json.parent.mkdir(parents=True, exist_ok=True)
    output_md.parent.mkdir(parents=True, exist_ok=True)

    with output_json.open("w", encoding="utf-8") as f:
        json.dump(data, f, indent=2, ensure_ascii=False)

    with output_md.open("w", encoding="utf-8") as f:
        f.write("\n".join(lines))

    print(f"Generated {output_json}")
    print(f"Generated {output_md}")


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Generate a semantic review report from clean JSON files.")
    parser.add_argument("--categories-dir", type=Path, default=Path("categories"))
    parser.add_argument("--output-json", type=Path, default=Path("data/all_keywords.json"))
    parser.add_argument("--output-md", type=Path, default=Path("tasks/reports/SEMANTIC_REVIEW.md"))
    args = parser.parse_args(argv)

    if not args.categories_dir.exists():
        parser.error(f"categories directory not found: {args.categories_dir}")

    data = collect_keywords(args.categories_dir)
    generate_report(data, args.output_json, args.output_md)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
