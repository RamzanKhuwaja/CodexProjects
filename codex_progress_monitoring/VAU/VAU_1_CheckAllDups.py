import re
import sys
from contextlib import redirect_stdout
from io import StringIO
from pathlib import Path
from typing import Any, Iterable

PROJECT_ROOT = Path(__file__).resolve().parent.parent
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

import pandas as pd

import Common.my_utils as utils

CAMPUS = "VAU"

def ensure_dataframe(data):
    """
    Return a pandas DataFrame copy for any tabular input supported by utils.ensure_table_data.
    Handles TableData objects coming back from utils duplicate checks.
    """
    if data is None:
        return None
    if isinstance(data, pd.DataFrame):
        return data.copy()
    if isinstance(data, utils.TableData):
        return pd.DataFrame(data.to_records(), columns=data.columns)
    table = utils.ensure_table_data(data)
    if table is None:
        return None
    return pd.DataFrame(table.to_records(), columns=table.columns)


def derive_export_key(file_path: Path, dataset_type: str) -> tuple[str, str] | None:
    stem = file_path.stem.strip()
    if not stem:
        return None

    clean = re.sub(r"\s*\(\d+\)$", "", stem).strip()
    clean = re.sub(r"\s*copy$", "", clean, flags=re.IGNORECASE).strip()

    if dataset_type in {"Attendance", "Grades"}:
        parts = clean.split("_")
        key_label = clean if len(parts) <= 1 else "_".join(parts[:-1])
        return key_label.lower(), key_label

    if dataset_type == "ClassList":
        marker = " - Spirit of Math Schools"
        lowercase_clean = clean.lower()
        marker_index = lowercase_clean.find(marker.lower())
        if marker_index != -1:
            key_label = clean[: marker_index + len(marker)]
        else:
            key_label = re.sub(r"[\s_-]*(\(\d+\)|\d+)$", "", clean).rstrip(" -_")
        if not key_label:
            key_label = clean
        return key_label.lower(), key_label

    return None


def collect_multiple_exports(directory: str, dataset_label: str, dataset_type: str) -> list[dict[str, Any]]:
    if not directory:
        return []

    directory_path = Path(directory)
    if not directory_path.exists():
        return []

    pattern = "*.html" if dataset_type == "ClassList" else "*.csv"
    grouped: dict[str, dict[str, Any]] = {}

    for file_path in sorted(directory_path.glob(pattern)):
        if not file_path.is_file():
            continue
        export_key = derive_export_key(file_path, dataset_type)
        if export_key is None:
            continue
        key_id, key_label = export_key
        bucket = grouped.setdefault(key_id, {"label": key_label, "files": []})
        bucket["files"].append(file_path.name)

    duplicates = []
    for entry in grouped.values():
        files_sorted = sorted(entry["files"])
        if len(files_sorted) <= 1:
            continue
        if len(files_sorted) == 2:
            sample = ", ".join(files_sorted)
        else:
            sample = f"{files_sorted[0]}, {files_sorted[1]} ... {files_sorted[-1]}"
        duplicates.append(
            {
                "label": entry["label"],
                "count": len(files_sorted),
                "sample": sample,
                "files": files_sorted,
                "dataset": dataset_label,
            }
        )

    return sorted(duplicates, key=lambda item: item["label"])


def execute_with_capture(func, *args, **kwargs) -> tuple[Any, str]:
    buffer = StringIO()
    with redirect_stdout(buffer):
        result = func(*args, **kwargs)
    return result, buffer.getvalue()


def extract_notices(captured: str) -> tuple[list[str], list[str], list[str]]:
    warnings: list[str] = []
    errors: list[str] = []
    notes: list[str] = []

    for raw_line in captured.splitlines():
        line = raw_line.strip()
        if not line:
            continue
        lower = line.lower()
        if lower.startswith("warning"):
            message = line.split(":", 1)[1].strip() if ":" in line else line
            warnings.append(message or line)
        elif lower.startswith("error"):
            message = line.split(":", 1)[1].strip() if ":" in line else line
            errors.append(message or line)
        elif line.startswith("Processed") or "Final master DataFrame" in line:
            notes.append(line)

    return warnings, errors, notes


def format_dataframe_preview(df, *, max_rows: int = 10) -> list[str]:
    df = ensure_dataframe(df)
    if df is None or df.empty:
        return ["(no duplicate details available)"]

    candidate_columns = [
        ["Org Defined ID", "Student Full Name", "Class Code"],
        ["OrgDefinedId", "Student Name", "File Name"],
        ["Org Defined ID", "Student Name", "File Name"],
    ]

    selected_columns: list[str] | None = None
    for columns in candidate_columns:
        if all(col in df.columns for col in columns):
            selected_columns = columns
            break

    if selected_columns is None:
        selected_columns = list(df.columns)[: min(4, len(df.columns))]

    trimmed = df[selected_columns].drop_duplicates()
    preview = trimmed.head(max_rows)
    lines = preview.to_string(index=False).splitlines()

    if len(trimmed) > max_rows:
        remaining = len(trimmed) - max_rows
        lines.append(f"... {remaining} more row(s) not shown")

    return lines


