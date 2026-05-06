from __future__ import annotations

import argparse
import csv
import hashlib
import importlib.util
import json
import os
import re
import shutil
import subprocess
import sys
import tempfile
from dataclasses import dataclass, replace
from pathlib import Path

import pymupdf


PROJECT_ROOT = Path(__file__).resolve().parent.parent
DEFAULT_INPUT_DIR = PROJECT_ROOT / "data" / "current"
DEFAULT_MANIFEST_PATH = PROJECT_ROOT / "data" / "metadata" / "books_manifest.csv"
DEFAULT_OUTPUT_ROOT = PROJECT_ROOT / "output"
PAGE_MARKER_TEMPLATE = "[[page_{page_number:03d}]]"
DEFAULT_OCR_LANGUAGES = "eng+ara"
DEFAULT_OCR_DPI = 300

MANIFEST_COLUMNS = [
    "book_id",
    "source_relpath",
    "source_sha256",
    "full_title",
    "author",
    "translator_editor",
    "language",
    "text_direction",
    "normalization_level",
    "notes",
]

BOOKS_COLUMNS = [
    "book_id",
    "full_title",
    "author",
    "translator_editor",
    "language",
    "text_direction",
    "pdf_filename",
    "book_md_filename",
    "ocr_required",
    "ocr_confidence",
    "normalization_level",
    "review_priority",
    "notes",
]

PASSAGES_COLUMNS = [
    "passage_id",
    "book_id",
    "language",
    "section_title",
    "page_start",
    "page_end",
    "filename",
    "nahj_category",
    "nahj_number",
    "ocr_confidence",
    "needs_manual_review",
    "notes",
]

QC_PAGE_COLUMNS = [
    "page_number",
    "language",
    "flags",
    "manual_review",
    "ocr_required",
    "ocr_used",
    "raw_char_count",
    "cleaned_char_count",
    "warnings",
    "review_image",
]


@dataclass(frozen=True)
class ManifestEntry:
    book_id: str
    source_relpath: str
    source_sha256: str
    full_title: str
    author: str
    translator_editor: str
    language: str
    text_direction: str
    normalization_level: str
    notes: str

    @classmethod
    def from_row(cls, row: dict[str, str]) -> "ManifestEntry":
        data = {column: (row.get(column, "") or "").strip() for column in MANIFEST_COLUMNS}
        return cls(**data)

    def to_row(self) -> dict[str, str]:
        return {column: getattr(self, column) for column in MANIFEST_COLUMNS}


@dataclass(frozen=True)
class PageResult:
    page_number: int
    raw_text: str
    cleaned_text: str
    ocr_required: bool
    ocr_used: bool
    arabic_direct_ocr_used: bool
    warnings: list[str]


@dataclass(frozen=True)
class PassageRecord:
    passage_id: str
    book_id: str
    section_marker: str
    section_title: str
    category: str
    nahj_number: str
    page_start: int | None
    page_end: int | None
    filename: str
    content: str


@dataclass(frozen=True)
class OcrRuntime:
    ocrmypdf_python_available: bool
    pypdfium2_python_available: bool
    tesseract_executable: str | None
    ghostscript_executable: str | None
    tessdata_dir: str | None

    def can_run_ocrmypdf(self) -> bool:
        return bool(
            self.ocrmypdf_python_available
            and self.tesseract_executable
            and (self.pypdfium2_python_available or self.ghostscript_executable)
        )

    def can_run_pymupdf_ocr(self) -> bool:
        return bool(self.tesseract_executable)


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Convert project PDF files into traceable Markdown outputs."
    )
    selection = parser.add_mutually_exclusive_group(required=True)
    selection.add_argument(
        "--input",
        type=Path,
        help="Path to a single PDF file. Relative paths are resolved from the project root.",
    )
    selection.add_argument(
        "--all",
        action="store_true",
        help="Process every PDF found in data/current.",
    )
    parser.add_argument(
        "--manifest",
        type=Path,
        default=DEFAULT_MANIFEST_PATH,
        help="CSV manifest used for stable book IDs.",
    )
    parser.add_argument(
        "--output-root",
        type=Path,
        default=DEFAULT_OUTPUT_ROOT,
        help="Root directory for generated outputs.",
    )
    parser.add_argument(
        "--overwrite",
        action="store_true",
        help="Allow existing generated book outputs to be replaced.",
    )
    parser.add_argument(
        "--ocr-mode",
        choices=["auto", "always", "off"],
        default="auto",
        help="OCR strategy. 'auto' OCRs only weak pages, 'always' forces OCR, 'off' disables OCR.",
    )
    parser.add_argument(
        "--ocr-languages",
        default=DEFAULT_OCR_LANGUAGES,
        help="OCR language codes joined by '+', for example 'eng+ara'.",
    )
    parser.add_argument(
        "--ocr-dpi",
        type=int,
        default=DEFAULT_OCR_DPI,
        help="Rendering DPI used for OCR when PyMuPDF integrated OCR is used.",
    )
    return parser.parse_args()


def resolve_project_path(path: Path) -> Path:
    return path if path.is_absolute() else (PROJECT_ROOT / path)


def ensure_csv(path: Path, columns: list[str]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    if path.exists():
        return
    with path.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=columns)
        writer.writeheader()


def load_manifest(path: Path) -> list[ManifestEntry]:
    ensure_csv(path, MANIFEST_COLUMNS)
    with path.open("r", encoding="utf-8", newline="") as handle:
        reader = csv.DictReader(handle)
        return [ManifestEntry.from_row(row) for row in reader]


def write_manifest(path: Path, entries: list[ManifestEntry]) -> None:
    ensure_csv(path, MANIFEST_COLUMNS)
    with path.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=MANIFEST_COLUMNS)
        writer.writeheader()
        for entry in sorted(entries, key=lambda item: item.book_id):
            writer.writerow(entry.to_row())


def file_sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def project_relative_string(path: Path) -> str:
    resolved = path.resolve()
    try:
        return resolved.relative_to(PROJECT_ROOT).as_posix()
    except ValueError:
        return resolved.as_posix()


def next_book_id(entries: list[ManifestEntry]) -> str:
    numeric_ids = []
    for entry in entries:
        match = re.fullmatch(r"B(\d+)", entry.book_id)
        if match:
            numeric_ids.append(int(match.group(1)))
    return f"B{(max(numeric_ids, default=0) + 1):03d}"


def get_or_create_manifest_entry(
    manifest_path: Path, pdf_path: Path
) -> tuple[ManifestEntry, list[ManifestEntry], bool]:
    entries = load_manifest(manifest_path)
    source_relpath = project_relative_string(pdf_path)
    source_sha256 = file_sha256(pdf_path)

    for entry in entries:
        if entry.source_sha256 and entry.source_sha256 == source_sha256:
            updated = replace(entry, source_relpath=source_relpath)
            entries = [updated if item.book_id == entry.book_id else item for item in entries]
            write_manifest(manifest_path, entries)
            return updated, entries, False

    for entry in entries:
        if entry.source_relpath == source_relpath:
            updated = replace(entry, source_sha256=source_sha256)
            entries = [updated if item.book_id == entry.book_id else item for item in entries]
            write_manifest(manifest_path, entries)
            return updated, entries, False

    created = ManifestEntry(
        book_id=next_book_id(entries),
        source_relpath=source_relpath,
        source_sha256=source_sha256,
        full_title="",
        author="",
        translator_editor="",
        language="",
        text_direction="",
        normalization_level="",
        notes="Auto-created during first processing run.",
    )
    entries.append(created)
    write_manifest(manifest_path, entries)
    return created, entries, True


