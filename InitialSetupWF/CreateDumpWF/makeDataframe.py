import os
import pandas as pd 
import glob
rootdir = 'E:\EDI'
def get_all_files(rootdir): #get all files of a month 
    files_stored = []
    for subdir,dir,files in os.walk(rootdir):
        for sdir,di,file in os.walk(subdir):
          
          csv_files = glob.glob(os.path.join(sdir, "*.xlsx"))
                # print(sdir)
        files_stored.extend(csv_files)
    files_stored = sorted(list(set(files_stored)))
    print(files_stored)
    return files_stored
def combine_data(files): #combine all collected files into one csv 
    print(files)
    df = pd.read_excel(files[0])
    dataframes = [df]
    for i in files[1:]:
        # try:
            if not(i[-4:] == ".csv"):
                print(i)
                df1 = pd.read_excel(i)
                # df1 = df1.iloc[:,:]
                # print(df1.shape)
                # df1 = df1.dropna()
                dataframes.append(df1)
                # df1 = df1.dropna(subset = ["Companies"], inplace=True)
                # df = df.append(df1)
        # except:
        #     print("Problem in : ",i)
        #     continue
    big_df = pd.concat(dataframes)
    print(big_df)
    return big_df
def remove_blank(df): #Removes all the empty rows from the dataframe
    nan_value = float ("NaN")
    df.replace("", nan_value, inplace=True)
    df. dropna (subset = [ "Companies"],
    inplace=True)
    return df
def run_feature1(rootdir,output_dir):
    files = get_all_files(rootdir=rootdir)
    df = combine_data(files)
    df = remove_blank(df)
    df.to_csv(output_dir + "Cleaned_datadump.csv")
    return df
if __name__ =='__main__':
#     files = get_all_files(rootdir=rootdir)
#     df = combine_data(files)
#     df = remove_blank(df)
#     # df.to_csv("Cleaned_dump.csv")
#     # df = df.dropna(
#     # axis=0,
#     # how='any',
#     # thresh=None,
#     # subset=None,
#     # inplace=True
# # )
#     df.to_csv("Cleaned_dump.csv")
    # print(df)
    df = run_feature1("E:\\EDI\\")

