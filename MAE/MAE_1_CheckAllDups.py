import sys

import MAE.MAE_11_CheckClassMap as check1
import MAE.MAE_12_DupStudentsInBSViaClassList as check2
import MAE.MAE_13_DupStudentsInBSViaAttendance as check3
import MAE.MAE_14_DupStudentsInBSViaGrades as check4


CHECKS = [
    ("MAE CheckClassMap", check1.main, "MAE ClassMap csv file"),
    ("MAE DupStudentsInBSViaClassList", check2.main, "MAE ClassList directory"),
    ("MAE DupStudentsInBSViaAttendance", check3.main, "MAE Attendance directory"),
    ("MAE DupStudentsInBSViaGrades", check4.main, "MAE Grades directory"),
]


def main() -> bool:
    print("\n===========================================\n")
    print("Entering main - MAECheckAllDups\n")

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

    print("Exiting main - MAECheckAllDups\n")
    print("===========================================\n")
    return overall_success


if __name__ == "__main__":
    sys.exit(0 if main() else 1)
