# Full Category Audit Implementation Plan

> **For Claude:** REQUIRED SUB-SKILL: Use superpowers:executing-plans to implement this plan task-by-task.

**Goal:** Провести повний аудит 102 категорій (50 RU + 52 UK) через скілли автофіксу з паралельними воркерами.

**Architecture:** 6 tmux воркерів (W1-W4 для UK, W5-W6 для RU), кожен викликає відповідний content-reviewer скілл для своїх категорій. Воркери пишуть логи в `data/generated/audit-logs/`. Оркестратор моніторить прогрес та робить фінальний коміт.

**Tech Stack:** tmux, claude CLI, content-reviewer skill, uk-content-reviewer skill, audit_coverage.py

---

## Task 1: Prepare Environment

**Files:**
- Create: `data/generated/audit-logs/` (directory)

**Step 1: Verify tmux session**

```bash
echo $TMUX
```

Expected: Non-empty output (e.g., `/tmp/tmux-1000/default,12345,0`)

**Step 2: Create logs directory**

```bash
mkdir -p /home/user/projects/llm-keywords-pipeline/data/generated/audit-logs
```

Expected: Directory created

**Step 3: Clean old audit logs**

```bash
rm -f /home/user/projects/llm-keywords-pipeline/data/generated/audit-logs/W*_audit.md
```

Expected: Old logs removed

**Step 4: Verify clean state**

```bash
ls -la /home/user/projects/llm-keywords-pipeline/data/generated/audit-logs/
```

Expected: Empty directory (only . and ..)

---

## Task 2: Create tmux Windows

**Step 1: Create W1-UK window**

```bash
tmux new-window -n "W1-UK" -c /home/user/projects/llm-keywords-pipeline
```

**Step 2: Create W2-UK window**

```bash
tmux new-window -n "W2-UK" -c /home/user/projects/llm-keywords-pipeline
```

**Step 3: Create W3-UK window**

```bash
tmux new-window -n "W3-UK" -c /home/user/projects/llm-keywords-pipeline
```

**Step 4: Create W4-UK window**

```bash
tmux new-window -n "W4-UK" -c /home/user/projects/llm-keywords-pipeline
```

**Step 5: Create W5-RU window**

```bash
tmux new-window -n "W5-RU" -c /home/user/projects/llm-keywords-pipeline
```

**Step 6: Create W6-RU window**

```bash
tmux new-window -n "W6-RU" -c /home/user/projects/llm-keywords-pipeline
```

**Step 7: Verify windows created**

```bash
tmux list-windows
```

Expected: 6 windows with names W1-UK, W2-UK, W3-UK, W4-UK, W5-RU, W6-RU

---

## Task 3: Spawn W1-UK Worker

**Step 1: Send claude command to W1-UK**

```bash
tmux send-keys -t "W1-UK" "claude --dangerously-skip-permissions 'W1: UK Content Audit — категорії akkumulyatornaya...keramika-dlya-diskov.

Для КОЖНОЇ категорії зі списку виконай скілл:
uk-content-reviewer {slug}

Після кожної категорії ОБОВЯЗКОВО логуй результат в /home/user/projects/llm-keywords-pipeline/data/generated/audit-logs/W1_uk_audit.md:

## {slug}
**Verdict:** PASS / WARNING / FIXED
**Density:** X% (was Y%)
**Nausea:** X (was Y)
**Coverage:** X/Y (Z%)
**Issues:** ...
**Fixes:** ...

КАТЕГОРІЇ (13 шт):
1. akkumulyatornaya
2. aksessuary
3. aksessuary-dlya-naneseniya-sredstv
4. aktivnaya-pena
5. antibitum
6. antidozhd
7. antimoshka
8. apparaty-tornador
9. avtoshampuni
10. cherniteli-shin
11. glina-i-avtoskraby
12. gubki-i-varezhki
13. keramika-dlya-diskov

Після останньої категорії додай:
[COMPLETE] timestamp

НЕ ДЕЛАЙ git commit.'" Enter
```

Expected: Claude starts in W1-UK window

---

## Task 4: Spawn W2-UK Worker

**Step 1: Send claude command to W2-UK**

```bash
tmux send-keys -t "W2-UK" "claude --dangerously-skip-permissions 'W2: UK Content Audit — категорії keramika-i-zhidkoe-steklo...ochistiteli-dvigatelya.

Для КОЖНОЇ категорії зі списку виконай скілл:
uk-content-reviewer {slug}

Після кожної категорії ОБОВЯЗКОВО логуй результат в /home/user/projects/llm-keywords-pipeline/data/generated/audit-logs/W2_uk_audit.md:

## {slug}
**Verdict:** PASS / WARNING / FIXED
**Density:** X% (was Y%)
**Nausea:** X (was Y)
**Coverage:** X/Y (Z%)
**Issues:** ...
**Fixes:** ...

КАТЕГОРІЇ (13 шт):
1. keramika-i-zhidkoe-steklo
2. kisti-dlya-deteylinga
3. kvik-deteylery
4. malyarniy-skotch
5. mekhovye
6. mikrofibra-i-tryapki
7. moyka-i-eksterer
8. nabory
9. neytralizatory-zapakha
10. obezzhirivateli
11. oborudovanie
12. ochistiteli-diskov
13. ochistiteli-dvigatelya

Після останньої категорії додай:
[COMPLETE] timestamp

НЕ ДЕЛАЙ git commit.'" Enter
```

