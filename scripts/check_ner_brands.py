#!/usr/bin/env python3
"""
NER Brand/City Checker using Natasha

Автоматически находит и предупреждает о:
- ORG (организации) → бренды: Koch Chemie, Grass, Karcher, Sonax
- LOC (локации) → города: Киев, Харьков, Одесса
- PER (персоны) → имена: нежелательны в SEO текстах

Usage:
    python3 scripts/check_ner_brands.py <file.md>
    python3 scripts/check_ner_brands.py <file.md> --json

Exit codes:
    0 = PASS (no forbidden entities)
    1 = WARNING (found entities)
"""

import json
import re
import sys
from pathlib import Path

try:
    from natasha import (
        Doc,
        NewsEmbedding,
        NewsNERTagger,
        Segmenter,
    )

    NATASHA_FULL = True
except ImportError:
    # Fallback to basic Natasha
    try:
        from natasha import Doc, Segmenter

        NATASHA_FULL = False
    except ImportError:
        print("❌ Natasha не установлена: pip install natasha")
        sys.exit(2)


# Blacklist брендов (явные упоминания)
BRAND_BLACKLIST = {
    # Химия
    "koch chemie",
    "koch",
    "grass",
    "грасс",
    "karcher",
    "керхер",
    "kärcher",
    "sonax",
    "сонакс",
    "meguiars",
    "мегуарс",
    "chemical guys",
    "turtle wax",
    "тёртл вакс",
    "hi-gear",
    "хай-гир",
    "lavr",
    "лавр",
    "liqui moly",
    "ликви моли",
    "mannol",
    "маннол",
    "felix",
    "феликс",
    "aim-one",
    "аим-ван",
    "runway",
    "ранвей",
    "abro",
    "абро",
    "doctor wax",
    "доктор вакс",
    "soft99",
    "софт99",
    # Оборудование
    "bosch",
    "бош",
    "makita",
    "макита",
    "dewalt",
    "девольт",
    "stihl",
    "штиль",
    "husqvarna",
    "хускварна",
    # Авто
    "toyota",
    "тойота",
    "bmw",
    "бмв",
    "mercedes",
    "мерседес",
    "volkswagen",
    "фольксваген",
    "audi",
    "ауди",
    "ford",
    "форд",
}

# Blacklist городов
CITY_BLACKLIST = {
    # Украина
    "київ",
    "киев",
    "kyiv",
    "kiev",
    "харків",
    "харьков",
    "kharkiv",
    "одеса",
    "одесса",
    "odesa",
    "odessa",
    "дніпро",
    "днепр",
    "dnipro",
    "львів",
    "львов",
    "lviv",
    "запоріжжя",
    "запорожье",
    "zaporizhzhia",
    "вінниця",
    "винница",
    "vinnytsia",
    "полтава",
    "poltava",
    "чернігів",
    "чернигов",
    "chernihiv",
    "черкаси",
    "черкассы",
    "cherkasy",
    "суми",
    "сумы",
    "sumy",
    "житомир",
    "zhytomyr",
    "миколаїв",
    "николаев",
    "mykolaiv",
    "херсон",
    "kherson",
    "рівне",
    "ровно",
    "rivne",
    "луцьк",
    "луцк",
    "lutsk",
    "ужгород",
    "uzhhorod",
    "тернопіль",
    "тернополь",
    "ternopil",
    "івано-франківськ",
    "ивано-франковск",
    "кропивницький",
    "кропивницкий",
    # Другие страны (если упоминают)
    "москва",
    "moscow",
    "санкт-петербург",
    "минск",
    "варшава",
}

# FIX v8.5: Whitelist для false positives (слова, которые похожи на города)
# Эти слова проверяются по контексту: если перед ними нет предлога "в/из/до/на" — не город
FALSE_POSITIVE_CITIES = {
    "ровно",  # наречие: "ровно столько", "ровно по центру"
    "суми",  # может быть "суми" в контексте "суммы" (опечатка)
}

