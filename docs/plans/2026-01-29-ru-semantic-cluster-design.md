# Дизайн: Semantic Cluster для всех RU категорий

**Дата:** 2026-01-29
**Статус:** Draft

---

## Цель

Пройтись по всем 53 RU категориям и применить `/semantic-cluster` — кластеризацию ключей по стемам с переносом variants в synonyms.

## Scope

- 53 файла `*_clean.json` в `categories/`
- 53 файла `*_meta.json` — обновление `keywords_in_content`
- Full режим: clean + meta

## Что делает /semantic-cluster

1. Читает `_clean.json`
2. Находит дубли по стемам (авто/автомобиль, машина/машинка, мойка/мытьё)
3. Выбирает canonical форму (по volume → длине → нейтральности)
4. Переносит variants в `synonyms` с `use_in: "lsi"` и `variant_of`
5. Обновляет `_meta.json` — в `keywords_in_content` только canonical формы
6. Валидирует результат

## Ресурсы

- 5 параллельных воркеров
- ~10-11 категорий на воркера
- Запуск через `/parallel`

---

## Распределение по воркерам

### W1 (11 категорий) — aksessuary + glavnaya

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
glavnaya
```

### W2 (11 категорий) — moyka-i-eksterer часть 1

```
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
```

### W3 (11 категорий) — moyka-i-eksterer часть 2 + oborudovanie

```
moyka-i-eksterer/sredstva-dlya-diskov-i-shin/keramika-dlya-diskov
moyka-i-eksterer/sredstva-dlya-diskov-i-shin/ochistiteli-diskov
moyka-i-eksterer/sredstva-dlya-diskov-i-shin/ochistiteli-shin
moyka-i-eksterer/sredstva-dlya-stekol/antidozhd
moyka-i-eksterer/sredstva-dlya-stekol/ochistiteli-stekol
moyka-i-eksterer/sredstva-dlya-stekol/omyvatel
moyka-i-eksterer/sredstva-dlya-stekol/polirol-dlya-stekla
oborudovanie
oborudovanie/apparaty-tornador
opt-i-b2b
polirovka
```

### W4 (11 категорий) — polirovka + ukhod-za-intererom

```
polirovka/polirovalnye-krugi
polirovka/polirovalnye-krugi/mekhovye
polirovka/polirovalnye-mashinki
polirovka/polirovalnye-mashinki/akkumulyatornaya
polirovka/polirovalnye-pasty
ukhod-za-intererom
ukhod-za-intererom/neytralizatory-zapakha
ukhod-za-intererom/poliroli-dlya-plastika
ukhod-za-intererom/pyatnovyvoditeli
ukhod-za-intererom/sredstva-dlya-khimchistki-salona
ukhod-za-intererom/sredstva-dlya-kozhi
```

### W5 (9 категорий) — ukhod-za-kozhi + zashchitnye-pokrytiya

```
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

## Алгоритм работы воркера

Каждый воркер выполняет для своих категорий:

### Для каждой категории из списка:

1. **Вызывает `/semantic-cluster {slug}`**
   - Скилл выполняет весь workflow:
     - Читает `_clean.json`
     - Находит дубли по стемам
     - Выбирает canonical
     - Переносит variants в synonyms с `use_in: "lsi"` и `variant_of`
     - Обновляет `_meta.json`
     - Валидирует результат

2. **Логирует результат** в `data/generated/audit-logs/W{N}_log.md`:
   ```markdown
   ## {slug}
   - Найдено дублей: X
   - Перенесено в synonyms: Y
   - Canonical forms: [список]
   ```

3. **Переходит к следующей категории**

### После всех категорий:

- `/superpowers:verification-before-completion`
- **НЕ делает git commit** — коммиты делает оркестратор

---

## Запуск

```bash
/parallel docs/plans/2026-01-29-ru-semantic-cluster-plan.md
W1: Task 1
W2: Task 2
W3: Task 3
W4: Task 4
W5: Task 5
```

---

## После завершения воркеров

1. Проверить логи в `data/generated/audit-logs/W*_log.md`
2. Проверить изменения: `git diff categories/`
3. Коммит:
   ```bash
   git add categories/
   git commit -m "cluster(ru): semantic clustering for 53 categories"
   ```

---

## Валидация

```bash
python3 scripts/validate_meta.py --all
python3 scripts/audit_keyword_consistency.py
```

---

## Риски

| Риск | Митигация |
|------|-----------|
| Неправильный выбор canonical | Приоритет по volume → длине → нейтральности |
| Потеря важных ключей | Variants сохраняются в synonyms с `variant_of` |
| Конфликты между воркерами | Разделение по родительским категориям |

---

## Референсы

- Скилл: `.claude/skills/semantic-cluster/SKILL.md`
- Паттерны стемов: `.claude/skills/semantic-cluster/references/stem-patterns.md`
- Параллельные воркеры: `docs/PARALLEL_WORKERS.md`
