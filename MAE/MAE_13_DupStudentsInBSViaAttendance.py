
import Common.my_utils as utils

def main():

    utils.set_campus_info("MAE")

    print("Entering Check to MAE DupStudentsInBSViaAttendance.")
    
    if utils.FindDupStudentsInBSViaAttendanceGrades (utils.MAE_ATTENDANCE_DIR, "Org Defined ID"):
        print("Exiting Check on MAE DupStudentsInBSViaAttendance.")
        return True
    else:
        print("WARNING: Exiting Check on MAE DupStudentsInBSViaAttendance.")
        return False


if __name__ == "__main__":
    main()
