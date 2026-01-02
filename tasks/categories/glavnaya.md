# Checklist: glavnaya

**Type:** Homepage
**Primary Keywords:** автокосметика (480), автохимия (470)
**Total Volume:** 2950

---

## Stages

### 01-Init
- [x] Создать папку категории
- [x] Создать `data/glavnaya_clean.json`
- [x] Добавить ключевые слова из CSV

### 02-Meta
- [ ] Запустить `/generate-meta glavnaya`
- [ ] Создать `meta/glavnaya_meta.json`
- [ ] Валидация: `python3 scripts/validate_meta.py`

### 03-Research
- [ ] Запустить `/seo-research glavnaya`
- [ ] Создать `research/RESEARCH_DATA.md`
- [ ] Проверить 8 обязательных блоков

### 04-Content
- [ ] Запустить `/content-generator glavnaya`
- [ ] Создать `content/glavnaya_ru.md`
- [ ] Валидация: `python3 scripts/validate_content.py`

### 05-UK
- [ ] Запустить `/uk-content-init glavnaya`
- [ ] Создать UK версию
- [ ] Перевод и адаптация

### 06-Quality
- [ ] Запустить `/quality-gate glavnaya`
- [ ] RU версия: PASS
- [ ] UK версия: PASS

### 07-Deploy
- [ ] Запустить `/deploy-to-opencart glavnaya`
- [ ] Проверить на сайте

---

## L1 Sections (links from homepage)
- moyka-i-eksteryer
- aksessuary
- polirovka
- ukhod-za-interyerom
- zashchitnye-pokrytiya

---

**Status:** Init ✅ | Meta ⬜ | Research ⬜ | Content ⬜ | UK ⬜ | Quality ⬜ | Deploy ⬜
