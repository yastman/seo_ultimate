# Tasks

**Обновлено:** 2026-01-19

---

## Текущий этап: Research → Content

```
/seo-research → Perplexity → /content-generator → /quality-gate → /deploy
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

## Статус (2026-01-19)

| Этап | Готово | Осталось |
|------|--------|----------|
| Research | 31 | 15 |
| Content | 31 | 6 готовы к генерации, 15 ждут research |

---

## Следующие действия

1. **Сейчас можно:** Генерировать контент для 6 категорий (есть research)
   - vedra-i-emkosti, ukhod-za-naruzhnym-plastikom, mekhovye
   - poliroli-dlya-plastika, ukhod-za-kozhey, ukhod-za-intererom

2. **Нужен research:** 15 категорий — см. TODO_RESEARCH.md
