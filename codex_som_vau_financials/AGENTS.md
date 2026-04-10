# codex_som_vau_financials

## Read Order

Before substantial work in this project, read:

1. `memory/PROJECT_MEMORY.md`
2. `tasks/TASKS.md`
3. `tasks/DECISIONS.md`
4. `CLAUDE.md`

When Ramzan says `start session`, use the read order above, then report:
- current status
- what was done last session
- next recorded step

When Ramzan says `end session`, update:
- `tasks/TASKS.md`
- `tasks/DECISIONS.md` if needed
- `memory/PROJECT_MEMORY.md` if stable facts changed
- `tasks/ARCHIVE.md` if more than 5 recent sessions are kept

## Live Codex Workflow

For Codex, the preferred VAU workflow is now:

1. Run `python scripts/build_live_session_packet.py`
2. Read `data/extracted/live_session_packet.json`
3. Review any relevant cached text under `data/extracted/source_text/`
4. Present one short on-screen brief at a time:
   - marketing
   - tax
   - deviation
   - shareholder
5. Wait for Ramzan's plain-English reply after each brief
6. Only generate final `.docx` reports after approval by creating `data/extracted/live_report_payload.json`
   and running `python scripts/render_live_reports.py data/extracted/live_report_payload.json`

Python may do extraction and basic calculations, but final judgment belongs in the live Codex session.
Extra documents beyond QuickBooks may be added and should be considered in the same flow.

## Legacy Prototype

The earlier prototype remains in the repo for reference:

1. Run `python scripts/run_briefing_cycle.py`
2. Read `data/extracted/briefing_packets.json`
3. Present one short on-screen brief at a time:
   - marketing
   - tax
   - deviation
   - shareholder
4. Wait for Ramzan's plain-English reply after each brief
5. Only generate final `.docx` reports after approval

The new live workflow above overrides the old direct report-generation flow in `CLAUDE.md` for Codex-led sessions.

## Notes

- `CLAUDE.md` remains the detailed project instruction source.
- `memory/PROJECT_MEMORY.md` stores stable Codex-facing project context for fast reload.
- Update project memory when new stable facts are learned.
