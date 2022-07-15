import luigi 
from datetime import date
from Pipeline.Scraper import scraper
from Pipeline.Prediction import predict
from Pipeline.DataPreprocess import datapreprocess

class Scraper(luigi.Task):
    # input_dir = luigi.Parameter(default="./Pipeline/Scraper/")
    output_dir = luigi.Parameter(default="./Output/")
    
    def output(self):
        return luigi.LocalTarget(self.output_dir+"todays_report.csv")
    def run(self):
        scraper.multilex_scraper(self.output_dir[0:-1],self.output_dir[0:-1])

class Predict(luigi.Task):
    input_dir = luigi.Parameter(default="./Output/")
    output_dir = luigi.Parameter(default="./Output/")
    def requires(self):
        return [Scraper(output_dir = self.output_dir)]
    def output(self):
        return luigi.LocalTarget(self.output_dir + "EDI_PREIPO_report.csv")
    def run(self):
        predict.NERModel_lg(input_dir=self.output_dir[0:-1],output_dir=self.output_dir[0:-1])


class Run_workflow(luigi.Task):
    input_dir = luigi.Parameter(default="./Output/")
    output_dir = luigi.Parameter(default="./Output/")
    dat = str(date.today().strftime("%Y-%m-%d"))
    file_name = "EDI_PREIPO_report.csv"
    def requires(self):
        return [Predict(input_dir = self.output_dir,output_dir = self.output_dir)]
    # def output(self):
    #     return luigi.LocalTarget(self.output_dir + "FinalReport_"+self.dat+".csv")
    def run(self):
        datapreprocess.CleanedReport(self.file_name,input_dir=self.input_dir[0:-1],output_dir=self.output_dir[0:-1])

# class Run_workflow(luigi.Task):
#     run_data = luigi.Parameter(default="Morning")
#     def requires(self):
#         return [DataPreprocess()]
#     def run(self):
#         print(str(self.run_data) + " is successful!!!!!")


# E: & cd luigi/DailyRunWF & python -m luigi --module run_workflow Run_workflow --local-scheduler