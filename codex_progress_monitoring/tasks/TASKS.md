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
**Last session:** 2026-04-28 — ran the MAE supervised pipeline for week 31 in both test-send and production modes, validated the new K-4 struggling-student output on MAE, and sent the live MAE teacher and principal emails.
**Next step:** Review whether any K-4 wording or activity-bucket labels should be refined after the MAE validation, then decide whether to clean the recurring duplicate MAE and VAU Brightspace exports before the next live runs.

## Open Items

- Decide whether to clean the MAE duplicate exports now that the live run has succeeded but duplicate warnings still fire for students `42457`, `44458`, and `45962`.
- Decide whether to clean the VAU duplicate exports now that the live run has succeeded but the duplicate-office warning still fires.
- Decide whether any K-4 activity bucket names or teacher/principal wording should be refined now that both campuses have been validated.
- Decide whether to persist per-run history so future teacher and principal summaries can compare new results to prior runs.
- Add regression tests around the HTML and CSV parsers using anonymized fixtures when the workflow is stable enough.

## Session Log

### Session 7 — 2026-04-28

**Focus:** Validate the MAE K-4 struggling-student flow in test mode, then complete the approved live send for week 31.
- Ran `MAE_0_CheckDownloadedFiles.py` successfully and confirmed all 68 MAE attendance, class-list, and grades exports were present before starting the pipeline.
- Ran the supervised MAE `main` flow in `test-send` mode for week 31 after Outlook was opened manually, and confirmed the missing-attendance, struggling-students, and principal-summary steps all completed to the test recipient.
- Observed recurring MAE duplicate-export warnings for students `42457`, `44458`, and `45962` across class-list, attendance, and grades inputs; the pipeline continued by policy.
- Regenerated `Common/MAEStudentMap2025-26.csv` and confirmed `Attendance (%)` is still missing for those same 3 duplicate-linked students.
- Generated the MAE struggling-students workbook at `Ready For Printing/MAE/MAE_StrugglingStudents-April 28, 2026.xlsx` during both the test and production runs.
- Confirmed the production runner requires the explicit `--confirm-live-send` flag, then ran the MAE `main` flow in `production` mode for week 31 and sent the live teacher emails plus the principal summary to Lisa Chiu with CC to `markhameast@spiritofmath.com`.

**Next:** Review whether any K-4 wording or activity-bucket labels need refinement after the MAE validation, then decide whether to clean the recurring MAE and VAU duplicate exports before the next live runs.

### Session 6 — 2026-04-22

**Focus:** Confirm the real Brightspace cumulative-grade source, implement K-4 activity-level detail for struggling-student reporting, and validate the result with VAU test sends.
- Confirmed the current overall grade logic uses `Calculated Final Grade Numerator` and `Calculated Final Grade Denominator`, not `Calculated Final Grade Scheme Symbol`, for struggling-student filtering and related grade-driven outputs.
- Implemented K-4 activity-detail extraction from Brightspace subtotal numerator/denominator columns, normalized them into reporting buckets, and kept the overall `Final Grade` calculation unchanged.
- Extended the struggling-students workbook to enrich `Details` with K-4 concern fields and add `K4_Student_Activity_Details`, `K4_Class_Activity_Summary`, and `K4_Campus_Activity_Summary` sheets when K-4 flagged students are present.
- Updated the VAU and MAE teacher struggling-student email flows so K-4 teachers receive per-student activity detail directly in the email body.
- Added a principal-summary note so the attached workbook explicitly calls out the presence of K-4 activity summaries when they exist.
- Verified the implementation with compile checks, an in-memory VAU smoke test, and a temporary workbook export smoke test.
- Opened Outlook manually and sent VAU teacher test emails plus the VAU principal test email to the test recipient, with the updated workbook generated at `Ready For Printing/VAU/VAU_StrugglingStudents-April 22, 2026.xlsx`.
- Captured user feedback that the K-4 reporting direction looks correct, with any remaining refinement expected to be wording or bucket-label tuning rather than logic changes.

**Next:** Run an MAE test-send pass for struggling-students and principal-summary with the new K-4 detail, then adjust wording or activity-bucket labels only if the reviewed VAU output suggests it.

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
