import pandas as pd
import Common.my_utils as utils
import Common.CheckClassMap as check1
import Common.DupStudentsInBSViaClassList as check2
import Common.DupStudentsInBSViaAttendance as check3
import Common.DupStudentsInBSViaGrades as check4

def main():
    # Path where ClassMap file is stored
    print("\n===========================================\n")
    print("Entering main - MAE-CheckForDups.py\n")

    print("Entering MAE_CheckClassMap.py\n")
    if (check1.main()):
        print("No duplicates found in the MAE ClassMap csv file.\n")
    else:
        print("Duplicates found! Please check ClassMap csv file.\n")

    print("Exiting MAE_CheckClassMap.p\n")

    print("Entering MAE_DupStudentsInBSViaClassList.py\n")

    if (check2.main()):
        print("No duplicates found in the ClassList directory.\n")
    else:
        print("Duplicates found! Please check ClassList directory.\n")

    print("Exiting MAE_DupStudentsInBSViaClassList.py\n")

    print("Entering MAE_DupStudentsInBSViaAttendance.py\n")

    if (check3.main()):
        print("No duplicates found in the Attendance directory.\n")
    else:
        print("Duplicates found! Please check Attendance directory.\n")

    print("Exiting MAE_DupStudentsInBSViaAttendance.py\n")

    print("Entering MAE_DupStudentsInBSViaGrades.py\n")

    if (check4.main()):
        print("No duplicates found in the Grades directory.\n")
    else:
        print("Duplicates found! Please check Grades directory.\n")

    print("Exiting MAE_DupStudentsInBSViaGrades.py\n")

    print("Exiting main - MAE-CheckForDups\n") 
    print("===========================================\n")

    

if __name__ == "__main__":
    main()
