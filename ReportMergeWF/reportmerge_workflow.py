import luigi 
import merge_reports
from datetime import date

class MorningFile_check(luigi.Task):
    dat = str(date.today().strftime("%Y-%m-%d"))
    output_dir = luigi.Parameter(default="./Output/")
    def output(self):
        return luigi.LocalTarget(self.output_dir + "FinalReport_"+self.dat+".csv")
class EveningFile_check(luigi.Task):
    dat = str(date.today().strftime("%Y-%m-%d"))
    output_dir = luigi.Parameter(default="./Output/")
    def output(self):
        return luigi.LocalTarget(self.output_dir + "FinalReport_"+self.dat+"_1.csv")
class reportmerge_workflow(luigi.Task):
    output_dir = luigi.Parameter(default="./Output/")
    dat = str(date.today().strftime("%Y-%m-%d"))
    def output(self):
        return luigi.LocalTarget(self.output_dir + "PREIPO_Final_Report_"+self.dat+".csv")
    def run(self):
        merge_reports.merge_reports(self.output_dir)
    def requires(self):
        return [MorningFile_check(),EveningFile_check()]
