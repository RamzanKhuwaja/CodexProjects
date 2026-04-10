# Task #4 — Shareholder Advances Review

**Goal:** Determine how much each shareholder owes to or is owed by the corporation this fiscal
year. Verify the full multi-year history is balanced and flag any CRA risk items.

## Steps (follow in order every time this task is requested)

### Step 1 — Read all source files fresh

Use openpyxl to read both shareholder advance files:

- `data/current/Spirit of Math Schools Vaughan_Shareholder advances - this fiscal year.xlsx` or `.csv`
- `data/current/Spirit of Math Schools Vaughan_Shareholder Advances - all dates.xlsx` or `.csv`

Also read the most recent reviewed balance sheet for the shareholder advance balances:

- `data/archive/FS_REVIEW_July31_2025_2236262_ONTARIO_INC_o_a_SPIRIT_OF_MATH_SCHOOLS_VAUGHAN.pdf`

### Step 2 — Read all past Task #4 reports

Glob for `reports/claude_report_shareholder_vau_*.docx`, sort by filename ascending. Read each to
understand prior findings and whether flagged items were resolved.

### Step 3 — Perform the analysis

**Shareholders in this company:**

- Account 2901: Ramzan Khuwaja — main active shareholder
- Account 2902: Farah Khuwaja — secondary shareholder
- Account 2900: Main/parent shareholder account (used for structural entries)

**Sign convention:** A negative balance means the shareholder owes the corporation.
A positive balance means the corporation owes the shareholder.

**Current year (this fiscal year file):**

- Extract beginning balance for each shareholder (2900, 2901, 2902)
- Note the opening JE-22 entries on Aug 3, 2025 that reset sub-account balances
- Extract all transactions with: date, type, amount, memo/description, running balance
- Verify: ending balance = beginning balance + sum of all transaction amounts
- Flag personal expenses flowing through the account:
  - Hajj travel payments (Jan 13 and Jan 14, 2026): $10,000 + $7,990 = $17,990
  - February bank transfers (Feb 2 and Feb 4, 2026): $10,000 + $10,000 = $20,000
  - Sep 15, 2025 Cheque 438: -$35,382.54
  - Walmart, PC Express, Cineplex credit card credits (personal expense refunds)
- Explain all journal entries (JE-22, JE-2031-Adj, JE-2032-Adj, JE-21)

**Multi-year history (all dates file):**

- Records go back to 2010; trace the trajectory of balances over the years
- Identify large one-time transactions and whether they were repaid within 1 year
  *(CRA ITA s.15(2): loans from a corporation to a shareholder must be repaid within 1 year
  of the fiscal year-end, or the full amount is added to the shareholder's personal income)*
- Identify recurring journal entries — document what each one is for
- Verify arithmetic: sum of all net changes since inception should equal the current ending balance

**Balance check:**

- Balance sheet at Jul 31, 2025: "Due from shareholders" = $29,373 (shareholders owe corp)
- Confirm this matches the combined balance of all 2900-series accounts at that date

### Step 4 — Key items to always check

Never skip these:

| Item | Why it matters |
| --- | --- |
| Sep 15 cheque ($35,382.54) | Large shareholder-account transaction; confirm support and purpose |
| Hajj travel ($17,990 total) | Must remain clearly documented in the shareholder account, not the P&L |
| Feb 2026 transfers ($20,000) | Purpose unclear; could be personal draws |
| Interest on corp-to-shareholder loans | CRA ITA s.80.4 — prescribed rate interest required |
| JE-22 entries (Aug 3, 2025) | Must be documented by bookkeeper |
| Recurring year-end JEs | Purpose must be documented for each |
| Farah's historical personal expenses | Cancun trip etc. — confirm properly handled |

### Step 5 — Write a new report script

Model the script on `scripts/generate_shareholder_report.py` (the Task #4 style template).

- Use the `callout_blue()` helper function for CRA rules and key findings
- Include the Ramzan transaction table and Farah summary table
- Include the multi-year history table
- Do not hardcode transaction dates, amounts, or sign assumptions that can be read from the source files
- Use `datetime.date.today().strftime("%B %d, %Y")` for the report date
- Save output to `reports/claude_report_shareholder_vau_YYYY-MM-DD.docx` (today's date)
- Run scripts from the `som_vau_financials/` project folder

### Step 6 — Run the script

```bash
python scripts/generate_shareholder_report.py
```

### Step 7 — Update CLAUDE.md

Add the new report to the **Past Reports** list in CLAUDE.md with:
- filename, task number, key findings (balances, flags, CRA risk items), date

## Safety Rules

- Never modify files in `data/` or the original shareholder advance spreadsheets
- All CRA ITA references are informational — always recommend consulting Tang & Partners
  before taking action on loans, interest, or year-end journal entries
- If arithmetic does not balance, flag it clearly and do NOT adjust numbers to make it balance —
  report the discrepancy and recommend the bookkeeper investigate
- If a known transaction cannot be found in the current source files, say so plainly and do not invent a fallback number
- This is VAU (2236262 Ontario Inc.) — shareholders are Ramzan (2901) and Farah (2902),
  NOT Ramzan and Rezai (those are MAE shareholders)
