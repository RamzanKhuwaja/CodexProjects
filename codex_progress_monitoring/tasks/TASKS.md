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
**Last session:** 2025-09-18 — hardened parsers and wrappers, improved validation, and verified the code compiles.
**Next step:** Run the VAU and MAE pipelines against fresh Brightspace exports from the moved workspace location and confirm the updated parsing heuristics still behave correctly.

## Open Items

- Validate the moved workspace paths against the download checks and student-map generation scripts.
- Decide whether any new output should move into `output/` or whether `Ready For Printing/` remains the long-term report location.
- Add regression tests around the HTML and CSV parsers using anonymized fixtures when the workflow is stable enough.

## Session Log

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
