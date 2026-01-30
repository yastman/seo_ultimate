# Needs Review Cleanup Plan

> **For Claude:** REQUIRED SUB-SKILL: Use superpowers:executing-plans to implement this plan task-by-task.

**Goal:** Очистить 45 ключей из needs_review: удалить дубли, удалить UK ключи, переместить ключи в правильные категории.

**Architecture:** Параллельное выполнение 5 воркерами. Каждый воркер работает с изолированной группой файлов. Воркеры пишут логи в `data/generated/audit-logs/W{N}_fix_log.md`.

**Tech Stack:** JSON редактирование, spawn-claude

---

## Правила обработки

1. **Дубли (keywords vs synonyms):** удалить из needs_review, оставить только в keywords (уже там с большим volume)
2. **UK ключи:** удалить из RU файлов полностью (не переносить в UK — это отдельный процесс)
3. **Неправильная категория:** удалить из текущей, добавить в synonyms правильной категории
4. **Слишком общие:** удалить из needs_review, добавить в родительскую категорию (если есть)

---

## Task 1: W1 — polirovka cluster

**Files:**
- Modify: `categories/polirovka/data/polirovka_clean.json`
- Modify: `categories/polirovka/polirovalnye-krugi/data/polirovalnye-krugi_clean.json`
- Modify: `categories/polirovka/polirovalnye-mashinki/data/polirovalnye-mashinki_clean.json`
- Create: `data/generated/audit-logs/W1_fix_log.md`

**Проблемы (7 ключей):**

| Файл | Ключ | Проблема | Действие |
|------|------|----------|----------|
| polirovka | полировочный круг для машины (10) | относится к polirovalnye-krugi | → synonyms polirovalnye-krugi |
| polirovka | круги для полировки машины (10) | относится к polirovalnye-krugi | → synonyms polirovalnye-krugi |
| polirovka | круги на полировочную машинку (10) | относится к polirovalnye-krugi | → synonyms polirovalnye-krugi |
| polirovka | круги для полировальной машины (10) | относится к polirovalnye-krugi | → synonyms polirovalnye-krugi |
| polirovka | круги для полировальной машинки (10) | относится к polirovalnye-krugi | → synonyms polirovalnye-krugi |
| polirovalnye-krugi | набор для полировки авто (480) | слишком общий | → synonyms polirovka (родительская) |
| polirovalnye-mashinki | аккумуляторная полировальная машина (260) | дубль с подкатегорией | удалить (уже в akkumulyatornaya) |

**Step 1:** Прочитать все 3 файла

**Step 2:** В `polirovka_clean.json`:
- Удалить весь `needs_review` массив

**Step 3:** В `polirovalnye-krugi_clean.json`:
- Добавить в synonyms 5 ключей из polirovka:
```json
{"keyword": "полировочный круг для машины", "volume": 10},
{"keyword": "круги для полировки машины", "volume": 10},
{"keyword": "круги на полировочную машинку", "volume": 10},
{"keyword": "круги для полировальной машины", "volume": 10},
{"keyword": "круги для полировальной машинки", "volume": 10}
```
- Удалить `needs_review` массив

**Step 4:** В `polirovka_clean.json`:
- Добавить в synonyms: `{"keyword": "набор для полировки авто", "volume": 480}`

**Step 5:** В `polirovalnye-mashinki_clean.json`:
- Удалить `needs_review` массив (ключ уже есть в akkumulyatornaya)

**Step 6:** Написать лог `W1_fix_log.md`:
```markdown
# W1 Fix Log

## polirovka
- Удалён needs_review (5 ключей → polirovalnye-krugi)
- Добавлен synonym: "набор для полировки авто" (480)

## polirovalnye-krugi
- Удалён needs_review (1 ключ → polirovka)
- Добавлено 5 synonyms из polirovka

## polirovalnye-mashinki
- Удалён needs_review (1 ключ — дубль с akkumulyatornaya)

**Итого:** 7 ключей обработано
```

**Step 7:** Валидировать JSON:
```bash
python3 -c "import json; json.load(open('categories/polirovka/data/polirovka_clean.json'))"
python3 -c "import json; json.load(open('categories/polirovka/polirovalnye-krugi/data/polirovalnye-krugi_clean.json'))"
python3 -c "import json; json.load(open('categories/polirovka/polirovalnye-mashinki/data/polirovalnye-mashinki_clean.json'))"
```

---

## Task 2: W2 — aktivnaya-pena дубли

**Files:**
- Modify: `categories/moyka-i-eksterer/avtoshampuni/aktivnaya-pena/data/aktivnaya-pena_clean.json`
- Create: `data/generated/audit-logs/W2_fix_log.md`

**Проблемы (9 ключей):** Все дубли — ключи уже есть в synonyms с большим volume.

