from __future__ import annotations

import os
import re
import time
import csv
import math
import html
from io import StringIO
from dataclasses import dataclass
from datetime import datetime, timedelta
from pathlib import Path
from typing import Iterable, Mapping, Optional, Sequence
from collections import Counter

import glob
import numpy as np
import openpyxl
try:
    from bs4 import BeautifulSoup
    _BS4_IMPORT_ERROR: Exception | None = None
except Exception as exc:  # noqa: BLE001
    BeautifulSoup = None  # type: ignore[assignment]
    _BS4_IMPORT_ERROR = exc
import win32com.client as email_client

try:
    import pandas as pd
    _PANDAS_IMPORT_ERROR: Exception | None = None
except Exception as exc:  # noqa: BLE001
    pd = None  # type: ignore[assignment]
    _PANDAS_IMPORT_ERROR = exc


PANDAS_AVAILABLE = _PANDAS_IMPORT_ERROR is None
BS4_AVAILABLE = _BS4_IMPORT_ERROR is None


def _ensure_bs4(context: str) -> bool:
    if BS4_AVAILABLE:
        return True
    print(
        f"ERROR: BeautifulSoup dependency (bs4) is required for {context}. "
        "Install it with: python -m pip install beautifulsoup4"
    )
    return False


def is_missing(value: object) -> bool:
    if value is None:
        return True
    if isinstance(value, float) and math.isnan(value):
        return True
    if isinstance(value, str) and not value.strip():
        return True
    if PANDAS_AVAILABLE:
        try:
            return bool(pd.isna(value))  # type: ignore[union-attr]
        except Exception:  # noqa: BLE001
            return False
    return False


def _coerce_str(value: object) -> str:
    if value is None:
        return ""
    return str(value)


def _format_table(rows: Iterable[Mapping[str, object]], columns: Sequence[str]) -> str:
    rows_list = list(rows)
    if not rows_list:
        return "(no rows)"

    widths: dict[str, int] = {col: len(col) for col in columns}
    for row in rows_list:
        for col in columns:
            widths[col] = max(widths[col], len(_coerce_str(row.get(col, ""))))

    header = " | ".join(col.ljust(widths[col]) for col in columns)
    separator = "-+-".join("-" * widths[col] for col in columns)
    lines = [header, separator]

    for row in rows_list:
        lines.append(
            " | ".join(_coerce_str(row.get(col, "")).ljust(widths[col]) for col in columns)
        )

    return "\n".join(lines)


def _sorted_rows(rows: Iterable[Mapping[str, object]], keys: Sequence[str]) -> list[dict[str, object]]:
    if not keys:
        return [dict(row) for row in rows]

    def sort_key(row: Mapping[str, object]) -> tuple:
        return tuple(
            _coerce_str(row.get(key, "")).lower()
            for key in keys
        )

    return sorted((dict(row) for row in rows), key=sort_key)


@dataclass
class TableData:
    columns: list[str]
    rows: list[dict[str, object]]

    def __post_init__(self) -> None:
        # Normalise columns and row keys to avoid KeyError later.
        self.columns = [str(col) for col in self.columns]
        normalised_rows: list[dict[str, object]] = []
        for row in self.rows:
            normalised_rows.append({col: row.get(col, "") for col in self.columns})
        self.rows = normalised_rows

    @property
    def is_empty(self) -> bool:
        return not self.rows

    def __bool__(self) -> bool:
        return not self.is_empty

    def __len__(self) -> int:
        return len(self.rows)

    def select(self, columns: Sequence[str]) -> "TableData":
        column_list = [str(col) for col in columns]
        return TableData(column_list, [{col: row.get(col, "") for col in column_list} for row in self.rows])

    def drop_duplicates(self, subset: Sequence[str] | None = None) -> "TableData":
        if subset is None:
            subset = self.columns
        seen: set[tuple[object, ...]] = set()
        unique_rows: list[dict[str, object]] = []
        for row in self.rows:
            key = tuple(row.get(col, "") for col in subset)
            if key in seen:
                continue
            seen.add(key)
            unique_rows.append(row.copy())
        return TableData(self.columns, unique_rows)

    def sorted(self, columns: Sequence[str]) -> "TableData":
        return TableData(self.columns, _sorted_rows(self.rows, columns))

    def to_string(self) -> str:
        return _format_table(self.rows, self.columns)

    def to_records(self) -> list[dict[str, object]]:
        return [row.copy() for row in self.rows]


def ensure_table_data(data: object, default_columns: Sequence[str] | None = None) -> TableData | None:
    if data is None:
        return None

    if isinstance(data, TableData):
        return data

    if PANDAS_AVAILABLE and isinstance(data, pd.DataFrame):  # type: ignore[union-attr]
        filled = data.fillna("")  # type: ignore[union-attr]
        return TableData(list(filled.columns), filled.to_dict(orient="records"))  # type: ignore[union-attr]

    if isinstance(data, list):
        if not data:
            columns = list(default_columns or [])
        else:
            # Merge keys across all rows to preserve information
            column_set: list[str] = []
            for row in data:
                if isinstance(row, Mapping):
                    for key in row.keys():
                        if key not in column_set:
                            column_set.append(str(key))
            if column_set:
                columns = column_set
            else:
                columns = list(default_columns or [])
        processed_rows = []
        for row in data:
            if isinstance(row, Mapping):
                processed_rows.append({str(col): row.get(col, "") for col in columns})
        return TableData(columns, processed_rows)

    return None

try:
    import pdfkit
except ImportError:
    pdfkit = None

# Debug flag to control which paths to use
#  <======  Be CAREFUL with this switch!!!!!!!!!!!!!
#   use only when doing a new run with 3 files only
DEBUG = False  #  <======  Be CAREFUL with this switch!!!!!!!!!!!!!
              # Set to True to use debugging paths (with limited # of files), False for production paths
TESTING = False
    #  <======  Be CAREFUL with this switch!!!!!!!!!!!!!
                  #  This is NOR DEBUGGING!  This uses all data before sending to teachers
THIS_WEEK_NUM = 27 #  <======  Change this every week!!!!!!!!!!!!!

SEND_EMAIL = True
PRINT_REPORT = True


# ======  Following Don't Change Often!

GRADES_MIN_BAR = int(50) # Scoring less than 50%!
HIGH_HONOURS_MIN_BAR = int(90) # Scoring 90% or higher!
NOT_LOGGED_IN_SINCE = int(14) # Not logged in since last 2 weeks!
ATTENDANCE_MIN_BAR = int(80) # Min attendance required (in %)

CAMPUS = to_email = cc_email = body_email = subject_email = ""

SUPPORTED_DATE_FORMATS = [
    "%b %d, %Y %I:%M %p",
    "%b %d, %Y",
    "%Y-%m-%d %H:%M:%S",
    "%Y-%m-%d",
    "%Y/%m/%d %H:%M",
    "%d-%b-%Y %H:%M",
    "%m/%d/%Y %I:%M %p",
]

CLASS_CODE_REGEX = re.compile(r"(?:SOMp|MAE)\w+", re.IGNORECASE)

_WARNED_MESSAGES: set[tuple[str, str]] = set()
_OUTLOOK_APP = None
_OUTLOOK_CONNECTION_FAILED = False


def warn_once(level: str, message: str) -> None:
    key = (level, message)
    if key not in _WARNED_MESSAGES:
        print(f"{level}: {message}")
        _WARNED_MESSAGES.add(key)


def _get_outlook_app():
    global _OUTLOOK_APP, _OUTLOOK_CONNECTION_FAILED

    if _OUTLOOK_CONNECTION_FAILED:
        return None
    if _OUTLOOK_APP is not None:
        return _OUTLOOK_APP

    try:
        _OUTLOOK_APP = email_client.Dispatch("outlook.application")
    except Exception as exc:
        _OUTLOOK_CONNECTION_FAILED = True
        warn_once("ERROR", f"Unable to connect to Outlook to send email: {exc}")
        return None

    return _OUTLOOK_APP



def normalize(value: object) -> str:
    return str(value).strip().lower()



EMAIL_WRAPPER_STYLE = (
    "font-family:'Segoe UI', Arial, sans-serif;"
    " color:#1f3a4d;"
    " font-size:13px;"
    " line-height:1.5;"
)
EMAIL_TITLE_STYLE = (
    "font-size:16px;"
    " font-weight:600;"
    " margin:0 0 8px 0;"
)
EMAIL_SUBTITLE_STYLE = (
    "font-size:13px;"
    " margin:0 0 12px 0;"
    " color:#2b5d80;"
)
EMAIL_TABLE_STYLE = (
    "border-collapse:collapse;"
    " width:100%;"
    " max-width:680px;"
    " margin:0 0 12px 0;"
    " border:1px solid #c6d6e5;"
)
EMAIL_HEADER_STYLE = (
    "background-color:#007795;"
    " color:#ffffff;"
    " text-align:left;"
    " padding:10px 12px;"
    " font-weight:600;"
    " border-bottom:1px solid #005c73;"
)
EMAIL_CELL_STYLE = (
    "padding:9px 12px;"
    " border-bottom:1px solid #c6d6e5;"
    " background-color:#ffffff;"
    " color:#1f3a4d;"
    " text-align:left;"
)
EMAIL_CELL_ALT_STYLE = (
    "padding:9px 12px;"
    " border-bottom:1px solid #c6d6e5;"
    " background-color:#f2f8fb;"
    " color:#1f3a4d;"
    " text-align:left;"
)


