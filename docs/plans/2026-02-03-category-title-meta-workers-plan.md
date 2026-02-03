# Category Title Meta Update — Workers Plan

> **For Claude:** REQUIRED SUB-SKILL: Use tmux-swarm-orchestration to execute this plan via parallel workers.

**Goal:** Обновить мета-теги 10 составных категорий (RU+UK), использовать `category_title` из `_clean.json` для Title/H1.

**Architecture:** 2 воркера параллельно: W1 обновляет RU мета, W2 обновляет UK мета. После — оркестратор генерирует SQL и деплоит.

**Tech Stack:** JSON, Bash, validate_meta.py

---

## Предварительные условия (уже выполнены)

- ✅ Task 1-2: `category_title` добавлен во все `_clean.json`
- ✅ Task 3: UK skill обновлён до v17.0

---

## Worker W1: Update RU Meta (10 files)

**Промпт для spawn-claude:**

```
W1: Update RU Meta Files.

Обнови мета-теги для 10 категорий с `category_title`.
Бери `category_title` из `_clean.json`, используй в Title и H1.

**Title формула:** {category_title} — купить, цены | Ultimate
**H1:** {category_title}

**Файлы для обновления:**

| slug | category_title | meta.json path |
|------|---------------|----------------|
| glavnaya | Автохимия и автокосметика | categories/glavnaya/meta/glavnaya_meta.json |
| moyka-i-eksterer | Мойка и экстерьер | categories/moyka-i-eksterer/meta/moyka-i-eksterer_meta.json |
| glina-i-avtoskraby | Глина и автоскрабы | categories/moyka-i-eksterer/ochistiteli-kuzova/glina-i-avtoskraby/meta/glina-i-avtoskraby_meta.json |
| gubki-i-varezhki | Губки и варежки | categories/aksessuary/gubki-i-varezhki/meta/gubki-i-varezhki_meta.json |
| mikrofibra-i-tryapki | Микрофибра и тряпки | categories/aksessuary/mikrofibra-i-tryapki/meta/mikrofibra-i-tryapki_meta.json |
| raspyliteli-i-penniki | Распылители и пенники | categories/aksessuary/raspyliteli-i-penniki/meta/raspyliteli-i-penniki_meta.json |
| vedra-i-emkosti | Вёдра и ёмкости | categories/aksessuary/vedra-i-emkosti/meta/vedra-i-emkosti_meta.json |
| kisti-dlya-deteylinga | Щётки и кисти для детейлинга | categories/aksessuary/shchetki-i-kisti/kisti-dlya-deteylinga/meta/kisti-dlya-deteylinga_meta.json |
| keramika-i-zhidkoe-steklo | Керамика и жидкое стекло | categories/zashchitnye-pokrytiya/keramika-i-zhidkoe-steklo/meta/keramika-i-zhidkoe-steklo_meta.json |
| opt-i-b2b | Автохимия оптом | categories/opt-i-b2b/meta/opt-i-b2b_meta.json |

**Для каждого файла:**
1. Прочитай файл
2. Обнови `meta.title` по формуле
3. Обнови `h1` = category_title
4. Сохрани файл
5. Валидируй: `python3 scripts/validate_meta.py <path>`

**Description паттерны:**
- Producer категории: "{category_title} от производителя Ultimate..."
- Shop категории: "{category_title} в интернет-магазине Ultimate..."

Пиши лог в data/generated/audit-logs/W1_ru_meta_log.md

НЕ ДЕЛАЙ git commit
```

---

## Worker W2: Update UK Meta (10 files)

**Промпт для spawn-claude:**

