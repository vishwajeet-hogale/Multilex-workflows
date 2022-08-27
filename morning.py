import luigi 
from DailyRunWF.run_workflow import *
from DailyRunWF.Pipeline.DataPreprocess import datapreprocess
import os
root = "C:\\Multilex-workflows\\"
class MorningPipeline(luigi.Task):
    input_dir = luigi.Parameter(default=root + "DailyRunWF\\Output\\")
    output_dir = luigi.Parameter(default=root + "DailyRunWF\\Output\\")
    dat = str(date.today().strftime("%Y-%m-%d"))
    dat = str(date.today().strftime("%Y-%m-%d"))
    file_name = "FinalReport_"+dat+".csv"
    file_name1 = "EDI_PREIPO_report.csv"
    def output(self):
        return luigi.LocalTarget(self.output_dir + self.file_name)
    def requires(self):
        return Predict(input_dir = self.output_dir,output_dir = self.output_dir)
    def run(self):
        datapreprocess.CleanedReport(self.file_name1,input_dir=self.output_dir[0:-1],output_dir=self.output_dir[0:-1])
        if os.path.isfile(self.output_dir + "todays_report.csv"):
            os.remove(self.output_dir + "todays_report.csv")
        if os.path.isfile(self.output_dir + self.file_name1):
            os.remove(self.output_dir + self.file_name1)
        

# if __name__ == "__main__":
    # luigi.run(args=MorningPipeline())