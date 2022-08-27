import luigi 
from UpdateDatabaseWF.uploaddatabase_workflow import *
from Mail.mail import sendemail
from datetime import date
root = "C:\\Multilex-workflows\\"
class NightPipeline(luigi.Task):
    input_dir = luigi.Parameter(default = root + "Output\\")
    output_dir = luigi.Parameter(default = root + "Output\\")
    dat = str(date.today().strftime("%Y-%m-%d"))
    def output(self):
        return luigi.LocalTarget(self.input_dir +  self.dat +".txt")
    def run(self):
        sendemail("sharikavallambatlapes@gmail.com",["191381679manasaab@gmail.com","sharikavallambatla@gmail.com"],"Greetings Team,\n\nThe final report is attcahed to this email.\nRegards,\nSai Manasa Nadimpalli","Report for "+self.dat , self.input_dir + "PREIPO_Final_Report_"+self.dat+".xlsx")
        # add to CFS
    def requires(self):
        return removeduplicate_workflow(input_dir = self.input_dir,output_dir = self.output_dir)