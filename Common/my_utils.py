import os
import re
import time
import pdfkit
import pandas as pd
from bs4 import BeautifulSoup
from numpy import float64, int64
import win32com.client as email_client
from datetime import datetime, timedelta


CAMPUS = to_email = cc_email = body_email = subject_email = ""

TESTING = True  #  <======  Be CAREFUL with this switch!!!!!!!!!!!!!
THIS_WEEK_NUM = 22 #  <======  Change this every week!!!!!!!!!!!!!!
SEND_EMAIL = True
PRINT_REPORT = True
GRADES_MIN_BAR = int(50) # Scoring less than 50%!
HIGH_HONOURS_MIN_BAR = int(90) # Scoring 90% or higher!
NOT_LOGGED_IN_SINCE = int(14) # Not logged in since last 2 weeks!
ATTENDANCE_MIN_BAR = int(80) # Min attendance required (in %)

# Path where ClassMap file is stored
VAU_CLASS_MAP_FILE  = r'C:\Users\ramza\Dropbox\VAUDocs\Automation\Code\Automation\Common\VAUClassMap2023-24.csv'
MAE_CLASS_MAP_FILE  = r'C:\Users\ramza\Dropbox\VAUDocs\Automation\Code\Automation\Common\MAEClassMap2023-24.csv'

# Path where StudentMap file is stored
VAU_STUDENT_MAP_FILE = r'C:\Users\ramza\Dropbox\VAUDocs\Automation\Code\Automation\Common\VAUStudentMap2023-24.csv'
MAE_STUDENT_MAP_FILE = r'C:\Users\ramza\Dropbox\VAUDocs\Automation\Code\Automation\Common\MAEStudentMap2023-24.csv'

# Directory containing the CSV files for Attendance
VAU_ATTENDANCE_DIR = r'C:\Users\ramza\Dropbox\VAUDocs\Automation\Data\VAU\Attendance\BSFiles'
MAE_ATTENDANCE_DIR = r'C:\Users\ramza\Dropbox\VAUDocs\Automation\Data\MAE\Attendance\BSFiles'

# Dir where Brightspace Class List (HTML files)downloaded files are stored
VAU_CLASS_LIST_DIR = r'C:\Users\ramza\Dropbox\VAUDocs\Automation\Data\VAU\BSLogin'
MAE_CLASS_LIST_DIR = r'C:\Users\ramza\Dropbox\VAUDocs\Automation\Data\MAE\BSLogin'

# Directory containing the CSV files for Grades
VAU_GRADES_DIR = r'C:\Users\ramza\Dropbox\VAUDocs\Automation\Data\VAU\Grades\BSFiles'
MAE_GRADES_DIR = r'C:\Users\ramza\Dropbox\VAUDocs\Automation\Data\MAE\Grades\BSFiles'

# Path where PDF files are stored
VAU_REPORT_DIRECTORY = r"C:\Users\ramza\Dropbox\VAUDocs\Automation\Ready For Printing\VAU"
MAE_REPORT_DIRECTORY = r"C:\Users\ramza\Dropbox\MAE Share\Automation\Ready For Printing\MAE"

# Ensure the directory exists else create one
#os.makedirs(os.path.dirname(output_path), exist_ok=True)

def set_campus_info(campus_code):
    global CAMPUS, to_email, cc_email
    if campus_code == "VAU":
        to_email = "rkhuwaja@spiritofmath.com"
        cc_email = "vaughan@spiritofmath.com"
        CAMPUS = campus_code
    elif campus_code == "MAE":
        to_email = "rkhuwaja@spiritofmath.com"
        cc_email = "markhameast@spiritofmath.com"
        CAMPUS = campus_code
    else:
        print("ERROR: Invalid campus code")

def check_duplicates_in_column(df, column_name):
    duplicates = df[df.duplicated(column_name, keep=False)]
    if not duplicates.empty:
        print(f"Duplicate entries found in '{column_name}':")
        for index, row in duplicates.iterrows():
            print(f"Row {index + 2}: {row[column_name]}")
        print()
    else:
        print(f"No duplicates found in '{column_name}'.")

def check_class_map (ClassMap):
    try:
        df = pd.read_csv(ClassMap)

        columns_to_check = ['Class Code', 'Attendance', 'Grades', 'ClassList']
        for column in columns_to_check:
            if column in df.columns:
                check_duplicates_in_column(df, column)
            else:
                print(f"Column '{column}' not found in the CSV file.")
        return True

    except FileNotFoundError:
        print(f"File not found: {ClassMap}")
        return False
    except Exception as e:
        print(f"An error occurred: {e}")
        return False