def render_html_table(
    data,
    *,
    title: str | None = None,
    subtitle: str | None = None,
) -> str:
    """Return a branded HTML table snippet suitable for Outlook emails."""
    table = ensure_table_data(data)
    if table is None or table.is_empty:
        return ''

    columns = table.columns
    if not columns:
        return ''

    header_cells = ''.join(
        f'<th style="{EMAIL_HEADER_STYLE}">{html.escape(str(col))}</th>' for col in columns
    )

    body_rows: list[str] = []
    for index, row in enumerate(table.rows):
        cell_style = EMAIL_CELL_ALT_STYLE if index % 2 else EMAIL_CELL_STYLE
        cells = ''.join(
            f'<td style="{cell_style}">{html.escape(_coerce_str(row.get(col, "")))}</td>'
            for col in columns
        )
        body_rows.append(f'<tr>{cells}</tr>')

    table_html = (
        f'<table style="{EMAIL_TABLE_STYLE}" cellpadding="0" cellspacing="0">'
        f'<thead><tr>{header_cells}</tr></thead>'
        f'<tbody>{"".join(body_rows)}</tbody>'
        '</table>'
    )

    wrapper_parts: list[str] = [f'<div style="{EMAIL_WRAPPER_STYLE}">']
    if title:
        wrapper_parts.append(f'<div style="{EMAIL_TITLE_STYLE}">{html.escape(title)}</div>')
    if subtitle:
        wrapper_parts.append(f'<div style="{EMAIL_SUBTITLE_STYLE}">{html.escape(subtitle)}</div>')
    wrapper_parts.append(table_html)
    wrapper_parts.append('</div>')
    return ''.join(wrapper_parts)




def extract_student_id(primary: object, fallback: object | None = None) -> Optional[str]:
    "Return the best numeric student id string, preserving leading zeros when possible."
    candidates: list[str] = []

    def add_candidate(source: object) -> None:
        if source is None:
            return
        if isinstance(source, str):
            raw = source
        else:
            if is_missing(source):
                return
            raw = str(source)
        value = raw.strip()
        if not value:
            return
        match = re.search(r'(\d+)', value)
        if not match:
            return
        digits = match.group(1)
        if digits:
            candidates.append(digits)

    add_candidate(primary)
    add_candidate(fallback)

    if not candidates:
        return None

    def leading_zero_count(value: str) -> int:
        count = 0
        for char in value:
            if char == '0':
                count += 1
            else:
                break
        return count

    best = max(candidates, key=lambda item: (len(item), leading_zero_count(item)))
    return best

def find_first_matching_column(columns_or_df, candidates: Sequence[str]) -> Optional[str]:
    if columns_or_df is None:
        return None
    if hasattr(columns_or_df, "columns"):
        columns = columns_or_df.columns  # type: ignore[assignment]
    else:
        columns = columns_or_df

    for col in columns:
        if any(keyword in normalize(col) for keyword in candidates):
            return col
    return None



def parse_datetime(value: object, context: str = "") -> Optional[datetime]:
    if is_missing(value):
        return None
    if isinstance(value, datetime):
        return value
    text = str(value).strip()
    if not text or text.lower() in {"nan", "none", "nat"}:
        return None
    for fmt in SUPPORTED_DATE_FORMATS:
        try:
            return datetime.strptime(text, fmt)
        except ValueError:
            continue
    warn_once("WARNING", f"Unrecognized date format '{text}'{f' while processing {context}' if context else ''}")
    return None


def load_student_map(campus: str) -> pd.DataFrame:
    campus = campus.upper() if isinstance(campus, str) else campus
    mapping = {"VAU": VAU_STUDENT_MAP_FILE, "MAE": MAE_STUDENT_MAP_FILE}
    file_path = mapping.get(campus)
    if not file_path:
        print(f"ERROR: Invalid campus name '{campus}'")
        return pd.DataFrame()
    if not os.path.exists(file_path):
        print(f"ERROR: Student map file not found: {file_path}")
        return pd.DataFrame()
    try:
        return pd.read_csv(file_path)
    except Exception as exc:
        print(f"ERROR: Failed to read student map '{file_path}': {exc}")
        return pd.DataFrame()












# Resolve project root (two levels up from this file: ProgressMonitoring)



_THIS_DIR = os.path.abspath(os.path.dirname(__file__))



_PROJ_ROOT = os.path.abspath(os.path.join(_THIS_DIR, os.pardir, os.pardir))







# File locations relative to project root to avoid hardcoded absolute paths



VAU_CLASS_MAP_FILE  = os.path.join(_PROJ_ROOT, 'Code', 'Common', 'VAUClassMap2025-26.csv')



MAE_CLASS_MAP_FILE  = os.path.join(_PROJ_ROOT, 'Code', 'Common', 'MAEClassMap2025-26.csv')



VAU_STUDENT_MAP_FILE = os.path.join(_PROJ_ROOT, 'Code', 'Common', 'VAUStudentMap2025-26.csv')



MAE_STUDENT_MAP_FILE = os.path.join(_PROJ_ROOT, 'Code', 'Common', 'MAEStudentMap2025-26.csv')







if DEBUG:



    VAU_ATTENDANCE_DIR = os.path.join(_PROJ_ROOT, 'Data', 'Debugging', 'VAU', 'Attendance')



    MAE_ATTENDANCE_DIR = os.path.join(_PROJ_ROOT, 'Data', 'Debugging', 'MAE', 'Attendance')



    VAU_CLASS_LIST_DIR = os.path.join(_PROJ_ROOT, 'Data', 'Debugging', 'VAU', 'ClassList')



    MAE_CLASS_LIST_DIR = os.path.join(_PROJ_ROOT, 'Data', 'Debugging', 'MAE', 'ClassList')



    VAU_GRADES_DIR = os.path.join(_PROJ_ROOT, 'Data', 'Debugging', 'VAU', 'Grades')



    MAE_GRADES_DIR = os.path.join(_PROJ_ROOT, 'Data', 'Debugging', 'MAE', 'Grades')



else:



    VAU_ATTENDANCE_DIR = os.path.join(_PROJ_ROOT, 'Data', 'VAU', 'Attendance')



    MAE_ATTENDANCE_DIR = os.path.join(_PROJ_ROOT, 'Data', 'MAE', 'Attendance')



    VAU_CLASS_LIST_DIR = os.path.join(_PROJ_ROOT, 'Data', 'VAU', 'ClassList')



    MAE_CLASS_LIST_DIR = os.path.join(_PROJ_ROOT, 'Data', 'MAE', 'ClassList')



    VAU_GRADES_DIR = os.path.join(_PROJ_ROOT, 'Data', 'VAU', 'Grades')



    MAE_GRADES_DIR = os.path.join(_PROJ_ROOT, 'Data', 'MAE', 'Grades')
def _download_list_files(folder: Path) -> list[Path]:
    folder_path = Path(folder)
    return [item for item in folder_path.iterdir() if item.is_file()]


def _download_issue(message: str, potential: str) -> str:
    return (
        f"Issue: {message}. "
        f"Potential issue with data download: {potential}."
    )


def _download_folder_issues(
    name: str,
    folder: Path,
    expected_count: int,
    expected_suffix: str,
) -> tuple[list[str], Optional[bool], list[str]]:
    folder_path = Path(folder)
    issues: list[str] = []
    format_ok: Optional[bool] = None

    if not folder_path.exists():
        issues.append(
            _download_issue(
                f"Missing folder '{name}'",
                "The download step may have been skipped or saved to a different location",
            )
        )
        return issues, format_ok, []

    files = _download_list_files(folder_path)
    actual_count = len(files)
    if actual_count != expected_count:
        issues.append(
            _download_issue(
                (
                    f"Folder '{name}' contains {actual_count} files but "
                    f"expected {expected_count}"
                ),
                "Some class exports might not have been downloaded",
            )
        )

    invalid = sorted(path.name for path in files if path.suffix.lower() != expected_suffix)
    if invalid:
        format_ok = False
        issues.append(
            _download_issue(
                f"Folder '{name}' has files with unexpected extensions",
                "Files may have been exported or renamed in the wrong format",
            )
        )
    else:
        format_ok = True

    return issues, format_ok, invalid

def count_class_codes(class_map_file: str | Path) -> int:
    class_map_path = Path(class_map_file)
    with class_map_path.open(newline="", encoding="utf-8-sig") as handle:
        reader = csv.DictReader(handle)
        if reader.fieldnames is None or "Class Code" not in reader.fieldnames:
            raise ValueError("Class map is missing the 'Class Code' column.")
        return sum(1 for row in reader if row.get("Class Code", "").strip())


def check_downloaded_files(
    campus: str,
    class_map_file: str | Path,
    folder_specs: Mapping[str, tuple[str | Path, str]],
) -> bool:
    class_map_path = Path(class_map_file)

    if not class_map_path.exists():
        print(
            _download_issue(
                f"Class map file '{class_map_path.name}' not found at {class_map_path.parent}",
                "Cannot verify the expected number of classes",
            )
        )
        return False

    try:
        expected_classes = count_class_codes(class_map_path)
    except Exception as exc:  # noqa: BLE001
        print(
            _download_issue(
                f"Failed to read class map: {exc}",
                "The download verification could not be completed",
            )
        )
        return False

    print(
        f"Expected class files for {campus} based on class map: {expected_classes}\n"
    )

    overall_success = True
    for folder_name, (folder_path, suffix) in folder_specs.items():
        print(f"Checking folder '{folder_name}'...")
        folder_path = Path(folder_path)
        issues, format_ok, invalid_files = _download_folder_issues(
            folder_name, folder_path, expected_classes, suffix
        )
        if issues:
            overall_success = False
            for issue in issues:
                print(issue)

            if invalid_files:
                print("Unexpected file formats detected:")
                for file_name in invalid_files:
                    print(f"  - {file_name}")
                print()

            if format_ok is True:
                print(
                    f"Folder '{folder_name}' file formats are correct "
                    f"(expected '{suffix}' extension).\n"
                )
            elif format_ok is False:
                print(
                    f"Folder '{folder_name}' file formats have issues. "
                    "See details above.\n"
                )
            else:
                print(
                    f"Folder '{folder_name}' file formats could not be verified "
                    "because the folder is missing.\n"
                )
        else:
            print(
                f"Folder '{folder_name}' contains {expected_classes} files "
                f"with expected '{suffix}' format.\n"
            )

    return overall_success

VAU_REPORT_DIRECTORY = os.path.join(_PROJ_ROOT, 'Ready For Printing', 'VAU')



