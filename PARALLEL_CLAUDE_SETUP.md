# Параллельные Claude сессии в tmux

Инструкция по запуску нескольких Claude-агентов одновременно для ускорения работы.

---

## Архитектура

```
tmux session "claude"
├── Окно 1: Основной Claude (оркестратор)
│   └── Создаёт план и запускает воркеров через spawn-claude
├── Окно 2: Worker 1 (независимая Claude сессия)
├── Окно 3: Worker 2 (независимая Claude сессия)
├── Окно 4: Worker 3 (независимая Claude сессия)
└── Окно 5+: Дополнительные воркеры по мере необходимости
```

**Результат:** N Claude-агентов работают **параллельно**, каждый на своей задаче, в одной tmux сессии.

---

## Быстрый старт (3 шага)

### 1. Открыть tmux сессию в проекте

```bash
# Если в WSL
cd /mnt/c/Users/user/Documents/Сайты/Ultimate.net.ua/сео_для_категорий_ультимейт

# Или через WezTerm (Ctrl+Shift+M)
# Меню → выбрать проект "SEO Ultimate"
```

### 2. Запустить основную Claude сессию

```bash
claude code
```

Это окно 1 (оркестратор). Здесь ты будешь запускать воркеров.

### 3. Из Claude запустить воркеров

Скопируй и выполни эту команду **внутри Claude**:

```bash
spawn-claude "W1: Добавить UK keywords в kategoriya-1" "$(pwd)"
spawn-claude "W2: Генерировать контент для kategoriya-2" "$(pwd)"
spawn-claude "W3: Проверить качество мета для kategoriya-3" "$(pwd)"
```

**Готово!** Три Claude работают параллельно.

---

## Переключение между воркерами

| Комбо | Действие |
|-------|----------|
| **Ctrl+A, 1** | Основной Claude (оркестратор) |
| **Ctrl+A, 2** | Worker 1 |
| **Ctrl+A, 3** | Worker 2 |
| **Ctrl+A, 4** | Worker 3 |
| **Ctrl+A, n** | Следующее окно |
| **Ctrl+A, p** | Предыдущее окно |
| **Ctrl+A, w** | Список всех окон (выбрать) |

---

## Синтаксис spawn-claude

```bash
spawn-claude "ПРОМПТ" "ПУТЬ"
```

### Параметры

| Параметр | Значение | Пример |
|----------|----------|--------|
| **ПРОМПТ** | Задача для Claude | `"W1: Добавить UK keywords"` |
| **ПУТЬ** | Путь к проекту | `"$(pwd)"` или абсолютный путь |

### Примеры

**Пример 1: Простой воркер**
```bash
spawn-claude "W1: Добавить UK keywords в aktivnaya-pena" "$(pwd)"
```

**Пример 2: С использованием skills**
```bash
spawn-claude "W1: Добавить UK keywords.

REQUIRED SKILLS:
- superpowers:executing-plans
- superpowers:verification-before-completion

План: docs/plans/uk-keywords.md
Категория: aktivnaya-pena

Алгоритм:
1. Прочитай uk/categories/aktivnaya-pena/data/aktivnaya-pena_clean.json
2. Обнови keywords массив из плана
3. VERIFY: python -m json.tool < файл.json
4. git commit" "$(pwd)"
```

**Пример 3: Несколько категорий**
```bash
spawn-claude "W2: Генерировать контент.

Категории: antibitum, antidozhd, antizagryaznitel

Для каждой:
1. /content-generator {slug}
2. Проверить качество
3. git commit

План: docs/plans/content-gen.md" "$(pwd)"
```

---

## Структура промпта воркера

**Рекомендуемый формат:**

```
W{N}: {Краткое описание задачи}.

REQUIRED SKILLS:
- superpowers:executing-plans
- superpowers:verification-before-completion

План: docs/plans/YYYY-MM-DD-task.md
Чек-лист: tasks/TODO_xxx.md

Твои файлы/категории: список

Алгоритм:
1. Прочитай источник данных
2. Примени изменения
3. VERIFY: команда для проверки
4. git commit

Путь: /мнт/путь/к/проекту
```

---

## Мониторинг прогресса

### Способ 1: git log

В отдельном окне tmux:

```bash
Ctrl+A, c                    # Новое окно
watch -n 2 "git log --oneline -10"
```

Будет обновляться каждые 2 секунды, показывая свежие коммиты от воркеров.

### Способ 2: git status

```bash
git status
```

Покажет какие файлы изменены всеми воркерами.

### Способ 3: git diff

```bash
git diff --name-only HEAD~5
```

Показать какие файлы изменены за последние 5 коммитов.

---

## Правила параллелизации

| Правило | ✅ Хорошо | ❌ Плохо |
|---------|----------|---------|
| 1 воркер = 1 независимый набор файлов | W1: kategoriya-1, W2: kategoriya-2 | W1: kategoriya-1 строка 1-50, W2: kategoriya-1 строка 51-100 |
| Группируй мелкое | W1: meta + keywords + content | W1: meta, W2: keywords, W3: content (оверхед) |
| Общий файл — только читать | Все читают план | Все пишут в один файл |
| Тесты с кодом | W1: content-gen + test_content | W1: content-gen, W2: test_content |

---