Expected: Claude starts in W2-UK window

---

## Task 5: Spawn W3-UK Worker

**Step 1: Send claude command to W3-UK**

```bash
tmux send-keys -t "W3-UK" "claude --dangerously-skip-permissions 'W3: UK Content Audit — категорії ochistiteli-kozhi...raspyliteli-i-penniki.

Для КОЖНОЇ категорії зі списку виконай скілл:
uk-content-reviewer {slug}

Після кожної категорії ОБОВЯЗКОВО логуй результат в /home/user/projects/llm-keywords-pipeline/data/generated/audit-logs/W3_uk_audit.md:

## {slug}
**Verdict:** PASS / WARNING / FIXED
**Density:** X% (was Y%)
**Nausea:** X (was Y)
**Coverage:** X/Y (Z%)
**Issues:** ...
**Fixes:** ...

КАТЕГОРІЇ (13 шт):
1. ochistiteli-kozhi
2. ochistiteli-kuzova
3. ochistiteli-shin
4. ochistiteli-stekol
5. omyvatel
6. opt-i-b2b
7. polirol-dlya-stekla
8. poliroli-dlya-plastika
9. polirovalnye-mashinki
10. polirovalnye-pasty
11. polirovka
12. pyatnovyvoditeli
13. raspyliteli-i-penniki

Після останньої категорії додай:
[COMPLETE] timestamp

НЕ ДЕЛАЙ git commit.'" Enter
```

Expected: Claude starts in W3-UK window

---

## Task 6: Spawn W4-UK Worker

**Step 1: Send claude command to W4-UK**

```bash
tmux send-keys -t "W4-UK" "claude --dangerously-skip-permissions 'W4: UK Content Audit — категорії shampuni-dlya-ruchnoy-moyki...zhidkiy-vosk.

Для КОЖНОЇ категорії зі списку виконай скілл:
uk-content-reviewer {slug}

Після кожної категорії ОБОВЯЗКОВО логуй результат в /home/user/projects/llm-keywords-pipeline/data/generated/audit-logs/W4_uk_audit.md:

## {slug}
**Verdict:** PASS / WARNING / FIXED
**Density:** X% (was Y%)
**Nausea:** X (was Y)
**Coverage:** X/Y (Z%)
**Issues:** ...
**Fixes:** ...

КАТЕГОРІЇ (13 шт):
1. shampuni-dlya-ruchnoy-moyki
2. shchetka-dlya-moyki-avto
3. silanty
4. sredstva-dlya-khimchistki-salona
5. sredstva-dlya-kozhi
6. tverdyy-vosk
7. ukhod-za-intererom
8. ukhod-za-kozhey
9. ukhod-za-naruzhnym-plastikom
10. vedra-i-emkosti
11. voski
12. zashchitnye-pokrytiya
13. zhidkiy-vosk

Після останньої категорії додай:
[COMPLETE] timestamp

НЕ ДЕЛАЙ git commit.'" Enter
```

Expected: Claude starts in W4-UK window

---

## Task 7: Spawn W5-RU Worker

**Step 1: Send claude command to W5-RU**

