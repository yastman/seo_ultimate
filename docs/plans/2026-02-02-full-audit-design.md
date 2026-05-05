# Full Category Audit Design

**Дата:** 2026-02-02
**Задача:** Повний аудит всіх категорій RU + UK через скілли автофіксу

---

## 1. Scope та Цілі

**Масштаб:**
- RU: 50 категорій (вкладена структура)
- UK: 52 категорії (плоска структура)
- **Всього: 102 категорії**

**Цілі:**
1. Знайти всі проблеми: density, nausea, missing keywords, UK terminology
2. Автоматично виправити через `content-reviewer` (RU) та `uk-content-reviewer` (UK)
3. Зібрати логи для аналізу результатів

**Що роблять скілли:**
- Валідують meta, density, nausea, coverage, SEO structure
- Автоматично фіксять BLOCKER issues (density >3%, nausea >4.0, missing keywords)
- Заміняють надлишкові слова синонімами
- Додають непокриті ключі органічно в текст
- Для UK — перевіряють термінологію (резина→гума, мойка→миття)

**Thresholds:**

| Метрика | Target | BLOCKER |
|---------|--------|---------|
| Stem density | ≤2.5% | >3.0% |
| Classic nausea | ≤3.5 | >4.0 |
| Academic nausea | ≥7% | <6% |
| Coverage primary+secondary | 100% | <100% |
| Coverage supporting | ≥80% | <80% |

---

## 2. Worker Distribution

**6 воркерів** — оптимальний баланс швидкості та контролю.

### UK Workers (W1-W4) — по 13 категорій

**W1-UK:**
```
akkumulyatornaya, aksessuary, aksessuary-dlya-naneseniya-sredstv,
aktivnaya-pena, antibitum, antidozhd, antimoshka, apparaty-tornador,
avtoshampuni, cherniteli-shin, glina-i-avtoskraby, gubki-i-varezhki,
keramika-dlya-diskov
```

**W2-UK:**
```
keramika-i-zhidkoe-steklo, kisti-dlya-deteylinga, kvik-deteylery,
malyarniy-skotch, mekhovye, mikrofibra-i-tryapki, moyka-i-eksterer,
nabory, neytralizatory-zapakha, obezzhirivateli, oborudovanie,
ochistiteli-diskov, ochistiteli-dvigatelya
```

**W3-UK:**
```
ochistiteli-kozhi, ochistiteli-kuzova, ochistiteli-shin, ochistiteli-stekol,
omyvatel, opt-i-b2b, polirol-dlya-stekla, poliroli-dlya-plastika,
polirovalnye-mashinki, polirovalnye-pasty, polirovka, pyatnovyvoditeli,
raspyliteli-i-penniki
```

**W4-UK:**
```
shampuni-dlya-ruchnoy-moyki, shchetka-dlya-moyki-avto, silanty,
sredstva-dlya-khimchistki-salona, sredstva-dlya-kozhi, tverdyy-vosk,
ukhod-za-intererom, ukhod-za-kozhey, ukhod-za-naruzhnym-plastikom,
vedra-i-emkosti, voski, zashchitnye-pokrytiya, zhidkiy-vosk
```

### RU Workers (W5-W6) — по 25 категорій

**W5-RU:**
```
aksessuary
aksessuary/aksessuary-dlya-naneseniya-sredstv
aksessuary/gubki-i-varezhki
aksessuary/malyarniy-skotch
aksessuary/mikrofibra-i-tryapki
aksessuary/nabory
aksessuary/raspyliteli-i-penniki
aksessuary/shchetki-i-kisti/kisti-dlya-deteylinga
aksessuary/shchetki-i-kisti/shchetka-dlya-moyki-avto
aksessuary/vedra-i-emkosti
moyka-i-eksterer
moyka-i-eksterer/avtoshampuni
moyka-i-eksterer/avtoshampuni/aktivnaya-pena
moyka-i-eksterer/avtoshampuni/shampuni-dlya-ruchnoy-moyki
moyka-i-eksterer/ochistiteli-dvigatelya
moyka-i-eksterer/ochistiteli-kuzova/antibitum
moyka-i-eksterer/ochistiteli-kuzova/antimoshka
moyka-i-eksterer/ochistiteli-kuzova/glina-i-avtoskraby
moyka-i-eksterer/ochistiteli-kuzova/obezzhirivateli
moyka-i-eksterer/ochistiteli-kuzova/ukhod-za-naruzhnym-plastikom
moyka-i-eksterer/sredstva-dlya-diskov-i-shin/cherniteli-shin
moyka-i-eksterer/sredstva-dlya-diskov-i-shin/keramika-dlya-diskov
moyka-i-eksterer/sredstva-dlya-diskov-i-shin/ochistiteli-diskov
moyka-i-eksterer/sredstva-dlya-diskov-i-shin/ochistiteli-shin
moyka-i-eksterer/sredstva-dlya-stekol/antidozhd
```

