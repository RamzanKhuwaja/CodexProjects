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
- On `start session`, report status and wait for Ramzan's next instruction before doing implementation work.
- Primary PDF extraction should use PyMuPDF.
- Preferred OCR path is OCRmyPDF when Tesseract is available; otherwise use PyMuPDF integrated OCR if Tesseract is available.
- This machine now has a user-local Tesseract 5.5 install under `~/scoop/apps/tesseract/current` with `eng` and `ara` language data.
- Passage splitting should prefer explicit numbered section markers such as `1.1`, `2.23`, and `3.245` when a source provides them.
- The pipeline now writes machine-readable QC outputs under `output/qc/` and PNG snapshots for manual-review pages under `output/review_images/<book_id>/`.
- Arabic-heavy pages now bypass the broken PDF text layer and use direct Tesseract OCR so the stored Markdown is closer to logical Arabic order.
- `passages.csv` now carries coarse OCR confidence plus review notes for weak sections instead of only a boolean manual-review flag.

## Workflow Pattern

- Define requirements in `docs/Requirements.md`, register books in `data/metadata/books_manifest.csv`, place PDFs in `data/current/`, then run the project conversion script from the project root.

## Known Risks Or Recurring Flags

- PDF extraction quality can vary by source document structure.
- Arabic extraction should be handled conservatively and only split into passages when structure is confidently detected.
