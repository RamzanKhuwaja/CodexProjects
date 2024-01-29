import Common.my_utils as utils

def main():
    utils.set_campus_info("VAU")

    print("Entering VAU StrugglingStudents")
        
    df_struggling_students = utils.FindStrugglingStudents("VAU")

    if df_struggling_students.empty:
        print("No struggling students - Exiting VAU StrugglingStudents")
        return True
    else:
        utils.email_struggling_students_to_stakeholders(df_struggling_students)
        print("ERROR: Found struggling students - Exiting VAU StrugglingStudents")
        return False

if __name__ == "__main__":
    main()
    