def resolve_inputs(args: argparse.Namespace) -> list[Path]:
    if args.input:
        pdf_path = resolve_project_path(args.input).resolve()
        if not pdf_path.exists():
            raise FileNotFoundError(f"Input PDF not found: {pdf_path}")
        if pdf_path.suffix.lower() != ".pdf":
            raise ValueError(f"Input path is not a PDF: {pdf_path}")
        return [pdf_path]

    input_dir = DEFAULT_INPUT_DIR
    pdf_paths = sorted(path.resolve() for path in input_dir.iterdir() if path.is_file() and path.suffix.lower() == ".pdf")
    if not pdf_paths:
        raise FileNotFoundError(f"No PDF files found in {input_dir}")
    return pdf_paths


def detect_tessdata_dir(tesseract_executable: str | None) -> str | None:
    candidates: list[Path] = []
    for env_var in ("CODEX_PDF2MD_TESSDATA_DIR", "TESSDATA_PREFIX"):
        value = (os.environ.get(env_var) or "").strip()
        if value:
            env_path = Path(value).expanduser()
            candidates.append(env_path)
            candidates.append(env_path / "tessdata")

    if tesseract_executable:
        exe_path = Path(tesseract_executable).resolve()
        candidates.extend(
            [
                exe_path.parent / "tessdata",
                exe_path.parent.parent / "tessdata",
                Path.home() / "scoop" / "persist" / "tesseract" / "tessdata",
                Path.home() / "scoop" / "apps" / "tesseract" / "current" / "tessdata",
            ]
        )

    for candidate in candidates:
        if candidate.exists() and any(candidate.glob("*.traineddata")):
            return str(candidate)
    return None


def find_executable(command: str, extra_candidates: list[Path]) -> str | None:
    discovered = shutil.which(command)
    if discovered:
        return discovered
    for candidate in extra_candidates:
        if not str(candidate).strip() or str(candidate) == ".":
            continue
        if candidate.exists():
            return str(candidate.resolve())
    return None


def discover_ocr_runtime() -> OcrRuntime:
    local_app_data = Path(os.environ.get("LOCALAPPDATA", ""))
    program_files = Path(os.environ.get("ProgramFiles", ""))
    program_files_x86 = Path(os.environ.get("ProgramFiles(x86)", ""))

    tesseract_executable = find_executable(
        "tesseract",
        [
            Path(os.environ.get("CODEX_PDF2MD_TESSERACT_EXE", "")),
            Path.home() / "scoop" / "apps" / "tesseract" / "current" / "tesseract.exe",
            local_app_data / "Programs" / "Tesseract-OCR" / "tesseract.exe",
            program_files / "Tesseract-OCR" / "tesseract.exe",
            program_files_x86 / "Tesseract-OCR" / "tesseract.exe",
        ],
    )
    ghostscript_executable = find_executable(
        "gswin64c",
        [
            Path(os.environ.get("CODEX_PDF2MD_GHOSTSCRIPT_EXE", "")),
            Path.home() / "scoop" / "apps" / "ghostscript" / "current" / "bin" / "gswin64c.exe",
            program_files / "gs" / "bin" / "gswin64c.exe",
            program_files_x86 / "gs" / "bin" / "gswin64c.exe",
        ],
    ) or shutil.which("gs")
    return OcrRuntime(
        ocrmypdf_python_available=importlib.util.find_spec("ocrmypdf") is not None,
        pypdfium2_python_available=importlib.util.find_spec("pypdfium2") is not None,
        tesseract_executable=tesseract_executable,
        ghostscript_executable=ghostscript_executable,
        tessdata_dir=detect_tessdata_dir(tesseract_executable),
    )


def build_ocr_environment(runtime: OcrRuntime) -> dict[str, str]:
    environment = dict(os.environ)

    extra_path_entries: list[str] = []
    if runtime.tesseract_executable:
        extra_path_entries.append(str(Path(runtime.tesseract_executable).resolve().parent))
    if runtime.ghostscript_executable:
        extra_path_entries.append(str(Path(runtime.ghostscript_executable).resolve().parent))
    if extra_path_entries:
        environment["PATH"] = os.pathsep.join(extra_path_entries + [environment.get("PATH", "")])

    if runtime.tessdata_dir:
        tessdata_prefix = str(Path(runtime.tessdata_dir).resolve())
        if not tessdata_prefix.endswith(("\\", "/")):
            tessdata_prefix = f"{tessdata_prefix}{os.sep}"
        environment["TESSDATA_PREFIX"] = tessdata_prefix

    return environment


BIDI_CONTROL_PATTERN = re.compile(r"[\u200e\u200f\u202a-\u202e\u2066-\u2069]")


def strip_bidi_controls(text: str) -> str:
    return BIDI_CONTROL_PATTERN.sub("", text)


def arabic_letter_ratio(text: str) -> float:
    letters = [character for character in text if character.isalpha()]
    if not letters:
        return 0.0
    arabic_letters = [character for character in letters if "\u0600" <= character <= "\u06FF"]
    return len(arabic_letters) / len(letters)


def detect_language(text: str) -> str:
    letters = [character for character in text if character.isalpha()]
    if not letters:
        return "en"
    arabic_letters = [character for character in letters if "\u0600" <= character <= "\u06FF"]
    arabic_ratio = len(arabic_letters) / len(letters)
    if 0.15 < arabic_ratio < 0.85:
        return "mixed"
    if arabic_ratio >= 0.85:
        return "ar"
    return "en"


def default_text_direction(language: str) -> str:
    if language == "mixed":
        return "mixed"
    return "rtl" if language == "ar" else "ltr"


def default_normalization_level(language: str) -> str:
    return "conservative" if language in {"ar", "mixed"} else "moderate"


def normalize_whitespace(text: str) -> str:
    text = text.replace("\r\n", "\n").replace("\r", "\n")
    lines = [line.rstrip() for line in text.split("\n")]
    compacted: list[str] = []
    previous_blank = False
    for line in lines:
        if line.strip():
            compacted.append(line.strip())
            previous_blank = False
            continue
        if not previous_blank:
            compacted.append("")
        previous_blank = True
    return "\n".join(compacted).strip()


FORWARD_ARABIC_MARKERS = {
    "الله",
    "بسم",
    "الرحيم",
    "الرحمن",
    "السلام",
    "عليه",
    "الذين",
    "التي",
    "المؤمنين",
    "الأئمة",
    "خصائص",
    "يتضمن",
    "آخرها",
    "المواعظ",
    "الحمد",
    "معرفته",
    "التصديق",
    "توحيده",
    "الإخلاص",
    "الصفات",
    "الموصوف",
    "سبحانه",
    "أشار",
    "جهله",
    "موجود",
    "الحركات",
    "الآلات",
    "منظور",
    "خلقه",
    "متوحد",
}