| Ключ в needs_review | Volume | Уже в synonyms с volume |
|---------------------|--------|------------------------|
| пена для минимойки | 10 | 70 |
| шампунь для бесконтактной мойки | 10 | 110 |
| пена для бесконтактной мойки | 10 | 70 |
| бесконтактная пена | 10 | 20 |
| бесконтактная химия для автомойки | 10 | 20 |
| профессиональная пена для мойки авто | 10 | 10 |
| пена для автомойки | 20 | 40 |
| купить активную пену | 20 | 260 meta_only |
| купить пену для мойки авто | 40 | 590 meta_only |

**Step 1:** Прочитать файл

**Step 2:** Удалить весь `needs_review` массив (все ключи — дубли, оригиналы остаются в synonyms)

**Step 3:** Написать лог `W2_fix_log.md`:
```markdown
# W2 Fix Log

## aktivnaya-pena
- Удалён needs_review (9 дублей)
- Все ключи уже были в synonyms с бо́льшим volume
- Никаких изменений в keywords/synonyms не требуется

**Итого:** 9 дублей удалено
```

**Step 4:** Валидировать JSON

---

## Task 3: W3 — moyka-i-eksterer дубли

**Files:**
- Modify: `categories/moyka-i-eksterer/ochistiteli-kuzova/antibitum/data/antibitum_clean.json`
- Modify: `categories/moyka-i-eksterer/ochistiteli-kuzova/antimoshka/data/antimoshka_clean.json`
- Modify: `categories/moyka-i-eksterer/ochistiteli-kuzova/glina-i-avtoskraby/data/glina-i-avtoskraby_clean.json`
- Create: `data/generated/audit-logs/W3_fix_log.md`

**Проблемы:**

**antibitum (3 ключа):** коммерческие ключи в keywords → должны быть в synonyms meta_only
- купить антибитум для авто
- антибитум купить
- антибитум цена

**antimoshka (2 ключа):** дубли
- антимошка на мойке (30) — дубль в synonyms
- концентрат антимошка (20) — дубль в synonyms

**glina-i-avtoskraby (5 ключей):** дубли и коммерческие
- автомобильная глина (20) — дубль в synonyms
- глина для кузова авто — дубль в variations
- глина для полировки авто — дубль в variations
- купить синюю глину для авто — коммерческий, уже в synonyms meta_only
- глина для мойки авто (10) — дубль в synonyms

**Step 1:** Прочитать все 3 файла

**Step 2:** antibitum: проверить, есть ли коммерческие в synonyms. Если нет — добавить с meta_only. Удалить needs_review.

**Step 3:** antimoshka: удалить needs_review (дубли)

**Step 4:** glina-i-avtoskraby: удалить needs_review (дубли)

**Step 5:** Написать лог

**Step 6:** Валидировать JSON

---

## Task 4: W4 — sredstva-dlya-diskov-i-shin

**Files:**
- Modify: `categories/moyka-i-eksterer/sredstva-dlya-diskov-i-shin/ochistiteli-diskov/data/ochistiteli-diskov_clean.json`
- Modify: `categories/moyka-i-eksterer/sredstva-dlya-diskov-i-shin/ochistiteli-shin/data/ochistiteli-shin_clean.json`
- Modify: `categories/moyka-i-eksterer/sredstva-dlya-diskov-i-shin/cherniteli-shin/data/cherniteli-shin_clean.json`
- Create: `data/generated/audit-logs/W4_fix_log.md`

**Проблемы:**

**ochistiteli-diskov (7 ключей):** дубли + 1 нерелевантный
- средства для чистки дисков (50) — дубль
- полироль для колес — нерелевантен (про шины, не диски) → УДАЛИТЬ
- химия для чистки дисков (20) — дубль
- жидкость для чистки дисков (10) — дубль
- средство для дисков (20) — дубль
- средство для мойки дисков (20) — дубль
- очиститель колесных дисков (10) — дубль

**ochistiteli-shin (2 ключа):** дубли
- средство для чистки шин (10) — дубль
- средство для очистки резины (10) — дубль

**cherniteli-shin (4 ключа):** дубли + коммерческий
- купить чернитель резины (70) — коммерческий, проверить meta_only
- полироль для шин (90) — дубль
- средство для резины (10) — дубль
- средства для шин (10) — дубль

**Step 1-5:** Аналогично предыдущим — удалить needs_review, проверить meta_only

---

## Task 5: W5 — zashchitnye-pokrytiya + aksessuary + pyatnovyvoditeli

