import luigi 
import ReportMergeWF.merge_reports as merge_reports
from datetime import date

class MorningFile_check(luigi.Task):
    dat = str(date.today().strftime("%Y-%m-%d"))
    output_dir = luigi.Parameter(default="./DailyRunWF/Output/")
    def output(self):
        return luigi.LocalTarget(self.output_dir + "FinalReport_"+self.dat+".csv")
class EveningFile_check(luigi.Task):
    dat = str(date.today().strftime("%Y-%m-%d"))
    output_dir = luigi.Parameter(default="./DailyRunWF/Output/")
    def output(self):
        return luigi.LocalTarget(self.output_dir + "FinalReport_"+self.dat+"_1.csv")
class Reportmerge_workflow(luigi.Task):
    input_dir = luigi.Parameter(default="./DailyRunWF/Output/")
    output_dir = luigi.Parameter(default="./ReportMergeWF/Output/")
    dat = str(date.today().strftime("%Y-%m-%d"))
    def output(self):
        return luigi.LocalTarget(self.output_dir + "PREIPO_Final_Report_"+self.dat+".csv")
    def run(self):
        merge_reports.merge_reports(self.input_dir,self.output_dir)
    def requires(self):
        return [MorningFile_check(output_dir = self.input_dir),EveningFile_check(output_dir = self.input_dir)]


# python -m luigi --module reportmerge_workflow Reportmerge_workflow --local-scheduler 