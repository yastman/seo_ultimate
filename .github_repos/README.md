# .github_repos — Внешние NLP библиотеки

**Назначение:** Референсные репозитории для SEO-анализа русских текстов

---

## Скачанные репозитории

| Репо | Размер | Источник | Назначение |
|------|--------|----------|------------|
| `natasha/` | 69 MB | [github.com/natasha/natasha](https://github.com/natasha/natasha) | NLP для русского языка |
| `stopwords-ru/` | 153 KB | [github.com/stopwords-iso/stopwords-ru](https://github.com/stopwords-iso/stopwords-ru) | Стоп-слова (558 слов) |

---

## План внедрения

### Фаза 1: Стоп-слова (ГОТОВО)

- [x] Скачать `stopwords-ru.txt` в `data/stopwords/`
- [x] Обновить `check_water_natasha.py` для использования расширенного списка
- [x] Fallback на pip `stop-words` если файл не найден

**Результат:** 558+ стоп-слов вместо ~200 базовых

---

### Фаза 2: Natasha — Полный pipeline

**Файл:** `.github_repos/natasha/docs.ipynb` — главный референс

**Текущее использование:**

```python
# check_water_natasha.py — только базовое
from natasha import Segmenter, MorphVocab, Doc
```

**Расширить до:**

```python
from natasha import (
    Segmenter,
    MorphVocab,
    NewsEmbedding,
    NewsMorphTagger,
    NewsSyntaxParser,
    NewsNERTagger,
    Doc
)
```

**Задачи:**

| # | Задача | Скрипт | Статус |
|---|--------|--------|--------|
| 2.1 | Морфологический тег (POS) | `check_water_natasha.py` | TODO |
| 2.2 | Лемматизация через MorphTagger | `check_water_natasha.py` | TODO |
| 2.3 | NER для детекции брендов | `seo_utils.py` (новая функция) | TODO |
| 2.4 | Синтаксический разбор | опционально | BACKLOG |

---

### Фаза 3: NER проверка брендов/городов

**Цель:** Автоматически находить и предупреждать о брендах/городах в тексте

**Создать:** `scripts/check_ner_brands.py`

```python
from natasha import NewsNERTagger, NewsEmbedding, Doc, Segmenter

# Детектируем:
# - ORG (организации) → бренды: Koch Chemie, Grass, Karcher
# - LOC (локации) → города: Киев, Харьков, Одесса
# - PER (персоны) → имена: нежелательны в SEO текстах
```

**Интеграция:**

- Добавить в `quality_runner.py` как Check 5
- Или в `seo-validate` skill

---

### Фаза 4: Advego-подобные метрики

**Референс:** Формулы из Advego SEO-анализатора

| Метрика | Формула | Статус |
|---------|---------|--------|
| Вода (%) | `(стоп-слова / всего слов) × 100` | ЕСТЬ |
| Классическая тошнота | `√(max_lemma_frequency)` | ЕСТЬ |
| Академическая тошнота | `(max_freq / total_significant) × 100` | ЕСТЬ |
| Уникальность лемм | `unique_lemmas / total_words` | TODO |
| Читаемость | Flesch-Kincaid для русского | BACKLOG |

---

## Полезные файлы

### Natasha

```
.github_repos/natasha/
├── docs.ipynb          # 47 KB — ГЛАВНЫЙ РЕФЕРЕНС с примерами
├── README.md           # Документация
├── natasha/
│   ├── morph/          # Морфология, лемматизация
│   ├── ner.py          # Named Entity Recognition
│   ├── extractors.py   # Извлечение сущностей
│   └── grammars/       # Yargy грамматики (даты, деньги, имена)
└── tests/              # Тесты — примеры использования
```

### Stopwords-ru

```
.github_repos/stopwords-ru/
├── stopwords-ru.txt    # 558 стоп-слов (уже скопирован в data/stopwords/)
└── README.md
```

---

## Как использовать docs.ipynb

```bash
# Открыть в Jupyter
jupyter notebook .github_repos/natasha/docs.ipynb

# Или просто читать как референс для кода
```

**Ключевые секции в docs.ipynb:**

1. Tokenization (Segmenter)
2. Morphology (MorphTagger)
3. Lemmatization (MorphVocab)
4. Syntax (SyntaxParser)
5. NER (NERTagger)
6. Extractors (даты, деньги, имена)

---

## Зависимости (requirements.txt)

Уже установлены:

```
natasha==1.6.0
pymorphy2==0.9.1
pymorphy2-dicts-ru==2.4.417127.4579844
navec==0.10.0
slovnet==0.6.0
razdel==0.5.0
yargy==0.16.0
```

---

## Приоритеты внедрения

| Приоритет | Задача | Эффект |
|-----------|--------|--------|
| **P0** | Стоп-слова 558+ | Точнее расчёт воды |
| **P1** | NER бренды/города | Автопроверка anti-spam |
| **P2** | Полный MorphTagger | Точнее лемматизация |
| **P3** | Синтаксис | Качество предложений |

---

## Дополнительные библиотеки (Context7 research)

### Рекомендованные к установке

| Библиотека | pip install | Назначение | Приоритет |
|------------|-------------|------------|-----------|
| **textdescriptives** | `pip install textdescriptives` | Метрики читаемости (Flesch, LIX, SMOG, Gunning-Fog) | P2 |
| **advertools** | `pip install advertools` | Word frequency, SEO анализ, n-grams | P3 |

---

### textdescriptives — Метрики текста

**Что умеет:**

- Readability scores: Flesch Reading Ease, Flesch-Kincaid Grade, SMOG, Gunning-Fog, ARI, Coleman-Liau, LIX, RIX
- Dependency distance (сложность предложений)
- Quality metrics (дубликаты n-gram, alpha ratio)
- Работает через spaCy pipeline

**Пример использования:**

```python
import textdescriptives as td

# Автоматически скачает spaCy модель
df = td.extract_metrics(
    text="Ваш текст здесь...",
    lang="ru",  # Для русского нужна ru модель
    metrics=["readability", "dependency_distance"]
)

# Или через spaCy pipeline
import spacy
nlp = spacy.load("ru_core_news_sm")
nlp.add_pipe("textdescriptives/readability")
doc = nlp("Текст для анализа")
doc._.readability  # dict с метриками
```

**Проблема:** Формулы читаемости (Flesch и др.) оптимизированы для английского. Для русского нужна адаптация или использование LIX (универсальная).

---

### advertools — SEO инструменты

**Что умеет:**

- `word_frequency()` — частотность слов с весами
- `word_tokenize()` — токенизация + n-grams
- URL анализ, emoji extraction
- SERP crawling

**Пример:**

```python
import advertools as adv

texts = ['Активная пена для бесконтактной мойки', 'Пена для автомойки']
word_freq = adv.word_frequency(texts)
# DataFrame с частотами слов
```

---

### spaCy для русского

**Модели:**

```bash
# Маленькая (быстрая)
python -m spacy download ru_core_news_sm

# Средняя (баланс)
python -m spacy download ru_core_news_md

# Большая (точная)
python -m spacy download ru_core_news_lg
```

**Лемматизация через spaCy:**

```python
import spacy
nlp = spacy.load("ru_core_news_sm")
doc = nlp("Студенты изучали языки программирования")
lemmas = [token.lemma_ for token in doc]
# ['студент', 'изучать', 'язык', 'программирование']
```

**Сравнение с Natasha:**

| Аспект | Natasha | spaCy ru |
|--------|---------|----------|
| Размер модели | ~50 MB | 15-500 MB |
| Скорость | Быстрее | Медленнее |
| NER качество | Хорошее | Хорошее |
| Зависимости | Меньше | Больше |
| Для проекта | ✅ Используем | Опционально |

---

### Что НЕ нужно добавлять

| Библиотека | Причина |
|------------|---------|
| YAKE | Keyword extraction — у нас уже есть keywords JSON |
| Jieba | Для китайского языка |
| HanLP | Для китайского языка |
| SerpAPI | Платный API, у нас уже есть SERP данные |
| DataForSEO | Платный API |

---

**Updated:** 2025-12-10
