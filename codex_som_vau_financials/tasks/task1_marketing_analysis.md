# Task #1 — Marketing/Advertising Spend Analysis

**Goal:** Analyse how much has been spent on marketing and advertising for the current fiscal year,
and how much more needs to be spent to meet the 3% of gross revenue obligation.

## Steps (follow in order every time this task is requested)

### Step 1 — Read all source files fresh

Use the code snippets in CLAUDE.md (Data Files section) to read:

- `data/current/Spirit of Math Schools Vaughan_Profit and Loss - Compare YTD for 3 years.xlsx` or `.csv`
- `data/archive/FS_REVIEW_July31_2025_2236262_ONTARIO_INC_o_a_SPIRIT_OF_MATH_SCHOOLS_VAUGHAN.pdf`
- `data/archive/Vaughan_REVIEWReport_FinancialStatements_July31_2024.pdf`
- `docs/VAU-Requirements.docx` or the current requirements doc in `docs/`

Do this regardless of prior sessions. Note the **exact YTD cutoff date** from the spreadsheet
header row 3 — do NOT assume it matches a prior report.

### Step 2 — Read all past Task #1 reports

Glob for `reports/claude_report_marketing_vau_*.docx`, sort by filename ascending (oldest first,
newest last). Use python-docx to extract text and understand prior findings and trends before
producing a new report.

### Step 3 — Perform the analysis

- Extract current YTD gross tuition (account 4100) from the Excel — column B
- Extract same-period prior year tuition from column C
- Extract full prior-year revenue from the reviewed financial statement
- Compute YTD-to-annual ratio from prior year: same-period tuition ÷ full-year tuition
- Project current full-year revenue: current YTD tuition ÷ prior-year ratio
- Compute the 3% obligation from both current YTD tuition and projected full-year tuition
- Extract all 6200-series marketing accounts (YTD and prior year YTD) from the Excel
- Calculate total YTD marketing spend and gap remaining to meet the obligation
- Compute monthly run rate needed for the remaining months of the fiscal year
- Note year-over-year changes and flag missing items (e.g., FTC account 6201.2 — currently $0)
- **Important:** Account 5711 "Service Fee" is NOT marketing spend — do not count it toward the 3% obligation

### Step 4 — Write a new report script

Model the script on `scripts/generate_marketing_report.py` (the Task #1 style template).

- Do not hardcode current-year figures, dates, or projected obligations into the script
- Use `datetime.date.today().strftime("%B %d, %Y")` for the report date
- Save output to `reports/claude_report_marketing_vau_YYYY-MM-DD.docx` (today's date)
- Run scripts from the `som_vau_financials/` project folder so relative paths resolve correctly

### Step 5 — Run the script

```bash
python scripts/generate_marketing_report.py
```

### Step 6 — Update CLAUDE.md

Add the new report to the **Past Reports** list in CLAUDE.md with:
- filename, task number, brief description of key findings, date

## Safety Rules

- Always re-read source files fresh — never carry forward numbers from a prior session
- Never modify files in `data/` or `reports/` (except to add a new report)
- The 3% obligation is on **gross revenue** (account 4100 tuition only), not net income
- This is VAU (2236262 Ontario Inc.) — do not use any MAE data or numbers
