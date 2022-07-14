import luigi
from datetime import date 
from s1docscraper import make_report
from Mail.mail import sendemail


class Fetch_Data(luigi.Task):
    output_dir = luigi.Parameter(default="./Output/")
    def output(self):
        dat = date.today()
        dat = str(dat.strftime("%Y-%m-%d"))
        return luigi.LocalTarget(self.output_dir+"S1DOC_Report_"+dat+".csv")
    def run(self):
        make_report(self.output_dir)

class S1_workflow(luigi.Task):
    output_dir = luigi.Parameter(default="./Output/")
    def output(self):
        dat = date.today()
        dat = str(dat.strftime("%Y-%m-%d"))
        return luigi.LocalTarget(self.output_dir+"S1DOC_Report_"+dat+".csv")
    def run(self):
        dat = date.today()
        dat = str(dat.strftime("%Y-%m-%d"))
        sendemail("sharikavallambatlapes@gmail.com","vishwajeethogale307@gmail.com","I have attached the S1 report to this email","S1 report for " + dat,self.output_dir+"S1DOC_Report_"+dat+".csv")
        # return luigi.LocalTarget(self.output_dir+"S1DOC_Report_"+dat+".csv")
    def requires(self):
        return [
            Fetch_Data(output_dir = self.output_dir)
        ]