from datetime import date, datetime
from encodings.utf_8 import encode
import pymysql
import pandas as pd
<<<<<<< Updated upstream
=======
from soupsieve import select
>>>>>>> Stashed changes
from sqlalchemy import create_engine
# from decouple import os.environ.get 
import re
import os
from nltk import bigrams,trigrams,ngrams
from advertools import word_tokenize
TABLES = {}
def setup_connection():
    user = 'root'
    DB_PASSWORD = 'Mjklop@0987'
    DB_PORT = 3306
    passw = DB_PASSWORD
    host =  'localhost'
    port = DB_PORT
    database = 'preipo'
    conn = pymysql.connect(host=host,port=port,user=user,passwd=passw,db=database)
    return conn
def get_table(table_name):
    conn = setup_connection()
    # initial_setup()
    cur = conn.cursor()
    data = cur.execute(f"SELECT * FROM {table_name}")
    cur.close()
    conn.close()
    return data
def create_task_table_if_not_exists():
    conn = setup_connection()
    print(conn)
    TABLES['Tasks'] = (
    "CREATE TABLE IF NOT EXISTS `Tasks` ("
    "  `id` int(11) NOT NULL AUTO_INCREMENT,"
    "  `Task_name` VARCHAR(200) NOT NULL,"
    "  `Assigned` varchar(14) NOT NULL,"
    "  `Status` varchar(16) NOT NULL,"
    "  PRIMARY KEY (`id`)"
    ") ENGINE=InnoDB")
    cur = conn.cursor()
    cur.execute(TABLES["Tasks"])
    cur.close()
    conn.close()

def get_source(i):
  try:
    first = i.split("/")[2]
    if first.startswith("www"):
      return "".join(first.split(".")[1:-1])
    else:
      return "".join(first.split(".")[0:-1])
  except:
    return "#"
def create_instance_table_if_not_exists():
    conn = setup_connection()
    print(conn)
    TABLES['Instance'] = (
    "CREATE TABLE IF NOT EXISTS `Tasks` ("
    "  `id` int(11) NOT NULL AUTO_INCREMENT,"
    "  `User_name` VARCHAR(200) NOT NULL,"
    "  `Time_Of_Login` TIME NOT NULL,"
    "  `Date` DATE NOT NULL,"
    "  PRIMARY KEY (`id`)"
    ") ENGINE=InnoDB")
    cur = conn.cursor()
    cur.execute(TABLES["Instance"])
    cur.close()
    conn.close()

def create_user_table_if_not_exists():
    conn = setup_connection()
    print(conn)
    TABLES['User'] = (
    "CREATE TABLE IF NOT EXISTS `User` ("
    "  `id` int(11) NOT NULL AUTO_INCREMENT,"
    "  `email` VARCHAR(200) NOT NULL,"
    "  `password` varchar(14) NOT NULL,"

    "  PRIMARY KEY (`id`)"
    ") ENGINE=InnoDB")
    cur = conn.cursor()
    cur.execute(TABLES["User"])
    cur.close()
    conn.close()
def create_source_table_if_not_exists():
    conn = setup_connection()
    print(conn)
    TABLES['News_source'] = (
    "CREATE TABLE IF NOT EXISTS `News_source` ("
    "  `id` int(11) NOT NULL AUTO_INCREMENT,"
    "  `name` VARCHAR(200) NOT NULL,"
    "  `comment` varchar(14) ,"
    "   `present` int DEFAULT 0,"
    "  PRIMARY KEY (`id`)"
    ") ENGINE=InnoDB")
    cur = conn.cursor()
    cur.execute(TABLES["News_source"])
    cur.close()
    conn.close()
def initial_setup():
    create_task_table_if_not_exists()
    create_user_table_if_not_exists()
    create_source_table_if_not_exists()
