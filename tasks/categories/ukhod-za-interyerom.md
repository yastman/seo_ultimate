# Checklist: ukhod-za-interyerom

**Type:** L1 (Hub)
**Primary Keyword:** для химчистки салона (50)
**Total Volume:** 200

---

## Stages

### 01-Init
- [x] Создать папку категории
- [x] Создать `data/ukhod-za-interyerom_clean.json`
- [x] Добавить ключевые слова из CSV

### 02-Meta
- [ ] Запустить `/generate-meta ukhod-za-interyerom`
- [ ] Создать `meta/ukhod-za-interyerom_meta.json`
- [ ] Валидация: `python3 scripts/validate_meta.py`

### 03-Research
- [ ] Запустить `/seo-research ukhod-za-interyerom`
- [ ] Создать `research/RESEARCH_DATA.md`
- [ ] Проверить 8 обязательных блоков

### 04-Content
- [ ] Запустить `/content-generator ukhod-za-interyerom`
- [ ] Создать `content/ukhod-za-interyerom_ru.md`
- [ ] Валидация: `python3 scripts/validate_content.py`

### 05-UK
- [ ] Запустить `/uk-content-init ukhod-za-interyerom`
- [ ] Создать UK версию
- [ ] Перевод и адаптация

### 06-Quality
- [ ] Запустить `/quality-gate ukhod-za-interyerom`
- [ ] RU версия: PASS
- [ ] UK версия: PASS

### 07-Deploy
- [ ] Запустить `/deploy-to-opencart ukhod-za-interyerom`
- [ ] Проверить на сайте

---

## L2 Subcategories
- dlya-khimchistki-salona
- sredstva-dlya-kozhi
- neytralizatory-zapakha
- poliroli-dlya-plastika

---

**Status:** Init ✅ | Meta ⬜ | Research ⬜ | Content ⬜ | UK ⬜ | Quality ⬜ | Deploy ⬜
