import luigi
import os
from MailingWF import *
from DailyRunWF.run_workflow import *
from LoggingWF.log_workflow import *
from ReportMergeWF.reportmerge_workflow import *
from RemovePastThreeDaysDuplicatesWF.remove_data import remove_duplicates_from_todays_file
import pandas as pd
# import boto3
# from pathlib import Path
# from dotenv import load_dotenv
# import os
# from botocore.exceptions import NoCredentialsError

# # read s3 bucket connection data from .env file 
# env_path = Path('.', '.env')
# load_dotenv(dotenv_path=env_path)
# client = boto3.client('s3',
#                     aws_access_key_id = os.getenv('aws_access_key_id'),
#                     aws_secret_access_key = os.getenv('aws_secret_access_key'),
#                     region_name = os.getenv('region_name'))
# #                     # aws_access_key_id = 'AKIAR7D36P44QPQK6IUY',
# #                     # aws_secret_access_key = '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',
# #                     # region_name = 'ap-south-1'


root = "/home/rishika/Multilex-workflows/"
class Log_Report_Mailing_workflow(luigi.Task):
    input_dir = luigi.Parameter(root + "DailyRunWF/Output/")
    output_dir = luigi.Parameter(root + "LoggingWF/Output/")
    dat = str(date.today().strftime("%Y-%m-%d"))
    def output(self):
        return luigi.LocalTarget(self.output_dir+"log_report_"+self.dat+".txt")
    def run(self):
        sendemail("sharikavallambatlapes@gmail.com",["vishwajeethogale307@gmail.com","ujwalujwalc@gmail.com","techmultilex@gmail.com"],"Greetings Team,\n\nLog report is attached to this email.\nRegards,\nVishwajeet Hogale","Log report for "+self.dat , self.output_dir + "log_report_"+self.dat+".txt")
    def requires(self):
        return [Fetch_clean_log_workflow(input_dir=self.input_dir,output_dir=self.output_dir)]

class Final_Report_Mailing_workflow(luigi.Task):
    input_dir = luigi.Parameter(root + "DailyRunWF/Output/")
    output_dir = luigi.Parameter(root + "ReportMergeWF/Output/")
    dat = str(date.today().strftime("%Y-%m-%d"))
    def output(self):
        return luigi.LocalTarget(self.output_dir+"log_report_"+self.dat+".txt")
    def run(self):
        try:

            remove_duplicates_from_todays_file(root + "ReportMergeWF/Output/",root + "ReportMergeWF/Output/",2)
        except:
            print("Days parameter passed needs to be tuned!")
        
        df = pd.read_csv(self.output_dir + "PREIPO_Final_Report_" + self.dat + ".csv")
        def Filtering_titles(final):
            try:         
                if (final.empty):
                    return final
                
                key_1_gram = ['ipo', 'ipo', 'ipo ', 'spacs', 'ipo', 'pre-ipo', 'pre-ipo', 'pre-ipo', 'pre-ipo', 'spac', 'shares', 'pre ipo']
                key_2_gram = ['ipo calendar', 'shelves ipo', 'halts ipo', 'ipo pipeline', 'withdraws ipo', 'eyes ipo', 'ipo-bound', 'ipo registration', 'red herring', 'pre-initial public', 'pre-ipo announcement', 'ipos scheduled', 'ipo scheduled', 'offering ipo', 'listed on', 'go public', 'plan to', 'going public', 'offering shares', 'initial public', 'public offering', 'have listed', 'files for']
                
                key_3_gram = ['begins ipo process', 'set to ipo', 'ipo open for', 'open for subscription', 'prices ipo', 'expected ipo filings', 'files for ipo', 'upcoming ipo', 'an initial public', 'offer its shares', 'to the public', 'going to list', 'files for ipo', 'filed for ipo', 'initial public offering', 'public offering ipo']
                
                key_4_gram = ['gets nod for ipo', 'fixed a price band', 'sets ipo price band', 'planning to go public', 'preparing to go public', 'ipo to be launched', 'an initial public offering', 'the initial public offering', 'its initial public offering', 'initial public offering ipo', 'the initial public offering', 'its initial public offering ', 'has set its ipo', 'targeting a 2023 ipo']
                
                key_5_gram = ['planning an initial public offering', 'files a prospectus for ipo', 'considering an initial public offering', 'for an initial public offering']
                
                key_6_gram = [ 'sebagai ungkapan terimakasih atas perhatian anda', 'ungkapan terimakasih atas perhatian anda tersedia', 'terimakasih atas perhatian anda tersedia voucer', 'atas perhatian anda tersedia voucer gratis', 'perhatian anda tersedia voucer gratis senilai', 'anda tersedia voucer gratis senilai donasi',
                            'tersedia voucer gratis senilai donasi yang', 'voucer gratis senilai donasi yang bisa', 'gratis senilai donasi yang bisa digunakan', 'senilai donasi yang bisa digunakan berbelanja', 'donasi yang bisa digunakan berbelanja di', 'b initial public offering b b', 'b initial public offering b of', 'initial public offering b b ipo', 'public offering b b ipo b', 'the b initial public offering b', "Will Hold An Initial Public Offering", "On Its Potential Initial Public Offering"]
                key_7_gram = ["has filed for an initial public offering",'sebagai ungkapan terimakasih atas perhatian anda tersedia', 'ungkapan terimakasih atas perhatian anda tersedia voucer', 'terimakasih atas perhatian anda tersedia voucer gratis', 'atas perhatian anda tersedia voucer gratis senilai', 'perhatian anda tersedia voucer gratis senilai donasi', 'anda tersedia voucer gratis senilai donasi yang', 'tersedia voucer gratis senilai donasi yang bisa', 'voucer gratis senilai donasi yang bisa digunakan', 'gratis senilai donasi yang bisa digunakan berbelanja', 'senilai donasi yang bisa digunakan berbelanja di'
                            , 'dapat voucer gratis sebagai ungkapan terimakasih atas', 'voucer gratis sebagai ungkapan terimakasih atas perhatian', 'gratis sebagai ungkapan terimakasih atas perhatian anda', 'donasi yang bisa digunakan berbelanja di dukungan', 'yang bisa digunakan berbelanja di dukungan anda', 'bisa digunakan berbelanja di dukungan anda akan', "Raise Funds Through An Initial Public Offering"]
                key_8_gram = ["listing",'initial public offering','initial public offfering','to go public','goes Public','goes public','restricted shares','traded','list','listed','listing','lifted','allotment','Nyse','will be listed','stock exchange','delisting','moved to','hit','funding','raise','raises','valuation','going public','subscription','spac','sells','stake','debut','fundraising','board','enrollment','trade','hits','revenues','expansion','rebrand','subscribe','purchase','target price','shares','investing','allotmnet','approved','approves','fpo','registration','funds','sebi','investment','offering','nasdaq','files','launch','fund', 'stock', 'stocks', 'aims to', 'explores options', 'spinoff', 'digest', 'securities', "offer price"]
                title, link, published_date, scraped_date, text = [], [], [], [], []
                final["accepted"]=""
                for i, row in final.iterrows():
                    
                    article = str(row["title"]).lower()
                    # print(article + "\n\n\n\n")
                    c=0
                    for j in key_1_gram:
                        if j in article:
                            c+=1
                            break
                    for j in key_2_gram:
                        if j in article:
                            c+=1
                            break
                    
                    for j in key_3_gram:
                        if j in article:
                            c+=1
                            break
                    
                    for j in key_4_gram:
                        if j in article:
                            c+=1
                            break
                    
                    for j in key_5_gram:
                        if j in article:
                            c+=1
                            break
                    
                    for j in key_8_gram:
                        if j in article:
                            c+=1
                            break
                            
                    if(c>0):
                        final.at[i, "accepted"]="Yes"
                    else:
                        final.at[i, "accepted"]="No"
                    c=0
                final=final[final["accepted"]=="Yes"]
                del final["accepted"]
                final = final.reset_index(drop=True)
                return final
            except:
                print("Issue in Filter Function")
        
        df=Filtering_titles(df)
        df.drop_duplicates(subset=["link"])
        df.drop_duplicates(subset=["title"])
        df.to_csv(self.output_dir + "PREIPO_Final_Report_" + self.dat + ".csv", index=False)
        sendemail("sharikavallambatlapes@gmail.com",["vishwajeethogale307@gmail.com","sharikavallambatla@gmail.com","ujwalujwalc@gmail.com","techmultilex@gmail.com"],"Greetings Team,\n\nThe final report is attached to this email.\nRegards,\nVishwajeet Hogale","Report for "+ self.dat, self.output_dir + "PREIPO_Final_Report_" + self.dat + ".csv")
    def requires(self):
        return [Reportmerge_workflow(input_dir=self.input_dir,output_dir=self.output_dir)]

