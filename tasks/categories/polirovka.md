# Checklist: polirovka

**Type:** L1 (Hub)
**Primary Keyword:** набор для полировки авто (480)
**Total Volume:** 1160

---

## Stages

### 01-Init
- [x] Создать папку категории
- [x] Создать `data/polirovka_clean.json`
- [x] Добавить ключевые слова из CSV

### 02-Meta
- [ ] Запустить `/generate-meta polirovka`
- [ ] Создать `meta/polirovka_meta.json`
- [ ] Валидация: `python3 scripts/validate_meta.py`

### 03-Research
- [ ] Запустить `/seo-research polirovka`
- [ ] Создать `research/RESEARCH_DATA.md`
- [ ] Проверить 8 обязательных блоков

### 04-Content
- [ ] Запустить `/content-generator polirovka`
- [ ] Создать `content/polirovka_ru.md`
- [ ] Валидация: `python3 scripts/validate_content.py`

### 05-UK
- [ ] Запустить `/uk-content-init polirovka`
- [ ] Создать UK версию
- [ ] Перевод и адаптация

### 06-Quality
- [ ] Запустить `/quality-gate polirovka`
- [ ] RU версия: PASS
- [ ] UK версия: PASS

### 07-Deploy
- [ ] Запустить `/deploy-to-opencart polirovka`
- [ ] Проверить на сайте

---

## L2 Subcategories
- polirovalnye-mashinki
- polirovalnye-pasty
- polirovalnye-krugi
- glina-i-avtoskraby

---

**Status:** Init ✅ | Meta ⬜ | Research ⬜ | Content ⬜ | UK ⬜ | Quality ⬜ | Deploy ⬜