**Files:**
- Modify: `categories/zashchitnye-pokrytiya/keramika-i-zhidkoe-steklo/data/keramika-i-zhidkoe-steklo_clean.json`
- Modify: `categories/zashchitnye-pokrytiya/kvik-deteylery/data/kvik-deteylery_clean.json`
- Modify: `categories/zashchitnye-pokrytiya/voski/tverdyy-vosk/data/tverdyy-vosk_clean.json`
- Modify: `categories/aksessuary/malyarniy-skotch/data/malyarniy-skotch_clean.json`
- Modify: `categories/aksessuary/mikrofibra-i-tryapki/data/mikrofibra-i-tryapki_clean.json`
- Modify: `categories/ukhod-za-intererom/pyatnovyvoditeli/data/pyatnovyvoditeli_clean.json`
- Create: `data/generated/audit-logs/W5_fix_log.md`

**Проблемы:**

**keramika-i-zhidkoe-steklo (1 ключ):**
- жидкое стекло на лобовое (10) — может относиться к antidozhd → УДАЛИТЬ (спорный)

**kvik-deteylery (1 ключ):**
- полимер для авто (140) — слишком общий → переместить в zashchitnye-pokrytiya (родитель)

**tverdyy-vosk (1 ключ):**
- купить воск для машины (30) — слишком общий → переместить в voski (родитель)

**malyarniy-skotch (1 UK ключ):**
- скотч малярний (1000) — UK ключ → УДАЛИТЬ из RU

**mikrofibra-i-tryapki (1 UK ключ):**
- купити тряпку для авто (10) — UK ключ → УДАЛИТЬ из RU

**pyatnovyvoditeli (1 ключ):**
- автохимия очиститель кузова (10) — про кузов, не салон → УДАЛИТЬ (нерелевантен)

**Step 1:** Прочитать все 6 файлов

**Step 2-7:** Для каждого файла:
- Удалить needs_review
- Для kvik-deteylery: добавить "полимер для авто" в zashchitnye-pokrytiya synonyms
- Для tverdyy-vosk: добавить "купить воск для машины" в voski synonyms

**Step 8:** Написать лог

**Step 9:** Валидировать JSON

---

## Запуск воркеров

```bash
# W1: polirovka cluster
spawn-claude "W1: Очистка needs_review в polirovka/*.

REQUIRED SKILLS:
- superpowers:executing-plans
- superpowers:verification-before-completion

План: docs/plans/2026-01-29-needs-review-cleanup-plan.md
Задача: Task 1

НЕ ДЕЛАЙ git commit - коммиты делает оркестратор" "$(pwd)"

# W2: aktivnaya-pena
spawn-claude "W2: Очистка needs_review в aktivnaya-pena.

REQUIRED SKILLS:
- superpowers:executing-plans
- superpowers:verification-before-completion

План: docs/plans/2026-01-29-needs-review-cleanup-plan.md
Задача: Task 2

НЕ ДЕЛАЙ git commit - коммиты делает оркестратор" "$(pwd)"

# W3: moyka-i-eksterer ochistiteli-kuzova
spawn-claude "W3: Очистка needs_review в antibitum, antimoshka, glina-i-avtoskraby.

REQUIRED SKILLS:
- superpowers:executing-plans
- superpowers:verification-before-completion

План: docs/plans/2026-01-29-needs-review-cleanup-plan.md
Задача: Task 3

НЕ ДЕЛАЙ git commit - коммиты делает оркестратор" "$(pwd)"

# W4: sredstva-dlya-diskov-i-shin
spawn-claude "W4: Очистка needs_review в ochistiteli-diskov, ochistiteli-shin, cherniteli-shin.

REQUIRED SKILLS:
- superpowers:executing-plans
- superpowers:verification-before-completion

План: docs/plans/2026-01-29-needs-review-cleanup-plan.md
Задача: Task 4

НЕ ДЕЛАЙ git commit - коммиты делает оркестратор" "$(pwd)"

# W5: zashchitnye-pokrytiya + aksessuary + pyatnovyvoditeli
spawn-claude "W5: Очистка needs_review в keramika, kvik-deteylery, tverdyy-vosk, malyarniy-skotch, mikrofibra, pyatnovyvoditeli.

REQUIRED SKILLS:
- superpowers:executing-plans
- superpowers:verification-before-completion

План: docs/plans/2026-01-29-needs-review-cleanup-plan.md
Задача: Task 5

НЕ ДЕЛАЙ git commit - коммиты делает оркестратор" "$(pwd)"
```

---

## После воркеров

**Step 1:** Проверить логи в `data/generated/audit-logs/W{1-5}_fix_log.md`

**Step 2:** Валидировать все 16 JSON файлов:
```bash
for f in $(find categories -name "*_clean.json"); do python3 -c "import json; json.load(open('$f'))" && echo "✓ $f"; done
```

**Step 3:** Проверить, что needs_review удалён:
```bash
grep -r '"needs_review"' categories/ --include="*_clean.json" | grep -v '": \[\]'
```

**Step 4:** Коммит:
```bash
git add categories/ data/generated/audit-logs/
git commit -m "fix: cleanup 45 keywords from needs_review sections"
```