def addfile(filename,type="csv"):
    
    df =pd.read_csv(filename) #fix this 
    df = df.iloc[: , 1:]
    # print(preipo)
    df = df.fillna(" ")
    df = df.drop_duplicates(subset=["title","text","link"])
    conn = setup_connection()
    TABLES['Multilex'] = (
    """CREATE TABLE Multilex (
                    `id` INT NOT NULL AUTO_INCREMENT, 
                    `publish_date` DATE NOT NULL,
                    `scraped_date` VARCHAR(100) NOT NULL,
                    `title` VARCHAR(200) NOT NULL,
                    `text` VARCHAR(5000),
                    `Companies` VARCHAR(100) NOT NULL,
                    `Country` VARCHAR(50) NOT NULL,
                    `Listing` VARCHAR(500),
                    `link` VARCHAR(500),
                    `Comments` VARCHAR(500),
                    `Update_news` VARCHAR(500),
                    `Exchange` VARCHAR(500),
                    `source_name` int,
                    PRIMARY KEY (`id`),
                    FOREIGN KEY (`source_name`) REFERENCES News_source (`id`)
                    ON UPDATE CASCADE) ENGINE=InnoDB""")
    cursor = conn.cursor()
    cursor.execute('DROP TABLE IF EXISTS Multilex;')
    print('Creating table....')
    cursor.execute(TABLES["Multilex"])
    print("Multilex table is created....")
  
    err_rows = []
    for i,row in df.iterrows():
        # print(row["publish_date"])
        try:
            # print(row)
            sql = "INSERT INTO preipo.Multilex(publish_date,scraped_date,title,text,Companies,Country,Listing,link,comments,`Update_news`,`Exchange`,`source_name`) VALUES (%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s)"
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
            print("Record inserted")
            """the connection is not autocommitted by default, so we 
            must commit to save our changes"""
            conn.commit()
        except:
            err_rows.append(str(i) + " " + str(row["publish_date"]) + "  " + str(row["Companies"]))
    textfile = open("error_rows.txt","w")
    for val,i in enumerate(err_rows):
        try:
            textfile.write(str(i))
            textfile.write("\n")
        except:
            print(val)
    # print(err_rows)
    textfile.close()
    cursor.close()
    conn.close()
    # except:
        # print("Error while connecting to MySQL")

def get_all_source_names():
    # initial_setup()
    df = pd.read_csv("Cleaned_datadump.csv")
    data = [get_source(str(i).strip()) for i in df["link"].tolist()]
    sources = list(set(data))
    return sorted(sources)
def add_source_table():
    create_source_table_if_not_exists()
    sources = get_all_source_names()
    conn = setup_connection()
    cur = conn.cursor()

    for i in sources:
        sql = "INSERT INTO preipo.News_source(name) VALUES (%s)"
        data = [str(i)]
        cur.execute(sql,data)
        conn.commit()
    cur.close()
    conn.close()

def find_user(email,password):
    conn = setup_connection()
    initial_setup()
    cur = conn.cursor()
    data = cur.execute(f"SELECT email,password FROM preipo.User WHERE email = '{email}' ")
    cur.close()
    conn.close()
    return data

def check_valid_user(email,password):
    conn = setup_connection()
    # initial_setup()
    cur = conn.cursor()
    cur.execute(f"SELECT email,password FROM preipo.User WHERE email = '{email}' && password='{password}'")
    data = cur.fetchone()
    cur.close()
    conn.close()
    print(data)
    return data

def get_source_table():
    conn = setup_connection()
    cur = conn.cursor()
    cur.execute("SELECT * FROM preipo.news_source")
    data = cur.fetchall()
    print(data)
def get_latest_publish_date_in_db():
    conn =setup_connection()
    cur_date = date.today()
    cur_date = str(cur_date.strftime("%Y-%m-%d"))
    cur = conn.cursor()
    cur.execute(f"SELECT publish_date FROM preipo.Multilex WHERE publish_date <= '{cur_date}' ORDER BY publish_date DESC LIMIT 1")
    return cur.fetchall()[0][0]
