import sys
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parent.parent
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

import Common.my_utils as utils

CAMPUS = "MAE"
GRADES_DIR = getattr(utils, "MAE_GRADES_DIR")
COLUMN_NAME = "OrgDefinedId"


def main() -> bool:
    try:
        utils.set_campus_info(CAMPUS)
    except Exception as exc:  # noqa: BLE001
        print(f"ERROR: Unable to set campus info for {CAMPUS}: {exc}")
        return False

    print(f"Entering {CAMPUS} DupStudentsInBSViaGrades.")
    try:
        result = utils.FindDupStudentsInBSViaAttendanceGrades(
            GRADES_DIR,
            COLUMN_NAME,
            send_notification=False,
        )
    except Exception as exc:  # noqa: BLE001
        print(f"ERROR: FindDupStudentsInBSViaAttendanceGrades crashed for {GRADES_DIR}: {exc}")
        return False

    if result:
        print(f"Exiting {CAMPUS} DupStudentsInBSViaGrades.")
        return True
    else:
        print(f"WARNING: Exiting {CAMPUS} DupStudentsInBSViaGrades.")
        return False


if __name__ == "__main__":
    sys.exit(0 if main() else 1)
