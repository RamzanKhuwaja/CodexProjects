# CodexProjects Workspace — Permanent Decisions

> Permanent, locked workspace-level decisions live here.
> Project-level decisions live in each project's own `tasks/DECISIONS.md`.

## Workspace Files

- `AGENTS.md` at root is the workspace-level instruction file.
- `CHEATSHEET.txt` at root is allowed as a workspace meta file.

## Session Management

- Workspace sessions are valid for template work, workspace rules, and cross-project concerns.
- Workspace session state lives in `tasks/TASKS.md` and `tasks/DECISIONS.md` at the repo root.
- `start session` and `end session` are the standard session phrases for Codex.
- Workspace session history older than the last 5 entries should move to `tasks/ARCHIVE.md`.

## Memory System

- Workspace memory lives in `memory/` at the repo root.
- Project memory lives in each project's `memory/PROJECT_MEMORY.md`.
- Memory files store stable facts and preferences; `tasks/` files store active state.
- Codex should maintain these files proactively so Ramzan does not need to manage them.
- Repo memory and task files are the primary durable continuity system Codex should rely on between sessions.

## Reporting Style

- Redesigned financial reports should be brief, clear, and readable by a non-accountant.
- Tax outputs should lead with the estimated final bill in plain language before deeper explanation.
- For important changes, show both `% change` and `$ change`.
- Reports should include important categories that are unusually lower than prior years, not just higher ones, when that helps explain the overall picture.

## Project Standard

- New Codex projects should start from `_project_template/`.
- Project-specific instructions should live in `AGENTS.md`.
- `README.md` files are not part of the standard CodexProjects pattern.

## Local Codex Config

- Codex laptop defaults are `approval_policy = "never"` and `sandbox_mode = "danger-full-access"` in `C:\Users\ramza\.codex\config.toml`.
- `C:\Users\ramza\My Software Projects\CodexProjects` is the trusted workspace root for Codex.
