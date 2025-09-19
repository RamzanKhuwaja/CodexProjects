import sys

import VAU.VAU_11_CheckClassMap as check1
import VAU.VAU_12_DupStudentsInBSViaClassList as check2
import VAU.VAU_13_DupStudentsInBSViaAttendance as check3
import VAU.VAU_14_DupStudentsInBSViaGrades as check4


CHECKS = [
    ("VAU CheckClassMap", check1.main, "VAU ClassMap csv file"),
    ("VAU DupStudentsInBSViaClassList", check2.main, "VAU ClassList directory"),
    ("VAU DupStudentsInBSViaAttendance", check3.main, "VAU Attendance directory"),
    ("VAU DupStudentsInBSViaGrades", check4.main, "VAU Grades directory"),
]


def main() -> bool:
    print("\n===========================================\n")
    print("Entering main - VAUCheckAllDups\n")

    overall_success = True

    for name, func, target in CHECKS:
        print(f"Entering {name}\n")
        try:
            result = func()
        except Exception as exc:  # noqa: BLE001
            print(f"ERROR: {name} failed: {exc}\n")
            overall_success = False
        else:
            if result:
                print(f"No duplicates found in the {target}.\n")
            else:
                print(f"Duplicates found! Please check {target}.\n")
                overall_success = False
        print(f"Exiting {name}\n")

    print("Exiting main - VAUCheckAllDups\n")
    print("===========================================\n")
    return overall_success


if __name__ == "__main__":
    sys.exit(0 if main() else 1)
