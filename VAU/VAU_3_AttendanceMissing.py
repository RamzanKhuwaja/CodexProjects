import Common.my_utils as utils

def main():
    utils.set_campus_info("VAU")

    print("Entering VAU AttendanceMissing")
        
    df_missing_attendance = utils.FindMissingAttendance("VAU")

    if df_missing_attendance.empty:
        print("No missing attendance - Exiting VAU AttendanceMissing")
        return True
    else:
        utils.email_att_missing_to_stakeholders(df_missing_attendance)
        print("ERROR: Found missing attendance - Exiting VAU AttendanceMissing")
        return False

if __name__ == "__main__":
    main()
    