## Примеры реальных воркеров

### Пример 1: UK Keywords для 3 категорий

```bash
spawn-claude "W1: Добавить UK keywords.

REQUIRED SKILLS:
- superpowers:executing-plans
- superpowers:verification-before-completion

План: docs/plans/2026-01-27-uk-keywords.md

Категории: aktivnaya-pena, antibitum, antidozhd

Алгоритм для каждой:
1. Прочитай uk/categories/{slug}/data/{slug}_clean.json
2. Обнови keywords из плана
3. VERIFY: python -m json.tool < файл.json
4. git commit

Путь: /mnt/c/Users/user/Documents/Сайты/Ultimate.net.ua/сео_для_категорий_ультимейт" "$(pwd)"
```

### Пример 2: Generate Content для 3 категорий

```bash
spawn-claude "W2: Генерировать контент.

REQUIRED SKILLS:
- superpowers:executing-plans
- superpowers:verification-before-completion

План: docs/plans/2026-01-27-content-gen.md

Категории: aktivnaya-pena, antibitum, antidozhd

Для каждой:
1. /content-generator {slug}
2. Проверить результат: wc -w categories/{slug}/content/{slug}_ru.md
3. git commit" "$(pwd)"
```

### Пример 3: Quality Gate для 3 категорий

```bash
spawn-claude "W3: Quality gate для всех.

REQUIRED SKILLS:
- superpowers:verification-before-completion

Категории: aktivnaya-pena, antibitum, antidozhd

Для каждой:
1. /quality-gate {slug}
2. Проверить результат
3. git commit" "$(pwd)"
```

---

## Обработка ошибок

### Ошибка: "Not inside tmux session"

```
❌ Error: Not inside tmux session
   Run: tmux new -A -s claude
```

**Решение:**
```bash
# Входишь в tmux
Ctrl+Shift+M
```

### Worker зависает

```bash
# Ctrl+A, {номер} → перейти на зависший worker
# Ctrl+C → прервать
# claude code → перезапустить
```

### Конфликт в git

Если два воркера редактируют один файл:

```bash
# 1. Посмотреть конфликт
git status

# 2. Разрешить (оркестратор)
git diff
git add .
git commit -m "Merge workers results"
```

---

## Шпаргалка tmux команд

### Окна (Windows)

| Комбо | Действие |
|-------|----------|
| `Ctrl+A, c` | Новое окно |
| `Ctrl+A, n` | Следующее окно |
| `Ctrl+A, p` | Предыдущее окно |
| `Ctrl+A, 1/2/3` | Перейти на окно 1/2/3 |
| `Ctrl+A, w` | Список окон |
| `Ctrl+A, ,` | Переименовать окно |
| `Ctrl+A, x` | Закрыть окно |

### Панели (Splits)

| Комбо | Действие |
|-------|----------|
| `Ctrl+A, \|` | Вертикальный сплит |
| `Ctrl+A, -` | Горизонтальный сплит |
| `Ctrl+A, hjkl` | Переместиться между панелями |
| `Ctrl+A, z` | Развернуть панель |

### Работа

| Комбо | Действие |
|-------|----------|
| `Ctrl+A, d` | Отсоединиться (session stays alive) |
| `Ctrl+A, r` | Перезагрузить конфиг |
| `Ctrl+A, [` | Enter copy mode (скроллинг) |

---

## Продвинутые техники

### Batch Processing (много воркеров за раз)

```bash
# Создаёшь список категорий
categories=("aktivnaya-pena" "antibitum" "antidozhd" "antimoshhnost" "antioxidant")

# Запускаешь воркера для каждой (или группы)
for cat in "${categories[@]}"; do
  spawn-claude "W: Process $cat" "$(pwd)"
done
```

### Переиспользование старого плана

```bash
spawn-claude "W1: Повторить план из вчера.

План: docs/plans/2026-01-26-old-plan.md
Изменения: только для категорий antibitum и antidozhd" "$(pwd)"
```

### Логирование воркеров

```bash
# В каждом воркере добавь в промпт:
spawn-claude "W1: ...

VERIFY:
- Логи сохраняй: tee -a logs/worker-1.log
- Коммиты: git log --oneline -3" "$(pwd)"
```

---

## Когда использовать параллельных Claude

✅ **Используй когда:**
- Нужно обработать много категорий (5+)
- Задачи **независимы** друг от друга
- Каждому воркеру **свой набор файлов**
- Нужно ускорить процесс в 3-4 раза

❌ **НЕ используй когда:**
- Задачи зависят друг от друга
- Воркеры редактируют **один и тот же файл**
- Сложная логика синхронизации

---

## Контрольный чек-лист

- [ ] tmux открыт (`Ctrl+Shift+M`)
- [ ] Находишься в правильной директории проекта
- [ ] Claude сессия запущена (`claude code`)
- [ ] Скрипт `spawn-claude` доступен (`which spawn-claude`)
- [ ] Конфиг tmux загружен (`Ctrl+A, r`)
- [ ] spawn-claude создаёт окна с воркерами
- [ ] Переключение между окнами работает (`Ctrl+A, n`)
- [ ] git коммиты видны от всех воркеров (`git log`)

---

## Версия

**2026-01-27** — Полная настройка для параллельных Claude сессий в tmux
