# Tasks

**Обновлено:** 2026-01-20

---

## Текущий этап: Content Generation

```
/content-generator → /quality-gate → /deploy
```

---

## Файлы задач

| Файл | Что делать |
|------|------------|
| **[`TODO_RESEARCH.md`](TODO_RESEARCH.md)** | Чеклист категорий для research через Perplexity |
| **[`TODO_CONTENT.md`](TODO_CONTENT.md)** | Чеклист категорий для генерации контента |
| [`CONTENT_STATUS.md`](CONTENT_STATUS.md) | Детальный аудит всех категорий |

---

## Workflow

### 1. Research (TODO_RESEARCH.md)
```
/seo-research {slug} → копируем промпт в Perplexity → сохраняем в RESEARCH_DATA.md
```

### 2. Content (TODO_CONTENT.md)
```
/content-generator {slug} → проверяем результат
```

### 3. Проверка и деплой
```
/quality-gate {slug} → /deploy-to-opencart {slug}
```

---

## Статус (2026-01-20)

| Этап | Готово | Осталось |
|------|--------|----------|
| Research | 45 | 1 ждёт Perplexity (zashchitnye-pokrytiya) |
| Content | 30 | 16 готовы к генерации |

---

## Следующие действия

1. **Сейчас можно:** Генерировать контент для **16 категорий** (есть research)

   **Приоритет 1 (нет контента):**
   - neytralizatory-zapakha, akkumulyatornaya, ukhod-za-naruzhnym-plastikom
   - mekhovye, poliroli-dlya-plastika, ukhod-za-kozhey
   - ukhod-za-intererom, vedra-i-emkosti

   **Приоритет 2 (research добавлен недавно):**
   - antidozhd, keramika-dlya-diskov, kislotnyy, kvik-deteylery
   - zhidkiy-vosk, tverdyy-vosk, silanty, podarochnyy

2. **Ждёт Perplexity:** zashchitnye-pokrytiya (L1 hub) — RESEARCH_PROMPT.md готов
