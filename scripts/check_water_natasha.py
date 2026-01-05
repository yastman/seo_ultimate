#!/usr/bin/env python3
"""
Stage 8.1: Water and Nausea Calculator using NATASHA (from GitHub)

SEO 2025 v7.3 (Shop Mode - Buying Guides)

Рассчитывает метрики качества текста по формулам Адвего:
- Вода (%) = (стоп-слова / всего слов) × 100 | Target: 40-60% (Tier A/B), 40-65% (Tier C)
- Классическая тошнота = √(max_lemma_frequency) | Target: ≤3.5 (BLOCKER >4.0)
- Академическая тошнота = (max_freq / total_significant) × 100 | Target: 7-9.5%

Usage:
    python3 scripts/check_water_natasha.py <file.md> [target_min] [target_max]
"""

import math
import re
import sys
from collections import Counter
from pathlib import Path

if __name__ == "__main__" and __package__ is None:
    sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

try:
    from natasha import Doc, MorphVocab, NewsEmbedding, NewsMorphTagger, Segmenter

    NATASHA_FULL = True
except ImportError:
    try:
        from natasha import Doc, MorphVocab, Segmenter

        NATASHA_FULL = False
    except ImportError as e:
        print(f"❌ Ошибка импорта: {e}")
        print("\nУстановите зависимости:")
        print("  pip install natasha")
        sys.exit(1)

# Кэш для тяжёлых объектов Natasha (загружаются один раз)
_NLP_CACHE = {}


def get_nlp_pipeline():
    """Singleton для NLP объектов Natasha (экономит ~50MB RAM при повторных вызовах)."""
    if "initialized" not in _NLP_CACHE:
        _NLP_CACHE["segmenter"] = Segmenter()
        _NLP_CACHE["morph_vocab"] = MorphVocab()
        if NATASHA_FULL:
            emb = NewsEmbedding()
            _NLP_CACHE["morph_tagger"] = NewsMorphTagger(emb)
        else:
            _NLP_CACHE["morph_tagger"] = None
        _NLP_CACHE["initialized"] = True
    return _NLP_CACHE


# Загрузить расширенный список стоп-слов (stopwords-iso)
def load_stopwords(lang="ru"):
    """
    Загружает расширенный список стоп-слов из stopwords-{lang}.txt
    Fallback: если файл не найден, использует базовый список

    Args:
        lang: 'ru' or 'uk'
    """
    stopwords_file = Path(__file__).parent.parent / "data" / "stopwords" / f"stopwords-{lang}.txt"

    # Fallback для UK на RU, если UK файл отсутствует
    if lang == "uk" and not stopwords_file.exists():
        stopwords_file = (
            Path(__file__).parent.parent / "uk" / "data" / "stopwords" / "stopwords-uk.txt"
        )

    if stopwords_file.exists():
        with open(stopwords_file, encoding="utf-8") as f:
            stopwords = {line.strip() for line in f if line.strip()}
        print(f"ℹ️  Загружено {len(stopwords)} стоп-слов из {stopwords_file.name}")
        return stopwords
    else:
        # Fallback: базовый набор стоп-слов
        print(f"⚠️  Файл {stopwords_file} не найден, использую базовый набор")
        try:
            from stop_words import get_stop_words

            lang_code = "russian" if lang == "ru" else "ukrainian"
            return set(get_stop_words(lang_code))
        except ImportError:
            # Минимальный набор если ничего не установлено
            if lang == "uk":
                return {
                    "і",
                    "в",
                    "не",
                    "на",
                    "з",
                    "що",
                    "це",
                    "як",
                    "а",
                    "по",
                    "для",
                    "від",
                    "із",
                    "до",
                    "або",
                    "же",
                    "про",
                    "але",
                    "за",
                    "у",
                    "який",
                    "також",
                    "більше",
                    "бути",
                    "може",
                    "дуже",
                }
            else:
                return {
                    "и",
                    "в",
                    "не",
                    "на",
                    "с",
                    "что",
                    "это",
                    "как",
                    "а",
                    "по",
                    "для",
                    "от",
                    "из",
                    "к",
                    "или",
                    "же",
                    "о",
                    "но",
                    "за",
                    "у",
                    "который",
                    "также",
                    "более",
                    "быть",
                    "может",
                    "очень",
                }


