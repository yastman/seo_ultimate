# TZ_GPT_VISION.md — архивное видение после аудита

**Проект:** Ultimate.net.ua — SEO Content Pipeline  
**Статус:** superseded by `TZ_FINAL.md` v4.0 (Post‑Audit).  
**Назначение:** зафиксировать выводы аудита и steady‑state, чтобы понимать расхождения с фактом.  
**Дальнейшие изменения/план:** смотреть только `TZ_FINAL.md`.  
**Дата фиксации:** 2025‑12‑12 (обновлено после ревизии)

---

## 1. Коротко о проекте

Локальный Python‑конвейер для SEO‑контента категорий автохимии.

**Вход:** `slug + tier (A/B/C)` + CSV семантики + (опц.) SERP/MEGA.  
**Желаемый выход (RU‑only):**

- `categories/{slug}/content/{slug}_ru.md`
- `categories/{slug}/meta/{slug}_meta.json` (RU)
- `categories/{slug}/deliverables/*` + `QUALITY_REPORT.md`

Контракт рабочей зоны — `categories/{slug}/…`. Качество — `scripts/quality_runner.py` (v7.3).

---

## 2. Ключевые факты (синхронизировано с аудитом)

1. **Task‑файлов нет.** В корне нет `task_{slug}.json`; часть скриптов ожидает task‑путь.
2. **Двойной SSOT не решён.** `prompts/produce.md` и `.claude/skills/seo-content/SKILL.md` почти дублируют друг друга. Выбор не зафиксирован.
3. **RU‑only цель, но фактически RU+UK.** UK присутствует в `README.md`, `categories/README.md`, `CLAUDE.md`, `prompts/*`, `.claude/skills/seo-meta`, `.claude/skills/seo-package`, `.claude/skills/seo-translator`.
4. **Cleanup не выполнен.** В репо всё ещё есть `.claude/agents_archive/`, `.claude/skills_archive/`, `.claude/commands/` и заявленные “дубликаты CSV”.
5. **Версионный дрейф.** `TZ_FINAL.md` = v4.0, `README.md` = v4.3, `SEO_MASTER.md` = v1.0; архитектура описана по‑разному.
6. **Расширение до 17 L3 не конкретизировано.** 8 новых slug/tier не перечислены в файлах; ссылку на `Лист1.csv` недостаточно.

---

## 3. Steady‑state: одна категория (минимальный режим, целевой)

1. Init: создать `categories/{slug}/` + `task_{slug}.json` (после фиксации схемы).
2. Keywords JSON: `python3 scripts/parse_semantics_to_json.py {slug} {tier}` → `data/{slug}.json`.
3. (Опционально для Tier A) конкуренты: SERP → URLs; MEGA → `filter_mega_competitors.py {slug}` → `meta_patterns.json`.
4. Написать RU текст + RU meta строго по `SEO_MASTER.md` (RU‑only).
5. Проверка: `PYTHONPATH=. python3 scripts/quality_runner.py categories/{slug}/content/{slug}_ru.md "{keyword}" {tier}`; правки до PASS.
6. Deliverables (опц.): скопировать RU/Meta в `deliverables/`, приложить `QUALITY_REPORT.md`.

---

## 4. Steady‑state: массово (17 категорий, RU‑only)

- Разово: подготовить все категории и task‑файлы через обновлённый `scripts/setup_all.py` (когда схема задана).
- Сгенерировать keywords JSON для всех slug.
- Проходить категории по одной сессии: читать `SEO_MASTER.md` + JSON → писать RU+meta → `quality_runner.py` → фиксировать PASS.
- Tier A — блоком: сначала URLs/competitors, затем контент.
- Если нужен параллельный batch, выбрать один SSOT (prompts **или** skills) и сделать их RU‑only.

---

## 5. Критические расхождения факт ↔ целевой RU‑only

- Документация (README, CLAUDE, categories/README) требует RU+UK, что противоречит `TZ_FINAL.md`.
- Skills/prompts/meta/package содержат UK‑выход и чек‑листы для UK.
- Task‑schema не утверждена, скрипты под неё не обновлены.
- Cleanup из `TZ_FINAL.md` не выполнен (архивы и дубликаты лежат в репо).
- Нет явного списка 8 новых L3 категорий и их tier.

---

## 6. Что делать дальше (ссылка на основной ТЗ)

Операционные шаги, порядок и критерии даны в `TZ_FINAL.md` v4.0.  
Этот файл хранится как архивное видение и фиксирует расхождения, которые нужно закрыть перед RU‑only релизом.
