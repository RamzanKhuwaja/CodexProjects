"""
Shared project context helpers for MAE reporting.

These helpers derive repeatable facts from the archived source documents
instead of duplicating year-specific values inside report scripts.
"""

from __future__ import annotations

import os
import re
from datetime import date
from pathlib import Path

try:
    import pdfplumber
except ImportError:  # pragma: no cover
    pdfplumber = None

try:
    from docx import Document as DocxReader
except ImportError:  # pragma: no cover
    DocxReader = None


PROJECT_NAME = "Spirit of Math Schools Markham East"
FISCAL_YEAR_START_MONTH = 8
FISCAL_YEAR_START_DAY = 1
MARKETING_OBLIGATION_RATE = 0.03


def money_from_text(text: str, pattern: str) -> float | None:
    match = re.search(pattern, text, re.IGNORECASE | re.MULTILINE)
    if not match:
        return None
    return parse_money(match.group(1))


def parse_money(value: str | None) -> float | None:
    if value is None:
        return None
    cleaned = value.replace(",", "").replace("$", "").strip()
    if not cleaned:
        return None
    try:
        return float(cleaned)
    except ValueError:
        return None


def read_text_file(path: Path) -> str:
    return path.read_text(encoding="utf-8", errors="replace")


def extract_pdf_text(path: Path, page_limit: int | None = None) -> str:
    if pdfplumber is None:
        raise RuntimeError("pdfplumber is required to read archived PDF sources")
    chunks = []
    with pdfplumber.open(str(path)) as pdf:
        pages = pdf.pages if page_limit is None else pdf.pages[:page_limit]
        for page in pages:
            text = (page.extract_text() or "").strip()
            if text:
                chunks.append(text)
    return "\n\n".join(chunks)


def extract_docx_text(path: Path) -> str:
    if DocxReader is None:
        raise RuntimeError("python-docx is required to read DOCX sources")
    doc = DocxReader(str(path))
    lines = [p.text.strip() for p in doc.paragraphs if p.text.strip()]
    return "\n".join(lines)


def first_match(base_dir: Path, *patterns: str) -> Path | None:
    for pattern in patterns:
        matches = sorted(base_dir.glob(pattern))
        if matches:
            return matches[0]
    return None


def load_requirements_text(base_dir: Path) -> str:
    docs_dir = base_dir / "docs"
    path = first_match(docs_dir, "*Requirements*.docx", "*requirements*.docx", "*Requirements*.txt")
    if path is None:
        return ""
    if path.suffix.lower() == ".docx":
        return extract_docx_text(path)
    return read_text_file(path)


def load_t2_text(base_dir: Path) -> str:
    archive_dir = base_dir / "data" / "archive"
    txt_path = first_match(archive_dir, "*t2*extracted*.txt", "*T2*.txt")
    if txt_path is not None:
        return read_text_file(txt_path)

    pdf_path = first_match(archive_dir, "*T2*.pdf", "*t2*.pdf")
    if pdf_path is None:
        raise FileNotFoundError("Could not find archived T2 source")
    return extract_pdf_text(pdf_path)


def load_review_fs_text(base_dir: Path) -> str:
    archive_dir = base_dir / "data" / "archive"
    pdf_path = first_match(archive_dir, "*2024-2025*.pdf", "*2025*.pdf")
    if pdf_path is None:
        raise FileNotFoundError("Could not find FY2024-25 reviewed financial statements PDF")
    return extract_pdf_text(pdf_path, page_limit=6)


def parse_sbd_limit(requirements_text: str) -> float:
    value = money_from_text(requirements_text, r"Small Business Deduction limit of \$?\s*([0-9,]+)")
    if value is None:
        value = money_from_text(requirements_text, r"gets \$\s*([0-9,]+) separately")
    if value is None:
        raise ValueError("Could not derive the small business deduction limit from requirements")
    return value


def parse_review_fs_metrics(fs_text: str) -> dict:
    tuition = money_from_text(fs_text, r"Tuition\s+([0-9,]+)\s+[0-9,]+")
    total_revenue = money_from_text(fs_text, r"Total Revenue\s+([0-9,]+)\s+[0-9,]+")
    pretax_income = money_from_text(fs_text, r"Net income before income tax\s+([0-9,]+)\s+[0-9,]+")
    current_income_taxes = money_from_text(fs_text, r"Current income taxes\s+([0-9,]+)\s+[0-9,]+")
    if tuition is None or pretax_income is None:
        raise ValueError("Could not derive FY2024-25 reviewed financial metrics")
    return {
        "full_year_tuition": tuition,
        "total_revenue": total_revenue,
        "net_income_before_tax": pretax_income,
        "current_income_taxes": current_income_taxes,
    }


def parse_t2_metrics(t2_text: str) -> dict:
    taxable_income = money_from_text(t2_text, r"Taxable income 360\s+([0-9,]+)")
    total_tax_payable = money_from_text(t2_text, r"Total tax payable 770\s+([0-9,]+)")
    balance_owing = money_from_text(t2_text, r"Balance owing \(refund\)\s+([0-9,]+)")
    part_i_tax = money_from_text(t2_text, r"Part I tax payable 700\s+([0-9,]+)")
    net_income_tax_purposes = money_from_text(
        t2_text,
        r"Net income or \(loss\) for tax purposes 300\s+([0-9,]+)",
    )
    if taxable_income is None or total_tax_payable is None:
        raise ValueError("Could not derive FY2024-25 T2 metrics")
    return {
        "taxable_income": taxable_income,
        "total_tax_payable": total_tax_payable,
        "balance_owing": balance_owing,
        "part_i_tax": part_i_tax,
        "net_income_tax_purposes": net_income_tax_purposes,
    }


def load_historical_context(base_dir: str | os.PathLike[str]) -> dict:
    root = Path(base_dir)
    requirements_text = load_requirements_text(root)
    t2_text = load_t2_text(root)
    fs_text = load_review_fs_text(root)

    review_fs = parse_review_fs_metrics(fs_text)
    t2 = parse_t2_metrics(t2_text)
    sbd_limit = parse_sbd_limit(requirements_text)

    return {
        "project_name": PROJECT_NAME,
        "marketing_rate": MARKETING_OBLIGATION_RATE,
        "sbd_limit": sbd_limit,
        "prior_year": {
            "review_fs": review_fs,
            "t2": t2,
        },
    }


def fiscal_year_bounds(cutoff_date: date) -> tuple[date, date]:
    if (cutoff_date.month, cutoff_date.day) >= (FISCAL_YEAR_START_MONTH, FISCAL_YEAR_START_DAY):
        start_year = cutoff_date.year
    else:
        start_year = cutoff_date.year - 1

    start = date(start_year, FISCAL_YEAR_START_MONTH, FISCAL_YEAR_START_DAY)
    end = date(start_year + 1, FISCAL_YEAR_START_MONTH, FISCAL_YEAR_START_DAY) - date.resolution
    return start, end


def fiscal_year_label(start: date, end: date) -> str:
    return f"{start.strftime('%B')} {start.day}, {start.year} - {end.strftime('%B')} {end.day}, {end.year}"
