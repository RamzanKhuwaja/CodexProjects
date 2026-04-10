# Memory System

This Codex workspace uses repo files as the memory system.

## Layers

- `memory/*.md` — stable workspace facts and user preferences
- `tasks/TASKS.md` — current workspace state
- `tasks/DECISIONS.md` — locked workspace decisions
- `<project>/memory/PROJECT_MEMORY.md` — stable project facts
- `<project>/tasks/TASKS.md` — current project state
- `<project>/tasks/DECISIONS.md` — locked project decisions

## Rule

Ramzan should not need to manage these files manually.
Codex should update them when stable facts or meaningful session changes occur.
