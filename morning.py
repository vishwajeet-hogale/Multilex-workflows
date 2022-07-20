import luigi 
from DailyRunWF.run_workflow import *
from DailyRunWF.Pipeline.DataPreprocess import datapreprocess

root = "E:\\luigi\\"
class MorningPipeline(luigi.Task):
    input_dir = luigi.Parameter(default=root + "DailyRunWF\\Output\\")
    output_dir = luigi.Parameter(default=root + "DailyRunWF\\Output\\")
    dat = str(date.today().strftime("%Y-%m-%d"))
    file_name = "EDI_PREIPO_report.csv"
    dat = str(date.today().strftime("%Y-%m-%d"))
    def requires(self):
        return [Predict(input_dir = self.output_dir,output_dir = self.output_dir)]
    def run(self):
        datapreprocess.CleanedReport(self.file_name,input_dir=self.input_dir[0:-1],output_dir=self.output_dir[0:-1])


if __name__ == "__main__":
    luigi.run(args=MorningPipeline())