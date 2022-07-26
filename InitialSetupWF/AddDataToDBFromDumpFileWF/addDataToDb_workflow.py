import luigi 
from InitialSetupWF.AddDataToDBFromDumpFileWF.addDataDump import uploadDump
from InitialSetupWF.CreateDumpWF.createDump import *
from Database.db import *
class AddDataToDbWorkflow(luigi.Task):
    input_dir = luigi.Parameter("./Output/")
    output_dir = luigi.Parameter("./Output/")
    # def output(self):
    #     return luigi.LocalTarget(self.output_dir + "Output\\init_setup_success.txt")
    def run(self):
        df = create_dataframe(self.input_dir)
        i_dir = self.input_dir + "Cleaned_datadump.csv"
        uploadDump(i_dir)
        print("Upload done!")
        conn = setup_connection()
        cur = conn.cursor()
        cur.execute("SELECT * FROM preipo.Multilex")
        data = len(cur.fetchall())
        if(data > 0):
            with open(self.output_dir + "Output\\init_setup_success.txt","w") as f:
                f.write("Success")
        else:
            with open(self.output_dir + "Output\\init_setup_failure.txt","w") as f:
                f.write("Failure")
    
