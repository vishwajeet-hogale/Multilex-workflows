import luigi
from InitialSetupWF.AddDataToDBFromDumpFileWF.addDataToDb_workflow import AddDataToDbWorkflow

class InitialSetupWorkflow(luigi.Task):
    input_dir = luigi.Parameter('E:\\luigi\\')
    output_dir = luigi.Parameter('E:\\luigi\\')
    def run(self):
        print("Dump creation and upload successful!")
    def requires(self):
        return AddDataToDbWorkflow(input_dir = self.input_dir,output_dir = self.output_dir)
        