import pandas as pd
import my_mae_utils as utils
from datetime import datetime


TESTING = True
FOR_OFFICE_USE_ONLY = True

NOT_LOGGED_IN_SINCE = int(14) # Not logged in since last 2 weeks!
teacher = email = klasses = all_klasses = ""
class_list_1 = class_list_2 = class_list_3 = class_list_4 = class_list_5 = class_list_6 = class_list_7 = class_list_8 = class_list_9 = class_list_10 = class_list_11 = ""


# Set display options
pd.set_option('display.max_columns', None)  # Show all columns
pd.set_option('display.max_rows', None)     # Show all rows
pd.set_option('display.max_colwidth', None) # Show full content of each column
pd.set_option('display.width', None)        # Automatically detect the console width

# Read STUDENT_MAP_FILE as a df
df_student_map = pd.read_csv(utils.STUDENT_MAP_FILE)

# Read ClassMap as a df
df_class_map = pd.read_csv(utils.CLASS_MAP_FILE)

targeted_df = df_student_map[df_student_map['Last Accessed'].apply (lambda x: utils.is_within_days(x, NOT_LOGGED_IN_SINCE))]

# Define the columns you want to keep
columns_to_keep = ["Student Full Name", "Last Accessed", "Class Code", "Teacher Full Name", "Teacher Email", "Teacher Group", "Parent Email"]
targeted_df = targeted_df[columns_to_keep]

df_class_list_1 = targeted_df[targeted_df['Teacher Group'] == "class_list_1"]
df_class_list_2 = targeted_df[targeted_df['Teacher Group'] == "class_list_2"]
df_class_list_3 = targeted_df[targeted_df['Teacher Group'] == "class_list_3"]
df_class_list_4 = targeted_df[targeted_df['Teacher Group'] == "class_list_4"]
df_class_list_5 = targeted_df[targeted_df['Teacher Group'] == "class_list_5"]
df_class_list_6 = targeted_df[targeted_df['Teacher Group'] == "class_list_6"]
df_class_list_7 = targeted_df[targeted_df['Teacher Group'] == "class_list_7"]
df_class_list_8 = targeted_df[targeted_df['Teacher Group'] == "class_list_8"]
df_class_list_9 = targeted_df[targeted_df['Teacher Group'] == "class_list_9"]
df_class_list_10 = targeted_df[targeted_df['Teacher Group'] == "class_list_10"]
df_class_list_11 = targeted_df[targeted_df['Teacher Group'] == "class_list_11"]

# Redefine the columns you want to keep
columns_to_keep = ["Class Code", "Student Full Name", "Parent Email", "Last Accessed"]
df_class_list_1 = df_class_list_1[columns_to_keep].sort_values(by=["Class Code", "Student Full Name"], ascending=[True, True])
df_class_list_2 = df_class_list_2[columns_to_keep].sort_values(by=["Class Code", "Student Full Name"], ascending=[True, True])
df_class_list_3 = df_class_list_3[columns_to_keep].sort_values(by=["Class Code", "Student Full Name"], ascending=[True, True])
df_class_list_4 = df_class_list_4[columns_to_keep].sort_values(by=["Class Code", "Student Full Name"], ascending=[True, True])
df_class_list_5 = df_class_list_5[columns_to_keep].sort_values(by=["Class Code", "Student Full Name"], ascending=[True, True])
df_class_list_6 = df_class_list_6[columns_to_keep].sort_values(by=["Class Code", "Student Full Name"], ascending=[True, True])
df_class_list_7 = df_class_list_7[columns_to_keep].sort_values(by=["Class Code", "Student Full Name"], ascending=[True, True])
df_class_list_8 = df_class_list_8[columns_to_keep].sort_values(by=["Class Code", "Student Full Name"], ascending=[True, True])
df_class_list_9 = df_class_list_9[columns_to_keep].sort_values(by=["Class Code", "Student Full Name"], ascending=[True, True])
df_class_list_10 = df_class_list_10[columns_to_keep].sort_values(by=["Class Code", "Student Full Name"], ascending=[True, True])
df_class_list_11 = df_class_list_11[columns_to_keep].sort_values(by=["Class Code", "Student Full Name"], ascending=[True, True])


