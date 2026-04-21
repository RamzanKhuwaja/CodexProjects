# ProgressMonitoring Project Plan

## Working Protocol
- Start every session by reviewing **Session Journal**, **Short-Term Priorities**, and **Next Session Checklist**.
- Log new discoveries, decisions, and delivered work in the Session Journal before ending the session.
- Keep this file as the single source for planning; append new notes rather than rewriting history.

## Current State Snapshot
- Automation suite that processes Brightspace exports for Vaughan (VAU) and Markham East (MAE) campuses.
- Core logic lives in `Common/my_utils.py`, with campus-specific entry scripts under `VAU/` and `MAE/`.
- Data ingested from `Data/<Campus>/{Attendance,ClassList,Grades}` and merged into student map CSVs.
- Reports and stakeholder emails produced from consolidated data; outputs saved to `Ready For Printing/<Campus>/`.
- Legacy Selenium IDE `.side` scripts remain under `old-scripts/` as historical references.

## Repository Layout Reference
| Path | Notes |
| --- | --- |
| `Common/my_utils.py` | Shared toolkit: file discovery, CSV normalization, report builders, email/PDF helpers, and campus configuration toggles. |
| `VAU/*.py` & `MAE/*.py` | Thin wrappers that set campus context and invoke utilities for duplicate checks, student map generation, and communications. |
| `Common/MAEClassMap2024-25.csv`, `VAUClassMap2024-25.csv` | Master mappings between class codes and teacher metadata. |
| `Common/MAEStudentMap2024-25.csv`, `VAUStudentMap2024-25.csv` | Consolidated outputs from `GenerateStudentMap`; consumed by downstream reports. |
| `Data/<Campus>/...` | Raw Brightspace data exports (attendance, grades, class lists). |
| `Ready For Printing/<Campus>/` | Final Excel deliverables for staff distribution. |
| `Common/What to do weekly.docx` | Operational guide describing Monday routines, toggle management, and run cadence. |
| `old-scripts/` | Archived Selenium automation artefacts for downloads. |

## Key Components Overview
- `GenerateStudentMap(campus)` builds the master dataset by combining class lists, teacher mappings, attendance histories, and gradebooks.
- Duplicate detection suite (`FindDupStudentsInBSViaClassList`, `FindDupStudentsInBSViaAttendanceGrades`) protects against data duplication in Brightspace exports.
- Health monitors:
  - `FindMissingAttendance` flags stale attendance (`Att Uptodate?` false).
  - `FindStrugglingStudents` selects students below `GRADES_MIN_BAR` (50%).
  - `FindNeedsToAttendMoreRegularly` highlights attendance under `ATTENDANCE_MIN_BAR` (80%).
  - `RemindForBSLogin` tracks logins older than `NOT_LOGGED_IN_SINCE` days (14 by default).
- Notification utilities send HTML emails via Outlook (`win32com.client`) and can generate PDFs via `pdfkit` (requires local wkhtmltopdf installation).

## Data Flow Summary
1. Download Brightspace exports into `Data/<Campus>/...` directories (see operational runbook below).
2. Run campus duplicate checks (`*_1_CheckAllDups.py`) to validate class maps and raw files.
3. Execute `*_2_GenerateStudentMap.py` to refresh the consolidated CSV.
4. Produce stakeholder reports (`*_3` through `*_7` scripts) which depend on the refreshed student map and send emails / save Excel summaries.

## Operational Runbook (from `Common/What to do weekly.docx`)
- **Weekly (Mondays) – Office-only duplicate checks**
  - Clear historical downloads in Dropbox automation directories (attendance, BS login, grades).
  - Use Chrome extension & Selenium IDE suites to download 59 files per category for VAU.
  - Run `VAU_1_CheckAllDups.py` through `VAU_4_StrugglingStudents.py`, toggling `TESTING` as needed; revert `TESTING = True` afterward.
- **Weekly (Mondays) – Teachers + Office**
  - Run `VAU_5_AttendanceMissing.py` with `TESTING = True`; flip to `False` only when ready to alert staff.
- **Bi-weekly (Mondays)**
  - Run `VAU_6_RemindForBSLogin.py` (`TESTING = True; FOR_OFFICE_USE_ONLY = True`) to produce reminders & PDFs.
- **Monthly (Mondays)**
  - Run `VAU_7_NeedsToAttendMoreRegularly.py`, `VAU_8_StrugglingStudents.py`, `VAU_9_HighFlyingStu.py` for office distributions.
- Mirror the same cadence for MAE scripts once VAU pipeline proves stable (existing MAE scripts follow identical naming).

## Configuration & Dependencies
- Global toggles in `Common/my_utils.py`:
  - `DEBUG` switches to sandbox data directories.
  - `TESTING` reroutes all outbound emails to campus lead (`to_email`) and suppresses CCs.
  - `SEND_EMAIL`, `PRINT_REPORT`, `SEND_SUMMARY` gate side-effects.
