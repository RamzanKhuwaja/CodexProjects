import os
import time
import pandas as pd
import my_mae_utils as utils


TESTING = True
current_som_week = past_two_weeks = 0
teacher = email = klass = ""
class_list_1 = class_list_2 = class_list_3 = class_list_4 = class_list_5 = class_list_6 = class_list_7 = class_list_8 = class_list_9 = class_list_10 = class_list_11 = ""

# Read CLASS_MAP_FILE as a df
df_class_map = pd.read_csv(utils.CLASS_MAP_FILE)

current_som_week = int(df_class_map["Todays Week Number"].iloc[0])
past_two_weeks = str(current_som_week - 2)

# Read each CSV file in this directory using pandas library
os.chdir(utils.ATTENDANCE_DIR)

for filename in os.listdir(utils.ATTENDANCE_DIR):

    if filename.endswith(".csv"):
        df_att = pd.read_csv(filename)

        # Clean each cell that has "-" to a blank
        df_att.replace("-", None, inplace=True)

        # Check the column "Lesson 10," e.g., and if all rows are blank then print "Yes" to the output terminal
        if ("Lesson " + past_two_weeks) in df_att.columns and df_att[
            "Lesson " + past_two_weeks
        ].isna().all():
            # Lookup the first value in the first row in column "Org Defined ID" in df_att
            student_id = df_att["Org Defined ID"].iloc[0]

            # Look up student_id in df_class_map
            teacher_info = df_class_map[df_class_map["Org Defined ID"] == student_id]

            if not teacher_info.empty: 

                # Store the values in the 'Teacher', 'Email', 'Class' columns to variables
                teacher = teacher_info["Teacher Full Name"].iloc[0]
                email = teacher_info["Teacher Email"].iloc[0]
                klass = teacher_info["Class Code"].iloc[0]

                # case statement
                case_key = teacher_info["Teacher Group"].iloc[0]

                if case_key == "class_list_1":
                    class_list_1 = class_list_1 + "<li>" + klass + "</li>"
                elif case_key == "class_list_2":
                    class_list_2 = class_list_2 + "<li>" + klass + "</li>"
                elif case_key == "class_list_3":
                    class_list_3 = class_list_3 + "<li>" + klass + "</li>"
                elif case_key == "class_list_4":
                    class_list_4 = class_list_4 + "<li>" + klass + "</li>"
                elif case_key == "class_list_5":
                    class_list_5 = class_list_5 + "<li>" + klass + "</li>"
                elif case_key == "class_list_6":
                    class_list_6 = class_list_6 + "<li>" + klass + "</li>"
                elif case_key == "class_list_7":
                    class_list_7 = class_list_7 + "<li>" + klass + "</li>"
                elif case_key == "class_list_8":
                    class_list_8 = class_list_8 + "<li>" + klass + "</li>"
                elif case_key == "class_list_9":
                    class_list_9 = class_list_9 + "<li>" + klass + "</li>"
                elif case_key == "class_list_10":
                    class_list_10 = class_list_10 + "<li>" + klass + "</li>"
                elif case_key == "class_list_11":
                    class_list_11 = class_list_11 + "<li>" + klass + "</li>"
                else:
                    print("ERROR: Can't find a class list in 'Teacher Group!' column in the df_class_map file!")
            else:
                print("ERROR: Can't find student id " + str(student_id) + " in the df_class_map file! " + "Source attendance file: " + filename)
        else: 
             print("MESSAGE: Data is up-to-date in the file: " + filename)

# Getting unique values from the 'blah' column
unique_lists = df_class_map['Teacher Group'].unique()

# Iterating through unique values
for value in unique_lists:
    teacher_info = df_class_map[df_class_map["Teacher Group"] == value]
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
            print("Sending emails: Should not be here!")
    
    utils.set_campus_info()

    if (klasses != ""): 

        if TESTING: 
            to=utils.to_email
        else:
            to=teacher_email
        if TESTING: 
            cc=utils.to_email
        else:
            cc="vaughan@spiritofmath.com"

        subject="Please update your Brightspace class data"
        body="Hello " + teacher_name + ",<br><br>" + \
            "Spirit of Math advises parents and students to access their class attendance and marks within a week after a class is completed.  \n\nOur records show that the following of your classes have not been updated for the past two weeks!  Please update ASAP and keep the above practice for the rest of this school year.  Thank you.<br><br>" \
                + klasses + "<br><br>Sincerely, <br>Ramzan Khuwaja"

        utils.send_email(to, cc, subject, body)
