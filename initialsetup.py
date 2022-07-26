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
        # conn = setup_connection()
        # cur = conn.cursor()
        # cur.execute("SELECT * FROM preipo.Multilex")
        # data = len(cur.fetchall())
        # if(data > 0):
        #     with open(self.output_dir + "Output\\init_setup_success.txt","w") as f:
        #         f.write("Success")
        # else:
        #     with open(self.output_dir + "Output\\init_setup_failure.txt","w") as f:
        #         f.write("Failure")
        
            
    def requires(self):
        return AddDataToDbWorkflow(input_dir = self.input_dir,output_dir = self.output_dir)
        