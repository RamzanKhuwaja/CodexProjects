# Task #2 — Corporate Tax Estimation

**Goal:** Estimate total corporate tax payable by July 31, 2026, based on YTD actuals and a
projection of H2 income and expenses. Identify legal tax-reduction strategies.

## Steps (follow in order every time this task is requested)

### Step 1 — Read all source files fresh

Use the code snippets in CLAUDE.md (Data Files section) to read:

- `data/current/Spirit of Math Schools Markham East_Profit and Loss - Compare YTD for 3 years.xlsx`
- `data/archive/FinancialStatement_2039321 ONTARIO INC_2024-2025.pdf`
- `data/archive/FinancialStatement_2039321 ONTARIO INC_2023-2024.pdf`
- `data/archive/2039321 Ontario Inc July 31 2025 T2 Client copy 2025-10-20 (1).pdf`
- `docs/MAE-background and requirements.docx`

Note the YTD cutoff date from the spreadsheet header — do NOT assume it matches a prior report.

### Step 2 — Read all past Task #2 reports

Glob for `reports/claude_report_tax_mae_*.docx`, sort by filename ascending. Read each to
understand prior projections and how they compared to actuals when the year closed.

### Step 3 — Perform the analysis

**H1 income (YTD actuals):**

- Extract current YTD totals from Excel: net income (QuickBooks "Profit" row) and account
  8500 Taxes Paid (tax installments booked as expense)
- H1 pre-tax proxy = QuickBooks Profit + 8500 Taxes Paid − Canada Carbon Rebate (non-taxable)
- Confirm the Canada Carbon Rebate amount from the "Other Income" section of the Excel

**H2 income projection:**

- H2 revenue: project full-year tuition using the YTD ratio (see CLAUDE.md Known Constants),
  then subtract H1 tuition to get H2-only tuition
- H2 wages: apply the H1 year-over-year growth rate to the prior-year H2 wages
  (prior-year H2 wages = audited full-year direct wages − prior-year H1 payroll total)
- H2 royalties: 12% × H2 projected tuition
- H2 rent + materials: use prior-year H2 as baseline
- H2 operating expenses: compare H1 run rates to prior-year full-year; note front-loaded items
  (IT, insurance) vs. evenly spread items (finance charges, office)
- H2 amortization: calculate from net book values in the most recent balance sheet
  (see CLAUDE.md Known Constants for FY2025-26 estimate of ~$13,700)
- H2 remaining marketing obligation: use Task #1 gap figure

**Tax calculation:**

- Sum H1 + H2 estimated income before tax
- Apply Canadian small business corporate tax rates:
  - Federal 9% + Ontario 3.2% = **12.2%** on first $500,000 of active business income
  - Federal 15% + Ontario 11.5% = **26.5%** on income above $500,000
- Apply ~1–2% uplift for Ontario Corporate Minimum Tax if applicable
- Compare to historical effective rates (FY2024-25: 13.7%) as a sanity check
- Note installments already paid (account 8500) and estimate balance owing at July 31

### Step 4 — Identify tax reduction strategies

Always cover these legal levers:

- Complete required marketing spend (mandatory + saves tax)
- Year-end salary/bonus vs. RRSP (only beneficial if RRSP room will actually be used)
- Equipment purchases for CCA (Class 50: 55% declining, half-year rule in year of purchase)
- Outstanding FTC charges (account 6201.1) — check if still payable to franchise
- Year-end expense review (outstanding invoices, prepaid insurance timing)
- Long-term salary/dividend mix optimisation (note: consult Tang & Partners before implementing)

### Step 5 — Write a new report script

Model the script on `scripts/generate_tax_report.py` (the Task #2 style template).

- Embed all analysed numbers directly into the script
- Use `datetime.date.today().strftime("%B %d, %Y")` for the report date
- Save output to `reports/claude_report_tax_mae_YYYY-MM-DD.docx` (today's date)

### Step 6 — Run the script

```bash
python scripts/generate_tax_report.py
```

(or a new versioned copy if the script was updated)

### Step 7 — Update CLAUDE.md

Add the new report to the **Past Reports** list in CLAUDE.md with:
- filename, task number, key findings (estimated tax, effective rate, top strategies), date

## Safety Rules

- Always re-read source files fresh — never carry forward numbers from a prior session
- Tax rates must be confirmed against current CRA rules (rates above are as of FY2025-26)
- All tax reduction strategies suggested must be legal; flag any that require professional advice
- Never modify files in `data/`
