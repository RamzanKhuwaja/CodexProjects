# codex_pdf2md — Task Tracker

> This file tracks current state only — position, open items, session log.
> Permanent decisions live in `DECISIONS.md`. Older sessions live in `ARCHIVE.md`.
>
> **Cleanup (do at each session start):** Move sessions older than the last 5 to `ARCHIVE.md`.
> Delete checked open items. Keep this file readable in under 60 seconds.
>
> **To open a session:** `start session`
> **To close a session:** `end session`
 
## Current Position

**Status:** Active.
**Last session:** 2026-04-12 — consolidated the project requirements into `docs/Requirements.md`, updated project instructions, and removed redundant requirement files.
**Next step:** Create `data/metadata/books_manifest.csv`, then scaffold `scripts/pdf_to_md.py` around single-file processing with explicit `--all` and `--overwrite` behavior.

## Open Items

- Choose the first PDF-to-Markdown extraction approach and dependencies.
- Create the manual manifest at `data/metadata/books_manifest.csv`.
- Scaffold the first conversion script against `docs/Requirements.md`.

## Session Log

### Session 1 — 2026-04-12

**Focus:** Bootstrapped `codex_pdf2md` from `_project_template` and replaced template placeholders with PDF-to-Markdown starter context.
**Decisions:** Project starts from the standard Codex template and will use `data/current/` for input PDFs and `output/` for generated Markdown.
**Next:** Add the real requirements doc and build the initial conversion workflow.

### Session 2 — 2026-04-12

**Focus:** Reviewed the brainstorming requirements, converted them into a locked phase-1 spec, standardized the canonical requirements file as `docs/Requirements.md`, and removed redundant requirement documents.
**Decisions:** Use `docs/Requirements.md` as the single source of truth; use `data/metadata/books_manifest.csv` as the book ID manifest; default CLI behavior is single-file mode; batch mode requires an explicit flag; overwriting generated output requires `--overwrite`; OCR backend remains pluggable.
**Next:** Create the manifest file and implement the initial single-file conversion script.