def find_column(df, candidates: Iterable[str]) -> str | None:
    for candidate in candidates:
        if candidate in df.columns:
            return candidate
    return None


def diagnose_duplicates(dataset_type: str, duplicates_df, exports: list[dict[str, Any]]) -> list[str]:
    duplicates_df = ensure_dataframe(duplicates_df)
    if duplicates_df is None or duplicates_df.empty:
        return []

    messages: list[str] = []

    if dataset_type == "ClassList":
        id_col = find_column(duplicates_df, ("Org Defined ID", "OrgDefinedId"))
        class_col = find_column(duplicates_df, ("Class Code",))
        if id_col and class_col:
            unique_classes = duplicates_df.groupby(id_col)[class_col].nunique()
            multi_class_students = unique_classes[unique_classes > 1]
            if not multi_class_students.empty:
                messages.append(
                    f"{len(multi_class_students)} student(s) are enrolled in more than one class code; remove the extra enrollments in Brightspace."
                )
            elif exports:
                messages.append(
                    "Duplicates appear within the same class list export; delete older HTML downloads and rerun."
                )
        elif exports:
            messages.append("Multiple class list exports detected; clear extra HTML files and rerun.")
        return messages

    id_col = find_column(duplicates_df, ("Org Defined ID", "OrgDefinedId"))
    file_col = find_column(duplicates_df, ("File Name",))
    if not id_col or not file_col:
        if exports:
            messages.append("Multiple exports detected; remove older files and rerun.")
        return messages

    temp = duplicates_df.copy()

    def extract_key(name: str) -> str:
        key = derive_export_key(Path(name), dataset_type)
        return key[0] if key else name

    temp["_export_key"] = temp[file_col].astype(str).apply(extract_key)
    key_counts = temp.groupby(id_col)["_export_key"].nunique()
    multi_count = int((key_counts > 1).sum())
    single_count = int((key_counts == 1).sum())

    if multi_count:
        messages.append(
            f"{multi_count} student(s) appear across different class exports; confirm Brightspace doesn't list them in multiple classes."
        )
    if single_count and exports:
        messages.append(
            f"{single_count} student(s) only repeat within one class export; removing older CSV downloads should clear them."
        )
    elif single_count:
        messages.append(
            f"{single_count} student(s) repeat within one class export; review the source files for duplicate rows."
        )

    return messages


def print_section_header(index: int, total: int, title: str) -> None:
    header = f"[{index}/{total}] {title}"
    print()
    print(header)
    print("-" * len(header))


def calculate_duplicate_summary(df) -> str:
    df = ensure_dataframe(df)
    if df is None or df.empty:
        return "no detail rows captured"

    for col in ("Org Defined ID", "OrgDefinedId"):
        if col in df.columns:
            return f"{df[col].dropna().nunique()} student(s)"

    return f"{df.drop_duplicates().shape[0]} record(s)"


def prepare_duplicate_rows(source_label: str, duplicates_df) -> pd.DataFrame:
    duplicates_df = ensure_dataframe(duplicates_df)
    if duplicates_df is None or duplicates_df.empty:
        return pd.DataFrame()

    df = duplicates_df.copy()
    id_col = find_column(df, ("Org Defined ID", "OrgDefinedId"))
    name_col = find_column(df, ("Student Full Name", "Student Name"))
    class_col = find_column(df, ("Class Code",))
    file_col = find_column(df, ("File Name",))

    if id_col is None:
        return pd.DataFrame()

    result = pd.DataFrame({
        "Source": source_label,
        "Student ID": df[id_col].astype(str).fillna(""),
        "Student Name": df[name_col].astype(str).fillna("") if name_col else "",
        "Class Code": df[class_col].astype(str).fillna("") if class_col else "",
        "File Name": df[file_col].astype(str).fillna("") if file_col else "",
    })
    return result.drop_duplicates()


def run_class_map() -> dict[str, Any]:
    file_path = getattr(utils, f"{CAMPUS}_CLASS_MAP_FILE")
    try:
        success, captured = execute_with_capture(utils.check_class_map, file_path)
    except Exception as exc:  # noqa: BLE001
        return {
            "success": False,
            "duplicates": None,
            "warnings": [],
            "errors": [f"check_class_map failed for {file_path}: {exc}"],
            "notes": [],
            "multiple_exports": [],
            "dataset_type": None,
            "dataset_label": None,
        }

    warnings, errors, notes = extract_notices(captured)
    return {
        "success": success,
        "duplicates": None,
        "warnings": warnings,
        "errors": errors,
        "notes": notes,
        "multiple_exports": [],
        "dataset_type": None,
        "dataset_label": None,
    }


