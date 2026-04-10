# MAE Live Codex Cycle

Use this when Ramzan updates QuickBooks files or adds supporting tax or finance documents and wants Codex to do the reasoning live in chat.

## Goal

Create a repeatable monthly MAE workflow where:

- Python extracts evidence only
- Codex reasons live in chat
- Ramzan reviews one short brief at a time
- final redesigned `.docx` reports are generated only after approval

## Steps

1. Run:

```bash
python scripts/build_live_session_packet.py
```

2. Read:

- `data/extracted/live_session_packet.json`
- any relevant cached text files under `data/extracted/source_text/`

3. Present one short brief at a time in this order:

- marketing
- tax
- deviation
- shareholder

4. Wait for Ramzan's reply after each brief.

5. After approval, create:

- `data/extracted/live_report_payload.json`

using `data/extracted/live_report_payload.template.json` as the starting shape.

6. Render final reports:

```bash
python scripts/render_live_reports.py data/extracted/live_report_payload.json
```

## Rules

- Do not let scripts make the final judgment calls.
- Use extra source documents if Ramzan dropped them into `data/current/`, `data/archive/`, or `docs/`.
- Keep explanations in plain English.
- If the evidence and an old script disagree, trust the evidence and live reasoning.
