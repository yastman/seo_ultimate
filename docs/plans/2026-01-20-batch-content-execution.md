# Batch Content Generation — Implementation Plan

> **For Claude:** REQUIRED SUB-SKILL: Use superpowers:executing-plans to implement this plan task-by-task.

**Goal:** Generate SEO content (buyer guide) for 20 categories via parallel subagents with automatic validation.

**Architecture:** 4 waves of parallel subagents (6/6/6/2). Each subagent reads data files, generates buyer guide content following content-generator skill, validates via Python scripts, fixes issues, and saves. Orchestrator collects results after each wave.

**Tech Stack:** Task tool with `content-generator` subagent, Python validation scripts (`validate_content.py`, `check_keyword_density.py`, `check_water_natasha.py`)

---

## Category Mapping (20 total)

| Slug | Path | Type |
|------|------|------|
| neytralizatory-zapakha | `categories/ukhod-za-intererom/neytralizatory-zapakha` | Product |
| nabory | `categories/aksessuary/nabory` | Product |
| akkumulyatornaya | `categories/polirovka/polirovalnye-mashinki/akkumulyatornaya` | Product |
| voski | `categories/zashchitnye-pokrytiya/voski` | Product |
| zhidkiy-vosk | `categories/zashchitnye-pokrytiya/voski/zhidkiy-vosk` | Product |
| tverdyy-vosk | `categories/zashchitnye-pokrytiya/voski/tverdyy-vosk` | Product |
| zashchitnye-pokrytiya | `categories/zashchitnye-pokrytiya` | **Hub** |
| polirol-dlya-stekla | `categories/moyka-i-eksterer/sredstva-dlya-stekol/polirol-dlya-stekla` | Product |
| vedra-i-emkosti | `categories/aksessuary/vedra-i-emkosti` | Product |
| opt-i-b2b | `categories/opt-i-b2b` | **Hub** |
| mekhovye | `categories/polirovka/polirovalnye-krugi/mekhovye` | Product |
| keramika-dlya-diskov | `categories/moyka-i-eksterer/sredstva-dlya-diskov-i-shin/keramika-dlya-diskov` | Product |
| kvik-deteylery | `categories/zashchitnye-pokrytiya/kvik-deteylery` | Product |
| ukhod-za-naruzhnym-plastikom | `categories/moyka-i-eksterer/ochistiteli-kuzova/ukhod-za-naruzhnym-plastikom` | Product |
| kisti-dlya-deteylinga | `categories/aksessuary/shchetki-i-kisti/kisti-dlya-deteylinga` | Product |
| shchetka-dlya-moyki-avto | `categories/aksessuary/shchetki-i-kisti/shchetka-dlya-moyki-avto` | Product |
| poliroli-dlya-plastika | `categories/ukhod-za-intererom/poliroli-dlya-plastika` | Product |
| ukhod-za-kozhey | `categories/ukhod-za-intererom/sredstva-dlya-kozhi/ukhod-za-kozhey` | Product |
| ukhod-za-intererom | `categories/ukhod-za-intererom` | **Hub** |
| silanty | `categories/zashchitnye-pokrytiya/silanty` | Product |

---

## Task 0: Pre-flight Verification

**Goal:** Confirm all 20 categories have required input files before spawning subagents.

**Files:**
- Check: `categories/**/data/*_clean.json` (20 files)
- Check: `categories/**/meta/*_meta.json` (20 files)
- Check: `categories/**/research/RESEARCH_DATA.md` (20 files)

**Step 1: Run verification script**

