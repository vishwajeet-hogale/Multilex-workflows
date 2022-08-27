from os import remove
import luigi 
from RemovePastThreeDaysDuplicatesWF.remove_data import *
from datetime import date
class removeDataWorkflow(luigi.Task):
    input_dir = luigi.Parameter(default="C:\\Multilex-workflows\\ReportMergeWF\\Output\\")
    # input_dir = "E:\\luigi\\DailyRunWF\\Output\\"
    output_dir = luigi.Parameter(default="C:\\Multilex-workflows\\RemovePastThreeDaysDuplicatesWF\\Output\\")
    dat =str(date.today().strftime("%Y-%m-%d"))
    def requires(self):
        return luigi.LocalTarget(self.output_dir + "PREIPO_Final_Report_" + self.dat + ".csv")
    def run(self):
        remove_duplicates_from_todays_file(self.input_dir,self.output_dir)
    