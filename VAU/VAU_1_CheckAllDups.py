import VAU_11_CheckClassMap as check1
import VAU_12_DupStudentsInBSViaClassList as check2
import VAU_13_DupStudentsInBSViaAttendance as check3
import VAU_14_DupStudentsInBSViaGrades as check4

def main():
    print("\n===========================================\n")
    print("Entering main - VAUCheckAllDups\n")

    checks = [
        ("VAU CheckClassMap", check1.main, "VAU ClassMap csv file"),
        ("VAU DupStudentsInBSViaClassList", check2.main, "VAU ClassList directory"),
        ("VAU DupStudentsInBSViaAttendance", check3.main, "VAU Attendance directory"),
        ("VAU DupStudentsInBSViaGrades", check4.main, "VAU Grades directory")
    ]

    for check_name, check_function, check_target in checks:
        print(f"Entering {check_name}\n")
        try:
            if check_function():
                print(f"No duplicates found in the {check_target}.\n")
            else:
                print(f"Duplicates found! Please check {check_target}.\n")
        except Exception as e:
            print(f"An error occurred in {check_name}: {e}\n")
        print(f"Exiting {check_name}\n")

    print("Exiting main - VAUCheckAllDups\n") 
    print("===========================================\n")

if __name__ == "__main__":
    main()
