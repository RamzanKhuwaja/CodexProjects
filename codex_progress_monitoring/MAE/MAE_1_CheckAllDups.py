import sys
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parent.parent
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

import Common.my_utils as utils

CAMPUS = "MAE"
ACTIONABLE_EMAIL_CHECKS = {"MAE DupStudentsInBSViaClassList"}


def classify_status(success: bool, duplicates_data) -> str:
    if success:
        return "clean"
    if duplicates_data:
        return "duplicates"
    return "invalid"


def render_duplicate_details(check_name: str, duplicates_data) -> list[str]:
    preferred_columns = [
        "Duplicate Column",
        "Row Number",
        "Org Defined ID",
        "OrgDefinedId",
        "Student Full Name",
        "Student Name",
        "Last Accessed",
        "Class Code",
        "Attendance",
        "Grades",
        "ClassList",
        "File Name",
    ]
    detail_parts: list[str] = []
    tables = duplicates_data if isinstance(duplicates_data, list) else [duplicates_data]

    for index, item in enumerate(tables, start=1):
        table = utils.ensure_table_data(item)
        if table is None or table.is_empty:
            continue

        display_columns = [column for column in preferred_columns if column in table.columns]
        if not display_columns:
            display_columns = list(table.columns)

        trimmed = table.select(display_columns).drop_duplicates(display_columns)
        title = check_name
        if "Duplicate Column" in trimmed.columns and trimmed.rows:
            duplicate_column = str(trimmed.rows[0].get("Duplicate Column", "")).strip()
            if duplicate_column:
                title = f"{check_name} - {duplicate_column}"
        elif len(tables) > 1:
            title = f"{check_name} - Set {index}"

        table_html = utils.render_html_table(
            trimmed,
            title=title,
            subtitle="Please review and remove extra enrollments.",
        )
        if table_html:
            detail_parts.append(table_html)

    return detail_parts


def summarize_class_list_duplicates(duplicates_data):
    source_tables = duplicates_data if isinstance(duplicates_data, list) else [duplicates_data]
    required_columns = ["Org Defined ID", "Student Full Name", "Class Code"]
    merged_rows: list[dict[str, object]] = []

    for item in source_tables:
        table = utils.ensure_table_data(item)
        if table is None or table.is_empty:
            continue
        if not all(column in table.columns for column in required_columns):
            continue
        merged_rows.extend(table.select(required_columns).rows)

    if not merged_rows:
        return None, {"total": 0, "same_class": 0, "multi_class": 0}

    grouped: dict[tuple[str, str], dict[str, object]] = {}
    for row in merged_rows:
        student_id = str(row.get("Org Defined ID", "")).strip()
        student_name = str(row.get("Student Full Name", "")).strip()
        class_code = str(row.get("Class Code", "")).strip()
        if not student_id and not student_name:
            continue

        key = (student_id, student_name)
        entry = grouped.setdefault(
            key,
            {
                "Student ID": student_id,
                "Student Name": student_name,
                "Class Codes": [],
                "Row Count": 0,
            },
        )
        entry["Row Count"] = int(entry["Row Count"]) + 1
        if class_code and class_code not in entry["Class Codes"]:
            entry["Class Codes"].append(class_code)

    summary_rows: list[dict[str, object]] = []
    same_class = 0
    multi_class = 0
    for entry in grouped.values():
        class_codes = list(entry["Class Codes"])
        row_count = int(entry["Row Count"])
        if len(class_codes) > 1:
            issue = "Appears in multiple classes"
            multi_class += 1
        else:
            issue = "Listed twice in the same class"
            same_class += 1

        summary_rows.append(
            {
                "Student ID": entry["Student ID"],
                "Student Name": entry["Student Name"],
                "Issue": issue,
                "Class Codes": ", ".join(class_codes),
            }
        )

    summary_table = utils.TableData(
        ["Student ID", "Student Name", "Issue", "Class Codes"],
        summary_rows,
    ).sorted(["Student Name", "Student ID"])
    counts = {
        "total": len(summary_rows),
        "same_class": same_class,
        "multi_class": multi_class,
    }
    return summary_table, counts


