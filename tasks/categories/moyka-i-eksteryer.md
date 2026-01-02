# Checklist: moyka-i-eksteryer

**Type:** L1 (Hub)
**Primary Keyword:** химия для мойки авто (590)
**Total Volume:** 1340

---

## Stages

### 01-Init
- [x] Создать папку категории
- [x] Создать `data/moyka-i-eksteryer_clean.json`
- [x] Добавить ключевые слова из CSV

### 02-Meta
- [ ] Запустить `/generate-meta moyka-i-eksteryer`
- [ ] Создать `meta/moyka-i-eksteryer_meta.json`
- [ ] Валидация: `python3 scripts/validate_meta.py`

### 03-Research
- [ ] Запустить `/seo-research moyka-i-eksteryer`
- [ ] Создать `research/RESEARCH_DATA.md`
- [ ] Проверить 8 обязательных блоков

### 04-Content
- [ ] Запустить `/content-generator moyka-i-eksteryer`
- [ ] Создать `content/moyka-i-eksteryer_ru.md`
- [ ] Валидация: `python3 scripts/validate_content.py`

### 05-UK
- [ ] Запустить `/uk-content-init moyka-i-eksteryer`
- [ ] Создать UK версию
- [ ] Перевод и адаптация

### 06-Quality
- [ ] Запустить `/quality-gate moyka-i-eksteryer`
- [ ] RU версия: PASS
- [ ] UK версия: PASS

### 07-Deploy
- [ ] Запустить `/deploy-to-opencart moyka-i-eksteryer`
- [ ] Проверить на сайте

---

## L2 Subcategories
- avtoshampuni
- sredstva-dlya-stekol
- ochistiteli-kuzova
- sredstva-dlya-diskov-i-shin
- ochistiteli-dvigatelya
- obezzhirivateli
- dlya-vneshnego-plastika

---

**Status:** Init ✅ | Meta ⬜ | Research ⬜ | Content ⬜ | UK ⬜ | Quality ⬜ | Deploy ⬜
