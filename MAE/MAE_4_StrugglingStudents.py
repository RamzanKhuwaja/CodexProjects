import pandas as pd
from datetime import datetime
import Common.my_utils as utils

def main():
    utils.set_campus_info("MAE")

    print("Entering MAE StrugglingStudents")
        
    df_struggling_students = utils.FindStrugglingStudents("MAE")

    if df_struggling_students.empty:
        print("No struggling students - Exiting MAE StrugglingStudents")
        return True
    else:
        email_struggling_students_to_stakeholders(df_struggling_students)
        utils.export_struggling_students_to_excel(df_struggling_students, "MAE")

        print("ERROR: Found struggling students - Exiting MAE StrugglingStudents")
        return False

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


if __name__ == "__main__":
    main()
    
