# Quality Gate Report: sredstva-dlya-kozhi

**Date:** 2026-01-21
**Status:** PASS

---

## Final Report: sredstva-dlya-kozhi

| Metric | Target | Result | Status |
|--------|--------|--------|--------|
| Meta validation | PASS | PASS | OK |
| Density (max stem) | <2.5% | 2.33% (kozh*) | OK |
| Classic nausea | <=3.5 | 3.00 | OK |
| Water | 40-65% | 63.8% | OK |
| Academic | 7-9.5% | 6.9% | INFO (dry) |
| Content validation | PASS | PASS | OK |

---

## Files Checklist

| File | Status |
|------|--------|
| meta/sredstva-dlya-kozhi_meta.json | OK |
| content/sredstva-dlya-kozhi_ru.md | OK |
| data/sredstva-dlya-kozhi_clean.json | OK |
| research/RESEARCH_DATA.md | OK |
| research/RESEARCH_PROMPT.md | OK |

---

## Keywords Coverage

**Primary keywords:** 4/7 exact matches
- [x] sredstvo dlya kozhi avto
- [x] sredstva dlya kozhi avtomobilya
- [x] himiya dlya kozhi avto
- [x] sredstva dlya kozhi avto
- [ ] sredstvo dlya kozhanogo salona (synonym, optional)
- [ ] sredstva dlya kozhi salona avtomobilya (low volume)
- [ ] sredstvo dlya kozhi salona avtomobilya (low volume)

**Entities:** 7/7 present (partial match)
- [x] ochistitel kozhi
- [x] konditsioner dlya kozhi
- [x] dvukhetapnyy ukhod
- [x] pH-neytralnyi sostav
- [x] Top Coat zashchita
- [x] Nappa kozha
- [x] Dakota kozha

---

## Validators Output

### validate_meta.py
```
TITLE: PASS (37 chars)
DESCRIPTION: PASS (117 chars)
H1: Sredstva dlya kozhi
OVERALL: PASS
```

### check_keyword_density.py
```
Max stem: kozh* = 2.33% (OK)
RESULT: OK
```

### check_water_natasha.py
```
Water: 63.8% (warning for Tier C, acceptable)
Classic nausea: 3.00 (PASS)
Academic: 6.9% (INFO: slightly dry)
```

### validate_content.py
```
Structure: PASS
Primary keyword: PASS
Blacklist: PASS
OVERALL: PASS
```

---

## Decision

**PASS** - Ready for `/deploy-to-opencart ukhod-za-intererom/sredstva-dlya-kozhi`

---

*Generated: 2026-01-21*
