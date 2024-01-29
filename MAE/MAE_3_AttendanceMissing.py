import Common.my_utils as utils

def main():
    utils.set_campus_info("MAE")

    print("Entering MAE AttendanceMissing")
        
    df_missing_attendance = utils.FindMissingAttendance("MAE")

    if df_missing_attendance.empty:
        print("No missing attendance - Exiting MAE AttendanceMissing")
        return True
    else:
        utils.email_att_missing_to_stakeholders(df_missing_attendance)
        print("ERROR: Found missing attendance - Exiting MAE AttendanceMissing")
        return False

if __name__ == "__main__":
    main()
    