```bash
tmux send-keys -t "W5-RU" "claude --dangerously-skip-permissions 'W5: RU Content Audit — категорії aksessuary...antidozhd.

Для КОЖНОЇ категорії зі списку виконай скілл:
content-reviewer {path}

Після кожної категорії ОБОВЯЗКОВО логуй результат в /home/user/projects/llm-keywords-pipeline/data/generated/audit-logs/W5_ru_audit.md:

## {slug}
**Verdict:** PASS / WARNING / FIXED
**Density:** X% (was Y%)
**Nausea:** X (was Y)
**Coverage:** X/Y (Z%)
**Issues:** ...
**Fixes:** ...

КАТЕГОРІЇ (25 шт, використовуй ПОВНИЙ path):
1. aksessuary
2. aksessuary/aksessuary-dlya-naneseniya-sredstv
3. aksessuary/gubki-i-varezhki
4. aksessuary/malyarniy-skotch
5. aksessuary/mikrofibra-i-tryapki
6. aksessuary/nabory
7. aksessuary/raspyliteli-i-penniki
8. aksessuary/shchetki-i-kisti/kisti-dlya-deteylinga
9. aksessuary/shchetki-i-kisti/shchetka-dlya-moyki-avto
10. aksessuary/vedra-i-emkosti
11. moyka-i-eksterer
12. moyka-i-eksterer/avtoshampuni
13. moyka-i-eksterer/avtoshampuni/aktivnaya-pena
14. moyka-i-eksterer/avtoshampuni/shampuni-dlya-ruchnoy-moyki
15. moyka-i-eksterer/ochistiteli-dvigatelya
16. moyka-i-eksterer/ochistiteli-kuzova/antibitum
17. moyka-i-eksterer/ochistiteli-kuzova/antimoshka
18. moyka-i-eksterer/ochistiteli-kuzova/glina-i-avtoskraby
19. moyka-i-eksterer/ochistiteli-kuzova/obezzhirivateli
20. moyka-i-eksterer/ochistiteli-kuzova/ukhod-za-naruzhnym-plastikom
21. moyka-i-eksterer/sredstva-dlya-diskov-i-shin/cherniteli-shin
22. moyka-i-eksterer/sredstva-dlya-diskov-i-shin/keramika-dlya-diskov
23. moyka-i-eksterer/sredstva-dlya-diskov-i-shin/ochistiteli-diskov
24. moyka-i-eksterer/sredstva-dlya-diskov-i-shin/ochistiteli-shin
25. moyka-i-eksterer/sredstva-dlya-stekol/antidozhd

Після останньої категорії додай:
[COMPLETE] timestamp

НЕ ДЕЛАЙ git commit.'" Enter
```

Expected: Claude starts in W5-RU window

---

## Task 8: Spawn W6-RU Worker

**Step 1: Send claude command to W6-RU**

```bash
tmux send-keys -t "W6-RU" "claude --dangerously-skip-permissions 'W6: RU Content Audit — категорії ochistiteli-stekol...zhidkiy-vosk.

Для КОЖНОЇ категорії зі списку виконай скілл:
content-reviewer {path}

Після кожної категорії ОБОВЯЗКОВО логуй результат в /home/user/projects/llm-keywords-pipeline/data/generated/audit-logs/W6_ru_audit.md:

## {slug}
**Verdict:** PASS / WARNING / FIXED
**Density:** X% (was Y%)
**Nausea:** X (was Y)
**Coverage:** X/Y (Z%)
**Issues:** ...
**Fixes:** ...

КАТЕГОРІЇ (25 шт, використовуй ПОВНИЙ path):
1. moyka-i-eksterer/sredstva-dlya-stekol/ochistiteli-stekol
2. moyka-i-eksterer/sredstva-dlya-stekol/omyvatel
3. moyka-i-eksterer/sredstva-dlya-stekol/polirol-dlya-stekla
4. oborudovanie
5. oborudovanie/apparaty-tornador
6. opt-i-b2b
7. polirovka
8. polirovka/polirovalnye-krugi/mekhovye
9. polirovka/polirovalnye-mashinki/akkumulyatornaya
10. polirovka/polirovalnye-pasty
11. ukhod-za-intererom
12. ukhod-za-intererom/neytralizatory-zapakha
13. ukhod-za-intererom/poliroli-dlya-plastika
14. ukhod-za-intererom/pyatnovyvoditeli
15. ukhod-za-intererom/sredstva-dlya-khimchistki-salona
16. ukhod-za-intererom/sredstva-dlya-kozhi
17. ukhod-za-intererom/sredstva-dlya-kozhi/ochistiteli-kozhi
18. ukhod-za-intererom/sredstva-dlya-kozhi/ukhod-za-kozhey
19. zashchitnye-pokrytiya
20. zashchitnye-pokrytiya/keramika-i-zhidkoe-steklo
21. zashchitnye-pokrytiya/kvik-deteylery
22. zashchitnye-pokrytiya/silanty
23. zashchitnye-pokrytiya/voski
24. zashchitnye-pokrytiya/voski/tverdyy-vosk
25. zashchitnye-pokrytiya/voski/zhidkiy-vosk

Після останньої категорії додай:
[COMPLETE] timestamp

НЕ ДЕЛАЙ git commit.'" Enter
```

Expected: Claude starts in W6-RU window

---

## Task 9: Monitor Workers Progress

**Step 1: Watch logs in real-time**

```bash
watch -n 30 'for f in /home/user/projects/llm-keywords-pipeline/data/generated/audit-logs/W*_audit.md; do echo "=== $(basename $f) ==="; grep -c "^## " "$f" 2>/dev/null || echo "0"; done'
```

Expected: Numbers incrementing as categories are processed

**Step 2: Check for completion**

```bash
grep -l "\[COMPLETE\]" /home/user/projects/llm-keywords-pipeline/data/generated/audit-logs/*.md 2>/dev/null | wc -l
```

Expected: 6 when all workers complete

