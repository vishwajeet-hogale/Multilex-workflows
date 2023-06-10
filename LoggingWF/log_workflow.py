import luigi 
from Mail.mail import sendemail
from datetime import date
from ReportMergeWF.reportmerge_workflow import *
from ReportMergeWF.reportmerge_workflow import MorningFile_check 
# class Get_date(luigi.Task):
#     def run(self):
#         return str(date.today().strftime("%Y-%m-%d"))
class Fetch_clean_log_workflow(luigi.Task):
    input_dir = luigi.Parameter(default="E:/MultilexDash/Pipeline/Scraper/")
    output_dir = luigi.Parameter("./Output/")
    dat = date.today()
    dat = str(dat.strftime("%Y-%m-%d"))
    def output(self):
        return luigi.LocalTarget(self.output_dir+"log_report_"+self.dat+".txt")
    def run(self):
        with open(self.input_dir + "logs.txt","r") as f:
            data = set(f.read().split("\n"))
        with open(self.input_dir +"logs1.txt","r") as f:
            data1 = set(f.read().split("\n"))
        res = data.union(data1)
        with open(self.output_dir + "log_report_"+self.dat+".txt","w") as f:
            for i in res:
                f.write(i+"\n")
    def requires(self):
        return [EveningFile_check(output_dir = self.input_dir)]
""

# class Log_workflow(luigi.Task):
#     input_dir = luigi.Parameter(default="E:/MultilexDash/Pipeline/Scraper/")
#     output_dir = luigi.Parameter(default="./Output/")
#     dat = str(date.today().strftime("%Y-%m-%d"))
#     def output(self):
#         return luigi.LocalTarget(self.output_dir+"log_report_"+self.dat+".txt")
#     def run(self):
#         sendemail("sharikavallambatlapes@gmail.com","vishwajeethogale307@gmail.com","Log report is attcahed to this email.","Demo : Log report for "+self.dat , self.output_dir + "log_report_"+self.dat+".txt")
#     def requires(self):
#         return [Fetch_clean_log_workflow(input_dir=self.input_dir,output_dir=self.output_dir)]