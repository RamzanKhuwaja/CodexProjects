# som_vau_financials — Task Tracker

> This file tracks current state only — position, open items, session log.
> Permanent decisions live in `DECISIONS.md`. Older sessions live in `ARCHIVE.md`.
>
> **Cleanup (do at each session start):** Move sessions older than the last 5 to `ARCHIVE.md`.
> Delete checked open items. Keep this file readable in under 60 seconds.
>
> **To open a session:** `/orient`
> **To close a session:** `/close-session`

---

## Current Position

**Status:** Active — FY2025-26 in progress. VAU live Codex workflow rebuilt on April 10, 2026 for evidence-first review plus redesigned final reports.
**Last session:** Apr 10, 2026 — built VAU-only live workflow: Python now prepares neutral evidence and cached source text, Codex does reasoning live in chat, and redesigned reports render from an approved payload.
**Next step:** On next QuickBooks or tax-doc drop, run `python scripts/build_live_session_packet.py`, review the 4 briefs live, then render final reports with `python scripts/render_live_reports.py data/extracted/live_report_payload.json`.

---

## Open Items

- **Ramzan owes corp −$120,071** — needs a repayment plan before July 31, 2027. Discuss with Tang & Partners.
- **Hajj payments $17,990** (two e-Transfers Jan 2026) — verify they are in account 2901 ONLY, not in any P&L expense account.
- **Personal credit card items in Ramzan's account** — Walmart, Cineplex, Aritzia, Air Canada, Uber credits/charges. Confirm corporate card is not being used for personal purchases.
- **Service Fee 5711 ($61,130)** — new account, unresolved. Confirm what it is, who it's paid to, and that it's tax-deductible.
- **Journal entries with no memos** (JE-21, JE-22, JE-23, JE-24) — ask bookkeeper to add memo descriptions.
- **Marketing gap** — $51,131 spent vs ~$62,825–$64,659 obligation. Gap of ~$11,694 YTD or ~$13,528 projected remaining.
- **H1 pre-tax $732,889 already exceeds $300K SBD limit** — income above SBD taxed at 26.5%. Discuss tax planning with Tang & Partners.
- **Corporate tax installments/payment status** — do not assume they are paid or unpaid from the current project files alone. Confirm from CRA/accountant records or a QuickBooks source that explicitly shows payments.

---

## Session Log

### Session 5 — 2026-04-10

**Focus:** Replace script-led report logic with a VAU-only live Codex workflow.

**Changes made:**

- Added `scripts/live_workflow.py` — shared live-session extraction and report-rendering helpers.
- Added `scripts/build_live_session_packet.py` — builds `data/extracted/live_session_packet.json` plus cached source text and a payload template.
- Added `scripts/render_live_reports.py` — renders redesigned `.docx` reports from a live-session payload.
- Added `tasks/run_live_vau_cycle.md` — repeatable monthly recipe for QuickBooks plus extra supporting docs.
- Generated sample redesigned reports dated April 10, 2026 to verify the new renderer.

**Next:** Use the live packet on the next real monthly update, brief one topic at a time in chat, then create the approved payload and final reports.

### Session 4 — 2026-04-09

**Focus:** VAU redesign prototype for deeper LLM-led analysis before report generation.

**Changes made:**

- Added `scripts/run_briefing_cycle.py` — extract-first prototype runner that stops before `.docx` generation.
- Added `scripts/build_briefing_packets.py` — writes `data/extracted/briefing_packets.json` for 4 short VAU briefs.
- Updated `AGENTS.md`, `CHEATSHEET.txt`, `tasks/TASKS.md`, `tasks/DECISIONS.md`, and `memory/PROJECT_MEMORY.md` to make the brief-first workflow the default Codex path.

**Next:** Use the prototype on the next VAU data refresh and refine brief quality before redesigning final report generation.

### Session 3 — 2026-04-07

**Focus:** Token optimization — CLAUDE.md slimmed, `docs/constants.md` created, Lean Report Run Protocol added.

**Changes made:**

- `docs/constants.md` created — all financial constants, CCA tables, 3-year benchmarks, and file-reading code snippets moved here. Only read on demand.
- `CLAUDE.md` rewritten — ~55% smaller. Removed constants tables, code snippets, verbose task descriptions.
- `tasks/ARCHIVE.md` updated — old past reports list moved here.
- **Lean Report Run Protocol** added to CLAUDE.md: next QB export run = 1 bash command → read validation summary → summarize. No script reading.

**Result:** Next report run session estimated at ~6,000 tokens vs ~60,000 previously (~90% reduction).

### Session 2 — 2026-04-07

**Focus:** Pipeline upgrade applied from MAE — all 6 scripts updated to handle CSV exports (QuickBooks now exports CSVs with prefix "Spirit of Math Schools Vaughan_"). All 4 report scripts fully rewritten to be dynamic (read from run_data.json, no hardcoded dates/amounts). Regenerated all 4 reports with April 3 data. All 15 validation checks pass.

**Infrastructure changes:**

- `extract_data.py`: CSV/glob support; `safe_float` strips `$` and commas; fixed VAU account labels (6935 = Corporate Tax Expense, 4110.1 = Canada Carbon Rebate)
- `run_all_reports.py`: keyword-based glob file verification

**Key Apr 3 findings:**

- Tuition YTD: $2,094,169 (+8.5% YoY); projected full year ~$2,211,163
- Marketing spent: $51,131; gap ~$15,204 remaining; FTC $0 again this year (was $0 last year too)
- H1 pre-tax: $732,889 — already exceeds $300K SBD limit (income above SBD at 26.5%)
- Ramzan: −$120,071 (large, needs repayment plan); Farah: +$94.55
- Student Handouts +162% vs PY; Service Fee 5711 ($61,130) still unresolved
- Automobile costs (6300) +137% vs PY — CRA logbook required

**Next:** Run again when next QuickBooks export arrives.

### Session 1 — 2026-03-12

**Focus:** Full report run — all 4 reports regenerated. Shareholder sign convention corrected (Ramzan owes corp ~$141K; Farah owes corp ~$3,905).
**Key findings:** Marketing on track but tight ($46,297 vs $42,720 required YTD); projected full-year taxable income ~$290K; Service Fee $63,726 is a new unresolved account; Student Handouts +169% vs PY.
**Next:** Run again when next QuickBooks export arrives. Resolve Service Fee account.