def clean_df(df):
    columns = df.columns.tolist()
    rows = []
    rows1 = []
    for i,row in df.iterrows():
        try:
            row["publish_date"] = datetime.strptime(str(row["publish_date"]),"%d-%m-%Y")
            rows.append(list(row))
        except:
           
            rows1.append(row)
            continue
    df1 = pd.DataFrame(rows,columns=columns)
    df2 = pd.DataFrame(rows1,columns=columns)
    df2.to_csv("Puberror_datadump.csv")
    # print(df1)
    return df1


def adddatatomultilextable(filename):
    df =pd.read_csv(filename) #fix this 
    df = df.iloc[: , 1:]
    # print(preipo)
    cur_date = date.today()
    cur_date = cur_date.strftime("%Y-%m-%d")
    df = df.fillna(" ")
    df = df.drop_duplicates(subset=["title","text","link"])
    df = clean_df(df)
    df['publish_date'] = pd.to_datetime(df['publish_date'], format="%d-%m-%Y")
    # latest_date = get_latest_publish_date_in_db()
    # df = df[df['publish_date']>latest_date and df['publish_date']<=cur_date]
    print(df)
    # print(df)
    conn = setup_connection()
    # TABLES['Multilex'] = (
    # """CREATE TABLE Multilex (
    #                 `id` INT NOT NULL AUTO_INCREMENT, 
    #                 `publish_date` DATE NOT NULL,
    #                 `scraped_date` VARCHAR(100) NOT NULL,
    #                 `title` VARCHAR(200) NOT NULL,
    #                 `text` VARCHAR(5000),
    #                 `Companies` VARCHAR(100) NOT NULL,
    #                 `Country` VARCHAR(50) NOT NULL,
    #                 `Listing` VARCHAR(500),
    #                 `link` VARCHAR(500),
    #                 `Comments` VARCHAR(500),
    #                 `Update_news` VARCHAR(500),
    #                 `Exchange` VARCHAR(500),
    #                 `source_name` int,
    #                 PRIMARY KEY (`id`),
    #                 FOREIGN KEY (`source_name`) REFERENCES News_source (`id`)
    #                 ON UPDATE CASCADE) ENGINE=InnoDB""")
    # cursor = conn.cursor()
    # cursor.execute('DROP TABLE IF EXISTS Multilex;')
    # print('Creating table....')
    # cursor.execute(TABLES["Multilex"])
    # print("Multilex table is created....")
  
    # err_rows = []
    # for i,row in df.iterrows():
    #     # print(row["publish_date"])
    #     try:
    #         # print(row)
    #         sql = "INSERT INTO preipo.Multilex(publish_date,scraped_date,title,text,Companies,Country,Listing,link,comments,`Update_news`,`Exchange`,`source_name`) VALUES (%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s)"
    #         row["publish_date"] = str(row["publish_date"])
    #         if(len(str(row["text"]))>5000):
    #             row["text"] = row["text"][0:5000]
    #         if(len(str(row["Companies"]))>100):
    #             row["Companies"] = row["Companies"][0:100]
    #         if(row["publish_date"]) == "Date":
    #             # print(1)
    #             if(len(re.findall(r'\d{1,2}/\d{1,2}/\d{4}',row["scraped_date"]))):
    #                   i = re.findall(r'\d{1,2}/\d{1,2}/\d{4}',row["scraped_date"])[0]
    #                   i = i.split("/")
    #                   temp = i[0]
    #                   i[0] = i[1]
    #                   i[1] = temp
    #                   i[2] = "20"+str(i[2])
    #                   row["publish_date"] = "-".join(i)
                      
    #             elif(len(re.findall(r'\d{4}-\d{1,2}-\d{1,2}',row["scraped_date"]))):
    #                   i = re.findall(r'\d{4}-\d{1,2}-\d{1,2}',row["scraped_date"])[0]
    #                   row["publish_date"] = i
    #         if(len(re.findall(r'\d{1,2}-\d{1,2}-\d{4}',row["publish_date"]))):
    #                 i = re.findall(r'\d{1,2}-\d{1,2}-\d{4}',row["publish_date"])[0]
    #                 i = "-".join(i.split("-")[::-1])
    #                 row["publish_date"] = i
                    
            
    #         source = str(get_source(row["link"]))
    #         sid = cursor.execute("select id from preipo.News_source where name = %s",[source])
    #         try:
    #             sid = cursor.fetchall()[0][0]
    #         except:
    #             cursor.execute('''INSERT INTO preipo.News_source VALUES(%s)''',[str(source)])
    #             sid = cursor.execute("select id from preipo.News_source where name = %s",[source])
    #             sid = cursor.fetchall()[0][0]
    #         # print(source + "--->" + str(sid))
    #         print(str(row["publish_date"]) + "--> " + str(row["scraped_date"]) )
    #         data = [str(row["publish_date"]),str(row["scraped_date"]),str(row["title"]),
    #         str(row["text"]),str(row["Companies"]),str(row["Country"]),str(row["Listing"]),str(row["link"]),str(row["Comments"]),str(row["update"]),str(row["Exchange"]),sid]
    #         cursor.execute(sql,data)
    #         print("Record inserted")
    #         """the connection is not autocommitted by default, so we 
    #         must commit to save our changes"""
    #         conn.commit()
    #     except:
    #         err_rows.append(str(i) + " " + str(row["publish_date"]) + "  " + str(row["Companies"]))
    # textfile = open("error_rows.txt","w")
    # for val,i in enumerate(err_rows):
    #     try:
    #         textfile.write(str(i))
    #         textfile.write("\n")
    #     except:
    #         print(val)
    # # print(err_rows)
    # textfile.close()
    # cursor.close()
    # conn.close()

