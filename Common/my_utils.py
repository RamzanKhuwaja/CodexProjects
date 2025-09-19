import os
import re
import time
from datetime import datetime, timedelta
from typing import Iterable, Optional, Sequence

import glob
import numpy as np
import openpyxl
import pandas as pd
from bs4 import BeautifulSoup
import win32com.client as email_client

try:
    import pdfkit
except ImportError:
    print("Warning: pdfkit module not found. PDF functionality will not be available.")
    print("To install, run: pip install pdfkit")
    pdfkit = None

# Debug flag to control which paths to use
#  <======  Be CAREFUL with this switch!!!!!!!!!!!!!
#   use only when doing a new run with 3 files only
DEBUG = False  #  <======  Be CAREFUL with this switch!!!!!!!!!!!!!
              # Set to True to use debugging paths, False for production paths
TESTING = True    #  <======  Be CAREFUL with this switch!!!!!!!!!!!!!
                  #  This is NOR DEBUGGING!  This uses all data before sending to teachers
THIS_WEEK_NUM = 28 #  <======  Change this every week!!!!!!!!!!!!!

SEND_EMAIL = True
PRINT_REPORT = True


# ======  Following Don't Change Often!

GRADES_MIN_BAR = int(50) # Scoring less than 50%!
HIGH_HONOURS_MIN_BAR = int(90) # Scoring 90% or higher!
NOT_LOGGED_IN_SINCE = int(14) # Not logged in since last 2 weeks!
ATTENDANCE_MIN_BAR = int(80) # Min attendance required (in %)

CAMPUS = to_email = cc_email = body_email = subject_email = ""

SUPPORTED_DATE_FORMATS = [
    "%b %d, %Y %I:%M %p",
    "%b %d, %Y",
    "%Y-%m-%d %H:%M:%S",
    "%Y-%m-%d",
    "%Y/%m/%d %H:%M",
    "%d-%b-%Y %H:%M",
    "%m/%d/%Y %I:%M %p",
]

CLASS_CODE_REGEX = re.compile(r"(?:SOMp|MAE)\w+", re.IGNORECASE)

_WARNED_MESSAGES: set[tuple[str, str]] = set()


def warn_once(level: str, message: str) -> None:
    key = (level, message)
    if key not in _WARNED_MESSAGES:
        print(f"{level}: {message}")
        _WARNED_MESSAGES.add(key)



def normalize(value: object) -> str:
    return str(value).strip().lower()



def find_first_matching_column(df: pd.DataFrame, candidates: Sequence[str]) -> Optional[str]:
    for col in df.columns:
        if any(keyword in normalize(col) for keyword in candidates):
            return col
    return None



def parse_datetime(value: object, context: str = "") -> Optional[datetime]:
    if pd.isna(value):
        return None
    if isinstance(value, datetime):
        return value
    text = str(value).strip()
    if not text or text.lower() in {"nan", "none", "nat"}:
        return None
    for fmt in SUPPORTED_DATE_FORMATS:
        try:
            return datetime.strptime(text, fmt)
        except ValueError:
            continue
    warn_once("WARNING", f"Unrecognized date format '{text}'{f' while processing {context}' if context else ''}")
    return None


def load_student_map(campus: str) -> pd.DataFrame:
    campus = campus.upper() if isinstance(campus, str) else campus
    mapping = {"VAU": VAU_STUDENT_MAP_FILE, "MAE": MAE_STUDENT_MAP_FILE}
    file_path = mapping.get(campus)
    if not file_path:
        print(f"ERROR: Invalid campus name '{campus}'")
        return pd.DataFrame()
    if not os.path.exists(file_path):
        print(f"ERROR: Student map file not found: {file_path}")
        return pd.DataFrame()
    try:
        return pd.read_csv(file_path)
    except Exception as exc:
        print(f"ERROR: Failed to read student map '{file_path}': {exc}")
        return pd.DataFrame()












# Resolve project root (two levels up from this file: ProgressMonitoring)



_THIS_DIR = os.path.abspath(os.path.dirname(__file__))



_PROJ_ROOT = os.path.abspath(os.path.join(_THIS_DIR, os.pardir, os.pardir))







# File locations relative to project root to avoid hardcoded absolute paths



VAU_CLASS_MAP_FILE  = os.path.join(_PROJ_ROOT, 'Code', 'Common', 'VAUClassMap2024-25.csv')



MAE_CLASS_MAP_FILE  = os.path.join(_PROJ_ROOT, 'Code', 'Common', 'MAEClassMap2024-25.csv')



VAU_STUDENT_MAP_FILE = os.path.join(_PROJ_ROOT, 'Code', 'Common', 'VAUStudentMap2024-25.csv')



MAE_STUDENT_MAP_FILE = os.path.join(_PROJ_ROOT, 'Code', 'Common', 'MAEStudentMap2024-25.csv')







if DEBUG:



    VAU_ATTENDANCE_DIR = os.path.join(_PROJ_ROOT, 'Data', 'Debugging', 'VAU', 'Attendance')



    MAE_ATTENDANCE_DIR = os.path.join(_PROJ_ROOT, 'Data', 'Debugging', 'MAE', 'Attendance')



    VAU_CLASS_LIST_DIR = os.path.join(_PROJ_ROOT, 'Data', 'Debugging', 'VAU', 'ClassList')



    MAE_CLASS_LIST_DIR = os.path.join(_PROJ_ROOT, 'Data', 'Debugging', 'MAE', 'ClassList')



    VAU_GRADES_DIR = os.path.join(_PROJ_ROOT, 'Data', 'Debugging', 'VAU', 'Grades')



    MAE_GRADES_DIR = os.path.join(_PROJ_ROOT, 'Data', 'Debugging', 'MAE', 'Grades')



else:



    VAU_ATTENDANCE_DIR = os.path.join(_PROJ_ROOT, 'Data', 'VAU', 'Attendance')



    MAE_ATTENDANCE_DIR = os.path.join(_PROJ_ROOT, 'Data', 'MAE', 'Attendance')



    VAU_CLASS_LIST_DIR = os.path.join(_PROJ_ROOT, 'Data', 'VAU', 'ClassList')



    MAE_CLASS_LIST_DIR = os.path.join(_PROJ_ROOT, 'Data', 'MAE', 'ClassList')



    VAU_GRADES_DIR = os.path.join(_PROJ_ROOT, 'Data', 'VAU', 'Grades')



    MAE_GRADES_DIR = os.path.join(_PROJ_ROOT, 'Data', 'MAE', 'Grades')







