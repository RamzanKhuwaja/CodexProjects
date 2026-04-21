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
**Last session:** 2026-04-20 — validated the VAU supervised pipeline end to end on fresh exports, completed both test-send and production runs for week 30, and resent the duplicate-removal email to the office in production mode.
**Next step:** Before the next grade-driven review or pipeline run, confirm which Brightspace/student-grade column is currently being used; then decide whether to clean the VAU duplicate exports or proceed to an MAE test-send pass for the shared principal-summary flow.

## Open Items

- Run an MAE test-send pass for the principal-summary step so both campuses are visually confirmed under the new shared formatting.
- Confirm which Brightspace/student-grade column the current pipeline logic is using before relying on future grade-based outputs.
- Decide whether to clean the VAU duplicate exports now that the live run has succeeded but the duplicate-office warning still fires.
- Decide whether to persist per-run history so future teacher and principal summaries can compare new results to prior runs.
- Add regression tests around the HTML and CSV parsers using anonymized fixtures when the workflow is stable enough.

## Session Log

### Session 5 — 2026-04-20

**Focus:** Run the refreshed VAU pipeline on current exports, validate test-send behavior, then complete the approved production send.
- Ran `VAU` step `0_CheckDownloadedFiles`, identified the initially missing Grade 8 grades export, traced it to class `SOMp2508Su1130ETVAU` (`ou=25497`), and re-ran step `0` successfully after the missing export was downloaded.
- Ran the VAU `main` flow in `test-send` mode for week 30 after Outlook was opened and confirmed the attendance-missing, struggling-students, and principal-summary steps completed successfully to the test recipient.
- Observed duplicate-export clutter across 11 VAU class buckets and a cross-class duplicate for Felix Li during step `1`; the pipeline continued by policy.
- Regenerated `Common/VAUStudentMap2025-26.csv` and confirmed the warning that `Attendance (%)` is still missing for students `47011`, `47012`, `47299`, `48147`, and `48370`.
- Ran the VAU `main` flow in `production` mode for week 30 with explicit live-send confirmation; the duplicate-removal office email, live teacher emails, and principal-summary email all completed successfully.
- Captured a recurring reminder for future sessions: confirm which Brightspace/student-grade column is being used before relying on grade-based outputs.

**Next:** Before the next grade-driven review or pipeline run, confirm the grade column choice, then decide whether to clean VAU duplicate exports or move on to an MAE test-send pass.

### Session 4 — 2026-04-18

**Focus:** Implement the supervised pipeline design, unify office/principal email presentation, and validate VAU test-send behavior.
- Added `Common/supervised_runner.py` to run `start`, `main`, and `optional` flows one step at a time for both VAU and MAE, with explicit mode control and per-step statuses.
- Added runtime overrides in `Common/my_utils.py` so campus, test/live mode, email sending, printing, and `THIS_WEEK_NUM` can be controlled without hand-editing globals.
- Enforced the interaction rule that `*_0_CheckDownloadedFiles` runs first and the week number is requested only after that step passes.
- Changed duplicate handling so `*_1_CheckAllDups` reports warnings but does not block the primary pipeline, and unified the duplicate office email format for both campuses.
- Added a new shared post-`*_4` principal-summary step for both campuses, with a formatted workbook attachment and a campus-specific production recipient model.
- Improved the struggling-students workbook formatting for both campuses by styling the `Details` and `Summary` sheets, sorting the summary by `Total Students`, and making the `TOTAL` row stand out.
- Sent successful VAU test emails for the duplicate cleanup notice and the new principal-summary step, both routed to the test recipient.
- Recorded the production principal recipients:
  - VAU: Angela Armstrong (`aarmstrong@spiritofmath.com`), CC `vaughan@spiritofmath.com`
  - MAE: Lisa Chiu (`lisachiu@spiritofmath.com`), CC `markhameast@spiritofmath.com`

**Next:** Use fresh VAU exports tomorrow to run the supervised flow from `run pipeline for VAU`, confirm the week number after step `0`, and validate the updated main pipeline on current data.

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
