# [PROJECT NAME] — Codex Instructions

## Source Of Truth

Requirements, background, and project notes live in:

```text
docs/Requirements.docx
```

Always read that file at the start of any session or task. Do not rely on prior chat context alone.

---

## Memory

Read these before substantial work:

1. `memory/PROJECT_MEMORY.md`
2. `tasks/TASKS.md`
3. `tasks/DECISIONS.md`
4. `docs/Requirements.docx`

Use `memory/PROJECT_MEMORY.md` for stable facts and user/project preferences.
Use `tasks/` files for active state.

---

## Session Commands

Preferred session phrases are:

- `start session`
- `end session`

When Ramzan says `start session` for this project:

1. Read:
   - `AGENTS.md`
   - `memory/PROJECT_MEMORY.md`
   - `tasks/TASKS.md`
   - `tasks/DECISIONS.md`
   - `docs/Requirements.docx` or the current requirement source for the project
2. Report back:
   - current project status
   - what was done last session
   - the next recorded step
3. Then continue unless redirected.

When Ramzan says `end session` for this project:

1. Update `tasks/TASKS.md`:
   - current status
   - open items
   - session log entry
   - next step
2. Update `tasks/DECISIONS.md` if any permanent decisions were made.
3. Move session entries older than the last 5 from `tasks/TASKS.md` to `tasks/ARCHIVE.md`.
4. Update `memory/PROJECT_MEMORY.md` if any stable facts were learned.
5. Update `CHEATSHEET.txt` if commands, files, or trigger phrases changed.

---

## Session Management

| File | Purpose |
| --- | --- |
| `tasks/TASKS.md` | Current state: position, open items, last 5 sessions |
| `tasks/DECISIONS.md` | Permanent locked decisions |
| `tasks/ARCHIVE.md` | Session history older than last 5 |

---

## Rules

- Do not create or maintain `README.md` files.
- Keep `CHEATSHEET.txt` up to date whenever commands, flags, or trigger phrases change.
- Generated code and helper scripts go in `scripts/`.
- Input and reference files go in `data/current/`. Older or superseded versions go in `data/archive/`.
- Generated artifacts go in `output/`.

---

## Folder Structure

```text
[project_name]/
├── AGENTS.md
├── CHEATSHEET.txt
├── requirements.txt
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

---

## Git Rules

Do commit:

- Everything in `docs/`
- Everything in `data/`
- Everything in `scripts/`

Do not commit:

- Machine-generated files in `output/` unless explicitly requested

If a `.gitignore` exists:

- Ensure it does not exclude `docs/` or Office/PDF file types
- Only `output/` should be ignored by default

---

## Tasks

### Task #1 — [Task Name]

**Trigger:**
`Perform task #1`

**Steps:**

1. Re-read `docs/Requirements.docx`.
2. Read relevant source files in `data/current/`.
3. Do the work.
4. Write or update scripts in `scripts/`.
5. Run the script and save output to `output/`.