MAE_REPORT_DIRECTORY = os.path.join(_PROJ_ROOT, 'Ready For Printing', 'MAE')







# Ensure the directory exists else create one



#os.makedirs(os.path.dirname(output_path), exist_ok=True)







def set_campus_info(campus_code):



    global CAMPUS, to_email, cc_email



    if campus_code == "VAU":



        to_email = "rkhuwaja@spiritofmath.com"



        cc_email = "vaughan@spiritofmath.com"



        CAMPUS = campus_code



    elif campus_code == "MAE":



        to_email = "rkhuwaja@spiritofmath.com"



        cc_email = "markhameast@spiritofmath.com"



        CAMPUS = campus_code



    else:



        print("ERROR: Invalid campus code")







def check_duplicates_in_column(df, column_name):
    if PANDAS_AVAILABLE and hasattr(df, "duplicated"):
        duplicates = df[df.duplicated(column_name, keep=False)]  # type: ignore[index]

        if not duplicates.empty:  # type: ignore[union-attr]
            print()
            print("Duplicate students found:")

            print(f"Duplicate entries found in '{column_name}':")

            for index, row in duplicates.iterrows():  # type: ignore[union-attr]

                print(f"Row {index + 2}: {row[column_name]}")

            print()



        else:



            print(f"No duplicates found in '{column_name}'.")

        return

    if not isinstance(df, list):
        print(f"No duplicates found in '{column_name}'.")
        return

    seen: dict[str, list[int]] = {}
    for index, row in enumerate(df):
        if not isinstance(row, Mapping):
            continue
        value = _coerce_str(row.get(column_name, "")).strip()
        if not value:
            continue
        seen.setdefault(value, []).append(index)

    duplicates = [(idx, value) for value, positions in seen.items() for idx in positions if len(positions) > 1]

    if duplicates:
        print()
        print("Duplicate students found:")
        print(f"Duplicate entries found in '{column_name}':")
        for index, value in duplicates:
            print(f"Row {index + 2}: {value}")
        print()
    else:
        print(f"No duplicates found in '{column_name}'.")



def check_class_map(class_map: str) -> bool:
    directory = os.path.dirname(os.path.abspath(class_map))
    print(f"Processing files in directory: {directory}")
    print(f"Processing class map file: {class_map}")
    if PANDAS_AVAILABLE:
        try:
            df = pd.read_csv(class_map)  # type: ignore[assignment]
        except FileNotFoundError:
            print(f"File not found: {class_map}")
            return False
        except Exception as exc:  # noqa: BLE001
            print(f"An error occurred: {exc}")
            return False

        columns_to_check = ['Class Code', 'Attendance', 'Grades', 'ClassList']
        for column in columns_to_check:
            if column in df.columns:  # type: ignore[union-attr]
                check_duplicates_in_column(df, column)
            else:
                print(f"Column '{column}' not found in the CSV file.")

        print('Processed 1 file successfully')
        return True

    try:
        with open(class_map, newline='', encoding='utf-8-sig') as handle:
            reader = csv.DictReader(handle)
            rows = [row for row in reader if row]
            fieldnames = reader.fieldnames or []
    except FileNotFoundError:
        print(f"File not found: {class_map}")
        return False
    except Exception as exc:  # noqa: BLE001
        print(f"An error occurred: {exc}")
        return False

    columns_to_check = ['Class Code', 'Attendance', 'Grades', 'ClassList']
    for column in columns_to_check:
        if column in fieldnames:
            check_duplicates_in_column(rows, column)
        else:
            print(f"Column '{column}' not found in the CSV file.")

    print('Processed 1 file successfully')
    return True
def strip_hash(input_string):



    cleaned_str = ''.join(c for c in input_string if c.isdigit())







    while cleaned_str.startswith('0') and len(cleaned_str) > 1:



        cleaned_str = cleaned_str[1:]







    return cleaned_str



    



    #return result











# Function to clean a cell value



def clean_cell(cell_value):



    if isinstance(cell_value, str):



        cleaned_value = re.sub(r'^[^a-zA-Z0-9]+|[^a-zA-Z0-9]+$', '', cell_value)



        return cleaned_value



    else:



        return cell_value



    







def send_email(to: str | None, cc: str | None, subject: str, body: str) -> bool:
    if not SEND_EMAIL:
        print("INFO: SEND_EMAIL is disabled; skipping email dispatch.")
        return False
    if not to:
        warn_once("WARNING", "No primary recipient specified for email; skipping send.")
        return False

    outlook = _get_outlook_app()
    if outlook is None:
        return False

    try:
        mail = outlook.CreateItem(0)
        date_string = datetime.now().strftime('%B %d, %Y')
        campus_prefix = f"{CAMPUS}: " if CAMPUS else ""

        mail.To = to
        mail.CC = cc or ""
        mail.Subject = f"{campus_prefix}{date_string}: {subject}"
        mail.HTMLBody = body or ""
        mail.Send()
        time.sleep(2)
        return True
    except Exception as exc:
        global _OUTLOOK_APP
        _OUTLOOK_APP = None
        print(f"ERROR: Failed to send email via Outlook: {exc}")
        return False



def send_duplicate_notification(
    *,
    subject: str,
    intro_html: str,
    duplicates: TableData | object | None = None,
    details_html: str | None = None,
    closing_html: str | None = None,
) -> bool:
    """Send a duplicate summary email using Outlook."""
    if not SEND_EMAIL:
        print("INFO: SEND_EMAIL is disabled; skipping duplicate notification email.")
        return False

    recipient_to = to_email
    recipient_cc = to_email if TESTING else cc_email

    body_parts: list[str] = []
    if intro_html:
        body_parts.append(intro_html.strip())
    duplicates_table = ensure_table_data(duplicates)
    if duplicates_table is not None and not duplicates_table.is_empty:
        body_parts.append(render_html_table(duplicates_table, title='Potential duplicate students'))
    if details_html:
        body_parts.append(details_html.strip())
    if closing_html:
        body_parts.append(closing_html.strip())

    if not body_parts:
        warn_once("WARNING", "Attempted to send duplicate notification email with empty body; skipping.")
        return False

    return send_email(recipient_to, recipient_cc, subject, "<br><br>".join(body_parts))


def create_pdf_from_html(html: str, output_path: str) -> bool:
    if pdfkit is None:
        warn_once("WARNING", "pdfkit is not installed; skipping PDF creation.")
        return False

    try:
        config = pdfkit.configuration(wkhtmltopdf='C:/Program Files/wkhtmltopdf/bin/wkhtmltopdf.exe')
    except (OSError, IOError) as exc:
        print(f"ERROR: Unable to configure wkhtmltopdf: {exc}")
        return False

    options = {
        'enable-local-file-access': '',
        'quiet': ''
    }

    try:
        pdfkit.from_string(html, output_path, configuration=config, options=options)
        print(f"PDF saved at {output_path}")
        return True
    except IOError as exc:
        print(f"ERROR: IO issue while generating PDF '{output_path}': {exc}")
    except Exception as exc:
        print(f"ERROR: Unexpected issue while generating PDF '{output_path}': {exc}")
    return False


# Function to convert date format



def convert_date_format(value, context="Last Accessed") -> str:
    parsed = parse_datetime(value, context)
    if parsed is None:
        fallback_date = datetime(2024, 9, 1)
        return fallback_date.strftime('%b %d, %Y')
    return parsed.strftime('%b %d, %Y')



def is_within_days(value, days: int) -> bool:
    parsed = parse_datetime(value, f"date threshold ({days} days)")
    if parsed is None:
        # Treat unparseable dates as needing attention
        return True
    threshold = datetime.now() - timedelta(days=days)
    return parsed < threshold


# Generate HTML code for head and body start



def generate_html_head_and_body_start():



    html_content = """



    <!DOCTYPE html>



    <html>



    <head>



        <style>



            body {



                font-family: Arial, sans-serif;



            }



            .custom-font {



                font-family: Arial, sans-serif;



            }



            table, th, td {



                border: 1px solid black;



            }



            table {



                border-collapse: collapse; 



            }



        </style>



    </head>



    <body>



    """



    return html_content







# Generate HTML code for table start



def generate_html_table_start():



    table_content_start = """



                <table> \



                <thead>



                    <tr>



                        <th>First Name</th>



                        <th>Last Name</th>



                        <th>Org Defined ID</th>



                        <th>Attendance (%)</th>



                    </tr>



                </thead>



                <tbody>



            """



    return table_content_start







# Generate HTML code for table start



def generate_html_grades_table_start():



    table_content_start = """



                <table border="1"> \



                <thead>



                    <tr>



                        <th>First Name</th>



                        <th>Last Name</th>



                        <th>Org Defined ID</th>



                        <th>Grade (%)</th>



                        <th>Email</th>



                    </tr>



                </thead>



                <tbody>



            """



    return table_content_start







# Generate HTML code for table end



def generate_html_table_end():



    table_content_end = """



                    </tbody>



                </table>



    """



    return table_content_end







# Function to strip leading '#'



def strip_leading_hash(s):



    return s.lstrip('#')







def calculate_final_grade(row: pd.Series) -> int:
    numerator = pd.to_numeric(row.get('Calculated Final Grade Numerator', 0), errors='coerce')
    denominator = pd.to_numeric(row.get('Calculated Final Grade Denominator', 0), errors='coerce')

    if pd.isna(numerator):
        numerator = 0
    if pd.isna(denominator) or denominator == 0:
        return 0

    try:
        final_grade = int(round(100 * float(numerator) / float(denominator)))
    except Exception as exc:
        print(f"WARNING: Failed to calculate final grade for row: {exc}")
        return 0
    return final_grade












# Read each HTML file in this directory using pandas library


def _iter_table_headers_and_rows(soup: BeautifulSoup) -> Iterable[tuple[list[str], list[list[str]]]]:
    for table in soup.find_all('table'):
        rows: list[list[str]] = []
        headers: list[str] = []
        for tr in table.find_all('tr'):
            cells = tr.find_all(['th', 'td'])
            if not cells:
                continue
            values = [cell.get_text(strip=True) for cell in cells]
            if not headers:
                headers = values
                continue
            if not headers:
                continue
            while len(values) < len(headers):
                values.append("")
            rows.append(values[:len(headers)])
        if headers:
            yield headers, rows


