# Task #3 — Spending Deviation Analysis (CRA Risk Review)

**Goal:** Identify spending categories that deviate from prior years on a proportionate basis.
Flag anything that could attract CRA attention on the next tax filing.

## Steps (follow in order every time this task is requested)

### Step 1 — Read all source files fresh

Use the code snippets in CLAUDE.md (Data Files section) to read:

- `data/current/Spirit of Math Schools Markham East_Profit and Loss - Compare YTD for 3 years.xlsx`
- `data/current/Spirit of Math Schools Markham East_Profit and Loss - Aug 2022 to July 2025.xlsx`
- `data/archive/FinancialStatement_2039321 ONTARIO INC_2024-2025.pdf`
- `data/archive/FinancialStatement_2039321 ONTARIO INC_2023-2024.pdf`
- `docs/MAE-background and requirements.docx`

Note the YTD cutoff date from the spreadsheet header — do NOT assume it matches a prior report.

### Step 2 — Read all past Task #3 reports

Glob for `reports/claude_report_deviation_mae_*.docx`, sort by filename ascending. Read each to
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
| HIGH RISK | CRA is likely to flag this — document now and consider reducing |
| MEDIUM RISK | Worth monitoring; prepare documentation in case of audit |
| ACCOUNTING CONSISTENCY | Discuss with bookkeeper — may be a coding or timing issue |
| LOW RISK | Spend is lower than usual — fine, no action needed |

**Key categories to always check (never skip any of these):**

| Account | Category | What to watch for |
| --- | --- | --- |
| 5780 | Student Handouts | Biggest volatility item — any spike is HIGH RISK |
| 6600 | Insurance | Historically low; sudden increases stand out |
| 5710 | Royalty fee | Should stay near 12% of tuition — verify |
| 5606 | Campus Rent | Growth should match lease terms — flag unexplained jumps |
| 6200 series | Marketing & Advertising | Compare to 3% obligation; flag if 6201.1 FTC is missing |
| 6405 series | IT Expenses | Historically large (~$139K/year avg); watch for spikes |
| 5200 series | Payroll (all sub-accounts) | Compare % of tuition; flag if any sub-account disappears |
| 6420 / 6427 | Finance charges / Merchant Services | Usually consistent — flag unusual movement |
| 5100 | Materials | Flag if this account disappears year-over-year |
| 5215 | Employee Benefits | Flag if this account disappears year-over-year |

### Step 4 — Write a new report script

Model the script on `scripts/generate_deviation_report.py` (the Task #3 style template).

- Use the `callout_red()` / `callout_green()` helper functions for HIGH/LOW risk callouts
- Include the 8-column summary table (category, current YTD $, PY YTD $, PY-1 YTD $,
  current % tuition, PY % tuition, change in pp, risk rating)
- Embed all analysed numbers directly into the script
- Use `datetime.date.today().strftime("%B %d, %Y")` for the report date
- Save output to `reports/claude_report_deviation_mae_YYYY-MM-DD.docx` (today's date)

### Step 5 — Run the script

```bash
python scripts/generate_deviation_report.py
```

(or a new versioned copy if the script was updated)

### Step 6 — Update CLAUDE.md

Add the new report to the **Past Reports** list in CLAUDE.md with:
- filename, task number, key flags (HIGH risk items and their % deviation), date

## Safety Rules

- Always compare proportionally (% of tuition) — absolute dollar increases alone are not enough,
  because revenue also grows year over year
- Never suggest reducing a legitimate business expense just to avoid CRA scrutiny —
  only flag and document it
- Never modify files in `data/`
