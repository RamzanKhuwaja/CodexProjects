# codex_pdf2md Requirements

Last updated: 2026-04-12

## 1. Purpose

Build a local PDF-to-Markdown pipeline for Nahj al-Balagha related books.

The pipeline must produce durable, reviewable source assets that are easy to:

- read
- quote
- search
- compare across books
- upload into a ChatGPT project library

The phase 1 goal is clean, traceable source material. It is not to build a full retrieval or RAG system.

## 2. Phase 1 Non-Goals

Phase 1 does not require:

- vector databases
- a full RAG stack
- embeddings-based retrieval
- graph tooling
- semantic search infrastructure beyond Markdown and CSV outputs

These may be added later, but they are out of scope for phase 1.

## 3. Source Types And Language Support

The pipeline must support:

- digitally born PDFs
- scanned PDFs that require OCR
- English books
- Arabic books

### 3.1 Source-Type Policy

Digitally born PDFs are the primary happy path in phase 1.

Scanned PDFs are supported in phase 1, but conservatively:

- OCR is allowed and required when needed
- raw OCR text must be preserved
- page traceability must be preserved where possible
- QC logs must surface uncertainty clearly
- aggressive OCR cleanup is not required in phase 1

OCR must be implemented through a pluggable backend so the engine can be changed later.

### 3.2 Language Policy

English books are the main readable and writable corpus.

Arabic books are the reference and verification corpus unless extraction quality is very high.

Core rule:

- English for writing
- Arabic for checking

## 4. Inputs And Canonical Metadata

### 4.1 Input PDFs

Source PDFs live in:

- `data/current/`

### 4.2 Manual Book Manifest

Stable `book_id` assignment must come from the manual manifest:

- `data/metadata/books_manifest.csv`

This manifest is the source of truth for book identity.

Requirements:

- Use simple stable IDs such as `B001`, `B002`, `B003`
- Do not derive identity from filenames
- New books may be assigned the next available ID
- New assignments must be written back to the manifest
- A book's `book_id` must remain stable across reruns unless its source identity changes

## 5. Required Outputs Per Book

For each processed PDF, the pipeline must produce:

- original PDF preserved unchanged
- raw extracted text
- one cleaned book-level Markdown file
- zero or more passage-level Markdown files
- one `books.csv` row
- zero or more `passages.csv` rows
- one review log
- optional machine-readable QC output if useful

## 6. Output Layout

Generated outputs should be organized under `output/`:

- `output/raw_text/`
- `output/book_markdown/`
- `output/passage_markdown/<book_id>/`
- `output/metadata/`
- `output/review_logs/`

At minimum:

- `output/metadata/books.csv`
- `output/metadata/passages.csv`

The source PDF must never be modified or overwritten.

## 7. Processing Pipeline

The intended phase 1 flow is:

`PDF -> extraction/OCR -> raw text -> cleaned book Markdown -> passage Markdown -> metadata -> QC logs`

The pipeline must keep raw extraction separate from cleaned output.

## 8. Book-Level Markdown Requirements

Each book must produce one cleaned Markdown file.

This file must:

- contain structured metadata at the top
- contain the book title
- include language and text-direction metadata
- preserve headings where they can be detected reliably
- preserve numbering where relevant
- preserve section hierarchy where recoverable
- preserve page markers whenever page boundaries can be recovered
- flag uncertain text explicitly instead of guessing

Example page marker styles may include:

- `[[page_012]]`
- `<!-- page: 12 -->`

The exact marker style may be chosen in implementation, but it must be consistent.

## 9. Passage-Level Markdown Requirements

Passages are smaller logical units derived from a book.

A passage may represent:

- a sermon
- a letter
- a wisdom saying
- a commentary section
- a thematic subsection
- a translator or editor note linked to a section

Each passage file must include metadata at the top, including:

- `passage_id`
- `book_id`
- title or section title if known
- `language`
- `text_direction`
- `page_start` when known
- `page_end` when known
- Nahj category and number when known

## 10. Passage Splitting Rules

Passage splitting must use meaningful structural boundaries whenever possible.

Priority order:

- explicit headings
- sermon numbers
- letter numbers
- wisdom or saying numbers
- commentary section boundaries
- clear thematic subheadings
- coherent paragraph groups if no stronger structure exists

Fixed-size chunking is allowed only as a documented fallback.

### 10.1 Arabic Splitting Rule

Arabic passage splitting is allowed only when headings, numbering, or structure are detected confidently.

If Arabic structure is not reliable, the pipeline must:

- keep Arabic output at the book level
- still produce metadata
- still produce QC logs
- avoid forcing fine-grained passage segmentation

