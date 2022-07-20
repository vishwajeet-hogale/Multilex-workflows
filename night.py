import luigi 
from UpdateDatabaseWF.uploaddatabase_workflow import *
from Mail.mail import sendemail
from datetime import date
root = "E:\\luigi\\"
class NightPipeline(luigi.Task):
    input_dir = luigi.Parameter(root + "Output\\")
    dat = str(date.today().strftime("%Y-%m-%d"))
    def output(self):
        return luigi.LocalTarget(self.input_dir + "PREIPO_Final_Report_"+ self.dat +".xlsx")
    def run(self):
        sendemail("sharikavallambatlapes@gmail.com",["vishwajeethogale307@gmail.com","sharikavallambatla@gmail.com"],"Greetings Team,\n\nThe final report is attcahed to this email.\nRegards,\nVishwajeet Hogale","Report for "+self.dat , self.input_dir + "PREIPO_Final_Report_"+self.dat+".csv")
    def requires(self):
        return removeduplicate_workflow(input_dir = self.input_dir)