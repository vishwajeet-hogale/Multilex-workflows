from InitialSetupWF.CreateDumpWF.makeDataframe import *
import pandas as pd
root_dir_all_files = 'E:\EDI'
pipeline_dir = 'E:\luigi\Output'
def create_dataframe(output_dir):
    df = run_feature1(root_dir_all_files,output_dir)
    df1 = run_feature1(pipeline_dir,output_dir)
    df = pd.concat([df,df1])
    df = df.drop_duplicates(subset=["text","title","link"])
    df.to_csv(output_dir + "Cleaned_datadump.csv")
    print(df)

# create_dataframe("")