# Function to strip leading '#' or '#0' from a string
def strip_hash(input_string):
    # # Define a regular expression pattern to match "#" or "#0" at the beginning of the string
    # pattern = r'^#0?'
    
    # # Use re.sub to replace the matched pattern with an empty string
    # result = re.sub(pattern, '', input_string)

    # Remove non-numeric characters from the beginning and end of the string
    cleaned_str = ''.join(c for c in input_string if c.isdigit())

    # Ensure the string doesn't start with zero
    while cleaned_str.startswith('0') and len(cleaned_str) > 1:
        cleaned_str = cleaned_str[1:]

    return cleaned_str
    
    #return result


# Function to clean a cell value
def clean_cell(cell_value):
    if isinstance(cell_value, str):
        # Remove non-alphanumeric characters from the beginning and end
        cleaned_value = re.sub(r'^[^a-zA-Z0-9]+|[^a-zA-Z0-9]+$', '', cell_value)
        return cleaned_value
    else:
        return cell_value
    

def send_email(to, cc, subject, body):
    # Use the Dispatch method to interact with Outlook
    outlook = email_client.Dispatch("outlook.application")
    mail = outlook.CreateItem(0)  # 0 is the code for an email item

    # Get today's date
    today = datetime.now()

    # Format the date as a string
    date_string = today.strftime("%B %d, %Y")  # Format (e.g.,): November 23, 2023

    # Set mail properties
    mail.To = to  # String of recipient email addresses
    mail.CC = cc  # String of CC email addresses
    mail.Subject = CAMPUS + ": " + date_string + ": " + subject  # String for the email's subject
    #mail.Body = body  # String for the email's body
    # Set the email body to HTML
    mail.HTMLBody = body  # String containing HTML for the email's body

    # Send the email
    mail.Send()
    time.sleep(5)

def create_pdf_from_html(html, output_path):
    # Configuration for pdfkit to use wkhtmltopdf
    # Replace '/path/to/wkhtmltopdf' with the actual path to the wkhtmltopdf executable on your system
    config = pdfkit.configuration(wkhtmltopdf='C:/Program Files/wkhtmltopdf/bin/wkhtmltopdf.exe')

    # Options to pass to wkhtmltopdf
    # These options ensure wkhtmltopdf runs in headless mode
    options = {
        'enable-local-file-access': '',
        'quiet': ''
    }

    # Convert HTML to PDF
    try:
        pdfkit.from_string(html, output_path, configuration=config, options=options)
        print(f"PDF saved at {output_path}")
    except IOError as e:
        print(f"An error occurred: {e}")
    except Exception as e:
        print(f"An unexpected error occurred: {e}")

# Function to convert date format
def convert_date_format(date_str):
    #print(date_str)
    if not pd.isna(date_str):
        # Convert to datetime object
        date_object = datetime.strptime(date_str, '%b %d, %Y %I:%M %p')
        # Convert back to string with new format
        new_date_str = date_object.strftime('%b %d, %Y')
    else: 
        new_date_str = str(datetime.now().strftime('%b %d, %Y'))
    return new_date_str

def is_within_days(date_str, NOT_LOGGED_IN_SINCE):
    # Change the format here to '%d-%b-%y' to match the input date format 'DD-Mon-YY'
    date_object = datetime.strptime(date_str, '%b %d, %Y') #'%d-%b-%y')
    fourteen_days_ago = datetime.now() - timedelta(days=NOT_LOGGED_IN_SINCE)
    return date_object < fourteen_days_ago

# Generate HTML code for head and body start
def generate_html_head_and_body_start():
# HTML tags
    html_content = """
    <!DOCTYPE html>
    <html>
    <head>
        <style>
            body {
                font-family: Arial, sans-serif;
            }
            .custom-font {
                font-family: Arial, sans-serif;
            }
            table, th, td {
                border: 1px solid black;
            }
            table {
                border-collapse: collapse; 
            }
        </style>
    </head>
    <body>
    """
    return html_content

# Generate HTML code for table start
def generate_html_table_start():
# HTML tags
    table_content_start = """
                <table> \
                <thead>
                    <tr>
                        <th>First Name</th>
                        <th>Last Name</th>
                        <th>Org Defined ID</th>
                        <th>Attendance (%)</th>
                    </tr>
                </thead>
                <tbody>
            """
    return table_content_start

