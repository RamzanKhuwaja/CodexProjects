# Workspace Rules

- `CodexProjects` is a workspace containing multiple independent projects.
- Workspace-level meta files are allowed at the root: `AGENTS.md`, `CHEATSHEET.txt`, `tasks/`, and `memory/`.
- New projects should start from `_project_template/`.
- Do not create or maintain `README.md` files.
- Keep project logic inside project folders, not at the workspace root.
- Use file-based memory inside the repo as the primary continuity system for Codex.
- Local Codex config is intentionally high-autonomy on this laptop: `approval_policy = "never"` and `sandbox_mode = "danger-full-access"`.
- Standard session phrases for Ramzan are `start session` and `end session`.
- Financial-report redesign should favor short, clear, plain-English outputs instead of long Claude-style narratives.
