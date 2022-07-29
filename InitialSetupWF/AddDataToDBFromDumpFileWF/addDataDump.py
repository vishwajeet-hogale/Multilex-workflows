"""
Write a function that takes input directory and output directory as input 
Functionality of the function :
    1) Reads csv file from input directory 
    2) Uses functions from db file to update the database 

    File name type : Cleaned_datadump.csv -> to database 
    Note : 
    Function is already present to update the database in db.py 

    Hint : 
    Just call addfile function from db.py 

==================================================================================================================

"""
import pandas as pd
import db.py
input_dir = "E:\\MultilexDash\\Backend\\"
def uploadDump(input_dir,file_name="Cleaned_datadump.csv"):
    #write code here
    pd.read_csv("E:\\MultilexDash\\Backend\\/Cleaned_datadump.csv")
    apply.addfile( Cleaned_datadump.csv,type="csv")
from db import *
input_dir = "E:\\MultilexDash\\Backend\\"
def uploadDump(input_dir,file_name="Cleaned_datadump.csv"):
    #write code here
    addfile( input_dir + "Cleaned_datadump.csv",type="csv")

