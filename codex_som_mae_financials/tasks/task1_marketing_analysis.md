# Task #1 — Marketing/Advertising Spend Analysis

**Goal:** Analyse how much has been spent on marketing and advertising for the current fiscal year,
and how much more needs to be spent to meet the 3% of gross revenue obligation.

## Steps (follow in order every time this task is requested)

### Step 1 — Read all source files fresh

Use the code snippets in CLAUDE.md (Data Files section) to read:

- `data/current/Spirit of Math Schools Markham East_Profit and Loss - Compare YTD for 3 years.xlsx`
- `data/archive/FinancialStatement_2039321 ONTARIO INC_2024-2025.pdf`
- `data/archive/FinancialStatement_2039321 ONTARIO INC_2023-2024.pdf`
- `docs/MAE-background and requirements.docx`

Do this regardless of prior sessions. Note the **exact YTD cutoff date** from the spreadsheet
header row 3 — do NOT assume it matches a prior report.

### Step 2 — Read all past Task #1 reports

Glob for `reports/claude_report_marketing_mae_*.docx`, sort by filename ascending (oldest first,
newest last). Use python-docx to extract text and understand prior findings and trends before
producing a new report.

### Step 3 — Perform the analysis

- Extract current YTD gross tuition (account 4100) from the Excel — column B
- Extract same-period prior year tuition from column C
- Extract full prior-year revenue from the audited financial statement
- Compute YTD-to-annual ratio from prior year: same-period tuition ÷ full-year tuition
- Project current full-year revenue: current YTD tuition ÷ prior-year ratio
- Compute 3% obligation on both the conservative ($3.2M) and projected full-year figures
- Extract all 6200-series marketing accounts (YTD and prior year YTD) from the Excel
- Calculate total YTD marketing spend and gap remaining to meet the obligation
- Compute monthly run rate needed for the remaining months of the fiscal year
- Note year-over-year changes and flag missing items (e.g., FTC account 6201.1 — currently $0)

### Step 4 — Write a new report script

Model the script on `scripts/generate_report.py` (the Task #1 style template).

- Embed all analysed numbers directly into the script
- Use `datetime.date.today().strftime("%B %d, %Y")` for the report date
- Save output to `reports/claude_report_marketing_mae_YYYY-MM-DD.docx` (today's date)

### Step 5 — Run the script

```bash
python scripts/generate_marketing_report.py
```

(or a new versioned copy if the script was updated)

### Step 6 — Update CLAUDE.md

Add the new report to the **Past Reports** list in CLAUDE.md with:
- filename, task number, brief description of key findings, date

## Safety Rules

- Always re-read source files fresh — never carry forward numbers from a prior session
- Never modify files in `data/` or `reports/` (except to add a new report)
- The 3% obligation is on **gross revenue** (account 4100 tuition only), not net income