- Threshold constants (`GRADES_MIN_BAR`, `HIGH_HONOURS_MIN_BAR`, `NOT_LOGGED_IN_SINCE`, `ATTENDANCE_MIN_BAR`) drive filters; adjust here for policy changes.
- Requires Python environment with `pandas`, `numpy`, `openpyxl`, `beautifulsoup4`, `lxml`, `pdfkit`, and Windows Outlook client for email automation.
- `pdfkit` additionally relies on a system-level `wkhtmltopdf` binary.

## Short-Term Priorities (next 1-2 weeks)
1. Design a supervised campus pipeline runner that preserves manual MAE/VAU entry scripts while orchestrating the same underlying steps safely.
2. Confirm current Brightspace export process still matches VAU/MAE class map schemas (validate against Spring 2026 rosters and current export naming).
3. Replace hand-edited runtime globals with safer run-time controls for campus, testing/live mode, and side-effect gating.
4. Add sanity checks in `GenerateStudentMap` to fail fast when expected columns (e.g., `Start Week`, `Parent Email`) are missing or renamed.
5. Align MAE pipeline with VAU updates; ensure both campuses share consistent thresholds and report layouts.

## Long-Term Opportunities
- Parameterize campus metadata (email recipients, thresholds) in external config to reduce code edits during turnover.
- Replace manual Selenium workflows with scripted API/download automation to eliminate Chrome extension reliance.
- Introduce automated test harness (sample CSV fixtures) for regression detection before sending real emails.
- Consider central logging/reporting dashboard for generated Excel outputs and email sends.

## Implementation Roadmap
- **Phase 1 – Stabilization:** address short-term priorities, audit data directories, and lock down toggle usage.
- **Phase 2 – Automation:** script data download process and integrate validation tests.
- **Phase 3 – Productization:** externalize configuration, add logging/monitoring, and document onboarding for new operators.

## Risks & Open Questions
- Brightspace export formats may shift (column renames) without notice; manual review currently required.
- Reliance on Outlook COM automation ties execution to Windows with Outlook configured and running.
- Email-capable steps must never start Outlook automatically; the operator has to open Outlook manually before test or live sends.
- `pdfkit` usage will fail silently without wkhtmltopdf; need confirmation of installation status on run machine.
- Historical Dropbox paths in runbook should be validated against present directory structure.

## Decision Log
| Date | Decision | Context / Link |
| --- | --- | --- |
| _TBD_ | _Add entries as decisions are made._ | |

## Session Journal
_Add a new entry per session (reverse chronological)._

### 2026-04-20 — VAU Pipeline Validation And Live Send
- Ran the supervised VAU pipeline on fresh April 20, 2026 exports after confirming the missing Grade 8 grades export for class `SOMp2508Su1130ETVAU` (`ou=25497`) had been downloaded.
- Completed `start` successfully, then ran the `main` flow for week 30 in `test-send` mode and confirmed the attendance-missing, struggling-students, and principal-summary emails all sent correctly once Outlook was open.
- Re-ran the VAU `main` flow in `production` mode with explicit live-send confirmation so the duplicate-removal office email, teacher-facing emails, and principal summary were all sent to live recipients.
- Confirmed the current VAU run still reports duplicate-export clutter in 11 class buckets and a cross-class student duplicate for Felix Li.
- Confirmed `GenerateStudentMap` completed and refreshed `Common/VAUStudentMap2025-26.csv`, while still warning that `Attendance (%)` is missing for five students.
- Recorded a follow-up reminder to confirm which grade column is being used before relying on grade-based outputs in future sessions.

### 2026-04-17 — Validation And Automation Design Capture
- Verified the moved workspace path by running `VAU_1_CheckAllDups.py` and `MAE_1_CheckAllDups.py` successfully from the project root.
- Confirmed current exports on disk are recent enough for validation work: VAU data dated March 29, 2026 and MAE data dated April 14, 2026.
- Captured user requirements for a phased orchestration layer: keep manual campus scripts available, reuse the existing underlying code, execute one step at a time with outcome review before advancing, halt on key failures, and separate test-send from approved live-send.
- Confirmed Outlook must remain operator-controlled: scripts may connect only to an already running Outlook instance and must never launch Outlook automatically.
- Deferred deeper pipeline execution until duplicate-export cleanup and orchestration rules are formalized.

### 2025-09-18 — Repository Documentation Pass
- Reviewed Python modules in `Common/`, `VAU/`, and `MAE/` to understand data flow and reporting jobs.
- Extracted operational steps from `Common/What to do weekly.docx` and summarized above.
- Established planning structure (this file) for future sessions.
- Next focus: validate current data exports and strengthen student map validation (see Short-Term Priorities #1-2).

## Next Session Checklist
- Read the latest Session Journal entry.
- Confirm which Brightspace/student-grade column is currently being used before relying on grade-driven outputs.
- Review the VAU duplicate-export clutter and decide whether to clean older downloads before the next live run.
- Run an MAE test-send pass for the shared principal-summary step so both campuses are confirmed under the new flow.
- Confirm Outlook is already open before any email-capable test or live send.
- After each work session, append a new entry under "Session Journal" and refresh the checklist so the next pickup is seamless.

