import pandas as pd
from datetime import datetime
import Common.my_utils as utils

def email_to_remind_restudents(df_remind_students):
    print("Start - email_to_remind_students")
    teacher_email = ""

    if utils.SEND_EMAIL:

        for email in df_remind_students['Teacher Email'].unique():
            df1 = df_remind_students[df_remind_students['Teacher Email'] == email]

            teacher = df1["Teacher Full Name"].iloc[0]
            teacher_email = email

            df2 = pd.DataFrame(df1, columns=["Class Code", "Student Full Name", "Last Accessed", "Parent Email"])

            if utils.TESTING: 
                to = utils.to_email
                cc = ""
            else:
                to = teacher_email
                cc = utils.cc_email

            subject_email="Please remind these students to login to BS regularly"
            body_email="Hello " + teacher + ",<br><br>" \
                "The following students have not logged in for at least 2 weeks to Brightspace. The successful student uses this resource regularly.  Please remind these students to login every week and use its content.<br>" \
                "<br><br>" \
                + df2.to_html(index=False) + "<br><br>Thank you.<br><br> Ramzan Khuwaja<br><br>" 

            utils.send_email(to, cc, subject_email, body_email)


def main():
    utils.set_campus_info("VAU")

    print("Entering VAU RemindForBSLogin")
        
    df_remind_students = utils.RemindForBSLogin("VAU")

    if df_remind_students.empty:
        print("Exiting VAU RemindForBSLogin")
        return True
    else:
        email_to_remind_restudents(df_remind_students)
        utils.export_student_reminder_to_excel(df_remind_students, "VAU")

        print("ERROR: Exiting VAU RemindForBSLogin")
        return False
    
if __name__ == "__main__":
    main()