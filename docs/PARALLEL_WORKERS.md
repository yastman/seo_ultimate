# Parallel Claude Workers

Запуск нескольких Claude-агентов для параллельной работы над задачами.

---

## Быстрый старт

```
/parallel docs/plans/2026-01-28-feature.md
W1: Task 1
W2: Task 2, Task 3
W3: Task 4
```

Оркестратор читает план и запускает воркеров. После завершения — проверяет логи и делает коммит.

---

## Синтаксис spawn-claude

```bash
spawn-claude "W{N}: {Краткое описание задачи}.

/superpowers:executing-plans docs/plans/YYYY-MM-DD-task.md

Выполни ТОЛЬКО Task N.

НЕ ДЕЛАЙ git commit - коммиты делает оркестратор" "$(pwd)"
```

### Пример

```bash
spawn-claude "W1: Очистка needs_review в polirovka cluster.

/superpowers:executing-plans docs/plans/2026-01-29-cleanup-plan.md

Выполни ТОЛЬКО Task 1.

НЕ ДЕЛАЙ git commit - коммиты делает оркестратор" "$(pwd)"
```

---

## Логи воркеров

Воркеры пишут логи в `data/generated/audit-logs/`:

```
data/generated/audit-logs/
├── W1_log.md      # или W1_fix_log.md
├── W2_log.md
├── W3_log.md
└── ...
```

### Формат лога

```markdown
# W{N} Log

## {category-slug}
- Действие 1
- Действие 2
- ⚠️ Проблема (если есть)

## {another-category}
- ...

---

**Итого:** N файлов обработано, M проблем
```

---

## Правила

### Для оркестратора

1. **Разделяй файлы** — 1 воркер = 1 набор файлов, без пересечений
2. **Группируй связанные** — если нужен перенос между файлами, оба файла одному воркеру
3. **Не делай задачи сам** — только запускай воркеров и коммить после
4. **Проверяй логи** — после завершения воркеров читай `data/generated/audit-logs/`

### Для воркеров

1. **Читай план** — `/superpowers:executing-plans` загружает план
2. **Выполняй только свою Task** — не трогай чужие файлы
3. **Пиши лог** — создай `data/generated/audit-logs/W{N}_log.md`
4. **Не коммить** — коммиты делает оркестратор
5. **Валидируй JSON** — `python3 -c "import json; json.load(open('file.json'))"`

---

## tmux навигация

| Комбо | Действие |
|-------|----------|
| `Ctrl+A, w` | Список окон (выбрать воркера) |
| `Ctrl+A, n` | Следующее окно |
| `Ctrl+A, p` | Предыдущее окно |
| `Ctrl+A, d` | Отсоединиться от tmux |
| `tmux a` | Подключиться обратно |

---

## После завершения воркеров

### 1. Проверить логи

```bash
ls data/generated/audit-logs/
cat data/generated/audit-logs/W*_log.md
```

### 2. Валидировать файлы

```bash
# Все JSON
for f in $(find categories -name "*_clean.json"); do
  python3 -c "import json; json.load(open('$f'))" && echo "✓ $f"
done

# Проверить конкретную секцию
grep -r '"needs_review"' categories/ --include="*_clean.json"
```

### 3. Коммит

```bash
git add categories/ data/generated/audit-logs/
git commit -m "feat: описание изменений"
git push
```

---

## Troubleshooting

### Воркер сделал что-то не то

```bash
# Откатить изменения
git checkout -- categories/

# Перезапустить воркера с исправленным промптом
spawn-claude "W1: ..." "$(pwd)"
```

### Конфликт файлов

Если два воркера изменили один файл — откатить и перераспределить задачи.

### Воркер завис

```bash
# Убить окно
Ctrl+A, &

# Или через tmux
tmux kill-window -t W1
```
