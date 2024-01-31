import pandas as pd
from datetime import datetime
import Common.my_utils as utils

def main():
    utils.set_campus_info("MAE")

    print("Entering MAE StrugglingStudents")
        
    df_struggling_students = FindStrugglingStudents("MAE")

    if df_struggling_students.empty:
        print("No struggling students - Exiting MAE StrugglingStudents")
        return True
    else:
        email_struggling_students_to_stakeholders(df_struggling_students)
        export_struggling_students_to_excel(df_struggling_students, "MAE")

        print("ERROR: Found struggling students - Exiting MAE StrugglingStudents")
        return False

def FindStrugglingStudents(campus):
    print("Start - FindStrugglingStudents")

    if campus == "MAE":
        student_map_file = utils.MAE_STUDENT_MAP_FILE
    elif campus == "MAE":
        student_map_file = utils.MAE_STUDENT_MAP_FILE
    else: 
        print("ERROR: Invalid campus name")
        return False

    df_student_map = pd.read_csv(student_map_file)

    df1 = df_student_map[df_student_map['Final Grade'] < utils.GRADES_MIN_BAR]
    #print(df1)

    df2 = pd.DataFrame(df1, columns=["Org Defined ID", "Student Full Name", "Class Code", "Teacher Email", "Teacher Full Name", "Final Grade"])
    return df2


def email_struggling_students_to_stakeholders(df_struggling_students):
    print("Start - email_to_stakeholders")
    teacher_email = ""

    if utils.SEND_EMAIL:

        for email in df_struggling_students['Teacher Email'].unique():
            df1 = df_struggling_students[df_struggling_students['Teacher Email'] == email]

            teacher = df1["Teacher Full Name"].iloc[0]
            teacher_email = email

            df2 = pd.DataFrame(df1, columns=["Org Defined ID", "Student Full Name", "Class Code", "Final Grade"])

            if utils.TESTING: 
                to = utils.to_email
                cc = ""
            else:
                to = teacher_email
                cc = utils.cc_email

            subject_email="Intervention needed for students below 50%!"
            body_email="Hello " + teacher + ",<br><br>" + \
                "The following students (see Brightspace for details) in your classes have scored, so far, less than 50% as their cumulative marks. These students can potentially dropout of our program if this situation continues.  We should be proactive to prevent this situation. <br><br>" + \
                "Please work with Angela and Surbhi (copied above) to create a plan to increase their scores.<br><br>" + \
                "Many of your students are doing well, so thank you for your effort! I will send a similar report to check progress in the next four weeks.  Thanks. <br><br>" \
                + df2.to_html(index=False) + "<br><br>Ramzan Khuwaja<br><br>" \
                + "P.S. Some cases might be obvious, i.e., late joining, absenteeism, student transfer and grades missing.  Please focus first on students who actually need immediate attention."

            utils.send_email(to, cc, subject_email, body_email)


def export_struggling_students_to_excel(df_struggling_students, campus):
    if utils.PRINT_REPORT:

        if campus == "MAE":
            grades_dir = utils.MAE_REPORT_DIRECTORY + "\\MAE_StrugglingStudents-"
        elif campus == "MAE":
            grades_dir = utils.MAE_REPORT_DIRECTORY + "\\MAE_StrugglingStudents-"
        else: 
            print("ERROR: Invalid campus name")
            return False

        # Get today's date
        today = datetime.now()

        # Format the date as a string
        date_string = today.strftime("%B %d, %Y")  # Format (e.g.,): November 23, 2023

        # Specify the output path
        output_path = grades_dir + date_string + ".xlsx"

        # Example condition: selecting students with a final grade less than 60
        condition = df_struggling_students['Final Grade'] < utils.GRADES_MIN_BAR

        # Apply the condition and then sort
        df_struggling_students = df_struggling_students[condition].sort_values(
            by=["Teacher Full Name", "Class Code", "Student Full Name", "Final Grade"], 
            ascending=[True, True, True, True]
        )


        #df_struggling_students = df_struggling_students[df_struggling_students].sort_values(by=["Teacher Full Name", "Class Code", "Student Full Name", "Final Grade"], ascending=[True, True, True, True])

        df_struggling_students.to_excel(output_path, index=False)
        print("MAE_StrugglingStudents exported to " + output_path)


if __name__ == "__main__":
    main()
    
