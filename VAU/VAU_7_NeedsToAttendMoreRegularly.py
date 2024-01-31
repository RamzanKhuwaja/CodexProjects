
import pandas as pd
from datetime import datetime
import Common.my_utils as utils

def main():
    utils.set_campus_info("VAU")

    print("Entering VAU NeedsToAttendMoreRegularly")
        
    df_not_regular_students = utils.FindNeedsToAttendMoreRegularly("VAU")

    if df_not_regular_students.empty:
        print("Exiting VAU NeedsToAttendMoreRegularly - no student found!")
        return True
    else:
        utils.export_students_to_attend_more_to_excel(df_not_regular_students, "VAU")

        print("Exiting VAU NeedsToAttendMoreRegularly")
        return False


if __name__ == "__main__":
    main()