VAU_REPORT_DIRECTORY = os.path.join(_PROJ_ROOT, 'Ready For Printing', 'VAU')



MAE_REPORT_DIRECTORY = os.path.join(_PROJ_ROOT, 'Ready For Printing', 'MAE')







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
        print()
        print("Duplicate students found:")

        print(f"Duplicate entries found in '{column_name}':")



        for index, row in duplicates.iterrows():



            print(f"Row {index + 2}: {row[column_name]}")



        print()



    else:



        print(f"No duplicates found in '{column_name}'.")







def check_class_map(class_map: str) -> bool:
    directory = os.path.dirname(os.path.abspath(class_map))
    print(f"Processing files in directory: {directory}")
    print(f"Processing class map file: {class_map}")
    try:
        df = pd.read_csv(class_map)
    except FileNotFoundError:
        print(f"File not found: {class_map}")
        return False
    except Exception as exc:  # noqa: BLE001
        print(f"An error occurred: {exc}")
        return False

    columns_to_check = ['Class Code', 'Attendance', 'Grades', 'ClassList']
    for column in columns_to_check:
        if column in df.columns:
            check_duplicates_in_column(df, column)
        else:
            print(f"Column '{column}' not found in the CSV file.")

    print('Processed 1 file successfully')
    return True
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



    







def send_email(to: str | None, cc: str | None, subject: str, body: str) -> bool:
    if not SEND_EMAIL:
        print("INFO: SEND_EMAIL is disabled; skipping email dispatch.")
        return False
    if not to:
        warn_once("WARNING", "No primary recipient specified for email; skipping send.")
        return False

    try:
        outlook = email_client.Dispatch("outlook.application")
    except Exception as exc:
        print(f"ERROR: Unable to connect to Outlook to send email: {exc}")
        return False

    try:
        mail = outlook.CreateItem(0)
        date_string = datetime.now().strftime('%B %d, %Y')
        campus_prefix = f"{CAMPUS}: " if CAMPUS else ""

        mail.To = to
        mail.CC = cc or ""
        mail.Subject = f"{campus_prefix}{date_string}: {subject}"
        mail.HTMLBody = body or ""
        mail.Send()
        time.sleep(2)
        return True
    except Exception as exc:
        print(f"ERROR: Failed to send email via Outlook: {exc}")
        return False



def create_pdf_from_html(html: str, output_path: str) -> bool:
    if pdfkit is None:
        warn_once("WARNING", "pdfkit is not installed; skipping PDF creation.")
        return False

    try:
        config = pdfkit.configuration(wkhtmltopdf='C:/Program Files/wkhtmltopdf/bin/wkhtmltopdf.exe')
    except (OSError, IOError) as exc:
        print(f"ERROR: Unable to configure wkhtmltopdf: {exc}")
        return False

    options = {
        'enable-local-file-access': '',
        'quiet': ''
    }

    try:
        pdfkit.from_string(html, output_path, configuration=config, options=options)
        print(f"PDF saved at {output_path}")
        return True
    except IOError as exc:
        print(f"ERROR: IO issue while generating PDF '{output_path}': {exc}")
    except Exception as exc:
        print(f"ERROR: Unexpected issue while generating PDF '{output_path}': {exc}")
    return False


# Function to convert date format



def convert_date_format(value, context="Last Accessed") -> str:
    parsed = parse_datetime(value, context)
    if parsed is None:
        return datetime.now().strftime('%b %d, %Y')
    return parsed.strftime('%b %d, %Y')



def is_within_days(value, days: int) -> bool:
    parsed = parse_datetime(value, f"date threshold ({days} days)")
    if parsed is None:
        # Treat unparseable dates as needing attention
        return True
    threshold = datetime.now() - timedelta(days=days)
    return parsed < threshold


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







def calculate_final_grade(row: pd.Series) -> int:
    numerator = pd.to_numeric(row.get('Calculated Final Grade Numerator', 0), errors='coerce')
    denominator = pd.to_numeric(row.get('Calculated Final Grade Denominator', 0), errors='coerce')

    if pd.isna(numerator):
        numerator = 0
    if pd.isna(denominator) or denominator == 0:
        return 0

    try:
        final_grade = int(round(100 * float(numerator) / float(denominator)))
    except Exception as exc:
        print(f"WARNING: Failed to calculate final grade for row: {exc}")
        return 0
    return final_grade












# Read each HTML file in this directory using pandas library







