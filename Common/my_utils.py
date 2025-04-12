import os
import re
import time
import numpy as np
import pandas as pd
import openpyxl
from bs4 import BeautifulSoup
from numpy import float64, int64
import win32com.client as email_client
from datetime import datetime, timedelta
import glob
import pdfkit

try:
    import pdfkit
except ImportError:
    print("Warning: pdfkit module not found. PDF functionality will not be available.")
    print("To install, run: pip install pdfkit")
    pdfkit = None

# Debug flag to control which paths to use
#  <======  Be CAREFUL with this switch!!!!!!!!!!!!!
#   use only when doing a new run with 3 files only

DEBUG = False  # Set to True to use debugging paths, False for production paths

CAMPUS = to_email = cc_email = body_email = subject_email = ""

TESTING = True    #  <======  Be CAREFUL with this switch!!!!!!!!!!!!!
THIS_WEEK_NUM = 28 #  <======  Change this every week!!!!!!!!!!!!!

SEND_EMAIL = True
PRINT_REPORT = True
SEND_SUMMARY = True
GRADES_MIN_BAR = int(50) # Scoring less than 50%!
HIGH_HONOURS_MIN_BAR = int(90) # Scoring 90% or higher!
NOT_LOGGED_IN_SINCE = int(14) # Not logged in since last 2 weeks!
ATTENDANCE_MIN_BAR = int(80) # Min attendance required (in %)


if DEBUG:
    VAU_CLASS_MAP_FILE  = r'C:\Users\ramza\My Drive\Frequent Files\Fun Projects\ProgressMonitoring\Code\Common\VAUClassMap2024-25.csv'
    MAE_CLASS_MAP_FILE  = r'C:\Users\ramza\My Drive\Frequent Files\Fun Projects\ProgressMonitoring\Code\Common\MAEClassMap2024-25.csv'
    VAU_STUDENT_MAP_FILE = r'C:\Users\ramza\My Drive\Frequent Files\Fun Projects\ProgressMonitoring\Code\Common\VAUStudentMap2024-25.csv'
    MAE_STUDENT_MAP_FILE = r'C:\Users\ramza\My Drive\Frequent Files\Fun Projects\ProgressMonitoring\Code\Common\MAEStudentMap2024-25.csv'
    VAU_ATTENDANCE_DIR = r'C:\Users\ramza\My Drive\Frequent Files\Fun Projects\ProgressMonitoring\Data\Debugging\VAU\Attendance'
    MAE_ATTENDANCE_DIR = r'C:\Users\ramza\My Drive\Frequent Files\Fun Projects\ProgressMonitoring\Data\Debugging\MAE\Attendance'
    VAU_CLASS_LIST_DIR = r'C:\Users\ramza\My Drive\Frequent Files\Fun Projects\ProgressMonitoring\Data\Debugging\VAU\ClassList'
    MAE_CLASS_LIST_DIR = r'C:\Users\ramza\My Drive\Frequent Files\Fun Projects\ProgressMonitoring\Data\Debugging\MAE\ClassList'
    VAU_GRADES_DIR = r'C:\Users\ramza\My Drive\Frequent Files\Fun Projects\ProgressMonitoring\Data\Debugging\VAU\Grades'
    MAE_GRADES_DIR = r'C:\Users\ramza\My Drive\Frequent Files\Fun Projects\ProgressMonitoring\Data\Debugging\MAE\Grades'
    VAU_REPORT_DIRECTORY = r"C:\Users\ramza\My Drive\Frequent Files\Fun Projects\ProgressMonitoring\Ready For Printing\VAU"
    MAE_REPORT_DIRECTORY = r"C:\Users\ramza\My Drive\Frequent Files\Fun Projects\ProgressMonitoring\Ready For Printing\MAE"
