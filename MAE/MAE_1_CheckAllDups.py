try:
    import MAE_11_CheckClassMap as check1
    import MAE_12_DupStudentsInBSViaClassList as check2
    import MAE_13_DupStudentsInBSViaAttendance as check3
    import MAE_14_DupStudentsInBSViaGrades as check4
except ImportError as e:
    print(f"Error importing MAE modules: {e}")
    exit(1)

def main():
    print("\n===========================================\n")
    print("Entering main - MAECheckAllDups\n")

    print("Entering MAE CheckClassMap\n")
    if (check1.main()):
        print("No duplicates found in the MAE ClassMap csv file.\n")
    else:
        print("Duplicates found! Please check MAE ClassMap csv file.\n")

    print("Exiting MAE CheckClassMap\n")

    print("Entering MAE DupStudentsInBSViaClassList\n")

    if (check2.main()):
        print("No duplicates found in the MAE ClassList directory.\n")
    else:
        print("Duplicates found! Please check MAE ClassList directory.\n")

    print("Exiting MAE DupStudentsInBSViaClassList\n")

    print("Entering MAE DupStudentsInBSViaAttendance\n")

    if (check3.main()):
        print("No duplicates found in the MAE Attendance directory.\n")
    else:
        print("Duplicates found! Please check MAE Attendance directory.\n")

    print("Exiting MAE DupStudentsInBSViaAttendance\n")

    print("Entering MAE DupStudentsInBSViaGrades\n")

    if (check4.main()):
        print("No duplicates found in the MAE Grades directory.\n")
    else:
        print("Duplicates found! Please check MAE Grades directory.\n")

    print("Exiting MAE DupStudentsInBSViaGrades\n")

    print("Exiting main - MAECheckAllDups\n") 
    print("===========================================\n")

    

if __name__ == "__main__":
    main()
