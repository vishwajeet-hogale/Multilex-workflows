import luigi 
from UpdateDatabaseWF.uploaddatabase_workflow import *
root = "E:\\luigi\\"
class NightPipeline(luigi.Task):
    input_dir = luigi.Parameter(root + "ReportMergeWF\\Output\\")
    
    