else:
    VAU_CLASS_MAP_FILE  = r'C:\Users\ramza\My Drive\Frequent Files\Fun Projects\ProgressMonitoring\Code\Common\VAUClassMap2024-25.csv'
    MAE_CLASS_MAP_FILE  = r'C:\Users\ramza\My Drive\Frequent Files\Fun Projects\ProgressMonitoring\Code\Common\MAEClassMap2024-25.csv'
    VAU_STUDENT_MAP_FILE = r'C:\Users\ramza\My Drive\Frequent Files\Fun Projects\ProgressMonitoring\Code\Common\VAUStudentMap2024-25.csv'
    MAE_STUDENT_MAP_FILE = r'C:\Users\ramza\My Drive\Frequent Files\Fun Projects\ProgressMonitoring\Code\Common\MAEStudentMap2024-25.csv'
    VAU_ATTENDANCE_DIR = r'C:\Users\ramza\My Drive\Frequent Files\Fun Projects\ProgressMonitoring\Data\VAU\Attendance'
    MAE_ATTENDANCE_DIR = r'C:\Users\ramza\My Drive\Frequent Files\Fun Projects\ProgressMonitoring\Data\MAE\Attendance'
    VAU_CLASS_LIST_DIR = r'C:\Users\ramza\My Drive\Frequent Files\Fun Projects\ProgressMonitoring\Data\VAU\ClassList'
    MAE_CLASS_LIST_DIR = r'C:\Users\ramza\My Drive\Frequent Files\Fun Projects\ProgressMonitoring\Data\MAE\ClassList'
    VAU_GRADES_DIR = r'C:\Users\ramza\My Drive\Frequent Files\Fun Projects\ProgressMonitoring\Data\VAU\Grades'
    MAE_GRADES_DIR = r'C:\Users\ramza\My Drive\Frequent Files\Fun Projects\ProgressMonitoring\Data\MAE\Grades'
    VAU_REPORT_DIRECTORY = r"C:\Users\ramza\My Drive\Frequent Files\Fun Projects\ProgressMonitoring\Ready For Printing\VAU"
    MAE_REPORT_DIRECTORY = r"C:\Users\ramza\My Drive\Frequent Files\Fun Projects\ProgressMonitoring\Ready For Printing\MAE"

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
    cleaned_str = ''.join(c for c in input_string if c.isdigit())

    while cleaned_str.startswith('0') and len(cleaned_str) > 1:
        cleaned_str = cleaned_str[1:]

    return cleaned_str
    
    #return result


# Function to clean a cell value
def clean_cell(cell_value):
    if isinstance(cell_value, str):
        cleaned_value = re.sub(r'^[^a-zA-Z0-9]+|[^a-zA-Z0-9]+$', '', cell_value)
        return cleaned_value
    else:
        return cell_value
    

def send_email(to, cc, subject, body):
    try:
        outlook = email_client.Dispatch("outlook.application")
        mail = outlook.CreateItem(0)  

        today = datetime.now()
        date_string = today.strftime("%B %d, %Y")  

        mail.To = to  
        mail.CC = cc  
        mail.Subject = CAMPUS + ": " + date_string + ": " + subject  
        mail.HTMLBody = body  

        mail.Send()
        time.sleep(5)

    except Exception as e:
        print(f"An error occurred while sending the email (e.g., outlook is not running): {e}")

def create_pdf_from_html(html, output_path):
    config = pdfkit.configuration(wkhtmltopdf='C:/Program Files/wkhtmltopdf/bin/wkhtmltopdf.exe')

    options = {
        'enable-local-file-access': '',
        'quiet': ''
    }

    try:
        pdfkit.from_string(html, output_path, configuration=config, options=options)
        print(f"PDF saved at {output_path}")
    except IOError as e:
        print(f"An error occurred: {e}")
    except Exception as e:
        print(f"An unexpected error occurred: {e}")

# Function to convert date format
def convert_date_format(date_str):
    if not pd.isna(date_str):
        date_object = datetime.strptime(date_str, '%b %d, %Y %I:%M %p')
        new_date_str = date_object.strftime('%b %d, %Y')
    else: 
        new_date_str = str(datetime.now().strftime('%b %d, %Y'))
    return new_date_str

def is_within_days(date_str, days):
    date_object = datetime.strptime(date_str, '%b %d, %Y')
    fourteen_days_ago = datetime.now() - timedelta(days=days)
    return date_object < fourteen_days_ago

# Generate HTML code for head and body start
def generate_html_head_and_body_start():
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
        numerator = row['Calculated Final Grade Numerator']
        denominator = row['Calculated Final Grade Denominator']

        numerator = 0 if pd.isna(numerator) else numerator
        denominator = 1 if pd.isna(denominator) else denominator  

        if denominator == 0:
            final_grade = 0
        else:
            final_grade = int(100 * numerator / denominator)
    except ZeroDivisionError:
        final_grade = 0
    except Exception as e:
        print(f"WARNING - Error occurred: {e}")
        final_grade = 0

    return final_grade


# Read each HTML file in this directory using pandas library

