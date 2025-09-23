import sys

import Common.my_utils as utils

CAMPUS = "VAU"


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

    duplicates_df = duplicates_bucket[0] if duplicates_bucket else None
    return result, duplicates_df


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

    duplicates_df = duplicates_bucket[0] if duplicates_bucket else None
    return result, duplicates_df


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

    duplicates_df = duplicates_bucket[0] if duplicates_bucket else None
    return result, duplicates_df


CHECKS = [
    ("VAU CheckClassMap", run_class_map, "VAU ClassMap csv file"),
    ("VAU DupStudentsInBSViaClassList", run_class_list, "VAU ClassList directory"),
    ("VAU DupStudentsInBSViaAttendance", run_attendance, "VAU Attendance directory"),
    ("VAU DupStudentsInBSViaGrades", run_grades, "VAU Grades directory"),
]


def main() -> bool:
    print("\n===========================================\n")
    print("Entering main - VAUCheckAllDups\n")

    try:
        utils.set_campus_info(CAMPUS)
    except Exception as exc:  # noqa: BLE001
        print(f"WARNING: Unable to set campus info for {CAMPUS} prior to running checks: {exc}")

    overall_success = True
    duplicate_alerts: list[tuple[str, str]] = []
    duplicate_sections: list[tuple[str, object]] = []

    for name, runner, target in CHECKS:
        print(f"Entering {name}\n")
        try:
            result, duplicates_df = runner()
        except Exception as exc:  # noqa: BLE001
            print(f"ERROR: {name} failed: {exc}\n")
            overall_success = False
            continue

        if result:
            print(f"No duplicates found in the {target}.\n")
        else:
            print(f"Duplicates found! Please check {target}.\n")
            duplicate_alerts.append((name, target))
            if duplicates_df is not None:
                duplicate_sections.append((name, duplicates_df))
            overall_success = False

        print(f"Exiting {name}\n")

    if duplicate_alerts:
        required_columns = ['Org Defined ID', 'Student Full Name', 'Last Accessed', 'Class Code']
        details_parts: list[str] = []

        for check_name, duplicates_df in duplicate_sections:
            if hasattr(duplicates_df, 'to_html') and all(col in duplicates_df.columns for col in required_columns):
                trimmed = duplicates_df[required_columns].drop_duplicates().reset_index(drop=True)
                table_html = utils.render_html_table(
                    trimmed,
                    subtitle='Please review and remove extra enrollments.',
                )
                if table_html:
                    details_parts.append(table_html)

        if not details_parts:
            list_items = ''.join(f'<li>{check_name} - {target}</li>' for check_name, target in duplicate_alerts)
            details_parts.append(f'<ul>{list_items}</ul>')

        utils.send_duplicate_notification(
            subject='VAU Brightspace duplicates detected',
            intro_html=(
                'Hello Office, <br><br>'
                'The following Brightspace students appear more than once. '
                'Please remove the duplicates when convenient.'
            ),
            details_html=''.join(details_parts),
            closing_html='Sincerely, <br>Ramzan Khuwaja',
        )

    print("Exiting main - VAUCheckAllDups\n")
    print("===========================================\n")
    return overall_success


if __name__ == "__main__":
    sys.exit(0 if main() else 1)
