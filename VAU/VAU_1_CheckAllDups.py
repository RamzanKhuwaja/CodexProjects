import VAU_11_CheckClassMap as check1
import VAU_12_DupStudentsInBSViaClassList as check2
import VAU_13_DupStudentsInBSViaAttendance as check3
import VAU_14_DupStudentsInBSViaGrades as check4

def main():
    print("\n===========================================\n")
    print("Entering main - VAUCheckAllDups\n")

    print("Entering VAU CheckClassMap\n")
    if (check1.main()):
        print("No duplicates found in the VAU ClassMap csv file.\n")
    else:
        print("Duplicates found! Please check VAU ClassMap csv file.\n")

    print("Exiting VAU CheckClassMap\n")

    print("Entering VAU DupStudentsInBSViaClassList\n")

    if (check2.main()):
        print("No duplicates found in the VAU ClassList directory.\n")
    else:
        print("Duplicates found! Please check VAU ClassList directory.\n")

    print("Exiting VAU DupStudentsInBSViaClassList\n")

    print("Entering VAU DupStudentsInBSViaAttendance\n")

    if (check3.main()):
        print("No duplicates found in the VAU Attendance directory.\n")
    else:
        print("Duplicates found! Please check VAU Attendance directory.\n")

    print("Exiting VAU DupStudentsInBSViaAttendance\n")

    print("Entering VAU DupStudentsInBSViaGrades\n")

    if (check4.main()):
        print("No duplicates found in the VAU Grades directory.\n")
    else:
        print("Duplicates found! Please check VAU Grades directory.\n")

    print("Exiting VAU DupStudentsInBSViaGrades\n")

    print("Exiting main - VAUCheckAllDups\n") 
    print("===========================================\n")

    

if __name__ == "__main__":
    main()
