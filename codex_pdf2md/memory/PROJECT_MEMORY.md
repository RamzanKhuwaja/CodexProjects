# codex_pdf2md — Project Memory

## Purpose

- Convert PDF files into Markdown files.

## Stable Facts

- New project initialized from `_project_template` on 2026-04-12.
- Source PDF files should live in `data/current/`.
- Generated Markdown files should be written to `output/`.
- Canonical requirements file should be `docs/Requirements.md`.
- Manual book ID manifest should live at `data/metadata/books_manifest.csv`.
- Default script behavior should be single-file processing; batch mode should require an explicit flag.
- Generated outputs should not be overwritten unless an explicit overwrite flag is provided.
- OCR support should be pluggable so the backend can be swapped later.

## Workflow Pattern

- Define requirements in `docs/Requirements.md`, register books in `data/metadata/books_manifest.csv`, place PDFs in `data/current/`, then run the project conversion script from the project root.

## Known Risks Or Recurring Flags

- PDF extraction quality can vary by source document structure.
- Arabic extraction should be handled conservatively and only split into passages when structure is confidently detected.