def build_actionable_email(check_name: str, duplicates_data):
    if check_name != "MAE DupStudentsInBSViaClassList":
        return None, None

    summary_table, counts = summarize_class_list_duplicates(duplicates_data)
    if summary_table is None or summary_table.is_empty:
        return None, None

    table_html = utils.render_html_table(
        summary_table,
        title="Students To Review In Brightspace",
        subtitle="Remove the extra Brightspace enrollment for each student listed below.",
    )
    intro_html = (
        "Hello Office,<br><br>"
        "Please review the Brightspace enrollments below and remove the extra enrollment for each student.<br><br>"
        f"Summary: {counts['total']} students need review. "
        f"{counts['same_class']} are listed twice in the same class roster. "
        f"{counts['multi_class']} appear in multiple classes."
    )
    return intro_html, table_html


def run_class_map():
    print(f"Entering Check on {CAMPUS}_CLASS_MAP_FILE.")
    file_path = getattr(utils, f"{CAMPUS}_CLASS_MAP_FILE")
    duplicates_bucket = []
    try:
        success = utils.check_class_map(file_path, collect_duplicates=duplicates_bucket)
    except Exception as exc:  # noqa: BLE001
        print(f"ERROR: check_class_map failed for {file_path}: {exc}")
        return "invalid", None

    status = classify_status(success, duplicates_bucket)
    if status == "clean":
        print(f"Exiting Check on {CAMPUS}_CLASS_MAP_FILE.")
    elif status == "duplicates":
        print(f"WARNING: Exiting Check on {CAMPUS}_CLASS_MAP_FILE.")
    else:
        print(f"ERROR: Exiting Check on {CAMPUS}_CLASS_MAP_FILE.")
    return status, duplicates_bucket or None


def run_class_list():
    print(f"Entering Check to FindDupStudentsIn {CAMPUS} BSViaClassList.")
    duplicates_bucket = []
    directory = getattr(utils, f"{CAMPUS}_CLASS_LIST_DIR")
    try:
        result = utils.FindDupStudentsInBSViaClassList(directory, collect_duplicates=duplicates_bucket)
    except Exception as exc:  # noqa: BLE001
        print(f"ERROR: FindDupStudentsInBSViaClassList crashed for {directory}: {exc}")
        return "invalid", None

    status = classify_status(result, duplicates_bucket)
    if status == "clean":
        print(f"Exiting Check on FindDupStudentsIn {CAMPUS} BSViaClassList.")
    elif status == "duplicates":
        print(f"WARNING: Exiting Check on FindDupStudentsIn {CAMPUS} BSViaClassList.")
    else:
        print(f"ERROR: Exiting Check on FindDupStudentsIn {CAMPUS} BSViaClassList.")

    return status, duplicates_bucket or None


def run_attendance():
    print(f"Entering {CAMPUS} DupStudentsInBSViaAttendance.")
    duplicates_bucket = []
    directory = getattr(utils, f"{CAMPUS}_ATTENDANCE_DIR")
    try:
        result = utils.FindDupStudentsInBSViaAttendanceGrades(
            directory,
            "Org Defined ID",
            collect_duplicates=duplicates_bucket,
            send_notification=False,
        )
    except Exception as exc:  # noqa: BLE001
        print(f"ERROR: FindDupStudentsInBSViaAttendanceGrades crashed for {directory}: {exc}")
        return "invalid", None

    status = classify_status(result, duplicates_bucket)
    if status == "clean":
        print(f"Exiting {CAMPUS} DupStudentsInBSViaAttendance.")
    elif status == "duplicates":
        print(f"WARNING: Exiting {CAMPUS} DupStudentsInBSViaAttendance.")
    else:
        print(f"ERROR: Exiting {CAMPUS} DupStudentsInBSViaAttendance.")

    return status, duplicates_bucket or None