def _extract_students_from_table(headers: list[str], rows: list[list[str]], class_code: str) -> list[dict[str, object]]:
    normalized_headers = [normalize(item) for item in headers]

    target_columns = ("org defined id", "orgdefinedid", "username")
    if not any(keyword in normalized_headers for keyword in target_columns):
        return []
    if not any('role' in header for header in normalized_headers):
        return []

    id_col = find_first_matching_column(headers, target_columns)
    if id_col is None:
        return []

    role_col = find_first_matching_column(headers, ("role", "student role"))
    if role_col is None:
        return []

    username_col = find_first_matching_column(headers, ("username", "user name", "email"))
    full_name_col = find_first_matching_column(headers, ("full name", "student name", "name"))
    first_name_col = find_first_matching_column(headers, ("first name",))
    last_name_col = find_first_matching_column(headers, ("last name",))
    last_access_col = find_first_matching_column(headers, ("last accessed", "last accessed date"))

    def row_dict(values: list[str]) -> dict[str, object]:
        return {header: values[idx] if idx < len(values) else "" for idx, header in enumerate(headers)}

    result: list[dict[str, object]] = []
    for values in rows:
        record = row_dict(values)
        role_value = _coerce_str(record.get(role_col, ""))
        if "student" not in role_value.lower():
            continue

        student_id = extract_student_id(record.get(id_col), record.get(username_col) if username_col else None)
        if not student_id:
            continue

        if full_name_col:
            student_name = _coerce_str(record.get(full_name_col)).strip()
        else:
            first = _coerce_str(record.get(first_name_col)).strip() if first_name_col else ""
            last = _coerce_str(record.get(last_name_col)).strip() if last_name_col else ""
            student_name = (first + " " + last).strip()

        last_access = _coerce_str(record.get(last_access_col)).strip() if last_access_col else ""

        result.append({
            'Org Defined ID': student_id,
            'Student Full Name': student_name,
            'Last Accessed': last_access,
            'Class Code': class_code or 'UNKNOWN',
        })

    return result


def _read_html_text(filename: str) -> str | None:
    for encoding in ("utf-8", "utf-8-sig", "cp1252"):
        try:
            with open(filename, 'r', encoding=encoding) as handle:
                return handle.read()
        except UnicodeDecodeError:
            continue
        except Exception as exc:
            print(f"WARNING: Could not open '{filename}': {exc}")
            return None

    print(f"WARNING: Could not decode '{filename}' with supported encodings")
    return None


def _read_html_tables(filename: str, html_text: str) -> list[pd.DataFrame]:
    last_error: Exception | None = None

    for source in (StringIO(html_text), filename):
        try:
            return pd.read_html(source, encoding='utf-8')
        except ValueError:
            continue
        except Exception as exc:
            last_error = exc

    if last_error is not None:
        print(f"WARNING: Failed to read tables from '{filename}': {last_error}")
    else:
        warn_once("WARNING", f"No tables found in class list file '{filename}'")

    return []


def _find_student_table_from_tables(tables: list[pd.DataFrame]) -> pd.DataFrame | None:
    target_columns = ("org defined id", "orgdefinedid", "username")

    for table in tables:
        table = table.dropna(axis=1, how='all')
        table = table.dropna(how='all')
        if table.empty:
            continue

        table.columns = [str(col).strip() for col in table.columns]
        normalized_columns = [normalize(col) for col in table.columns]

        if not any(keyword in normalized_columns for keyword in target_columns):
            header_index = None
            header_values: list[str] | None = None
            for idx, row in table.iterrows():
                normalized_row = [normalize(value) for value in row]
                if any(keyword in value for value in normalized_row for keyword in target_columns):
                    header_index = idx
                    header_values = [str(value).strip() for value in row]
                    break
            if header_index is not None and header_values is not None:
                table = table.iloc[header_index + 1:].reset_index(drop=True)
                table.columns = header_values
                normalized_columns = [normalize(col) for col in table.columns]

        if any(keyword in normalized_columns for keyword in target_columns):
            if table.empty:
                continue
            if not any('role' in col for col in normalized_columns):
                continue
            return table

    return None


def _extract_students_from_dataframe(student_table: pd.DataFrame, class_code: str, filename: str) -> list[dict[str, object]]:
    role_col = find_first_matching_column(student_table, ("role", "student role"))
    if role_col is None:
        warn_once("WARNING", f"Missing role column in '{filename}'")
        return []

    student_rows = student_table[student_table[role_col].astype(str).str.contains('student', case=False, na=False)]
    if student_rows.empty:
        warn_once("WARNING", f"No student rows found in '{filename}'")
        return []

    id_col = find_first_matching_column(student_table, ("org defined id", "orgdefinedid", "username", "user id"))
    if id_col is None:
        warn_once("WARNING", f"Missing Org Defined ID column in '{filename}'")
        return []

    full_name_col = find_first_matching_column(student_table, ("full name", "student name", "name"))
    first_name_col = find_first_matching_column(student_table, ("first name",))
    last_name_col = find_first_matching_column(student_table, ("last name",))

    if full_name_col is not None:
        name_series = student_rows[full_name_col].astype(str)
    else:
        first_series = student_rows[first_name_col].astype(str) if first_name_col else pd.Series([''] * len(student_rows))
        last_series = student_rows[last_name_col].astype(str) if last_name_col else pd.Series([''] * len(student_rows))
        name_series = (first_series.fillna('') + ' ' + last_series.fillna('')).str.strip()

    last_accessed_col = find_first_matching_column(student_table, ("last accessed", "last access", "last login", "last activity"))
    if last_accessed_col is None:
        warn_once("WARNING", f"Missing last accessed column in '{filename}'")
        return []

    username_col = find_first_matching_column(student_table, ("username", "user name", "email"))
    if username_col:
        fallback_values = student_rows[username_col]
    else:
        fallback_values = [None] * len(student_rows)

    org_ids = [
        extract_student_id(primary, fallback)
        for primary, fallback in zip(student_rows[id_col], fallback_values)
    ]

    student_data = pd.DataFrame({
        'Org Defined ID': org_ids,
        'Student Full Name': name_series,
        'Last Accessed': student_rows[last_accessed_col],
        'Class Code': class_code,
    })

    student_data = student_data.dropna(subset=['Org Defined ID'])
    if student_data.empty:
        warn_once("WARNING", f"No valid student IDs found in '{filename}'")
        return []

    student_data['Org Defined ID'] = student_data['Org Defined ID'].astype(str)
    student_data['Last Accessed'] = student_data['Last Accessed'].apply(
        lambda value: convert_date_format(value, 'class list last accessed')
    )
    return student_data.to_dict(orient='records')


def _collect_class_list_students(class_list_dir_path: str) -> TableData:
    seed_columns = ['Org Defined ID', 'Student Full Name', 'Last Accessed', 'Class Code']
    print(f"Processing files in directory: {class_list_dir_path}\n")

    if not class_list_dir_path or not os.path.exists(class_list_dir_path):
        print(f"ERROR: Class list directory not found: {class_list_dir_path}")
        return TableData(seed_columns, [])

    file_paths = sorted(glob.glob(os.path.join(class_list_dir_path, '*.html')))
    if not file_paths:
        warn_once("WARNING", f"No HTML files found in {class_list_dir_path}")
        return TableData(seed_columns, [])

    file_count = 0
    records: list[dict[str, object]] = []

    for filename in file_paths:
        html_text = _read_html_text(filename)
        if html_text is None:
            continue

        soup = BeautifulSoup(html_text, 'html.parser') if BS4_AVAILABLE else None
        class_code = get_class_code_from_html(soup or html_text) or 'UNKNOWN'
        tables = _read_html_tables(filename, html_text)
        student_table = _find_student_table_from_tables(tables)
        extracted = _extract_students_from_dataframe(student_table, class_code, filename) if student_table is not None else []

        if not extracted:
            warn_once("WARNING", f"Could not identify student table in '{filename}'")
            continue

        records.extend(extracted)
        file_count += 1

    print(f"Processed {file_count} files successfully\n")
    return TableData(seed_columns, records)


def add_class_list_data(master_df: pd.DataFrame, class_list_dir_path: str) -> pd.DataFrame:
    """Extract students from Brightspace class list HTML exports."""
    print(f"Processing files in directory: {class_list_dir_path}\n")

    if not class_list_dir_path or not os.path.exists(class_list_dir_path):
        print(f"ERROR: Class list directory not found: {class_list_dir_path}")
        return master_df

    file_paths = sorted(glob.glob(os.path.join(class_list_dir_path, '*.html')))
    if not file_paths:
        warn_once("WARNING", f"No HTML files found in {class_list_dir_path}")
        return master_df

    file_count = 0

    for filename in file_paths:
        html_text = _read_html_text(filename)
        if html_text is None:
            continue

        soup = BeautifulSoup(html_text, 'html.parser') if BS4_AVAILABLE else None
        class_code = get_class_code_from_html(soup or html_text) or 'UNKNOWN'
        tables = _read_html_tables(filename, html_text)
        student_table = _find_student_table_from_tables(tables)

        if student_table is None:
            warn_once("WARNING", f"Could not identify student table in '{filename}'")
            continue

        records = _extract_students_from_dataframe(student_table, class_code, filename)
        if not records:
            continue

        student_data = pd.DataFrame.from_records(records)
        master_df = pd.concat([master_df, student_data], ignore_index=True)
        file_count += 1

    master_df = master_df.reset_index(drop=True)
    print()
    print(f"Processed {file_count} files successfully")
    print(f"Final master DataFrame has {len(master_df)} rows")
    return master_df


