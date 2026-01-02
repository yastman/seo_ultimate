# Checklist: aksessuary

**Type:** L1 (Hub)
**Primary Keyword:** аксессуары для мойки авто (50)
**Total Volume:** 300

---

## Stages

### 01-Init
- [x] Создать папку категории
- [x] Создать `data/aksessuary_clean.json`
- [x] Добавить ключевые слова из CSV

### 02-Meta
- [ ] Запустить `/generate-meta aksessuary`
- [ ] Создать `meta/aksessuary_meta.json`
- [ ] Валидация: `python3 scripts/validate_meta.py`

### 03-Research
- [ ] Запустить `/seo-research aksessuary`
- [ ] Создать `research/RESEARCH_DATA.md`
- [ ] Проверить 8 обязательных блоков

### 04-Content
- [ ] Запустить `/content-generator aksessuary`
- [ ] Создать `content/aksessuary_ru.md`
- [ ] Валидация: `python3 scripts/validate_content.py`

### 05-UK
- [ ] Запустить `/uk-content-init aksessuary`
- [ ] Создать UK версию
- [ ] Перевод и адаптация

### 06-Quality
- [ ] Запустить `/quality-gate aksessuary`
- [ ] RU версия: PASS
- [ ] UK версия: PASS

### 07-Deploy
- [ ] Запустить `/deploy-to-opencart aksessuary`
- [ ] Проверить на сайте

---

## L2 Subcategories
- gubki-i-varezhki
- mikrofibra-i-tryapki
- shchetki-i-kisti
- aksessuary-dlya-naneseniya
- vedra-i-emkosti
- raspyliteli-i-penniki
- apparaty-tornador

---

**Status:** Init ✅ | Meta ⬜ | Research ⬜ | Content ⬜ | UK ⬜ | Quality ⬜ | Deploy ⬜