def run_class_list() -> dict[str, Any]:
    duplicates_bucket = []
    directory = getattr(utils, f"{CAMPUS}_CLASS_LIST_DIR")
    dataset_type = "ClassList"
    dataset_label = f"{CAMPUS} ClassList"
    multiple_exports = collect_multiple_exports(directory, dataset_label, dataset_type)
    try:
        result, captured = execute_with_capture(
            utils.FindDupStudentsInBSViaClassList,
            directory,
            collect_duplicates=duplicates_bucket,
        )
    except Exception as exc:  # noqa: BLE001
        return {
            "success": False,
            "duplicates": None,
            "warnings": [],
            "errors": [f"FindDupStudentsInBSViaClassList crashed for {directory}: {exc}"],
            "notes": [],
            "multiple_exports": multiple_exports,
            "dataset_type": dataset_type,
            "dataset_label": dataset_label,
        }

    warnings, errors, notes = extract_notices(captured)
    duplicates_df = duplicates_bucket[0] if duplicates_bucket else None
    duplicates_df = ensure_dataframe(duplicates_df)
    if duplicates_df is not None:
        duplicates_df["Source"] = dataset_type
    return {
        "success": result,
        "duplicates": duplicates_df,
        "warnings": warnings,
        "errors": errors,
        "notes": notes,
        "multiple_exports": multiple_exports,
        "dataset_type": dataset_type,
        "dataset_label": dataset_label,
    }


def run_attendance() -> dict[str, Any]:
    duplicates_bucket = []
    directory = getattr(utils, f"{CAMPUS}_ATTENDANCE_DIR")
    dataset_type = "Attendance"
    dataset_label = f"{CAMPUS} Attendance"
    multiple_exports = collect_multiple_exports(directory, dataset_label, dataset_type)
    try:
        result, captured = execute_with_capture(
            utils.FindDupStudentsInBSViaAttendanceGrades,
            directory,
            "Org Defined ID",
            collect_duplicates=duplicates_bucket,
            send_notification=False,
        )
    except Exception as exc:  # noqa: BLE001
        return {
            "success": False,
            "duplicates": None,
            "warnings": [],
            "errors": [f"FindDupStudentsInBSViaAttendanceGrades crashed for {directory}: {exc}"],
            "notes": [],
            "multiple_exports": multiple_exports,
            "dataset_type": dataset_type,
            "dataset_label": dataset_label,
        }

    warnings, errors, notes = extract_notices(captured)
    duplicates_df = duplicates_bucket[0] if duplicates_bucket else None
    duplicates_df = ensure_dataframe(duplicates_df)
    if duplicates_df is not None:
        duplicates_df["Source"] = dataset_type
    return {
        "success": result,
        "duplicates": duplicates_df,
        "warnings": warnings,
        "errors": errors,
        "notes": notes,
        "multiple_exports": multiple_exports,
        "dataset_type": dataset_type,
        "dataset_label": dataset_label,
    }


def run_grades() -> dict[str, Any]:
    duplicates_bucket = []
    directory = getattr(utils, f"{CAMPUS}_GRADES_DIR")
    dataset_type = "Grades"
    dataset_label = f"{CAMPUS} Grades"
    multiple_exports = collect_multiple_exports(directory, dataset_label, dataset_type)
    try:
        result, captured = execute_with_capture(
            utils.FindDupStudentsInBSViaAttendanceGrades,
            directory,
            "OrgDefinedId",
            collect_duplicates=duplicates_bucket,
            send_notification=False,
        )
    except Exception as exc:  # noqa: BLE001
        return {
            "success": False,
            "duplicates": None,
            "warnings": [],
            "errors": [f"FindDupStudentsInBSViaAttendanceGrades crashed for {directory}: {exc}"],
            "notes": [],
            "multiple_exports": multiple_exports,
            "dataset_type": dataset_type,
            "dataset_label": dataset_label,
        }

    warnings, errors, notes = extract_notices(captured)
    duplicates_df = duplicates_bucket[0] if duplicates_bucket else None
    duplicates_df = ensure_dataframe(duplicates_df)
    if duplicates_df is not None:
        duplicates_df["Source"] = dataset_type
    return {
        "success": result,
        "duplicates": duplicates_df,
        "warnings": warnings,
        "errors": errors,
        "notes": notes,
        "multiple_exports": multiple_exports,
        "dataset_type": dataset_type,
        "dataset_label": dataset_label,
    }


