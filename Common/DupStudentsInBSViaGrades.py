import os
import time
import pandas as pd
import Common.my_utils as utils
import win32com.client as email_client


def main():

    TESTING = True
    SEND_EMAIL = False

    # Directory containing the CSV files
    directory = r"C:\Users\ramza\Dropbox\VAUDocs\Automation\Data\MAE\Grades\BSFiles"

    # List to store each DataFrame
    dfs = []

    to = cc = subject = body = ""

    # Loop through each file in the directory
    for filename in os.listdir(directory):
        if filename.endswith('.csv'):
            file_path = os.path.join(directory, filename)
            # Read the CSV file
            df = pd.read_csv(file_path)
            # Check if required columns exist
            if all(col in df.columns for col in ['OrgDefinedId', 'First Name', 'Last Name']):
                df["File Name"] = filename
                # Append the required columns to the list
                dfs.append(df[['OrgDefinedId', 'First Name', 'Last Name', "File Name"]])

    # Concatenate all DataFrames in the list
    combined_df = pd.concat(dfs, ignore_index=True)

    # Find duplicates based on 'OrgDefinedId'
    duplicates = combined_df[combined_df.duplicated(subset='OrgDefinedId', keep=False)]

    # Sort the DataFrame based on 'OrgDefinedId'
    sorted_duplicates = duplicates.sort_values(by='OrgDefinedId')


    if not sorted_duplicates.empty:
        # Print the non-unique elements sorted by 'OrgDefinedId', without the index
        print("Non-unique elements sorted by 'OrgDefinedId':")
        print(sorted_duplicates.to_string(index=False))
        
        df_string = sorted_duplicates.to_html(index=False)

        if SEND_EMAIL:
            if TESTING: 
                to="rkhuwaja@spiritofmath.com"
            else:
                cc="vaughan@spiritofmath.com"

            subject="Please check and remove duplicates in Brightspace classes"
            body="Hello Office, <br><br>" + \
                "I ran a script today, and the following students are registered in one or more classes in BrightSpace. Please check and remove duplicates. Thank you.<br><br>" \
                    + df_string + "<br><br>Sincerely, <br>Ramzan Khuwaja"

            utils.send_email(to, cc, subject, body)
        return False
    else: 
        print("No duplicates found in Brightspace classes - checked via Grades")
        return False

if __name__ == "__main__":
    main()