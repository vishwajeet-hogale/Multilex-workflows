import luigi 
import datetime
from db import *
import re
import pandas as pd

class Uploaddatabase_workflow(luigi.Task):
    input_dir = luigi.Parameter(default="./Output/")
    output_dir = luigi.Parameter(default="./Output/")
    Current_Date = datetime.today()
    Previous_Date = datetime.datetime.today() 
    prev_dat = str(Previous_Date.strftime("%Y-%m-%d"))
    def upload_file_database(self,input_dir,conn):
        df = pd.read_csv(input_dir + "PREIPO_Final_Report_"+self.prev_dat + ".csv")
        cursor = conn.cursor()
        sql = "INSERT INTO preipo.Multilex(publish_date,scraped_date,title,text,Companies,Country,Listing,link,comments,`Update_news`,`Exchange`,`source_name`) VALUES (%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s)"
        err_rows = []
        for i,row in df.iterrows():
            try:
                row["publish_date"] = str(row["publish_date"])
                if(len(str(row["text"]))>5000):
                    row["text"] = row["text"][0:5000]
                if(len(str(row["Companies"]))>100):
                    row["Companies"] = row["Companies"][0:100]
                if(row["publish_date"]) == "Date":
                    # print(1)
                    if(len(re.findall(r'\d{1,2}/\d{1,2}/\d{4}',row["scraped_date"]))):
                        i = re.findall(r'\d{1,2}/\d{1,2}/\d{4}',row["scraped_date"])[0]
                        i = i.split("/")
                        temp = i[0]
                        i[0] = i[1]
                        i[1] = temp
                        i[2] = "20"+str(i[2])
                        row["publish_date"] = "-".join(i)
                        
                    elif(len(re.findall(r'\d{4}-\d{1,2}-\d{1,2}',row["scraped_date"]))):
                        i = re.findall(r'\d{4}-\d{1,2}-\d{1,2}',row["scraped_date"])[0]
                        row["publish_date"] = i
                if(len(re.findall(r'\d{1,2}-\d{1,2}-\d{4}',row["publish_date"]))):
                        i = re.findall(r'\d{1,2}-\d{1,2}-\d{4}',row["publish_date"])[0]
                        i = "-".join(i.split("-")[::-1])
                        row["publish_date"] = i
                source = str(get_source(row["link"]))
                sid = cursor.execute("select id from preipo.News_source where name = %s",[source])
                try:
                    sid = cursor.fetchall()[0][0]
                except:
                    cursor.execute('''INSERT INTO preipo.News_source VALUES(%s)''',[str(source)])
                    sid = cursor.execute("select id from preipo.News_source where name = %s",[source])
                    sid = cursor.fetchall()[0][0]
                # print(source + "--->" + str(sid))
                print(str(row["publish_date"]) + "--> " + str(row["scraped_date"]) )
                data = [str(row["publish_date"]),str(row["scraped_date"]),str(row["title"]),
                str(row["text"]),str(row["Companies"]),str(row["Country"]),str(row["Listing"]),str(row["link"]),str(row["Comments"]),str(row["update"]),str(row["Exchange"]),sid]
                cursor.execute(sql,data)
            except:
                err_rows.append(str(i) + " " + str(row["publish_date"]) + "  " + str(row["Companies"]))
        textfile = open("error_rows.txt","a")
        for val,i in enumerate(err_rows):
            try:
                textfile.write(str(i))
                textfile.write("\n")
            except:
                print(val)
        # print(err_rows)
        textfile.close()
        cursor.close()
    def run(self):
        conn = setup_connection()
        self.upload_file_database(self.input_dir,conn)
        conn.close()

class removeduplicate_workflow(luigi.Task):
    input_dir = luigi.Parameter(default="./Output/")
    output_dir = luigi.Parameter(default="./Output/")
    def run(self):
        conn =setup_connection()
        cursor = conn.cursor()
        sql = """DELETE t1 FROM preipo.Multilex t1
                INNER  JOIN preipo.Multilex t2
                WHERE t1.id < t2.id AND
                    t1.publish_date = t2.publish_date AND
                    t1.text = t2.text AND
                    t1.title = t2.title AND
                    t1.Companies = t2.Companies;"""
        cursor.execute(sql)
        conn.commit()
    def requires(self):
        return [Uploaddatabase_workflow(input_dir=self.input_dir,output_dir=self.output_dir)]