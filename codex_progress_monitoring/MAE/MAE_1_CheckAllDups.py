import sys
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parent.parent
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

import Common.my_utils as utils

CAMPUS = "MAE"


def classify_status(success: bool, duplicates_data) -> str:
    if success:
        return "clean"
    if duplicates_data:
        return "duplicates"
    return "invalid"


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
    actionable_duplicates = None

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
            if name == f"{CAMPUS} DupStudentsInBSViaClassList":
                actionable_duplicates = duplicates_data
            had_findings = True
        else:
            print(
                f"Check could not be verified for the {target}. "
                "Please review the input files and rerun.\n"
            )
            execution_ok = False

        print(f"Exiting {name}\n")

    if duplicate_alerts:
        subject, intro_html, details_html = utils.build_office_duplicate_email(CAMPUS, actionable_duplicates)
        if details_html:
            notification_sent = utils.send_duplicate_notification(
                subject=subject or 'MAE Brightspace enrollments to review',
                intro_html=intro_html or "",
                details_html=details_html,
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