```bash
cd /mnt/c/Users/user/Documents/Сайты/Ultimate.net.ua/сео_для_категорий_ультимейт

MISSING=0
for slug in neytralizatory-zapakha nabory akkumulyatornaya voski zhidkiy-vosk tverdyy-vosk zashchitnye-pokrytiya polirol-dlya-stekla vedra-i-emkosti opt-i-b2b mekhovye keramika-dlya-diskov kvik-deteylery ukhod-za-naruzhnym-plastikom kisti-dlya-deteylinga shchetka-dlya-moyki-avto poliroli-dlya-plastika ukhod-za-kozhey ukhod-za-intererom silanty; do
  clean=$(ls categories/**/$slug/data/${slug}_clean.json 2>/dev/null)
  meta=$(ls categories/**/$slug/meta/${slug}_meta.json 2>/dev/null)
  research=$(ls categories/**/$slug/research/RESEARCH_DATA.md 2>/dev/null)

  if [ -z "$clean" ] || [ -z "$meta" ] || [ -z "$research" ]; then
    echo "MISSING: $slug"
    MISSING=$((MISSING+1))
  else
    echo "OK: $slug"
  fi
done
echo "---"
echo "Missing: $MISSING / 20"
```

**Expected:** `Missing: 0 / 20`

**Step 2: Verify validation scripts work**

```bash
python3 scripts/validate_content.py --help
python3 scripts/check_keyword_density.py --help
python3 scripts/check_water_natasha.py --help
```

**Expected:** Help output for all three scripts (no import errors)

---

## Task 1: Wave 1 — Generate Content (6 categories)

**Categories:** neytralizatory-zapakha, nabory, akkumulyatornaya, voski, zhidkiy-vosk, tverdyy-vosk

**Step 1: Spawn 6 parallel subagents**

Use Task tool with `subagent_type: content-generator` for each:

```
Subagent 1 prompt:
---
Сгенерируй SEO-контент для категории neytralizatory-zapakha.

Путь: categories/ukhod-za-intererom/neytralizatory-zapakha

1. Читай:
   - data/neytralizatory-zapakha_clean.json
   - meta/neytralizatory-zapakha_meta.json
   - research/RESEARCH_DATA.md

2. Определи тип: проверь parent_id в _clean.json
   - Если null → Hub Page
   - Иначе → Product Page (buyer guide)

3. Напиши контент по формату buyer guide:
   - H1 из _meta.json (без "Купить")
   - Intro 30-60 слов с primary keyword
   - Таблица сравнения типов
   - Сценарии: "Если X → Y"
   - FAQ 3-5 вопросов

4. Создай папку content если нет:
   mkdir -p categories/ukhod-za-intererom/neytralizatory-zapakha/content

5. Сохрани в:
   categories/ukhod-za-intererom/neytralizatory-zapakha/content/neytralizatory-zapakha_ru.md

6. Валидируй:
   python3 scripts/validate_content.py categories/ukhod-za-intererom/neytralizatory-zapakha/content/neytralizatory-zapakha_ru.md "нейтрализаторы запаха" --mode seo
   python3 scripts/check_keyword_density.py categories/ukhod-za-intererom/neytralizatory-zapakha/content/neytralizatory-zapakha_ru.md

7. Если FAIL — исправь и повтори (до 3 попыток)

8. Верни статус: PASS/WARN/FAIL + размер файла
---
```

**Repeat for all 6 categories with correct paths:**

| Slug | Path |
|------|------|
| neytralizatory-zapakha | `categories/ukhod-za-intererom/neytralizatory-zapakha` |
| nabory | `categories/aksessuary/nabory` |
| akkumulyatornaya | `categories/polirovka/polirovalnye-mashinki/akkumulyatornaya` |
| voski | `categories/zashchitnye-pokrytiya/voski` |
| zhidkiy-vosk | `categories/zashchitnye-pokrytiya/voski/zhidkiy-vosk` |
| tverdyy-vosk | `categories/zashchitnye-pokrytiya/voski/tverdyy-vosk` |

**Step 2: Wait for all 6 subagents to complete**

**Expected:** 6 reports with PASS or WARN status

---

## Task 2: Verify Wave 1 Results

**Step 1: Check all 6 files exist and have content**

```bash
cd /mnt/c/Users/user/Documents/Сайты/Ultimate.net.ua/сео_для_категорий_ультимейт

for slug in neytralizatory-zapakha nabory akkumulyatornaya voski zhidkiy-vosk tverdyy-vosk; do
  content=$(ls categories/**/$slug/content/${slug}_ru.md 2>/dev/null)
  if [ -n "$content" ]; then
    size=$(wc -c < "$content")
    echo "$slug: $size bytes"
    [ "$size" -lt 4000 ] && echo "  ⚠️ TOO SMALL"
  else
    echo "$slug: ❌ MISSING"
  fi
done
```

