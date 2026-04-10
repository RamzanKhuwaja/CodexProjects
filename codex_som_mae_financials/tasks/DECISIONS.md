# som_mae_financials — Permanent Decisions

> Permanent, locked decisions live here. Never put decisions in TASKS.md.
> When a decision changes, update the entry here — do not keep both.

---

## Architecture

- **Report pipeline:** `extract_data.py` → 4 report scripts → `validate_all.py`, orchestrated by `run_all_reports.py`
- **Brief-first prototype:** `run_briefing_cycle.py` → `briefing_packets.json` → 4 short on-screen briefs → approved final report generation
- **Shared helpers:** All 4 report scripts import from `scripts/report_helpers.py` — do not modify without testing all 4
- **Report format:** "Easy read" standard — Quick Summary (blue callout + red callout), numbered sections, Action Checklist, Bottom Line, Disclaimer
- **Report naming:** `reports/claude_report_<topic>_mae_YYYY-MM-DD.docx`
- **Extracted data cache:** `data/extracted/run_data.json` — gitignored, regenerated each run
- **Brief packet cache:** `data/extracted/briefing_packets.json` — gitignored, regenerated each run
- **Financial constants:** Live in `docs/constants.md` — update that file when new audited data arrives. Do not store in CLAUDE.md.
- **Lean Report Run Protocol:** When user drops new QB files → run `python scripts/run_all_reports.py` → read `reports/validation_summary_<date>.txt` → summarize. Do NOT read scripts or data files unless a check fails.
- **Codex default workflow:** For new MAE sessions, use the brief-first prototype before generating final reports.

## Business Rules

- **Fiscal year:** Aug 1 – Jul 31
- **Royalty rate:** 12% of gross revenue
- **Marketing obligation:** 3% of gross revenue
- **SBD limit:** $300,000 per business — MAE gets $300,000 and VAU gets $300,000 separately (confirmed by owner Apr 7, 2026)
- **Effective tax rate:** ~13.68% (from FY2024-25 T2 return)
