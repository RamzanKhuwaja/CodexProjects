
import sys

import Common.my_utils as utils

CAMPUS = "MAE"


def run_class_map():
    print(f"Entering Check on {CAMPUS}_CLASS_MAP_FILE.")
    file_path = getattr(utils, f"{CAMPUS}_CLASS_MAP_FILE")
    try:
        success = utils.check_class_map(file_path)
    except Exception as exc:  # noqa: BLE001
        print(f"ERROR: check_class_map failed for {file_path}: {exc}")
        return False, None

    if success:
        print(f"Exiting Check on {CAMPUS}_CLASS_MAP_FILE.")
    else:
        print(f"ERROR: Exiting Check on {CAMPUS}_CLASS_MAP_FILE.")
    return success, None


def run_class_list():
    print(f"Entering Check to FindDupStudentsIn {CAMPUS} BSViaClassList.")
    duplicates_bucket = []
    directory = getattr(utils, f"{CAMPUS}_CLASS_LIST_DIR")
    try:
        result = utils.FindDupStudentsInBSViaClassList(directory, collect_duplicates=duplicates_bucket)
    except Exception as exc:  # noqa: BLE001
        print(f"ERROR: FindDupStudentsInBSViaClassList crashed for {directory}: {exc}")
        return False, None

    if result:
        print(f"Exiting Check on FindDupStudentsIn {CAMPUS} BSViaClassList.")
    else:
        print(f"WARNING: Exiting Check on FindDupStudentsIn {CAMPUS} BSViaClassList.")

    duplicates_table = duplicates_bucket[0] if duplicates_bucket else None
    return result, duplicates_table


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
        return False, None

    if result:
        print(f"Exiting {CAMPUS} DupStudentsInBSViaAttendance.")
    else:
        print(f"WARNING: Exiting {CAMPUS} DupStudentsInBSViaAttendance.")

    duplicates_table = duplicates_bucket[0] if duplicates_bucket else None
    return result, duplicates_table


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
        return False, None

    if result:
        print(f"Exiting {CAMPUS} DupStudentsInBSViaGrades.")
    else:
        print(f"WARNING: Exiting {CAMPUS} DupStudentsInBSViaGrades.")

    duplicates_table = duplicates_bucket[0] if duplicates_bucket else None
    return result, duplicates_table


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
            result, duplicates_table = runner()
        except Exception as exc:  # noqa: BLE001
            print(f"ERROR: {name} failed: {exc}\n")
            execution_ok = False
            continue

        if result:
            print(f"No duplicates found in the {target}.\n")
        else:
            print(f"Duplicates found! Please check {target}.\n")
            duplicate_alerts.append((name, target))
            if duplicates_table is not None:
                duplicate_sections.append((name, duplicates_table))
            had_findings = True

        print(f"Exiting {name}\n")

    if duplicate_alerts:
        required_columns = ['Org Defined ID', 'Student Full Name', 'Last Accessed', 'Class Code']
        details_parts: list[str] = []

        for check_name, duplicates_data in duplicate_sections:
            table = utils.ensure_table_data(duplicates_data, required_columns)
            if table is None or table.is_empty:
                continue
            if not all(col in table.columns for col in required_columns):
                continue
            trimmed = table.select(required_columns).drop_duplicates(required_columns)
            table_html = utils.render_html_table(
                trimmed,
                subtitle='Please review and remove extra enrollments.',
            )
            if table_html:
                details_parts.append(table_html)

        if not details_parts:
            list_items = ''.join(f'<li>{check_name} - {target}</li>' for check_name, target in duplicate_alerts)
            details_parts.append(f'<ul>{list_items}</ul>')

        notification_sent = utils.send_duplicate_notification(
            subject='MAE Brightspace duplicates detected',
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

    print("Exiting main - MAECheckAllDups\n")
    print("===========================================\n")
    if had_findings:
        print("Completed with duplicate findings.\n")
    return execution_ok


if __name__ == "__main__":
    sys.exit(0 if main() else 1)