# Strict Blacklist (Фразы-паразиты, которые вызывают FAIL)
STRICT_PHRASES = [
    "в современном мире",
    "широкий ассортимент",
    "высокое качество по доступной цене",
    "является неотъемлемой частью",  # v7.2 requirement
]

# AI-fluff фразы (антипаттерны, вызывают WARNING)
AI_FLUFF_PATTERNS = [
    r"в этой статье",
    r"давайте разберёмся",
    r"давайте разберемся",
    r"в данной статье",
    r"мы рассмотрим",
    r"вы узнаете",
    r"в заключение",
    r"подводя итоги",
    r"как было сказано выше",
    r"как мы уже говорили",
    r"не секрет, что",
    r"ни для кого не секрет",
    r"стоит отметить",
    r"важно отметить",
    r"следует отметить",
    r"необходимо отметить",
    r"нельзя не отметить",
    r"безусловно",
    r"несомненно",
    r"очевидно, что",
]

# Attempt to sync stoplists with config SSOT.
try:
    from scripts.config import (
        AI_FLUFF_PATTERNS as AI_FLUFF_PATTERNS_SSOT,
    )
    from scripts.config import (
        FALSE_POSITIVE_CITIES as FALSE_POSITIVE_CITIES_SSOT,
    )
    from scripts.config import (
        STRICT_BLACKLIST_PHRASES as STRICT_PHRASES_SSOT,
    )
except ImportError:
    try:
        from config import (
            AI_FLUFF_PATTERNS as AI_FLUFF_PATTERNS_SSOT,
        )
        from config import (
            FALSE_POSITIVE_CITIES as FALSE_POSITIVE_CITIES_SSOT,
        )
        from config import (
            STRICT_BLACKLIST_PHRASES as STRICT_PHRASES_SSOT,
        )
    except ImportError:
        AI_FLUFF_PATTERNS_SSOT = None
        STRICT_PHRASES_SSOT = None
        FALSE_POSITIVE_CITIES_SSOT = None

if AI_FLUFF_PATTERNS_SSOT:
    AI_FLUFF_PATTERNS = AI_FLUFF_PATTERNS_SSOT
if STRICT_PHRASES_SSOT:
    STRICT_PHRASES = STRICT_PHRASES_SSOT
if FALSE_POSITIVE_CITIES_SSOT:
    FALSE_POSITIVE_CITIES = set(FALSE_POSITIVE_CITIES_SSOT)

# Предлоги, которые указывают на географический контекст
LOCATION_PREPOSITIONS = {"в", "из", "до", "на", "під", "под", "у", "із", "з"}


def is_false_positive_location(word: str, context: str) -> bool:
    """
    Проверяет, является ли найденное слово ложноположительным городом.

    Args:
        word: найденное слово (например "ровно")
        context: контекст вокруг слова

    Returns:
        True если это false positive (не город), False если это реальный город
    """
    word_lower = word.lower()

    # Если слово не в whitelist — это реальный город
    if word_lower not in FALSE_POSITIVE_CITIES:
        return False

    context_lower = context.lower()

    # Проверяем наличие предлога перед словом
    # Паттерн: предлог + пробел(ы) + слово
    for prep in LOCATION_PREPOSITIONS:
        pattern = rf"\b{prep}\s+{re.escape(word_lower)}\b"
        if re.search(pattern, context_lower):
            # Нашли предлог перед словом — это скорее всего город
            return False

    # Предлога нет — скорее всего это наречие/другое использование
    return True