def add_class_list_data(master_df: pd.DataFrame, class_list_dir_path: str) -> pd.DataFrame:
    """Extract students from Brightspace class list HTML exports."""
    print(f"Processing files in directory: {class_list_dir_path}\n")

    if not class_list_dir_path or not os.path.exists(class_list_dir_path):
        print(f"ERROR: Class list directory not found: {class_list_dir_path}")
        return master_df

    file_paths = sorted(glob.glob(os.path.join(class_list_dir_path, '*.html')))
    if not file_paths:
        warn_once("WARNING", f"No HTML files found in {class_list_dir_path}")
        return master_df

    file_count = 0

    for filename in file_paths:
        try:
            with open(filename, 'r', encoding='utf-8') as handle:
                soup = BeautifulSoup(handle, 'html.parser')
        except Exception as exc:
            print(f"WARNING: Could not open '{filename}': {exc}")
            continue

        class_code = get_class_code_from_html(soup) or 'UNKNOWN'

        try:
            tables = pd.read_html(filename, encoding='utf-8')
        except ValueError:
            warn_once("WARNING", f"No tables found in class list file '{filename}'")
            continue
        except Exception as exc:
            print(f"WARNING: Failed to read tables from '{filename}': {exc}")
            continue

        target_columns = ("org defined id", "orgdefinedid", "username")

        student_table = None
        for table in tables:
            table = table.dropna(axis=1, how='all')
            table = table.dropna(how='all')
            if table.empty:
                continue

            table.columns = [str(col).strip() for col in table.columns]
            normalized_columns = [normalize(col) for col in table.columns]

            if not any(keyword in normalized_columns for keyword in target_columns):
                header_index = None
                for idx, row in table.iterrows():
                    normalized_row = [normalize(value) for value in row]
                    if any(keyword in value for value in normalized_row for keyword in target_columns):
                        header_index = idx
                        header_values = [str(value).strip() for value in row]
                        break
                if header_index is not None:
                    table = table.iloc[header_index + 1:].reset_index(drop=True)
                    table.columns = header_values
                    normalized_columns = [normalize(col) for col in table.columns]

            if any(keyword in normalized_columns for keyword in target_columns):
                if table.empty:
                    continue
                if not any('role' in col for col in normalized_columns):
                    continue
                student_table = table
                break

        if student_table is None:
            warn_once("WARNING", f"Could not identify student table in '{filename}'")
            continue

        role_col = find_first_matching_column(student_table, ("role", "student role"))
        if role_col is None:
            warn_once("WARNING", f"Missing role column in '{filename}'")
            continue

        student_rows = student_table[student_table[role_col].astype(str).str.contains('student', case=False, na=False)]
        if student_rows.empty:
            warn_once("WARNING", f"No student rows found in '{filename}'")
            continue

        id_col = find_first_matching_column(student_table, ("org defined id", "orgdefinedid", "username", "user id"))
        if id_col is None:
            warn_once("WARNING", f"Missing Org Defined ID column in '{filename}'")
            continue

        full_name_col = find_first_matching_column(student_table, ("full name", "student name", "name"))
        first_name_col = find_first_matching_column(student_table, ("first name",))
        last_name_col = find_first_matching_column(student_table, ("last name",))

        if full_name_col is not None:
            name_series = student_rows[full_name_col].astype(str)
        else:
            first_series = student_rows[first_name_col].astype(str) if first_name_col else pd.Series([''] * len(student_rows))
            last_series = student_rows[last_name_col].astype(str) if last_name_col else pd.Series([''] * len(student_rows))
            name_series = (first_series.fillna('') + ' ' + last_series.fillna('')).str.strip()

        last_accessed_col = find_first_matching_column(student_table, ("last accessed", "last access", "last login", "last activity"))
        if last_accessed_col is None:
            warn_once("WARNING", f"Missing last accessed column in '{filename}'")
            continue

        student_data = pd.DataFrame({
            'Org Defined ID': student_rows[id_col].astype(str).str.extract(r'(\d+)', expand=False),
            'Student Full Name': name_series,
            'Last Accessed': student_rows[last_accessed_col],
            'Class Code': class_code
        })

        student_data = student_data.dropna(subset=['Org Defined ID'])
        if student_data.empty:
            warn_once("WARNING", f"No valid student IDs found in '{filename}'")
            continue

        student_data['Org Defined ID'] = student_data['Org Defined ID'].astype(str)
        student_data['Last Accessed'] = student_data['Last Accessed'].apply(lambda value: convert_date_format(value, 'class list last accessed'))

        master_df = pd.concat([master_df, student_data], ignore_index=True)
        file_count += 1

    master_df = master_df.reset_index(drop=True)
    print()
    print(f"Processed {file_count} files successfully")
    print(f"Final master DataFrame has {len(master_df)} rows")
    return master_df


def get_attendance_data(attendance_dir: str) -> pd.DataFrame:
    """Get attendance data from Brightspace CSV exports."""
    if not attendance_dir or not os.path.exists(attendance_dir):
        print(f"ERROR: Attendance directory not found: {attendance_dir}")
        return pd.DataFrame()

    csv_paths = sorted(glob.glob(os.path.join(attendance_dir, '*.csv')))
    if not csv_paths:
        warn_once("WARNING", f"No attendance CSV files found in {attendance_dir}")
        return pd.DataFrame()

    frames: list[pd.DataFrame] = []

    for filename in csv_paths:
        try:
            df = pd.read_csv(filename)
        except Exception as exc:
            print(f"WARNING: Unable to read attendance file '{filename}': {exc}")
            continue

        if df.empty:
            warn_once("WARNING", f"Attendance file '{filename}' is empty")
            continue

        id_col = find_first_matching_column(df, ("org defined id", "orgdefinedid", "org definedid", "student id"))
        if id_col is None:
            warn_once("WARNING", f"Skipping '{filename}' - no Org Defined ID column found")
            continue

        df['Org Defined ID'] = df[id_col].astype(str).str.extract(r"(\d+)", expand=False)
        df = df.dropna(subset=['Org Defined ID'])
        if df.empty:
            warn_once("WARNING", f"No valid Org Defined ID entries in '{filename}'")
            continue

        df['Org Defined ID'] = df['Org Defined ID'].astype(str)

        attendance_col = find_first_matching_column(df, ("% attendance", "attendance (%)", "attendance percent", "attendance%"))
        if attendance_col is None:
            warn_once("WARNING", f"'% Attendance' column not found in '{filename}'")
            df['% Attendance'] = np.nan
        else:
            df['% Attendance'] = pd.to_numeric(df[attendance_col], errors='coerce')

        class_code = os.path.splitext(os.path.basename(filename))[0]
        df['Class Code'] = class_code
        frames.append(df)

    if not frames:
        print("No attendance data found")
        return pd.DataFrame()

    attendance_df = pd.concat(frames, ignore_index=True)
    print(f"Found attendance data for {len(attendance_df)} students")
    return attendance_df


def get_grades_data(grades_dir: str) -> pd.DataFrame:
    """Get grades data from Brightspace CSV exports."""
    if not grades_dir or not os.path.exists(grades_dir):
        print(f"ERROR: Grades directory not found: {grades_dir}")
        return pd.DataFrame()

    csv_paths = sorted(glob.glob(os.path.join(grades_dir, '*.csv')))
    if not csv_paths:
        warn_once("WARNING", f"No grades CSV files found in {grades_dir}")
        return pd.DataFrame()

    frames: list[pd.DataFrame] = []

    for filename in csv_paths:
        try:
            df = pd.read_csv(filename)
        except Exception as exc:
            print(f"WARNING: Unable to read grades file '{filename}': {exc}")
            continue

        if df.empty:
            warn_once("WARNING", f"Grades file '{filename}' is empty")
            continue

        id_col = find_first_matching_column(df, ("orgdefinedid", "org defined id", "student id", "org-defined-id"))
        if id_col is None:
            warn_once("WARNING", f"Skipping '{filename}' - no OrgDefinedId column found")
            continue

        df['OrgDefinedId'] = df[id_col].astype(str).str.extract(r"(\d+)", expand=False)
        df = df.dropna(subset=['OrgDefinedId'])
        if df.empty:
            warn_once("WARNING", f"No valid OrgDefinedId entries in '{filename}'")
            continue

        df['OrgDefinedId'] = df['OrgDefinedId'].astype(str)

        parent_email_col = find_first_matching_column(df, ("parent email", "parentemail", "email"))
        if parent_email_col is not None:
            df['Parent Email'] = df[parent_email_col]
        else:
            df['Parent Email'] = None

        start_week_col = find_first_matching_column(df, ("enrolment start week points grade", "start week"))
        if start_week_col is not None:
            df['Start Week'] = pd.to_numeric(df[start_week_col], errors='coerce').fillna(-1).astype('int64')
        else:
            df['Start Week'] = -1

        df['Final Grade'] = df.apply(calculate_final_grade, axis=1).astype(int)
        df['Class Code'] = os.path.splitext(os.path.basename(filename))[0]

        keep_cols = ['OrgDefinedId', 'Class Code', 'Parent Email', 'Start Week', 'Final Grade']
        frames.append(df[keep_cols])

    if not frames:
        print("No grades data found")
        return pd.DataFrame()

    grades_df = pd.concat(frames, ignore_index=True)
    print(f"Found grades data for {len(grades_df)} students")
    return grades_df


