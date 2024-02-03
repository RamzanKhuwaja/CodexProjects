import Common.my_utils as utils

def main():

    utils.set_campus_info("MAE")

    print("Entering Check to MAE DupStudentsInBSViaGrades.")
    
    if utils.FindDupStudentsInBSViaAttendanceGrades (utils.MAE_GRADES_DIR, "OrgDefinedId"):
        print("Exiting Check on MAE DupStudentsInBSViaGrades.")
        return True
    else:
        print("WARNING: Exiting Check on MAE DupStudentsInBSViaGrades.")
        return False


if __name__ == "__main__":
    main()