**Step 3: View worker windows (optional)**

```bash
# Switch to specific window
tmux select-window -t "W1-UK"
```

---

## Task 10: Verify Results

**Step 1: Run coverage audit for UK**

```bash
python3 /home/user/projects/llm-keywords-pipeline/scripts/audit_coverage.py --lang uk 2>/dev/null | tee /home/user/projects/llm-keywords-pipeline/reports/post_audit_coverage_uk.txt
```

Expected: All categories show improved coverage

**Step 2: Run coverage audit for RU**

```bash
python3 /home/user/projects/llm-keywords-pipeline/scripts/audit_coverage.py --lang ru 2>/dev/null | tee /home/user/projects/llm-keywords-pipeline/reports/post_audit_coverage_ru.txt
```

Expected: All categories show improved coverage

**Step 3: Check for remaining blockers**

```bash
echo "=== UK <70% ===" && awk -F',' 'NR>1 && $6<70 {print $1, $6"%"}' /home/user/projects/llm-keywords-pipeline/reports/coverage_summary_uk_*.csv | tail -1
echo "=== RU <70% ===" && awk -F',' 'NR>1 && $6<70 {print $1, $6"%"}' /home/user/projects/llm-keywords-pipeline/reports/coverage_summary_ru_*.csv | tail -1
```

Expected: Empty output (no categories below 70%)

---

## Task 11: Review and Commit Changes

**Step 1: Check git status**

```bash
cd /home/user/projects/llm-keywords-pipeline && git status --short | head -50
```

Expected: List of modified content files

**Step 2: Review diff statistics**

```bash
cd /home/user/projects/llm-keywords-pipeline && git diff --stat | tail -20
```

Expected: Changes in content/*.md files

**Step 3: Stage all changes**

```bash
cd /home/user/projects/llm-keywords-pipeline && git add -A
```

**Step 4: Commit with summary**

```bash
cd /home/user/projects/llm-keywords-pipeline && git commit -m "$(cat <<'EOF'
audit: full category review RU+UK via content-reviewer skills

- Reviewed 50 RU + 52 UK categories
- Auto-fixed density/nausea issues
- Added missing keywords organically
- Fixed UK terminology (резина→гума, мойка→миття)

Co-Authored-By: Claude Opus 4.5 <noreply@anthropic.com>
EOF
)"
```

Expected: Commit created successfully

---

## Task 12: Cleanup

**Step 1: Close worker windows**

```bash
tmux kill-window -t "W1-UK" 2>/dev/null
tmux kill-window -t "W2-UK" 2>/dev/null
tmux kill-window -t "W3-UK" 2>/dev/null
tmux kill-window -t "W4-UK" 2>/dev/null
tmux kill-window -t "W5-RU" 2>/dev/null
tmux kill-window -t "W6-RU" 2>/dev/null
```

Expected: All worker windows closed

**Step 2: Generate summary report**

```bash
echo "# Audit Summary $(date +%Y-%m-%d)" > /home/user/projects/llm-keywords-pipeline/data/generated/audit-logs/SUMMARY.md
echo "" >> /home/user/projects/llm-keywords-pipeline/data/generated/audit-logs/SUMMARY.md
echo "## Statistics" >> /home/user/projects/llm-keywords-pipeline/data/generated/audit-logs/SUMMARY.md
echo "" >> /home/user/projects/llm-keywords-pipeline/data/generated/audit-logs/SUMMARY.md
for f in /home/user/projects/llm-keywords-pipeline/data/generated/audit-logs/W*_audit.md; do
  name=$(basename $f .md)
  total=$(grep -c "^## " "$f" 2>/dev/null || echo 0)
  fixed=$(grep -c "FIXED" "$f" 2>/dev/null || echo 0)
  echo "- $name: $total categories, $fixed fixed" >> /home/user/projects/llm-keywords-pipeline/data/generated/audit-logs/SUMMARY.md
done
```

Expected: SUMMARY.md created with statistics

---

## Success Criteria

- [ ] All 6 workers completed ([COMPLETE] in logs)
- [ ] 102 categories audited (50 RU + 52 UK)
- [ ] No categories with coverage <70%
- [ ] No BLOCKER issues remaining
- [ ] Git commit created with all fixes
- [ ] Worker windows closed
- [ ] Summary report generated

---

## Rollback Plan

If something goes wrong:

```bash
# Discard all uncommitted changes
cd /home/user/projects/llm-keywords-pipeline && git checkout -- .

# Or restore specific file
git checkout -- uk/categories/aktivnaya-pena/content/aktivnaya-pena_uk.md
```

---

## Notes

- Workers operate on non-overlapping file sets — no conflicts possible
- Each worker logs to separate file — easy to track progress
- Skills handle retry logic internally (max 3 iterations)
- If worker crashes, check log for last category and restart manually
