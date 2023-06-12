from newspaper import Article, Config
import requests
import nltk
#nltk.download('punkt')                         # Please uncomment if you're running this program for first time
import threading
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.service import Service as ChromeService
from webdriver_manager.chrome import ChromeDriverManager
import random

import logging
from requests_html import HTMLSession
from pathlib import Path
from googletrans import Translator
from deep_translator import GoogleTranslator
import re
import json
import time
import os
import pandas as pd
from bs4 import BeautifulSoup
from datetime import datetime, date, timedelta
from newspaper import Article
import importlib.util
import warnings
import pytz
from advertools import word_tokenize
from urllib.request import Request as rs, urlopen
import urllib3
import urllib.parse
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)





#                      Header functions







warnings.simplefilter("ignore", UserWarning)
logging.basicConfig(level=logging.INFO,
                    format="%(asctime)s - %(process)d - %(name)s - %(levelname)s - %(message)s")
logging.info("first line of multilex_scraper_xform")


def infin_transform_all_objects(input_dir, output_dir, **kwargs):
    logging.info("input_dir=" + input_dir + ", output_dir=" + output_dir)
    # onlyfiles = [f for f in os.listdir(input_dir) if os.path.isfile(os.path.join(input_dir, f))]
    # for f in onlyfiles:
    #  logging.info("file in directory %s = %s. size = %d", input_dir, os.path.join(input_dir, f), Path(os.path.join(input_dir, f)).stat().st_size)
    for path, subdirs, files in os.walk(input_dir):
        for name in files:
            logging.info("file in directory %s = %s. size = %d", path, os.path.join(
                path, name), Path(os.path.join(path, name)).stat().st_size)

    #s1 = dynamic_module_import(os.path.join(input_dir, "s1.py"), "s1")

    multilex_scraper(input_dir, output_dir)


def dynamic_module_import(file_path, module_name):
    spec = importlib.util.spec_from_file_location(module_name, file_path)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)

    logging.info("dynamically loaded module %s contents = %s",
                 file_path, dir(module))

    return module


