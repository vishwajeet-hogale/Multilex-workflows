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
# from Database.db import *
input_dir = "E:\\luigi\\ReportMergeWF\\Output\\"
# input_dir = "E:\\luigi\\DailyRunWF\\Output\\"
output_dir = "E:\\luigi\\RemovePastThreeDaysDuplicatesWF\\Output\\"
#

#


def check_title(df,title):
    try:
        return df["title"].to_list().index(title)
    except:
        return -1
def check_text(df,text):
    try:
        return df["text"].to_list().index(text)
    except:
        return -1
# remove duplicate Function
def remove_duplicates_from_todays_file(input_dir, output_dir):
    # Create File input and output names
    input_file_template = "PREIPO_Final_Report_{date}.csv"
    output_file_template = "PREIPO_Final_Report_{date}.csv"
    input_file = input_dir + input_file_template
    output_file = output_dir + output_file_template
    no_of_days = 3
    curr_date = date.today()
    # To store dataframes including todays and find todays date
    df_list = []
    # Adds todays data and then prev data
    df1 = pd.read_csv(input_dir + input_file_template.format(date=str(curr_date.strftime("%Y-%m-%d"))))
    for i in range(1,no_of_days+1):

        # Reading csv file and adding df to df_list
        file = input_file.format(date=(curr_date - timedelta(days=i)))
        df = pd.read_csv(file)
        df_list.append(df)

    # Concatenating dataframes in df_list
    df_concat = pd.concat(df_list)
    collection = []
    for i,row in enumerate(df1.values):
        if(check_text(df_concat,df1["text"][i]) == -1 and check_title(df_concat,df1["title"][i]) == -1):
            collection.append(row.tolist())
    new_df = pd.DataFrame(collection,columns=["Unnamed: 0","publish_date","scraped_date","title","text","Companies","Country","link","Comments","update"])
    # Droping Duplicates by keeping today data and resetting index
    new_df = new_df.drop_duplicates(subset=["text", "title"]).reset_index(drop=True)
    
    # Writing data to output_file
    new_df.to_csv(output_file.format(date=curr_date),index=False)
    

# For testing this file run this file with terminal in the RemovePastThreeDaysDuplicate folder
if __name__ == "__main__":
    # curr_date =  str(date.today().strftime("%Y-%m-%d"))
    # input_dir = ".\\testIO\\input\\"
    # output_dir = ".\\testIO\\output\\"
    remove_duplicates_from_todays_file(input_dir, output_dir)
