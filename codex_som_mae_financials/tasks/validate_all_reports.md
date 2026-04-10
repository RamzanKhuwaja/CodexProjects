# Task: Validate All Reports

## Instructions

### Step 1 — Discover all reports to validate

Scan the `reports/` folder. Collect all `.docx` files whose names start with `claude_report_`.
Exclude any files that end in `_validation.docx` or `_summary.docx` — those are outputs, not inputs.

### Step 2 — Validate each report

For each report found, follow the full instructions in `tasks/validate_report.md`, passing the
report filename as input. Run validations **sequentially** — complete each one before moving to
the next.

After each validation, record:

- Report filename
- Path to the `_validation.docx` produced
- Overall result: PASSED / FAILED / PASSED WITH WARNINGS

### Step 3 — Generate the master summary as a .docx

Write a Python script `scripts/generate_validation_temp.py` that produces a styled Word document
saved as `reports/all_reports_validation_summary.docx`.

**Follow the same python-docx styling conventions as the other reports.**

**Required document structure (in this order):**

1. **Title block** — "Validation Summary — All Reports" + date + "Validated by Claude"

2. **Summary callout — the first thing the owner sees:**
   - ALL PASSED → green background `RGBColor(0xD9, 0xEA, 0xD3)`, bold:
     `"✓  ALL REPORTS PASSED — No action required"`
     One sentence: total reports checked, all verified.
   - ANY FAILED → red background `RGBColor(0xFF, 0xCC, 0xCC)`, bold:
     `"✗  X OF Y REPORTS FAILED — See the table below for details"`
     Plain-English bullet list of the failed report names and what went wrong.
   - WARNINGS ONLY → yellow background `RGBColor(0xFF, 0xF2, 0xCC)`, bold:
     `"⚠  ALL PASSED WITH WARNINGS — Review recommended"`
     Brief description of what was flagged.

3. **Results table** with these columns:
   `| Report Name | Validation File | Result | Key Issue (if any) |`
   - Green row background for PASSED, red for FAILED, yellow for WARNINGS.

4. **Patterns section** (only if failures exist):
   Plain-English note on whether the same root cause appears in multiple reports
   (e.g., "All failures trace to a stale data file — re-export from QuickBooks and re-run").

Run the script, then delete it:

```bash
python scripts/generate_validation_temp.py
rm scripts/generate_validation_temp.py
```

## Safety Rules

- Do not modify any original `claude_report_*.docx` files
- Do not modify any source data files in `data/`
- Validation is read-only except for writing `_validation.docx` files and the master summary