# Generate HTML code for table start
def generate_html_grades_table_start():
# HTML tags
    table_content_start = """
                <table border="1"> \
                <thead>
                    <tr>
                        <th>First Name</th>
                        <th>Last Name</th>
                        <th>Org Defined ID</th>
                        <th>Grade (%)</th>
                        <th>Email</th>
                    </tr>
                </thead>
                <tbody>
            """
    return table_content_start

# Generate HTML code for table end
def generate_html_table_end():
    table_content_end = """
                    </tbody>
                </table>
    """
    return table_content_end

# Function to strip leading '#'
def strip_leading_hash(s):
    return s.lstrip('#')

def calculate_final_grade(row):
    try:
        # Extract values
        numerator = row['Calculated Final Grade Numerator']
        denominator = row['Calculated Final Grade Denominator']

        # Replace NaN with default values
        numerator = 0 if pd.isna(numerator) else numerator
        denominator = 1 if pd.isna(denominator) else denominator  # Corrected line

        # Check for division by zero
        if denominator == 0:
            final_grade = 0
        else:
            # Perform division and safely convert to integer
            final_grade = int(100 * numerator / denominator)
    except ZeroDivisionError:
        # Handle division by zero if needed
        final_grade = 0
    except Exception as e:
        # Handle any other exceptions
        print(f"WARNING - Error occurred: {e}")
        final_grade = 0

    return final_grade


# Read each HTML file in this directory using pandas library

def add_class_list_data(master_df, class_list_dir_path):
    os.chdir(class_list_dir_path)
    for filename in os.listdir(class_list_dir_path):
        if filename.endswith(".htm"):
            # Read the HTML file
            tables = pd.read_html(filename)

            # Check if there are at least 7 tables
            if len(tables) >= 7:
                # Assign the 7th table to a new DataFrame variable
                seventh_table_df = tables[6]

                # Filter the DataFrame to only include rows where the role is 'student'
                student_df = seventh_table_df[seventh_table_df['Role'] == 'Student']
                student_df = student_df.rename(columns={'First Name,\xa0Last Name': 'Student Full Name'})

                # Define the columns you want to keep
                columns_to_keep = ["Org Defined ID", "Student Full Name", "Last Accessed"]

                # Select only these columns from student_df
                filtered_student_df = student_df[columns_to_keep].copy()
                filtered_student_df['Org Defined ID'] = filtered_student_df['Org Defined ID'].astype(int64)
                filtered_student_df['Student Full Name'] = filtered_student_df['Student Full Name'].astype(object)
                filtered_student_df['Org Defined ID'] = filtered_student_df['Org Defined ID'].astype(object)

                # Define the default date in the specified format
                default_date = 'Sep 01, 2023 5:50 PM'

                # Check for missing values and fill them
                filtered_student_df['Last Accessed'] = filtered_student_df['Last Accessed'].apply(lambda x: default_date if pd.isna(x) else x)

                # Convert and update the 'Last Accessed' column
                filtered_student_df['Last Accessed'] = filtered_student_df['Last Accessed'].apply(convert_date_format)

                # Read the content of the file
                with open(filename, 'r', encoding='utf-8') as file:
                    html_content = file.read()

                # Parse the HTML content
                soup = BeautifulSoup(html_content, 'html.parser')

                # Find the anchor tag with the class 'd21-navigation-s-link'
                link = soup.find('a', class_='d2l-navigation-s-link')

                # Extract the title attribute
                title = link.get('title', '') if link else ''

                # Extract the class code from the title
                # Assuming the class code is always at the end after the last dash
                class_code = title.split('-')[-1].strip() if title else ''

                #Add class code to all rows in a new column "Class Code" in the filtered_student_df
                filtered_student_df["Class Code"] = class_code
                #print(filtered_student_df)
                master_df = pd.concat([master_df, filtered_student_df], axis=0)
            else: 
                print("ERROR: This file has less than 7 tables: " + filename)
        else:
            print("ERROR: " + filename + " is not an HTML file!")

    master_df = master_df.reset_index(drop=True)
    return master_df


# Read each CSV file in Attendance directory using pandas library
def get_attendance_data(attendance_dir):
    attendance_df = pd.DataFrame()

    os.chdir(attendance_dir)

    for filename in os.listdir(attendance_dir):

        if filename.endswith(".csv"):
            attendance_df = pd.concat([attendance_df, pd.read_csv(filename)], axis=0)
        else: 
            print("WARNING: This is not a CSV file: " + filename)

    attendance_df = attendance_df.reset_index(drop=True)

    # Clean each cell that has "-" to a blank
    attendance_df.replace("-", None, inplace=True)
    
    return attendance_df



