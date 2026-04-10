# Task: Validate Report

**Input:** report_name (the filename of the report to validate, located in `reports/`)

## Instructions

### Step 1 — Read and understand the report

Open `reports/{report_name}` using python-docx. Read its full contents.
Identify every key metric, dollar total, percentage, and calculated field in the report.

### Step 2 — Identify the original logic

Review the script in `scripts/` that generated this report.
Note: data sources used, date range (YTD cutoff), filters applied, and calculation method.

### Step 3 — Re-validate using an independent method

Read the raw source data directly from `data/current/` or `data/archive/` and recompute
every key figure from scratch — using a different aggregation approach than the original script.

Examples:

- If the original script summed by account code, re-sum by row scanning
- If the original computed a ratio, verify numerator and denominator separately
- Cross-check totals against a different source file where possible (e.g., Excel vs. PDF)

### Step 4 — Compare every key metric

For each metric in the report: record original value, re-computed value, whether they match,
and the discrepancy amount if they do not.

If discrepancies exist, identify the most likely cause:

- Stale data (source file changed since report was generated)
- Rounding difference (both correct, just formatted differently)
- Filter or date range mismatch
- Calculation error in the original script

### Step 5 — Generate the validation report as a .docx

Write a Python script `scripts/generate_validation_temp.py` that produces a styled Word document
saved as `reports/{report_name_without_extension}_validation.docx`.

**The script must follow the same python-docx styling conventions as the other reports:**

- Font: Calibri 11pt body; section headers 13pt bold in blue `RGBColor(0x1F, 0x38, 0x96)`
- Title: 18pt bold blue; subtitle 12pt italic; date line 10pt italic grey
- Tables: `Table Grid` style

**Required document structure (in this order):**

1. **Title block** — "Validation Report: {report_name}" + date + "Validated by Claude"

2. **Summary callout — the first thing the owner sees, large and colored:**
   - ALL PASSED → green background `RGBColor(0xD9, 0xEA, 0xD3)`, bold text:
     `"✓  ALL CHECKS PASSED — No action required"`
     Followed by one plain-English sentence summarizing what was verified.
   - ANY FAILED → red background `RGBColor(0xFF, 0xCC, 0xCC)`, bold text:
     `"✗  X CHECK(S) FAILED — Items below need your attention"`
     Followed by a plain-English bullet list of exactly what failed and why it matters.
   - WARNINGS ONLY → yellow background `RGBColor(0xFF, 0xF2, 0xCC)`, bold text:
     `"⚠  PASSED WITH WARNINGS — Review recommended"`
     Followed by a plain-English description of what was flagged.

3. **Validation method** — one short paragraph explaining what data was read and how
   the independent re-check was done.

4. **Results table** with these columns:
   `| Metric | Original Value | Validated Value | Match? | Discrepancy | Notes |`
   - Use green cell background for rows that match, red for rows that do not.

5. **Findings section** (only if failures or warnings exist):
   - Plain-English explanation of each discrepancy
   - Likely cause
   - Suggested fix or next step

Run the script:

```bash
python scripts/generate_validation_temp.py
```

Then delete the temp script:

```bash
rm scripts/generate_validation_temp.py
```

## Safety Rules

- Do not modify any original report files in `reports/`
- Do not modify any source data files in `data/`
- If arithmetic discrepancies are found, report them — never adjust numbers to make them balance
- The temp script is always deleted after running; only the `.docx` output is kept
