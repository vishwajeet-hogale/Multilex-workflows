import luigi 
from datetime import date
from Mail.mail import sendemail
import importlib.util       
from LoggingWF.log_workflow import Fetch_clean_log_workflow
class Log_report_workflow(luigi.Task):
    input_dir = luigi.Parameter("./Output/")
    output_dir = luigi.Parameter("./Output/")
    dat = str(date.today().strftime("%Y-%m-%d"))
    def output(self):
        return luigi.LocalTarget(self.input_dir + "log_report_"+self.dat+".txt")
    def run(self):
        sendemail("sharikavallambatla@gmail.com","191381679manasaab@gmail.com","Greetings Sharika,\n\nLog report attached to this email\n\nRegards,\nSai Manasa Nadimpalli","Log report for "+self.dat,self.output_dir + "log_report_"+self.dat+".txt")
    def requires(self):
        return [Fetch_clean_log_workflow(input_dir = self.input_dir,output_dir = self.output_dir)]