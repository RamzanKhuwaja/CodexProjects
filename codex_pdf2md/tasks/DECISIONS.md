# codex_pdf2md — Permanent Decisions

> Permanent, locked decisions live here. Never put decisions in TASKS.md.
> When a decision changes, update the entry here.

## Architecture

- Project structure is initialized from `_project_template`.
- Input PDFs live in `data/current/`.
- Generated Markdown files live in `output/`.
- Canonical requirements source should be `docs/Requirements.md`.
- Stable book IDs come from `data/metadata/books_manifest.csv`, not filenames.
- Default CLI behavior should be single-file processing, with batch mode requiring an explicit flag such as `--all`.
- Generated outputs must not be overwritten by default; overwriting requires an explicit `--overwrite` flag.
- OCR support is required in phase 1 for scanned PDFs, but the OCR engine must remain pluggable and not be fixed in the requirements.

## Business Rules

- English books are the main readable and writable corpus.
- Arabic books are the reference and verification corpus unless extraction quality is very high.
- Arabic passage splitting is allowed only when headings, numbering, or structure are detected confidently.
- Page markers are mandatory whenever page boundaries can be detected; missing recoverable page markers must be treated as a QC issue.
