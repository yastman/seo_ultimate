# 📁 `data/input/` — Input Data

**Назначение:** Входные данные для workflow

**↑ Назад:** [`../../INDEX.md`](../../INDEX.md)

---

## 📄 Файлы

| Файл | Размер | Назначение | Используется |
|------|--------|------------|--------------|
| `поисковая_выдача_топ_10.csv` | 1.2MB | SERP top-10 URLs | Stage 1 (url-extraction-agent) |
| `Структура Ultimate финал - Лист2.csv` | 20KB | Структура категорий + keywords | Stage 4 (data-preparation-agent) |

---

## 📊 Формат SERP CSV

**Колонки:**

- Keyword
- URL
- Position
- Domain
- Title
- Description

---

## 📊 Формат структуры CSV

**Колонки:**

- Category slug
- Tier (A/B/C)
- Keywords (comma-separated)
- Parent category

---

**Updated:** 2025-11-12
