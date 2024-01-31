import pandas as pd
from datetime import datetime
import Common.my_utils as utils

def RemindForBSLogin(campus):
    print("Start - RemindForBSLogin")

    if campus == "VAU":
        student_map_file = utils.VAU_STUDENT_MAP_FILE
    elif campus == "MAE":
        student_map_file = utils.MAE_STUDENT_MAP_FILE
    else: 
        print("ERROR: Invalid campus name")
        return False

    df_student_map = pd.read_csv(student_map_file)

    targeted_df = df_student_map[df_student_map['Last Accessed'].apply (lambda x: utils.is_within_days(x, utils.NOT_LOGGED_IN_SINCE))]

    # Define the columns you want to keep
    columns_to_keep = ["Student Full Name", "Last Accessed", "Class Code", "Teacher Full Name", "Teacher Email", "Teacher Group", "Parent Email"]
    targeted_df = targeted_df[columns_to_keep]
    return targeted_df


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


def export_student_reminder_to_excel(df_remind_students, campus):
    if utils.PRINT_REPORT:

        if campus == "VAU":
            report_dir = utils.VAU_REPORT_DIRECTORY + "\\VAU_RemindForBSLogin-"
        elif campus == "MAE":
            report_dir = utils.MAE_REPORT_DIRECTORY + "\\MAE_RemindForBSLogin-"
        else: 
            print("ERROR: Invalid campus name")
            return False

        # Get today's date
        today = datetime.now()

        # Format the date as a string
        date_string = today.strftime("%B %d, %Y")  # Format (e.g.,): November 23, 2023

        # Specify the output path
        output_path = report_dir + date_string + ".xlsx"

        df2 = pd.DataFrame(df_remind_students, columns=["Teacher Full Name", "Class Code", "Student Full Name", "Last Accessed", "Parent Email"])

        df2 = df2.sort_values(
            by=["Teacher Full Name", "Class Code", "Student Full Name", "Last Accessed"], 
            ascending=[True, True, True, True]
        )

        df2.to_excel(output_path, index=False)
        print("MAE_RemindStudents exported to " + output_path)

def main():
    utils.set_campus_info("MAE")

    print("Entering MAE RemindForBSLogin")
        
    df_remind_students = RemindForBSLogin("MAE")

    if df_remind_students.empty:
        print("Exiting MAE RemindForBSLogin")
        return True
    else:
        email_to_remind_restudents(df_remind_students)
        export_student_reminder_to_excel(df_remind_students, "MAE")

        print("ERROR: Exiting MAE RemindForBSLogin")
        return False
    
if __name__ == "__main__":
    main()