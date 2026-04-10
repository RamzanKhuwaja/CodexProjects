# Task: Fix and Regenerate Failed Reports

**Input:** One or more report filenames that failed validation (from `tasks/validate_all_reports.md`
or `tasks/validate_report.md`).

## Instructions

### Step 1 — Read the validation report(s)

For each failed report, open its corresponding `_validation.docx` file in `reports/`.
Understand exactly which metrics failed, and what the discrepancy was.

### Step 2 — Diagnose the root cause

Check the generating script in `scripts/` against the raw source data in `data/current/` and
`data/archive/`. Common causes:

- Stale data: source Excel or PDF was updated but the script still has old numbers
- Calculation error: formula in script is wrong
- Data file changed: QuickBooks re-export changed an account code or structure
- Rounding: script uses different rounding than the source

### Step 3 — Fix the generating script

Update the relevant script in `scripts/` with corrected numbers or logic.

Do NOT modify original reports in `reports/` directly — always re-run the script to regenerate.

### Step 4 — Regenerate the report

```bash
python scripts/generate_<topic>_report.py
```

Run from the `som_vau_financials/` project folder.

### Step 5 — Re-validate

Follow `tasks/validate_report.md` again on the newly generated report to confirm the fixes work.

### Step 6 — Update CLAUDE.md

If the regenerated report replaces the prior version, update the Past Reports list in CLAUDE.md
with the new filename and date.

## Safety Rules

- Never delete old reports — new reports have a new date in the filename so both are preserved
- Never modify data files in `data/`
- If the root cause cannot be identified, flag it for the owner and do not guess
