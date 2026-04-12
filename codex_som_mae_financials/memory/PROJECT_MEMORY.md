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
- Reports should answer the main question first in plain language, with a direct estimate up front and supporting detail after.

## Workflow Pattern

- Normal full refresh path is `python scripts/run_all_reports.py`.
- Validation summary lives in `reports/validation_summary_<date>.txt`.
- Use the lean run protocol from `CLAUDE.md` unless a validation check fails.
- New Codex default path is `python scripts/build_live_session_packet.py`, then one short on-screen brief at a time in chat, then final reports only after approval with `python scripts/render_live_reports.py data/extracted/live_report_payload.json`.
- The older brief-first prototype has been retired and should not be referenced in active instructions.
- The live Codex path may use extra tax or finance documents dropped into `data/current/`, `data/archive/`, or `docs/`.
- Python should stay limited to extraction, normalization, and rendering. Final conclusions should be made live in the Codex session.

## Known Recurring Flags

- FTC charges are zero this year and should stay flagged in marketing review until resolved.
- Student Handouts increase should stay flagged in deviation review.
- Class 13-a CCA expiry materially affects tax review.
- Do not state installment payment status unless a provided source file explicitly proves it.
