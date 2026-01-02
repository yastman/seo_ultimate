# Checklist: zashchitnye-pokrytiya

**Type:** L1 (Hub)
**Primary Keyword:** защитные покрытия для авто (70)
**Total Volume:** 110

---

## Stages

### 01-Init
- [x] Создать папку категории
- [x] Создать `data/zashchitnye-pokrytiya_clean.json`
- [x] Добавить ключевые слова из CSV

### 02-Meta
- [ ] Запустить `/generate-meta zashchitnye-pokrytiya`
- [ ] Создать `meta/zashchitnye-pokrytiya_meta.json`
- [ ] Валидация: `python3 scripts/validate_meta.py`

### 03-Research
- [ ] Запустить `/seo-research zashchitnye-pokrytiya`
- [ ] Создать `research/RESEARCH_DATA.md`
- [ ] Проверить 8 обязательных блоков

### 04-Content
- [ ] Запустить `/content-generator zashchitnye-pokrytiya`
- [ ] Создать `content/zashchitnye-pokrytiya_ru.md`
- [ ] Валидация: `python3 scripts/validate_content.py`

### 05-UK
- [ ] Запустить `/uk-content-init zashchitnye-pokrytiya`
- [ ] Создать UK версию
- [ ] Перевод и адаптация

### 06-Quality
- [ ] Запустить `/quality-gate zashchitnye-pokrytiya`
- [ ] RU версия: PASS
- [ ] UK версия: PASS

### 07-Deploy
- [ ] Запустить `/deploy-to-opencart zashchitnye-pokrytiya`
- [ ] Проверить на сайте

---

## L2 Subcategories
- voski
- keramika-i-zhidkoe-steklo
- kvik-deteylery
- silanty
- oborudovanie

---

**Status:** Init ✅ | Meta ⬜ | Research ⬜ | Content ⬜ | UK ⬜ | Quality ⬜ | Deploy ⬜
