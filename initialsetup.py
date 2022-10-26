import luigi
from InitialSetupWF.AddDataToDBFromDumpFileWF.addDataToDb_workflow import AddDataToDbWorkflow
from Database.db import *
class InitialSetupWorkflow(luigi.Task):
    input_dir = luigi.Parameter('E:\\luigi\\')
    output_dir = luigi.Parameter('E:\\luigi\\')
    def output(self):
        return luigi.LocalTarget(self.output_dir + "Output\\init_setup_success.txt")
    def run(self):
        # return AddDataToDbWorkflow(input_dir = self.input_dir,output_dir = self.output_dir)
        print("Dump creation and upload successful!")
        
        
            
    def requires(self):
        return AddDataToDbWorkflow(input_dir = self.input_dir,output_dir = self.output_dir)
        