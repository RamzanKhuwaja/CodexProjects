# codex_som_mae_financials — Project Memory

## Purpose

- Financial analysis tools and reports for Spirit of Math Schools Markham East.
- Primary outputs are four recurring report types: marketing, tax, deviation, and shareholder.

## Stable Facts

- Fiscal year: August 1 to July 31.
- Royalty obligation: 12% of gross revenue.
- Marketing obligation: 3% of gross revenue.
- Main project instructions live in `CLAUDE.md`.
- Current constants live in `docs/constants.md`.
- Session continuity lives in `tasks/TASKS.md` and `tasks/DECISIONS.md`.

## Workflow Pattern

- Normal full refresh path is `python scripts/run_all_reports.py`.
- Validation summary lives in `reports/validation_summary_<date>.txt`.
- Use the lean run protocol from `CLAUDE.md` unless a validation check fails.
- New Codex prototype path is `python scripts/run_briefing_cycle.py` first, then one short on-screen brief at a time, then final reports only after approval.

## Known Recurring Flags

- FTC charges are zero this year and should stay flagged in marketing review until resolved.
- Student Handouts increase should stay flagged in deviation review.
- Class 13-a CCA expiry materially affects tax review.
