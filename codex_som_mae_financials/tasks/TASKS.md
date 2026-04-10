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

**Status:** Active — FY2025-26 in progress. All 4 reports generated as of April 2, 2026. MAE brief-first prototype now added for Codex.
**Last session:** Apr 10, 2026 — MAE brief-first prototype added for Codex: extraction now supports one-short-brief-at-a-time review before final report generation.
**Next step:** On next QuickBooks drop, run the new brief-first flow before generating final reports.

---

## Open Items

- **JE-12 documentation needed** — Annual credits ($3,500 + $4,950 + $1,070.37 = $9,520.37) posted for both shareholders. Ask bookkeeper/Tang & Partners: what are these three entries for?
- **JE-11 documentation needed** — Written agreement between Ramzan and Rezai confirming Rezai waived his credit to offset Ramzan's debt.
- **Hajj advance verification** — Confirm $10,000 (Jan 13, 2026) is in account 2901 only, NOT in any expense account.
- **Apr 30, 2026 installment URGENT** — $13,565 due April 30, 2026.
- **Marketing gap** — $72,384 spent vs ~$95,295–$102,162 obligation. Gap of ~$22,911–$29,778 remaining before Jul 31.

---

## Session Log

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

### Session 1 — 2026-03-11

**Focus:** Full report run — all 4 reports regenerated with updated QuickBooks YTD data.
**Key findings:** Marketing spend $61,328 YTD (gap $34,700–$40,300 remaining); projected revenue ~$3.39M; Apr 30 tax installment $13,565 URGENT; Ramzan shareholder advance improved to −$8,799; JE-11 documentation still required.
**Next:** Run again when next QuickBooks export arrives.
