# codex_progress_monitoring — Codex Instructions

## Source Of Truth

Read these at the start of substantive work:

1. `projectplan.md`
2. `memory/PROJECT_MEMORY.md`
3. `tasks/TASKS.md`
4. `tasks/DECISIONS.md`
5. `docs/LEGACY_SESSION_NOTES.md`

`projectplan.md` is the main planning and operating reference for the project.
`docs/LEGACY_SESSION_NOTES.md` preserves the pre-template session notes that existed before this project was moved into `CodexProjects`.

---

## Memory

Use:

- `memory/PROJECT_MEMORY.md` for stable project facts and recurring cautions
- `tasks/TASKS.md` for current status, open items, and the latest sessions
- `tasks/DECISIONS.md` for locked project decisions

---

## Session Commands

Preferred session phrases are:

- `start session`
- `end session`

When Ramzan says `start session` for this project:

1. Read:
   - `AGENTS.md`
   - `projectplan.md`
   - `memory/PROJECT_MEMORY.md`
   - `tasks/TASKS.md`
   - `tasks/DECISIONS.md`
   - `docs/LEGACY_SESSION_NOTES.md`
2. Report back:
   - current project status
   - what was done last session
   - the next recorded step
3. Then continue unless redirected.

When Ramzan says `end session` for this project:

1. Update `tasks/TASKS.md`:
   - current status
   - open items
   - session log entry
   - next step
2. Update `tasks/DECISIONS.md` if any permanent decisions were made.
3. Move session entries older than the last 5 from `tasks/TASKS.md` to `tasks/ARCHIVE.md`.
4. Update `memory/PROJECT_MEMORY.md` if any stable facts were learned.
5. Update `CHEATSHEET.txt` if commands, paths, or trigger phrases changed.

---

## Rules

- Do not create or maintain `README.md` files.
- Run Python entry scripts from the project root so `Common`, `MAE`, and `VAU` import paths resolve correctly.
- Keep the current top-level code layout (`Common/`, `MAE/`, `VAU/`, `old-scripts/`) unless there is a specific reason to refactor it.
- `Data/` and `Ready For Printing/` are part of the active working layout and should not be renamed without updating path logic.
- Use `output/` only for new generated artifacts that are not part of the existing `Ready For Printing/` workflow.

---

## Git Rules

Do commit:

- `Common/`, `MAE/`, `VAU/`, and `old-scripts/`
- everything in `Data/`
- Office and PDF files in `Ready For Printing/`, `For Data Entry Person/`, and `WeekToWeek/`
- project memory, task, and docs files

Do not commit:

- `__pycache__/`
- `.pyc` files
- machine-generated files in `output/` unless explicitly requested
