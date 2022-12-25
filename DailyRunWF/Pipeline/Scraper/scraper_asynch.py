#                                      Importing modules










from newspaper import Article
import requests
import nltk
nltk.download('punkt')

import logging
from requests_html import HTMLSession
from pathlib import Path
from googletrans import Translator
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
    months = ["Jan", "Feb", "Mar", "Apr", "May", "Jun", "Jul", "Aug", "Sep", "Oct", "Nov", "Dec", "January",
              "February", "March", "April", "May", "June", "July", "August", "September", "October", "November", "December"]
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

    def get_date_mname_d_y(date):
        # Apr 21, 2022
        # 21 Apr 2022
        month = re.findall(
            r'''(Jan(uary)?|Feb(ruary)?|Mar(ch)?|Apr(il)?|May|Jun(e)?|Jul(y)?|Aug(ust)?|Sep(tember)?|Oct(ober)?|Nov(ember)?|Dec(ember)?)''', date)
        m = str(months.index(month[0][0].strip()) % 12 + 1)
        y = str(re.findall(r'\d{4}', date)[0])
        day = str(re.findall(r'\d{1,2}', date)[0])
        return "-".join([day, m, y])

    def get_date_min_read(date):
        # 2min read . Updated: 21 Apr 2022, time
        return get_date_mname_d_y(date.split(":")[1].split(",")[0].strip())

    def correct_publish_date(i):
        try:
            i = str(i)
            i = i.strip()
            if len(re.findall("\d{1,2}/\d{1,2}/\d{4}", i)):
                hi = re.findall("\d{1,2}/\d{1,2}/\d{4}", i)
                l1 = hi[0].split("/")
                temp = l1[0]
                l1[0] = l1[1]
                l1[1] = temp
                i = "-".join(l1)
                return i
            elif (re.findall("\d{1,2}/\w{3}/\d{4}", i)):
                i = get_date_mname_d_y(re.findall("\d{1,2}/\w{3}/\d{4}", i)[0])
                return i
            elif (len(re.findall("\d{1,2}\s\w{3}\s\d{4}", i))):

                i = get_date_mname_d_y(re.findall(
                    "\d{1,2}\s\w{3}\s\d{4}", i)[0])
                # print(i)
                return i
            elif (re.findall(r'min read . Updated:', i)):
                i = get_date_min_read(i)
                return i
            elif (len(i.split(".")) == 3):
                if (len(i.split(".")[0]) == 4):
                    i = "-".join(i.split(".")[::-1])
                    return i
                else:
                    i = i.replace(".", "-")
                    return i
            elif len(re.findall(r'\d{1,2}.\d{1,2}.\d{4}', i)) and i.find(":"):
                if len(i.split(" ")) > 1:
                    i = i.split(" ")[2].replace(".", "-")
                    return i
            elif (re.findall(r'\d{1,2}-\d{1,2}-\d{4}', i)):
                return i

            elif (i.count(":") >= 2):
                if len(re.findall(r'T', i)):
                    i = "-".join(i.split("T")[0].split("-")[::-1])
                    return i
                if len(re.findall(r'Newswire', i)):
                    i = "-".join(i.strip().split(" ")[-3].split("-")[::-1])
                    return i
                i = i.split(" ")[0].strip()
                if len(re.findall(r'[a-zA-Z]+', i)):
                    i = get_date_mname_d_y(i)
                else:
                    i = "-".join(i.split("-")[::-1])
                    return i
            elif len(i.split("-")[0]) == 4:
                i = "-".join(i.split("-")[::-1])
                return i

            i = get_date_mname_d_y(i)
            return i
        except:
            i = i.strip()

            i = translate(i)
            month = re.findall(
                r'''(Jan(uary)?|Feb(ruary)?|Mar(ch)?|Apr(il)?|May|Jun(e)?|Jul(y)?|Aug(ust)?|Sep(tember)?|Oct(ober)?|Nov(ember)?|Dec(ember)?)''', i)
            if not len(month):
                i = "Date"
                return i
            m = str(months.index(month[0][0].strip()) % 12 + 1)
            y = str(re.findall(r'\d{4}', i)[0])
            day = str(re.findall(r'\d{1,2}', i)[0])
            i = "-".join([day, m, y])
            return i

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
                    row["publish_date"] = correct_publish_date(
                        str(row["publish_date"]))
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
                df_final['publish_date'], format="%d-%m-%Y", errors='coerce', utc=True).dt.strftime("%d/%b/%Y" " " "%H:%M:%S")
            one_year_from_now = datetime.now()
            date_formated = one_year_from_now.strftime(
                "%d/%b/%Y" " " "%H:%M:%S")
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
            final["title"] = final["title"].str.replace(' b ',' ')
            final["text"] = final["text"].str.replace(' b ',' ')
            final["title"] = final["title"].str.replace(' B ',' ')
            final["text"] = final["text"].str.replace(' B ',' ')
            key_1_gram = ['IPO', 'IPO', 'IPO ', 'SPACs', 'ipo', 'pre-IPO',
                          'pre-ipo', 'PRE-IPO', 'pre-IPO', 'spac', 'shares', 'pre ipo']
            key_2_gram = ['IPO Calendar','Shelves IPO','Halts IPO','IPO Pipeline','Withdraws IPO','Eyes IPO','IPO-Bound','IPO Registration','Red Herring','Pre-Initial Public','Pre-IPO announcement','IPOs scheduled','IPO scheduled','offering ipo', "listed on", "go public", "plan to", "going public",
                          "offering shares", "initial public", "public offering", "have listed", "files for"]
            key_3_gram = ['Begins IPO Process','Set to IPO','IPO open for','Open for subscription','Prices IPO','Expected IPO Filings','Files for IPO','Upcoming IPO',"an initial public", "offer its shares", "to the public", "going to list",
                          "files for ipo", "filed for ipo", "initial public offering", "public offering ipo"]
            key_4_gram = ['Gets nod for IPO','Fixed a price band','Sets IPO Price Band','Planning to go public','Preparing to go public','IPO to be launched',"an initial public offering", "the initial public offering", "its initial public offering","initial public offering ipo", 
                          "The Initial Public Offering", "Its Initial Public Offering ", "Has Set Its Ipo", "Targeting A 2023 Ipo"]
            key_5_gram = ["Planning An Initial Public Offering", "Files A Prospectus For Ipo", "Considering An Initial Public Offering",'for an initial public offering']

            key_6_gram = [ 'sebagai ungkapan terimakasih atas perhatian anda', 'ungkapan terimakasih atas perhatian anda tersedia', 'terimakasih atas perhatian anda tersedia voucer', 'atas perhatian anda tersedia voucer gratis', 'perhatian anda tersedia voucer gratis senilai', 'anda tersedia voucer gratis senilai donasi',
                          'tersedia voucer gratis senilai donasi yang', 'voucer gratis senilai donasi yang bisa', 'gratis senilai donasi yang bisa digunakan', 'senilai donasi yang bisa digunakan berbelanja', 'donasi yang bisa digunakan berbelanja di', 'b initial public offering b b', 'b initial public offering b of', 'initial public offering b b ipo', 'public offering b b ipo b', 'the b initial public offering b', "Will Hold An Initial Public Offering", "On Its Potential Initial Public Offering"]
            key_7_gram = ["Has Filed For An Initial Public Offering",'sebagai ungkapan terimakasih atas perhatian anda tersedia', 'ungkapan terimakasih atas perhatian anda tersedia voucer', 'terimakasih atas perhatian anda tersedia voucer gratis', 'atas perhatian anda tersedia voucer gratis senilai', 'perhatian anda tersedia voucer gratis senilai donasi', 'anda tersedia voucer gratis senilai donasi yang', 'tersedia voucer gratis senilai donasi yang bisa', 'voucer gratis senilai donasi yang bisa digunakan', 'gratis senilai donasi yang bisa digunakan berbelanja', 'senilai donasi yang bisa digunakan berbelanja di'
                          , 'dapat voucer gratis sebagai ungkapan terimakasih atas', 'voucer gratis sebagai ungkapan terimakasih atas perhatian', 'gratis sebagai ungkapan terimakasih atas perhatian anda', 'donasi yang bisa digunakan berbelanja di dukungan', 'yang bisa digunakan berbelanja di dukungan anda', 'bisa digunakan berbelanja di dukungan anda akan', "Raise Funds Through An Initial Public Offering"]
            key_8_gram = []
            title, link, published_date, scraped_date, text = [], [], [], [], []
            for i, row in final.iterrows():
                cases = [0]*8
                article = str(str(row["title"]) + " " +
                              str(row["text"])).lower()
                # print(article + "\n\n\n\n")
                text_list = [article]
                key_1_gram = conver_to_lower(key_1_gram)
                key_2_gram = conver_to_lower(key_2_gram)
                key_3_gram = conver_to_lower(key_3_gram)
                key_4_gram = conver_to_lower(key_3_gram)
                key_5_gram = conver_to_lower(key_3_gram)
                key_6_gram = conver_to_lower(key_3_gram)
                key_7_gram = conver_to_lower(key_3_gram)
                # key_8_gram = conver_to_lower(key_3_gram)

                res_1_gram = tokenize_no_words(text_list, 1)
                res_2_gram = tokenize_no_words(text_list, 2)
                res_3_gram = tokenize_no_words(text_list, 3)
                res_4_gram = tokenize_no_words(text_list, 4)
                res_5_gram = tokenize_no_words(text_list, 5)
                res_6_gram = tokenize_no_words(text_list, 6)
                res_7_gram = tokenize_no_words(text_list, 7)
                # res_8_gram = tokenize_no_words(text_list, 8)
                if (len(res_1_gram.intersection(key_1_gram)) > 0):
                    cases[0] = 1
                if (len(res_2_gram.intersection(key_2_gram)) > 0):
                    cases[1] = 1
                if (len(res_3_gram.intersection(key_3_gram))):
                    cases[2] = 1
                if (len(res_4_gram.intersection(key_4_gram))):
                    cases[3] = 1
                if (len(res_5_gram.intersection(key_5_gram))):
                    cases[4] = 1
                if (len(res_6_gram.intersection(key_6_gram))):
                    cases[5] = 1
                if (len(res_7_gram.intersection(key_7_gram))):
                    cases[6] = 1
                # if (len(res_8_gram.intersection(key_8_gram))):
                #     cases[7] = 1
                if (cases[0] and (cases[1] or cases[2] or cases[3] or cases[4] or cases[5] or cases[6] )):
                    title.append(final['title'][i])
                    link.append(final['link'][i])
                    published_date.append(final['publish_date'][i])
                    scraped_date.append(final['scraped_date'][i])
                    text.append(final['text'][i])
                cases = [0]*8
            final = pd.DataFrame(list(zip(title, link, published_date, scraped_date, text)),
                                 columns=['title', 'link', 'publish_date', 'scraped_date', 'text'])
            final = final[~final['title'].isin(
                ["private placement", "reverse merger", "blank check merger"])]
            final = final[~final['text'].isin(
                ["private placement", "reverse merger", "blank check merger"])]
            # final.to_csv("Newshab.csv")
            return final
        except:
            print("Issue in Filter Function")

    def log_errors(err_logs):
        for i in err_logs:
            print(i)