class_list_1 = "<br>" + df_class_list_1.to_html(index=False) + "<br>"
class_list_2 = "<br>" + df_class_list_2.to_html(index=False) + "<br>"
class_list_3 = "<br>" + df_class_list_3.to_html(index=False) + "<br>"
class_list_4 = "<br>" + df_class_list_4.to_html(index=False) + "<br>"
class_list_5 = "<br>" + df_class_list_5.to_html(index=False) + "<br>"
class_list_6 = "<br>" + df_class_list_6.to_html(index=False) + "<br>"
class_list_7 = "<br>" + df_class_list_7.to_html(index=False) + "<br>"
class_list_8 = "<br>" + df_class_list_8.to_html(index=False) + "<br>"
class_list_9 = "<br>" + df_class_list_9.to_html(index=False) + "<br>"
class_list_10 = "<br>" + df_class_list_10.to_html(index=False) + "<br>"
class_list_11 = "<br>" + df_class_list_11.to_html(index=False) + "<br>"


# Getting unique values from the 'Classes That Need Attention' column
unique_lists = df_class_map['Teacher Group'].unique()

# Iterating through unique values
for value in unique_lists:
    teacher_info = df_class_map[df_class_map['Teacher Group'] == value]
    teacher_name = teacher_info["Teacher Full Name"].iloc[0]
    teacher_email = teacher_info["Teacher Email"].iloc[0]

     # case statement
    case_key = teacher_info["Teacher Group"].iloc[0]

    if case_key == "class_list_1":
            klasses = class_list_1 
    elif case_key == "class_list_2":
            klasses = class_list_2 
    elif case_key == "class_list_3":
            klasses = class_list_3 
    elif case_key == "class_list_4":
            klasses = class_list_4 
    elif case_key == "class_list_5":
            klasses = class_list_5        
    elif case_key == "class_list_6":
            klasses = class_list_6 
    elif case_key == "class_list_7":
            klasses = class_list_7 
    elif case_key == "class_list_8":
            klasses = class_list_8 
    elif case_key == "class_list_9":
            klasses = class_list_9      
    elif case_key == "class_list_10":
            klasses = class_list_10 
    elif case_key == "class_list_11":
            klasses = class_list_11                          
    else:
            print("ERROR: Sending emails: Should not be here!")
    
    if (not TESTING) and (klasses != ""):
        to=teacher_email
        cc="vaughan@spiritofmath.com"
        subject="Please remind these students to login to BS regularly"
        body="Hello " + teacher_name + ",<br><br>" \
            + "The following students have not logged in for at least 2 weeks to Brightspace. The successful student uses this resource regularly.  Please remind these students to login every week and use its content.<br>" \
            + "<br>Thank you.<br>" \
            + klasses + "<br><br>Ramzan Khuwaja<br>"

        utils.send_email(to, cc, subject, body)

    if (FOR_OFFICE_USE_ONLY) and (klasses != ""):
         all_klasses = all_klasses + "<br><b>Teacher Name: " + teacher_name + "</b><br>" + klasses


if TESTING and (all_klasses != ""):
    to="rkhuwaja@spiritofmath.com"
    cc=""
    subject="Please remind these students to login to BS regularly"
    body="Hello Office," + "<br><br>" \
        + "The following students have not logged in for at least 2 weeks to Brightspace. The successful student uses this resource regularly.  Please remind these students to login every week and use its content.<br>" \
        + "<br>Thank you.<br>" \
        + all_klasses + "<br><br>Ramzan Khuwaja<br>"

    utils.send_email(to, cc, subject, body)


if FOR_OFFICE_USE_ONLY and (all_klasses != ""):

    # Get today's date
    today = datetime.now()

    # Format the date as a string
    date_string = today.strftime("%B %d, %Y")  # Format: November 23, 2023

    # Specify the output path
    output_path = utils.MAEPDFdirectory + "\\RemindForBSLogin-" + date_string + ".xlsx"

    # Define the columns you want to keep
    columns_to_keep = ["Teacher Full Name", "Class Code", "Student Full Name", "Parent Email", "Last Accessed"]
    targeted_df = targeted_df[columns_to_keep].sort_values(by=["Teacher Full Name", "Class Code", "Student Full Name"], ascending=[True, True, True])

    targeted_df.to_excel(output_path, index=False)
    print("NeedToAttendMoreRegularly exported to " + output_path)