# Read each CSV file in Grades directory using pandas library
def get_grades_data(grades_dir):
    grades_df = pd.DataFrame()
    os.chdir(grades_dir)
    for filename in os.listdir(grades_dir):
        if filename.endswith(".csv"):
            grades_df_temp = pd.read_csv(filename)

            # Check if the DataFrame is empty
            if grades_df_temp.empty:
                print("ERROR: The file is empty: " + filename)
            else:
                # Check for rows containing only "End-of-Line Indicator"
                if (grades_df_temp.shape[1] == 1) and all(grades_df_temp.iloc[:, 0] == "End-of-Line Indicator"):
                    print("ERROR: The file contains only 'End-of-Line Indicator' word: " + filename)
                else:
                    # Renaming the column
                    #print(filename)

                    # Find the column that starts with or contains the specified substring
                    column_to_rename = [col for col in grades_df_temp.columns if "Enrolment Start Week Points Grade" in col]

                    # Check if the column exists and rename it
                    if column_to_rename:
                        # Only take the first matching column if there are multiple
                        grades_df_temp.rename(columns={column_to_rename[0]: 'Start Week'}, inplace=True)
                    else:
                        print("ERROR: No column found with the specified substring: Enrolment Start Week Points Grade: " + filename)

                    #grades_df_temp.rename(columns={'Enrolment Start Week Points Grade <Numeric MaxPoints:39>': 'Start Week'}, inplace=True)
                    #print(grades_df_temp.dtypes)
                    # Calculate the final grade
                    grades_df_temp['Final Grade'] = float64(grades_df_temp.apply(calculate_final_grade, axis=1))

                    # Apply the function to the 'OrgDefinedId' column
                    grades_df_temp['OrgDefinedId'] = int64(grades_df_temp['OrgDefinedId'].apply(strip_hash))

                    # Find column names that contain 'Start Week'
                    matching_columns = [col for col in grades_df_temp.columns if 'Start Week' in col]

                    # # Select the column if one matching column is found
                    # if len(matching_columns) == 1:
                    #     grades_df_temp['Start Week'] = int64(grades_df_temp[matching_columns[0]])
                    # elif len(matching_columns) > 1:
                    #     print("ERROR: Multiple columns found containing 'Start Week':", matching_columns)
                    # else:
                    #     print("ERROR: No column found with 'Start Week' in its name" + filename)

                    # Select the column if one matching column is found

                    # Check if 'Start Week' column already exists
                    if 'Start Week' not in grades_df_temp.columns:
                        # If it doesn't exist, create it with default value -1
                        grades_df_temp['Start Week'] = -1
                    else:
                        # If it exists, proceed with your existing logic
                        if len(matching_columns) == 1:
                            # Replace NaN with a placeholder, e.g., -1, then convert to int64
                            grades_df_temp[matching_columns[0]] = grades_df_temp[matching_columns[0]].fillna(-1).astype('int64')

                            grades_df_temp['Start Week'] = grades_df_temp[matching_columns[0]].astype('int64')
                        elif len(matching_columns) > 1:
                            print("WARNING: Multiple columns found containing 'Start Week':", matching_columns)
                            # Replace NaN with a placeholder, e.g., -1, then convert to int64
                            grades_df_temp[matching_columns[0]] = grades_df_temp[matching_columns[0]].fillna(-1).astype('int64')

                            grades_df_temp['Start Week'] = grades_df_temp[matching_columns[0]].astype('int64')
                        else:
                            # This block will now only execute if 'Start Week' exists but no matching columns are found
                            print("ERROR: No column found with 'Start Week' in its name in " + filename)

                    #grades_df_temp['Start Week'] = int64(grades_df_temp['Start Week'])
                    grades_df = pd.concat([grades_df, grades_df_temp], axis=0)
        else: 
            print("WARNING: This is not a CSV file: " + filename)

    grades_df = grades_df.reset_index(drop=True)
    return grades_df