## 11. Stable ID Requirements

Each book must have a stable `book_id`.

Each passage must have a stable `passage_id`.

Requirements:

- IDs must be unique
- passage IDs must link back to their parent `book_id`
- IDs must remain stable across reruns if the source and segmentation have not changed

## 12. Extraction Requirements

The extraction stage must:

- support direct extraction from digitally born PDFs
- support OCR for scanned PDFs
- preserve raw extracted text
- preserve page-level traceability where possible
- capture OCR confidence or equivalent quality signals if available
- log extraction issues

The pipeline must not silently discard difficult text.

## 13. Cleaning Rules

### 13.1 General Rules

Apply cleanup only where safe.

Preferred priorities:

- accuracy over prettiness
- traceability over stylistic normalization
- flagging over guessing

Where confidence is high, the pipeline may:

- remove repeated headers and footers
- remove obvious page-number noise
- fix broken line wraps
- merge paragraph fragments
- preserve headings
- preserve numbering
- preserve section hierarchy

### 13.2 English Rules

English cleanup may be moderately assertive when confidence is high.

Allowed behavior:

- header/footer removal
- paragraph reconstruction
- broken-line merging
- heading normalization
- safe punctuation normalization
- removal of obvious layout noise

### 13.3 Arabic Rules

Arabic cleanup must be conservative.

Required behavior:

- preserve wording as closely as possible
- avoid aggressive punctuation or orthographic normalization
- preserve RTL-safe text ordering
- preserve page traceability carefully
- mark unclear OCR rather than guessing
- prefer minimal normalization over readability-driven rewriting

## 14. Uncertainty Handling

Uncertain text must remain visible.

The pipeline must never silently invent or auto-correct uncertain text.

Implementation may use markers such as:

- `[unclear]`
- `[ocr? ... ]`
- HTML comments
- structured review annotations

The exact format may be chosen later, but uncertainty must remain explicit in outputs or logs.

## 15. Page Traceability Requirements

Every processed book must preserve page markers whenever page boundaries can be detected.

Rules:

- page markers are mandatory when page boundaries are recoverable
- page markers may be omitted only when boundaries genuinely cannot be recovered
- missing recoverable page markers must be logged as a QC issue

Every passage must be traceable back to:

- the source PDF
- the parent `book_id`
- a page number or page range when recoverable
- a source heading or section title when available

## 16. Metadata Requirements

### 16.1 `books.csv`

Each book must produce one row in `books.csv`.

Minimum columns:

- `book_id`
- `full_title`
- `author`
- `translator_editor`
- `language`
- `text_direction`
- `pdf_filename`
- `book_md_filename`
- `ocr_required`
- `ocr_confidence`
- `normalization_level`
- `review_priority`
- `notes`

### 16.2 `passages.csv`

Each passage must produce one row in `passages.csv` when passage files are created.

Minimum columns:

- `passage_id`
- `book_id`
- `language`
- `section_title`
- `page_start`
- `page_end`
- `filename`
- `nahj_category`
- `nahj_number`
- `ocr_confidence`
- `needs_manual_review`
- `notes`

## 17. QC And Review Log Requirements

Each processed book must produce a review log.

The review log must identify issues such as:

- pages with poor OCR confidence
- suspicious characters
- missing or ambiguous headings
- unusual formatting problems
- possible paragraph merge errors
- possible Arabic RTL issues
- sections that require manual review
- missing page-boundary recovery when it should have been possible

Machine-readable QC output is optional in phase 1.

## 18. CLI Requirements

The main entry point should be:

- `scripts/pdf_to_md.py`

Behavior requirements:

- default mode must process a single file
- batch processing must require an explicit flag such as `--all`
- reruns must not overwrite existing generated outputs by default
- overwriting must require an explicit `--overwrite` flag

The exact CLI syntax may evolve, but these behaviors are required.

## 19. Acceptance Criteria

Phase 1 is acceptable when all of the following are true:

- a user can place a PDF in `data/current/`
- a local command can process that file from the project root
- the original PDF remains unchanged
- raw text is saved separately from cleaned output
- one book-level Markdown file is created
- passage files are created when structure is reliable
- English output is reasonably readable
- Arabic output is conservative and does not silently corrupt text
- metadata files are created or updated
- QC logs are created
- outputs remain traceable back to source pages when recoverable

## 20. Later Enhancements

Possible future enhancements include:

- embeddings or vector indexes
- SQLite or similar metadata storage
- semantic search
- cross-source alignment tables
- Obsidian export
- graph relationships between passages and themes
- automated matching of the same Nahj passage across books

These are explicitly later-phase items and are not required for phase 1.
