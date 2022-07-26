from InitialSetupWF.CreateDumpWF.makeDataframe import *
root_dir_all_files = 'E:\EDI'
def create_dataframe(output_dir):
    df = run_feature1(root_dir_all_files,output_dir)
    print(df)