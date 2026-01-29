---
allowed-tools: Bash, Read, Write
---

# Parallel Workers Launcher

Запускает несколько Claude-воркеров параллельно на основе плана.

## Входные данные

$ARGUMENTS содержит:
- Строка 1: путь к плану (например docs/plans/2026-01-29-cleanup.md)
- Строки 2+: распределение воркеров (например W1: Task 1 или W1: Task 1, Task 2)

## Алгоритм

1. Прочитай план по пути из первой строки
2. Парсь распределение воркеров из остальных строк
3. Для каждого воркера запусти spawn-claude с /superpowers:executing-plans
4. Выведи сводку запущенных воркеров

## Шаблон spawn-claude

spawn-claude "W{N}: Выполнение задач из плана.

/superpowers:executing-plans {путь_к_плану}

Выполни ТОЛЬКО: {список задач}.

Пиши лог в data/generated/audit-logs/W{N}_log.md

НЕ ДЕЛАЙ git commit - коммиты делает оркестратор" "$(pwd)"

## Пример использования

/parallel docs/plans/2026-01-29-cleanup.md
W1: Task 1
W2: Task 2, Task 3
W3: Task 4, Task 5

## Важно

- Оркестратор НЕ выполняет задачи сам — только запускает воркеров
- После завершения воркеров — проверь логи в data/generated/audit-logs/
- Затем сделай коммит
