# Master Task — Regenerate All Reports

**Triggered by:** any phrase like "regenerate all reports", "run all tasks", "fresh run", or "generate all reports"

**Goal:** Generate all 4 analysis reports from fresh QuickBooks data, validate each one, and fix any
issues — all without the user having to manage individual steps.

---

## Steps (follow in order, no skipping)

### Step 1 — Confirm source files exist

Check that all 4 QuickBooks files are present in `data/current/`:

- `Profit and Loss - Compare YTD for 3 years.xlsx`
- `Profit and Loss - Aug 2022 to July 2025.xlsx`
- `Shareholder advances - this fiscal year.xlsx`
- `Shareholder Advances - all dates.xlsx`

If any file is missing, stop and tell the user which file is missing before continuing.

### Step 2 — Run extract_data.py

```bash
python scripts/extract_data.py
```

This reads all 4 source files and writes `data/extracted/run_data.json`.
Check the verification output — confirm tuition, marketing total, and shareholder
balances look reasonable before proceeding.

### Step 3 — Run Task #1 (Marketing Analysis)

Follow all steps in `tasks/task1_marketing_analysis.md` completely.
Then immediately validate the report just produced by following `tasks/validate_report.md`.
If validation finds errors: fix the script, re-run it, re-validate before moving on.
Do not move to Step 4 until Task #1 report passes validation.

### Step 4 — Run Task #2 (Corporate Tax Estimation)

Follow all steps in `tasks/task2_tax_estimation.md` completely.
Then immediately validate the report just produced by following `tasks/validate_report.md`.
If validation finds errors: fix the script, re-run it, re-validate before moving on.
Do not move to Step 5 until Task #2 report passes validation.

### Step 5 — Run Task #3 (Spending Deviation / CRA Risk)

Follow all steps in `tasks/task3_deviation_analysis.md` completely.
Then immediately validate the report just produced by following `tasks/validate_report.md`.
If validation finds errors: fix the script, re-run it, re-validate before moving on.
Do not move to Step 6 until Task #3 report passes validation.

### Step 6 — Run Task #4 (Shareholder Advances)

Follow all steps in `tasks/task4_shareholder_advances.md` completely.
Then immediately validate the report just produced by following `tasks/validate_report.md`.
If validation finds errors: fix the script, re-run it, re-validate before moving on.

### Step 7 — Run the full pipeline script (optional shortcut)

Instead of running Steps 3–6 manually, you can run:

```bash
python scripts/run_all_reports.py
```

This runs extract_data → all 4 reports → validate_all in one command.

### Step 8 — Final summary to the user

Tell the user:

1. All 4 reports have been generated and validated.
2. List each report filename and one sentence of key findings.
3. List any warnings or items that need the user's attention (across all reports).
4. Remind the user to commit the new reports to GitHub if they want to save them.

---

## Rules

- Always run tasks in order (1 → 2 → 3 → 4). Later tasks build on earlier data.
- Never skip validation. Fix errors silently before moving on.
- If a task fails and cannot be fixed automatically, stop and tell the user clearly what is wrong.
- Update CLAUDE.md Past Reports list after all 4 reports are done (one update, not four).