# Дополнительные стоп-слова (вода) из анализа Адвего
ADDITIONAL_STOP_WORDS = {
    "особенно",
    "актуально",
    "важно",
    "помнить",
    "подход",
    "снижает",
    "риск",
    "позволяет",
    "является",
    "данный",
    "следует",
    "необходимо",
    "можно",
    "нужно",
    "различный",
    "который",
    "такой",
    "этот",
    "свой",
    "весь",
    "один",
    "другой",
    "наш",
    "ваш",
    "тот",
    "сам",
    "мочь",
    "сказать",
}


def clean_markdown(text):
    """
    Удаляет markdown-разметку.

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
            # Fallback (local implementation if seo_utils unavailable)
            text = re.sub(r"^---\n.*?\n---\n", "", text, flags=re.DOTALL)
            text = re.sub(r"```.*?```", " ", text, flags=re.DOTALL)
            text = re.sub(r"`[^`]+`", " ", text)
            text = re.sub(r"\[([^\]]+)\]\([^\)]+\)", r"\1", text)
            text = re.sub(r"^#{1,6}\s+", "", text, flags=re.MULTILINE)
            text = re.sub(r"\|.*?\|", " ", text)
            text = re.sub(r"[*_]{1,2}([^*_]+)[*_]{1,2}", r"\1", text)
            text = re.sub(r"\s+", " ", text).strip()
            return text


def calculate_metrics_from_text(text: str, lang: str = "ru") -> dict:
    """
    Рассчитывает метрики качества текста (вода, тошнота).

    Args:
        text: Markdown текст для анализа
        lang: 'ru' or 'uk' - язык для стоп-слов

    Returns:
        Dict с метриками или None если текст пустой

    NOTE: Использует правильный pipeline Natasha:
        1. doc.segment(segmenter)
        2. doc.tag_morph(morph_tagger)  # Морфология
        3. token.lemmatize(morph_vocab)  # Лемматизация через метод токена
    """
    # Загрузить стоп-слова для нужного языка
    stopwords = load_stopwords(lang)
    stopwords.update(ADDITIONAL_STOP_WORDS)  # Добавляем дополнительные

    # Получаем кэшированные объекты NLP
    nlp = get_nlp_pipeline()
    segmenter = nlp["segmenter"]
    morph_vocab = nlp["morph_vocab"]
    morph_tagger = nlp["morph_tagger"]

    # Очистить от markdown
    clean_text = clean_markdown(text)

    doc = Doc(clean_text)
    doc.segment(segmenter)

    # Применяем морфологический анализ (если доступен полный Natasha)
    if morph_tagger:
        doc.tag_morph(morph_tagger)

    if not doc.tokens:
        print("❌ Текст не содержит токенов")
        return None

    # Извлечь только русские слова
    russian_tokens = [
        token for token in doc.tokens if re.match(r"[а-яё]+", token.text.lower(), re.UNICODE)
    ]

    if not russian_tokens:
        print("❌ Текст не содержит русских слов")
        return None

    total_words = len(russian_tokens)
    words_lower = [token.text.lower() for token in russian_tokens]

    # 1. ВОДА: стоп-слова
    # Калибровочный коэффициент для соответствия Адвего (Natasha ~22% → Адвего ~52%)
    ADVEGO_MULTIPLIER = 2.4  # Коэффициент синхронизации с Адвего (v7.2 Update)

    water_count = sum(1 for word in words_lower if word in stopwords)
    water_percent_raw = (water_count / total_words) * 100
    water_percent = water_percent_raw * ADVEGO_MULTIPLIER

    # 2. ЛЕММАТИЗАЦИЯ (правильный способ через Natasha)
    lemmas = []
    for token in russian_tokens:
        if morph_tagger and hasattr(token, "pos"):
            # Полный pipeline: используем lemmatize() через метод токена
            token.lemmatize(morph_vocab)
            if token.lemma:
                lemmas.append(token.lemma)
            else:
                lemmas.append(token.text.lower())
        else:
            # Fallback: прямой вызов morph_vocab (старый способ)
            parsed = morph_vocab(token.text.lower())
            if parsed:
                lemmas.append(parsed[0].normal)
            else:
                lemmas.append(token.text.lower())

    # 3. КЛАССИЧЕСКАЯ ТОШНОТА
    lemma_counts = Counter(lemmas)
    significant_lemma_counts = {
        lemma: count for lemma, count in lemma_counts.items() if lemma not in stopwords
    }

    if significant_lemma_counts:
        most_common_lemma, max_frequency = max(significant_lemma_counts.items(), key=lambda x: x[1])
    else:
        most_common_lemma, max_frequency = lemma_counts.most_common(1)[0]

    classic_nausea = math.sqrt(max_frequency)

    # 4. АКАДЕМИЧЕСКАЯ ТОШНОТА (Advego-like)
    significant_lemmas = {
        lemma: count
        for lemma, count in lemma_counts.items()
        if count > 1 and lemma not in stopwords
    }

    if significant_lemmas:
        total_significant = sum(significant_lemmas.values())
        max_freq_significant = max(significant_lemmas.values())
        most_common_significant = max(significant_lemmas, key=significant_lemmas.get)
        academic_nausea = max_freq_significant / total_significant * 100
    else:
        total_significant = 0
        max_freq_significant = 0
        most_common_significant = None
        academic_nausea = 0.0

    # 5. ИНДЕКС ПОВТОРОВ ЛЕММ
    repeated_words_count = sum(count for count in lemma_counts.values() if count > 1)
    lemma_repetition_index = (repeated_words_count / total_words) * 100 if total_words > 0 else 0.0

    return {
        "total_words": total_words,
        "water_count": water_count,
        "water_percent_raw": water_percent_raw,
        "water_percent": water_percent,
        "classic_nausea": classic_nausea,
        "most_common_lemma": most_common_lemma,
        "max_frequency": max_frequency,
        "academic_nausea": academic_nausea,
        "most_common_significant": most_common_significant,
        "max_freq_significant": max_freq_significant,
        "total_significant": total_significant,
        "lemma_repetition_index": lemma_repetition_index,
        "repeated_words_count": repeated_words_count,
        "unique_lemmas": len(lemma_counts),
    }


def calculate_metrics(file_path):
    with open(file_path, encoding="utf-8") as f:
        text = f.read()
    return calculate_metrics_from_text(text)


def check_water(file_path, target_min=40, target_max=60):
    """
    Проверяет воду и тошноту по стандартам SEO 2025 v7.3.

    Targets:
    - Вода: 40-60% (Tier A/B), 40-65% (Tier C)
    - Классическая тошнота: ≤3.5
    - Академическая тошнота: 7-9.5%
    """
    print(f"📊 Анализ качества текста (NATASHA): {Path(file_path).name}\n")

    metrics = calculate_metrics(file_path)

    if not metrics:
        return 1

    # Вывод результатов
    print(f"Всего слов: {metrics['total_words']}")
    print(f"Уникальных лемм: {metrics['unique_lemmas']}")
    print()

    # 1. ВОДА
    print(f"💧 ВОДА (Адвего): {metrics['water_percent']:.1f}%")
    print(
        f"   Raw (Natasha): {metrics['water_percent_raw']:.1f}% × 2.4 = {metrics['water_percent']:.1f}%"
    )
    print(f"   Стоп-слова: {metrics['water_count']} из {metrics['total_words']}")
    print(f"   Цель: {target_min}-{target_max}%")

    if target_min <= metrics["water_percent"] <= target_max:
        print("   ✅ PASS")
    elif metrics["water_percent"] > target_max:
        excess = metrics["water_percent"] - target_max
        if excess <= 5.0:
            print(f"   ⚠️ WARNING: Превышение на {excess:.1f}% (допустимо для Tier C)")
        else:
            print(f"   ⚠️ WARNING: Превышение на {excess:.1f}%")
    else:
        deficit = target_min - metrics["water_percent"]
        print(f"   ⚠️ WARNING: Ниже минимума на {deficit:.1f}%")

    print()

    # 2. КЛАССИЧЕСКАЯ ТОШНОТА
    print(f"🤢 КЛАССИЧЕСКАЯ ТОШНОТА: {metrics['classic_nausea']:.2f}")
    print(
        f"   Самое частое слово: '{metrics['most_common_lemma']}' ({metrics['max_frequency']} раз)"
    )
    print("   Цель: ≤3.5 (BLOCKER >4.0)")

    if metrics["classic_nausea"] <= 3.5:
        print("   ✅ PASS")
    elif metrics["classic_nausea"] <= 4.0:
        print(f"   ⚠️ WARNING: Превышение ({metrics['classic_nausea']:.2f} > 3.5)")
    else:
        print(f"   ❌ BLOCKER: Критическое превышение ({metrics['classic_nausea']:.2f} > 4.0)")

    print()

    # 3. АКАДЕМИЧЕСКАЯ ТОШНОТА
    # v7.3 Target: 7-9.5%
    ACADEMIC_MIN = 7.0
    ACADEMIC_MAX = 9.5

    print(f"📚 АКАДЕМИЧЕСКАЯ ТОШНОТА (Advego-like): {metrics['academic_nausea']:.1f}%")
    if metrics["most_common_significant"]:
        print(
            f"   Самое частое значимое слово: '{metrics['most_common_significant']}' ({metrics['max_freq_significant']} раз)"
        )
        print(f"   Значимых слов (без стоп-слов, freq>1): {metrics['total_significant']}")
    else:
        print("   Нет повторяющихся значимых слов")

    print(f"   Цель: {ACADEMIC_MIN}-{ACADEMIC_MAX}% (Адвего оптимум)")

    if ACADEMIC_MIN <= metrics["academic_nausea"] <= ACADEMIC_MAX:
        print("   ✅ PASS (Адвего оптимум)")
    elif metrics["academic_nausea"] < ACADEMIC_MIN:
        print(f'   🟦 INFO: Текст "сухой" ({metrics["academic_nausea"]:.1f}% < {ACADEMIC_MIN}%)')
    elif ACADEMIC_MAX < metrics["academic_nausea"] <= 12.0:
        print(
            f"   ⚠️ WARNING: Начинается переспам ({metrics['academic_nausea']:.1f}% > {ACADEMIC_MAX}%)"
        )
    else:
        print(f"   ❌ BLOCKER: Критический переспам ({metrics['academic_nausea']:.1f}% > 12%)")

    print()

    # 4. ИНДЕКС ПОВТОРОВ ЛЕММ
    print(f"🔁 ИНДЕКС ПОВТОРОВ ЛЕММ: {metrics['lemma_repetition_index']:.1f}%")
    print(f"   Повторяющиеся леммы: {metrics['repeated_words_count']} из {metrics['total_words']}")
    print("   (вспомогательная метрика для внутреннего анализа)")

    print()
    print("ℹ️ Используется библиотека Natasha для морфологического анализа")
    # Для вывода статистики снова загрузим стоп-слова (или можно передать их, но проще загрузить)
    stopwords_list = load_stopwords()
    print(f"ℹ️ Стоп-слов: {len(stopwords_list)} (stopwords-iso + дополнительные)")

    return 0


def main(argv: list[str] | None = None) -> int:
    argv = sys.argv[1:] if argv is None else argv

    if len(argv) < 1:
        print("Usage: check_water_natasha.py <file.md> [target_min] [target_max]")
        return 1

    file_path = argv[0]

    # Defaults v7.3: 40-60
    target_min = int(argv[1]) if len(argv) > 1 else 40
    target_max = int(argv[2]) if len(argv) > 2 else 60

    if not Path(file_path).exists():
        print(f"❌ Файл не найден: {file_path}")
        return 1

    return check_water(file_path, target_min, target_max)


if __name__ == "__main__":
    raise SystemExit(main())
