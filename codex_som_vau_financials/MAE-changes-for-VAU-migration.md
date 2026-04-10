# MAE → VAU Migration Guide
**Changes made to som_mae_financials (Mar 11–12, 2026) — apply to som_vau_financials**

---

## What changed and why

Two sessions of work upgraded som_mae_financials. The goals were:
1. Reduce token consumption and run time (was hitting Claude's plan usage limits)
2. Eliminate duplicated code across the 4 report scripts
3. Automate validation (was using 4 separate subagents, each re-reading Excel files)

---

## Change 1 — Shared helper module: `scripts/report_helpers.py`

**What it is:** A single Python file containing all 14 python-docx helper functions that were previously copy-pasted into every report script.

**What was duplicated (now centralised):**
- Constants: `HB`, `CAL`, `BS`
- Document factory: `make_doc()` (creates Document, sets margins)
- Styling: `sbg()`, `sbd()`, `shdr()`, `sdat()`, `ct()`
- Content: `hr()`, `bp()`, `sh()`, `sub_header()`, `note()`
- Callouts: `callout()`, `callout_red_bullets()`, `callout_green_bullets()`, `callout_blue_bullets()`

**How each report script was changed:**
- Deleted the entire `# ---- helpers ----` block (~100 lines)
- Replaced `from docx import Document` + `from docx.shared/oxml/enum import ...` (the helper-only imports) with:
  ```python
  import sys, os
  sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
  from report_helpers import (HB, CAL, BS, make_doc, sbg, sbd, shdr, sdat,
      ct, hr, bp, sh, sub_header, note, callout,
      callout_red_bullets, callout_green_bullets, callout_blue_bullets)
  ```
- Replaced `doc = Document()` + margin-setting loop with `doc = make_doc()`
- Removed `HB`, `CAL`, `BS` constant definitions
- Kept: `from docx.shared import Pt, RGBColor, Inches` and enum imports — these are still needed directly in report body code

**Note on callout function names:** MAE's marketing report uses `callout_blue_bullets` / `callout_red_bullets` (renamed from `callout_blue` / `callout_red`). Check whether VAU scripts use the old names and update them if so.

---

## Change 2 — Single-pass data extraction: `scripts/extract_data.py`

**What it is:** A script that reads all source Excel files once and writes a structured JSON snapshot to `data/extracted/run_data.json`.

**Why:** Previously Claude (and each validation subagent) re-read all Excel files independently. Now they all read from the pre-built JSON.

**What extract_data.py reads:**
- `data/current/Profit and Loss - Compare YTD for 3 years.xlsx` — YTD P&L
- `data/current/Profit and Loss - Aug 2022 to July 2025.xlsx` — 3-year aggregate
- `data/current/Shareholder Advances - this fiscal year.xlsx`
- `data/current/Shareholder Advances - all dates.xlsx`

**JSON structure (top-level keys):**
```
meta: { extracted_at, ytd_cutoff_date, ytd_period_label }
revenue: { ytd_tuition_current, ytd_tuition_prior, ytd_ratio, projected_full_year }
income: { qb_profit, taxes_paid, carbon_rebate, h1_pretax_proxy }
marketing: { total_ytd_current, gap_conservative, gap_projected, line_items: {...} }
expenses: { "5780": {current_ytd, prior_ytd}, "6600": {...}, ... }
shareholder: { ramzan: {opening, closing, transactions}, rezai: {opening, closing, transactions} }
benchmarks_3yr: { tuition_avg, marketing_avg, ftc_avg, it_avg, payroll_avg, insurance_avg }
```

**For VAU:** Write a new `extract_data.py` for VAU — the account codes, shareholder names, and data file names may differ. Use MAE's version as the template. Key differences to check:
- VAU shareholder sub-account codes (MAE uses 2901/2902)
- VAU marketing account codes (MAE uses 6200 series)
- VAU file names — check `data/current/` (they appear already simplified)

**gitignore:** Add `data/extracted/` to `.gitignore` — the JSON is derived/generated and should not be committed.

---

## Change 3 — Automated validation: `scripts/validate_all.py`

**What it is:** A Python script that reads `run_data.json` and opens each of the 4 most recent report `.docx` files, extracts values, and runs 17 assertion checks.

**How it works:**
- Finds the most recent report per task using `glob` + `os.path.getmtime` (excludes `*_validation.docx` and `*-reviewed.docx`)
- Extracts values from tables and paragraph text using python-docx
- `parse_dollar()` handles: `$61,328`, `($8,799)`, `-$8,799`, `−$8,799` (em-dash)
- `extract_embedded_numbers()` finds values embedded in mixed-content cells
- `check_dollar()` with `search_all=True` scans all cells for a value within tolerance
- Prints PASS / FAIL / WARN per check; exits 0 (all pass) or 1 (any fail)
- Writes `reports/validation_summary_YYYY-MM-DD.txt`

**Checks per report (17 total for MAE):**
- Task 1 Marketing: tuition CY, marketing total, gap to annual obligation, projected revenue
- Task 2 Tax: QB profit, H1 pre-tax proxy, installment amounts present, total installments present
- Task 3 Deviation: tuition CY, handouts CY, insurance CY, marketing total CY
- Task 4 Shareholder: Ramzan closing balance, Rezai present, Rezai zero, JE amount present, Hajj present

**For VAU:** Copy MAE's `validate_all.py` and update:
- Account codes in the checks (handouts, insurance — may use different codes)
- Shareholder names (replace "Ramzan"/"Rezai" with VAU shareholder names)
- Specific `number_present` checks for VAU-specific transactions
- The `gap_annual_conservative = 96000.0 - expected_mkt` hardcodes MAE's $96K minimum obligation — VAU will have a different projected revenue and therefore a different minimum obligation

---

## Change 4 — One-command orchestration: `scripts/run_all_reports.py`

**What it is:** A master script that runs the full pipeline in sequence with clear headers and timing.

**Pipeline:**
```
1. Verify source files exist (data/current/*.xlsx)
2. Run extract_data.py  →  writes run_data.json
3. Print data snapshot (YTD cutoff, tuition, marketing, shareholder balances)
4. Run generate_marketing_report.py
5. Run generate_tax_report.py
6. Run generate_deviation_report.py
7. Run generate_shareholder_report.py
8. Run validate_all.py
9. Print completion banner with all 8 output filenames + elapsed time
```

**Forces UTF-8 stdout** at startup — required on Windows to avoid cp1252 encoding errors with em-dashes and special characters.

**For VAU:** Copy MAE's `run_all_reports.py` and update:
- File names in the source file verification step (Step 1)
- The data snapshot print statements (shareholder names, etc.)

---

## Change 5 — Dynamic output filenames

**What changed:** All 4 report scripts now use `datetime.date.today()` for the output filename instead of a hardcoded date string.

```python
import datetime
FILE_DATE = datetime.date.today().strftime("%Y-%m-%d")
DATE_LABEL = datetime.date.today().strftime("%B %-d, %Y")   # "March 11, 2026"
# Windows note: use %#d instead of %-d on Windows:
DATE_LABEL = datetime.date.today().strftime("%B %#d, %Y")
```

Output path example:
```python
out_path = os.path.join(BASE_DIR, "reports", f"claude_report_marketing_vau_{FILE_DATE}.docx")
```

**For VAU:** Check if VAU scripts still have hardcoded dates — they do (the header shows "February 22, 2026"). Apply this change to all 4.

---

## Change 6 — `tasks/run_all_reports.md`

**What it is:** A recipe file added to `tasks/` that instructs Claude how to run the full pipeline when the user says "Regenerate all reports".

**For VAU:** Create a similar `tasks/run_all_reports.md`. The content is largely the same — reference `python scripts/run_all_reports.py` as the one command.

**CLAUDE.md update:** Add the following to the Normal workflow section:
```
After dropping fresh QuickBooks files into `data/current/`, say:
> "Regenerate all reports"

This runs:  python scripts/run_all_reports.py
Which does: extract_data → 4 reports → validate_all → summary
```

---

## What does NOT need changing in VAU

- The overall report structure (Quick Summary / numbered sections / callout boxes / Action Checklist / Bottom Line / Disclaimer) — identical in both projects
- The python-docx styling conventions (fonts, colours, table styles) — identical
- The validation logic approach — copy and adapt, not rewrite
- Git workflow — same rules

---

## Recommended implementation order for VAU

1. Copy `scripts/report_helpers.py` from MAE → VAU verbatim (no changes needed)
2. Migrate all 4 `generate_*.py` scripts to use `report_helpers` (Change 1)
3. Apply dynamic date filenames (Change 5)
4. Write `scripts/extract_data.py` for VAU — use MAE as template, update account codes and shareholder names
5. Write `scripts/validate_all.py` for VAU — use MAE as template, update checks
6. Write `scripts/run_all_reports.py` for VAU — use MAE as template, update file names
7. Add `tasks/run_all_reports.md`
8. Update VAU's `CLAUDE.md` How to Run section
9. Add `.gitignore` excluding `data/extracted/`
10. Run a full test: `python scripts/run_all_reports.py`
11. Commit

---

*Document written Mar 12, 2026. Reference commits: 306e2c6 (full run), b96c6f3 (efficiency improvements).*
