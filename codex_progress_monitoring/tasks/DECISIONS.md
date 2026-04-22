# codex_progress_monitoring — Permanent Decisions

> Permanent, locked decisions live here. Never put decisions in TASKS.md.

## Architecture

- The project keeps its existing top-level code layout (`Common/`, `MAE/`, `VAU/`, `old-scripts/`) instead of being refactored into `scripts/`, because the current code is path-sensitive and the move should minimize breakage.
- `projectplan.md` is the main project reference document.
- Template-style session management for this project lives in `AGENTS.md`, `memory/`, and `tasks/`.

## Data And Output

- Existing operational folders remain named `Data/`, `Ready For Printing/`, `For Data Entry Person/`, and `WeekToWeek/`.
- `Ready For Printing/` remains the active report output location for the existing workflow.
- Overall grade-driven reporting logic uses Brightspace `Calculated Final Grade Numerator` and `Calculated Final Grade Denominator`, not `Calculated Final Grade Scheme Symbol`.
- K-4 struggling-student reporting keeps the same overall final-grade trigger and supplements teacher/principal outputs with normalized activity-detail summaries derived from Brightspace subtotal numerator/denominator fields.

## Workflow Automation

- Manual execution of the existing MAE and VAU entry scripts remains a supported operating mode.
- Any future automation layer should orchestrate the existing campus scripts/shared code rather than replace the current pipeline logic wholesale.
- Unless explicitly requested otherwise, workflow and presentation changes should be implemented consistently for both VAU and MAE.
- Outlook must never be started automatically by project automation; email-capable steps may run only when the operator has opened Outlook manually.
- Email-capable workflow steps should support a test-send phase before any approved live send to teachers or other stakeholders.
- Production principal-summary emails use confirmed campus-specific recipients:
  - VAU: To Angela Armstrong (`aarmstrong@spiritofmath.com`), CC `vaughan@spiritofmath.com`
  - MAE: To Lisa Chiu (`lisachiu@spiritofmath.com`), CC `markhameast@spiritofmath.com`
- On `start session`, the assistant should brief Ramzan on status and then wait for explicit direction before doing substantive project work.
- When starting a campus pipeline, the assistant should first run `*_0_CheckDownloadedFiles`; only after that check should it ask which `THIS_WEEK_NUM` value to use for the remaining pipeline steps.

## Git

- Historical code commits are preserved by importing the old code repository into the `CodexProjects` workspace history under `codex_progress_monitoring/`.
- Cache artifacts such as `__pycache__/` and `*.pyc` are not part of the new workspace tracking baseline.