def add_class_list_data(master_df, class_list_dir_path):
    """Add data from class list HTML files to the master DataFrame."""
    print(f"Processing files in directory: {class_list_dir_path}\n")
    
    if not os.path.exists(class_list_dir_path):
        print(f"ERROR: Class list directory not found: {class_list_dir_path}")
        return master_df
    
    file_count = 0
    
    for filename in glob.glob(os.path.join(class_list_dir_path, "*.html")):
        try:
            with open(filename, 'r', encoding='utf-8') as f:
                soup = BeautifulSoup(f, 'html.parser')
            
            class_code = get_class_code_from_html(soup)
            tables = pd.read_html(filename)

            student_table = None
            for i, table in enumerate(tables):
                table.columns = [str(col) if isinstance(col, int) else col for col in table.columns]
                
                table_str = table.astype(str).values
                table_str_flat = ' '.join(table_str.flatten())
                
                if any(keyword in table_str_flat.lower() for keyword in ['role', 'student', 'username', 'org defined id']):
                    if len(table.columns) >= 6:
                        student_table = table
                        break

            if student_table is not None:
                role_col = None
                for col in student_table.columns:
                    col_values = student_table[col].astype(str)
                    col_values_flat = ' '.join(col_values.dropna())
                    if any(keyword in col_values_flat.lower() for keyword in ['role', 'student']):
                        role_col = col
                        break
                
                if role_col is not None:
                    id_col = None
                    for col in student_table.columns:
                        col_values = student_table[col].astype(str)
                        if any('org defined id' in val.lower() for val in col_values):
                            id_col = col
                            break
                    
                    if id_col is None:
                        for col in student_table.columns:
                            if not student_table[col].isna().all():
                                id_col = col
                                break
                    
                    name_col = student_table.columns[2] if len(student_table.columns) > 2 else None
                    last_accessed_col = student_table.columns[-1]
                    
                    student_df = student_table[student_table[role_col].astype(str).str.contains('Student', case=False, na=False)]
                    student_df = student_df[student_df[id_col].notna()]
                    
                    if not student_df.empty:
                        filtered_student_df = pd.DataFrame({
                            'Org Defined ID': student_df[id_col],
                            'Student Full Name': student_df[name_col],
                            'Last Accessed': student_df[last_accessed_col]
                        })
                        
                        orig_len = len(filtered_student_df)
                        filtered_student_df = filtered_student_df.dropna(subset=['Org Defined ID'])
                        if orig_len != len(filtered_student_df):
                            print(f"Dropped {orig_len - len(filtered_student_df)} rows with NaN IDs")
                        
                        filtered_student_df['Org Defined ID'] = filtered_student_df['Org Defined ID'].astype(str).str.extract(r'(\d+)', expand=False)
                        filtered_student_df = filtered_student_df.dropna(subset=['Org Defined ID'])
                        filtered_student_df['Org Defined ID'] = filtered_student_df['Org Defined ID'].astype(np.int64)
                        filtered_student_df['Org Defined ID'] = filtered_student_df['Org Defined ID'].astype(str)

                        default_date = 'Sep 01, 2024 5:50 PM'
                        filtered_student_df['Last Accessed'] = filtered_student_df['Last Accessed'].apply(lambda x: default_date if pd.isna(x) else x)
                        filtered_student_df['Last Accessed'] = filtered_student_df['Last Accessed'].apply(convert_date_format)
                        filtered_student_df['Class Code'] = class_code
                        
                        print(f"Adding {len(filtered_student_df)} students from {os.path.basename(filename)}")
                        master_df = pd.concat([master_df, filtered_student_df], axis=0)
                        file_count += 1
                else:
                    print(f"Warning: Could not find Role column in {filename}")
            else:
                print(f"Warning: Could not find student table in {filename}")
        except Exception as e:
            print(f"Warning: Error processing {filename}: {str(e)}")
            continue

    master_df = master_df.reset_index(drop=True)
    print(f"\nProcessed {file_count} files successfully")
    print(f"Final master DataFrame has {len(master_df)} rows")
    return master_df

def get_attendance_data(attendance_dir):
    """Get attendance data from CSV files."""
    if not os.path.exists(attendance_dir):
        print(f"ERROR: Attendance directory not found: {attendance_dir}")
        return pd.DataFrame()

    all_attendance = []
    
    for filename in glob.glob(os.path.join(attendance_dir, "*.csv")):
        try:
            df = pd.read_csv(filename)
            
            if 'Org Defined ID' in df.columns:
                df['Org Defined ID'] = df['Org Defined ID'].astype(str).str.extract(r'(\d+)', expand=False)
                df = df.dropna(subset=['Org Defined ID'])
                df['Org Defined ID'] = df['Org Defined ID'].astype(np.int64)
                df['Org Defined ID'] = df['Org Defined ID'].astype(str)
                
                class_code = os.path.splitext(os.path.basename(filename))[0]
                df['Class Code'] = class_code
                
                all_attendance.append(df)
            else:
                print(f"Warning: No 'Org Defined ID' column in {filename}")
                
        except Exception as e:
            print(f"Warning: Error processing {filename}: {str(e)}")
            continue
    
    if not all_attendance:
        print("No attendance data found")
        return pd.DataFrame()
    
    attendance_df = pd.concat(all_attendance, ignore_index=True)
    print(f"Found attendance data for {len(attendance_df)} students")
    return attendance_df

