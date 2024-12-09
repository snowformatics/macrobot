import argparse
import shutil
import os
#import pyodbc
import json
import cx_Oracle
import pandas as pd
from pathlib import Path
import numpy as np
# Temporarily adjust display settings
pd.set_option('display.max_rows', None)  # Show all rows
pd.set_option('display.max_columns', None)  # Show all columns
pd.set_option('display.width', None)  # Adjust width for wide DataFrames


def copy_and_verify(path1, path2):
    """
    Copies all folders and files from psg-09 to hsm and verifies the copy.

    Args:
        path1 (str): Source directory.
        path2 (str): Destination directory.

    Raises:
        ValueError: If the copy verification fails.
    """
    try:
        # Ensure source and destination paths exist
        if not os.path.exists(path1):
            raise ValueError(f"Source path '{path1}' does not exist.")

        if not os.path.exists(path2):
            os.makedirs(path2)

        # Copy files and directories
        for root, dirs, files in os.walk(path1):
            # Create destination folder structure
            relative_path = os.path.relpath(root, path1)
            destination_dir = os.path.join(path2, relative_path)
            if not os.path.exists(destination_dir):
                os.makedirs(destination_dir)

            # Copy files
            for file in files:
                src_file = os.path.join(root, file)
                dest_file = os.path.join(destination_dir, file)
                shutil.copy2(src_file, dest_file)

        # Verify the copy
        for root, dirs, files in os.walk(path1):
            relative_path = os.path.relpath(root, path1)
            destination_dir = os.path.join(path2, relative_path)

            for file in files:
                src_file = os.path.join(root, file)
                dest_file = os.path.join(destination_dir, file)
                if not os.path.exists(dest_file):
                    raise ValueError(f"File '{dest_file}' is missing in the destination.")

        print(f"All files and folders successfully copied from '{path1}' to '{path2}'.")
    except Exception as e:
        print(f"An error occurred: {e}")


def process_and_merge_files(excel_file, csv_file, identifier, output_file):
    try:
        # Extract the first word after splitting the filenames by '_'
        excel_base = os.path.basename(excel_file).split('_')[0]
        csv_base = os.path.basename(csv_file).split('_')[0]
        #print (excel_file, csv_file, output_file)
        if csv_base.startswith('gb2'):
            csv_base = csv_base + '_' + os.path.basename(csv_file).split('_')[1]
        print (csv_base)

        # Check if both files share the same starting word
        # if excel_base != csv_base:
        #     raise ValueError(
        #         f"Filename mismatch: '{excel_file}' and '{csv_file}' do not start with the same word after split by '_'."
        #     )
        # Read the Excel file
        #df1 = pd.read_excel(excel_file)
        df1 = pd.read_csv(excel_file, delimiter='\t')
        #df1 = df1.rename(columns={'plate_id': 'INFECTION', 'Lane_ID': 'LANE_ID2', 'Plate_ID': 'PLATE_ID2'})

        # Read the CSV file
        df2 = pd.read_csv(csv_file, delimiter=';')
       # print (df2)

        # Create the `plate_index` column by splitting `Plate_ID` and taking the last entry
        df2['plate_index'] = df2['Plate_ID'].apply(lambda x: x.split('_')[-1]) + '-' + df2['Lane_ID'].astype(str)

        # Check if both DataFrames contain the identifier column
        if identifier not in df1.columns:
            raise ValueError(f"Identifier column '{identifier}' is missing in the Excel file.")
        if identifier not in df2.columns:
            raise ValueError(f"Identifier column '{identifier}' is missing in the CSV file.")

        # Merge the files on the specified identifier
        merged_df = pd.merge(df1, df2, on=identifier, how='outer')
        merged_df = merged_df.drop(columns=['expNr', 'barcode'])
        # Add a new column `type` with the value `macrobot`
        merged_df['type'] = 'macrobot'
        # Add a new column `url1` with the path `\\hsm\AGR-BIM\macrobot\ + csv_base`
        merged_df['url1'] = merged_df.apply(
            lambda row: f"\\\\hsm\\AGR-BIM\\macrobot\\{row['experiment']}\\{row['dai']}dai", axis=1
        )
        merged_df['url2'] = merged_df.apply(
            lambda row: f"\\\\hsm\\AGR-BIM\\Results\\BluVisionMacro\\{row['experiment']}\\{row['dai']}dai", axis=1
        )

        # Validate the merged DataFrame
        if len(merged_df.columns) < len(df2.columns):
            raise ValueError("Merged DataFrame does not contain at least as many columns as the CSV file.")
        non_na_percentage = merged_df.notna().sum().sum() / merged_df.size
        if non_na_percentage <= 0.1:
            raise ValueError(
                f"Less than 10% of the cells in the merged DataFrame are non-NA or non-empty. "
                f"Non-NA percentage: {non_na_percentage:.2%}"
            )
        merged_df = merged_df.rename(columns={'%_Inf': 'INFECTION', 'Lane_ID': 'LANE_ID2', 'Plate_ID': 'PLATE_ID2',
                                              'index': 'index_', 'user': 'user_'})
        merged_df['experiment'] = csv_base
        # Save the merged DataFrame to a new CSV file
        merged_df.to_csv(output_file, index=False)
        #print(f"Merged file saved to: {output_file}")

    except Exception as e:
        print(f"An error occurred: {e}")