def run_grades():
    print(f"Entering {CAMPUS} DupStudentsInBSViaGrades.")
    duplicates_bucket = []
    directory = getattr(utils, f"{CAMPUS}_GRADES_DIR")
    try:
        result = utils.FindDupStudentsInBSViaAttendanceGrades(
            directory,
            "OrgDefinedId",
            collect_duplicates=duplicates_bucket,
            send_notification=False,
        )
    except Exception as exc:  # noqa: BLE001
        print(f"ERROR: FindDupStudentsInBSViaAttendanceGrades crashed for {directory}: {exc}")
        return "invalid", None

    status = classify_status(result, duplicates_bucket)
    if status == "clean":
        print(f"Exiting {CAMPUS} DupStudentsInBSViaGrades.")
    elif status == "duplicates":
        print(f"WARNING: Exiting {CAMPUS} DupStudentsInBSViaGrades.")
    else:
        print(f"ERROR: Exiting {CAMPUS} DupStudentsInBSViaGrades.")

    return status, duplicates_bucket or None


CHECKS = [
    ("MAE CheckClassMap", run_class_map, "MAE ClassMap csv file"),
    ("MAE DupStudentsInBSViaClassList", run_class_list, "MAE ClassList directory"),
    ("MAE DupStudentsInBSViaAttendance", run_attendance, "MAE Attendance directory"),
    ("MAE DupStudentsInBSViaGrades", run_grades, "MAE Grades directory"),
]


def main() -> bool:
    print("\n===========================================\n")
    print("Entering main - MAECheckAllDups\n")

    try:
        utils.set_campus_info(CAMPUS)
    except Exception as exc:  # noqa: BLE001
        print(f"WARNING: Unable to set campus info for {CAMPUS} prior to running checks: {exc}")

    execution_ok = True
    had_findings = False
    duplicate_alerts: list[tuple[str, str]] = []
    duplicate_sections: list[tuple[str, object]] = []

    for name, runner, target in CHECKS:
        print(f"Entering {name}\n")
        try:
            status, duplicates_data = runner()
        except Exception as exc:  # noqa: BLE001
            print(f"ERROR: {name} failed: {exc}\n")
            execution_ok = False
            continue

        if status == "clean":
            print(f"No duplicates found in the {target}.\n")
        elif status == "duplicates":
            print(f"Duplicates found! Please check {target}.\n")
            duplicate_alerts.append((name, target))
            if duplicates_data is not None:
                duplicate_sections.append((name, duplicates_data))
            had_findings = True
        else:
            print(
                f"Check could not be verified for the {target}. "
                "Please review the input files and rerun.\n"
            )
            execution_ok = False

        print(f"Exiting {name}\n")

    if duplicate_alerts:
        actionable_intro = None
        actionable_details: list[str] = []

        for check_name, duplicates_data in duplicate_sections:
            if check_name not in ACTIONABLE_EMAIL_CHECKS:
                continue
            intro_html, details_html = build_actionable_email(check_name, duplicates_data)
            if intro_html and actionable_intro is None:
                actionable_intro = intro_html
            if details_html:
                actionable_details.append(details_html)

        if actionable_details:
            notification_sent = utils.send_duplicate_notification(
                subject='MAE Brightspace enrollments to review',
                intro_html=actionable_intro or "",
                details_html=''.join(actionable_details),
                closing_html='Sincerely, <br>Ramzan Khuwaja',
            )
            if not notification_sent:
                print("WARNING: Duplicate notification email was not sent.")
        else:
            print(
                "INFO: Duplicate findings were detected, but none were suitable "
                "for an office action email."
            )

    print("Exiting main - MAECheckAllDups\n")
    print("===========================================\n")
    if had_findings:
        print("Completed with duplicate findings.\n")
    return execution_ok


if __name__ == "__main__":
    sys.exit(0 if main() else 1)
