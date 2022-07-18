import luigi
from MailingWF import *
from LoggingWF.log_workflow import *
from ReportMergeWF.reportmerge_workflow import *
root = "E:\\luigi\\"
class Log_Report_Mailing_workflow(luigi.Task):
    input_dir = luigi.Parameter(root + "DailyRunWF\\")
    output_dir = luigi.Parameter(root + "LoggingWF\\Output\\")
    dat = str(date.today().strftime("%Y-%m-%d"))
    # def output(self):
    #     return luigi.LocalTarget(self.output_dir+"log_report_"+self.dat+".txt")
    def run(self):
        sendemail("sharikavallambatlapes@gmail.com",["vishwajeethogale307@gmail.com"],"Greetings Team,\n\nLog report is attcahed to this email.\nRegards,\nVishwajeet Hogale","Log report for "+self.dat , self.output_dir + "log_report_"+self.dat+".txt")
    def requires(self):
        return [Fetch_clean_log_workflow(input_dir=self.input_dir,output_dir=self.output_dir)]

class Final_Report_Mailing_workflow(luigi.Task):
    input_dir = luigi.Parameter(root + "DailyRunWF\\Output\\")
    output_dir = luigi.Parameter(root + "ReportMergeWF\\Output\\")
    dat = str(date.today().strftime("%Y-%m-%d"))
    # def output(self):
    #     return luigi.LocalTarget(self.output_dir+"log_report_"+self.dat+".txt")
    def run(self):
        sendemail("sharikavallambatlapes@gmail.com",["vishwajeethogale307@gmail.com","sharikavallambatla@gmail.com"],"Greetings Team,\n\nThe final report is attcahed to this email.\nRegards,\nVishwajeet Hogale","Report for "+self.dat , self.output_dir + "PREIPO_Final_Report_"+self.dat+".csv")
    def requires(self):
        return [Reportmerge_workflow(input_dir=self.input_dir,output_dir=self.output_dir)]

# class Indata_Mailing()
"""
    Write Indata emailing Workflow here on success of Final_Report_mailing
"""