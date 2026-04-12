# som_mae_financials — Task Tracker

> This file tracks current state only — position, open items, session log.
> Permanent decisions live in `DECISIONS.md`. Older sessions live in `ARCHIVE.md`.
>
> **Cleanup (do at each session start):** Move sessions older than the last 5 to `ARCHIVE.md`.
> Delete checked open items. Keep this file readable in under 60 seconds.
>
> **To open a session:** `start session`
> **To close a session:** `end session`

---

## Current Position

**Status:** Closed cleanly for Apr 11, 2026. The MAE live workflow now generates answer-first reports, the retired prototype path has been removed from active support files, and the session changes are ready to resume from the new direct-answer format.
**Last session:** Apr 11, 2026 — cleaned the repo for the new workflow, changed live reports to answer the main question first with a direct estimate, regenerated the four `codex_live_report_*` reports, and recorded the new end-session git-add check.
**Next step:** On the next QuickBooks or tax-doc drop, run `python scripts/build_live_session_packet.py`, use the live answer-first format to generate `data/extracted/live_report_payload.json`, render final reports with `python scripts/render_live_reports.py data/extracted/live_report_payload.json`, and collect support for JE-11, JE-12, Hajj, and the installment catch-up.

---

## Open Items

- **JE-12 documentation needed** — Annual credits ($3,500 + $4,950 + $1,070.37 = $9,520.37) posted for both shareholders. Ask bookkeeper/Tang & Partners: what are these three entries for?
- **JE-11 documentation needed** — Written agreement between Ramzan and Rezai confirming Rezai waived his credit to offset Ramzan's debt.
- **Hajj advance verification** — Confirm $10,000 (Jan 13, 2026) is in account 2901 only, NOT in any expense account.
- **FY2025-26 installments not paid** — Owner stated on Apr 11, 2026 that no FY2025-26 installments were made. Catch-up and CRA exposure need review for Oct 31, 2025 $1,530; Jan 31, 2026 $13,565; Apr 30, 2026 $13,565; Jul 31, 2026 $13,566.
- **Marketing gap** — $72,384 spent vs ~$95,295–$102,162 obligation. Gap of ~$22,911–$29,778 remaining before Jul 31.

---

## Session Log

### Session 6 — 2026-04-11

**Focus:** Run the live MAE workflow end-to-end on current files, simplify the report style to direct answers first, and clean the project to remove the retired prototype path.

**Changes made:**

- Ran `python scripts/build_live_session_packet.py`, reviewed the four live briefs in chat, and captured current conclusions from the evidence packet.
- Recorded live owner input that no FY2025-26 installment payments have been made and carried that into the tax output.
- Wrote `data/extracted/live_report_payload.json` and rendered:
  - `reports/codex_live_report_marketing_mae_2026-04-11.docx`
  - `reports/codex_live_report_tax_mae_2026-04-11.docx`
  - `reports/codex_live_report_deviation_mae_2026-04-11.docx`
  - `reports/codex_live_report_shareholder_mae_2026-04-11.docx`
- Updated the live report renderer and payload shape so reports now start with the main question, direct answer, and best estimate in simple language.
- Cleaned `AGENTS.md`, `CHEATSHEET.txt`, `memory/PROJECT_MEMORY.md`, `tasks/DECISIONS.md`, and the repo support files so the retired brief-first prototype is no longer part of the active MAE instructions.
- Updated the project `end session` instructions so Codex must check `git status` and add any relevant new files before committing and pushing.

**Next:** Use the same live workflow on the next data refresh, keep the answer-first report style, and collect missing support for installments, JE-11, JE-12, and the $10,000 Hajj item.

### Session 5 — 2026-04-10

**Focus:** Replace the MAE brief-first prototype with the newer VAU-style live Codex workflow.

**Changes made:**

- Added `scripts/project_context.py` so archived MAE reviewed statements and the FY2024-25 T2 drive repeatable historical values instead of hardcoded script constants.
- Added `scripts/live_workflow.py`, `scripts/build_live_session_packet.py`, and `scripts/render_live_reports.py` to support evidence-first live review and payload-driven report rendering.
- Added `tasks/run_live_mae_cycle.md` and updated `AGENTS.md`, `CHEATSHEET.txt`, `CLAUDE.md`, `tasks/DECISIONS.md`, `tasks/TASKS.md`, and `memory/PROJECT_MEMORY.md` so the live Codex workflow is now the default MAE path.
- Verified the new MAE flow by running `python scripts/build_live_session_packet.py` successfully against the current MAE files.
- Committed and pushed the workflow changes to GitHub.

**Next:** Use the MAE live workflow on the next real data refresh, then render final reports only after the live brief review is approved.

### Session 4 — 2026-04-10

**Focus:** MAE redesign prototype for deeper LLM-led analysis before report generation.

**Changes made:**

- Added `scripts/run_briefing_cycle.py` — extract-first prototype runner that stops before `.docx` generation.
- Added `scripts/build_briefing_packets.py` — writes `data/extracted/briefing_packets.json` for 4 short MAE briefs.
- Updated `AGENTS.md`, `CHEATSHEET.txt`, `tasks/TASKS.md`, `tasks/DECISIONS.md`, and `memory/PROJECT_MEMORY.md` to make the brief-first workflow the default Codex path.
- Ran the new brief cycle successfully against current MAE data and verified that the generated briefing packet reflects MAE-specific issues, not VAU rules.

**Next:** Use the prototype on the next MAE data refresh and refine brief quality before redesigning final report generation.

### Session 3 — 2026-04-07

**Focus:** Token optimization — CLAUDE.md slimmed, `docs/constants.md` created, Lean Report Run Protocol added.

**Changes made:**

- `docs/constants.md` created — all financial constants, CCA tables, 3-year benchmarks, installment schedule, and file-reading code snippets moved here. Only read on demand.
- `CLAUDE.md` rewritten — ~55% smaller. Removed constants tables, code snippets, verbose task descriptions.
- `tasks/ARCHIVE.md` updated — old past reports list moved here.
- `tasks/DECISIONS.md` updated — constants pointer now points to `docs/constants.md`.
- **Lean Report Run Protocol** added to CLAUDE.md: next QB export run = 1 bash command → read validation summary → summarize. No script reading.

**Result:** Next report run session estimated at ~6,000 tokens vs ~60,000 previously (~90% reduction).

### Session 2 — 2026-04-07

**Focus:** Upgraded pipeline to handle CSV exports (QuickBooks now exports CSVs with prefix "Spirit of Math Schools Markham East_"). Removed all hardcoded dates/amounts from all 4 report scripts — fully dynamic from run_data.json. Regenerated all 4 reports. All 15 validation checks pass.
**Key findings (April 2, 2026 data):**

- Tuition YTD: $3,176,493 (+12.7% YoY); projected full year ~$3,405,399
- Marketing spent: $72,384; gap $22,911–$29,778 remaining to meet 3% obligation
- Tax: H1 pre-tax proxy $1,226,848; Apr 30 installment $13,565 URGENT
- Ramzan: +$721.68 (corp owes Ramzan — JE-12 posted); Rezai: +$9,520.37 (corp owes Rezai)
- Student Handouts +108% vs PY (CRA risk flag); Insurance +71% vs PY
**Changes made:** `extract_data.py`, `run_all_reports.py` — CSV/glob support; all 4 report scripts — fully dynamic (no hardcoding).
**Next:** Run again when next QuickBooks export arrives.