def get_class_code_from_html(soup: BeautifulSoup | None) -> Optional[str]:
    """Extract a class code from the supplied HTML soup."""
    if soup is None:
        return None

    def _match_code(candidate: str | None) -> Optional[str]:
        if not candidate:
            return None
        match = CLASS_CODE_REGEX.search(candidate)
        if match:
            return match.group(0)
        return None

    # Try key navigation and title elements first
    for element in [
        soup.find('a', class_='d2l-navigation-s-link'),
        soup.find('div', class_='d2l-navigation-s-main-wrapper'),
        soup.find('title'),
    ]:
        if element:
            code = _match_code(element.get_text(strip=True))
            if code:
                return code

    # Search other textual elements if direct match not found
    for tag in soup.find_all(['a', 'span', 'div']):
        code = _match_code(tag.get_text(strip=True))
        if code:
            return code

    # Fallback to scanning the entire HTML text
    code = _match_code(soup.get_text())
    if code:
        return code

    warn_once("WARNING", "Could not locate a class code pattern in class list HTML")
    return None


def FindDupStudentsInBSViaClassList(BSdirectory: str) -> bool:
    if not BSdirectory or not os.path.exists(BSdirectory):
        print(f"ERROR: Directory not found: {BSdirectory}")
        return True

    seed_columns = ['Org Defined ID', 'Student Full Name', 'Last Accessed', 'Class Code']
    filtered_student_df = pd.DataFrame(columns=seed_columns)
    filtered_student_df = add_class_list_data(filtered_student_df, BSdirectory)

    if filtered_student_df.empty:
        print("No student data found in any of the HTML files.")
        return True

    duplicates = filtered_student_df[filtered_student_df.duplicated(['Org Defined ID'], keep=False)]
    if duplicates.empty:
        duplicates = filtered_student_df[filtered_student_df.duplicated(['Student Full Name'], keep=False)]

    if not duplicates.empty:
        print()
        print("Duplicate students found:")
        print(duplicates.sort_values(['Student Full Name', 'Org Defined ID']).to_string(index=False))
        return False

    print("No duplicates found in Brightspace class lists")
    return True



def FindDupStudentsInBSViaAttendanceGrades(target_dir: str, column_name: str) -> bool:
    if not target_dir or not os.path.exists(target_dir):
        print(f"Directory not found: {target_dir}")
        return True

    print(f"Processing files in directory: {target_dir}")

    csv_files = sorted(f for f in glob.glob(os.path.join(target_dir, '*.csv')) if os.path.isfile(f))
    if not csv_files:
        print('Processed 0 files successfully')
        print(f"No CSV files found in directory: {target_dir}")
        return True

    records: list[pd.DataFrame] = []
    processed_count = 0

    for filename in csv_files:
        file_path = os.path.join(target_dir, os.path.basename(filename))
        try:
            df = pd.read_csv(file_path)
        except Exception as exc:  # noqa: BLE001
            print(f"WARNING: Error reading '{file_path}': {exc}")
            continue

        processed_this_file = False
        id_col = column_name if column_name in df.columns else find_first_matching_column(df, ('orgdefinedid', 'org defined id', 'student id', 'username'))

        if id_col is None:
            try:
                raw = pd.read_csv(file_path, header=None)
            except Exception as exc:  # noqa: BLE001
                print(f"WARNING: Unable to parse '{file_path}' without headers: {exc}")
                continue

            extracted_rows = []
            for value in raw.iloc[:, 0].astype(str):
                match = re.search(r'(\d+)', value)
                if match:
                    extracted_rows.append({column_name: match.group(0), 'File Name': os.path.basename(filename)})
            if extracted_rows:
                records.append(pd.DataFrame(extracted_rows))
                processed_this_file = True

            if processed_this_file:
                processed_count += 1
            continue

        df[column_name] = df[id_col].astype(str).str.extract(r'(\d+)', expand=False)
        df = df.dropna(subset=[column_name])
        if df.empty:
            warn_once('WARNING', f"No valid student identifiers in '{file_path}'")
            continue

        first_name_col = find_first_matching_column(df, ('first name',))
        last_name_col = find_first_matching_column(df, ('last name',))

        if first_name_col and last_name_col:
            df['Student Name'] = (df[first_name_col].astype(str).fillna('') + ' ' + df[last_name_col].astype(str).fillna('')).str.strip()
        else:
            name_col = find_first_matching_column(df, ('student full name', 'name', 'full name'))
            df['Student Name'] = df[name_col] if name_col else ''

        df['File Name'] = os.path.basename(filename)
        records.append(df[[column_name, 'Student Name', 'File Name']])
        processed_this_file = True

        if processed_this_file:
            processed_count += 1

    print()
    print(f"Processed {processed_count} files successfully")

    if not records:
        print(f"No files with required columns found in directory: {target_dir}")
        return True

    combined_df = pd.concat(records, ignore_index=True)
    duplicates = combined_df[combined_df.duplicated(subset=column_name, keep=False)]

    if duplicates.empty:
        print('No duplicates found in Brightspace classes - checked via Attendance or Grades')
        return True

    print()
    print('Found duplicate student IDs:')
    print(duplicates.sort_values(by=column_name).to_string(index=False))

    if SEND_EMAIL:
        if TESTING:
            cc = to_email
            to = to_email
        else:
            to = to_email
            cc = cc_email

        df_string = duplicates.to_html(index=False)
        subject_email = "Please check and remove duplicates in Brightspace classes"
        body_email = (
            "Hello Office, <br><br>"
            "I ran a report today, and the following students are registered in one or more classes in BrightSpace. "
            "Please check and remove duplicates. Thank you.<br><br>"
            f"{df_string}<br><br>Sincerely, <br>Ramzan Khuwaja"
        )
        send_email(to, cc, subject_email, body_email)

    return False