**Expected:** All 6 files exist, each ≥4000 bytes

**Step 2: Run batch validation**

```bash
for slug in neytralizatory-zapakha nabory akkumulyatornaya voski zhidkiy-vosk tverdyy-vosk; do
  echo "=== $slug ==="
  content=$(ls categories/**/$slug/content/${slug}_ru.md 2>/dev/null)
  [ -n "$content" ] && python3 scripts/validate_content.py "$content" --mode seo 2>&1 | tail -5
done
```

**Expected:** All PASS or WARN (no FAIL)

**Step 3: Handle failures (if any)**

If any category has FAIL:
1. Read the error message
2. Fix the specific issue (usually keyword density or missing H2)
3. Re-run validation

---

## Task 3: Wave 2 — Generate Content (6 categories)

**Categories:** zashchitnye-pokrytiya (Hub), polirol-dlya-stekla, vedra-i-emkosti, opt-i-b2b (Hub), mekhovye, keramika-dlya-diskov

**Step 1: Spawn 6 parallel subagents**

Same prompt template as Wave 1, with correct paths:

| Slug | Path | Note |
|------|------|------|
| zashchitnye-pokrytiya | `categories/zashchitnye-pokrytiya` | **Hub Page** |
| polirol-dlya-stekla | `categories/moyka-i-eksterer/sredstva-dlya-stekol/polirol-dlya-stekla` | |
| vedra-i-emkosti | `categories/aksessuary/vedra-i-emkosti` | |
| opt-i-b2b | `categories/opt-i-b2b` | **Hub Page** |
| mekhovye | `categories/polirovka/polirovalnye-krugi/mekhovye` | |
| keramika-dlya-diskov | `categories/moyka-i-eksterer/sredstva-dlya-diskov-i-shin/keramika-dlya-diskov` | |

**For Hub Pages (zashchitnye-pokrytiya, opt-i-b2b):** Add to prompt:
```
ВАЖНО: Это Hub Page (parent_id = null).
- H2 по процессам, НЕ по типам товаров
- Без детальных гайдов (каннибализация L2)
- 2000-2500 знаков
- FAQ про экосистему категории
```

**Step 2: Wait for completion and verify (same as Task 2)**

---

## Task 4: Verify Wave 2 Results

**Step 1: Check files**

```bash
for slug in zashchitnye-pokrytiya polirol-dlya-stekla vedra-i-emkosti opt-i-b2b mekhovye keramika-dlya-diskov; do
  content=$(ls categories/**/$slug/content/${slug}_ru.md 2>/dev/null)
  if [ -n "$content" ]; then
    size=$(wc -c < "$content")
    echo "$slug: $size bytes"
  else
    echo "$slug: ❌ MISSING"
  fi
done
```

**Step 2: Validate and fix failures**

Same process as Task 2.

---

## Task 5: Wave 3 — Generate Content (6 categories)

**Categories:** kvik-deteylery, ukhod-za-naruzhnym-plastikom, kisti-dlya-deteylinga, shchetka-dlya-moyki-avto, poliroli-dlya-plastika, ukhod-za-kozhey

| Slug | Path |
|------|------|
| kvik-deteylery | `categories/zashchitnye-pokrytiya/kvik-deteylery` |
| ukhod-za-naruzhnym-plastikom | `categories/moyka-i-eksterer/ochistiteli-kuzova/ukhod-za-naruzhnym-plastikom` |
| kisti-dlya-deteylinga | `categories/aksessuary/shchetki-i-kisti/kisti-dlya-deteylinga` |
| shchetka-dlya-moyki-avto | `categories/aksessuary/shchetki-i-kisti/shchetka-dlya-moyki-avto` |
| poliroli-dlya-plastika | `categories/ukhod-za-intererom/poliroli-dlya-plastika` |
| ukhod-za-kozhey | `categories/ukhod-za-intererom/sredstva-dlya-kozhi/ukhod-za-kozhey` |

