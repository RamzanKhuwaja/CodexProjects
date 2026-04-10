# Task #3 — Spending Deviation Analysis (CRA Risk Review)

**Goal:** Identify spending categories that deviate from prior years on a proportionate basis.
Flag anything that could attract CRA attention on the next tax filing.

## Steps (follow in order every time this task is requested)

### Step 1 — Read all source files fresh

Use the code snippets in CLAUDE.md (Data Files section) to read:

- `data/current/Spirit of Math Schools Vaughan_Profit and Loss - Compare YTD for 3 years.xlsx` or `.csv`
- `data/current/Spirit of Math Schools Vaughan_Profit and Loss - Aug 2022 to July 2025.xlsx` or `.csv`
- `data/archive/FS_REVIEW_July31_2025_2236262_ONTARIO_INC_o_a_SPIRIT_OF_MATH_SCHOOLS_VAUGHAN.pdf`
- `data/archive/Vaughan_REVIEWReport_FinancialStatements_July31_2024.pdf`
- `docs/VAU-Requirements.docx` or the current requirements doc in `docs/`

Note the YTD cutoff date from the spreadsheet header — do NOT assume it matches a prior report.

### Step 2 — Read all past Task #3 reports

Glob for `reports/claude_report_deviation_vau_*.docx`, sort by filename ascending. Read each to
understand what was flagged previously and whether those issues have been resolved.

### Step 3 — Perform the deviation analysis

For each major spending category:

1. Express it as **% of gross tuition** (account 4100) for the current YTD period
2. Compare that % against:
   - Same-period prior year (PY) % of tuition
   - Same-period two years ago (PY-1) % of tuition
   - 3-year annual average from the aggregate P&L file
3. Flag any category where the % shifted by more than ~1 percentage point vs. prior year
4. Also flag any category where the projected full-year run rate deviates significantly from
   the 3-year annual average

**Classify each item as:**

| Risk Level | Meaning |
| --- | --- |
| HIGH RISK | CRA is likely to flag this — document now |
| MEDIUM RISK | Worth monitoring; prepare documentation in case of audit |
| ACCOUNTING CONSISTENCY | Discuss with bookkeeper — may be a coding or timing issue |
| LOW RISK | Spend is lower than usual — fine, no action needed |

**Key categories to always check (never skip any of these):**

| Account | Category | What to watch for |
| --- | --- | --- |
| 5711 | Service Fee — NEW this year | Did NOT exist in prior years; HIGH RISK |
| 5780+5780.1 | Student Handouts & Shipping | Spiked 163% in FY2025-26; HIGH RISK |
| 5710+5710.2 | Royalty Fee (22%) | Should stay near 22% of tuition; verify structure change |
| 5600/5605 | Campus Rent (9135 Keele St) | Should match lease terms; flag unexplained jumps |
| 6200 series | Marketing & Advertising | Compare to 3% obligation; flag if 6201.2 FTC is missing |
| 6405 series | IT Expenses | Dropped dramatically in FY2025-26 vs prior years — flag |
| 5200 series | Payroll (all sub-accounts) | Compare % of tuition |
| 5411 | Tuition Refunds | Elevated in FY2025-26; document reasons |
| 6110 | Professional Fees | Large new item in FY2025-26; document |
| 6600 | Insurance | Rising year-over-year; monitor |
| 5500.1 | Credit Card / Merchant Services | Dropped 81% in FY2025-26; flag the drop |

### Step 4 — Write a new report script

Model the script on `scripts/generate_deviation_report.py` (the Task #3 style template).

- Use the `callout_red()` / `callout_green()` helper functions for HIGH/LOW risk callouts
- Include the 9-column summary table (account, category, CY $, CY %, PY $, PY %, PY-1 $, PY-1 %, Risk)
- Do not hardcode current-year figures, percentages, or risk amounts into the script
- Use `datetime.date.today().strftime("%B %d, %Y")` for the report date
- Save output to `reports/claude_report_deviation_vau_YYYY-MM-DD.docx` (today's date)
- Run scripts from the `som_vau_financials/` project folder

### Step 5 — Run the script

```bash
python scripts/generate_deviation_report.py
```

### Step 6 — Update CLAUDE.md

Add the new report to the **Past Reports** list in CLAUDE.md with:
- filename, task number, key flags (HIGH risk items and their % deviation), date

## Safety Rules

- Always compare proportionally (% of tuition) — absolute dollar increases alone are not enough,
  because revenue also grows year over year
- Never suggest reducing a legitimate business expense just to avoid CRA scrutiny —
  only flag and document it
- This is VAU (2236262 Ontario Inc.) — do not use any MAE benchmarks
- Never modify files in `data/`
