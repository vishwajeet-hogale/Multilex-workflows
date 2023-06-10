import luigi
import os
from MailingWF import *
from DailyRunWF.run_workflow import *
from LoggingWF.log_workflow import *
from ReportMergeWF.reportmerge_workflow import *
from RemovePastThreeDaysDuplicatesWF.remove_data import remove_duplicates_from_todays_file
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