# codex_progress_monitoring — Project Memory

## Purpose

- Automate Brightspace data validation, student-map refreshes, and report generation for the Vaughan (`VAU`) and Markham East (`MAE`) campuses.

## Stable Facts

- Core shared logic lives in `Common/my_utils.py`.
- Campus entry scripts live in `MAE/` and `VAU/`.
- Manual execution of the existing campus scripts must remain supported for both MAE and VAU.
- Raw Brightspace exports are stored in `Data/<Campus>/{Attendance,ClassList,Grades}`.
- Debugging fixtures live in `Data/Debugging/<Campus>/...`.
- Final Excel deliverables are stored in `Ready For Printing/<Campus>/`.
- Legacy Selenium IDE download artifacts live in `old-scripts/`.
- This project was moved into `CodexProjects` on April 17, 2026 and now uses template-style `AGENTS.md`, `memory/`, and `tasks/` files while keeping the existing code layout intact.
- Outlook must never be started automatically by the automation; the operator opens it manually when email-capable steps need to run.

## Workflow Pattern

- Start with `projectplan.md`, then confirm current status in `tasks/TASKS.md`.
- Run duplicate and download checks before rebuilding student maps or generating reports.
- Keep `TESTING`, `SEND_EMAIL`, and related toggles under control before running any script that can notify staff.
- Planned automation should orchestrate the existing campus steps one at a time, inspect outcomes before proceeding, stop on key errors, and use a test-send pass before any approved live send.

## Known Risks Or Recurring Flags

- Path-sensitive code depends on the current top-level layout remaining stable.
- Brightspace export columns can change without notice.
- Outlook COM automation requires a working Windows Outlook profile.
- Duplicate Brightspace downloads can create false duplicate findings and should be cleaned before trusting downstream results.
- PDF generation depends on `wkhtmltopdf` being installed locally.
