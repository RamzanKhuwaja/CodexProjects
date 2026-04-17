import sys
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parent.parent
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

import Common.my_utils as utils

CAMPUS = "VAU"


def main() -> bool:
    print(f"Entering {CAMPUS} HighHonoursStudents")
    try:
        utils.set_campus_info(CAMPUS)
    except Exception as exc:  # noqa: BLE001
        print(f"ERROR: Unable to set campus info for {CAMPUS}: {exc}")
        return False

    try:
        df_high = utils.FindHighHonoursStudents(CAMPUS)
    except Exception as exc:  # noqa: BLE001
        print(f"ERROR: FindHighHonoursStudents failed for {CAMPUS}: {exc}")
        return False

    if df_high is None or df_high.empty:
        print(f"No high honours students - Exiting {CAMPUS} HighHonoursStudents")
        return True

    export_ok = utils.export_high_honours_students_to_excel(df_high, CAMPUS)
    if not export_ok:
        print(f"ERROR: Unable to export high honours report for {CAMPUS}.")
        return False

    print(f"SUCCESS: Exported high honours report for {CAMPUS}")
    return True


if __name__ == "__main__":
    sys.exit(0 if main() else 1)