def find_frequent_phrases():
    conn = setup_connection()
    cursor = conn.cursor()
    data = cursor.execute("SELECT title,text from preipo.Multilex")
    data = cursor.fetchall()
    all_articles = " ".join([str(str(i[0]) + " " + str(i[1])).lower() for i in data])
    # b = bigrams(all_articles.split(' '))
    # t = trigrams(all_articles.split(' '))
    gg = word_tokenize([all_articles],2)
    # trigram_measures = nltk.collocations.TrigramAssocMeasures()
    from collections import Counter
    # print(Counter(b).most_common(10))
    # print()
    # print()
    # print()
    # print(Counter(t).most_common(10))
    # print()
    # print()
    # print()
    print([i[0] for i in Counter(gg[0]).most_common(20)])
    # change this to read in your data
    # finder = BigramCollocationFinder.from_words(all_articles)

    # only bigrams that appear 3+ times
    # finder.apply_freq_filter(1)

    # # return the 10 n-grams with the highest PMI
    # print(finder.nbest(bigram_measures.pmi, 10))
    # with open("all_articles.txt","wb") as f:
    #     f.write(all_articles.encode('utf8'))

# populating the database
def basic_setup():
    initial_setup()
    add_source_table()
    addfile("../Cleaned_datadump.csv")
if __name__ == "__main__":
    # print(len(get_all_source_names()))
    # add_source_table()
    # pass
    # get_source_table()
    # basic_setup()
    # adddatatomultilextable("../Cleaned_datadump.csv")
    # df = pd.read_csv("../Cleaned_datadump.csv")
    # clean_df(df)
<<<<<<< Updated upstream
    find_frequent_phrases()
=======
    find_frequent_phrases()
    
select * from preipo.Multilex where publish_date<= '{cur_date}'

import pandas as pd
import glob
import os

joined_files = os.path.join("/home", "*.csv")
joined_list = glob.glob(joined_files)
df = pd.concat(map(pd.read_csv, joined_list), ignore_index=True)
max(publish_date) from preipo.Multilex where publish_date<= '{cur_date}'



import pymysql
dbcon=pymysql.connect("hostname","username","password","database")
try:
    sql_query=pd.read_sql_query(select * from preipo.Multilex where publish_date<= '{cur_date}')
   
    joined_files = os.path.join("/home", "*.csv")
    joined_list = glob.glob(joined_files)
    df = pd.concat(map(pd.read_csv, joined_list), ignore_index=True)

    max(publish_date) from preipo.Multilex where publish_date<= '{cur_date}',dbcon

Df=pd.DataFrame(sql_query)
>>>>>>> Stashed changes