REVERSED_ARABIC_MARKERS = {
    "هللا",
    "مسب",
    "ميحرلا",
    "نمحرلا",
    "مالسلا",
    "هيلع",
    "نيذلا",
    "يتلا",
    "نينمؤملا",
    "ةمئألا",
    "صئاصخ",
    "نمضتي",
    "اهرخآ",
    "ظعاوملا",
    "دمحلا",
    "هتفرعم",
    "قيدصتلا",
    "هديحوت",
    "صالخإلا",
    "تافصلا",
    "فوصوملا",
    "هناحبس",
    "راشأ",
    "هلهج",
    "دوجوم",
    "تاكرحلا",
    "تالآلا",
    "روظنم",
    "هقلخ",
    "دحوتم",
}


def arabic_token_counts(text: str) -> tuple[int, int]:
    tokens = re.findall(r"[\u0600-\u06FF]+", text)
    forward_hits = sum(1 for token in tokens if token in FORWARD_ARABIC_MARKERS)
    reversed_hits = sum(1 for token in tokens if token in REVERSED_ARABIC_MARKERS)
    return forward_hits, reversed_hits


def line_has_reversed_arabic_markers(line: str) -> bool:
    forward_hits, reversed_hits = arabic_token_counts(line)
    stripped = line.strip()
    if stripped.startswith(("ميحرلا", "مسب", "هتفرعم", "دمحلا", "هديحوت")):
        return True
    return reversed_hits >= 1 and reversed_hits >= forward_hits


def repair_visual_order_arabic_line(line: str) -> str:
    stripped = line.strip()
    if not stripped:
        return line

    prefix = ""
    remainder = stripped
    prefix_match = re.match(r"^(?P<prefix>\d+(?:\.\d+)*)(?=[^\d\s])(?P<rest>.+)$", stripped)
    if prefix_match:
        prefix = prefix_match.group("prefix")
        remainder = prefix_match.group("rest").strip()

    repaired = remainder[::-1].strip()
    if prefix:
        return f"{prefix} {repaired}".strip()
    return repaired


def repair_arabic_visual_order(text: str, language: str, ocr_used: bool) -> tuple[str, bool]:
    if language not in {"ar", "mixed"}:
        return text, False

    repaired_lines: list[str] = []
    repaired_any = False
    for line in text.split("\n"):
        line_language = detect_language(line)
        arabic_letters = sum(1 for char in line if "\u0600" <= char <= "\u06FF")
        latin_letters = sum(1 for char in line if "A" <= char <= "Z" or "a" <= char <= "z")
        if (
            line_language in {"ar", "mixed"}
            and arabic_letters >= 8
            and arabic_letters > latin_letters * 2
            and line_has_reversed_arabic_markers(line)
        ):
            repaired_line = repair_visual_order_arabic_line(line)
            repaired_lines.append(repaired_line)
            repaired_any = repaired_any or repaired_line != line
            continue
        repaired_lines.append(line)

    repaired_text = "\n".join(repaired_lines).strip()
    return repaired_text or text, repaired_any


def is_noise_line(line: str) -> bool:
    stripped = line.strip()
    if not stripped:
        return False

    lowered = stripped.casefold()
    standalone_noise = {
        "text and translation",
        "∵",
        "(cont.)",
        "(d. 406/1015)",
        "text no. references",
        "additional sayings",
        "raḍī’s conclusion",
        "nahj al-balāghah",
        "the wisdom and eloquence of ʿalī",
        "compiled by al-sharīf al-raḍī (d. 406/1015)",
    }
    if lowered in standalone_noise:
        return True

    running_headings = [
        r"^\d+\s+text and translation$",
        r"^chapter\s+[123]:\s+(orations|letters|sayings)\s+\d+$",
        r"^(additional sayings|raḍī’s conclusion)\s+(p\.\s*)?\d+$",
        r"^(introduction|detailed contents|appendix of sources for the texts of nahj al-balāghah|glossary of names, places, and terms|bibliography|index of names and places|index of terms|index of qurʾan, hadith, poetry, and proverbs|index of religious and ethical concepts)\s+\d+$",
    ]
    if any(re.fullmatch(pattern, lowered) for pattern in running_headings):
        return True

    if lowered.startswith("© tahera qutbuddin, 2024"):
        return True
    if lowered.startswith("compiled by al-sharīf al-raḍī"):
        return True
    if lowered.startswith("this is an open access title distributed"):
        return True
    if lowered.startswith("this is an open access chapter distributed"):
        return True
    if "| doi:" in lowered:
        return True
    return False


def remove_noise_lines(text: str) -> str:
    cleaned_lines = [line for line in text.split("\n") if not is_noise_line(line)]
    return "\n".join(cleaned_lines).strip()


def clean_direct_tesseract_text(text: str) -> str:
    normalized = normalize_whitespace(strip_bidi_controls(text))
    cleaned_lines: list[str] = []
    for line in normalized.splitlines():
        cleaned = line.strip().strip("|")
        cleaned = re.sub(r"^[\-–—]+\s*", "", cleaned)
        if re.search(r"[\u0600-\u06FF]", cleaned):
            cleaned = re.sub(r"\s+[A-Za-z]{1,3}$", "", cleaned)
            cleaned = re.sub(r"^[A-Za-z]{1,3}\s+", "", cleaned)
        cleaned_lines.append(cleaned)
    return normalize_whitespace("\n".join(cleaned_lines))


def is_heading_like(line: str) -> bool:
    if len(line) <= 80 and line.endswith(":"):
        return True
    if re.fullmatch(r"[A-Z0-9 ,'\-]{4,}", line):
        return True
    if re.match(r"^(\d+[\.\)]|[IVXLCDM]+\.)\s+", line):
        return True
    return False


def should_join_english_lines(previous: str, current: str) -> bool:
    if not previous or not current:
        return False
    if is_heading_like(previous) or is_heading_like(current):
        return False
    if previous.endswith(("-", "/")):
        return True
    if previous.endswith((".", "?", "!", ":", ";")):
        return False
    return bool(re.match(r"^[a-z0-9(\"']", current))


def clean_page_text(text: str, language: str) -> str:
    normalized = remove_noise_lines(normalize_whitespace(text))
    if not normalized:
        return ""
    if language in {"ar", "mixed"}:
        return normalized

    paragraphs = normalized.split("\n\n")
    cleaned_paragraphs: list[str] = []
    for paragraph in paragraphs:
        lines = [line.strip() for line in paragraph.splitlines() if line.strip()]
        if not lines:
            continue
        merged = [lines[0]]
        for line in lines[1:]:
            if should_join_english_lines(merged[-1], line):
                separator = "" if merged[-1].endswith("-") else " "
                merged[-1] = merged[-1].removesuffix("-") + separator + line
            else:
                merged.append(line)
        cleaned_paragraphs.append("\n".join(merged))
    return "\n\n".join(cleaned_paragraphs).strip()