**Step 1:** Spawn 6 subagents with correct paths
**Step 2:** Wait and verify

---

## Task 6: Verify Wave 3 Results

Same verification process as Task 2/4.

---

## Task 7: Wave 4 — Generate Content (2 categories)

**Categories:** ukhod-za-intererom (Hub), silanty

| Slug | Path | Note |
|------|------|------|
| ukhod-za-intererom | `categories/ukhod-za-intererom` | **Hub Page** |
| silanty | `categories/zashchitnye-pokrytiya/silanty` | |

**Step 1:** Spawn 2 subagents
**Step 2:** Wait and verify

---

## Task 8: Verify Wave 4 Results

Same verification process.

---

## Task 9: Post-flight — Final Verification & Cleanup

**Step 1: Full audit of all 20 categories**

```bash
cd /mnt/c/Users/user/Documents/Сайты/Ultimate.net.ua/сео_для_категорий_ультимейт

echo "=== FINAL AUDIT ==="
PASS=0
FAIL=0

for slug in neytralizatory-zapakha nabory akkumulyatornaya voski zhidkiy-vosk tverdyy-vosk zashchitnye-pokrytiya polirol-dlya-stekla vedra-i-emkosti opt-i-b2b mekhovye keramika-dlya-diskov kvik-deteylery ukhod-za-naruzhnym-plastikom kisti-dlya-deteylinga shchetka-dlya-moyki-avto poliroli-dlya-plastika ukhod-za-kozhey ukhod-za-intererom silanty; do
  content=$(ls categories/**/$slug/content/${slug}_ru.md 2>/dev/null)
  if [ -n "$content" ]; then
    size=$(wc -c < "$content")
    if [ "$size" -ge 4000 ]; then
      echo "✅ $slug: $size bytes"
      PASS=$((PASS+1))
    else
      echo "⚠️ $slug: $size bytes (too small)"
      FAIL=$((FAIL+1))
    fi
  else
    echo "❌ $slug: MISSING"
    FAIL=$((FAIL+1))
  fi
done

echo "---"
echo "PASS: $PASS / 20"
echo "FAIL: $FAIL / 20"
```

**Expected:** `PASS: 20 / 20`, `FAIL: 0 / 20`

**Step 2: Update TODO_CONTENT.md**

Mark all 20 categories as completed:

```bash
# View current status
cat tasks/TODO_CONTENT.md
```

Then edit the file to mark completed categories.

**Step 3: Commit results**

```bash
git add categories/*/content/*_ru.md
git add categories/*/*/content/*_ru.md
git add categories/*/*/*/content/*_ru.md
git add tasks/TODO_CONTENT.md

git commit -m "$(cat <<'EOF'
feat(content): generate SEO content for 20 categories

- 17 Product Pages (buyer guide format)
- 3 Hub Pages (process-focused)
- All validated via validate_content.py

Categories:
- neytralizatory-zapakha, nabory, akkumulyatornaya
- voski, zhidkiy-vosk, tverdyy-vosk
- zashchitnye-pokrytiya, polirol-dlya-stekla
- vedra-i-emkosti, opt-i-b2b, mekhovye
- keramika-dlya-diskov, kvik-deteylery
- ukhod-za-naruzhnym-plastikom, kisti-dlya-deteylinga
- shchetka-dlya-moyki-avto, poliroli-dlya-plastika
- ukhod-za-kozhey, ukhod-za-intererom, silanty

Co-Authored-By: Claude Opus 4.5 <noreply@anthropic.com>
EOF
)"
```

---

## Success Criteria

| Metric | Target |
|--------|--------|
| Categories with content ≥4KB | 20/20 |
| Validation FAIL status | 0 |
| Stem density >3% | 0 |
| Classic nausea >4.0 | 0 |

---

## Next Steps After Completion

1. `/quality-gate {slug}` — for each category before deploy
2. `/uk-content-init {slug}` — Ukrainian version
3. `/deploy-to-opencart {slug}` — push to site

---

**Version:** 1.0
**Created:** 2026-01-20
