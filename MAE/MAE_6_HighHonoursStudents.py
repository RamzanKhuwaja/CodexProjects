import pandas as pd
from datetime import datetime
import Common.my_utils as utils

def main():
    utils.set_campus_info("MAE")

    print("Entering MAE HighHonoursStudents")
        
    df_high_honours_students = utils.FindHighHonoursStudents("MAE")

    if df_high_honours_students.empty:
        print("Exiting MAE HighHonoursStudents - no student found!")
        return True
    else:
        utils.export_high_honours_students_to_excel(df_high_honours_students, "MAE")

        print("Exiting MAE HighHonoursStudents")
        return False


if __name__ == "__main__":
    main()
