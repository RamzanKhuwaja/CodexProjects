# Supervised Runner Design

## Goal

- Add a safer orchestration layer without replacing the existing MAE and VAU entry scripts.
- Keep the current manual wrappers as the supported execution path.
- Run the pipeline one wrapper at a time, classify the result, and stop only on real technical blockers.

## Implemented Flows

- `start`: runs `*_0_CheckDownloadedFiles`
- `main`: runs `*_1_CheckAllDups`, `*_2_GenerateStudentMap`, `*_3_AttendanceMissing`, `*_4_StrugglingStudents`, `*_4_5_PrincipalSummary`
- `optional`: runs `*_5_RemindForBSLogin`, `*_6_HighHonoursStudents`, `*_7_NeedsToAttendMoreRegularly`
- `start` does not require a week number
- `main`, `optional`, and any single step after `*_0` require an explicit `--week` value

## Implemented Modes

- `silent-test`
  - `TESTING=True`
  - `SEND_EMAIL=False`
- `test-send`
  - `TESTING=True`
  - `SEND_EMAIL=True`
- `production`
  - `TESTING=False`
  - `SEND_EMAIL=True`
  - requires explicit live-send confirmation

## Status Policy

- `clear`
  - step ran successfully and found nothing notable
- `warning_continue`
  - step ran successfully but found duplicates or student findings; pipeline continues
- `blocked`
  - step could not complete properly or required output/action failed
- `failed`
  - wrapper crashed or raised an unhandled exception

## Continue Rules

- Continue automatically on `clear`
- Continue automatically on `warning_continue`
- Stop on `blocked`
- Stop on `failed`

## Duplicate Policy

- Duplicate findings are not business blockers for this project.
- `*_1_CheckAllDups` reports duplicate findings as `warning_continue`.
- The main pipeline continues even when duplicate findings exist.

## Outlook Policy

- Outlook status is reported during the `start` flow.
- Outlook status is also reported before email-capable teacher-facing steps.
- Outlook is informational when email is disabled.
- Email-capable steps become `blocked` only if the wrapper cannot complete the intended send/export work.
- Automation never launches Outlook automatically.

## Runtime Control Strategy

- A shared context manager in `Common/my_utils.py` temporarily overrides:
  - campus
  - `TESTING`
  - `SEND_EMAIL`
  - `PRINT_REPORT`
  - `THIS_WEEK_NUM`
  - test recipient overrides
- Existing wrappers still call `set_campus_info(...)`, so manual scripts and supervised runs continue to share the same underlying logic.
- `SEND_EMAIL=False` is treated as a clean side-effect skip instead of a failure.

## Example Commands

```powershell
python -m Common.supervised_runner --campus VAU --list-steps
python -m Common.supervised_runner --campus MAE --list-modes
python -m Common.supervised_runner --campus VAU --flow start --mode silent-test
python -m Common.supervised_runner --campus VAU --flow main --mode silent-test --week 30
python -m Common.supervised_runner --campus MAE --flow optional --mode test-send --week 30
python -m Common.supervised_runner --campus VAU --flow main --mode production --confirm-live-send --week 30
```