def get_grades_data(grades_dir):
    """Get grades data from CSV files."""
    if not os.path.exists(grades_dir):
        print(f"ERROR: Grades directory not found: {grades_dir}")
        return pd.DataFrame()

    all_grades = []
    
    for filename in glob.glob(os.path.join(grades_dir, "*.csv")):
        try:
            df = pd.read_csv(filename)
            
            if 'OrgDefinedId' in df.columns:
                df['OrgDefinedId'] = df['OrgDefinedId'].astype(str).str.extract(r'(\d+)', expand=False)
                df = df.dropna(subset=['OrgDefinedId'])
                df['OrgDefinedId'] = df['OrgDefinedId'].astype(np.int64)
                df['OrgDefinedId'] = df['OrgDefinedId'].astype(str)
                
                class_code = os.path.splitext(os.path.basename(filename))[0]
                df['Class Code'] = class_code
                
                start_week_col = next((col for col in df.columns if "Enrolment Start Week Points Grade" in col), None)
                if start_week_col:
                    df['Start Week'] = pd.to_numeric(df[start_week_col], errors='coerce').fillna(-1).astype('int64')
                else:
                    df['Start Week'] = -1
                
                df['Final Grade'] = df.apply(calculate_final_grade, axis=1)
                df['Parent Email'] = None
                
                all_grades.append(df)
            else:
                print(f"Warning: No 'OrgDefinedId' column in {filename}")
                
        except Exception as e:
            print(f"Warning: Error processing {filename}: {str(e)}")
            continue
    
    if not all_grades:
        print("No grades data found")
        return pd.DataFrame()
    
    grades_df = pd.concat(all_grades, ignore_index=True)
    print(f"Found grades data for {len(grades_df)} students")
    
    keep_cols = ['OrgDefinedId', 'Class Code', 'Parent Email', 'Start Week', 'Final Grade']
    grades_df = grades_df[keep_cols]
    
    return grades_df

def get_class_code_from_html(soup):
    """Extract class code from HTML file using multiple methods."""
    nav_link = soup.find('a', class_='d2l-navigation-s-link')
    if nav_link and 'SOMp' in nav_link.text:
        match = re.search(r'SOMp\d+[A-Za-z]+\d+[A-Za-z]+', nav_link.text)
        if match:
            return match.group(0)

    breadcrumb = soup.find('div', class_='d2l-navigation-s-main-wrapper')
    if breadcrumb and 'SOMp' in breadcrumb.text:
        match = re.search(r'SOMp\d+[A-Za-z]+\d+[A-Za-z]+', breadcrumb.text)
        if match:
            return match.group(0)

    title = soup.find('title')
    if title and 'Grade' in title.text:
        if 'Vaughan' in title.text:
            return 'SOMp2405Su0130ETVAU'  
        elif 'Markham' in title.text:
            return 'MAE'

    return 'VAU'  


