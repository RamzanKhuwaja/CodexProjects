# codex_progress_monitoring — Permanent Decisions

> Permanent, locked decisions live here. Never put decisions in TASKS.md.

## Architecture

- The project keeps its existing top-level code layout (`Common/`, `MAE/`, `VAU/`, `old-scripts/`) instead of being refactored into `scripts/`, because the current code is path-sensitive and the move should minimize breakage.
- `projectplan.md` is the main project reference document.
- Template-style session management for this project lives in `AGENTS.md`, `memory/`, and `tasks/`.

## Data And Output

- Existing operational folders remain named `Data/`, `Ready For Printing/`, `For Data Entry Person/`, and `WeekToWeek/`.
- `Ready For Printing/` remains the active report output location for the existing workflow.

## Workflow Automation

- Manual execution of the existing MAE and VAU entry scripts remains a supported operating mode.
- Any future automation layer should orchestrate the existing campus scripts/shared code rather than replace the current pipeline logic wholesale.
- Outlook must never be started automatically by project automation; email-capable steps may run only when the operator has opened Outlook manually.
- Email-capable workflow steps should support a test-send phase before any approved live send to teachers or other stakeholders.

## Git

- Historical code commits are preserved by importing the old code repository into the `CodexProjects` workspace history under `codex_progress_monitoring/`.
- Cache artifacts such as `__pycache__/` and `*.pyc` are not part of the new workspace tracking baseline.
