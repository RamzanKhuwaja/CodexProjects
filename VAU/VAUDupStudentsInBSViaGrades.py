import Common.my_utils as utils

def main():

    utils.set_campus_info("VAU")

    print("Entering Check to VAU DupStudentsInBSViaGrades.")
    
    if utils.FindDupStudentsInBSViaAttendanceGrades (utils.VAU_GRADES_DIR, "OrgDefinedId"):
        print("Exiting Check on VAU DupStudentsInBSViaGrades.")
        return True
    else:
        print("WARNING: Exiting Check on VAU DupStudentsInBSViaGrades.")
        return False


if __name__ == "__main__":
    main()
