import sys

import Common.my_utils as utils

CAMPUS = "MAE"
ATTENDANCE_DIR = getattr(utils, "MAE_ATTENDANCE_DIR")
COLUMN_NAME = "Org Defined ID"


def main() -> bool:
    try:
        utils.set_campus_info(CAMPUS)
    except Exception as exc:  # noqa: BLE001
        print(f"ERROR: Unable to set campus info for {CAMPUS}: {exc}")
        return False

    print(f"Entering {CAMPUS} DupStudentsInBSViaAttendance.")
    try:
        result = utils.FindDupStudentsInBSViaAttendanceGrades(ATTENDANCE_DIR, COLUMN_NAME)
    except Exception as exc:  # noqa: BLE001
        print(f"ERROR: FindDupStudentsInBSViaAttendanceGrades crashed for {ATTENDANCE_DIR}: {exc}")
        return False

    if result:
        print(f"Exiting {CAMPUS} DupStudentsInBSViaAttendance.")
    else:
        print(f"WARNING: Exiting {CAMPUS} DupStudentsInBSViaAttendance.")
    return result


if __name__ == "__main__":
    sys.exit(0 if main() else 1)
