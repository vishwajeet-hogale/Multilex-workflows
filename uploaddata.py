import luigi
from Database.db import *
class UploadxlsxDataWorkflow(luigi.Task):
    input_dir = luigi.Parameter('E:\\luigi\\DumpFiles\\')
    output_dir = luigi.Parameter('E:\\luigi\\')
    filename = luigi.Parameter('all_files.xlsx')
    def output(self):
        return luigi.LocalTarget(self.output_dir + "Output\\file_upload_success.txt")
    def run(self):
        # return AddDataToDbWorkflow(input_dir = self.input_dir,output_dir = self.output_dir)
        adddatatomultilextable(self.input_dir,self.filename,2,-1)
        conn = setup_connection()
        cur = conn.cursor()
        cur.execute("SELECT * FROM preipo.Multilex")
        data = len(cur.fetchall())
        if(data > 0):
            with open(self.output_dir + "Output\\file_upload_success.txt","w") as f:
                f.write("Success")
        else:
            with open(self.output_dir + "Output\\file_upload__failure.txt","w") as f:
                f.write("Failure")
        print(self.filename + " upload successful!")
        
        