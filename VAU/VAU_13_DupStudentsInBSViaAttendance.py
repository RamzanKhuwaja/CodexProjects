import Common.my_utils as utils

def main():

    utils.set_campus_info("VAU")

    print("Entering Check to VAU DupStudentsInBSViaAttendance.")
    
    if utils.FindDupStudentsInBSViaAttendanceGrades (utils.VAU_ATTENDANCE_DIR, "Org Defined ID"):
        print("Exiting Check on VAU DupStudentsInBSViaAttendance.")
        return True
    else:
        print("Exiting Check on VAU DupStudentsInBSViaAttendance.")
        return False


if __name__ == "__main__":
    main()
