# codex_som_vau_financials — Project Memory

## Purpose

- Financial analysis tools and reports for Spirit of Math Schools Vaughan.
- Primary outputs are four recurring report types: marketing, tax, deviation, and shareholder.

## Stable Facts

- Fiscal year: August 1 to July 31.
- Royalty obligation: 22% of gross revenue.
- Marketing obligation: 3% of gross revenue.
- Main project instructions live in `CLAUDE.md`.
- Current constants live in `docs/constants.md`.
- Session continuity lives in `tasks/TASKS.md` and `tasks/DECISIONS.md`.

## Workflow Pattern

- Normal full refresh path is `python scripts/run_all_reports.py`.
- Validation summary lives in `reports/validation_summary_<date>.txt`.
- Use the lean run protocol from `CLAUDE.md` unless a validation check fails.
- New Codex default path is `python scripts/build_live_session_packet.py`, then one short on-screen brief at a time in chat, then final reports only after approval with `python scripts/render_live_reports.py data/extracted/live_report_payload.json`.
- The live Codex path may use extra tax or finance documents dropped into `data/current/`, `data/archive/`, or `docs/`.
- Python should stay limited to extraction, normalization, and rendering. Final conclusions should be made live in the Codex session.

## Known Recurring Flags

- Account 5711 Service Fee is a new franchisor charge in FY2025-26 and should be flagged for classification/review until its accounting treatment is confirmed.
- Automobile costs require CRA logbook support and should be flagged in deviation review.
- Hajj payments and the September 15 cheque are currently recorded in the shareholder advance account, not the P&L. Reports should describe them as already posted correctly and needing clear documentation, not as suspected miscoding.
- Do not state installment payment status unless a provided source file explicitly proves it.