def should_run_direct_arabic_ocr(text: str) -> bool:
    if arabic_letter_ratio(text) < 0.45:
        return False
    return True


def run_direct_tesseract_page_ocr(
    page: pymupdf.Page,
    runtime: OcrRuntime,
    ocr_languages: str,
    ocr_dpi: int,
) -> str:
    if not runtime.tesseract_executable:
        return ""

    with tempfile.NamedTemporaryFile(prefix="codex_pdf2md_page_", suffix=".png", delete=False) as handle:
        image_path = Path(handle.name)

    try:
        page.get_pixmap(dpi=max(ocr_dpi, 300), alpha=False).save(image_path)
        completed = subprocess.run(
            [
                runtime.tesseract_executable,
                str(image_path),
                "stdout",
                "-l",
                ocr_languages,
                "--oem",
                "1",
                "--psm",
                "11",
            ],
            capture_output=True,
            text=True,
            encoding="utf-8",
            errors="replace",
            check=False,
            timeout=60 * 5,
            env=build_ocr_environment(runtime),
        )
        if completed.returncode != 0:
            return ""
        return clean_direct_tesseract_text(completed.stdout)
    finally:
        try:
            image_path.unlink()
        except OSError:
            pass


def visible_char_count(text: str) -> int:
    stripped = text.replace("[unclear]", "")
    stripped = re.sub(r"\s+", "", stripped)
    return len(stripped)


def page_flags_for(page: PageResult) -> list[str]:
    flags: list[str] = []
    raw_language = detect_language(page.raw_text)

    if page.ocr_required:
        flags.append("ocr_required")
    if page.ocr_used:
        flags.append("ocr_used")
    if "[unclear]" in page.raw_text or "[unclear]" in page.cleaned_text:
        flags.append("unclear")
    if "\ufffd" in page.raw_text or "\ufffd" in page.cleaned_text:
        flags.append("replacement_char")
    if visible_char_count(page.cleaned_text) < 40:
        flags.append("short_text")
    if raw_language == "ar":
        flags.append("arabic_heavy")
    elif raw_language == "mixed":
        flags.append("mixed_script")
    if page.arabic_direct_ocr_used:
        flags.append("arabic_direct_ocr")
    if page.warnings:
        flags.append("warning")

    deduped: list[str] = []
    seen: set[str] = set()
    for flag in flags:
        if flag not in seen:
            deduped.append(flag)
            seen.add(flag)
    return deduped


def page_needs_manual_review(page: PageResult, flags: list[str]) -> bool:
    review_flags = {"unclear", "replacement_char", "short_text"}
    if any(flag in review_flags for flag in flags):
        return True
    warning_markers = (
        "extraction returned no usable text",
        "cleaned text is empty after normalization",
    )
    return any(marker in warning.casefold() for warning in page.warnings for marker in warning_markers)


def ocr_confidence_for_page_record(page_record: dict[str, object]) -> str:
    flags = set(page_record["flags"])
    if page_record["manual_review"] or {"unclear", "replacement_char"} & flags:
        return "low"
    if page_record["ocr_used"] or page_record["ocr_required"] or page_record["arabic_direct_ocr_used"]:
        return "medium"
    return "high"


def ocr_confidence_for_page_records(page_records: list[dict[str, object]]) -> str:
    if not page_records:
        return "high"
    confidences = {ocr_confidence_for_page_record(page_record) for page_record in page_records}
    if "low" in confidences:
        return "low"
    if "medium" in confidences:
        return "medium"
    return "high"


def summarize_page_numbers(page_numbers: list[int]) -> str:
    if not page_numbers:
        return ""
    ordered = sorted(set(page_numbers))
    ranges: list[str] = []
    start = ordered[0]
    end = ordered[0]
    for page_number in ordered[1:]:
        if page_number == end + 1:
            end = page_number
            continue
        ranges.append(f"{start}" if start == end else f"{start}-{end}")
        start = end = page_number
    ranges.append(f"{start}" if start == end else f"{start}-{end}")
    return ", ".join(ranges)


def build_qc_pages(
    pages: list[PageResult],
) -> tuple[list[dict[str, object]], dict[int, dict[str, object]]]:
    qc_pages: list[dict[str, object]] = []
    page_lookup: dict[int, dict[str, object]] = {}

    for page in pages:
        flags = page_flags_for(page)
        page_record: dict[str, object] = {
            "page_number": page.page_number,
            "language": detect_language(page.raw_text),
            "flags": flags,
            "manual_review": page_needs_manual_review(page, flags),
            "ocr_required": page.ocr_required,
            "ocr_used": page.ocr_used,
            "arabic_direct_ocr_used": page.arabic_direct_ocr_used,
            "raw_char_count": visible_char_count(page.raw_text),
            "cleaned_char_count": visible_char_count(page.cleaned_text),
            "warnings": list(page.warnings),
            "review_image": "",
        }
        qc_pages.append(page_record)
        page_lookup[page.page_number] = page_record

    return qc_pages, page_lookup


