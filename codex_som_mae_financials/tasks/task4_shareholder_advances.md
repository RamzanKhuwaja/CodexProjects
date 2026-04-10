# Task #4 — Shareholder Advances Review

**Goal:** Determine how much each shareholder owes to or is owed by the corporation this fiscal
year. Verify the full multi-year history is balanced and flag any CRA risk items.

## Steps (follow in order every time this task is requested)

### Step 1 — Read all source files fresh

Use openpyxl to read both shareholder advance files:

- `data/current/Spirit of Math Schools Markham East_Shareholder Advances - this fiscal year.xlsx`
- `data/current/Spirit of Math Schools Markham East_Shareholder Advances - all dates.xlsx`

Also read the most recent audited balance sheet for the shareholder advance balances:

- `data/archive/FinancialStatement_2039321 ONTARIO INC_2024-2025.pdf`

### Step 2 — Read all past Task #4 reports

Glob for `reports/claude_report_shareholder_mae_*.docx`, sort by filename ascending. Read each to
understand prior findings and whether flagged items were resolved.

### Step 3 — Perform the analysis

**Current year (this fiscal year file):**

- Extract beginning balance for each shareholder:
  - Ramzan (account 2901)
  - Rezai (account 2902)
- Extract all transactions with: date, type, amount, memo/description, running balance
- Verify: ending balance = beginning balance + sum of all transaction amounts
- Note which transactions are marked **Uncleared** (not yet bank-reconciled)
- Flag personal expenses flowing through the account (e.g., travel, shopping, personal payments)
- Identify any transfers from/to related companies and document the company name and purpose

**Multi-year history (all dates file):**

- Build a year-end balance table for every fiscal year since records began
- Compute net change per fiscal year per shareholder
- Identify large one-time transactions and check whether they were repaid within 1 year
  *(CRA ITA s.15(2): loans from a corporation to a shareholder must be repaid within 1 year
  of the fiscal year-end, or the full amount is added to the shareholder's personal income)*
- Identify recurring journal entries — document what each one is for
- Verify arithmetic: sum of all net changes since inception should equal the current ending balance

**Balance check:**

- Confirm the all-time running total for each shareholder matches the current balance
- Flag any fiscal years with unusually large balance swings
- Note fiscal years where the balance was zero (fully settled) as reference points

### Step 4 — Key items to always check

Never skip these:

| Item | Why it matters |
| --- | --- |
| Personal expenses paid by corp and coded to shareholder advance | Must be documented; could be deemed a taxable benefit |
| Shareholder loans outstanding at fiscal year-end | Must be repaid within 1 year of FY-end (CRA ITA s.15(2)) |
| Interest charged on loans from corp to shareholder | CRA ITA s.80.4 — prescribed rate interest required |
| Recurring year-end journal entries ($3,500 + $4,950 + $1,070.37) | Purpose must be documented for each |
| Transfers from related companies | Identify the company; document the business purpose |
| Uncleared transactions | Confirm with bookkeeper that these will clear |

### Step 5 — Write a new report script

Model the script on `scripts/generate_shareholder_report.py` (the Task #4 style template).

- Use the `callout_blue()` helper function for key findings and warnings
- Include the multi-year balance history table (one row per fiscal year)
- Embed all analysed numbers directly into the script
- Use `datetime.date.today().strftime("%B %d, %Y")` for the report date
- Save output to `reports/claude_report_shareholder_mae_YYYY-MM-DD.docx` (today's date)

### Step 6 — Run the script

```bash
python scripts/generate_shareholder_report.py
```

(or a new versioned copy if the script was updated)

### Step 7 — Update CLAUDE.md

Add the new report to the **Past Reports** list in CLAUDE.md with:
- filename, task number, key findings (balances, flags, CRA risk items), date

## Safety Rules

- Never modify files in `data/` or the original shareholder advance spreadsheets
- All CRA ITA references are informational — always recommend consulting Tang & Partners
  before taking action on loans, interest, or year-end journal entries
- If arithmetic does not balance, flag it clearly and do NOT adjust numbers to make it balance —
  report the discrepancy and recommend the bookkeeper investigate