```
W2: Update UK Meta Files.

Обнови мета-теги для 10 UK категорій з `category_title`.
Бери `category_title` з `_clean.json`, використовуй в Title та H1.

**Title формула:** {category_title} — купити, ціни | Ultimate
**H1:** {category_title}

**Файли для оновлення:**

| slug | category_title | meta.json path |
|------|---------------|----------------|
| glavnaya | Автохімія та автокосметика | uk/categories/glavnaya/meta/glavnaya_meta.json |
| moyka-i-eksterer | Мийка та екстер'єр | uk/categories/moyka-i-eksterer/meta/moyka-i-eksterer_meta.json |
| glina-i-avtoskraby | Глина та автоскраби | uk/categories/glina-i-avtoskraby/meta/glina-i-avtoskraby_meta.json |
| gubki-i-varezhki | Губки та рукавички | uk/categories/gubki-i-varezhki/meta/gubki-i-varezhki_meta.json |
| mikrofibra-i-tryapki | Мікрофібра та ганчірки | uk/categories/mikrofibra-i-tryapki/meta/mikrofibra-i-tryapki_meta.json |
| raspyliteli-i-penniki | Розпилювачі та піноутворювачі | uk/categories/raspyliteli-i-penniki/meta/raspyliteli-i-penniki_meta.json |
| vedra-i-emkosti | Відра та ємності | uk/categories/vedra-i-emkosti/meta/vedra-i-emkosti_meta.json |
| kisti-dlya-deteylinga | Щітки та пензлі для детейлінгу | uk/categories/kisti-dlya-deteylinga/meta/kisti-dlya-deteylinga_meta.json |
| keramika-i-zhidkoe-steklo | Кераміка та рідке скло | uk/categories/keramika-i-zhidkoe-steklo/meta/keramika-i-zhidkoe-steklo_meta.json |
| opt-i-b2b | Автохімія оптом | uk/categories/opt-i-b2b/meta/opt-i-b2b_meta.json |

**Для кожного файлу:**
1. Прочитай файл
2. Онови `meta.title` за формулою
3. Онови `h1` = category_title
4. Збережи файл
5. Валідуй: `python3 scripts/validate_meta.py <path> --lang uk`

**Description патерни:**
- Producer категорії: "{category_title} від виробника Ultimate..."
- Shop категорії: "{category_title} в інтернет-магазині Ultimate..."

Пиши лог в data/generated/audit-logs/W2_uk_meta_log.md

НЕ РОБИ git commit
```

---

## Оркестратор: Post-Workers Tasks

После завершения W1 и W2:

### Task 1: Проверить логи воркеров

```bash
cat data/generated/audit-logs/W1_ru_meta_log.md
cat data/generated/audit-logs/W2_uk_meta_log.md
```

### Task 2: Batch валидация

```bash
python3 scripts/validate_meta.py --all --lang ru 2>&1 | grep -E "(PASS|FAIL)"
python3 scripts/validate_meta.py --all --lang uk 2>&1 | grep -E "(PASS|FAIL)"
```

### Task 3: Генерация SQL

Создать `data/generated/category_title_meta_update.sql` по шаблону из основного плана.

**Category ID маппинг (проверить на сервере):**

| slug | category_id |
|------|-------------|
| glavnaya | 468 |
| moyka-i-eksterer | ? |
| glina-i-avtoskraby | 423 |
| gubki-i-varezhki | 453 |
| mikrofibra-i-tryapki | 446 |
| raspyliteli-i-penniki | 447 |
| vedra-i-emkosti | 448 |
| kisti-dlya-deteylinga | 495 |
| keramika-i-zhidkoe-steklo | 439 |
| opt-i-b2b | 493 |

### Task 4: Git commit

```bash
git add categories/*/meta/*_meta.json uk/categories/*/meta/*_meta.json
git commit -m "feat(meta): update category_title in Title/H1 for 10 compound categories (RU+UK)"
```

### Task 5: Deploy SQL (отдельно)

См. основной план Tasks 7-9.

---

## Spawn Commands

