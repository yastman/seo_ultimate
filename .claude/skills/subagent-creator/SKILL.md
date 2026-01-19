---
name: subagent-creator
description: Create specialized subagents for Claude Code. Use when user wants to create a new agent, configure specialized AI assistants, or says /create-agent, создай агента, новый агент, create agent. Subagents are AI assistants with custom prompts, specific tool access, and focused configuration for domain-specific work.
---

# Subagent Creator

Create specialized subagents that handle specific task types within Claude Code.

## Workflow

```
1. Clarify purpose → 2. Choose scope → 3. Configure → 4. Write prompt → 5. Save & test
```

## Quick Start

Create agent file at appropriate location:

| Scope | Location | Use Case |
|-------|----------|----------|
| Project | `.claude/agents/` | Team-shared agents |
| User | `~/.claude/agents/` | Personal reusable agents |

## Agent File Format

```markdown
---
name: agent-name
description: When to use this agent (Claude reads this for delegation)
tools: Read, Grep, Glob, Bash
model: sonnet
---

You are a [role]. When invoked:
1. [First action]
2. [Second action]
3. [Third action]

[Additional instructions]
```

## Configuration Options

### Required Fields

- **`name`**: Unique identifier (lowercase, hyphens only)
- **`description`**: When Claude should delegate to this agent. Include "use proactively" for automatic delegation.

### Optional Fields

| Field | Values | Default |
|-------|--------|---------|
| `tools` | Allowlist: `Read, Grep, Glob, Bash, Edit, Write, WebFetch, WebSearch` | All tools |
| `disallowedTools` | Denylist specific tools | None |
| `model` | `sonnet`, `opus`, `haiku`, `inherit` | `sonnet` |
| `permissionMode` | `default`, `acceptEdits`, `dontAsk`, `bypassPermissions`, `plan` | `default` |

### Permission Modes

- **`default`**: Standard permission prompts
- **`acceptEdits`**: Auto-accept file edits
- **`dontAsk`**: Auto-deny permission prompts
- **`plan`**: Read-only exploration mode

## Common Patterns

### Read-Only Agent (code review, analysis)

```yaml
tools: Read, Grep, Glob, Bash
model: haiku
```

### Editor Agent (debugging, refactoring)

```yaml
tools: Read, Edit, Bash, Grep, Glob
model: sonnet
```

### Research Agent (exploration)

```yaml
tools: Read, Grep, Glob, WebFetch, WebSearch
model: haiku
permissionMode: plan
```

## Examples

See `references/agent-examples.md` for complete agent templates:
- Code Reviewer
- Debugger
- Test Runner
- Documentation Writer
- Data Analyst

## Creation Checklist

1. [ ] Define clear purpose (one task per agent)
2. [ ] Write triggering description
3. [ ] Grant minimum necessary tools
4. [ ] Choose appropriate model (haiku for fast/cheap, sonnet for complex)
5. [ ] Write focused system prompt
6. [ ] Test with real tasks