CHECKS = [
    ("VAU CheckClassMap", run_class_map, "VAU ClassMap csv file"),
    ("VAU DupStudentsInBSViaClassList", run_class_list, "VAU ClassList directory"),
    ("VAU DupStudentsInBSViaAttendance", run_attendance, "VAU Attendance directory"),
    ("VAU DupStudentsInBSViaGrades", run_grades, "VAU Grades directory"),
]


def main() -> bool:
    print("=" * 56)
    print(f"{CAMPUS} Brightspace Duplicate Checks")
    print("=" * 56)

    try:
        utils.set_campus_info(CAMPUS)
    except Exception as exc:  # noqa: BLE001
        print(f"WARNING: Unable to set campus info for {CAMPUS}: {exc}")

    execution_ok = True
    had_findings = False
    duplicate_alerts: list[tuple[str, str]] = []
    combined_duplicates: list[pd.DataFrame] = []
    diagnosis_notes: list[str] = []

    total_checks = len(CHECKS)

    for index, (name, runner, target) in enumerate(CHECKS, start=1):
        print_section_header(index, total_checks, name)
        try:
            outcome = runner()
        except Exception as exc:  # noqa: BLE001
            print(f"  ERROR: {name} failed unexpectedly: {exc}")
            execution_ok = False
            continue

        dataset_type = outcome.get("dataset_type")
        dataset_label = outcome.get("dataset_label") or target

        for error in outcome.get("errors", []):
            print(f"  ERROR: {error}")
            execution_ok = False

        for warning in outcome.get("warnings", []):
            print(f"  WARNING: {warning}")

        for note in outcome.get("notes", []):
            print(f"  INFO: {note}")

        exports = outcome.get("multiple_exports", [])
        if exports:
            print(f"  WARNING: {len(exports)} class(es) have multiple exports in this folder.")
            preview_limit = 5
            for entry in exports[:preview_limit]:
                print(f"    - {entry['label']} ({entry['count']} files; e.g. {entry['sample']})")
            remaining = len(exports) - preview_limit
            if remaining > 0:
                print(f"    ... {remaining} more class(es) with duplicate exports")
            print("    SUGGESTION: Keep only the newest export per class before rerunning.")

        duplicates_df = outcome.get("duplicates")
        success = outcome.get("success", False)

        if success:
            print(f"  OK: no duplicates found in {target}.")
        else:
            had_findings = True
            duplicate_alerts.append((name, target))

            summary = calculate_duplicate_summary(duplicates_df)
            print(f"  ACTION: duplicates detected in {target} ({summary}).")
            for line in format_dataframe_preview(duplicates_df):
                print(f"    {line}")

            diagnosis = diagnose_duplicates(
                dataset_type or "Unknown",
                duplicates_df,
                outcome.get("multiple_exports", []),
            )
            for message in diagnosis:
                print(f"    NOTE: {message}")
                diagnosis_notes.append(f"{dataset_label}: {message}")

            prepared = prepare_duplicate_rows(dataset_label, duplicates_df)
            if not prepared.empty:
                combined_duplicates.append(prepared)

    if duplicate_alerts:
        details_parts: list[str] = []
        combined_df = pd.concat(combined_duplicates, ignore_index=True).drop_duplicates() if combined_duplicates else pd.DataFrame()

        if not combined_df.empty:
            summary_series = combined_df.groupby("Source")["Student ID"].nunique()
            summary_text = ", ".join(f"{label}: {count}" for label, count in summary_series.items())
            details_parts.append(f"<p><strong>Summary by source:</strong> {summary_text}</p>")

            table_html = utils.render_html_table(
                combined_df,
                subtitle='Combined duplicates across ClassList, Attendance, and Grades.',
            )
            if table_html:
                details_parts.append(table_html)

        if diagnosis_notes:
            list_items = ''.join(f"<li>{note}</li>" for note in diagnosis_notes)
            details_parts.append(f"<p>Suggested actions:</p><ul>{list_items}</ul>")

        if not details_parts:
            list_items = ''.join(f'<li>{check_name} - {target}</li>' for check_name, target in duplicate_alerts)
            details_parts.append(f'<ul>{list_items}</ul>')

        notification_sent = utils.send_duplicate_notification(
            subject=f'{CAMPUS} Brightspace duplicates detected',
            intro_html=(
                'Hello Office, <br><br>'
                'The following Brightspace students appear more than once. '
                'Please remove the duplicates when convenient.'
            ),
            details_html=''.join(details_parts),
            closing_html='Sincerely, <br>Ramzan Khuwaja',
        )
        if not notification_sent:
            print("WARNING: Duplicate notification email was not sent.")

    print("\nAll checks complete.")
    print("=" * 56)
    if had_findings:
        print("Completed with duplicate findings.")
    return execution_ok


if __name__ == "__main__":
    sys.exit(0 if main() else 1)