def GenerateStudentMap(campus):
    """Generate student map by combining data from various sources."""
    campus = campus.upper() if isinstance(campus, str) else campus

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
        print(f"ERROR: Invalid campus name '{campus}'")
        return False

    pd.set_option('display.max_columns', None)

    columns = [
        'Org Defined ID',
        'Student Full Name',
        'Last Accessed',
        'Class Code',
        'Teacher Full Name',
        'Teacher Email',
        'Teacher Group',
        'Attendance (%)',
        'Parent Email',
        'Start Week',
        'Final Grade',
        'Att Uptodate?'
    ]
    StudentMap = pd.DataFrame(columns=columns)

    column_types = {
        'Org Defined ID': str,
        'Student Full Name': str,
        'Last Accessed': str,
        'Class Code': str,
        'Teacher Full Name': str,
        'Teacher Email': str,
        'Teacher Group': str,
        'Attendance (%)': float,
        'Parent Email': str,
        'Start Week': np.int64,
        'Final Grade': float,
        'Att Uptodate?': bool
    }
    StudentMap = StudentMap.astype(column_types)

    print()
    print("Start - Adding class list data")
    StudentMap = add_class_list_data(StudentMap, class_list_dir_path)
    if StudentMap.empty:
        print("ERROR: No data was added from class lists")
        return False
    print("End - Adding class list data")

    print()
    print("Start - Reading class map")
    if not os.path.exists(class_map_file):
        print(f"ERROR: Class map file not found: {class_map_file}")
        return False
    try:
        ClassMap = pd.read_csv(class_map_file)
    except Exception as exc:
        print(f"ERROR: Failed to read class map '{class_map_file}': {exc}")
        return False

    required_class_cols = {'Class Code', 'Teacher Full Name', 'Teacher Email', 'Teacher Group'}
    missing_class_cols = [col for col in required_class_cols if col not in ClassMap.columns]
    if missing_class_cols:
        warn_once("WARNING", f"Missing columns {missing_class_cols} in class map; teacher info may be incomplete")

    teacher_lookup = {}
    if 'Class Code' in ClassMap.columns:
        teacher_lookup = ClassMap.drop_duplicates('Class Code').set_index('Class Code').to_dict('index')

    print(f"Read {len(ClassMap)} entries from class map")
    print("End - Reading class map")

    print()
    print("Start - Copying StudentMap data")
    teacher_matches = 0
    missing_codes: set[str] = set()

    for index, row in StudentMap.iterrows():
        class_code = row['Class Code']
        details = teacher_lookup.get(class_code)
        if details:
            StudentMap.at[index, 'Teacher Full Name'] = details.get('Teacher Full Name', '')
            StudentMap.at[index, 'Teacher Email'] = details.get('Teacher Email', '')
            StudentMap.at[index, 'Teacher Group'] = details.get('Teacher Group', '')
            teacher_matches += 1
        else:
            missing_codes.add(class_code)

    print(f"Found teacher info for {teacher_matches} students")
    if missing_codes:
        sample_codes = sorted(missing_codes)[:5]
        warn_once("WARNING", f"No teacher mapping for {len(missing_codes)} class codes (e.g., {sample_codes})")
    print("End - Copying StudentMap data")

    print()
    print("Start - Getting attendance data")
    attendance_df = get_attendance_data(attendance_dir)
    print("End - Getting attendance data")

    attendance_lookup: dict[str, dict] = {}
    lesson_week = max(THIS_WEEK_NUM - 2, 1)
    lesson_col = f"Lesson {lesson_week}"

    if not attendance_df.empty:
        if 'Org Defined ID' in attendance_df.columns:
            attendance_df['Org Defined ID'] = attendance_df['Org Defined ID'].astype(str)
            attendance_lookup = attendance_df.drop_duplicates('Org Defined ID').set_index('Org Defined ID').to_dict('index')
        else:
            warn_once("WARNING", "'Org Defined ID' column missing in attendance data")
    else:
        warn_once("WARNING", "Attendance data unavailable")

    lesson_available = not attendance_df.empty and lesson_col in attendance_df.columns
    student_ids = {str(x).strip() for x in StudentMap['Org Defined ID'].dropna() if str(x).strip()} 
    attendance_ids = set(attendance_lookup.keys()) if attendance_lookup else set()

    if attendance_ids:
        missing_students = student_ids - attendance_ids
        extra_attendance = attendance_ids - student_ids

        if missing_students:
            sample_missing = sorted(missing_students)[:5]
            warn_once("WARNING", f"{len(missing_students)} students missing attendance entries (e.g., {sample_missing})")

        if extra_attendance:
            sample_extra = sorted(extra_attendance)[:5]
            warn_once("WARNING", f"{len(extra_attendance)} attendance records have unknown student IDs (e.g., {sample_extra})")


    print()
    print("Start - Copying attendance data")
    attendance_matches = 0
    for index, row in StudentMap.iterrows():
        student_id = row['Org Defined ID']
        StudentMap.at[index, 'Att Uptodate?'] = False
        if student_id and student_id in attendance_lookup:
            matching_row = attendance_lookup[student_id]
            attendance_value = matching_row.get('% Attendance')
            if attendance_value is None:
                attendance_value = matching_row.get('% attendance')
            StudentMap.at[index, 'Attendance (%)'] = attendance_value
            attendance_matches += 1

            if lesson_available:
                lesson_value = matching_row.get(lesson_col)
                if pd.isna(lesson_value) or str(lesson_value).strip() in {'', '-'}:
                    StudentMap.at[index, 'Att Uptodate?'] = False
                else:
                    StudentMap.at[index, 'Att Uptodate?'] = True
        else:
            StudentMap.at[index, 'Attendance (%)'] = np.nan

    print(f"Found attendance records for {attendance_matches} students")
    print("End - Copying attendance data")

    print()
    print("Start - Getting grade data")
    grades_df = get_grades_data(grades_dir)
    print("End - Getting grade data")

    grade_lookup: dict[str, dict] = {}
    if not grades_df.empty:
        if 'OrgDefinedId' in grades_df.columns:
            grades_df['OrgDefinedId'] = grades_df['OrgDefinedId'].astype(str)
            grade_lookup = grades_df.drop_duplicates('OrgDefinedId').set_index('OrgDefinedId').to_dict('index')
        else:
            warn_once("WARNING", "'OrgDefinedId' column missing in grade data")
    else:
        warn_once("WARNING", "Grade data unavailable")

    grade_ids = set(grade_lookup.keys()) if grade_lookup else set()

    if grade_ids:
        missing_grades = student_ids - grade_ids
        extra_grades = grade_ids - student_ids

        if missing_grades:
            sample_missing = sorted(missing_grades)[:5]
            warn_once("WARNING", f"{len(missing_grades)} students missing grade entries (e.g., {sample_missing})")

        if extra_grades:
            sample_extra = sorted(extra_grades)[:5]
            warn_once("WARNING", f"{len(extra_grades)} grade records have unknown student IDs (e.g., {sample_extra})")

    print()
    print("Start - Copying grade data")
    grade_matches = 0
    for index, row in StudentMap.iterrows():
        student_id = row['Org Defined ID']
        if student_id and student_id in grade_lookup:
            matching_row = grade_lookup[student_id]
            if matching_row.get('Parent Email'):
                StudentMap.at[index, 'Parent Email'] = matching_row.get('Parent Email')
            if matching_row.get('Final Grade') is not None:
                StudentMap.at[index, 'Final Grade'] = matching_row.get('Final Grade')
            start_week_val = matching_row.get('Start Week', -1)
            if pd.isna(start_week_val):
                start_week_val = -1
            StudentMap.at[index, 'Start Week'] = int(start_week_val)
            grade_matches += 1

    print(f"Found grade records for {grade_matches} students")
    print("End - Copying grade data")

    StudentMap['Attendance (%)'] = pd.to_numeric(StudentMap['Attendance (%)'], errors='coerce')
    StudentMap['Final Grade'] = pd.to_numeric(StudentMap['Final Grade'], errors='coerce')
    StudentMap['Start Week'] = pd.to_numeric(StudentMap['Start Week'], errors='coerce').fillna(-1).astype('int64')
    StudentMap['Att Uptodate?'] = (
        StudentMap['Att Uptodate?']
        .astype('boolean')
        .fillna(False)
        .astype(bool)
    )

    print("Start - Saving student map")
    try:
        output_dir = os.path.dirname(student_map_file)
        os.makedirs(output_dir, exist_ok=True)
        StudentMap.to_csv(student_map_file, index=False)
        print(f"Saved {len(StudentMap)} students to {student_map_file}")
        print("End - Saving student map\n")
    except Exception as exc:
        print(f"ERROR: Failed to save student map to '{student_map_file}': {exc}")
        return False

    missing_data = []
    if StudentMap['Parent Email'].isna().any():
        missing_data.append('Parent Email')
    if StudentMap['Final Grade'].isna().any():
        missing_data.append('Final Grade')
    if StudentMap['Attendance (%)'].isna().any():
        missing_data.append('Attendance (%)')

    if missing_data:
        warn_once("WARNING", f"Missing data in columns: {', '.join(missing_data)}")
        for column in missing_data:
            missing_ids = StudentMap.loc[StudentMap[column].isna(), 'Org Defined ID'].dropna().astype(str)
            sample_ids = sorted({id_.strip() for id_ in missing_ids if id_.strip()})[:5]
            print(f"WARNING: {column} missing for {len(missing_ids)} students (e.g., {sample_ids})")

    return True