def FindDupStudentsInBSViaClassList (BSdirectory): 

    # Set display options
    pd.set_option('display.max_columns', None)  # Show all columns
    pd.set_option('display.max_rows', None)     # Show all rows
    pd.set_option('display.max_colwidth', None) # Show full content of each column
    pd.set_option('display.width', None)        # Automatically detect the console width

    filtered_student_df = pd.DataFrame()

    # Read each HTML file in this directory using pandas library
    os.chdir(BSdirectory)
    for filename in os.listdir(BSdirectory):
        if filename.endswith(".htm"):
            # Read the HTML file
            tables = pd.read_html(filename)

            # Check if there are at least 7 tables
            if len(tables) >= 7:
                # Assign the 7th table to a new DataFrame variable
                seventh_table_df = tables[6]

                # Filter the DataFrame to only include rows where the role is 'student'
                student_df = seventh_table_df[seventh_table_df['Role'] == 'Student']

                student_df.columns.values[2] = 'Full Name'

                student_df = student_df.iloc[:, [2, 3]]

                # Select only these columns from student_df
                temp_df = student_df.copy()

                # Read the content of the file
                with open(filename, 'r', encoding='utf-8') as file:
                    html_content = file.read()

                # Parse the HTML content
                soup = BeautifulSoup(html_content, 'html.parser')

                # Find the anchor tag with the class 'd21-navigation-s-link'
                link = soup.find('a', class_='d2l-navigation-s-link')

                # Extract the title attribute
                title = link.get('title', '') if link else ''

                # Extract the class code from the title
                # Assuming the class code is always at the end after the last dash
                class_code = title.split('-')[-1].strip() if title else ''

                temp_df["Class Code"] = class_code

                filtered_student_df = pd.concat([filtered_student_df, temp_df], ignore_index=True)
            else: 
                print("ERROR: This file has less than 7 tables: " + filename)
                return False
        else:
            print("ERROR: " + filename + " is not an HTML file!")
            return False

    # Convert 'col' from string to int, set errors='coerce' to handle non-numeric values
    filtered_student_df['Org Defined ID'] = pd.to_numeric(filtered_student_df['Org Defined ID'], errors='coerce')

    # Find duplicates based on 'Org Defined ID'
    duplicates = filtered_student_df[filtered_student_df.duplicated(subset='Org Defined ID', keep=False)]

    # Sort the DataFrame based on 'Org Defined ID'
    sorted_duplicates = duplicates.sort_values(by='Org Defined ID')

    # Convert DataFrame to HTML
    df_string = sorted_duplicates.to_html(index=False)
            
    if (df_string != "") and (not sorted_duplicates.empty):
        # Print the non-unique elements sorted by 'Org Defined ID', without the index
        print("Non-unique elements sorted by 'Org Defined ID':")
        print(sorted_duplicates.to_string(index=False))
        if SEND_EMAIL:
            if TESTING: 
                cc_email = to_email

            subject_email="Please check and remove duplicates in Brightspace classes"
            body_email="Hello Office, <br><br>" + \
                "I ran a script today, and the following students are registered in one or more classes in BrightSpace (BS). Please check BS (Classlists) and remove duplicates. Thank you.<br><br>" \
                    + df_string + "<br><br>Sincerely, <br>Ramzan Khuwaja"

            send_email(to_email, cc_email, subject_email, body_email)

        return False
    else: 
        print("No duplicates found in Brightspace classes - checked via Class Lists")
        return True


def FindDupStudentsInBSViaAttendanceGrades (target_dir, column_name): 
    # List to store each DataFrame
    dfs = []

    # Loop through each file in the directory
    for filename in os.listdir(target_dir):
        if filename.endswith('.csv'):
            file_path = os.path.join(target_dir, filename)
            # Read the CSV file
            df = pd.read_csv(file_path)
            # Check if required columns exist
            if all(col in df.columns for col in [column_name, 'First Name', 'Last Name']):
                df["File Name"] = filename
                # Append the required columns to the list
                dfs.append(df[[column_name, 'First Name', 'Last Name', "File Name"]])

    # Concatenate all DataFrames in the list
    combined_df = pd.concat(dfs, ignore_index=True)
    #print(combined_df)

    # Find duplicates based on column_name
    duplicates = combined_df[combined_df.duplicated(subset=column_name, keep=False)]

    # Sort the DataFrame based on column_name
    sorted_duplicates = duplicates.sort_values(by=column_name)
    #print(sorted_duplicates.to_string(index=False))

    if not sorted_duplicates.empty:
        # Print the non-unique elements sorted by column_name, without the index
        print("Non-unique elements sorted by " + column_name + ": ")
        print(sorted_duplicates.to_string(index=False))
        
        df_string = sorted_duplicates.to_html(index=False)
        if SEND_EMAIL:
            if TESTING: 
                cc_email = to_email

            subject_email="Please check and remove duplicates in Brightspace classes"
            body_email="Hello Office, <br><br>" + \
                "I ran a script today, and the following students are registered in one or more classes in BrightSpace. Please check and remove duplicates. Thank you.<br><br>" \
                    + df_string + "<br><br>Sincerely, <br>Ramzan Khuwaja"

            send_email(to_email, cc_email, subject_email, body_email)
        return False
    else: 
        #print(sorted_duplicates.to_string(index=False))
        print("No duplicates found in Brightspace classes - checked via Attendance or Grades")
        return True
    
