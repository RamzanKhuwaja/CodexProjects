from __future__ import annotations

import Common.my_utils as utils

CAMPUS = "MAE"
CLASS_MAP_PATH = utils.MAE_CLASS_MAP_FILE
DATA_FOLDERS = {
    "Attendance": (utils.MAE_ATTENDANCE_DIR, ".csv"),
    "ClassList": (utils.MAE_CLASS_LIST_DIR, ".html"),
    "Grades": (utils.MAE_GRADES_DIR, ".csv"),
}


def main() -> bool:
    print("\n===========================================\n")
    print("Entering main - MAE_CheckDownloadedFiles\n")

    success = utils.check_downloaded_files(CAMPUS, CLASS_MAP_PATH, DATA_FOLDERS)

    if success:
        print("All downloaded files are present and match the expected formats.\n")

    print("Exiting main - MAE_CheckDownloadedFiles\n")
    print("===========================================\n")
    return success


if __name__ == "__main__":
    raise SystemExit(0 if main() else 1)
