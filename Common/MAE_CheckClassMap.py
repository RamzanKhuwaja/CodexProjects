import pandas as pd

def check_duplicates_in_column(df, column_name):
    duplicates = df[df.duplicated(column_name, keep=False)]
    if not duplicates.empty:
        print(f"Duplicate entries found in '{column_name}':")
        for index, row in duplicates.iterrows():
            print(f"Row {index + 2}: {row[column_name]}")
        print()
    else:
        print(f"No duplicates found in '{column_name}'.")

def main():
    # Path where ClassMap file is stored
    ClassMap = r"C:\Users\ramza\Dropbox\VAUDocs\Automation\Code\MAE\MAEClassMap2023-24.csv"

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
if __name__ == "__main__":
    main()