#                                      Korean_Websites



            
    def korea():
        try:
            print("Korea")
            err_logs = []
            url = "http://www.koreaherald.com/search/index.php?kr=0&q=IPO"
            domain_url = "http://www.koreaherald.com/"
            title, links, text, pub_date, scraped_date = [], [], [], [], []
            try:
                page = requests.get(url)
                soup = BeautifulSoup(page.content, "html.parser")


            except:
                err = "Korea : err : Couldn't fetch " + url
                err_logs.append(err)
                return
            for a in soup.find_all('ul', {'class': 'main_sec_li'}):
                for l in a.find_all('a', href=True):
                    links.append(domain_url + l["href"])

            final_links = []
            today = date.today()
            
            for link in links:
                try:
                    article = Article(link)
                    article.download()
                    article.parse()
                    article.nlp()
                except:
                    err = "Korea : err : Couldn't fetch url " + link
                    err_logs.append(err)

                    continue
                pub_date.append(article.publish_date)
                # Title of article
                title.append(article.title)
                # Text of article
                text.append(article.text)
                # print(text)
                # Scrapped date
                scraped_date.append(str(today))
                # Working links
                final_links.append(link)
            
            df = pd.DataFrame({"text": text, "link": final_links,
                              "publish_date": pub_date, "scraped_date": scraped_date, "title": title})
            
            if df.empty:
                err = "Korea : err: Empty dataframe"
                err_logs.append(err)
            
            df = df.drop_duplicates(subset=["link"])
            df = FilterFunction(df)
            emptydataframe("Korea", df)
            
            return df
        except:
            print("Korea not working")
            not_working_functions.append('Korea')
        
        