def extract_pages(
    pdf_path: Path,
    runtime: OcrRuntime,
    preferred_language: str = "",
    ocr_mode: str = "auto",
    ocr_languages: str = DEFAULT_OCR_LANGUAGES,
    ocr_dpi: int = DEFAULT_OCR_DPI,
) -> tuple[list[PageResult], dict[str, str], list[str], str]:
    review_notes: list[str] = []
    ocr_environment = build_ocr_environment(runtime)
    document = pymupdf.open(str(pdf_path))
    try:
        metadata = document.metadata or {}
        direct_texts = [
            normalize_whitespace(document.load_page(index).get_text("text", sort=True) or "")
            for index in range(document.page_count)
        ]
    finally:
        document.close()

    needs_ocr_flags = [not text or len(re.sub(r"\s+", "", text)) < 20 or text.count("\ufffd") >= 3 for text in direct_texts]
    wants_ocr = ocr_mode == "always" or (ocr_mode == "auto" and any(needs_ocr_flags))
    extracted_texts = list(direct_texts)
    extraction_engine = "pymupdf"

    if wants_ocr and runtime.can_run_ocrmypdf():
        with tempfile.TemporaryDirectory(prefix="codex_pdf2md_ocrmypdf_") as temp_dir:
            output_pdf = Path(temp_dir) / f"{pdf_path.stem}.searchable.pdf"
            command = [
                sys.executable,
                "-m",
                "ocrmypdf",
                "--output-type",
                "pdf",
                "--language",
                ocr_languages,
                "--rasterizer",
                "pypdfium",
                "-O",
                "0",
            ]
            command.append("--force-ocr" if ocr_mode == "always" else "--skip-text")
            command.extend([str(pdf_path), str(output_pdf)])
            completed = subprocess.run(
                command,
                capture_output=True,
                text=True,
                check=False,
                timeout=60 * 30,
                env=ocr_environment,
            )
            if completed.returncode == 0 and output_pdf.exists():
                processed_document = pymupdf.open(str(output_pdf))
                try:
                    extracted_texts = [
                        normalize_whitespace(processed_document.load_page(index).get_text("text", sort=True) or "")
                        for index in range(processed_document.page_count)
                    ]
                finally:
                    processed_document.close()
                extraction_engine = "ocrmypdf"
                review_notes.append("OCRmyPDF preprocessing was used before text extraction.")
            else:
                details = completed.stderr.strip() or completed.stdout.strip() or "OCRmyPDF failed."
                review_notes.append(f"OCRmyPDF was requested but failed: {details}")

    document = pymupdf.open(str(pdf_path))
    try:
        if extraction_engine != "ocrmypdf" and wants_ocr and runtime.can_run_pymupdf_ocr():
            os.environ.update(ocr_environment)
            for index, needs_ocr in enumerate(needs_ocr_flags):
                if not (ocr_mode == "always" or needs_ocr):
                    continue
                page = document.load_page(index)
                ocr_kwargs = {
                    "language": ocr_languages,
                    "dpi": ocr_dpi,
                    "full": True,
                }
                if runtime.tessdata_dir:
                    ocr_kwargs["tessdata"] = runtime.tessdata_dir
                textpage = page.get_textpage_ocr(**ocr_kwargs)
                extracted_texts[index] = normalize_whitespace(
                    page.get_text("text", textpage=textpage, sort=True) or ""
                )
            extraction_engine = "pymupdf_ocr"
            review_notes.append("PyMuPDF integrated OCR was used on pages that needed it.")
    finally:
        document.close()

    if wants_ocr and extraction_engine == "pymupdf" and not runtime.can_run_pymupdf_ocr():
        review_notes.append(
            "OCR was requested but no usable Tesseract runtime was found for OCRmyPDF or PyMuPDF OCR."
        )

    direct_arabic_ocr_pages: set[int] = set()
    if runtime.tesseract_executable:
        source_document = pymupdf.open(str(pdf_path))
        try:
            for page_number, raw_text in enumerate(extracted_texts, start=1):
                normalized_raw = normalize_whitespace(raw_text)
                if not normalized_raw or not should_run_direct_arabic_ocr(normalized_raw):
                    continue
                direct_ocr_text = run_direct_tesseract_page_ocr(
                    source_document.load_page(page_number - 1),
                    runtime,
                    ocr_languages=ocr_languages,
                    ocr_dpi=ocr_dpi,
                )
                if not direct_ocr_text:
                    continue
                extracted_texts[page_number - 1] = direct_ocr_text
                direct_arabic_ocr_pages.add(page_number)
        finally:
            source_document.close()

    if direct_arabic_ocr_pages:
        review_notes.append(
            "Direct Tesseract OCR replaced extracted text on Arabic-heavy pages: "
            + summarize_page_numbers(sorted(direct_arabic_ocr_pages))
            + "."
        )

    book_language = preferred_language or detect_language("\n".join(extracted_texts))
    pages: list[PageResult] = []
    for page_number, raw_text in enumerate(extracted_texts, start=1):
        warnings: list[str] = []
        ocr_required = ocr_mode == "always" or (ocr_mode == "auto" and needs_ocr_flags[page_number - 1])
        ocr_used = extraction_engine in {"ocrmypdf", "pymupdf_ocr"} and ocr_required
        if ocr_used and extraction_engine == "ocrmypdf":
            warnings.append(f"Page {page_number:03d}: OCRmyPDF preprocessing supplied the extracted text.")
        elif ocr_used and extraction_engine == "pymupdf_ocr":
            warnings.append(f"Page {page_number:03d}: PyMuPDF integrated OCR supplied the extracted text.")
        elif ocr_required:
            warnings.append(
                f"Page {page_number:03d}: text extraction looked weak, but no OCR engine is available on this machine."
            )

        normalized_raw = normalize_whitespace(raw_text)
        if not normalized_raw:
            normalized_raw = "[unclear]"
            warnings.append(f"Page {page_number:03d}: extraction returned no usable text.")

        page_language = (
            preferred_language
            if preferred_language and preferred_language != "mixed"
            else detect_language(normalized_raw)
        )
        cleaned_text = clean_page_text(normalized_raw, page_language)
        arabic_direct_ocr_used = page_number in direct_arabic_ocr_pages
        if not cleaned_text:
            cleaned_text = "[unclear]"
            warnings.append(f"Page {page_number:03d}: cleaned text is empty after normalization.")

        pages.append(
            PageResult(
                page_number=page_number,
                raw_text=normalized_raw,
                cleaned_text=cleaned_text,
                ocr_required=ocr_required,
                ocr_used=ocr_used,
                arabic_direct_ocr_used=arabic_direct_ocr_used,
                warnings=warnings,
            )
        )

    metadata_map = {
        "title": (metadata.get("title") or "").strip(),
        "author": (metadata.get("author") or "").strip(),
    }
    return pages, metadata_map, review_notes, extraction_engine


def build_paths(output_root: Path, book_id: str) -> dict[str, Path]:
    return {
        "raw_text": output_root / "raw_text" / f"{book_id}.txt",
        "book_markdown": output_root / "book_markdown" / f"{book_id}.md",
        "passage_dir": output_root / "passage_markdown" / book_id,
        "review_log": output_root / "review_logs" / f"{book_id}.md",
        "qc_json": output_root / "qc" / f"{book_id}.json",
        "qc_pages_csv": output_root / "qc" / f"{book_id}_pages.csv",
        "review_image_dir": output_root / "review_images" / book_id,
        "books_csv": output_root / "metadata" / "books.csv",
        "passages_csv": output_root / "metadata" / "passages.csv",
    }


def ensure_outputs(paths: dict[str, Path]) -> None:
    for key, path in paths.items():
        if key.endswith("_csv"):
            continue
        if key in {"passage_dir", "review_image_dir"}:
            path.mkdir(parents=True, exist_ok=True)
        else:
            path.parent.mkdir(parents=True, exist_ok=True)
    ensure_csv(paths["books_csv"], BOOKS_COLUMNS)
    ensure_csv(paths["passages_csv"], PASSAGES_COLUMNS)
    ensure_csv(paths["qc_pages_csv"], QC_PAGE_COLUMNS)


def assert_writable(paths: dict[str, Path], overwrite: bool) -> None:
    existing: list[Path] = []
    for key, path in paths.items():
        if key.endswith("_csv"):
            continue
        if key in {"passage_dir", "review_image_dir"}:
            pattern = "*.md" if key == "passage_dir" else "*.png"
            if any(path.glob(pattern)):
                existing.append(path)
            continue
        if path.exists():
            existing.append(path)
    if existing and not overwrite:
        formatted = ", ".join(path.as_posix() for path in existing)
        raise FileExistsError(
            f"Generated outputs already exist for this book. Re-run with --overwrite to replace: {formatted}"
        )


def yaml_scalar(value: str) -> str:
    escaped = value.replace("\\", "\\\\").replace('"', '\\"')
    return f'"{escaped}"'


def render_front_matter(metadata: dict[str, str]) -> str:
    lines = ["---"]
    for key, value in metadata.items():
        lines.append(f"{key}: {yaml_scalar(value)}")
    lines.append("---")
    return "\n".join(lines)