# class Indata_Mailing()
"""
    Write Indata emailing Workflow here on success of Final_Report_mailing
"""
class Part1EveningPipeline(luigi.Task):
    input_dir = luigi.Parameter(root + "DailyRunWF/Output/")
    output_dir = luigi.Parameter(root + "DailyRunWF/Output/")
    dat = str(date.today().strftime("%Y-%m-%d"))
    file_name = "EDI_PREIPO_report.csv"
    file_name1 = "FinalReport_"+dat+"_1.csv"
    def output(self):
        return luigi.LocalTarget(self.output_dir + self.file_name1)
    def requires(self):
        return [Predict(input_dir = self.output_dir,output_dir = self.output_dir)]
    def run(self):
        datapreprocess.CleanedReport(self.file_name,input_dir=self.input_dir[0:-1],output_dir=self.output_dir[0:-1])
        if os.path.isfile(self.output_dir + "todays_report.csv"):
            os.remove(self.output_dir + "todays_report.csv")
        if os.path.isfile(self.output_dir + "EDI_PREIPO_REPORT.csv"):
            os.remove(self.output_dir + "EDI_PREIPO_REPORT.csv")
class Part2EveningPipeline_new(luigi.Task):
    input_dir = luigi.Parameter(root + "DailyRunWF/Output/")
    output_dir = luigi.Parameter(root + "ReportMergeWF/Output/")
    dat = str(date.today().strftime("%Y-%m-%d"))
    file_name1 = "EDI_PREIPO_report.csv"
    def output(self):
        return luigi.LocalTarget(self.output_dir + "PREIPO_Final_Report_"+self.dat+".csv")
    def run(self):
        print("Evening Pipeline Successful!")
        if os.path.isfile(self.output_dir + "todays_report.csv"):
            os.remove(self.output_dir + "todays_report.csv")
        if os.path.isfile(self.output_dir + self.file_name1):
            os.remove(self.output_dir + self.file_name1)
        # try:
        #     client.upload_file(file_name, multilex, "PREIPO_Final_Report_" + cur_date + ".csv")
        #     print("Upload Successful")
        # except FileNotFoundError:
        #     print("The file was not found.")

    def requires(self):
       
        return [Log_Report_Mailing_workflow()]

# Note : 
# in case there is value error : Just change the name of the pipeline 