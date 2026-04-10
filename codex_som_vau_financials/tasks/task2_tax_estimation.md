# Task #2 — Corporate Tax Estimation

**Goal:** Estimate total corporate tax payable by the current fiscal year-end from YTD actuals
and the archived FY2024-25 tax/reporting files. Identify legal tax-reduction strategies.

## Steps (follow in order every time this task is requested)

### Step 1 — Read all source files fresh

Use the code snippets in CLAUDE.md or the shared extraction helpers to read:

- `data/current/Spirit of Math Schools Vaughan_Profit and Loss - Compare YTD for 3 years.xlsx` or `.csv`
- `data/archive/FS_REVIEW_July31_2025_2236262_ONTARIO_INC_o_a_SPIRIT_OF_MATH_SCHOOLS_VAUGHAN.pdf`
- `data/archive/Vaughan_REVIEWReport_FinancialStatements_July31_2024.pdf`
- `data/archive/2236262_Ontario_Inc_2025_T2_Client_copy_2025-10-28.pdf`
- `docs/VAU-Requirements.docx` or the current requirements doc in `docs/`

Note the YTD cutoff date from the spreadsheet header — do NOT assume it matches a prior report.

### Step 2 — Read all past Task #2 reports

Glob for `reports/claude_report_tax_vau_*.docx`, sort by filename ascending. Read each to
understand prior projections and how they compared to actuals when the year closed.

### Step 3 — Perform the analysis

**H1 income (YTD actuals):**

- Extract current YTD totals from Excel: net income (QuickBooks "Profit" row) and account
  6935 Corporate Tax Expense (last year's tax installments booked as expense)
- H1 pre-tax proxy = QuickBooks Profit + 6935 Corporate Tax Expense − Canada Carbon Rebate (non-taxable)
- Confirm the Canada Carbon Rebate amount from the "Other Income" section of the Excel

**Projection method:**

- Start from the current YTD pre-tax proxy.
- Compare that number to the same-cutoff prior-year QuickBooks pre-tax proxy.
- Compare the prior-year same-cutoff proxy to the actual prior-year taxable income from the T2.
- Use that conversion as the main planning estimate unless current-year facts clearly show a major break from last year.
- Cross-check the answer against the reviewed financial statements and the current QuickBooks pattern.
- If you choose a different method, explain why the prior-year same-cutoff method is not reliable enough.

**Tax calculation:**

- Sum H1 + H2 estimated income before tax
- Apply Canadian small business corporate tax rates using the current project rule for VAU:
  - **12.2%** on active business income within the confirmed SBD limit
  - **26.5%** on income above that limit
- Note: IG Wealth Management portfolio triggers Part IV tax (~$3,795 last year) on investment income
- Apply dividend refund estimate (~$5,337 last year) to reduce net tax
- Compare to historical effective rates (FY2024-25: 21.83% overall, 12.94% Part I only) as a sanity check
- Do NOT state installment status unless a provided source file explicitly shows it

### Step 4 — Identify tax reduction strategies

Always cover these legal levers:

- Complete required marketing spend (mandatory + saves tax)
- Year-end salary/bonus vs. RRSP (only beneficial if RRSP room will actually be used)
- Equipment purchases for CCA (Class 50: 55% declining, half-year rule in year of purchase)
- Outstanding FTC charges (account 6201.2) — check if still payable to franchise
- Year-end expense review (outstanding invoices, prepaid insurance timing)
- Clarify Service Fee (5711) deductibility with Tang & Partners
- Long-term salary/dividend mix optimisation (note: consult Tang & Partners before implementing)

### Step 5 — Write a new report script

Model the script on `scripts/generate_tax_report.py` (the Task #2 style template).

- Do not hardcode current-year estimates, installment statuses, or fiscal-year labels in the script
- Use `datetime.date.today().strftime("%B %d, %Y")` for the report date
- Save output to `reports/claude_report_tax_vau_YYYY-MM-DD.docx` (today's date)
- Run scripts from the `som_vau_financials/` project folder

### Step 6 — Run the script

```bash
python scripts/generate_tax_report.py
```

### Step 7 — Update CLAUDE.md

Add the new report to the **Past Reports** list in CLAUDE.md with:
- filename, task number, key findings (estimated tax, effective rate, top strategies), date

## Safety Rules

- Always re-read source files fresh — never carry forward numbers from a prior session
- Tax rates and limits must match the current project evidence and requirements files
- All tax reduction strategies suggested must be legal; flag any that require professional advice
- This is VAU (2236262 Ontario Inc.) — the royalty rate is 22%, NOT 12% (that is MAE)
- Never modify files in `data/`
