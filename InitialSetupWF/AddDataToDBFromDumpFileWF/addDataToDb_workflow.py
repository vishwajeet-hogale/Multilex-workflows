import luigi 
from InitialSetupWF.AddDataToDBFromDumpFileWF.addDataDump import uploadDump
from InitialSetupWF.CreateDumpWF.createDump import *
class AddDataToDbWorkflow(luigi.Task):
    input_dir = luigi.Parameter("./Output/")
    output_dir = luigi.Parameter("./Output/")
    def run(self):
        df = create_dataframe(self.input_dir)
        i_dir = self.input_dir + "Cleaned_datadump.csv"
        uploadDump(i_dir)
        print("Upload done!")
    