def multilex_scraper(input_dir, output_dir):
    cur_date = str(date.today())
    not_working_functions = []
    log_format = (
        '[%(asctime)s] %(levelname)-8s %(name)-12s %(message)s')

    def emptydataframe(name, df):
        if df.empty:
            not_working_functions.append(name+" : err : Empty datframe")
    
    formats = [
            '%d-%m-%Y', '%d/%m/%Y', '%d %m %Y',
            '%d-%b-%Y', '%d/%b/%Y', '%d %b %Y',
            '%d-%B-%Y', '%d/%B/%Y', '%d %B %Y',
            '%Y-%m-%d', '%Y/%m/%d', '%Y %m %d',
            '%Y-%b-%d', '%Y/%b/%d', '%Y %b %d',
            '%Y-%B-%d', '%Y/%B/%d', '%Y %B %d',
            '%B %d, %Y', '%b %d, %Y',
            '%m-%d-%Y', '%m/%d/%Y', '%m %d %Y',
            '%b-%d-%Y', '%b/%d/%Y', '%b %d %Y',
            '%B-%d-%Y', '%B/%d/%Y', '%B %d %Y'
        ]

    regexes = []
    for fmt in formats:
        # Replace %d, %m, %b, %B, and %Y with regular expression patterns
        regex = fmt.replace(r'%d', r'([1-9]|0[1-9]|[1-2][0-9]|3[0-1])')
        regex = regex.replace(r'%m', r'([1-9]|0[1-9]|1[0-2])')
        regex = regex.replace(r'%b', r'(Jan|Feb|Mar|Apr|May|Jun|Jul|Aug|Sep|Oct|Nov|Dec)')
        regex = regex.replace(r'%B', r'(January|February|March|April|May|June|July|August|September|October|November|December)')
        regex = regex.replace(r'%Y', r'\d{4}')
        regex = regex.replace(r" ", r"\s")
        regex = r"\b"+regex+r"\b"
        regexes.append(re.compile(regex, re.IGNORECASE))
        
    
    

    
    logging.basicConfig(
        level=logging.DEBUG,
        format=log_format,
        filename=os.path.join(output_dir, 'debug.log'),
    )

    def get_time_valid():  # Returns the hour from the time
        IST = pytz.timezone('Asia/Kolkata')
        time = datetime.now(IST)
        time = time.time()
        return time.hour

    def translate(text):
        translator = Translator()
        translation = translator.translate(text, dest='en')
        return translation.text
    
    def translatedeep(text):
        translation = GoogleTranslator(source='auto', target='en').translate(text)
        return translation

    def translate_dataframe(df):
        try:
            for i, row in df.iterrows():
                # row["publish_date"]= translate(row["publish_date"])
                row["title"] = translate(row["title"])
                row["text"] = translate(row["text"])

                # time.sleep(0.2)
            return df
        except:
            for i, row in df.iterrows():
                # row["publish_date"]= translate(row["publish_date"])
                row["title"] = translate(row["title"])
                # row["text"] = translate(row["text"])

                # time.sleep(0.2)
            return df

    def correct_link(link):
        link = str(link)
        if (link.find("&ct") != -1):
            link = link.split("&ct")[0]
        return link

    def correct_publish_date(i):
        try:
            i = str(i)
            i = i.strip()
            if ("/" in i) or ("-" in i):
                i = "".join(i.split())
            
        
            for index, regex in enumerate(regexes):
                for match in regex.finditer(i):
                    date_string = match.group()
                    return datetime.strptime(date_string, formats[index]).strftime("%d-%m-%Y")
            return "Date"
        except:
            return "Date"

    def correct_navigable_string(df1):
        try:
            err = []
            for i, row in df1.iterrows():
                try:
                    if (row["publish_date"] == None):
                        row["publish_date"] = "Date"
                        continue

                    soup = BeautifulSoup('''
                    <html>
                        ''' + str(row["publish_date"]) + '''
                    </html>
                    ''', "lxml")

                # Get the whole h2 tag
                    row["publish_date"] = str(soup.p.string)
                    row["publish_date"] = str(row["publish_date"]).strip()
                    row["publish_date"] = str(row["publish_date"]).encode("utf-8", "ignore").decode("utf-8")
                    row["publish_date"] = correct_publish_date(
                        str(row["publish_date"]))
                    row["text"] = row["text"].replace("â€™", "'")
                    row["title"] = row["title"].replace("â€™", "'")
                    row["link"] = correct_link(str(row["link"]))
                except:
                    #     # print(row)
                    #     # print("\n")
                    err.append(i)
            print(err)
            df_final = df1
            # df2 = pd.DataFrame(columns=["title","link","publish_date","scraped_date","text"])
            # if "Date" in df_final["publish_date"].tolist():
            df2 = df_final[df_final["publish_date"] == "Date"]
            df_final = df_final[df_final["publish_date"] != "Date"]
            df_final['publish_date'] = pd.to_datetime(
                df_final['publish_date'], format="%d-%m-%Y", errors='coerce', utc=True).dt.strftime("%d/%m/%Y" " " "%H:%M:%S")
            one_year_from_now = datetime.now()
            date_formated = one_year_from_now.strftime(
                "%d/%m/%Y" " " "%H:%M:%S")
            df_final['scraped_date'] = date_formated
            

            public_date = pd.to_datetime(
                df_final['publish_date'], errors='coerce', utc=True).dt.strftime('%d-%m-%Y')
            scrap_date = pd.to_datetime(
                df_final['scraped_date'], errors='coerce', utc=True).dt.strftime('%d-%m-%Y')

            # morning
            yesterday = (date.today() - timedelta(days=1)).strftime('%d-%m-%Y')
            daybefore = (date.today() - timedelta(days=2)).strftime('%d-%m-%Y')
            final_1 = df_final.loc[public_date == yesterday]
            final_2 = df_final.loc[public_date == scrap_date]
            final_3 = df_final.loc[public_date == daybefore]
            # evening
            fn = []
            if (int(get_time_valid()) >= 16):
                fn = [final_2, df2]
            else:
                fn = [final_1, final_2, final_3, df2]
            final = pd.concat(fn)
            return final
        except:
            return df1

    def conver_to_lower(li):
        return [str(i).lower() for i in li]

    def tokenize_no_words(text_list, val):
        return set(word_tokenize(text_list, val)[0])
    
    def FilterFunction(final):
        
        try:         
            if (final.empty):
                return final
            
            key_1_gram = ['ipo', 'ipo', 'ipo ', 'spacs', 'ipo', 'pre-ipo', 'pre-ipo', 'pre-ipo', 'pre-ipo', 'spac', 'shares', 'pre ipo']
            key_2_gram = ['ipo calendar', 'shelves ipo', 'halts ipo', 'ipo pipeline', 'withdraws ipo', 'eyes ipo', 'ipo-bound', 'ipo registration', 'red herring', 'pre-initial public', 'pre-ipo announcement', 'ipos scheduled', 'ipo scheduled', 'offering ipo', 'listed on', 'go public', 'plan to', 'going public', 'offering shares', 'initial public', 'public offering', 'have listed', 'files for']
            
            key_3_gram = ['begins ipo process', 'set to ipo', 'ipo open for', 'open for subscription', 'prices ipo', 'expected ipo filings', 'files for ipo', 'upcoming ipo', 'an initial public', 'offer its shares', 'to the public', 'going to list', 'files for ipo', 'filed for ipo', 'initial public offering', 'public offering ipo']
            
            key_4_gram = ['gets nod for ipo', 'fixed a price band', 'sets ipo price band', 'planning to go public', 'preparing to go public', 'ipo to be launched', 'an initial public offering', 'the initial public offering', 'its initial public offering', 'initial public offering ipo', 'the initial public offering', 'its initial public offering ', 'has set its ipo', 'targeting a 2023 ipo']
            
            key_5_gram = ['planning an initial public offering', 'files a prospectus for ipo', 'considering an initial public offering', 'for an initial public offering']
            
            key_6_gram = [ 'sebagai ungkapan terimakasih atas perhatian anda', 'ungkapan terimakasih atas perhatian anda tersedia', 'terimakasih atas perhatian anda tersedia voucer', 'atas perhatian anda tersedia voucer gratis', 'perhatian anda tersedia voucer gratis senilai', 'anda tersedia voucer gratis senilai donasi',
                          'tersedia voucer gratis senilai donasi yang', 'voucer gratis senilai donasi yang bisa', 'gratis senilai donasi yang bisa digunakan', 'senilai donasi yang bisa digunakan berbelanja', 'donasi yang bisa digunakan berbelanja di', 'b initial public offering b b', 'b initial public offering b of', 'initial public offering b b ipo', 'public offering b b ipo b', 'the b initial public offering b', "Will Hold An Initial Public Offering", "On Its Potential Initial Public Offering"]
            key_7_gram = ["has filed for an initial public offering",'sebagai ungkapan terimakasih atas perhatian anda tersedia', 'ungkapan terimakasih atas perhatian anda tersedia voucer', 'terimakasih atas perhatian anda tersedia voucer gratis', 'atas perhatian anda tersedia voucer gratis senilai', 'perhatian anda tersedia voucer gratis senilai donasi', 'anda tersedia voucer gratis senilai donasi yang', 'tersedia voucer gratis senilai donasi yang bisa', 'voucer gratis senilai donasi yang bisa digunakan', 'gratis senilai donasi yang bisa digunakan berbelanja', 'senilai donasi yang bisa digunakan berbelanja di'
                          , 'dapat voucer gratis sebagai ungkapan terimakasih atas', 'voucer gratis sebagai ungkapan terimakasih atas perhatian', 'gratis sebagai ungkapan terimakasih atas perhatian anda', 'donasi yang bisa digunakan berbelanja di dukungan', 'yang bisa digunakan berbelanja di dukungan anda', 'bisa digunakan berbelanja di dukungan anda akan', "Raise Funds Through An Initial Public Offering"]
            key_8_gram = ["listing",'initial public offering','initial public offfering','to go public','goes Public','goes public','restricted shares','traded','list','listed','listing','lifted','allotment','Nyse','will be listed','stock exchange','delisting','moved to','hit','funding','raise','raises','valuation','going public','subscription','spac','sells','stake','debut','fundraising','board','enrollment','trade','hits','revenues','expansion','rebrand','subscribe','purchase','target price','shares','investing','allotmnet','approved','approves','fpo','registration','funds','sebi','investment','offering','nasdaq','files','launch','fund', 'stock', 'stocks', 'aims to', 'explores options', 'spinoff', 'digest', 'securities', "offer price"]
            title, link, published_date, scraped_date, text = [], [], [], [], []
            final["accepted"]=""
            for i, row in final.iterrows():
                
                article = str(row["title"]).lower()
                # print(article + "\n\n\n\n")
                c=0
                for j in key_1_gram:
                    if j in article:
                        c+=1
                        break
                for j in key_2_gram:
                    if j in article:
                        c+=1
                        break
                
                for j in key_3_gram:
                    if j in article:
                        c+=1
                        break
                
                for j in key_4_gram:
                    if j in article:
                        c+=1
                        break
                
                for j in key_5_gram:
                    if j in article:
                        c+=1
                        break
                
                for j in key_8_gram:
                    if j in article:
                        c+=1
                        break
                        
                if(c>0):
                    final.at[i, "accepted"]="Yes"
                else:
                    final.at[i, "accepted"]="No"
                c=0
            final=final[final["accepted"]=="Yes"]
            del final["accepted"]
            final = final.reset_index(drop=True)
            return final
        except:
            print("Issue in Filter Function")


    def log_errors(err_logs):
        for i in err_logs:
            print(i)

    
    def date_correction_for_newspaper3k(date):
        return str(date.strftime("%d/%m/%Y"))
    
    
    Errors={}
    
    def err_dict(link="", published_date="", title="", text=""):
        return {
            "link": link,
            "published_date": published_date,
            "title": title,
            "text": text
        }
    

        
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    df_final_1 = ["some_function()"] #call the function here
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
       
    
    df_final = pd.concat(df_final_1)
    df_final = FilterFunction(df_final)
    df_final.drop_duplicates(subset=["link"])
    df_final.drop_duplicates(subset=["title"])
    
    print(df_final)

    
    todays_report_filename = os.path.join(output_dir, 'todays_report.csv')
    todays_report_filename1 = os.path.join(output_dir, 'todays_report1.csv')
    
    
    df_final.to_csv(todays_report_filename1, index=False)
    final = correct_navigable_string(df_final)
    
    
    # final = FilterFunction(final)
    final.to_csv(todays_report_filename, index=False)
    
    
    
    logfile = ""
    if(get_time_valid() < 16):
        logfile = input_dir + "/logs.txt"
    else:
        logfile = input_dir + "/logs1.txt"
    textfile = open(logfile, "w")
    for i in not_working_functions:
        textfile.write(i+"\n")
    textfile.close()
    
    logging.info("writing output artifact " +
                 todays_report_filename + " to " + output_dir)
    final.to_csv(todays_report_filename, index=False)
    logging.info("completed writing output artifact " +
                 todays_report_filename + " to " + output_dir)
    
    err_file=""
    if(get_time_valid() < 16):
        err_file = input_dir + "/brief_err_file.txt"
    else:
        err_file = input_dir + "/brief_err_file.txt"
        
    with open(err_file, 'w', encoding='utf-8') as f:
        for key, value in Errors.items():
            if len(value)!=0:
                
                if type(value[0])==str:
                    f.write('%s : %s ' % (key, value[0]))
                else:
                    f.write(key+"\n\n")
                    for val in value:
                        for data, corr in val.items():
                            f.write('\t\t %s : %s \n' % (data, corr))
                        f.write("\n")
                
                f.write("\n\n--------------------------------------------------------------------------\n\n")
                
# multilex_scraper( "", "")
logging.info("last line of scraper")

if __name__ == "__main__":
    x=time.time()
    multilex_scraper(r"C:\Users\ujwal\OneDrive\Desktop\abc",r"C:\Users\ujwal\OneDrive\Desktop\abc")   
    y=time.time()
    print()
    print()
    print("time taken by scraper.py: ", y-x)
    print()
    print()