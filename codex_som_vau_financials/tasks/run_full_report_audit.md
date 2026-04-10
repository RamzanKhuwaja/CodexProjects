# Task: Full Report Audit (Validate → Fix → Re-validate)

**Goal:** Run a complete audit cycle: validate all reports, fix any that failed, and confirm
all reports pass before finishing.

## Instructions

### Step 1 — Validate all reports

Follow `tasks/validate_all_reports.md` completely. This will:
- Validate every `claude_report_*.docx` in `reports/`
- Generate individual `_validation.docx` for each
- Generate a master `all_reports_validation_summary.docx`

### Step 2 — If all reports pass

Report to the owner: "All X reports passed validation. No fixes required."
Provide the path to `reports/all_reports_validation_summary.docx`.

### Step 3 — If any reports fail

For each failed report, follow `tasks/fix_and_regenerate_failed_reports.md`.
After fixing, re-validate just that report using `tasks/validate_report.md`.

### Step 4 — Repeat until all pass

Continue the fix → re-validate cycle until every report passes (or until a root cause is
found that requires owner input, in which case document and pause).

### Step 5 — Final summary

Regenerate `reports/all_reports_validation_summary.docx` to reflect the final state of all reports.

## Safety Rules

- Never mark a report as "passed" if discrepancies remain unexplained
- Never modify source data in `data/` as a "fix" — only fix the scripts
- Maximum 2 fix attempts per report before escalating to the owner