def render_raw_text(pages: list[PageResult]) -> str:
    rendered: list[str] = []
    for page in pages:
        rendered.append(PAGE_MARKER_TEMPLATE.format(page_number=page.page_number))
        rendered.append(page.raw_text)
        rendered.append("")
    return "\n".join(rendered).strip() + "\n"


def render_book_markdown(front_matter: dict[str, str], title: str, pages: list[PageResult]) -> str:
    blocks = [render_front_matter(front_matter), "", f"# {title}", ""]
    for page in pages:
        blocks.append(PAGE_MARKER_TEMPLATE.format(page_number=page.page_number))
        blocks.append("")
        blocks.append(page.cleaned_text)
        blocks.append("")
    return "\n".join(blocks).strip() + "\n"


def strip_front_matter(markdown_text: str) -> str:
    if not markdown_text.startswith("---\n"):
        return markdown_text
    parts = markdown_text.split("\n---\n", 1)
    if len(parts) != 2:
        return markdown_text
    return parts[1].lstrip()


def category_for_section(section_number: str) -> str:
    return {
        "1": "oration",
        "2": "letter",
        "3": "saying",
    }.get(section_number, "")


def sanitize_section_marker(section_marker: str) -> str:
    return section_marker.replace(".", "_")


def passage_filename_for(book_id: str, section_number: str, nahj_number: str) -> str:
    return f"{book_id}_{section_number}_{int(nahj_number):03d}.md"


def parse_passages(book_markdown_text: str, book_id: str) -> list[PassageRecord]:
    body = strip_front_matter(book_markdown_text)
    lines = body.splitlines()
    page_marker_pattern = re.compile(r"^\[\[page_(\d{3})\]\]$")
    heading_pattern = re.compile(r"^(?P<section>[123])\.(?P<number>\d{1,3})\s+(?P<title>.+)$")
    stop_markers = {
        "Appendix of Sources for the Texts of Nahj al-Balāghah",
        "Glossary of Names, Places, and Terms",
        "Bibliography",
        "Index of Names and Places",
        "Index of Terms",
        "Index of Qurʾan, Hadith, Poetry, and Proverbs",
        "Index of Religious and Ethical Concepts",
    }

    passages: list[PassageRecord] = []
    current_page: int | None = None
    current_section_name = ""
    current_heading: tuple[str, str, str, int | None] | None = None
    current_lines: list[str] = []
    seen_markers: set[str] = set()

    def flush_current(page_end: int | None) -> None:
        nonlocal current_heading, current_lines
        if not current_heading:
            current_lines = []
            return

        section_number, nahj_number, section_title, page_start = current_heading
        content = "\n".join(current_lines).strip()
        if not content:
            current_heading = None
            current_lines = []
            return

        section_marker = f"{section_number}.{nahj_number}"
        passage_filename = passage_filename_for(book_id, section_number, nahj_number)
        passages.append(
            PassageRecord(
                passage_id=f"{book_id}-{section_marker}",
                book_id=book_id,
                section_marker=section_marker,
                section_title=section_title,
                category=category_for_section(section_number),
                nahj_number=nahj_number,
                page_start=page_start,
                page_end=page_end if page_end is not None else page_start,
                filename=passage_filename,
                content=content,
            )
        )
        current_heading = None
        current_lines = []

    for line in lines:
        page_match = page_marker_pattern.match(line.strip())
        if page_match:
            current_page = int(page_match.group(1))
            if current_heading:
                current_lines.append(line)
            continue

        stripped = line.strip()
        if stripped in stop_markers:
            break

        if stripped in {"Orations", "Letters", "Sayings"}:
            current_section_name = stripped

        heading_match = heading_pattern.match(stripped)
        if heading_match and current_section_name:
            section_number = heading_match.group("section")
            section_title = heading_match.group("title").strip()
            expected_name = {
                "1": "Orations",
                "2": "Letters",
                "3": "Sayings",
            }.get(section_number, "")
            section_marker = f"{section_number}.{heading_match.group('number')}"
            if current_section_name == expected_name:
                active_marker = (
                    f"{current_heading[0]}.{current_heading[1]}"
                    if current_heading
                    else None
                )
                if active_marker != section_marker:
                    flush_current(current_page)

                if section_marker in seen_markers:
                    current_heading = None
                    current_lines = []
                    continue

                if re.search(r"[A-Za-z]", section_title):
                    current_heading = (
                        section_number,
                        heading_match.group("number"),
                        section_title,
                        current_page,
                    )
                    seen_markers.add(section_marker)
                    current_lines = [line]
                else:
                    current_heading = None
                    current_lines = []
                continue

        if current_heading:
            current_lines.append(line)

    flush_current(current_page)
    return passages


def render_passage_markdown(
    passage: PassageRecord,
) -> str:
    passage_language = detect_language(passage.content)
    passage_text_direction = default_text_direction(passage_language)
    front_matter = {
        "passage_id": passage.passage_id,
        "book_id": passage.book_id,
        "section_title": passage.section_title,
        "language": passage_language,
        "text_direction": passage_text_direction,
        "page_start": "" if passage.page_start is None else str(passage.page_start),
        "page_end": "" if passage.page_end is None else str(passage.page_end),
        "nahj_category": passage.category,
        "nahj_number": passage.nahj_number,
    }
    return f"{render_front_matter(front_matter)}\n\n{passage.content.strip()}\n"


def render_review_log(
    book_id: str,
    pdf_path: Path,
    pages: list[PageResult],
    title: str,
    created_manifest_entry: bool,
    extraction_engine: str,
    runtime: OcrRuntime,
    review_notes: list[str],
    passage_count: int,
    manual_review_count: int,
    exported_review_images: int,
    qc_json_path: Path,
    qc_pages_csv_path: Path,
    qc_pages: list[dict[str, object]],
    weak_passage_lines: list[str],
) -> str:
    issue_lines: list[str] = []
    for note in review_notes:
        issue_lines.append(f"- {note}")
    for page in pages:
        for warning in page.warnings:
            issue_lines.append(f"- {warning}")

    if created_manifest_entry:
        issue_lines.insert(0, "- Added a new manifest entry for this source file.")
    if not issue_lines:
        issue_lines.append("- No extraction issues detected in this run.")

    manual_review_lines = [
        (
            f"- Page {int(page['page_number']):03d}: "
            f"flags=`{', '.join(page['flags'])}`; "
            f"image=`{page['review_image'] or 'not exported'}`"
        )
        for page in qc_pages
        if page["manual_review"]
    ]
    if not manual_review_lines:
        manual_review_lines.append("- No pages currently marked for manual review.")
    if not weak_passage_lines:
        weak_passage_lines = ["- No passage-level weak sections detected in this run."]

    ocr_required_count = sum(1 for page in pages if page.ocr_required)
    ocr_used_count = sum(1 for page in pages if page.ocr_used)
    arabic_direct_ocr_count = sum(1 for page in pages if page.arabic_direct_ocr_used)
    body = [
        f"# Review Log For {book_id}",
        "",
        f"- Source PDF: `{project_relative_string(pdf_path)}`",
        f"- Title used: `{title}`",
        f"- Pages processed: `{len(pages)}`",
        f"- Extraction engine: `{extraction_engine}`",
        f"- OCRmyPDF Python package available: `{'yes' if runtime.ocrmypdf_python_available else 'no'}`",
        f"- pypdfium2 Python package available: `{'yes' if runtime.pypdfium2_python_available else 'no'}`",
        f"- Tesseract executable available: `{'yes' if runtime.tesseract_executable else 'no'}`",
        f"- Ghostscript executable available: `{'yes' if runtime.ghostscript_executable else 'no'}`",
        f"- Pages flagged as needing OCR: `{ocr_required_count}`",
        f"- Pages actually OCRed: `{ocr_used_count}`",
        f"- Pages marked for manual review: `{manual_review_count}`",
        "",
        "## Issues",
        "",
        *issue_lines,
        "",
        "## Manual Review Pages",
        "",
        *manual_review_lines,
        "",
        "## Weak Sections",
        "",
        *weak_passage_lines,
        "",
        "## Notes",
        "",
        f"- Passage files generated in this run: `{passage_count}`.",
        f"- Pages with direct Tesseract Arabic OCR replacement: `{arabic_direct_ocr_count}`.",
        f"- QC JSON written to `{project_relative_string(qc_json_path)}`.",
        f"- QC page CSV written to `{project_relative_string(qc_pages_csv_path)}`.",
        f"- Review images exported in this run: `{exported_review_images}`.",
    ]
    return "\n".join(body).strip() + "\n"