def clean_markdown(text: str) -> str:
    """
    Удаляет markdown разметку для анализа.

    NOTE: Uses unified clean_markdown from seo_utils (SSOT).
    Fallback to local implementation if import fails.
    """
    # Try importing from seo_utils (SSOT - Single Source of Truth)
    try:
        from scripts.seo_utils import clean_markdown as seo_clean_markdown

        return seo_clean_markdown(text)
    except ImportError:
        try:
            from seo_utils import clean_markdown as seo_clean_markdown

            return seo_clean_markdown(text)
        except ImportError:
            # Fallback (local implementation)
            text = re.sub(r"^---\n.*?\n---\n", "", text, flags=re.DOTALL)
            text = re.sub(r"^#+\s+", "", text, flags=re.MULTILINE)
            text = re.sub(r"\[([^\]]+)\]\([^)]+\)", r"\1", text)
            text = re.sub(r"\*{1,2}([^*]+)\*{1,2}", r"\1", text)
            text = re.sub(r"^[-*]\s+", "", text, flags=re.MULTILINE)
            return text


def check_blacklist(text: str) -> dict:
    """Проверяет текст на наличие запрещённых слов."""
    text_lower = text.lower()

    found_brands = []
    found_cities = []
    found_ai_fluff = []
    found_strict = []

    # Проверка брендов
    for brand in BRAND_BLACKLIST:
        if brand in text_lower:
            # Найти точную позицию
            for match in re.finditer(re.escape(brand), text_lower):
                # Получить контекст (±30 символов)
                start = max(0, match.start() - 30)
                end = min(len(text), match.end() + 30)
                context = text[start:end].replace("\n", " ")
                found_brands.append({"entity": brand, "type": "BRAND", "context": f"...{context}..."})

    # Проверка городов (с фильтрацией false positives)
    for city in CITY_BLACKLIST:
        if city in text_lower:
            for match in re.finditer(re.escape(city), text_lower):
                start = max(0, match.start() - 30)
                end = min(len(text), match.end() + 30)
                context = text[start:end].replace("\n", " ")

                # FIX v8.5: Проверяем false positives (например "ровно" как наречие)
                if is_false_positive_location(city, context):
                    continue  # Пропускаем false positive

                found_cities.append({"entity": city, "type": "CITY", "context": f"...{context}..."})

    # Проверка Strict Phrases (FAIL)
    for phrase in STRICT_PHRASES:
        if phrase in text_lower:
            for match in re.finditer(re.escape(phrase), text_lower):
                start = max(0, match.start() - 30)
                end = min(len(text), match.end() + 30)
                context = text[start:end].replace("\n", " ")
                found_strict.append({"entity": phrase, "type": "STRICT_BLACKLIST", "context": f"...{context}..."})

    # Проверка AI-fluff
    for pattern in AI_FLUFF_PATTERNS:
        matches = re.finditer(pattern, text_lower)
        for match in matches:
            start = max(0, match.start() - 20)
            end = min(len(text), match.end() + 20)
            context = text[start:end].replace("\n", " ")
            found_ai_fluff.append({"entity": match.group(), "type": "AI_FLUFF", "context": f"...{context}..."})

    return {
        "brands": found_brands,
        "cities": found_cities,
        "ai_fluff": found_ai_fluff,
        "strict_phrases": found_strict,
    }


def check_ner(text: str) -> dict:
    """Использует Natasha NER для поиска сущностей."""
    if not NATASHA_FULL:
        return {"ner_entities": [], "warning": "NER недоступен (установите natasha полностью)"}

    # Инициализация Natasha NER pipeline
    segmenter = Segmenter()
    emb = NewsEmbedding()
    ner_tagger = NewsNERTagger(emb)

    # Очистить текст
    clean_text = clean_markdown(text)

    # Создать Doc и обработать
    doc = Doc(clean_text)
    doc.segment(segmenter)
    doc.tag_ner(ner_tagger)

    entities = []
    for span in doc.spans:
        # span.type: PER, LOC, ORG
        entity_text = span.text
        entity_type = span.type

        # Получить контекст
        start = max(0, span.start - 30)
        end = min(len(clean_text), span.stop + 30)
        context = clean_text[start:end].replace("\n", " ")

        entities.append({"entity": entity_text, "type": entity_type, "context": f"...{context}..."})

    return {"ner_entities": entities}


