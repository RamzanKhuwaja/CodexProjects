import os
import pandas as pd
import my_mae_utils as utils
from bs4 import BeautifulSoup


def main():

    TESTING = True
    SEND_EMAIL = False
    to = cc = subject = body = ""

    # Set display options
    pd.set_option('display.max_columns', None)  # Show all columns
    pd.set_option('display.max_rows', None)     # Show all rows
    pd.set_option('display.max_colwidth', None) # Show full content of each column
    pd.set_option('display.width', None)        # Automatically detect the console width

    # Dir where Brightspace downloaded files are stored
    BSdirectory = r'C:\Users\ramza\Dropbox\VAUDocs\Automation\Data\MAE\BSLogin'

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
                to="rkhuwaja@spiritofmath.com"
            else:
                cc="vaughan@spiritofmath.com"

            subject="Please check and remove duplicates in Brightspace classes"
            body="Hello Office, <br><br>" + \
                "I ran a script today, and the following students are registered in one or more classes in BrightSpace (BS). Please check BS (Classlists) and remove duplicates. Thank you.<br><br>" \
                    + df_string + "<br><br>Sincerely, <br>Ramzan Khuwaja"

            utils.send_email(to, cc, subject, body)

        return False
    else: 
        print("No duplicates found in Brightspace classes - checked via Class Lists")
        return True

if __name__ == "__main__":
    main()