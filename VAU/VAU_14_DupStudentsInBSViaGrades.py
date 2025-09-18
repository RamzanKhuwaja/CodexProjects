import sys

import Common.my_utils as utils

CAMPUS = "VAU"
GRADES_DIR = getattr(utils, "VAU_GRADES_DIR")
COLUMN_NAME = "OrgDefinedId"


def main() -> bool:
    try:
        utils.set_campus_info(CAMPUS)
    except Exception as exc:  # noqa: BLE001
        print(f"ERROR: Unable to set campus info for {CAMPUS}: {exc}")
        return False

    print(f"Entering {CAMPUS} DupStudentsInBSViaGrades.")
    try:
        result = utils.FindDupStudentsInBSViaAttendanceGrades(GRADES_DIR, COLUMN_NAME)
    except Exception as exc:  # noqa: BLE001
        print(f"ERROR: FindDupStudentsInBSViaAttendanceGrades crashed for {GRADES_DIR}: {exc}")
        return False

    if result:
        print(f"Exiting {CAMPUS} DupStudentsInBSViaGrades.")
    else:
        print(f"WARNING: Exiting {CAMPUS} DupStudentsInBSViaGrades.")
    return result


if __name__ == "__main__":
    sys.exit(0 if main() else 1)
