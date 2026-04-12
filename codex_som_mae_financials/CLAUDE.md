# som_mae_financials

## Communication Style — IMPORTANT

**Always write reports and explanations in plain, simple English.**
The owner has no financial or accounting background. Follow these rules in every report and response:

- Never use jargon without explaining it. If you must use a financial term (e.g., "CCA"), explain it
  in one plain-English sentence immediately after, e.g. "CCA (Capital Cost Allowance) — this is the
  tax deduction the government lets you take each year for equipment and improvements you've bought."
- Use short sentences. Avoid passive voice. Say "you owe" not "a tax liability is incurred."
- After any calculation, add a "What this means for you" sentence in plain language.
- Analogies are encouraged where helpful.

---

## Background Doc Sync Protocol

**When the user says anything like "I updated the background doc" or "I added something to the requirements doc", always do the following — in this order — before anything else:**

1. Read `docs/MAE-background and requirements.docx` using python-docx.
2. Compare what you read against the current CLAUDE.md. Look for new tasks, changed business rules,
   new data sources, or new financial constants.
3. Tell the user in plain English what you found — what is new or changed, and whether CLAUDE.md needs updating.
4. If CLAUDE.md needs updating, propose the specific changes and ask for confirmation before making them.

---

## Vault Index

A SQLite database indexes every file on Ramzan's Google Drive (~17,000 files).
Use it to find MAE financial documents without scanning Drive directly.
**Relevant bucket:** `SpiritOfMathSchoolsMarkhamEast Bucket`.
Full guide: `shared_second_brain/VAULT_GUIDE.md`.

```python
import sqlite3
DB_PATH = r'C:\Users\ramza\My Software Projects\ClaudeCodeProjects\shared_second_brain\data\db\vault.db'
conn = sqlite3.connect(DB_PATH)
results = conn.execute(
    """SELECT v.file_path, v.file_name
       FROM vault_notes v JOIN vault_notes_fts ON v.id = vault_notes_fts.rowid
       WHERE vault_notes_fts MATCH ? AND v.bucket = 'SpiritOfMathSchoolsMarkhamEast Bucket'
       ORDER BY rank LIMIT 10""",
    ('financial report 2025',)
).fetchall()
conn.close()
```

**FTS5 note:** No hyphens in MATCH queries — `'financial report'` not `'financial-report'`.

---

## Purpose

Financial analysis tools and reports for Spirit of Math Schools Markham East (2039321 Ontario Inc.).
A Spirit of Math franchise offering after-school math classes (SK–Grade 11).
Fiscal year: August 1 – July 31.

Key obligations:

- 12% royalty on all gross revenue
- 3% of gross revenue must be spent on local marketing

Financial constants (audited figures, CCA, 3-year benchmarks, installment schedule): see `docs/constants.md`.

---

## Session Management

Use `start session` at the start of every session and `end session` at the end.

| File | Purpose |
| --- | --- |
| `tasks/TASKS.md` | Current state: position, open items, last 5 sessions |
| `tasks/DECISIONS.md` | Permanent locked decisions |
| `tasks/ARCHIVE.md` | Session history older than last 5 |

---

## Workspace & Git Rules

- Do not create or maintain `README.md` files.
- Generated code and helper scripts go in `scripts/`.
- Input and reference files go in `data/current/`. Superseded versions go in `data/archive/`.
- Generated artifacts (reports, exports) go in `output/`. Existing reports remain in `reports/`.

**DO commit to GitHub:** everything in `docs/`, `data/`, `scripts/`.

**DO NOT commit:** non-Office generated files in `output/` or `reports/` (logs, CSVs, `.txt` files).

**Office files are always committed** regardless of folder: `.docx`, `.xlsx`, `.pptx`, `.pdf`.

**If a `.gitignore` exists:** ensure it does NOT exclude `docs/` or Office/PDF file types.
In `output/` and `reports/`, ignore non-Office files only.

---

## Folder Structure

```text
som_mae_financials/
├── CLAUDE.md                    ← Claude's instruction manual (this file)
├── data/
│   ├── current/                 ← Refreshed from QuickBooks periodically (Excel/CSV exports)
│   └── archive/                 ← Never changes (audited PDFs, filed T2 tax returns)
├── docs/                        ← Background context, requirements, constants
├── scripts/                     ← Python scripts
├── reports/                     ← All generated output files (.docx)
└── tasks/                       ← Task recipe files and session management
```

---

## Data Files

| File | Location | Updates | Use |
| --- | --- | --- | --- |
| `MAE-background and requirements.docx` | `docs/` | Rarely | Business context and task list |
| `Profit and Loss - Compare YTD for 3 years.xlsx` | `data/current/` | Each run | Current-year YTD P&L vs. 2 prior years |
| `Profit and Loss - Aug 2022 to July 2025.xlsx` | `data/current/` | Annually | 3-year aggregate full P&L |
| `Shareholder Advances - this fiscal year.xlsx` | `data/current/` | Each run | Current-year shareholder advance transactions |
| `Shareholder Advances - all dates.xlsx` | `data/current/` | Each run | Full multi-year shareholder advance history |
| `FinancialStatement_2039321 ONTARIO INC_2024-2025.pdf` | `data/archive/` | Annual | Audited full-year FY2024-25 financials |
| `FinancialStatement_2039321 ONTARIO INC_2023-2024.pdf` | `data/archive/` | Annual | Audited full-year FY2023-24 financials |
| `2039321 Ontario Inc July 31 2025 T2 Client copy 2025-10-20 (1).pdf` | `data/archive/` | Annual | FY2024-25 T2 corporate tax return (73 pages) |

Code snippets for reading these files: see `docs/constants.md`.

---

## Stack