def FindDupStudentsInBSViaClassList (BSdirectory): 

    pd.set_option('display.max_columns', None)  
    pd.set_option('display.max_rows', None)     
    pd.set_option('display.max_colwidth', None) 
    pd.set_option('display.width', None)        

    filtered_student_df = pd.DataFrame()

    os.chdir(BSdirectory)
    for filename in os.listdir(BSdirectory):
        if filename.endswith(".html"):
            try:
                with open(filename, 'r', encoding='utf-8') as file:
                    html_content = file.read()

                soup = BeautifulSoup(html_content, 'html.parser')

                class_code = ""
                
                title_tag = soup.find('title')
                if title_tag:
                    title_text = title_tag.get_text()
                    if 'Vaughan' in title_text:
                        class_code = 'VAU'
                
                nav_links = soup.find_all('a')
                for link in nav_links:
                    text = link.get_text()
                    if 'SOMp' in text:
                        match = re.search(r'SOMp\d+[A-Za-z]+\d+[A-Za-z]+', text)
                        if match:
                            class_code = match.group()
                            break
                
                breadcrumbs = soup.find_all(['div', 'span', 'a'])
                for crumb in breadcrumbs:
                    text = crumb.get_text()
                    if 'SOMp' in text:
                        match = re.search(r'SOMp\d+[A-Za-z]+\d+[A-Za-z]+', text)
                        if match:
                            class_code = match.group()
                            break
                
                if not class_code:
                    if 'SOMp' in html_content:
                        match = re.search(r'SOMp\d+[A-Za-z]+\d+[A-Za-z]+', html_content)
                        if match:
                            class_code = match.group()
                
                if not class_code:
                    class_code = 'VAU'  

                print(f"Found class code: {class_code}")

                tables = pd.read_html(filename)

                student_table = None
                for i, table in enumerate(tables):
                    table_str = table.astype(str).values
                    table_str_flat = ' '.join(table_str.flatten())
                    
                    if any(keyword in table_str_flat.lower() for keyword in ['role', 'student', 'username', 'org defined id']):
                        if len(table.columns) >= 6:  
                            student_table = table
                            print(f"Found student table at index {i}")
                            print(f"Columns: {table.columns.tolist()}")
                            break

                if student_table is not None:
                    role_col = None
                    for col in student_table.columns:
                        col_values = student_table[col].astype(str)
                        col_values_flat = ' '.join(col_values.dropna())
                        if any(keyword in col_values_flat.lower() for keyword in ['role', 'student']):
                            role_col = col
                            break
                    
                    if role_col is not None:
                        student_df = student_table[student_table[role_col].astype(str).str.contains('Student', case=False, na=False)]
                        
                        if not student_df.empty:
                            name_col = student_table.columns[2]
                            username_col = student_table.columns[3]
                            
                            student_df = student_df[[name_col, username_col]]
                            student_df.columns = ['Full Name', 'Username']
                            
                            student_df['Class Code'] = class_code
                            
                            filtered_student_df = pd.concat([filtered_student_df, student_df], axis=0)
                    else:
                        print(f"Warning: Could not find Role column in {filename}")
                else:
                    print(f"Warning: Could not find student table in {filename}")
                    
            except Exception as e:
                print(f"Warning: Error processing {filename}: {str(e)}")
                continue

    if filtered_student_df.empty:
        print("No student data found in any of the HTML files.")
        return False

    filtered_student_df = filtered_student_df.reset_index(drop=True)

    duplicates = filtered_student_df[filtered_student_df.duplicated(['Full Name'], keep=False)]
    
    if not duplicates.empty:
        print("\nDuplicate students found:")
        print(duplicates.sort_values('Full Name'))
        return False
    
    return True


def FindDupStudentsInBSViaAttendanceGrades (target_dir, column_name): 
    if not os.path.exists(target_dir):
        print(f"Directory not found: {target_dir}")
        return True
        
    dfs = []
    csv_files = [f for f in os.listdir(target_dir) if f.endswith('.csv')]
    
    if not csv_files:
        print(f"No CSV files found in directory: {target_dir}")
        return True

    for filename in csv_files:
        file_path = os.path.join(target_dir, filename)
        try:
            # First try to read as normal CSV with header
            df = pd.read_csv(file_path, quotechar='"', encoding='utf-8')
            
            # Handle attendance files
            if 'Org Defined ID' in df.columns:
                if column_name == 'OrgDefinedId':
                    df[column_name] = df['Org Defined ID']
                if all(col in df.columns for col in ['First Name', 'Last Name']):
                    df["File Name"] = filename
                    dfs.append(df[[column_name, 'First Name', 'Last Name', "File Name"]])
                    continue
            
            # If normal read fails or columns missing, try reading as grades file
            content = pd.read_csv(file_path, header=None)
            if content[0].astype(str).str.startswith('#').any():
                student_data = []
                for _, row in content.iterrows():
                    try:
                        # Split first column by comma and clean up
                        fields = str(row[0]).split(',')
                        student_id = fields[0].strip('#') if fields[0].startswith('#') else None
                        if student_id and student_id.isdigit():
                            student_data.append({
                                column_name: student_id,
                                'First Name': 'Student',  # Placeholder
                                'Last Name': str(student_id),  # Use ID as last name
                                'File Name': filename
                            })
                    except:
                        continue
                
                if student_data:
                    df_students = pd.DataFrame(student_data)
                    dfs.append(df_students)
                    continue
            
        except Exception as e:
            print(f"Warning: Error processing {filename}: {str(e)}")
            continue

    if not dfs:
        print(f"No files with required columns found in directory: {target_dir}")
        return True

    combined_df = pd.concat(dfs, ignore_index=True)
    duplicates = combined_df[combined_df.duplicated(subset=column_name, keep=False)]

    sorted_duplicates = duplicates.sort_values(by=column_name)
    if not sorted_duplicates.empty:
        print("\nFound duplicate student IDs:")
        print(sorted_duplicates.to_string(index=False))
        
        df_string = sorted_duplicates.to_html(index=False)
        if SEND_EMAIL:
            if TESTING: 
                cc_email = to_email

            subject_email="Please check and remove duplicates in Brightspace classes"
            body_email="Hello Office, <br><br>" + \
                "I ran a report today, and the following students are registered in one or more classes in BrightSpace. Please check and remove duplicates. Thank you.<br><br>" \
                    + df_string + "<br><br>Sincerely, <br>Ramzan Khuwaja"

            send_email(to_email, cc_email, subject_email, body_email)
        return False
    else: 
        print("No duplicates found in Brightspace classes - checked via Attendance or Grades")
        return True


