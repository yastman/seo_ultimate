# Stage 06: Quality Gate

**Skill:** `/quality-gate {slug}`
**Progress:** 13/51 RU | 13/51 UK

---

## Checklist per Category

### Pre-flight

- [ ] Все предыдущие этапы (01-05) завершены
- [ ] RU и UK версии существуют

### Quality Checks — Полный Аудит

#### 1. Data Files Check

```bash
# RU
python3 -c "
import json
data = json.load(open('categories/{slug}/data/{slug}_clean.json'))
required = ['slug', 'language', 'keywords', 'stats', 'usage_rules']
missing = [f for f in required if f not in data]
print('DATA RU: PASS' if not missing else f'DATA RU: FAIL - {missing}')
"

# UK
python3 -c "
import json
data = json.load(open('uk/categories/{slug}/data/{slug}_clean.json'))
print('DATA UK: PASS' if 'keywords' in data else 'DATA UK: FAIL')
"
```

#### 2. Meta Tags Check

```bash
# RU
python3 scripts/validate_meta.py categories/{slug}/meta/{slug}_meta.json

# UK
python3 scripts/validate_meta.py uk/categories/{slug}/meta/{slug}_meta.json
```

**Критерии:**

- [ ] title RU: 50-60 chars, содержит keyword
- [ ] title UK: 50-60 chars, содержит keyword
- [ ] description RU: 150-160 chars
- [ ] description UK: 150-160 chars
- [ ] h1 RU: без commercial слов
- [ ] h1 UK: без commercial слов

#### 3. Content Check

```bash
# RU
python3 scripts/validate_content.py \
  categories/{slug}/content/{slug}_ru.md \
  "{primary_keyword}" \
  --mode seo

# UK
python3 scripts/validate_content.py \
  uk/categories/{slug}/content/{slug}_uk.md \
  "{primary_keyword_uk}" \
  --mode seo --lang uk
```

**Критерии:**

- [ ] Word count: 1500-2500
- [ ] Keyword density: 1.5-2.5%
- [ ] H2 count: >= 4
- [ ] FAQ count: >= 5
- [ ] Table exists: yes
- [ ] No commercial keywords in text

#### 4. Research Check

```bash
# Count blocks
grep -c "^## Block" categories/{slug}/research/RESEARCH_DATA.md
# Must be >= 8

# Check status
grep "Status:" categories/{slug}/research/RESEARCH_DATA.md
# Must be "COMPLETED"
```

**Критерии:**

- [ ] 8 блоков заполнены
- [ ] Status: COMPLETED

#### 5. Cross-Check RU ↔ UK

- [ ] Структура контента идентична
- [ ] Все H2 переведены
- [ ] FAQ количество совпадает
- [ ] Таблицы совпадают по структуре

#### 6. SEO Compliance

- [ ] Primary keyword в H1
- [ ] Primary keyword в первом абзаце
- [ ] Alt-теги для изображений (если есть)
- [ ] Внутренние ссылки присутствуют

### Generate Quality Report

```bash
# Создать отчёт
cat > categories/{slug}/QUALITY_REPORT.md << 'EOF'
# Quality Report: {slug}

**Date:** $(date +%Y-%m-%d)
**Status:** PASS/FAIL

## Checks

| Check | RU | UK |
|-------|----|----|
| Data JSON | ✅ | ✅ |
| Meta Tags | ✅ | ✅ |
| Content | ✅ | ✅ |
| Research | ✅ | — |
| SEO | ✅ | ✅ |

## Issues Found
- None / List issues

## Ready for Deploy: YES/NO
EOF
```

### Acceptance Criteria

- [ ] Все 6 проверок пройдены
- [ ] QUALITY_REPORT.md создан
- [ ] Status: PASS
- [ ] Ready for Deploy: YES

### Post-action

- [ ] Переместить из `pending/` в `completed/`
- [ ] Обновить счётчик в `PIPELINE_STATUS.md`
- [ ] Категория готова к Stage 07 (Deploy)

---

## Pending (38)

*Ожидают завершения Stage 04 и 05*

---

## Completed (13)

aktivnaya-pena, dlya-ruchnoy-moyki, ochistiteli-stekol, glina-i-avtoskraby, antimoshka, antibitum, cherniteli-shin, ochistiteli-diskov, ochistiteli-shin, dlya-khimchistki-salona, ochistiteli-dvigatelya, keramika-i-zhidkoe-steklo, gubki-i-varezhki

---

## Quality Report Template

```markdown
# Quality Report: {slug}

**Date:** 2025-XX-XX
**Auditor:** Claude Code
**Status:** PASS

---

## Summary

| Metric | RU | UK |
|--------|----|----|
| Data Valid | ✅ | ✅ |
| Meta Valid | ✅ | ✅ |
| Content Valid | ✅ | ✅ |
| Research Complete | ✅ | — |
| SEO Compliant | ✅ | ✅ |

---

## Detailed Results

### Data
- RU: slug, keywords, stats, usage_rules ✅
- UK: slug, keywords ✅

### Meta
- RU title: 58 chars ✅
- UK title: 56 chars ✅
- RU description: 155 chars ✅
- UK description: 152 chars ✅

### Content
- RU word count: 1823 ✅
- UK word count: 1756 ✅
- RU keyword density: 2.1% ✅
- UK keyword density: 1.9% ✅

### SEO
- H1 contains keyword: ✅
- First paragraph keyword: ✅
- Internal links: 3 ✅

---

## Issues
None

---

## Conclusion
**Ready for Deploy: YES**
```

---

## Common Issues

| Issue | Impact | Fix |
|-------|--------|-----|
| Meta > 60 chars | SEO | Shorten title |
| Density > 2.5% | SEO | Remove keyword repeats |
| Missing FAQ | UX | Add 5+ questions |
| No table | Content | Add comparison |
| RU/UK mismatch | QA | Align structures |
