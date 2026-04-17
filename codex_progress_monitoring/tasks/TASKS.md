# codex_progress_monitoring — Task Tracker

> This file tracks current state only — position, open items, and recent session log.
> Permanent decisions live in `DECISIONS.md`. Older sessions live in `ARCHIVE.md`.
>
> **Cleanup (do at each session start or end):** Move sessions older than the last 5 to `ARCHIVE.md`.
>
> **To open a session:** `start session`
> **To close a session:** `end session`

## Current Position

**Status:** Active.
**Last session:** 2026-04-17 — validated the moved workspace with duplicate-check runs and captured requirements for a supervised automation layer.
**Next step:** Draft the supervised runner design, including halt/continue rules, runtime controls for test vs live execution, and a first implementation scope for VAU before extending to MAE.

## Open Items

- Validate the moved workspace paths against the download checks and student-map generation scripts.
- Formalize the orchestration design so manual script runs and automated runs share the same underlying campus code.
- Replace hand-edited globals with safer runtime configuration for campus selection and side-effect control.
- Decide how to store per-run history so future teacher and principal summaries can compare new results to prior runs.
- Add regression tests around the HTML and CSV parsers using anonymized fixtures when the workflow is stable enough.

## Session Log

### Session 3 — 2026-04-17

**Focus:** Resume the project, validate the moved workspace, and capture automation requirements.
- Read the project operating files and resumed from the recorded next step.
- Verified recent Brightspace exports exist on disk: VAU dated 2026-03-29 and MAE dated 2026-04-14.
- Ran `VAU_1_CheckAllDups.py` and `MAE_1_CheckAllDups.py` successfully from the new project root, confirming the moved path logic works.
- Observed real duplicate-export findings in both campuses and Outlook-not-running warnings on notification steps, so no deeper report pipeline was run.
- Captured the planned direction for future work: preserve manual MAE/VAU entry scripts, build a supervised runner above the existing code, never auto-start Outlook, pause on key failures, and support test-send before approved live-send.

**Next:** Write the orchestration design spec and identify the minimum refactor needed to replace manual global toggles with run-time controls.

### Session 1 — 2026-04-17

**Focus:** Moved ProgressMonitoring into `CodexProjects` as `codex_progress_monitoring`.
- Imported the existing code repository history into the workspace project folder.
- Copied the surrounding project data folders (`Data`, `Ready For Printing`, `For Data Entry Person`, `WeekToWeek`) into the new project root.
- Added template-style session, memory, and task management files without forcing a risky codebase reorganization.
- Updated path-sensitive project-root logic so the scripts resolve files from the new folder layout.

**Next:** Verify the moved project from its new workspace path, then remove the original folder once the verification passes.

### Session 2 — 2025-09-18

**Focus:** Parser hardening and wrapper stabilization.
- Hardened `Common/my_utils.py` with new helper utilities such as `warn_once`, `parse_datetime`, and more tolerant column detection.
- Reworked class-list, attendance, and grades ingestion to validate files, normalize identifiers, and emit warnings instead of crashing.
- Upgraded student-map generation and campus entry scripts with early exits and more consistent error handling.
- Verified the codebase compiles via `python -m compileall`.

**Next:** Run pipelines against fresh exports and watch for warnings caused by changing Brightspace fields.