def FindMissingAttendance(campus):
    print("Start - FindMissingAttendance")

    df_student_map = load_student_map(campus)
    if df_student_map.empty:
        return pd.DataFrame(columns=[
            "Org Defined ID",
            "Student Full Name",
            "Class Code",
            "Teacher Email",
            "Teacher Full Name",
            "Att Uptodate?",
            "Start Week"
        ])

    required_cols = {
        'Att Uptodate?',
        'Org Defined ID',
        'Student Full Name',
        'Class Code',
        'Teacher Email',
        'Teacher Full Name',
        'Start Week'
    }
    missing_cols = [col for col in required_cols if col not in df_student_map.columns]
    if missing_cols:
        warn_once("WARNING", f"Missing columns {missing_cols} in student map; unable to compute missing attendance")
        return pd.DataFrame()

    df_missing = df_student_map[df_student_map['Att Uptodate?'] == False]
    if df_missing.empty:
        return pd.DataFrame(columns=list(required_cols))

    df_result = df_missing[[
        'Org Defined ID',
        'Student Full Name',
        'Class Code',
        'Teacher Email',
        'Teacher Full Name',
        'Att Uptodate?',
        'Start Week'
    ]].copy()
    df_result['Start Week'] = pd.to_numeric(df_result['Start Week'], errors='coerce').fillna(-1).astype(int)
    return df_result


def email_att_missing_to_stakeholders(df_missing_attendance: pd.DataFrame) -> None:
    print("Start - email_to_stakeholders")

    if df_missing_attendance.empty:
        print("No missing attendance rows to email.")
        return

    required_cols = {'Teacher Email', 'Teacher Full Name', 'Org Defined ID', 'Student Full Name', 'Class Code', 'Att Uptodate?'}
    missing_cols = [col for col in required_cols if col not in df_missing_attendance.columns]
    if missing_cols:
        warn_once("WARNING", f"Missing columns {missing_cols} in missing attendance report; email not sent")
        return

    if not SEND_EMAIL:
        print("INFO: SEND_EMAIL disabled; skipping stakeholder notification.")
        return

    for email in df_missing_attendance['Teacher Email'].dropna().unique():
        df_teacher = df_missing_attendance[df_missing_attendance['Teacher Email'] == email]
        if df_teacher.empty:
            continue

        teacher = df_teacher['Teacher Full Name'].iloc[0]
        df_report = df_teacher[[
            'Org Defined ID', 'Student Full Name', 'Class Code', 'Att Uptodate?'
        ]].copy()

        if TESTING:
            to = to_email
            cc = ''
        else:
            to = email
            cc = cc_email

        subject_email = "Please update your Brightspace class data"
        body_email = (
            f"Hello {teacher},<br><br>"
            "Spirit of Math advises parents and students to access their class attendance and marks within a week after a class is completed.<br><br>"
            "Our records show that the following of your students/classes have not been updated for the past two weeks. "
            "Please update ASAP and keep the above practice for the rest of this school year.<br><br>"
            "No need to respond to this email, just make the applicable corrections. Thank you.<br><br>"
            f"{df_report.to_html(index=False)}<br><br>Sincerely,<br>Ramzan Khuwaja<br><br>"
        )

        send_email(to, cc, subject_email, body_email)


