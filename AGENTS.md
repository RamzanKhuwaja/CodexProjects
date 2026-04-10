# CodexProjects Workspace

This is a workspace containing multiple independent Codex projects, each in its own subfolder.

---

## Projects

```text
CodexProjects/
├── _project_template/        # Template — copy this to start a new project
├── codex_som_mae_financials/ # Spirit of Math Markham East financial analysis
├── codex_som_vau_financials/ # Spirit of Math Vaughan financial analysis
└── tasks/                    # Workspace-level session tracking
```

Each project should have its own `AGENTS.md` with project-specific instructions.

---

## Memory System

Workspace memory lives in `memory/`.

Read these before substantial workspace-level work:

1. `memory/MEMORY.md`
2. The specific memory files referenced there that are relevant to the task
3. `tasks/TASKS.md`
4. `tasks/DECISIONS.md`

For project work, also read:

1. `<project>/AGENTS.md`
2. `<project>/memory/PROJECT_MEMORY.md` if it exists
3. `<project>/tasks/TASKS.md`
4. `<project>/tasks/DECISIONS.md`

Memory rules:

- Use memory files for stable facts, user preferences, and workspace conventions.
- Use `tasks/TASKS.md` for current status, open items, and recent session history.
- Use `tasks/DECISIONS.md` for locked decisions.
- Update memory files yourself when you learn stable facts that will help future sessions.

---

## Session Commands

Preferred session phrases are:

- `start session`
- `end session`

When Ramzan says `start session`:

1. Determine whether this is a workspace session or a project session from context.
2. For a workspace session, read:
   - `memory/MEMORY.md`
   - the relevant files referenced there
   - `tasks/TASKS.md`
   - `tasks/DECISIONS.md`
3. For a project session, read:
   - `<project>/AGENTS.md`
   - `<project>/memory/PROJECT_MEMORY.md` if it exists
   - `<project>/tasks/TASKS.md`
   - `<project>/tasks/DECISIONS.md`
   - project requirements/instruction files named by that project
4. Report back in plain English:
   - which session type is active
   - current status
   - what was done last session
   - the next recorded step
5. Then proceed unless Ramzan redirects.

When Ramzan says `end session`:

1. Determine whether this was a workspace or project session.
2. Update the relevant `tasks/TASKS.md`:
   - current status
   - open items
   - a concise session log entry
   - explicit next step
3. Update the relevant `tasks/DECISIONS.md` if any permanent decisions were made.
4. Move session entries older than the last 5 from `TASKS.md` to `ARCHIVE.md` if that file exists for that scope.
5. Update memory files if any new stable facts were learned.
6. Commit the relevant files for that session to git with a focused commit.
7. Push the commit to GitHub unless Ramzan says not to push.
8. Summarize the recorded state so the next `start session` can resume cleanly.

---

## Workspace Rules

- Do not create or maintain `README.md` files anywhere in this workspace.
- Do not create files at the workspace root unless they are workspace meta files.
- Allowed root-level meta files are `AGENTS.md` and `CHEATSHEET.txt`.
- Treat each first-level project folder as independent unless the user explicitly asks for cross-project work.
- For non-trivial work, read the target project's `AGENTS.md` and `tasks/` files first if they exist.

---

## Session Management

Workspace sessions are valid when working on workspace rules, templates, shared conventions, or cross-project concerns.

| File | Purpose |
| --- | --- |
| `tasks/TASKS.md` | Current workspace state and last sessions |
| `tasks/DECISIONS.md` | Permanent workspace-level decisions |
| `tasks/ARCHIVE.md` | Older workspace session history |

Project-level work belongs in each project's own `tasks/` files.

---

## Standard Project Layout

```text
<project>/
├── AGENTS.md
├── CHEATSHEET.txt
├── requirements.txt
├── .gitignore
├── data/
│   ├── current/
│   └── archive/
├── docs/
├── memory/
│   └── PROJECT_MEMORY.md
├── output/
├── scripts/
└── tasks/
    ├── TASKS.md
    ├── DECISIONS.md
    └── ARCHIVE.md
```

Use `_project_template/` as the default starting point for new projects.

---

## Git Rules

Do commit:

- Everything in `docs/`
- Everything in `data/`
- Everything in `scripts/`
- Office documents and PDFs anywhere in a project

Do not commit:

- Non-Office generated files in `output/`
- Mixed commits across unrelated projects