def GenerateStudentMap(campus):

    if campus == "VAU":
        class_list_dir_path = VAU_CLASS_LIST_DIR
        class_map_file = VAU_CLASS_MAP_FILE
        attendance_dir = VAU_ATTENDANCE_DIR
        grades_dir = VAU_GRADES_DIR
        student_map_file = VAU_STUDENT_MAP_FILE
    elif campus == "MAE":
        class_list_dir_path = MAE_CLASS_LIST_DIR
        class_map_file = MAE_CLASS_MAP_FILE
        attendance_dir = MAE_ATTENDANCE_DIR
        grades_dir = MAE_GRADES_DIR
        student_map_file = MAE_STUDENT_MAP_FILE
    else: 
        print("ERROR: Invalid campus name")
        return False

    # Set the maximum number of columns to display without truncation
    pd.set_option('display.max_columns', None)
    
    #create a dataframe - StudentMap
    columns = ['Org Defined ID', 'Student Full Name', 'Last Accessed', 'Class Code', 'Teacher Full Name', 'Teacher Email', 'Teacher Group', 'Attendance (%)', 'Parent Email', 'Start Week', 'Final Grade', 'Att Uptodate?']
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
        'Final Grade': float64,
        'Att Uptodate?': bool
    }
    StudentMap = StudentMap.astype(column_types)

    StudentMap = add_class_list_data(StudentMap, class_list_dir_path)
    #print(StudentMap)

    ClassMap = pd.read_csv(class_map_file)

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
    AttandanceData = get_attendance_data(attendance_dir)
    
    #Copy Attandance Data to  StudentMap
    for index, row in StudentMap.iterrows():
        student_id = row['Org Defined ID']
        
        # Check if student_id exists in AttandanceData
        # if student_id in AttandanceData['Org Defined ID'].values:
        if AttandanceData['Org Defined ID'].isin([student_id]).any():
            matching_row = AttandanceData[AttandanceData['Org Defined ID'] == student_id].iloc[0]
            
            # Copy data from AttandanceData to df_master
            StudentMap.at[index, 'Attendance (%)'] = matching_row['% Attendance']

            # Copy if attance is up to date

            current_som_week = past_two_weeks = 0
            current_som_week = THIS_WEEK_NUM
            past_two_weeks = str(current_som_week - 2)
            #print("====> " + past_two_weeks)

            if ("Lesson " + past_two_weeks) in AttandanceData.columns:
                #print("Lesson " + past_two_weeks + " column does exits!" + " Value: " + str(matching_row["Lesson " + past_two_weeks]))
                if matching_row["Lesson " + past_two_weeks] == None:
                    # Lookup the first value in the first row in column "Org Defined ID" in df_att
                    StudentMap.at[index, 'Att Uptodate?'] = False
                    #print("Lesson " + past_two_weeks + " - Data missing!")
                else: 
                    #print("Lesson " + past_two_weeks + " - Data present!")
                    StudentMap.at[index, 'Att Uptodate?'] = True
            else:
                #print("Lesson " + past_two_weeks + " column does NOT exits!")
                StudentMap.at[index, 'Att Uptodate?'] = False

    print("End - Copying Attandance data")

    print("Start - Copying Grade data")

    #Get Grade Data dataframe
    GradesData = get_grades_data(grades_dir)
    #print(GradesData)

    if GradesData.empty:
        print("ERROR: GradesData is empty")
    else:
        # #Copy Grades Data to  StudentMap
        for index, row in StudentMap.iterrows():
            student_id = row['Org Defined ID']
            
            # Check if student_id exists in GradesData
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
    StudentMap.to_csv(student_map_file, index=False)
    #print("StudentMap saved to " + utils.STUDENT_MAP_FILE)

    # Find and print rows with empty cells
    empty_rows = StudentMap[StudentMap.isnull().any(axis=1)]
    if empty_rows.empty:
        print("Good: No empty cells found in StudentMap!")
        return True
    else:
        print("StudentMap rows with empty cells:")
        print(empty_rows)  
        return False 
    