def export_db(csv_file_path):
    os.chdir('C:/instantclient_19_3/')

    # Load configuration from a JSON file
    with open('C:/Users/lueck/PycharmProjects/macrobot/macrobot/config.json', 'r') as config_file:
        config = json.load(config_file)

    # Extract the configuration parameters
    ip = config['ip']
    port = config['port']
    service_name = config['service_name']
    username = config['username']
    password = config['password']

    # Construct the DSN
    dsn = cx_Oracle.makedsn(ip, port, service_name=service_name)

    # Connect to the database
    db_con = cx_Oracle.connect(username, password, dsn)

    # Create a cursor
    cursor = db_con.cursor()

    # Query the database table
    cursor.execute("SELECT * FROM MACROBOT_DB")

    # Get the database table column headers
    db_headers = [x[0] for x in cursor.description]

    # Load CSV file
    csv_data = pd.read_csv(csv_file_path, delimiter=',')
    csv_data.columns = [col.upper() for col in csv_data.columns]  # Convert CSV headers to uppercase


    #csv_data = csv_data.where(pd.notnull(csv_data), None)
    #csv_data = csv_data.fillna('NA')
    # Format date columns
    date_columns = ['SAW_DATE', 'INOC_DATE']
    for col in date_columns:
        if col in csv_data.columns:
            csv_data[col] = pd.to_datetime(csv_data[col], errors='coerce')
            csv_data[col] = csv_data[col].dt.strftime('%Y-%m-%d')
            if csv_data[col].isna().all():
                #print(f"Column {col} is empty or contains only invalid dates.")
                # Optionally fill with a default value, or leave as NaT
                csv_data[col] = pd.Timestamp('1900-01-01')  # Example default date
            #csv_data[col] = csv_data[col].where(pd.notnull(csv_data[col]), None)
    #csv_data.where(pd.notnull(csv_data), None)

    # Compare and ensure CSV columns exist in the database
    matching_headers = set(db_headers).intersection(csv_data.columns)
    if not matching_headers:
        print("No matching columns between CSV and database.")
        return

    # Insert CSV data into the database
    for _, row in csv_data.iterrows():
        # Prepare the columns and values for the SQL statement
        columns = ', '.join([col for col in db_headers if col in csv_data.columns])
        values = ', '.join([
            f"TO_DATE(:{col}, 'YYYY-MM-DD')" if col in date_columns else f":{col}"
            for col in db_headers if col in csv_data.columns
        ])
        sql = f"INSERT INTO MACROBOT_DB ({columns}) VALUES ({values})"

        # Prepare the parameters dictionary
        params = {}
        for col in db_headers:
            if col in csv_data.columns:
                value = row[col]
                if col in date_columns:  # Handle date columns
                    try:
                        # Attempt to parse the date; if invalid, use a default
                        value = pd.to_datetime(value, errors='coerce').strftime('%Y-%m-%d') if pd.notnull(
                            value) else None
                    except Exception:
                        value = None  # Fallback for invalid dates
                elif isinstance(value, str) and not value.strip():  # Handle empty strings for numeric fields
                    value = None
                elif pd.isnull(value):  # Handle NaN values
                    value = None
                params[col] = value

        try:
            cursor.execute(sql, params)
        except cx_Oracle.DatabaseError as e:
            print(f"Error inserting row: {row}\n{e}")

    # for _, row in csv_data.iterrows():
    #
    #     columns = ', '.join([col for col in db_headers if col in csv_data.columns])
    #     values = ', '.join([
    #         f"TO_DATE(:{col}, 'YYYY-MM-DD')" if col in date_columns else f":{col}"
    #         for col in db_headers if col in csv_data.columns
    #     ])
    #     sql = f"INSERT INTO MACROBOT_DB ({columns}) VALUES ({values})"
    #
    #     params = {col: row[col] for col in db_headers if col in csv_data.columns}
    #     #print (params)
    #     try:
    #         cursor.execute(sql, params)
    #     except cx_Oracle.DatabaseError as e:
    #         pass
    #         print(f"Error inserting row: {row}\n{e}")

    # Commit changes to the database
    db_con.commit()
    print("Data from CSV inserted successfully into the database.")
    #cursor.execute("SELECT * FROM MACROBOT_DB")
   # rv = cursor.fetchall()
    #for result in rv:
     #   print(result)

    # Close the cursor and connection
    cursor.close()
    db_con.close()
  

