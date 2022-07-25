"""
Write a function that takes input directory and output directory as input 
Functionality of the function :
    1) Reads csv files of last three days excluding current date file, stores it in three seperate dataframe 
    2) Concatenate all the dataframes 
    3) Remove duplicates based on text and title from current date file after comparing it with 
    the dataframe genrated in step 2

    File name type : PREIPO_Final_Report_2022-07-21.csv -> PREIPO_Final_Report_<date>.csv

"""
input_dir = "E:\\luigi\\ReportMergeWF\\Output\\"
output_dir = "E:\\luigi\\RemovePastThreeDaysDuplicatesWF\\Output\\"
def remove_duplicates_from_todays_file(input_dir,output_dir):
    # Insert code here
    pass