def GenerateStudentMap(campus):
    """Generate student map by combining data from various sources."""
    if campus == "VAU":
        class_list_dir_path = VAU_CLASS_LIST_DIR
        class_map_file = VAU_CLASS_MAP_FILE
        attendance_dir = VAU_ATTENDANCE_DIR
        grades_dir = VAU_GRADES_DIR
        student_map_file = VAU_STUDENT_MAP_FILE
        report_dir = VAU_REPORT_DIRECTORY
    elif campus == "MAE":
        class_list_dir_path = MAE_CLASS_LIST_DIR
        class_map_file = MAE_CLASS_MAP_FILE
        attendance_dir = MAE_ATTENDANCE_DIR
        grades_dir = MAE_GRADES_DIR
        student_map_file = MAE_STUDENT_MAP_FILE
        report_dir = MAE_REPORT_DIRECTORY
    else: 
        print("ERROR: Invalid campus name")
        return False

    pd.set_option('display.max_columns', None)
    
    columns = ['Org Defined ID', 'Student Full Name', 'Last Accessed', 'Class Code', 'Teacher Full Name', 'Teacher Email', 'Teacher Group', 'Attendance (%)', 'Parent Email', 'Start Week', 'Final Grade', 'Att Uptodate?']
    StudentMap = pd.DataFrame(columns=columns)

    column_types = {
        'Org Defined ID': np.int64,
        'Student Full Name': str,
        'Last Accessed': str,
        'Class Code': str,
        'Teacher Full Name': str,
        'Teacher Email': str,
        'Teacher Group': str,
        'Attendance (%)': str,
        'Parent Email': str,
        'Start Week': np.int64,
        'Final Grade': np.float64,
        'Att Uptodate?': bool
    }
    StudentMap = StudentMap.astype(column_types)

    print("\nStart - Adding class list data")
    StudentMap = add_class_list_data(StudentMap, class_list_dir_path)
    if len(StudentMap) == 0:
        print("ERROR: No data was added from class lists")
        return False
    print("End - Adding class list data")

    print("\nStart - Reading class map")
    if not os.path.exists(class_map_file):
        print(f"ERROR: Class map file not found: {class_map_file}")
        return False
    ClassMap = pd.read_csv(class_map_file)
    print(f"Read {len(ClassMap)} entries from class map")
    print("End - Reading class map")

    print("\nStart - Copying StudentMap data")
    teacher_matches = 0
    for index, row in StudentMap.iterrows():
        class_code = row['Class Code']
        matching_row = None
        
        if class_code in ClassMap['Class Code'].values:
            matching_row = ClassMap[ClassMap['Class Code'] == class_code].iloc[0]
            
            StudentMap.at[index, 'Teacher Full Name'] = matching_row['Teacher Full Name']
            StudentMap.at[index, 'Teacher Email'] = matching_row['Teacher Email']
            StudentMap.at[index, 'Teacher Group'] = matching_row['Teacher Group']
            teacher_matches += 1

    print(f"Found teacher info for {teacher_matches} students")
    print("End - Copying StudentMap data")

    print("\nStart - Getting attendance data")
    AttandanceData = get_attendance_data(attendance_dir)
    print("End - Getting attendance data")

    print("\nStart - Copying attendance data")
    attendance_matches = 0
    for index, row in StudentMap.iterrows():
        student_id = row['Org Defined ID']
        
        if AttandanceData['Org Defined ID'].isin([student_id]).any():
            matching_row = AttandanceData[AttandanceData['Org Defined ID'] == student_id].iloc[0]
            
            StudentMap.at[index, 'Attendance (%)'] = matching_row['% Attendance']
            attendance_matches += 1

            current_som_week = past_two_weeks = 0
            current_som_week = THIS_WEEK_NUM
            past_two_weeks = str(current_som_week - 2)
            lesson_col = "Lesson " + past_two_weeks

            if lesson_col in AttandanceData.columns:
                value = matching_row[lesson_col]
                # Check if the value is missing or not recorded
                if pd.isna(value) or value == '-' or value == '':
                    StudentMap.at[index, 'Att Uptodate?'] = False
                else: 
                    StudentMap.at[index, 'Att Uptodate?'] = True
            else:
                StudentMap.at[index, 'Att Uptodate?'] = False

    print(f"Found attendance records for {attendance_matches} students")
    print("End - Copying attendance data")

    print("\nStart - Getting grade data")
    GradesData = get_grades_data(grades_dir)
    print("End - Getting grade data")

    print("\nStart - Copying grade data")
    grade_matches = 0
    for index, row in StudentMap.iterrows():
        student_id = row['Org Defined ID']
        
        if student_id in GradesData['OrgDefinedId'].values:
            matching_row = GradesData[GradesData['OrgDefinedId'] == student_id].iloc[0]
            
            StudentMap.at[index, 'Parent Email'] = matching_row['Parent Email']
            StudentMap.at[index, 'Final Grade'] = matching_row['Final Grade']
            if pd.isnull(matching_row['Start Week']):
                StudentMap.at[index, 'Start Week'] = -1
            else:
                StudentMap.at[index, 'Start Week'] = matching_row['Start Week']
            grade_matches += 1

    print(f"Found grade records for {grade_matches} students")
    print("End - Copying grade data")

    print("Start - Saving student map")
    try:
        # Save to the same directory as class map file
        output_dir = os.path.dirname(student_map_file)
        os.makedirs(output_dir, exist_ok=True)
        
        # Save directly to the final file
        StudentMap.to_csv(student_map_file, index=False)
        print(f"Saved {len(StudentMap)} students to {student_map_file}")
        print("End - Saving student map\n")
        
        # Check for missing data
        missing_data = []
        if StudentMap['Parent Email'].isna().any():
            missing_data.append('Parent Email')
        if StudentMap['Start Week'].isna().any():
            missing_data.append('Start Week')
        if StudentMap['Final Grade'].isna().any():
            missing_data.append('Final Grade')
        if StudentMap['Attendance (%)'].isna().any():
            missing_data.append('Attendance')
            
        if missing_data:
            print(f"\nMissing data in columns: {', '.join(missing_data)}")
            if len(missing_data) == 1 and missing_data[0] == 'Parent Email':
                print("\nOnly Parent Email is missing, which is expected")
                return True
            return False 
        return True
        
    except Exception as e:
        print(f"An error occurred during GenerateStudentMap: {str(e)}")
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

            df2 = pd.DataFrame(df1, columns=["Org Defined ID", "Student Full Name", "Class Code", "Att Uptodate?"])

            if TESTING: 
                to = to_email
                cc = ""
            else:
                to = teacher_email
                cc = cc_email

            subject_email="Please update your Brightspace class data"
            body_email="Hello " + teacher + ",<br><br>" + \
                    "Spirit of Math advises parents and students to access their class attendance and marks within a week after a class is completed.  <br><br> Our records show that the following of your students/classes have not been updated for the past two weeks!  Please update ASAP and keep the above practice for the rest of this school year.  <br><br>" \
                        + "No need to respond to this email, just make the applicable corrections.  Thank you.<br><br>" \
                        + df2.to_html(index=False) + "<br><br>Sincerely, <br>Ramzan Khuwaja<br><br>" 

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

    if 'Start Week' not in df_student_map.columns:
        print("ERROR: 'Start Week' column not found in the student map file.")
        return False

    df1 = df_student_map[df_student_map['Final Grade'] < GRADES_MIN_BAR]
    df2 = pd.DataFrame(df1, columns=["Org Defined ID", "Student Full Name", "Class Code", "Teacher Email", "Teacher Full Name", "Final Grade"])
    
    if 'Start Week' in df2.columns:
        df2['Start Week'] = df2['Start Week'].astype(int)
    else:
        print("WARNING: 'Start Week' column is missing in the filtered DataFrame.")

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

        today = datetime.now()
        date_string = today.strftime("%B %d, %Y")  

        output_path = grades_dir + date_string + ".xlsx"

        condition = df_struggling_students['Final Grade'] < GRADES_MIN_BAR

        df_struggling_students = df_struggling_students[condition].sort_values(
            by=["Teacher Full Name", "Class Code", "Student Full Name", "Final Grade"], 
            ascending=[True, True, True, True]
        )

        df_struggling_students.to_excel(output_path, sheet_name='Details',index=False)

        SummaryOfStrugglingStudents(output_path)

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

    targeted_df = df_student_map[df_student_map["Last Accessed"].apply (lambda x: is_within_days(x, NOT_LOGGED_IN_SINCE))]

    columns_to_keep = ["Student Full Name", "Last Accessed", "Class Code", "Teacher Email", "Teacher Full Name", "Teacher Group", "Parent Email"]
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

        today = datetime.now()
        date_string = today.strftime("%B %d, %Y")  

        output_path = report_dir + date_string + ".xlsx"

        df2 = pd.DataFrame(df_remind_students, columns=["Teacher Full Name", "Class Code", "Student Full Name", "Last Accessed", "Parent Email"])

        df2 = df2.sort_values(
            by=["Teacher Full Name", "Class Code", "Student Full Name", "Last Accessed"], 
            ascending=[True, True, True, True]
        )

        df2.to_excel(output_path, sheet_name='Details',index=False)
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

        today = datetime.now()
        date_string = today.strftime("%B %d, %Y")  

        output_path = grades_dir + date_string + ".xlsx"

        df2 = pd.DataFrame(df_high_honours_students, columns=["Teacher Full Name", "Class Code", "Student Full Name", "Final Grade", "Parent Email"])


        condition = df2['Final Grade'] >= HIGH_HONOURS_MIN_BAR

        df2 = df2[condition].sort_values(
            by=["Teacher Full Name", "Class Code", "Student Full Name", "Final Grade"], 
            ascending=[True, True, True, True]
        )

        df2.to_excel(output_path, sheet_name='Details', index=False)
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

        today = datetime.now()
        date_string = today.strftime("%B %d, %Y")  

        output_path = report_dir + date_string + ".xlsx"

        df2 = pd.DataFrame(df_remind_students, columns=["Teacher Full Name", "Class Code", "Student Full Name", "Attendance (%)", "Parent Email"])

        df2 = df2.sort_values(
            by=["Teacher Full Name", "Class Code", "Student Full Name", "Attendance (%)"], 
            ascending=[True, True, True, True]
        )

        df2.to_excel(output_path, sheet_name='Details', index=False)
        print("RemindStudents exported to " + output_path)