def get_attendance_data(attendance_dir: str) -> pd.DataFrame:
    """Get attendance data from Brightspace CSV exports."""
    if not attendance_dir or not os.path.exists(attendance_dir):
        print(f"ERROR: Attendance directory not found: {attendance_dir}")
        return pd.DataFrame()

    csv_paths = sorted(glob.glob(os.path.join(attendance_dir, '*.csv')))
    if not csv_paths:
        warn_once("WARNING", f"No attendance CSV files found in {attendance_dir}")
        return pd.DataFrame()

    frames: list[pd.DataFrame] = []

    for filename in csv_paths:
        try:
            df = pd.read_csv(filename)
        except Exception as exc:
            print(f"WARNING: Unable to read attendance file '{filename}': {exc}")
            continue

        if df.empty:
            warn_once("WARNING", f"Attendance file '{filename}' is empty")
            continue

        id_col = find_first_matching_column(df, ("org defined id", "orgdefinedid", "org definedid", "student id"))
        if id_col is None:
            warn_once("WARNING", f"Skipping '{filename}' - no Org Defined ID column found")
            continue

        username_col = find_first_matching_column(df, ("username", "user name", "email"))

        def compute_student_id(row):
            fallback = row[username_col] if username_col else None
            return extract_student_id(row[id_col], fallback)

        df['Org Defined ID'] = df.apply(compute_student_id, axis=1)
        df = df.dropna(subset=['Org Defined ID'])
        if df.empty:
            warn_once("WARNING", f"No valid Org Defined ID entries in '{filename}'")
            continue

        df['Org Defined ID'] = df['Org Defined ID'].astype(str)

        attendance_col = find_first_matching_column(df, ("% attendance", "attendance (%)", "attendance percent", "attendance%"))
        if attendance_col is None:
            warn_once("WARNING", f"'% Attendance' column not found in '{filename}'")
            df['% Attendance'] = np.nan
        else:
            df['% Attendance'] = pd.to_numeric(df[attendance_col], errors='coerce')

        class_code = os.path.splitext(os.path.basename(filename))[0]
        df['Class Code'] = class_code
        frames.append(df)

    if not frames:
        print("No attendance data found")
        return pd.DataFrame()

    attendance_df = pd.concat(frames, ignore_index=True)
    print(f"Found attendance data for {len(attendance_df)} students")
    return attendance_df


def get_grades_data(grades_dir: str) -> pd.DataFrame:
    """Get grades data from Brightspace CSV exports."""
    if not grades_dir or not os.path.exists(grades_dir):
        print(f"ERROR: Grades directory not found: {grades_dir}")
        return pd.DataFrame()

    csv_paths = sorted(glob.glob(os.path.join(grades_dir, '*.csv')))
    if not csv_paths:
        warn_once("WARNING", f"No grades CSV files found in {grades_dir}")
        return pd.DataFrame()

    frames: list[pd.DataFrame] = []

    for filename in csv_paths:
        try:
            df = pd.read_csv(filename)
        except Exception as exc:
            print(f"WARNING: Unable to read grades file '{filename}': {exc}")
            continue

        if df.empty:
            warn_once("WARNING", f"Grades file '{filename}' is empty")
            continue

        id_col = find_first_matching_column(df, ("orgdefinedid", "org defined id", "student id", "org-defined-id"))
        if id_col is None:
            warn_once("WARNING", f"Skipping '{filename}' - no OrgDefinedId column found")
            continue

        username_col = find_first_matching_column(df, ("username", "user name", "email"))

        def compute_student_id(row):
            fallback = row[username_col] if username_col else None
            return extract_student_id(row[id_col], fallback)

        org_ids = df.apply(compute_student_id, axis=1)
        valid_mask = org_ids.notna()
        if not valid_mask.any():
            warn_once("WARNING", f"No valid OrgDefinedId entries in '{filename}'")
            continue

        filtered = df.loc[valid_mask]
        org_ids = org_ids.loc[valid_mask].astype(str)

        parent_email_col = find_first_matching_column(df, ("parent email", "parentemail", "email"))
        if parent_email_col is not None:
            parent_email = filtered[parent_email_col]
        else:
            parent_email = pd.Series([None] * len(filtered), index=filtered.index, dtype='object')

        start_week_col = find_first_matching_column(df, ("enrolment start week points grade", "start week"))
        if start_week_col is not None:
            start_week = pd.to_numeric(filtered[start_week_col], errors='coerce').fillna(-1).astype('int64')
        else:
            start_week = pd.Series([-1] * len(filtered), index=filtered.index, dtype='int64')

        final_grade = filtered.apply(calculate_final_grade, axis=1).astype(int)
        class_code = os.path.splitext(os.path.basename(filename))[0]

        result = pd.DataFrame({
            'OrgDefinedId': org_ids.to_numpy(),
            'Class Code': class_code,
            'Parent Email': parent_email.to_numpy(),
            'Start Week': start_week.to_numpy(),
            'Final Grade': final_grade.to_numpy(),
        })
        frames.append(result)

    if not frames:
        print("No grades data found")
        return pd.DataFrame()

    grades_df = pd.concat(frames, ignore_index=True)
    print(f"Found grades data for {len(grades_df)} students")
    return grades_df


def get_class_code_from_html(document: object | None) -> Optional[str]:
    """Extract a class code from HTML content or a BeautifulSoup document."""
    if document is None:
        return None

    def _match_code(candidate: str | None) -> Optional[str]:
        if not candidate:
            return None
        match = CLASS_CODE_REGEX.search(candidate)
        if match:
            return match.group(0)
        return None

    if BS4_AVAILABLE and hasattr(document, 'find'):
        soup = document
        for element in [
            soup.find('a', class_='d2l-navigation-s-link'),
            soup.find('div', class_='d2l-navigation-s-main-wrapper'),
            soup.find('title'),
        ]:
            if element:
                code = _match_code(element.get_text(strip=True))
                if code:
                    return code

        for tag in soup.find_all(['a', 'span', 'div']):
            code = _match_code(tag.get_text(strip=True))
            if code:
                return code

        code = _match_code(soup.get_text())
        if code:
            return code

    raw_html = _coerce_str(document)
    title_match = re.search(r'<title[^>]*>(.*?)</title>', raw_html, flags=re.IGNORECASE | re.DOTALL)
    if title_match:
        code = _match_code(html.unescape(re.sub(r'<[^>]+>', ' ', title_match.group(1))))
        if code:
            return code

    text_content = html.unescape(re.sub(r'<[^>]+>', ' ', raw_html))
    code = _match_code(text_content)
    if code:
        return code

    warn_once("WARNING", "Could not locate a class code pattern in class list HTML")
    return None


def FindDupStudentsInBSViaClassList(
    BSdirectory: str,
    collect_duplicates: list[TableData] | None = None,
) -> bool:
    if not BSdirectory or not os.path.exists(BSdirectory):
        print(f"ERROR: Directory not found: {BSdirectory}")
        return True

    student_table = _collect_class_list_students(BSdirectory)

    if student_table.is_empty:
        print("No student data found in any of the HTML files.")
        return True

    def detect_duplicates(column_name: str) -> TableData:
        counts: dict[str, int] = {}
        for row in student_table.rows:
            value = _coerce_str(row.get(column_name, "")).strip()
            if not value:
                continue
            counts[value] = counts.get(value, 0) + 1
        duplicate_rows = [
            row for row in student_table.rows
            if counts.get(_coerce_str(row.get(column_name, "")).strip(), 0) > 1
        ]
        return TableData(student_table.columns, duplicate_rows)

    duplicates = detect_duplicates('Org Defined ID')
    if duplicates.is_empty:
        duplicates = detect_duplicates('Student Full Name')

    if not duplicates.is_empty:
        print()
        print("Duplicate students found:")
        sorted_duplicates = duplicates.sorted(['Student Full Name', 'Org Defined ID'])
        print(sorted_duplicates.to_string())
        if collect_duplicates is not None:
            collect_duplicates.append(sorted_duplicates)
        return False

    print("No duplicates found in Brightspace class lists")
    return True



def _extract_ids_from_first_column(file_path: str, column_name: str, base_name: str) -> list[dict[str, object]]:
    extracted_rows: list[dict[str, object]] = []
    try:
        with open(file_path, newline='', encoding='utf-8-sig') as raw_handle:
            reader = csv.reader(raw_handle)
            for row in reader:
                if not row:
                    continue
                value = row[0]
                match = re.search(r'(\d+)', value)
                if match:
                    extracted_rows.append({
                        column_name: match.group(1),
                        'Student Name': '',
                        'File Name': base_name,
                    })
    except Exception as exc:  # noqa: BLE001
        print(f"WARNING: Unable to parse '{file_path}' without headers: {exc}")
    return extracted_rows