def FindMissingAttendance(campus):
    print("Start - FindMissingAttendance")

    if campus == "VAU":
        student_map_file = VAU_STUDENT_MAP_FILE
    elif campus == "MAE":
        student_map_file = MAE_STUDENT_MAP_FILE
    else: 
        print("ERROR: Invalid campus name")
        return False

    df_student_map = pd.read_csv(student_map_file)

    df1 = df_student_map[df_student_map["Att Uptodate?"] == False]
    #print(df1)

    df2 = pd.DataFrame(df1, columns=["Org Defined ID", "Student Full Name", "Class Code", "Teacher Email", "Teacher Full Name", "Att Uptodate?", "Start Week"])
    df2['Start Week'] = df2['Start Week'].astype(int)
    
    return df2


def email_att_missing_to_stakeholders(df_missing_attendance):
    print("Start - email_to_stakeholders")
    teacher_email = ""

    if SEND_EMAIL:

        for email in df_missing_attendance['Teacher Email'].unique():
            df1 = df_missing_attendance[df_missing_attendance['Teacher Email'] == email]

            teacher = df1["Teacher Full Name"].iloc[0]
            teacher_email = email

            df2 = pd.DataFrame(df1, columns=["Org Defined ID", "Student Full Name", "Class Code", "Att Uptodate?", "Start Week"])

            if TESTING: 
                to = to_email
                cc = ""
            else:
                to = teacher_email
                cc = cc_email

            subject_email="Please update your Brightspace class data"
            body_email="Hello " + teacher + ",<br><br>" + \
                    "Spirit of Math advises parents and students to access their class attendance and marks within a week after a class is completed.  <br><br> Our records show that the following of your students/classes have not been updated for the past two weeks!  Please update ASAP and keep the above practice for the rest of this school year.  <br>" \
                        + "No need to respond to this email, just make the applicable corrections.  Thank you.<br><br>" \
                        + df2.to_html(index=False) + "<br><br>Sincerely, <br>Ramzan Khuwaja<br><br>" \
                        + "P.S. Start Week = -1 means you have not added the start for this student in the Brightspace.  Please add, if missing.<br>"

            send_email(to, cc, subject_email, body_email)


def FindStrugglingStudents(campus):
    print("Start - FindStrugglingStudents")

    if campus == "VAU":
        student_map_file = VAU_STUDENT_MAP_FILE
    elif campus == "MAE":
        student_map_file = MAE_STUDENT_MAP_FILE
    else: 
        print("ERROR: Invalid campus name")
        return False

    df_student_map = pd.read_csv(student_map_file)

    df1 = df_student_map[df_student_map['Final Grade'] < GRADES_MIN_BAR]
    #print(df1)

    df2 = pd.DataFrame(df1, columns=["Org Defined ID", "Student Full Name", "Class Code", "Teacher Email", "Teacher Full Name", "Final Grade", "Start Week"])
    df2['Start Week'] = df2['Start Week'].astype(int)
    return df2

def FindHighHonoursStudents(campus):
    print("Start - FindStrugglingStudents")

    if campus == "VAU":
        student_map_file = VAU_STUDENT_MAP_FILE
    elif campus == "MAE":
        student_map_file = MAE_STUDENT_MAP_FILE
    else: 
        print("ERROR: Invalid campus name")
        return False

    df_student_map = pd.read_csv(student_map_file)

    df1 = df_student_map[df_student_map['Final Grade'] >= HIGH_HONOURS_MIN_BAR]
    #print(df1)

    df2 = pd.DataFrame(df1, columns=["Org Defined ID", "Student Full Name", "Class Code", "Teacher Email", "Teacher Full Name", "Final Grade", "Parent Email"])
    return df2

def FindNeedsToAttendMoreRegularly(campus):
    print("Start - FindNeedsToAttendMoreRegularly")

    if campus == "VAU":
        student_map_file = VAU_STUDENT_MAP_FILE
    elif campus == "MAE":
        student_map_file = MAE_STUDENT_MAP_FILE
    else: 
        print("ERROR: Invalid campus name")
        return False

    df_student_map = pd.read_csv(student_map_file)

    df1 = df_student_map[df_student_map['Attendance (%)'] < ATTENDANCE_MIN_BAR]
    #print(df1)

    df2 = pd.DataFrame(df1, columns=["Org Defined ID", "Student Full Name", "Class Code", "Teacher Email", "Teacher Full Name", "Attendance (%)", "Parent Email"])
    return df2