#process_and_merge_files("meta_empty.csv", "MB0267_leaf.csv", "plate_index", "MB0267_db.csv")
#export_db("C:/Users/lueck/PycharmProjects/macrobot/macrobot/MB0267_db.csv")
#copy_and_verify("//psg-09/Mikroskop/Images/BluVisionMacro/MB0263/6dai/", "//hsm/AGR-BIM/Results/BluVisionMacro/MB0263/6dai/")

def old_mb_data():
    #for old data
    #Define the source directory
    source_dir = os.listdir(r"\\psg-09\Mikroskop\Images\BluVisionMacro")
    # Use glob to search recursively for files ending with _leaf.csv
    leaf_csv_files = []

    # Walk through all directories and files
    for folder in source_dir:
        folder_dai = os.listdir(r"\\psg-09\Mikroskop\Images\BluVisionMacro\\" + folder)
        for dai in folder_dai:
            if not dai.endswith('.txt'):
                #print (folder, folder_dai, dai)
                csv_dir =  os.listdir(r"\\psg-09\Mikroskop\Images\BluVisionMacro\\" + folder + '\\' + '\\' + dai)
                for csv in csv_dir:
                    if csv.endswith('_leaf.csv'):
                        #print (folder, folder_dai, dai, csv)
                        print (folder)
                        process_and_merge_files("meta_empty.csv",
                                                r"\\psg-09\Mikroskop\Images\BluVisionMacro\\" + folder + '\\' + dai + '\\' + csv,
                                                "plate_index", r"\\psg-09\Mikroskop\Images\hsm_db\\" + folder + "_db.csv")

    # # Use glob to search recursively for files ending with _leaf.csv
    leaf_csv_files = os.listdir(r"\\psg-09\Mikroskop\Images\hsm_db\\")

    # Check if any files were found

    for file in leaf_csv_files[1:]:
        print (file)
        try:
            export_db(r"\\psg-09\Mikroskop\Images\hsm_db\\" + file)
        except:
            print ('erorr')
