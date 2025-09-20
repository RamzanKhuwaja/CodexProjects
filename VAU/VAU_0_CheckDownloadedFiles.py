from __future__ import annotations

import Common.my_utils as utils

CAMPUS = "VAU"
CLASS_MAP_PATH = utils.VAU_CLASS_MAP_FILE
DATA_FOLDERS = {
    "Attendance": (utils.VAU_ATTENDANCE_DIR, ".csv"),
    "ClassList": (utils.VAU_CLASS_LIST_DIR, ".html"),
    "Grades": (utils.VAU_GRADES_DIR, ".csv"),
}


def main() -> bool:
    print("\n===========================================\n")
    print("Entering main - VAU_CheckDownloadedFiles\n")

    success = utils.check_downloaded_files(CAMPUS, CLASS_MAP_PATH, DATA_FOLDERS)

    if success:
        print("All downloaded files are present and match the expected formats.\n")

    print("Exiting main - VAU_CheckDownloadedFiles\n")
    print("===========================================\n")
    return success


if __name__ == "__main__":
    raise SystemExit(0 if main() else 1)
