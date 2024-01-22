from numpy import float64, int64
import pandas as pd
import my_mae_utils as utils


def main():
    # Set the maximum number of columns to display without truncation
    pd.set_option('display.max_columns', None)
    
    #create a dataframe - StudentMap
    columns = ['Org Defined ID', 'Student Full Name', 'Last Accessed', 'Class Code', 'Teacher Full Name', 'Teacher Email', 'Teacher Group', 'Attendance (%)', 'Parent Email', 'Start Week', 'Final Grade']
    StudentMap = pd.DataFrame(columns=columns)

    # Specify data types for each column after creating the DataFrame
    column_types = {
        'Org Defined ID': int64,
        'Student Full Name': object,
        'Last Accessed': object,
        'Class Code': object,
        'Teacher Full Name': object,
        'Teacher Email': object,
        'Teacher Group': object,
        'Attendance (%)': object,
        'Parent Email': object,
        'Start Week': int64,
        'Final Grade': float64
    }
    StudentMap = StudentMap.astype(column_types)

    StudentMap = utils.add_class_list_data(StudentMap)
    #print(StudentMap)

    ClassMap = pd.read_csv(utils.CLASS_MAP_FILE)

    print("Start - Copying StudentMap data")
 
    #Copy Data from ClassMap to  StudentMap
    for index, row in StudentMap.iterrows():
        class_code = row['Class Code']
        matching_row = None
        
        # Check if class_code exists in ClassMap
        if class_code in ClassMap['Class Code'].values:
            matching_row = ClassMap[ClassMap['Class Code'] == class_code].iloc[0]
            #print(matching_row.dtype)
            
            # Copy data from df1 to df_master
            f_name = matching_row['Teacher Full Name']
            #print(f_name)
            #print(index)
            StudentMap.at[index, 'Teacher Full Name'] = f_name
            StudentMap.at[index, 'Teacher Email'] = matching_row['Teacher Email']
            StudentMap.at[index, 'Teacher Group'] = matching_row['Teacher Group']

    print("End - Copying StudentMap data")

    print("Start - Copying Attandance data")

    #Get Attandance Data dataframe
    AttandanceData = utils.get_attendance_data()
    
    #Copy Attandance Data to  StudentMap
    for index, row in StudentMap.iterrows():
        student_id = row['Org Defined ID']
        
        # Check if student_id exists in AttandanceData
        # if student_id in AttandanceData['Org Defined ID'].values:
        if AttandanceData['Org Defined ID'].isin([student_id]).any():
            matching_row = AttandanceData[AttandanceData['Org Defined ID'] == student_id].iloc[0]
            
            # Copy data from AttandanceData to df_master
            StudentMap.at[index, 'Attendance (%)'] = matching_row['% Attendance']

    print("End - Copying Attandance data")

    print("Start - Copying Grade data")

    #Get Grade Data dataframe
    GradesData = utils.get_grades_data()
    #print(GradesData)

    # #Copy Grades Data to  StudentMap
    for index, row in StudentMap.iterrows():
        student_id = row['Org Defined ID']
        
        # Check if student_id exists in AttandanceData
        if student_id in GradesData['OrgDefinedId'].values:
            matching_row = GradesData[GradesData['OrgDefinedId'] == student_id].iloc[0]
            
            # Copy data from GradesData to df_master
            StudentMap.at[index, 'Parent Email'] = matching_row['Email']
            StudentMap.at[index, 'Final Grade'] = matching_row['Final Grade']
            # if Start Week is NaN then assign -1
            if pd.isnull(matching_row['Start Week']):
                StudentMap.at[index, 'Start Week'] = -1
            else:
                StudentMap.at[index, 'Start Week'] = matching_row['Start Week']
        else:
            print("ERROR: Student ID not found in GradesData: " + str(student_id))
            
    print("End - Copying Grade data")

    #save datafrane - StudentMap
    StudentMap.to_csv(utils.STUDENT_MAP_FILE, index=False)
    #print("StudentMap saved to " + utils.STUDENT_MAP_FILE)

    # Find and print rows with empty cells
    empty_rows = StudentMap[StudentMap.isnull().any(axis=1)]
    if empty_rows.empty:
        print("Good: No empty cells found in StudentMap!")
    else:
        print("StudentMap rows with empty cells:")
        print(empty_rows)   


if __name__ == "__main__":
    main()


