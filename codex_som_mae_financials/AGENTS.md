# codex_som_mae_financials

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

## Brief-First Prototype

For Codex, the preferred MAE workflow is now:

1. Run `python scripts/run_briefing_cycle.py`
2. Read `data/extracted/briefing_packets.json`
3. Present one short on-screen brief at a time:
   - marketing
   - tax
   - deviation
   - shareholder
4. Wait for Ramzan's plain-English reply after each brief
5. Only generate final `.docx` reports after approval

This overrides the old direct report-generation flow in `CLAUDE.md` for Codex-led sessions.

## Notes

- `CLAUDE.md` remains the detailed project instruction source.
- `memory/PROJECT_MEMORY.md` stores stable Codex-facing project context for fast reload.
- Update project memory when new stable facts are learned.
