# AI Patterns to Detect

## Linguistic Patterns (LLM fingerprints)

Search for these exact phrases:

```
"В современном мире"
"Важно отметить"
"Понимание .* помогает"
"Это позволяет"
"Следует учитывать"
"Стоит обратить внимание"
"Необходимо понимать"
"Играет важную роль"
"Является неотъемлемой частью"
"Обеспечивает надёжную защиту"
"Благодаря этому"
"Таким образом"
"В связи с этим"
```

## Semantic Emptiness

Sentences that say nothing concrete:

```
"Качество имеет значение при выборе"
"Правильный выбор обеспечит хороший результат"
"Каждый тип имеет свои особенности"
"Это серьёзная проблема, требующая серьёзного подхода"
"Всё зависит от конкретной ситуации"
"Важно учитывать все факторы"
```

## Structural Patterns

- Paragraphs of identical length (3-4 sentences each)
- Lists always 3-5 items
- Each list item starts with noun
- Repeating "X — это Y, который Z" constructs
- Every section has exactly same structure

## Red Flags for Facts

Often invented by LLMs — verify extra carefully:

- Exact percentages ("95% эффективность")
- Specific time durations ("действует 5-10 минут")
- Competitor comparisons
- "Рекомендуется профессионалами"
- Any numbers without source