def FindDupStudentsInBSViaAttendanceGrades(
    target_dir: str,
    column_name: str,
    *,
    collect_duplicates: list[TableData] | None = None,
    send_notification: bool = True,
) -> bool:
    if not target_dir or not os.path.exists(target_dir):
        print(f"Directory not found: {target_dir}")
        return True

    print(f"Processing files in directory: {target_dir}")

    csv_files = sorted(f for f in glob.glob(os.path.join(target_dir, '*.csv')) if os.path.isfile(f))
    if not csv_files:
        print('Processed 0 files successfully')
        print(f"No CSV files found in directory: {target_dir}")
        return True

    records: list[dict[str, object]] = []
    processed_count = 0

    for file_path in csv_files:
        base_name = os.path.basename(file_path)

        try:
            with open(file_path, newline='', encoding='utf-8-sig') as handle:
                reader = csv.DictReader(handle)
                rows = [row for row in reader if row]
                fieldnames = reader.fieldnames or []
        except Exception as exc:  # noqa: BLE001
            print(f"WARNING: Error reading '{file_path}': {exc}")
            continue

        if not fieldnames:
            extracted = _extract_ids_from_first_column(file_path, column_name, base_name)
            if extracted:
                records.extend(extracted)
                processed_count += 1
            continue

        id_col = column_name if column_name in fieldnames else find_first_matching_column(fieldnames, ('orgdefinedid', 'org defined id', 'student id', 'username'))

        if id_col is None:
            extracted = _extract_ids_from_first_column(file_path, column_name, base_name)
            if extracted:
                records.extend(extracted)
                processed_count += 1
            else:
                warn_once('WARNING', f"Missing identifier column in '{file_path}'")
            continue

        username_col = find_first_matching_column(fieldnames, ('username', 'user name', 'email'))
        first_name_col = find_first_matching_column(fieldnames, ('first name',))
        last_name_col = find_first_matching_column(fieldnames, ('last name',))
        full_name_col = find_first_matching_column(fieldnames, ('student full name', 'name', 'full name'))

        processed_this_file = False
        for row in rows:
            student_id = extract_student_id(row.get(id_col), row.get(username_col) if username_col else None)
            if not student_id:
                continue

            if full_name_col:
                student_name = _coerce_str(row.get(full_name_col)).strip()
            else:
                first = _coerce_str(row.get(first_name_col)).strip() if first_name_col else ""
                last = _coerce_str(row.get(last_name_col)).strip() if last_name_col else ""
                if first or last:
                    student_name = (first + " " + last).strip()
                else:
                    student_name = _coerce_str(row.get(username_col)).strip() if username_col else ""

            records.append({
                column_name: student_id,
                'Student Name': student_name,
                'File Name': base_name,
            })
            processed_this_file = True

        if processed_this_file:
            processed_count += 1
        else:
            warn_once('WARNING', f"No valid student identifiers in '{file_path}'")

    print()
    print(f"Processed {processed_count} files successfully")

    if not records:
        print(f"No files with required columns found in directory: {target_dir}")
        return True

    counts = Counter(_coerce_str(row.get(column_name, "")).strip() for row in records if _coerce_str(row.get(column_name, "")).strip())
    duplicate_rows = [
        row for row in records
        if counts.get(_coerce_str(row.get(column_name, "")).strip(), 0) > 1
    ]

    if not duplicate_rows:
        print('No duplicates found in Brightspace classes - checked via Attendance or Grades')
        return True

    print()
    print('Found duplicate student IDs:')
    duplicates_table = TableData([column_name, 'Student Name', 'File Name'], duplicate_rows).sorted([column_name, 'Student Name'])
    print(duplicates_table.to_string())

    if collect_duplicates is not None:
        collect_duplicates.append(duplicates_table)

    if send_notification:
        send_duplicate_notification(
            subject='Please check and remove duplicates in Brightspace classes',
            intro_html=(
                'Hello Office, <br><br>'
                'I ran a report today, and the following students are registered in one or more classes in BrightSpace. '
                'Please check and remove duplicates. Thank you.'
            ),
            duplicates=duplicates_table,
            closing_html='Sincerely, <br>Ramzan Khuwaja',
        )

    return False

def GenerateStudentMap(campus):
    """Generate student map by combining data from various sources."""
    campus = campus.upper() if isinstance(campus, str) else campus

    if campus == "VAU":
        class_list_dir_path = VAU_CLASS_LIST_DIR
        class_map_file = VAU_CLASS_MAP_FILE
        attendance_dir = VAU_ATTENDANCE_DIR
        grades_dir = VAU_GRADES_DIR
        student_map_file = VAU_STUDENT_MAP_FILE
    elif campus == "MAE":
        class_list_dir_path = MAE_CLASS_LIST_DIR
        class_map_file = MAE_CLASS_MAP_FILE
        attendance_dir = MAE_ATTENDANCE_DIR
        grades_dir = MAE_GRADES_DIR
        student_map_file = MAE_STUDENT_MAP_FILE
    else:
        print(f"ERROR: Invalid campus name '{campus}'")
        return False

    pd.set_option('display.max_columns', None)

    columns = [
        'Org Defined ID',
        'Student Full Name',
        'Last Accessed',
        'Class Code',
        'Teacher Full Name',
        'Teacher Email',
        'Teacher Group',
        'Attendance (%)',
        'Parent Email',
        'Start Week',
        'Final Grade',
        'Att Uptodate?'
    ]
    StudentMap = pd.DataFrame(columns=columns)

    column_types = {
        'Org Defined ID': str,
        'Student Full Name': str,
        'Last Accessed': str,
        'Class Code': str,
        'Teacher Full Name': str,
        'Teacher Email': str,
        'Teacher Group': str,
        'Attendance (%)': float,
        'Parent Email': str,
        'Start Week': np.int64,
        'Final Grade': float,
        'Att Uptodate?': bool
    }
    StudentMap = StudentMap.astype(column_types)

    print()
    print("Start - Adding class list data")
    StudentMap = add_class_list_data(StudentMap, class_list_dir_path)
    if StudentMap.empty:
        print("ERROR: No data was added from class lists")
        return False
    print("End - Adding class list data")

    print()
    print("Start - Reading class map")
    if not os.path.exists(class_map_file):
        print(f"ERROR: Class map file not found: {class_map_file}")
        return False
    try:
        ClassMap = pd.read_csv(class_map_file)
    except Exception as exc:
        print(f"ERROR: Failed to read class map '{class_map_file}': {exc}")
        return False

    required_class_cols = {'Class Code', 'Teacher Full Name', 'Teacher Email', 'Teacher Group'}
    missing_class_cols = [col for col in required_class_cols if col not in ClassMap.columns]
    if missing_class_cols:
        warn_once("WARNING", f"Missing columns {missing_class_cols} in class map; teacher info may be incomplete")

    teacher_lookup = {}
    if 'Class Code' in ClassMap.columns:
        teacher_lookup = ClassMap.drop_duplicates('Class Code').set_index('Class Code').to_dict('index')

    print(f"Read {len(ClassMap)} entries from class map")
    print("End - Reading class map")

    print()
    print("Start - Copying StudentMap data")
    teacher_matches = 0
    missing_codes: set[str] = set()

    for index, row in StudentMap.iterrows():
        class_code = row['Class Code']
        details = teacher_lookup.get(class_code)
        if details:
            StudentMap.at[index, 'Teacher Full Name'] = details.get('Teacher Full Name', '')
            StudentMap.at[index, 'Teacher Email'] = details.get('Teacher Email', '')
            StudentMap.at[index, 'Teacher Group'] = details.get('Teacher Group', '')
            teacher_matches += 1
        else:
            missing_codes.add(class_code)

    print(f"Found teacher info for {teacher_matches} students")
    if missing_codes:
        sample_codes = sorted(missing_codes)[:5]
        warn_once("WARNING", f"No teacher mapping for {len(missing_codes)} class codes (e.g., {sample_codes})")
    print("End - Copying StudentMap data")

    print()
    print("Start - Getting attendance data")
    attendance_df = get_attendance_data(attendance_dir)
    print("End - Getting attendance data")

    attendance_lookup: dict[str, dict] = {}
    lesson_week = max(THIS_WEEK_NUM - 2, 1)
    lesson_col = f"Lesson {lesson_week}"

    if not attendance_df.empty:
        if 'Org Defined ID' in attendance_df.columns:
            attendance_df['Org Defined ID'] = attendance_df['Org Defined ID'].astype(str)
            attendance_lookup = attendance_df.drop_duplicates('Org Defined ID').set_index('Org Defined ID').to_dict('index')
        else:
            warn_once("WARNING", "'Org Defined ID' column missing in attendance data")
    else:
        warn_once("WARNING", "Attendance data unavailable")

    lesson_available = not attendance_df.empty and lesson_col in attendance_df.columns
    student_ids = {str(x).strip() for x in StudentMap['Org Defined ID'].dropna() if str(x).strip()} 
    attendance_ids = set(attendance_lookup.keys()) if attendance_lookup else set()

    if attendance_ids:
        missing_students = student_ids - attendance_ids
        extra_attendance = attendance_ids - student_ids

        if missing_students:
            sample_missing = sorted(missing_students)[:5]
            warn_once("WARNING", f"{len(missing_students)} students missing attendance entries (e.g., {sample_missing})")

        if extra_attendance:
            sample_extra = sorted(extra_attendance)[:5]
            warn_once("WARNING", f"{len(extra_attendance)} attendance records have unknown student IDs (e.g., {sample_extra})")


    print()
    print("Start - Copying attendance data")
    attendance_matches = 0
    for index, row in StudentMap.iterrows():
        student_id = row['Org Defined ID']
        StudentMap.at[index, 'Att Uptodate?'] = False
        if student_id and student_id in attendance_lookup:
            matching_row = attendance_lookup[student_id]
            attendance_value = matching_row.get('% Attendance')
            if attendance_value is None:
                attendance_value = matching_row.get('% attendance')
            StudentMap.at[index, 'Attendance (%)'] = attendance_value
            attendance_matches += 1

            if lesson_available:
                lesson_value = matching_row.get(lesson_col)
                if pd.isna(lesson_value) or str(lesson_value).strip() in {'', '-'}:
                    StudentMap.at[index, 'Att Uptodate?'] = False
                else:
                    StudentMap.at[index, 'Att Uptodate?'] = True
        else:
            StudentMap.at[index, 'Attendance (%)'] = np.nan

    print(f"Found attendance records for {attendance_matches} students")
    print("End - Copying attendance data")

    print()
    print("Start - Getting grade data")
    grades_df = get_grades_data(grades_dir)
    print("End - Getting grade data")

    grade_lookup: dict[str, dict] = {}
    if not grades_df.empty:
        if 'OrgDefinedId' in grades_df.columns:
            grades_df['OrgDefinedId'] = grades_df['OrgDefinedId'].astype(str)
            grade_lookup = grades_df.drop_duplicates('OrgDefinedId').set_index('OrgDefinedId').to_dict('index')
        else:
            warn_once("WARNING", "'OrgDefinedId' column missing in grade data")
    else:
        warn_once("WARNING", "Grade data unavailable")

    grade_ids = set(grade_lookup.keys()) if grade_lookup else set()

    if grade_ids:
        missing_grades = student_ids - grade_ids
        extra_grades = grade_ids - student_ids

        if missing_grades:
            sample_missing = sorted(missing_grades)[:5]
            warn_once("WARNING", f"{len(missing_grades)} students missing grade entries (e.g., {sample_missing})")

        if extra_grades:
            sample_extra = sorted(extra_grades)[:5]
            warn_once("WARNING", f"{len(extra_grades)} grade records have unknown student IDs (e.g., {sample_extra})")

    print()
    print("Start - Copying grade data")
    grade_matches = 0
    for index, row in StudentMap.iterrows():
        student_id = row['Org Defined ID']
        if student_id and student_id in grade_lookup:
            matching_row = grade_lookup[student_id]
            if matching_row.get('Parent Email'):
                StudentMap.at[index, 'Parent Email'] = matching_row.get('Parent Email')
            if matching_row.get('Final Grade') is not None:
                StudentMap.at[index, 'Final Grade'] = matching_row.get('Final Grade')
            start_week_val = matching_row.get('Start Week', -1)
            if pd.isna(start_week_val):
                start_week_val = -1
            StudentMap.at[index, 'Start Week'] = int(start_week_val)
            grade_matches += 1

    print(f"Found grade records for {grade_matches} students")
    print("End - Copying grade data")

    StudentMap['Attendance (%)'] = pd.to_numeric(StudentMap['Attendance (%)'], errors='coerce')
    StudentMap['Final Grade'] = pd.to_numeric(StudentMap['Final Grade'], errors='coerce')
    StudentMap['Start Week'] = pd.to_numeric(StudentMap['Start Week'], errors='coerce').fillna(-1).astype('int64')
    StudentMap['Att Uptodate?'] = (
        StudentMap['Att Uptodate?']
        .astype('boolean')
        .fillna(False)
        .astype(bool)
    )

    print("Start - Saving student map")
    try:
        output_dir = os.path.dirname(student_map_file)
        os.makedirs(output_dir, exist_ok=True)
        StudentMap.to_csv(student_map_file, index=False)
        print(f"Saved {len(StudentMap)} students to {student_map_file}")
        print("End - Saving student map\n")
    except Exception as exc:
        print(f"ERROR: Failed to save student map to '{student_map_file}': {exc}")
        return False

    missing_data = []
    if StudentMap['Parent Email'].isna().any():
        missing_data.append('Parent Email')
    if StudentMap['Final Grade'].isna().any():
        missing_data.append('Final Grade')
    if StudentMap['Attendance (%)'].isna().any():
        missing_data.append('Attendance (%)')

    if missing_data:
        warn_once("WARNING", f"Missing data in columns: {', '.join(missing_data)}")
        for column in missing_data:
            missing_ids = StudentMap.loc[StudentMap[column].isna(), 'Org Defined ID'].dropna().astype(str)
            sample_ids = sorted({id_.strip() for id_ in missing_ids if id_.strip()})[:5]
            print(f"WARNING: {column} missing for {len(missing_ids)} students (e.g., {sample_ids})")

    return True