**W6-RU:**
```
moyka-i-eksterer/sredstva-dlya-stekol/ochistiteli-stekol
moyka-i-eksterer/sredstva-dlya-stekol/omyvatel
moyka-i-eksterer/sredstva-dlya-stekol/polirol-dlya-stekla
oborudovanie
oborudovanie/apparaty-tornador
opt-i-b2b
polirovka
polirovka/polirovalnye-krugi/mekhovye
polirovka/polirovalnye-mashinki/akkumulyatornaya
polirovka/polirovalnye-pasty
ukhod-za-intererom
ukhod-za-intererom/neytralizatory-zapakha
ukhod-za-intererom/poliroli-dlya-plastika
ukhod-za-intererom/pyatnovyvoditeli
ukhod-za-intererom/sredstva-dlya-khimchistki-salona
ukhod-za-intererom/sredstva-dlya-kozhi
ukhod-za-intererom/sredstva-dlya-kozhi/ochistiteli-kozhi
ukhod-za-intererom/sredstva-dlya-kozhi/ukhod-za-kozhey
zashchitnye-pokrytiya
zashchitnye-pokrytiya/keramika-i-zhidkoe-steklo
zashchitnye-pokrytiya/kvik-deteylery
zashchitnye-pokrytiya/silanty
zashchitnye-pokrytiya/voski
zashchitnye-pokrytiya/voski/tverdyy-vosk
zashchitnye-pokrytiya/voski/zhidkiy-vosk
```

---

## 3. Worker Prompts

### UK Worker Template (W1-W4)

```
W{N}: UK Content Audit — категорії {first}...{last}.

Для КОЖНОЇ категорії зі списку виконай скілл:

uk-content-reviewer {slug}

Після кожної категорії логуй результат в /home/user/projects/llm-keywords-pipeline/data/generated/audit-logs/W{N}_uk_audit.md:

## {slug}
**Verdict:** PASS / WARNING / FIXED
**Density:** X% (was Y%)
**Nausea:** X (was Y)
**Coverage:** X/Y (Z%)
**Issues:** ...
**Fixes:** ...

КАТЕГОРІЇ:
{list}

Після останньої категорії додай:
[COMPLETE] 2026-02-02 HH:MM

НЕ ДЕЛАЙ git commit.
```

### RU Worker Template (W5-W6)

```
W{N}: RU Content Audit — категорії {first}...{last}.

Для КОЖНОЇ категорії зі списку виконай скілл:

content-reviewer {path}

Після кожної категорії логуй результат в /home/user/projects/llm-keywords-pipeline/data/generated/audit-logs/W{N}_ru_audit.md:

## {slug}
**Verdict:** PASS / WARNING / FIXED
**Density:** X% (was Y%)
**Nausea:** X (was Y)
**Coverage:** X/Y (Z%)
**Issues:** ...
**Fixes:** ...

КАТЕГОРІЇ:
{list}

Після останньої категорії додай:
[COMPLETE] 2026-02-02 HH:MM

НЕ ДЕЛАЙ git commit.
```

---

## 4. Execution Steps

### Step 1: Prepare Environment