```bash
# Создать директорию для логов
mkdir -p data/generated/audit-logs

# Запуск воркеров
spawn-claude "W1: Update RU Meta Files.

Обнови мета-теги для 10 категорий с category_title.
Бери category_title из _clean.json, используй в Title и H1.

Title формула: {category_title} — купить, цены | Ultimate
H1: {category_title}

Файлы:
- categories/glavnaya/meta/glavnaya_meta.json → Автохимия и автокосметика
- categories/moyka-i-eksterer/meta/moyka-i-eksterer_meta.json → Мойка и экстерьер
- categories/moyka-i-eksterer/ochistiteli-kuzova/glina-i-avtoskraby/meta/glina-i-avtoskraby_meta.json → Глина и автоскрабы
- categories/aksessuary/gubki-i-varezhki/meta/gubki-i-varezhki_meta.json → Губки и варежки
- categories/aksessuary/mikrofibra-i-tryapki/meta/mikrofibra-i-tryapki_meta.json → Микрофибра и тряпки
- categories/aksessuary/raspyliteli-i-penniki/meta/raspyliteli-i-penniki_meta.json → Распылители и пенники
- categories/aksessuary/vedra-i-emkosti/meta/vedra-i-emkosti_meta.json → Вёдра и ёмкости
- categories/aksessuary/shchetki-i-kisti/kisti-dlya-deteylinga/meta/kisti-dlya-deteylinga_meta.json → Щётки и кисти для детейлинга
- categories/zashchitnye-pokrytiya/keramika-i-zhidkoe-steklo/meta/keramika-i-zhidkoe-steklo_meta.json → Керамика и жидкое стекло
- categories/opt-i-b2b/meta/opt-i-b2b_meta.json → Автохимия оптом

Для каждого: обнови title и h1, валидируй python3 scripts/validate_meta.py <path>

Пиши лог: data/generated/audit-logs/W1_ru_meta_log.md

НЕ ДЕЛАЙ git commit" "$(pwd)"


spawn-claude "W2: Update UK Meta Files.

Онови мета-теги для 10 UK категорій з category_title.
Бери category_title з _clean.json, використовуй в Title та H1.

Title формула: {category_title} — купити, ціни | Ultimate
H1: {category_title}

Файли:
- uk/categories/glavnaya/meta/glavnaya_meta.json → Автохімія та автокосметика
- uk/categories/moyka-i-eksterer/meta/moyka-i-eksterer_meta.json → Мийка та екстер'єр
- uk/categories/glina-i-avtoskraby/meta/glina-i-avtoskraby_meta.json → Глина та автоскраби
- uk/categories/gubki-i-varezhki/meta/gubki-i-varezhki_meta.json → Губки та рукавички
- uk/categories/mikrofibra-i-tryapki/meta/mikrofibra-i-tryapki_meta.json → Мікрофібра та ганчірки
- uk/categories/raspyliteli-i-penniki/meta/raspyliteli-i-penniki_meta.json → Розпилювачі та піноутворювачі
- uk/categories/vedra-i-emkosti/meta/vedra-i-emkosti_meta.json → Відра та ємності
- uk/categories/kisti-dlya-deteylinga/meta/kisti-dlya-deteylinga_meta.json → Щітки та пензлі для детейлінгу
- uk/categories/keramika-i-zhidkoe-steklo/meta/keramika-i-zhidkoe-steklo_meta.json → Кераміка та рідке скло
- uk/categories/opt-i-b2b/meta/opt-i-b2b_meta.json → Автохімія оптом

Для кожного: онови title і h1, валідуй python3 scripts/validate_meta.py <path> --lang uk

Пиши лог: data/generated/audit-logs/W2_uk_meta_log.md

НЕ РОБИ git commit" "$(pwd)"
```

---

## Validation Checklist

- [ ] W1 завершён — 10 RU meta обновлены
- [ ] W2 завершён — 10 UK meta обновлены
- [ ] Batch валидация пройдена (PASS для всех)
- [ ] SQL сгенерирован
- [ ] Git commit создан
- [ ] Deploy на сервер (отдельный шаг)

---

**Version:** 1.0 — February 2026