def FindStrugglingStudents(campus):
    print("Start - FindStrugglingStudents")

    df_student_map = load_student_map(campus)
    if df_student_map.empty:
        return pd.DataFrame(columns=[
            "Org Defined ID",
            "Student Full Name",
            "Class Code",
            "Teacher Email",
            "Teacher Full Name",
            "Final Grade",
            "Start Week"
        ])

    required_cols = {
        'Final Grade',
        'Org Defined ID',
        'Student Full Name',
        'Class Code',
        'Teacher Email',
        'Teacher Full Name',
        'Start Week'
    }
    missing_cols = [col for col in required_cols if col not in df_student_map.columns]
    if missing_cols:
        warn_once("WARNING", f"Missing columns {missing_cols} in student map; unable to evaluate struggling students")
        return pd.DataFrame()

    df_student_map['Final Grade'] = pd.to_numeric(df_student_map['Final Grade'], errors='coerce')
    struggling = df_student_map[df_student_map['Final Grade'] < GRADES_MIN_BAR]
    if struggling.empty:
        return pd.DataFrame(columns=list(required_cols))

    result = struggling[[
        'Org Defined ID',
        'Student Full Name',
        'Class Code',
        'Teacher Email',
        'Teacher Full Name',
        'Final Grade',
        'Start Week'
    ]].copy()
    result['Start Week'] = pd.to_numeric(result['Start Week'], errors='coerce').fillna(-1).astype(int)
    return result


def FindHighHonoursStudents(campus):
    print("Start - FindHighHonoursStudents")

    df_student_map = load_student_map(campus)
    if df_student_map.empty:
        return pd.DataFrame(columns=[
            "Org Defined ID",
            "Student Full Name",
            "Class Code",
            "Teacher Email",
            "Teacher Full Name",
            "Final Grade",
            "Parent Email"
        ])

    required_cols = {
        'Final Grade',
        'Org Defined ID',
        'Student Full Name',
        'Class Code',
        'Teacher Email',
        'Teacher Full Name',
        'Parent Email'
    }
    missing_cols = [col for col in required_cols if col not in df_student_map.columns]
    if missing_cols:
        warn_once("WARNING", f"Missing columns {missing_cols} in student map; unable to evaluate high honours students")
        return pd.DataFrame()

    df_student_map['Final Grade'] = pd.to_numeric(df_student_map['Final Grade'], errors='coerce')
    honours = df_student_map[df_student_map['Final Grade'] >= HIGH_HONOURS_MIN_BAR]
    if honours.empty:
        return pd.DataFrame(columns=list(required_cols))

    return honours[[
        'Org Defined ID',
        'Student Full Name',
        'Class Code',
        'Teacher Email',
        'Teacher Full Name',
        'Final Grade',
        'Parent Email'
    ]].copy()


def FindNeedsToAttendMoreRegularly(campus):
    print("Start - FindNeedsToAttendMoreRegularly")

    df_student_map = load_student_map(campus)
    if df_student_map.empty:
        return pd.DataFrame(columns=[
            'Org Defined ID',
            'Student Full Name',
            'Class Code',
            'Teacher Email',
            'Teacher Full Name',
            'Attendance (%)',
            'Parent Email'
        ])

    required_cols = {
        'Attendance (%)',
        'Org Defined ID',
        'Student Full Name',
        'Class Code',
        'Teacher Email',
        'Teacher Full Name',
        'Parent Email'
    }
    missing_cols = [col for col in required_cols if col not in df_student_map.columns]
    if missing_cols:
        warn_once("WARNING", f"Missing columns {missing_cols} in student map; unable to evaluate attendance")
        return pd.DataFrame()

    df_student_map['Attendance (%)'] = pd.to_numeric(df_student_map['Attendance (%)'], errors='coerce')
    needs_regular = df_student_map[df_student_map['Attendance (%)'] < ATTENDANCE_MIN_BAR]
    if needs_regular.empty:
        return pd.DataFrame(columns=list(required_cols))

    return needs_regular[[
        'Org Defined ID',
        'Student Full Name',
        'Class Code',
        'Teacher Email',
        'Teacher Full Name',
        'Attendance (%)',
        'Parent Email'
    ]].copy()


def export_struggling_students_to_excel(df_struggling_students, campus):
    if not PRINT_REPORT:
        return True

    if df_struggling_students is None or df_struggling_students.empty:
        print("No struggling students to export.")
        return True

    if campus == "VAU":
        grades_dir = os.path.join(VAU_REPORT_DIRECTORY, 'VAU_StrugglingStudents-')
    elif campus == "MAE":
        grades_dir = os.path.join(MAE_REPORT_DIRECTORY, 'MAE_StrugglingStudents-')
    else:
        print(f"ERROR: Invalid campus name '{campus}'")
        return False

    today = datetime.now()
    date_string = today.strftime("%B %d, %Y")
    output_path = grades_dir + date_string + ".xlsx"

    df_filtered = df_struggling_students[pd.to_numeric(df_struggling_students['Final Grade'], errors='coerce') < GRADES_MIN_BAR]
    if df_filtered.empty:
        print("No struggling students below the grade threshold.")
        return True

    df_filtered = df_filtered.sort_values(
        by=["Teacher Full Name", "Class Code", "Student Full Name", "Final Grade"],
        ascending=[True, True, True, True]
    )

    try:
        df_filtered.to_excel(output_path, sheet_name='Details', index=False)
        SummaryOfStrugglingStudents(output_path)
        print(f"{campus}_StrugglingStudents exported to {output_path}")
    except Exception as exc:
        print(f"ERROR: Failed to export struggling students report '{output_path}': {exc}")
        return False

    return True


def RemindForBSLogin(campus):
    print("Start - RemindForBSLogin")

    df_student_map = load_student_map(campus)
    if df_student_map.empty:
        return pd.DataFrame(columns=[
            "Student Full Name",
            "Last Accessed",
            "Class Code",
            "Teacher Email",
            "Teacher Full Name",
            "Teacher Group",
            "Parent Email"
        ])

    required_cols = {
        'Last Accessed',
        'Student Full Name',
        'Class Code',
        'Teacher Email',
        'Teacher Full Name',
        'Teacher Group',
        'Parent Email'
    }
    missing_cols = [col for col in required_cols if col not in df_student_map.columns]
    if missing_cols:
        warn_once("WARNING", f"Missing columns {missing_cols} in student map; unable to identify login reminders")
        return pd.DataFrame()

    threshold = datetime.now() - timedelta(days=NOT_LOGGED_IN_SINCE)

    def needs_reminder(value):
        parsed = parse_datetime(value, 'Last Accessed')
        if parsed is None:
            return True
        return parsed <= threshold

    targeted_df = df_student_map[df_student_map['Last Accessed'].apply(needs_reminder)].copy()
    columns_to_keep = [
        'Student Full Name',
        'Last Accessed',
        'Class Code',
        'Teacher Email',
        'Teacher Full Name',
        'Teacher Group',
        'Parent Email'
    ]
    return targeted_df[columns_to_keep]


