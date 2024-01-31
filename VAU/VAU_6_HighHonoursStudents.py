import pandas as pd
from datetime import datetime
import Common.my_utils as utils

def main():
    utils.set_campus_info("VAU")

    print("Entering VAU HighHonoursStudents")
        
    df_high_honours_students = utils.FindHighHonoursStudents("VAU")

    if df_high_honours_students.empty:
        print("Exiting VAU HighHonoursStudents - no student found!")
        return True
    else:
        utils.export_high_honours_students_to_excel(df_high_honours_students, "VAU")

        print("Exiting VAU HighHonoursStudents")
        return False


if __name__ == "__main__":
    main()
