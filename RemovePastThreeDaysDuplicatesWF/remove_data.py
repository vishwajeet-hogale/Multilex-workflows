"""
Write a function that takes input directory and output directory as input 
Functionality of the function :
    1) Reads csv files of last three days excluding current date file, stores it in three seperate dataframe 
    2) Concatenate all the dataframes 
    3) Remove duplicates based on text and title from current date file after comparing it with 
    the dataframe genrated in step 2

    File name type : PREIPO_Final_Report_2022-07-21.csv -> PREIPO_Final_Report_<date>.csv

==================================================================================================================
Removes duplicates if and only if >> text AND title << are the same


input_dir   : Defines the path for input folder of csvs
output_dir  : Defines the path for output files

input_file_template  : Defines the csv file name for input
output_file_template : Defines the csv file name for output

no_of_days  : Define the search range excluding today eg: 3 >> yesterday, day before and day before the day before
curr_date   : finds todays date
"""


import pandas as pd
from datetime import date, datetime, timedelta

input_dir = "E:\\luigi\\ReportMergeWF\\Output\\"
output_dir = "E:\\luigi\\RemovePastThreeDaysDuplicatesWF\\Output\\"
#
input_file_template = "PREIPO_Final_Report_{date}.csv"
output_file_template = "PREIPO_Final_Report_{date}.csv"
#
no_of_days = 3
curr_date = date.today()


# remove duplicate Function
def remove_duplicates_from_todays_file(input_dir, output_dir):
    # Create File input and output names
    input_file = input_dir + input_file_template
    output_file = output_dir + output_file_template
    # To store dataframes including todays and find todays date
    df_list = []
    #
    # Adds todays data and then prev data
    for i in range(no_of_days + 1):

        # Reading csv file and adding df to df_list
        file = input_file.format(date=(curr_date - timedelta(days=i)))
        df = pd.read_csv(file)
        df_list.append(df)

    # Concatenating dataframes in df_list
    df_concat = pd.concat(df_list)
    #
    # Droping Duplicates by keeping today data and resetting index
    new_df = df_concat.drop_duplicates(subset=["text", "title"]).reset_index(drop=True)
    #
    # Writing data to output_file
    new_df.to_csv(output_file.format(date=curr_date),index=False)


# For testing this file run this file with terminal in the RemovePastThreeDaysDuplicate folder
if __name__ == "__main__":
    curr_date =  datetime.strptime("25-07-2022", "%d-%m-%Y").date()
    input_dir = ".\\testIO\\input\\"
    output_dir = ".\\testIO\\output\\"
    remove_duplicates_from_todays_file(input_dir, output_dir)