- Python 3.13 (run as `python` in bash from the `som_mae_financials/` project folder)
- Libraries: openpyxl, python-docx, pdfplumber

---

## How to Run

### Live Codex Cycle — preferred when the user wants live reasoning before final reports

1. Run: `python scripts/build_live_session_packet.py`
2. Read:
   - `data/extracted/live_session_packet.json`
   - any relevant cached text under `data/extracted/source_text/`
3. Present one short brief at a time in this order:
   - marketing
   - tax
   - deviation
   - shareholder
4. Wait for Ramzan's reply after each brief.
5. After approval, create `data/extracted/live_report_payload.json` using `data/extracted/live_report_payload.template.json` as the starting shape.
6. Run: `python scripts/render_live_reports.py data/extracted/live_report_payload.json`

Use extra source documents if they were added to `data/current/`, `data/archive/`, or `docs/`.
Python should handle extraction and rendering only. Final judgment belongs in the live Codex session.

### Lean Report Run Protocol — use this when the user drops new QuickBooks files

**When the user says "Regenerate all reports" or drops new QB exports:**

1. Run one command: `python scripts/run_all_reports.py`
2. Read the output file: `reports/validation_summary_<date>.txt`
3. Summarize key findings to the user in a plain table (tuition, marketing gap, shareholder balance, any failures)
4. Update `tasks/TASKS.md` with findings and next steps

**Do NOT read task recipe files, individual scripts, or data files** unless a validation check
fails. If a check fails: read only the failing script, fix it, re-run the pipeline.

### Individual scripts (only when running a single task or debugging)

```bash
python scripts/build_live_session_packet.py   # Build live evidence packet + payload template
python scripts/render_live_reports.py         # Render redesigned reports from approved payload
python scripts/extract_data.py                # Read QuickBooks files → data/extracted/run_data.json
python scripts/generate_marketing_report.py   # Task #1
python scripts/generate_tax_report.py         # Task #2
python scripts/generate_deviation_report.py   # Task #3
python scripts/generate_shareholder_report.py # Task #4
python scripts/validate_all.py                # Validate all 4 latest reports
```

All scripts must be run from the `som_mae_financials/` project folder.

---

## Report Format Standard ("Easy Read")

All 4 reports should answer the main question first in simple English.

For live Codex reports, put these at the top in this order:

1. **Main Question**
2. **Direct Answer**
3. **Best Estimate**
4. **Key Numbers**
5. Short supporting detail after that

The older bulk reports follow the prior "easy read" structure. That fallback format is still supported, but the live Codex path should lead with the answer first.

Bulk reports follow this structure (enforced by `scripts/report_helpers.py`):

1. **Quick Summary** — blue callout (4–6 bullets) + red callout (1–3 urgent actions) + note pointing forward
2. **Numbered sections** with plain-English explanations
3. **Color-coded callout boxes** — red = urgent, yellow = caution, green = good, blue = rules
4. **Action Checklist** section (second-to-last) — numbered list, each item has **bold title** + plain-English body
5. **Bottom Line** section (last) — numbered list, each item has **bold title** + plain-English body
6. **Disclaimer note** at the very end

Report naming:

- Live workflow: `reports/codex_live_report_<topic>_mae_YYYY-MM-DD.docx`
- Bulk fallback workflow: `reports/claude_report_<topic>_mae_YYYY-MM-DD.docx`

**IMPORTANT — Known account flags (as of Apr 2026):**

- **FTC charges (6201.1) = $0 this year** — was $24,058/year historically. Flag in marketing report. Confirm with head office if still expected.
- **Student Handouts +108% vs PY** — flag in every deviation report (CRA risk).
- **Class 13-a CCA expired Jul 31, 2025** — ~$79,000 less in tax deductions this year. Flag in tax report.
- **Tax installment status:** Do NOT state paid/unpaid/upcoming/overdue status unless a provided project source explicitly shows it.

---

## Reports

Past reports from the older bulk pipeline (last 4 — older entries in `tasks/ARCHIVE.md`):

- `reports/claude_report_marketing_mae_2026-04-02.docx` — Task #1, Apr 2, 2026 (tuition $3,176,493; marketing $72,384; gap $22,911–$29,778)
- `reports/claude_report_tax_mae_2026-04-02.docx` — Task #2, Apr 2, 2026 (H1 pre-tax $1,226,848; Apr 30 installment $13,565 URGENT)
- `reports/claude_report_deviation_mae_2026-04-02.docx` — Task #3, Apr 2, 2026 (Handouts +108%; Insurance +71%)
- `reports/claude_report_shareholder_mae_2026-04-02.docx` — Task #4, Apr 2, 2026 (Ramzan +$721.68; Rezai +$9,520.37; JE-12 undocumented)

---

## Tasks

All task instructions live in the `tasks/` folder as individual recipe files.
When a task is triggered, read the corresponding file and follow its steps exactly.

### Task Index

| # | Task | Recipe file |
| --- | --- | --- |
| ALL | Generate + validate all 4 reports | `tasks/run_all_reports.md` |
| 1 | Marketing/Advertising Spend Analysis | `tasks/task1_marketing_analysis.md` |
| 2 | Corporate Tax Estimation | `tasks/task2_tax_estimation.md` |
| 3 | Spending Deviation Analysis (CRA Risk) | `tasks/task3_deviation_analysis.md` |
| 4 | Shareholder Advances Review | `tasks/task4_shareholder_advances.md` |
| — | Validate a single report | `tasks/validate_report.md` |
| — | Validate all reports | `tasks/validate_all_reports.md` |
| — | Fix and regenerate failed reports | `tasks/fix_and_regenerate_failed_reports.md` |
| — | Full audit (validate → fix → re-validate) | `tasks/run_full_report_audit.md` |