def render_qc_json(
    book_id: str,
    pdf_path: Path,
    title: str,
    extraction_engine: str,
    qc_pages: list[dict[str, object]],
) -> str:
    flag_counts: dict[str, int] = {}
    for page in qc_pages:
        for flag in page["flags"]:
            flag_counts[flag] = flag_counts.get(flag, 0) + 1

    payload = {
        "book_id": book_id,
        "source_pdf": project_relative_string(pdf_path),
        "title": title,
        "extraction_engine": extraction_engine,
        "summary": {
            "pages_total": len(qc_pages),
            "manual_review_pages": sum(1 for page in qc_pages if page["manual_review"]),
            "flag_counts": dict(sorted(flag_counts.items())),
        },
        "pages": qc_pages,
    }
    return json.dumps(payload, ensure_ascii=False, indent=2) + "\n"


def write_qc_pages_csv(path: Path, qc_pages: list[dict[str, object]]) -> None:
    ensure_csv(path, QC_PAGE_COLUMNS)
    with path.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=QC_PAGE_COLUMNS)
        writer.writeheader()
        for page in qc_pages:
            writer.writerow(
                {
                    "page_number": str(page["page_number"]),
                    "language": str(page["language"]),
                    "flags": "|".join(page["flags"]),
                    "manual_review": "true" if page["manual_review"] else "false",
                    "ocr_required": "true" if page["ocr_required"] else "false",
                    "ocr_used": "true" if page["ocr_used"] else "false",
                    "raw_char_count": str(page["raw_char_count"]),
                    "cleaned_char_count": str(page["cleaned_char_count"]),
                    "warnings": " | ".join(page["warnings"]),
                    "review_image": str(page["review_image"]),
                }
            )


def export_review_images(
    pdf_path: Path,
    qc_pages: list[dict[str, object]],
    output_dir: Path,
) -> int:
    manual_review_pages = [page for page in qc_pages if page["manual_review"]]
    if not manual_review_pages:
        return 0

    document = pymupdf.open(str(pdf_path))
    exported = 0
    try:
        for page in manual_review_pages:
            page_number = int(page["page_number"])
            page_path = output_dir / f"page_{page_number:03d}.png"
            pixmap = document.load_page(page_number - 1).get_pixmap(dpi=144, alpha=False)
            pixmap.save(page_path)
            page["review_image"] = project_relative_string(page_path)
            exported += 1
    finally:
        document.close()

    return exported


def upsert_csv_row(path: Path, columns: list[str], key_field: str, row: dict[str, str]) -> None:
    ensure_csv(path, columns)
    with path.open("r", encoding="utf-8", newline="") as handle:
        reader = csv.DictReader(handle)
        rows = [{column: (existing.get(column, "") or "") for column in columns} for existing in reader]

    replaced = False
    for index, existing in enumerate(rows):
        if existing.get(key_field, "") == row[key_field]:
            rows[index] = {column: row.get(column, "") for column in columns}
            replaced = True
            break

    if not replaced:
        rows.append({column: row.get(column, "") for column in columns})

    with path.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=columns)
        writer.writeheader()
        writer.writerows(rows)


def replace_passage_rows(path: Path, book_id: str, rows_to_add: list[dict[str, str]]) -> None:
    ensure_csv(path, PASSAGES_COLUMNS)
    with path.open("r", encoding="utf-8", newline="") as handle:
        reader = csv.DictReader(handle)
        rows = [
            {column: (existing.get(column, "") or "") for column in PASSAGES_COLUMNS}
            for existing in reader
            if (existing.get("book_id", "") or "") != book_id
        ]

    rows.extend(rows_to_add)
    with path.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=PASSAGES_COLUMNS)
        writer.writeheader()
        writer.writerows(rows)


def review_priority_for(pages: list[PageResult]) -> str:
    if any("[unclear]" in page.raw_text or "[unclear]" in page.cleaned_text for page in pages):
        return "high"
    if any(page.ocr_required and not page.ocr_used for page in pages):
        return "high"
    if any(page.ocr_required for page in pages):
        return "medium"
    if any(page.warnings for page in pages):
        return "medium"
    return "low"


