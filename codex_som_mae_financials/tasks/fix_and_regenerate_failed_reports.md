# Task: Fix and Regenerate Failed Reports

## Instructions

### Step 1 — Read the master validation summary

Open `reports/all_reports_validation_summary.docx` using python-docx.
Identify all reports marked as FAILED or PASSED WITH WARNINGS.

### Step 2 — Diagnose each failed report

For each failed report, open its `reports/{report_name_stem}_validation.docx` and extract:

- Which metric(s) failed
- The discrepancy amount
- The likely cause identified during validation

Then review the original generation script in `scripts/` and categorize the root cause:

- **Data source problem** — wrong file path, stale QuickBooks export, missing rows
- **Logic/calculation error** — wrong formula, incorrect filter, grouping issue
- **Rounding or formatting issue** — both values are correct but formatted differently
- **Date range mismatch** — YTD cutoff date differs between original and validation

### Step 3 — Attempt a fix

For each report where the root cause is clear:

- Correct the issue in the generation script in `scripts/`
- Add a comment in the code explaining what was wrong and what was changed
- If the root cause is unclear, skip the fix and escalate (see Step 5 — do not guess)

### Step 4 — Regenerate and re-validate

- Run the corrected script to regenerate the report in `reports/`
- Immediately re-run `tasks/validate_report.md` on the regenerated report
- If it now passes → mark as FIXED
- If it still fails → mark as ESCALATED and stop (do not attempt a second fix)

### Step 5 — Generate the fix log as a .docx

Write a Python script `scripts/generate_validation_temp.py` that produces a styled Word document
saved as `reports/fix_log_{YYYY-MM-DD}.docx`.

**Follow the same python-docx styling conventions as the other reports.**

**Required document structure (in this order):**

1. **Title block** — "Fix Log" + date + "Run by Claude"

2. **Summary callout:**
   - ALL FIXED → green background `RGBColor(0xD9, 0xEA, 0xD3)`, bold:
     `"✓  ALL FAILED REPORTS FIXED AND RE-VALIDATED"`
   - SOME ESCALATED → yellow background `RGBColor(0xFF, 0xF2, 0xCC)`, bold:
     `"⚠  X REPORT(S) REQUIRE YOUR ATTENTION — Could not be auto-fixed"`
     Plain-English bullet list of escalated report names and why they could not be fixed.

3. **Fix results table** with these columns:
   `| Report Name | Root Cause | Fix Applied | Re-validation Result | Status |`
   - Green row background for FIXED, red for ESCALATED.

4. **Escalated reports section** (only if any were escalated):
   For each escalated report: plain-English explanation of what was tried, why it failed,
   and what the owner or bookkeeper should do next.

Run the script, then delete it:

```bash
python scripts/generate_validation_temp.py
rm scripts/generate_validation_temp.py
```

### Step 6 — Update the master summary

Re-open `reports/all_reports_validation_summary.docx` and note which reports are now fixed vs.
still escalated. (Regenerate the summary `.docx` if needed to reflect current status.)

## Safety Rules

- Never modify raw source data files in `data/`
- Always re-validate after fixing — never mark a report as fixed without re-running validation
- If a report fails re-validation after one fix attempt, mark it ESCALATED and stop
- If the root cause is unclear, escalate immediately — do not guess