def FindMissingAttendance(campus):
    print("Start - FindMissingAttendance")

    df_student_map = load_student_map(campus)
    if df_student_map.empty:
        return pd.DataFrame(columns=[
            "Org Defined ID",
            "Student Full Name",
            "Class Code",
            "Teacher Email",
            "Teacher Full Name",
            "Att Uptodate?",
            "Start Week"
        ])

    required_cols = {
        'Att Uptodate?',
        'Org Defined ID',
        'Student Full Name',
        'Class Code',
        'Teacher Email',
        'Teacher Full Name',
        'Start Week'
    }
    missing_cols = [col for col in required_cols if col not in df_student_map.columns]
    if missing_cols:
        warn_once("WARNING", f"Missing columns {missing_cols} in student map; unable to compute missing attendance")
        return pd.DataFrame()

    df_missing = df_student_map[df_student_map['Att Uptodate?'] == False]
    if df_missing.empty:
        return pd.DataFrame(columns=list(required_cols))

    df_result = df_missing[[
        'Org Defined ID',
        'Student Full Name',
        'Class Code',
        'Teacher Email',
        'Teacher Full Name',
        'Att Uptodate?',
        'Start Week'
    ]].copy()
    df_result['Start Week'] = pd.to_numeric(df_result['Start Week'], errors='coerce').fillna(-1).astype(int)
    return df_result


def email_att_missing_to_stakeholders(df_missing_attendance: pd.DataFrame) -> None:
    print("Start - email_to_stakeholders")

    if df_missing_attendance.empty:
        print("No missing attendance rows to email.")
        return

    required_cols = {'Teacher Email', 'Teacher Full Name', 'Org Defined ID', 'Student Full Name', 'Class Code', 'Att Uptodate?'}
    missing_cols = [col for col in required_cols if col not in df_missing_attendance.columns]
    if missing_cols:
        warn_once("WARNING", f"Missing columns {missing_cols} in missing attendance report; email not sent")
        return

    if not SEND_EMAIL:
        print("INFO: SEND_EMAIL disabled; skipping stakeholder notification.")
        return

    for email in df_missing_attendance['Teacher Email'].dropna().unique():
        df_teacher = df_missing_attendance[df_missing_attendance['Teacher Email'] == email]
        if df_teacher.empty:
            continue

        teacher = df_teacher['Teacher Full Name'].iloc[0]
        df_report = df_teacher[[
            'Org Defined ID', 'Student Full Name', 'Class Code', 'Att Uptodate?'
        ]].copy()

        if TESTING:
            to = to_email
            cc = ''
        else:
            to = email
            cc = cc_email

        subject_email = "Please update your Brightspace class data"
        table_html = render_html_table(
            df_report,
            title='Students requiring updates',
            subtitle='These classes have not been updated in Brightspace for the past two weeks.',
        )
        body_email = (
            f"Hello {teacher},<br><br>"
            "Spirit of Math advises parents and students to check their class attendance and marks on BrightSpace within one week after a class is completed.<br><br>"
            "Our records show that the following students/classes of yours have not been updated for the past two weeks."
            " Please update them as soon as possible and maintain the above practice for the rest of this school year.<br><br>"
            "No response is necessary - just make the applicable corrections. Thank you.<br><br>"
            f"{table_html}<br>Sincerely,<br>Ramzan Khuwaja<br><br>"
        )

        send_email(to, cc, subject_email, body_email)


def FindStrugglingStudents(campus):
    print("Start - FindStrugglingStudents")

    df_student_map = load_student_map(campus)
    if df_student_map.empty:
        return pd.DataFrame(columns=[
            "Org Defined ID",
            "Student Full Name",
            "Class Code",
            "Teacher Email",
            "Teacher Full Name",
            "Final Grade",
            "Start Week"
        ])

    required_cols = {
        'Final Grade',
        'Org Defined ID',
        'Student Full Name',
        'Class Code',
        'Teacher Email',
        'Teacher Full Name',
        'Start Week'
    }
    missing_cols = [col for col in required_cols if col not in df_student_map.columns]
    if missing_cols:
        warn_once("WARNING", f"Missing columns {missing_cols} in student map; unable to evaluate struggling students")
        return pd.DataFrame()

    df_student_map['Final Grade'] = pd.to_numeric(df_student_map['Final Grade'], errors='coerce')
    struggling = df_student_map[df_student_map['Final Grade'] < GRADES_MIN_BAR]
    if struggling.empty:
        return pd.DataFrame(columns=list(required_cols))

    result = struggling[[
        'Org Defined ID',
        'Student Full Name',
        'Class Code',
        'Teacher Email',
        'Teacher Full Name',
        'Final Grade',
        'Start Week'
    ]].copy()
    result['Start Week'] = pd.to_numeric(result['Start Week'], errors='coerce').fillna(-1).astype(int)
    return result


def FindHighHonoursStudents(campus):
    print("Start - FindHighHonoursStudents")

    df_student_map = load_student_map(campus)
    if df_student_map.empty:
        return pd.DataFrame(columns=[
            "Org Defined ID",
            "Student Full Name",
            "Class Code",
            "Teacher Email",
            "Teacher Full Name",
            "Final Grade",
            "Parent Email"
        ])

    required_cols = {
        'Final Grade',
        'Org Defined ID',
        'Student Full Name',
        'Class Code',
        'Teacher Email',
        'Teacher Full Name',
        'Parent Email'
    }
    missing_cols = [col for col in required_cols if col not in df_student_map.columns]
    if missing_cols:
        warn_once("WARNING", f"Missing columns {missing_cols} in student map; unable to evaluate high honours students")
        return pd.DataFrame()

    df_student_map['Final Grade'] = pd.to_numeric(df_student_map['Final Grade'], errors='coerce')
    honours = df_student_map[df_student_map['Final Grade'] >= HIGH_HONOURS_MIN_BAR]
    if honours.empty:
        return pd.DataFrame(columns=list(required_cols))

    return honours[[
        'Org Defined ID',
        'Student Full Name',
        'Class Code',
        'Teacher Email',
        'Teacher Full Name',
        'Final Grade',
        'Parent Email'
    ]].copy()


def FindNeedsToAttendMoreRegularly(campus):
    print("Start - FindNeedsToAttendMoreRegularly")

    df_student_map = load_student_map(campus)
    if df_student_map.empty:
        return pd.DataFrame(columns=[
            'Org Defined ID',
            'Student Full Name',
            'Class Code',
            'Teacher Email',
            'Teacher Full Name',
            'Attendance (%)',
            'Parent Email'
        ])

    required_cols = {
        'Attendance (%)',
        'Org Defined ID',
        'Student Full Name',
        'Class Code',
        'Teacher Email',
        'Teacher Full Name',
        'Parent Email'
    }
    missing_cols = [col for col in required_cols if col not in df_student_map.columns]
    if missing_cols:
        warn_once("WARNING", f"Missing columns {missing_cols} in student map; unable to evaluate attendance")
        return pd.DataFrame()

    df_student_map['Attendance (%)'] = pd.to_numeric(df_student_map['Attendance (%)'], errors='coerce')
    needs_regular = df_student_map[df_student_map['Attendance (%)'] < ATTENDANCE_MIN_BAR]
    if needs_regular.empty:
        return pd.DataFrame(columns=list(required_cols))

    return needs_regular[[
        'Org Defined ID',
        'Student Full Name',
        'Class Code',
        'Teacher Email',
        'Teacher Full Name',
        'Attendance (%)',
        'Parent Email'
    ]].copy()


