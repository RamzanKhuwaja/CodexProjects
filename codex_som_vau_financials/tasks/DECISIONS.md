# som_vau_financials — Permanent Decisions

> Permanent, locked decisions live here. Never put decisions in TASKS.md.
> When a decision changes, update the entry here — do not keep both.

---

## Architecture

- **Report pipeline:** `extract_data.py` → 4 report scripts → `validate_all.py`, orchestrated by `run_all_reports.py`
- **Live Codex pipeline:** `build_live_session_packet.py` → `live_session_packet.json` → live chat briefs → `live_report_payload.json` → `render_live_reports.py`
- **Brief-first prototype:** `run_briefing_cycle.py` → `briefing_packets.json` → 4 short on-screen briefs → approved final report generation
- **Shared helpers:** All 4 report scripts import from `scripts/report_helpers.py` — do not modify without testing all 4
- **Live session evidence cache:** `data/extracted/live_session_packet.json` — regenerated each live session
- **Live report payload template:** `data/extracted/live_report_payload.template.json` — used as the fill-in shape after live review
- **Live report naming:** `reports/codex_live_report_<topic>_vau_YYYY-MM-DD.docx`
- **Report format:** Live reports should favor one clear answer, key numbers, plain-English sections, and a short bottom line
- **Report naming:** `reports/claude_report_<topic>_vau_YYYY-MM-DD.docx`
- **Extracted data cache:** `data/extracted/run_data.json` — gitignored, regenerated each run
- **Brief packet cache:** `data/extracted/briefing_packets.json` — gitignored, regenerated each run
- **Financial constants:** Live in `docs/constants.md` — update that file when new audited data arrives. Do not store in CLAUDE.md.
- **Lean Report Run Protocol:** When user drops new QB files → run `python scripts/run_all_reports.py` → read `reports/validation_summary_<date>.txt` → summarize. Do NOT read scripts or data files unless a check fails.
- **Codex default workflow:** For new VAU sessions, use the live Codex pipeline before generating final reports.
- **Payment-status rule:** Do not state that tax installments were paid, unpaid, upcoming, or overdue unless a provided project source explicitly shows that status.
- **Source-of-truth rule:** Current-year figures must come from the current QuickBooks files and provided supporting documents. Historical tax and financial reference figures should be derived from the archived reviewed statements and T2 files, not hardcoded into scripts.

## Business Rules

- **Fiscal year:** Aug 1 – Jul 31 (year 16 of operation in FY2025-26)
- **Royalty rate:** 22% of gross revenue (higher than some other SOM franchises)
- **Marketing obligation:** 3% of gross revenue
- **Franchise agreement expiry:** 2027
- **SBD limit:** $300,000 (confirmed — two businesses; each gets $300K separately)
- **Account 5711 "Service Fee":** New franchisor charge in FY2025-26 — do not treat as marketing-eligible; confirm accounting/tax treatment with Tang & Partners
- **VAU shareholder treatment:** The real shareholder number is the net position after including parent account `2900`; do not present the raw Ramzan/Farah subaccounts alone as the main answer.
- **Hajj and Sep 15 cheque:** These are currently posted in `2900 Shareholder's Advance:2901 Ramzan Khuwaja`, not in the P&L. Report them as shareholder items already booked correctly, while still advising clear documentation.
