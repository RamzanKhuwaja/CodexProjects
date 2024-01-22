import pandas as pd
import my_mae_utils as utils
from datetime import datetime


FOR_OFFICE_USE_ONLY = True

min_bar = int(90) # Scoring higher than 90%!

# Read STUDENT_MAP_FILE as a df
df_student_map = pd.read_csv(utils.STUDENT_MAP_FILE)

# create a new dataframe from df_student_map for rows where 'Final Grade' column is equal to or higher than min_bar
df_smart_students = df_student_map[df_student_map['Final Grade'] >= min_bar]
# Reset the index of df_smart_students
df_smart_students = df_smart_students.reset_index(drop=True)
df_smart_students = df_smart_students.drop(columns=['Org Defined ID', 'Last Accessed', 'Teacher Email', 'Teacher Group', 'Attendance (%)', 'Parent Email', 'Start Week'])

cols = ['Teacher Full Name'] + ['Class Code'] + ['Student Full Name'] + ['Final Grade']
df_smart_students = df_smart_students[cols]

sorted_df = df_smart_students.sort_values(by=['Teacher Full Name', 'Class Code', 'Final Grade'], ascending=[True, True, False])
sorted_df = sorted_df.reset_index(drop=True)
sorted_df.index = sorted_df.index + 1

#print(sorted_df)

if FOR_OFFICE_USE_ONLY:

    # Get today's date
    today = datetime.now()

    # Format the date as a string
    date_string = today.strftime("%B %d, %Y")  # Format: November 23, 2023

    # Specify the output path
    output_path = utils.MAEPDFdirectory + "\\HighFlyingStudents-" + date_string + ".xlsx"

    sorted_df.to_excel(output_path, index=False)
    print("High flying students exported to " + output_path)