def process_pdf(
    pdf_path: Path,
    manifest_path: Path,
    output_root: Path,
    overwrite: bool,
    ocr_mode: str,
    ocr_languages: str,
    ocr_dpi: int,
) -> tuple[str, Path]:
    manifest_entry, _entries, created_manifest_entry = get_or_create_manifest_entry(manifest_path, pdf_path)
    runtime = discover_ocr_runtime()
    pages, source_metadata, review_notes, extraction_engine = extract_pages(
        pdf_path,
        runtime,
        preferred_language=manifest_entry.language,
        ocr_mode=ocr_mode,
        ocr_languages=ocr_languages,
        ocr_dpi=ocr_dpi,
    )

    detected_language = detect_language("\n".join(page.raw_text for page in pages))
    language = manifest_entry.language or detected_language
    text_direction = manifest_entry.text_direction or default_text_direction(language)
    normalization_level = manifest_entry.normalization_level or default_normalization_level(language)
    title = manifest_entry.full_title or source_metadata["title"] or pdf_path.stem
    author = manifest_entry.author or source_metadata["author"]
    translator_editor = manifest_entry.translator_editor
    notes = manifest_entry.notes

    output_paths = build_paths(output_root, manifest_entry.book_id)
    ensure_outputs(output_paths)
    assert_writable(output_paths, overwrite)
    if overwrite and output_paths["passage_dir"].exists():
        for existing_passage in output_paths["passage_dir"].glob("*.md"):
            existing_passage.unlink()
    if overwrite and output_paths["review_image_dir"].exists():
        for existing_image in output_paths["review_image_dir"].glob("*.png"):
            existing_image.unlink()

    raw_text_output = render_raw_text(pages)
    front_matter = {
        "book_id": manifest_entry.book_id,
        "full_title": title,
        "author": author,
        "translator_editor": translator_editor,
        "language": language,
        "text_direction": text_direction,
        "pdf_filename": pdf_path.name,
        "source_relpath": project_relative_string(pdf_path),
        "total_pages": str(len(pages)),
        "ocr_required": "true" if any(page.ocr_required for page in pages) else "false",
        "ocr_used": "true" if any(page.ocr_used for page in pages) else "false",
        "extraction_engine": extraction_engine,
        "normalization_level": normalization_level,
    }
    book_markdown_output = render_book_markdown(front_matter, title, pages)
    passages = parse_passages(book_markdown_output, manifest_entry.book_id)
    qc_pages, qc_page_lookup = build_qc_pages(pages)
    exported_review_images = export_review_images(
        pdf_path,
        qc_pages,
        output_paths["review_image_dir"],
    )
    qc_json_output = render_qc_json(
        manifest_entry.book_id,
        pdf_path,
        title,
        extraction_engine,
        qc_pages,
    )
    manual_review_pages = {
        page_number
        for page_number, page_record in qc_page_lookup.items()
        if page_record["manual_review"]
    }

    output_paths["raw_text"].write_text(raw_text_output, encoding="utf-8")
    output_paths["book_markdown"].write_text(book_markdown_output, encoding="utf-8")
    output_paths["qc_json"].write_text(qc_json_output, encoding="utf-8")
    write_qc_pages_csv(output_paths["qc_pages_csv"], qc_pages)
    passage_rows: list[dict[str, str]] = []
    weak_passage_lines: list[str] = []
    for passage in passages:
        passage_path = output_paths["passage_dir"] / passage.filename
        passage_language = detect_language(passage.content)
        passage_page_numbers = list(
            range(
                passage.page_start or 0,
                (passage.page_end or passage.page_start or 0) + 1,
            )
        )
        passage_page_records = [
            qc_page_lookup[page_number]
            for page_number in passage_page_numbers
            if page_number in qc_page_lookup
        ]
        passage_manual_review_pages = [
            page_number
            for page_number in passage_page_numbers
            if page_number in manual_review_pages
        ]
        passage_ocr_pages = [
            page_number
            for page_number in passage_page_numbers
            if page_number in qc_page_lookup and qc_page_lookup[page_number]["ocr_used"]
        ]
        passage_needs_manual_review = bool(passage_manual_review_pages)
        passage_ocr_confidence = ocr_confidence_for_page_records(passage_page_records)
        passage_notes_parts: list[str] = []
        if passage_manual_review_pages:
            manual_page_summary = summarize_page_numbers(passage_manual_review_pages)
            passage_notes_parts.append(f"Manual review pages: {manual_page_summary}.")
            overlapping_flags = sorted(
                {
                    flag
                    for page_number in passage_manual_review_pages
                    for flag in qc_page_lookup[page_number]["flags"]
                }
            )
            if overlapping_flags:
                passage_notes_parts.append(
                    f"Weak-page flags: {', '.join(overlapping_flags)}."
                )
        elif passage_ocr_pages:
            passage_notes_parts.append(
                f"OCR-applied pages: {summarize_page_numbers(passage_ocr_pages)}."
            )
        if any(page_record["arabic_direct_ocr_used"] for page_record in passage_page_records):
            passage_notes_parts.append("Direct Tesseract Arabic OCR used on overlapping pages.")

        passage_path.write_text(
            render_passage_markdown(passage=passage),
            encoding="utf-8",
        )
        passage_rows.append(
            {
                "passage_id": passage.passage_id,
                "book_id": manifest_entry.book_id,
                "language": passage_language,
                "section_title": passage.section_title,
                "page_start": "" if passage.page_start is None else str(passage.page_start),
                "page_end": "" if passage.page_end is None else str(passage.page_end),
                "filename": project_relative_string(passage_path),
                "nahj_category": passage.category,
                "nahj_number": passage.nahj_number,
                "ocr_confidence": passage_ocr_confidence,
                "needs_manual_review": "true" if passage_needs_manual_review else "false",
                "notes": " ".join(passage_notes_parts).strip(),
            }
        )
        if passage_needs_manual_review:
            weak_passage_lines.append(
                f"- {passage.passage_id} pages `{summarize_page_numbers(passage_manual_review_pages)}`: "
                f"{' '.join(passage_notes_parts).strip()}"
            )
    review_log_output = render_review_log(
        manifest_entry.book_id,
        pdf_path,
        pages,
        title,
        created_manifest_entry,
        extraction_engine,
        runtime,
        review_notes,
        len(passages),
        len(manual_review_pages),
        exported_review_images,
        output_paths["qc_json"],
        output_paths["qc_pages_csv"],
        qc_pages,
        weak_passage_lines,
    )
    output_paths["review_log"].write_text(review_log_output, encoding="utf-8")

    books_row = {
        "book_id": manifest_entry.book_id,
        "full_title": title,
        "author": author,
        "translator_editor": translator_editor,
        "language": language,
        "text_direction": text_direction,
        "pdf_filename": pdf_path.name,
        "book_md_filename": project_relative_string(output_paths["book_markdown"]),
        "ocr_required": "true" if any(page.ocr_required for page in pages) else "false",
        "ocr_confidence": ocr_confidence_for_page_records(qc_pages),
        "normalization_level": normalization_level,
        "review_priority": review_priority_for(pages),
        "notes": (
            f"{notes} " if notes else ""
        ) + (
            f"Manual review pages: {summarize_page_numbers(sorted(manual_review_pages))}."
            if manual_review_pages
            else ""
        ),
    }
    upsert_csv_row(output_paths["books_csv"], BOOKS_COLUMNS, "book_id", books_row)
    replace_passage_rows(output_paths["passages_csv"], manifest_entry.book_id, passage_rows)

    return manifest_entry.book_id, output_paths["book_markdown"]


def main() -> int:
    args = parse_args()
    manifest_path = resolve_project_path(args.manifest).resolve()
    output_root = resolve_project_path(args.output_root).resolve()

    try:
        pdf_paths = resolve_inputs(args)
    except (FileNotFoundError, ValueError) as exc:
        print(f"Error: {exc}", file=sys.stderr)
        return 1

    failures = 0
    for pdf_path in pdf_paths:
        try:
            book_id, markdown_path = process_pdf(
                pdf_path=pdf_path,
                manifest_path=manifest_path,
                output_root=output_root,
                overwrite=args.overwrite,
                ocr_mode=args.ocr_mode,
                ocr_languages=args.ocr_languages,
                ocr_dpi=args.ocr_dpi,
            )
            print(f"{book_id}: wrote {project_relative_string(markdown_path)}")
        except Exception as exc:
            failures += 1
            print(f"{project_relative_string(pdf_path)}: {exc}", file=sys.stderr)

    return 1 if failures else 0


if __name__ == "__main__":
    raise SystemExit(main())
