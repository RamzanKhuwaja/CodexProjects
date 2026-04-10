# CodexProjects Workspace — Task Tracker

> This file tracks workspace-level sessions only — template changes, workspace rules,
> and cross-project conventions. Project-level work lives in each project's own
> `tasks/TASKS.md`.
>
> Permanent workspace decisions live in `DECISIONS.md`. Older workspace sessions
> live in `ARCHIVE.md`.
>
> **Cleanup (do at each session start or end):** Move workspace sessions older than
> the last 5 to `ARCHIVE.md`. Keep this file readable in under 60 seconds.
>
> **To open a session:** `start session`
> **To close a session:** `end session`

## Current Position

**Status:** Active.
**Last session:** 2026-04-10 — compared Claude and Codex session handling, then upgraded Codex to use explicit `start session` / `end session` conventions with archive support.
**Next step:** Use the new session routine consistently at workspace and project level, then apply the template to the next new project.

## Open Items

- Decide whether existing projects should be retrofitted from `CLAUDE.md` conventions to `AGENTS.md` conventions.
- Decide whether Codex needs a separate workspace memory pattern or should stay file-based only.

## Session Log

### Session 1 — 2026-04-09

**Focus:** Workspace bootstrap and template design.

- Confirmed `C:\Users\ramza\My Software Projects\CodexProjects` is already trusted in Codex config.
- Reviewed existing `codex_som_vau_financials` and `codex_som_mae_financials` project structure.
- Reviewed Claude workspace-level files and `_project_template` to capture the real design intent.
- Added workspace-level `AGENTS.md`, `CHEATSHEET.txt`, `tasks/TASKS.md`, and `tasks/DECISIONS.md`.
- Created `_project_template/` as the reusable Codex starter project.
- Added repo-based workspace and project memory files so Codex can manage continuity explicitly.

**Next:** Instantiate the next project from `_project_template/` when needed.

### Session 2 — 2026-04-10

**Focus:** Compared Claude workspace session handling with Codex, then upgraded Codex instructions and template files so `start session` and `end session` behave as explicit operating phrases.
- Added workspace archive support.
- Defined a standard session-start and session-close routine in root and template instructions.
- Updated quick references so session recovery relies on repo files first.

**Next:** Use the new session routine consistently and refine it if any friction shows up in real use.
