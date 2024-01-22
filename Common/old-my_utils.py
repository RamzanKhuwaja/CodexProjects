import os
import time
import pdfkit
import pandas as pd
from bs4 import BeautifulSoup
from datetime import datetime
import win32com.client as email_client
from datetime import datetime, timedelta

CAMPUS = "VAU" # "MAE"
to_email = cc_email = ""

def set_campus_info():
    global CAMPUS, to_email, cc_email
    if CAMPUS == "VAU":
        to_email = "rkhuwaja@spiritofmath.com"
        cc_email = "vaughan@spiritofmath.com"
    elif CAMPUS == "MAE":
        to_email = "rkhuwaja@spiritofmath.com"
        cc_email = "markhameast@spiritofmath.com"
    else:
        print("Invalid campus")

def send_email(to, cc, subject, body):
    # Use the Dispatch method to interact with Outlook
    outlook = email_client.Dispatch("outlook.application")
    mail = outlook.CreateItem(0)  # 0 is the code for an email item

    # Set mail properties
    mail.To = to  # String of recipient email addresses
    mail.CC = cc  # String of CC email addresses
    mail.Subject = subject  # String for the email's subject
    #mail.Body = body  # String for the email's body
    # Set the email body to HTML
    mail.HTMLBody = body  # String containing HTML for the email's body

    # Send the email
    mail.Send()
    time.sleep(5)

# def create_pdf_from_html(html, output_path):
#     # Convert HTML to PDF
#     pdfkit.from_string(html, output_path)
#     print(f"PDF saved at {output_path}")

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

# Example usage:
# create_pdf_from_html('<h1>Hello World</h1>', 'output.pdf')



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

# Function to check if the date is within the last NOT_LOGGED_IN_SINCE days
def is_within_days(date_str, NOT_LOGGED_IN_SINCE):
    date_object = datetime.strptime(date_str, '%b %d, %Y')
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