def analyze_file(filepath: str, output_json: bool = False) -> int:
    """
    Анализирует файл на наличие запрещённых сущностей.

    Returns:
        0 = PASS, 1 = WARNING (found issues)
    """
    path = Path(filepath)
    if not path.exists():
        print(f"❌ Файл не найден: {filepath}")
        return 2

    text = path.read_text(encoding="utf-8")

    # Blacklist проверка (быстрая)
    blacklist_results = check_blacklist(text)

    # NER проверка (если доступна)
    ner_results = check_ner(text)

    # Объединить результаты
    results = {
        "file": str(path),
        "blacklist": blacklist_results,
        "ner": ner_results,
        "summary": {
            "brands_count": len(blacklist_results["brands"]),
            "cities_count": len(blacklist_results["cities"]),
            "ai_fluff_count": len(blacklist_results["ai_fluff"]),
            "ner_org_count": len([e for e in ner_results.get("ner_entities", []) if e["type"] == "ORG"]),
            "ner_loc_count": len([e for e in ner_results.get("ner_entities", []) if e["type"] == "LOC"]),
            "ner_per_count": len([e for e in ner_results.get("ner_entities", []) if e["type"] == "PER"]),
        },
    }

    total_issues = (
        results["summary"]["brands_count"] + results["summary"]["cities_count"] + results["summary"]["ai_fluff_count"]
    )

    results["summary"]["total_issues"] = total_issues
    results["summary"]["status"] = "PASS" if total_issues == 0 else "WARNING"

    if output_json:
        print(json.dumps(results, ensure_ascii=False, indent=2))
    else:
        print(f"\n{'=' * 60}")
        print(f"NER & Blacklist Check: {path.name}")
        print(f"{'=' * 60}")

        # Blacklist results
        if blacklist_results["brands"]:
            print(f"\n⚠️  БРЕНДЫ ({len(blacklist_results['brands'])}):")
            for item in blacklist_results["brands"][:5]:  # Max 5
                print(f"   • {item['entity']}: {item['context']}")

        if blacklist_results["cities"]:
            print(f"\n⚠️  ГОРОДА ({len(blacklist_results['cities'])}):")
            for item in blacklist_results["cities"][:5]:
                print(f"   • {item['entity']}: {item['context']}")

        if blacklist_results["ai_fluff"]:
            print(f"\n⚠️  AI-FLUFF ({len(blacklist_results['ai_fluff'])}):")
            for item in blacklist_results["ai_fluff"][:5]:
                print(f'   • "{item["entity"]}": {item["context"]}')

        # NER results (если есть что-то интересное)
        ner_orgs = [e for e in ner_results.get("ner_entities", []) if e["type"] == "ORG"]
        ner_locs = [e for e in ner_results.get("ner_entities", []) if e["type"] == "LOC"]

        if ner_orgs:
            print(f"\nℹ️  NER ORG (организации): {len(ner_orgs)}")
            for item in ner_orgs[:3]:
                print(f"   • {item['entity']}")

        if ner_locs:
            print(f"\nℹ️  NER LOC (локации): {len(ner_locs)}")
            for item in ner_locs[:3]:
                print(f"   • {item['entity']}")

        # Summary
        print(f"\n{'=' * 60}")
        if total_issues == 0:
            print("✅ PASS: Запрещённые сущности не найдены")
        else:
            print(f"⚠️  WARNING: Найдено {total_issues} проблем")
            print("   Рекомендация: удалите упоминания брендов, городов и AI-фраз")
        print(f"{'=' * 60}\n")

    return 0 if total_issues == 0 else 1


def main():
    if len(sys.argv) < 2:
        print(__doc__)
        sys.exit(0)

    filepath = sys.argv[1]
    output_json = "--json" in sys.argv

    exit_code = analyze_file(filepath, output_json)
    sys.exit(exit_code)


if __name__ == "__main__":
    main()
