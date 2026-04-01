import sys

import Common.my_utils as utils

CAMPUS = "VAU"


def main() -> bool:
    print(f"Entering {CAMPUS} AttendanceMissing")
    try:
        utils.set_campus_info(CAMPUS)
    except Exception as exc:  # noqa: BLE001
        print(f"ERROR: Unable to set campus info for {CAMPUS}: {exc}")
        return False

    try:
        df_missing_attendance = utils.FindMissingAttendance(CAMPUS)
    except Exception as exc:  # noqa: BLE001
        print(f"ERROR: FindMissingAttendance failed for {CAMPUS}: {exc}")
        return False

    if df_missing_attendance is None or df_missing_attendance.empty:
        print(f"No missing attendance - Exiting {CAMPUS} AttendanceMissing")
        return True

    try:
        utils.email_att_missing_to_stakeholders(df_missing_attendance)
    except Exception as exc:  # noqa: BLE001
        print(f"ERROR: Failed to email missing attendance stakeholders: {exc}")
        return False

    print(f"WARNING: Found missing attendance - Exiting {CAMPUS} AttendanceMissing")
    return True


if __name__ == "__main__":
    sys.exit(0 if main() else 1)