```bash
# Verify tmux
echo $TMUX

# Create logs directory
mkdir -p /home/user/projects/llm-keywords-pipeline/data/generated/audit-logs

# Clean old logs (optional)
rm -f /home/user/projects/llm-keywords-pipeline/data/generated/audit-logs/W*_audit.md
```

### Step 2: Create tmux Windows

```bash
tmux new-window -n "W1-UK"
tmux new-window -n "W2-UK"
tmux new-window -n "W3-UK"
tmux new-window -n "W4-UK"
tmux new-window -n "W5-RU"
tmux new-window -n "W6-RU"
```

### Step 3: Spawn Workers

Для кожного вікна виконати `tmux send-keys` з відповідним промптом.

### Step 4: Monitor Progress

```bash
# Watch all logs
tail -f /home/user/projects/llm-keywords-pipeline/data/generated/audit-logs/W*_audit.md

# Check completion
grep -l "\[COMPLETE\]" /home/user/projects/llm-keywords-pipeline/data/generated/audit-logs/*.md

# Count processed categories
grep -c "^## " /home/user/projects/llm-keywords-pipeline/data/generated/audit-logs/*.md
```

### Step 5: After All Complete

```bash
# Review all changes
git status
git diff --stat

# Run coverage audit to verify
python3 scripts/audit_coverage.py --lang uk > reports/post_audit_uk.txt
python3 scripts/audit_coverage.py --lang ru > reports/post_audit_ru.txt

# Commit all fixes
git add -A
git commit -m "audit: full category review RU+UK via content-reviewer skills

- Reviewed 50 RU + 52 UK categories
- Auto-fixed density/nausea issues
- Added missing keywords
- Fixed UK terminology

Co-Authored-By: Claude Opus 4.5 <noreply@anthropic.com>"
```

---

## 5. Expected Output

### Log Files

```
data/generated/audit-logs/
├── W1_uk_audit.md   # 13 UK categories
├── W2_uk_audit.md   # 13 UK categories
├── W3_uk_audit.md   # 13 UK categories
├── W4_uk_audit.md   # 13 UK categories
├── W5_ru_audit.md   # 25 RU categories
└── W6_ru_audit.md   # 25 RU categories
```

### Log Entry Format

```markdown
## aktivnaya-pena
**Verdict:** FIXED
**Density:** 2.1% (was 3.2%)
**Nausea:** 3.2 (was 4.1)
**Coverage:** 11/11 (100%)
**Issues:** density 3.2%, nausea 4.1, missing "активна піна для авто"
**Fixes:**
- Replaced "піна" x5 with synonyms (засіб, склад, продукт)
- Added "активна піна для авто" to intro
```

### Summary Report

Після завершення — зібрати статистику:

| Metric | Before | After |
|--------|--------|-------|
| UK categories <70% coverage | 12 | 0 |
| RU categories <70% coverage | 1 | 0 |
| BLOCKER issues | X | 0 |

---

## 6. Risks & Mitigations

| Risk | Probability | Mitigation |
|------|-------------|------------|
| Worker crashes mid-process | Medium | Log shows last category; restart from there |
| File conflicts between workers | Low | Workers have non-overlapping file sets |
| Skill fails on specific category | Medium | Skill logs error, continues to next |
| Too many changes at once | Low | Review diff before commit |
| Nausea increases after keyword insertion | Medium | Skill has Step 9b re-check |

---

## 7. Success Criteria

- [ ] Всі 102 категорії пройшли аудит
- [ ] Всі BLOCKER issues виправлені
- [ ] Coverage primary+secondary = 100% для всіх
- [ ] Density ≤2.5% для всіх
- [ ] Nausea ≤3.5 для всіх
- [ ] UK terminology clean (0 знайдень резина/мойка/стекло)
- [ ] Логи збережені для всіх воркерів
- [ ] Git commit з усіма змінами

---

## 8. Rollback Plan

Якщо щось пішло не так:

```bash
# Discard all changes
git checkout -- .

# Or restore specific files
git checkout -- uk/categories/aktivnaya-pena/content/aktivnaya-pena_uk.md
```

---

**Status:** READY FOR EXECUTION
**Estimated workers:** 6
**Estimated categories per worker:** 13-25