def export_student_reminder_to_excel(df_remind_students, campus):
    if not PRINT_REPORT:
        return True
    if df_remind_students is None or df_remind_students.empty:
        print("No students to remind for Brightspace login.")
        return True

    if campus == "VAU":
        report_prefix = os.path.join(VAU_REPORT_DIRECTORY, 'VAU_RemindForBSLogin-')
    elif campus == "MAE":
        report_prefix = os.path.join(MAE_REPORT_DIRECTORY, 'MAE_RemindForBSLogin-')
    else:
        print(f"ERROR: Invalid campus name '{campus}'")
        return False

    today = datetime.now()
    date_string = today.strftime("%B %d, %Y")
    output_path = report_prefix + date_string + ".xlsx"

    df2 = df_remind_students[[
        "Teacher Full Name",
        "Class Code",
        "Student Full Name",
        "Last Accessed",
        "Parent Email"
    ]].copy()

    df2 = df2.sort_values(
        by=["Teacher Full Name", "Class Code", "Student Full Name", "Last Accessed"],
        ascending=[True, True, True, True]
    )

    try:
        df2.to_excel(output_path, sheet_name='Details', index=False)
        print(f"RemindStudents exported to {output_path}")
    except Exception as exc:
        print(f"ERROR: Failed to export reminder report '{output_path}': {exc}")
        return False

    return True


def export_high_honours_students_to_excel(df_high_honours_students, campus):
    if not PRINT_REPORT:
        return True
    if df_high_honours_students is None or df_high_honours_students.empty:
        print("No high honours students to export.")
        return True

    if campus == "VAU":
        grades_dir = os.path.join(VAU_REPORT_DIRECTORY, 'VAU_HighHonours-')
    elif campus == "MAE":
        grades_dir = os.path.join(MAE_REPORT_DIRECTORY, 'MAE_HighHonours-')
    else:
        print(f"ERROR: Invalid campus name '{campus}'")
        return False

    today = datetime.now()
    date_string = today.strftime("%B %d, %Y")
    output_path = grades_dir + date_string + ".xlsx"

    df2 = df_high_honours_students[[
        "Teacher Full Name",
        "Class Code",
        "Student Full Name",
        "Final Grade",
        "Parent Email"
    ]].copy()

    df2 = df2[pd.to_numeric(df2['Final Grade'], errors='coerce') >= HIGH_HONOURS_MIN_BAR]
    if df2.empty:
        print("No students meet the high honours threshold.")
        return True

    df2 = df2.sort_values(
        by=["Teacher Full Name", "Class Code", "Student Full Name", "Final Grade"],
        ascending=[True, True, True, True]
    )

    try:
        df2.to_excel(output_path, sheet_name='Details', index=False)
        print(f"{campus} - HighHonours exported to {output_path}")
    except Exception as exc:
        print(f"ERROR: Failed to export high honours report '{output_path}': {exc}")
        return False

    return True


def export_students_to_attend_more_to_excel(df_remind_students, campus):
    if not PRINT_REPORT:
        return True
    if df_remind_students is None or df_remind_students.empty:
        print("No students require attendance follow-up.")
        return True

    if campus == "VAU":
        report_dir = os.path.join(VAU_REPORT_DIRECTORY, 'VAU_NeedsToAttendMoreRegularly-')
    elif campus == "MAE":
        report_dir = os.path.join(MAE_REPORT_DIRECTORY, 'MAE_NeedsToAttendMoreRegularly-')
    else:
        print(f"ERROR: Invalid campus name '{campus}'")
        return False

    today = datetime.now()
    date_string = today.strftime("%B %d, %Y")
    output_path = report_dir + date_string + ".xlsx"

    df2 = df_remind_students[[
        "Teacher Full Name",
        "Class Code",
        "Student Full Name",
        "Attendance (%)",
        "Parent Email"
    ]].copy()

    df2 = df2.sort_values(
        by=["Teacher Full Name", "Class Code", "Student Full Name", "Attendance (%)"],
        ascending=[True, True, True, True]
    )

    try:
        df2.to_excel(output_path, sheet_name='Details', index=False)
        print(f"RemindStudents exported to {output_path}")
    except Exception as exc:
        print(f"ERROR: Failed to export attendance reminder '{output_path}': {exc}")
        return False

    return True


def SummaryOfStrugglingStudents(output_path):
    print("Start - SummaryOfStrugglingStudents")

    if not CAMPUS:
        warn_once("WARNING", "Campus not set before generating struggling student summary")
        return pd.DataFrame()

    df_student_map = load_student_map(CAMPUS)
    if df_student_map.empty:
        return pd.DataFrame()

    required_cols = {'Teacher Full Name', 'Final Grade'}
    missing_cols = [col for col in required_cols if col not in df_student_map.columns]
    if missing_cols:
        warn_once("WARNING", f"Missing columns {missing_cols} in student map; unable to build summary")
        return pd.DataFrame()

    df_student_map['Final Grade'] = pd.to_numeric(df_student_map['Final Grade'], errors='coerce').fillna(0)

    try:
        result = df_student_map.groupby('Teacher Full Name').apply(
            calculate_ranges,
            include_groups=False,
        ).reset_index()
    except Exception as exc:
        print(f"ERROR: Failed to aggregate struggling student summary: {exc}")
        return pd.DataFrame()

    result_sorted = result.sort_values(by='Total Students', ascending=False) if 'Total Students' in result.columns else result
    blank_row = pd.DataFrame('', index=[0], columns=result_sorted.columns)
    totals = result_sorted.sum(numeric_only=True)
    totals_df = pd.DataFrame([["TOTAL"] + totals.tolist()], columns=result_sorted.columns)
    result_with_summary = pd.concat([result_sorted, blank_row, totals_df], ignore_index=True)

    print(result_with_summary.to_string(index=False))

    try:
        with pd.ExcelWriter(output_path, engine='openpyxl', mode='a') as writer:
            result_with_summary.to_excel(writer, sheet_name='Summary', index=False)
    except FileNotFoundError:
        print(f"WARNING: Output file not found for summary append: {output_path}")
    except Exception as exc:
        print(f"ERROR: Failed to append summary to '{output_path}': {exc}")

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






