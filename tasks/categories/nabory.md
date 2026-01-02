# Checklist: nabory

**Type:** L1 (Hub)
**Primary Keyword:** наборы для авто (390)
**Total Volume:** 1150

---

## Stages

### 01-Init
- [x] Создать папку категории
- [x] Создать `data/nabory_clean.json`
- [x] Добавить ключевые слова из CSV

### 02-Meta
- [ ] Запустить `/generate-meta nabory`
- [ ] Создать `meta/nabory_meta.json`
- [ ] Валидация: `python3 scripts/validate_meta.py`

### 03-Research
- [ ] Запустить `/seo-research nabory`
- [ ] Создать `research/RESEARCH_DATA.md`
- [ ] Проверить 8 обязательных блоков

### 04-Content
- [ ] Запустить `/content-generator nabory`
- [ ] Создать `content/nabory_ru.md`
- [ ] Валидация: `python3 scripts/validate_content.py`

### 05-UK
- [ ] Запустить `/uk-content-init nabory`
- [ ] Создать UK версию
- [ ] Перевод и адаптация

### 06-Quality
- [ ] Запустить `/quality-gate nabory`
- [ ] RU версия: PASS
- [ ] UK версия: PASS

### 07-Deploy
- [ ] Запустить `/deploy-to-opencart nabory`
- [ ] Проверить на сайте

---

## L3 Subcategories (via nabory-dlya-deteylinga L2)
- nabory-dlya-moyki
- nabory-dlya-polirovki
- nabory-dlya-kozhi
- nabory-dlya-khimchistki
- podarochnye-nabory

---

**Status:** Init ✅ | Meta ⬜ | Research ⬜ | Content ⬜ | UK ⬜ | Quality ⬜ | Deploy ⬜
