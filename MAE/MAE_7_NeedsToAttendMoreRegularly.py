import sys

import Common.my_utils as utils

CAMPUS = "MAE"


def main() -> bool:
    print(f"Entering {CAMPUS} NeedsToAttendMoreRegularly")
    try:
        utils.set_campus_info(CAMPUS)
    except Exception as exc:  # noqa: BLE001
        print(f"ERROR: Unable to set campus info for {CAMPUS}: {exc}")
        return False

    try:
        df_needs_more = utils.FindNeedsToAttendMoreRegularly(CAMPUS)
    except Exception as exc:  # noqa: BLE001
        print(f"ERROR: FindNeedsToAttendMoreRegularly failed for {CAMPUS}: {exc}")
        return False

    if df_needs_more is None or df_needs_more.empty:
        print(f"No attendance concerns - Exiting {CAMPUS} NeedsToAttendMoreRegularly")
        return True

    export_ok = utils.export_students_to_attend_more_to_excel(df_needs_more, CAMPUS)
    if not export_ok:
        print(f"ERROR: Unable to export attendance report for {CAMPUS}.")
        return False

    print(f"WARNING: Found students needing more regular attendance - Exiting {CAMPUS} NeedsToAttendMoreRegularly")
    return False


if __name__ == "__main__":
    sys.exit(0 if main() else 1)