def export_struggling_students_to_excel(df_struggling_students, campus):
    if not PRINT_REPORT:
        return True

    if df_struggling_students is None or df_struggling_students.empty:
        print("No struggling students to export.")
        return True

    if campus == "VAU":
        grades_dir = os.path.join(VAU_REPORT_DIRECTORY, 'VAU_StrugglingStudents-')
    elif campus == "MAE":
        grades_dir = os.path.join(MAE_REPORT_DIRECTORY, 'MAE_StrugglingStudents-')
    else:
        print(f"ERROR: Invalid campus name '{campus}'")
        return False

    today = datetime.now()
    date_string = today.strftime("%B %d, %Y")
    output_path = grades_dir + date_string + ".xlsx"

    df_filtered = df_struggling_students[pd.to_numeric(df_struggling_students['Final Grade'], errors='coerce') < GRADES_MIN_BAR]
    if df_filtered.empty:
        print("No struggling students below the grade threshold.")
        return True

    df_filtered = df_filtered.sort_values(
        by=["Teacher Full Name", "Class Code", "Student Full Name", "Final Grade"],
        ascending=[True, True, True, True]
    )

    try:
        df_filtered.to_excel(output_path, sheet_name='Details', index=False)
        SummaryOfStrugglingStudents(output_path)
        print(f"{campus}_StrugglingStudents exported to {output_path}")
    except Exception as exc:
        print(f"ERROR: Failed to export struggling students report '{output_path}': {exc}")
        return False

    return True


def RemindForBSLogin(campus):
    print("Start - RemindForBSLogin")

    df_student_map = load_student_map(campus)
    if df_student_map.empty:
        return pd.DataFrame(columns=[
            "Student Full Name",
            "Last Accessed",
            "Class Code",
            "Teacher Email",
            "Teacher Full Name",
            "Teacher Group",
            "Parent Email"
        ])

    required_cols = {
        'Last Accessed',
        'Student Full Name',
        'Class Code',
        'Teacher Email',
        'Teacher Full Name',
        'Teacher Group',
        'Parent Email'
    }
    missing_cols = [col for col in required_cols if col not in df_student_map.columns]
    if missing_cols:
        warn_once("WARNING", f"Missing columns {missing_cols} in student map; unable to identify login reminders")
        return pd.DataFrame()

    threshold = datetime.now() - timedelta(days=NOT_LOGGED_IN_SINCE)

    def needs_reminder(value):
        parsed = parse_datetime(value, 'Last Accessed')
        if parsed is None:
            return True
        return parsed <= threshold

    targeted_df = df_student_map[df_student_map['Last Accessed'].apply(needs_reminder)].copy()
    columns_to_keep = [
        'Student Full Name',
        'Last Accessed',
        'Class Code',
        'Teacher Email',
        'Teacher Full Name',
        'Teacher Group',
        'Parent Email'
    ]
    return targeted_df[columns_to_keep]


def export_student_reminder_to_excel(df_remind_students, campus):
    if not PRINT_REPORT:
        return True
    if df_remind_students is None or df_remind_students.empty:
        print("No students to remind for Brightspace login.")
        return True

    if campus == "VAU":
        report_prefix = os.path.join(VAU_REPORT_DIRECTORY, 'VAU_RemindForBSLogin-')
    elif campus == "MAE":
        report_prefix = os.path.join(MAE_REPORT_DIRECTORY, 'MAE_RemindForBSLogin-')
    else:
        print(f"ERROR: Invalid campus name '{campus}'")
        return False

    today = datetime.now()
    date_string = today.strftime("%B %d, %Y")
    output_path = report_prefix + date_string + ".xlsx"

    df2 = df_remind_students[[
        "Teacher Full Name",
        "Class Code",
        "Student Full Name",
        "Last Accessed",
        "Parent Email"
    ]].copy()

    df2 = df2.sort_values(
        by=["Teacher Full Name", "Class Code", "Student Full Name", "Last Accessed"],
        ascending=[True, True, True, True]
    )

    try:
        df2.to_excel(output_path, sheet_name='Details', index=False)
        print(f"RemindStudents exported to {output_path}")
    except Exception as exc:
        print(f"ERROR: Failed to export reminder report '{output_path}': {exc}")
        return False

    return True


def export_high_honours_students_to_excel(df_high_honours_students, campus):
    if not PRINT_REPORT:
        return True
    if df_high_honours_students is None or df_high_honours_students.empty:
        print("No high honours students to export.")
        return True

    if campus == "VAU":
        grades_dir = os.path.join(VAU_REPORT_DIRECTORY, 'VAU_HighHonours-')
    elif campus == "MAE":
        grades_dir = os.path.join(MAE_REPORT_DIRECTORY, 'MAE_HighHonours-')
    else:
        print(f"ERROR: Invalid campus name '{campus}'")
        return False

    today = datetime.now()
    date_string = today.strftime("%B %d, %Y")
    output_path = grades_dir + date_string + ".xlsx"

    df2 = df_high_honours_students[[
        "Teacher Full Name",
        "Class Code",
        "Student Full Name",
        "Final Grade",
        "Parent Email"
    ]].copy()

    df2 = df2[pd.to_numeric(df2['Final Grade'], errors='coerce') >= HIGH_HONOURS_MIN_BAR]
    if df2.empty:
        print("No students meet the high honours threshold.")
        return True

    df2 = df2.sort_values(
        by=["Teacher Full Name", "Class Code", "Student Full Name", "Final Grade"],
        ascending=[True, True, True, True]
    )

    try:
        df2.to_excel(output_path, sheet_name='Details', index=False)
        print(f"{campus} - HighHonours exported to {output_path}")
    except Exception as exc:
        print(f"ERROR: Failed to export high honours report '{output_path}': {exc}")
        return False

    return True


def export_students_to_attend_more_to_excel(df_remind_students, campus):
    if not PRINT_REPORT:
        return True
    if df_remind_students is None or df_remind_students.empty:
        print("No students require attendance follow-up.")
        return True

    if campus == "VAU":
        report_dir = os.path.join(VAU_REPORT_DIRECTORY, 'VAU_NeedsToAttendMoreRegularly-')
    elif campus == "MAE":
        report_dir = os.path.join(MAE_REPORT_DIRECTORY, 'MAE_NeedsToAttendMoreRegularly-')
    else:
        print(f"ERROR: Invalid campus name '{campus}'")
        return False

    today = datetime.now()
    date_string = today.strftime("%B %d, %Y")
    output_path = report_dir + date_string + ".xlsx"

    df2 = df_remind_students[[
        "Teacher Full Name",
        "Class Code",
        "Student Full Name",
        "Attendance (%)",
        "Parent Email"
    ]].copy()

    df2 = df2.sort_values(
        by=["Teacher Full Name", "Class Code", "Student Full Name", "Attendance (%)"],
        ascending=[True, True, True, True]
    )

    try:
        df2.to_excel(output_path, sheet_name='Details', index=False)
        print(f"RemindStudents exported to {output_path}")
    except Exception as exc:
        print(f"ERROR: Failed to export attendance reminder '{output_path}': {exc}")
        return False

    return True


def SummaryOfStrugglingStudents(output_path):
    print("Start - SummaryOfStrugglingStudents")

    if not CAMPUS:
        warn_once("WARNING", "Campus not set before generating struggling student summary")
        return pd.DataFrame()

    df_student_map = load_student_map(CAMPUS)
    if df_student_map.empty:
        return pd.DataFrame()

    required_cols = {'Teacher Full Name', 'Final Grade'}
    missing_cols = [col for col in required_cols if col not in df_student_map.columns]
    if missing_cols:
        warn_once("WARNING", f"Missing columns {missing_cols} in student map; unable to build summary")
        return pd.DataFrame()

    df_student_map['Final Grade'] = pd.to_numeric(df_student_map['Final Grade'], errors='coerce').fillna(0)

    try:
        result = df_student_map.groupby('Teacher Full Name').apply(
            calculate_ranges,
            include_groups=False,
        ).reset_index()
    except Exception as exc:
        print(f"ERROR: Failed to aggregate struggling student summary: {exc}")
        return pd.DataFrame()

    result_sorted = result.sort_values(by='Total Students', ascending=False) if 'Total Students' in result.columns else result
    blank_row = pd.DataFrame('', index=[0], columns=result_sorted.columns)
    totals = result_sorted.sum(numeric_only=True)
    totals_df = pd.DataFrame([["TOTAL"] + totals.tolist()], columns=result_sorted.columns)
    result_with_summary = pd.concat([result_sorted, blank_row, totals_df], ignore_index=True)

    print(result_with_summary.to_string(index=False))

    try:
        with pd.ExcelWriter(output_path, engine='openpyxl', mode='a') as writer:
            result_with_summary.to_excel(writer, sheet_name='Summary', index=False)
    except FileNotFoundError:
        print(f"WARNING: Output file not found for summary append: {output_path}")
    except Exception as exc:
        print(f"ERROR: Failed to append summary to '{output_path}': {exc}")

    print("End - SummaryOfStrugglingStudents")
    return result_with_summary


def calculate_ranges(group):



    thresholds = [10, 20, 30, 40, 50]



    column_names = ['1 to 10%', '11 to 20%', '21 to 30%', '31 to 40%', '41 to 50%']







    counts = [0] * len(thresholds)



    total_students = 0  







    for i, t in enumerate(thresholds):



        if i == 0:



            counts[i] = (group['Final Grade'] < t).sum()



        else:



            counts[i] = (group['Final Grade'] < t).sum() - (group['Final Grade'] < thresholds[i-1]).sum()







        total_students += counts[i]



    



    return pd.Series(counts + [total_students], index=column_names + ['Total Students'])