def export_struggling_students_to_excel(df_struggling_students, campus):
    if PRINT_REPORT:

        if campus == "VAU":
            grades_dir = VAU_REPORT_DIRECTORY + "\\VAU_StrugglingStudents-"
        elif campus == "MAE":
            grades_dir = MAE_REPORT_DIRECTORY + "\\MAE_StrugglingStudents-"
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
        condition = df_struggling_students['Final Grade'] < GRADES_MIN_BAR

        # Apply the condition and then sort
        df_struggling_students = df_struggling_students[condition].sort_values(
            by=["Teacher Full Name", "Class Code", "Student Full Name", "Final Grade"], 
            ascending=[True, True, True, True]
        )

        df_struggling_students.to_excel(output_path, index=False)
        print("MAE_StrugglingStudents exported to " + output_path)


def RemindForBSLogin(campus):
    print("Start - RemindForBSLogin")

    if campus == "VAU":
        student_map_file = VAU_STUDENT_MAP_FILE
    elif campus == "MAE":
        student_map_file = MAE_STUDENT_MAP_FILE
    else: 
        print("ERROR: Invalid campus name")
        return False

    df_student_map = pd.read_csv(student_map_file)

    targeted_df = df_student_map[df_student_map['Last Accessed'].apply (lambda x: is_within_days(x, NOT_LOGGED_IN_SINCE))]

    # Define the columns you want to keep
    columns_to_keep = ["Student Full Name", "Last Accessed", "Class Code", "Teacher Full Name", "Teacher Email", "Teacher Group", "Parent Email"]
    targeted_df = targeted_df[columns_to_keep]
    return targeted_df


def export_student_reminder_to_excel(df_remind_students, campus):
    if PRINT_REPORT:

        if campus == "VAU":
            report_dir = VAU_REPORT_DIRECTORY + "\\VAU_RemindForBSLogin-"
        elif campus == "MAE":
            report_dir = MAE_REPORT_DIRECTORY + "\\MAE_RemindForBSLogin-"
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
        print("RemindStudents exported to " + output_path)


def export_high_honours_students_to_excel(df_high_honours_students, campus):
    if PRINT_REPORT:

        if campus == "VAU":
            grades_dir = VAU_REPORT_DIRECTORY + "\\VAU_HighHonours-"
        elif campus == "MAE":
            grades_dir = MAE_REPORT_DIRECTORY + "\\MAE_HighHonours-"
        else: 
            print("ERROR: Invalid campus name")
            return False

        # Get today's date
        today = datetime.now()

        # Format the date as a string
        date_string = today.strftime("%B %d, %Y")  # Format (e.g.,): November 23, 2023

        # Specify the output path
        output_path = grades_dir + date_string + ".xlsx"

        df2 = pd.DataFrame(df_high_honours_students, columns=["Teacher Full Name", "Class Code", "Student Full Name", "Final Grade", "Parent Email"])


        # Example condition: selecting students with a final grade less than 60
        condition = df2['Final Grade'] >= HIGH_HONOURS_MIN_BAR

        # Apply the condition and then sort
        df2 = df2[condition].sort_values(
            by=["Teacher Full Name", "Class Code", "Student Full Name", "Final Grade"], 
            ascending=[True, True, True, True]
        )

        df2.to_excel(output_path, index=False)
        print(campus + " - HighHonours exported to " + output_path)

def export_students_to_attend_more_to_excel(df_remind_students, campus):
    if PRINT_REPORT:

        if campus == "VAU":
            report_dir = VAU_REPORT_DIRECTORY + "\\VAU_NeedsToAttendMoreRegularly-"  
        elif campus == "MAE":
            report_dir = MAE_REPORT_DIRECTORY + "\\MAE_NeedsToAttendMoreRegularly-"
        else: 
            print("ERROR: Invalid campus name")
            return False

        # Get today's date
        today = datetime.now()

        # Format the date as a string
        date_string = today.strftime("%B %d, %Y")  # Format (e.g.,): November 23, 2023

        # Specify the output path
        output_path = report_dir + date_string + ".xlsx"

        df2 = pd.DataFrame(df_remind_students, columns=["Teacher Full Name", "Class Code", "Student Full Name", "Attendance (%)", "Parent Email"])

        df2 = df2.sort_values(
            by=["Teacher Full Name", "Class Code", "Student Full Name", "Attendance (%)"], 
            ascending=[True, True, True, True]
        )

        df2.to_excel(output_path, index=False)
        print("RemindStudents exported to " + output_path)