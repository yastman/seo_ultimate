# Checklist: opt

**Type:** B2B Page
**Primary Keyword:** автохимия опт (110)
**Total Volume:** 230

---

## Stages

### 01-Init
- [x] Создать папку категории
- [x] Создать `data/opt_clean.json`
- [x] Добавить ключевые слова из CSV

### 02-Meta
- [ ] Запустить `/generate-meta opt`
- [ ] Создать `meta/opt_meta.json`
- [ ] Валидация: `python3 scripts/validate_meta.py`

### 03-Research
- [ ] Запустить `/seo-research opt`
- [ ] Создать `research/RESEARCH_DATA.md`
- [ ] Проверить 8 обязательных блоков

### 04-Content
- [ ] Запустить `/content-generator opt`
- [ ] Создать `content/opt_ru.md`
- [ ] Валидация: `python3 scripts/validate_content.py`

### 05-UK
- [ ] Запустить `/uk-content-init opt`
- [ ] Создать UK версию
- [ ] Перевод и адаптация

### 06-Quality
- [ ] Запустить `/quality-gate opt`
- [ ] RU версия: PASS
- [ ] UK версия: PASS

### 07-Deploy
- [ ] Запустить `/deploy-to-opencart opt`
- [ ] Проверить на сайте

---

## B2B Content Focus
- Условия сотрудничества для дилеров
- Оптовые цены и скидки
- Минимальный заказ
- Доставка для B2B клиентов
- Работа с автомойками и детейлинг-студиями

---

**Status:** Init ✅ | Meta ⬜ | Research ⬜ | Content ⬜ | UK ⬜ | Quality ⬜ | Deploy ⬜