def SummaryOfStrugglingStudents(output_path):
    print("Start - SummaryOfStrugglingStudents")
   
    if CAMPUS == "VAU":
        student_map_file = VAU_STUDENT_MAP_FILE
    elif CAMPUS == "MAE":
        student_map_file = MAE_STUDENT_MAP_FILE
    else: 
        print("ERROR: Invalid campus name")
        return

    df_student_map = pd.read_csv(student_map_file)

    result = df_student_map.groupby('Teacher Full Name').apply(calculate_ranges).reset_index()

    result_sorted = result.sort_values(by='Total Students', ascending=False) if 'Total Students' in result.columns else result

    blank_row = pd.DataFrame(np.nan, index=[0], columns=result_sorted.columns)

    totals = result_sorted.sum(numeric_only=True)
    
    totals_df = pd.DataFrame([["TOTAL"] + totals.tolist()], columns=result_sorted.columns)

    result_with_summary = pd.concat([result_sorted, blank_row, totals_df], ignore_index=True)

    print(result_with_summary.to_string(index=False))

    with pd.ExcelWriter(output_path, engine='openpyxl', mode='a') as writer:
        result_with_summary.to_excel(writer, sheet_name='Summary', index=False)

    print("End - SummaryOfStrugglingStudents")

    return result_with_summary



def calculate_ranges(group):
    thresholds = [10, 20, 30, 40, 50]
    column_names = ['1 to 10%', '11 to 20%', '21 to 30%', '31 to 40%', '41 to 50%']

    counts = [0] * len(thresholds)
    total_students = 0  

    for i, t in enumerate(thresholds):
        if i == 0:
            counts[i] = (group['Final Grade'] < t).sum()
        else:
            counts[i] = (group['Final Grade'] < t).sum() - (group['Final Grade'] < thresholds[i-1]).sum()

        total_students += counts[i]
    
    return pd.Series(counts + [total_students], index=column_names + ['Total Students'])
