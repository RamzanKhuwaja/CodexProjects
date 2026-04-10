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
**Last session:** 2026-04-10 — copied the newer VAU live-review design into the MAE project, verified the new MAE live packet builder, and pushed the MAE changes to GitHub.
**Next step:** On the next MAE data refresh, use the new live packet workflow in a real session and refine only if real-use friction appears.

## Open Items

- Decide whether existing projects should be retrofitted from `CLAUDE.md` conventions to `AGENTS.md` conventions.
- Decide whether Codex needs a separate workspace memory pattern or should stay file-based only.

## Session Log

### Session 3 — 2026-04-10

**Focus:** Cross-project design transfer from VAU to MAE.

- Read both projects' instruction and task files to compare the newer VAU live-review workflow against the older MAE brief-first prototype.
- Ported the VAU-style live packet, archived-source context, payload-driven renderer, and supporting workflow instructions into `codex_som_mae_financials`.
- Verified the new MAE flow by running `python scripts/build_live_session_packet.py` successfully against the current MAE files.
- Committed and pushed the MAE design-port work to GitHub as `658430e`.

**Next:** Use the new MAE live workflow on the next real data drop, then decide whether any other older project conventions still need harmonizing.

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
