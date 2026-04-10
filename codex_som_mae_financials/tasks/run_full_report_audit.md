# Task: Run Full Report Audit

**Goal:** Validate every report, fix any that fail, and produce a single audit summary `.docx`
the owner can read in under 2 minutes to know whether anything needs their attention.

## Instructions

### Step 1 — Validate all reports

Follow the instructions in `tasks/validate_all_reports.md` in full.
Wait for completion. Open `reports/all_reports_validation_summary.docx` and read the result.

- If the summary callout is **green (ALL PASSED)** → skip to Step 3
- If the summary callout is **red or yellow** → proceed to Step 2

### Step 2 — Fix failed reports

Follow the instructions in `tasks/fix_and_regenerate_failed_reports.md` in full.
Wait for completion. Open the latest `reports/fix_log_{date}.docx` and read the result.

Note which reports were FIXED and which were ESCALATED (could not be auto-fixed).

Re-run `tasks/validate_report.md` on each FIXED report to confirm it now passes.

### Step 3 — Generate the audit summary as a .docx

Write a Python script `scripts/generate_validation_temp.py` that produces a styled Word document
saved as `reports/audit_log_{YYYY-MM-DD}.docx`.

**Follow the same python-docx styling conventions as the other reports.**

**Required document structure (in this order):**

1. **Title block** — "Full Report Audit" + date + "Run by Claude"

2. **Verdict callout — the first and most prominent element:**
   - PASSED → green background `RGBColor(0xD9, 0xEA, 0xD3)`, bold:
     `"✓  AUDIT COMPLETE — ALL REPORTS VERIFIED. No action required."`
   - PASSED WITH ESCALATIONS → yellow background `RGBColor(0xFF, 0xF2, 0xCC)`, bold:
     `"⚠  AUDIT COMPLETE — X REPORT(S) NEED YOUR ATTENTION"`
     Plain-English bullet list of escalated items and what the owner should do
     (e.g., "Re-export the QuickBooks P&L and re-run Task #1").
   - FAILED → red background `RGBColor(0xFF, 0xCC, 0xCC)`, bold:
     `"✗  AUDIT FAILED — MULTIPLE REPORTS HAVE UNRESOLVED ISSUES"`
     Same plain-English bullet list.

3. **Audit results table** with these columns:
   `| Report Name | Initial Result | Fix Applied | Final Result | Status |`
   - Green row for PASSED, red for FAILED/ESCALATED, yellow for WARNINGS.

4. **What to do next** section (only if any escalations exist):
   Numbered plain-English action items for the owner — no jargon.
   Example: "1. Re-export your QuickBooks Profit & Loss file and drop it into data/current/.
   Then re-run Task #1 to regenerate the marketing report."

Run the script, then delete it:

```bash
python scripts/generate_validation_temp.py
rm scripts/generate_validation_temp.py
```

## Decision Logic

```text
Validate All Reports
       ↓
  All pass? ──YES──→ Generate audit summary (green) → Done
       ↓ NO
Fix Failed Reports
       ↓
  All fixed? ──YES──→ Re-validate → All pass? ──YES──→ Audit summary (green) → Done
       ↓ NO                               ↓ NO
  Mark escalated                    Audit summary (yellow — PASSED WITH ESCALATIONS)
```

## Safety Rules

- Never skip re-validation after a fix
- Never mark the audit PASSED if any report is escalated
- Do not overwrite a previous `audit_log_*.docx` — use today's date to create a new one
- All intermediate files (`all_reports_validation_summary.docx`, `fix_log_*.docx`,
  individual `_validation.docx` files) are preserved — never delete them
