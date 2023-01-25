#                                      Importing modules










from newspaper import Article
import requests
import nltk
#nltk.download('punkt')                         # Please uncomment if you're running this program for first time
import threading
from GoogleNews import GoogleNews
from selenium import webdriver
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.chrome.service import Service as ChromeService

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
import urllib3
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
                i = "-".join(l1)
                return i
            
            elif (re.findall("\d{1,2}/\w{3}/\d{4}", i)):
                i = get_date_mname_d_y(re.findall("\d{1,2}/\w{3}/\d{4}", i)[0])
                return i
            
            elif (re.findall(r'\d{1,2}-\d{1,2}-\d{4}', i)):
                return i
            
            elif len(re.findall(r'\d{1,2}.\d{1,2}.\d{4}', i)) and i.find(":"):
                if len(i.split(" ")) > 1:
                    i = i.split(" ")[2].replace(".", "-")
                    return i
            
            elif len(i.split("-")[0]) == 4:
                i = "-".join(i.split("-")[::-1])
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




    #                                     Country - Korea



            
    def korea():
        try:
            print("Korea")
            Errors["Korea"]=[]
            
            url = "http://www.koreaherald.com/search/index.php?kr=0&q=IPO"
            domain_url = "http://www.koreaherald.com/"
            title, links, text, pub_date, scraped_date = [], [], [], [], []
            
            try:
                page = requests.get(url)
                soup = BeautifulSoup(page.content, "html.parser")


            except:
                print("Korea not working")
                not_working_functions.append('Korea')
                err = "Main link did not load: " + url
                Errors["Korea"].append(err)
                return
            
            try:
                for a in soup.find_all('ul', {'class': 'main_sec_li'}):
                    for l in a.find_all('a', href=True):
                        links.append(domain_url + l["href"])
            except:
                if len(links)==0:
                    print("Korea not working")
                    not_working_functions.append('Korea')
                    Errors["Korea"].append("Extraction of link not working.")
                    return
                    

            final_links = []
            today = date.today()
            
            def getartciles(link):
                    flag=0
                    err=err_dict()
                    try:
                        article = Article(link)
                        article.download()
                        article.parse()
                        article.nlp()
                    except:
                        err["link"]="Link not working: "+link
                        Errors["Korea"].append(err)
                        return
                    
                    try:
                        published=date_correction_for_newspaper3k(article.publish_date)
                        pub_date.append(published)
                    except:
                        err["link"]=link
                        err['published_date']="Error"
                        pub_date.append("-")
                        flag=1
                    
                    try:
                        title.append(article.title)
                    except:
                        err["link"]=link
                        err["title"]="Error"
                        title.append("-")
                        flag=1
                    
                    try:
                        text.append(article.text)
                    except:
                        err["link"]=link
                        err["title"]="Error"
                        text.append("-")
                        flag=1

                    scraped_date.append(str(today))
                    
                    if flag==1:
                        Errors["Korea"].append(err)

                    final_links.append(link)
            
            thread_list=[]
            length=len(links)
            for i in range(length):
                thread_list.append(threading.Thread(target=getartciles, args=(links[i], )))
            
            for thread in thread_list:
                thread.start()
            
            for thread in thread_list:
                thread.join()
            
            df = pd.DataFrame({"text": text, "link": final_links,
                              "publish_date": pub_date, "scraped_date": scraped_date, "title": title})
            
            df = df.drop_duplicates(subset=["link"])
            df = FilterFunction(df)
            emptydataframe("Korea", df)
            
            return df
        except:
            print("Korea not working")
            not_working_functions.append('Korea')
            

            
            
    #                          Country - Australia
    
    
    
       
            
    def proactive(keyword):
        try:
            print("proactive")
            Errors["Proactive"]=[]
            
            
            
            url = f"https://www.proactiveinvestors.com.au/search/advancedSearch/news?url=&keyword={keyword}"
            domain_url = "https://www.proactiveinvestors.com.au/"
            
            

            headers = {
                "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10.15; rv:78.0) Gecko/20100101 Firefox/78.0",
                "accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.9",
                'sec-fetch-site': 'none',
                'sec-fetch-mode': 'navigate',
                'sec-fetch-user': '?1',
                'sec-fetch-dest': 'document',
                'accept-language': 'en-GB,en-US;q=0.9,en;q=0.8',
            }
            
            try:
                page = requests.get(url, headers=headers)
                soup = BeautifulSoup(page.content, "html.parser")
            except:
                print("Proactive not working")
                not_working_functions.append('Proactive')
                err = "Main link did not load: " + url
                Errors["Proactive"].append(err)
                return
            
            # soup  # Debugging - if soup is working correctly
            # Class names of the elements to be scraped
            div_class = "advanced-search-block"  # Class name of div containing the a tag
            #h1_class = "_1Y-96"
            #h1_div_class = "col-xs-12"
            
            title_h1_class = "h2"
            date_p_itemprop = "datePublished"
            para_div_itemprop = "articleBody"
            links = []
            
            try:
                for divtag in soup.find_all("div", {"class": div_class}):
                    for a in divtag.find_all("a", href=True):
                        link = a["href"]  # Gets the link
                        # Checking the link if it is a relative link
                        if link[0] == '/':
                            link = domain_url + link[1:]
                        # Filtering advertaisment links
                        link_start = domain_url
                        if link.startswith(link_start):
                            links.append(link)
            except:
                if len(links)==0:
                    print("Proactive not working")
                    not_working_functions.append('Proactive')
                    Errors["Proactive"].append("Extraction of link not working.")
                    return
                        
            # Remove duplicates
            links = list(set(links))
            
            # links # Debugging - if link array is generated
            collection = []
            scrapper_name = "proactiveinvestors"
            
            def getarticles(link):
                flag=0
                err=err_dict()
                try:
                    l_page = requests.get(link, headers=headers)
                    l_soup = BeautifulSoup(l_page.content, 'html.parser')
                except:
                    err["link"]="Link not working: "+link
                    Errors["Proactive"].append(err)
                    return
                
                data = []
                
                # Scraping the heading
                #h1_ele = l_soup.find("h1", {"class": h1_class})
                
                try:
                    title_ele = l_soup.find("h1", {"class": title_h1_class})
                    data.append(title_ele.text)
                except:
                    err["link"]=link
                    err['title']="Error"
                    data.append("-")
                    flag=1
                 # drops the complete data if there is an error
                # Adding the link to data
                data.append(link)
                # Scraping the published date
                try:
                    date_ele = l_soup.find("p", {"itemprop": date_p_itemprop})
                    date_text = date_ele.text
                    #date_text = (date_text.split('/'))[-1]
                    #date_text = date_text.replace(" Updated: ", "")
                    # The date_text could be further modified to represent a proper date format
                    data.append(date_text)
                except:
                    err["link"]=link
                    err['published_date']="Error"
                    data.append("-")
                    flag=1
              # drops the complete data if there is an error
                # Adding the scraped date to data
                cur_date = str(datetime.today())
                data.append(cur_date)
                # Scraping the paragraph
                try:
                    para_ele = (l_soup.findAll(
                        "div", {"itemprop": para_div_itemprop}))[-1]
                    data.append(para_ele.text)  # Need to make this better
                except:
                    err["link"]=link
                    err['text']="Error"
                    data.append("-")
                    flag=1
                  # drops the complete data if there is an error
                # Adding data to a collection
                
                if flag==1:
                    Errors["Proactive"].append(err)
                
                collection.append(data)
                
            thread_list=[]
            length=len(links)
            for i in range(length):
                thread_list.append(threading.Thread(target=getarticles, args=(links[i], )))
            
            for thread in thread_list:
                thread.start()
            
            for thread in thread_list:
                thread.join()
            
            df = pd.DataFrame(collection, columns=[
                              'title', 'link', 'publish_date', 'scraped_date', 'text'])
            
            
            # print(df) # For debugging. To check if df is created
            # print(err_logs) # For debugging - to check if any errors occoured
            df = FilterFunction(df)
            emptydataframe("Proactive investors", df)
            # df  = link_correction(df)
            return df
        
        except:
            not_working_functions.append("Proactive Inverstors")
            print("Proactive investors not working")
            
    
    
    def gulfbusiness():
        try:
            print("gulfbusiness")
            Errors["gulfbusiness"]=[]
            
            
            
            url = "https://gulfbusiness.com/?s=ipo"
            domain_url = "https://gulfbusiness.com/"
            

            headers = {
                "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10.15; rv:78.0) Gecko/20100101 Firefox/78.0",
                "accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.9",
                'sec-fetch-site': 'none',
                'sec-fetch-mode': 'navigate',
                'sec-fetch-user': '?1',
                'sec-fetch-dest': 'document',
                'accept-language': 'en-GB,en-US;q=0.9,en;q=0.8',
            }
            div_class="post-title"# Class name of div containing the a tag
            #h1_class = "_1Y-96"
            #h1_div_class = "col-xs-12"
            title_h1_class= "entry-title"
            date_div_class= ["thb-post-date"]
            para_div_class=["post-content entry-content"]
            links=[]
            try:
                page = requests.get(url, headers=headers)
                soup = BeautifulSoup(page.content, "html.parser")
            except:
                print("gulfbusiness not working")
                not_working_functions.append('gulfbusiness')
                err = "Main link did not load: " + url
                Errors["gulfbusiness"].append(err)
                return
            
            
            try:
                
                for h2_tag in soup.find_all("div", {"class": div_class}):
                    for a in h2_tag.find_all("a", href=True):
                        link = a["href"]  # Gets the link
                        # Checking the link if it is a relative link
                        if link[0] == '/':
                            link = domain_url + link[1:]
                        # Filtering advertaisment links
                        link_start = domain_url
                        if link.startswith(link_start):
                            links.append(link)
            except:
                if len(links)==0:
                    print("gulfbusiness not working")
                    not_working_functions.append('gulfbusiness')
                    Errors["gulfbusiness"].append("Extraction of link not working.")
                    return
                        
            # Remove duplicates
            links = list(set(links))
            
            # links # Debugging - if link array is generated
            collection = []
            scrapper_name = "gulfbusiness"
            
            def getarticles(link):
                flag=0
                err=err_dict()
                try:
                    l_page = requests.get(link, headers=headers)
                    l_soup = BeautifulSoup(l_page.content, 'html.parser')
                except:
                    err["link"]="Link not working: "+link
                    Errors["gulfbusiness"].append(err)
                    return
                
                data = []
                
                # Scraping the heading
                #h1_ele = l_soup.find("h1", {"class": h1_class})
                
                try:
                    title_ele = l_soup.find("h1", {"class": title_h1_class})
                    data.append(title_ele.text)
                except:
                    err["link"]=link
                    err['title']="Error"
                    data.append("-")
                    flag=1
                 # drops the complete data if there is an error
                # Adding the link to data
                data.append(link)
                # Scraping the published date
                try:
                    date_ele = l_soup.find("div",{"class":date_div_class})
                    date_text = date_ele.text

                    #date_text = (date_text.split('/'))[-1]
                    #date_text = date_text.replace(" Updated: ", "")
                    # The date_text could be further modified to represent a proper date format
                    data.append(date_text)
                except:
                    err["link"]=link
                    err['published_date']="Error"
                    data.append("-")
                    flag=1
              # drops the complete data if there is an error
                # Adding the scraped date to data
                today = date.today()
                cur_date = str(today)
                data.append(cur_date)
                # Scraping the paragraph
                try:
                    para_ele = (l_soup.findAll(
                        "div", {"class": para_div_class}))[-1]
                    data.append(para_ele.text)  # Need to make this better
                except:
                    err["link"]=link
                    err['text']="Error"
                    data.append("-")
                    flag=1
                  # drops the complete data if there is an error
                # Adding data to a collection
                
                if flag==1:
                    Errors["gulfbusiness"].append(err)
                
                collection.append(data)
                
            thread_list=[]
            length=len(links)
            for i in range(length):
                thread_list.append(threading.Thread(target=getarticles, args=(links[i], )))
            
            for thread in thread_list:
                thread.start()
            
            for thread in thread_list:
                thread.join()
            
            df = pd.DataFrame(collection, columns=[
                              'title', 'link', 'publish_date', 'scraped_date', 'text'])
            
            
            # print(df) # For debugging. To check if df is created
            # print(err_logs) # For debugging - to check if any errors occoured
            df = FilterFunction(df)
            emptydataframe("gulfbusiness", df)
            # df  = link_correction(df)
            return df
        
        except:
            not_working_functions.append("gulfbusiness")
            print("gulfbusiness not working")
    
    def investmentu():
        try:
            print("investmentu")
            Errors["investmentu"]=[]
            
            
            
            url = "https://investmentu.com/?s=ipo"
            domain_url = "https://investmentu.com/"
            

            headers = {
                "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10.15; rv:78.0) Gecko/20100101 Firefox/78.0",
                "accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.9",
                'sec-fetch-site': 'none',
                'sec-fetch-mode': 'navigate',
                'sec-fetch-user': '?1',
                'sec-fetch-dest': 'document',
                'accept-language': 'en-GB,en-US;q=0.9,en;q=0.8',
            }
            div_class = "articlePreview container"
            #h1_class = "_1Y-96"
            #h1_div_class = "col-xs-12"
            title_h1_class = "page-title"
            date_time_class = ["updated"]
            para_div_role = ["main"]
            links=[]
            try:
                page = requests.get(url, headers=headers)
                soup = BeautifulSoup(page.content, "html.parser")
            except:
                print("investmentu not working")
                not_working_functions.append('investmentu')
                err = "Main link did not load: " + url
                Errors["investmentu"].append(err)
                return
            
            
            try:
                
                for h2_tag in soup.find_all("div", {"class": div_class}):
                    for a in h2_tag.find_all("a", href=True):
                        link = a["href"]  # Gets the link
                        # Checking the link if it is a relative link
                        if link[0] == '/':
                            link = domain_url + link[1:]
                        # Filtering advertaisment links
                        link_start = domain_url
                        if link.startswith(link_start):
                            links.append(link)
            except:
                if len(links)==0:
                    print("investmentu not working")
                    not_working_functions.append('investmentu')
                    Errors["investmentu"].append("Extraction of link not working.")
                    return
                        
            # Remove duplicates
            links = list(set(links))
            
            # links # Debugging - if link array is generated
            collection = []
            scrapper_name = "investmentu"
            
            def getarticles(link):
                flag=0
                err=err_dict()
                try:
                    l_page = requests.get(link, headers=headers)
                    l_soup = BeautifulSoup(l_page.content, 'html.parser')
                except:
                    err["link"]="Link not working: "+link
                    Errors["investmentu"].append(err)
                    return
                
                data = []
                
                # Scraping the heading
                #h1_ele = l_soup.find("h1", {"class": h1_class})
                
                try:
                    title_ele = l_soup.find("h1", {"class": title_h1_class})
                    data.append(title_ele.text)
                except:
                    err["link"]=link
                    err['title']="Error"
                    data.append("-")
                    flag=1
                 # drops the complete data if there is an error
                # Adding the link to data
                data.append(link)
                # Scraping the published date
                try:
                    date_ele = l_soup.find("time",{"class":date_time_class})
                    date_text = date_ele.text[0:12]

                    #date_text = (date_text.split('/'))[-1]
                    #date_text = date_text.replace(" Updated: ", "")
                    # The date_text could be further modified to represent a proper date format
                    data.append(date_text)
                except:
                    err["link"]=link
                    err['published_date']="Error"
                    data.append("-")
                    flag=1
              # drops the complete data if there is an error
                # Adding the scraped date to data
                today = date.today()
                cur_date = str(today)
                data.append(cur_date)
                # Scraping the paragraph
                try:
                    para_ele = (l_soup.findAll(
                        "div", {"role": para_div_role}))[-1]
                    data.append(para_ele.text)  # Need to make this better
                except:
                    err["link"]=link
                    err['text']="Error"
                    data.append("-")
                    flag=1
                  # drops the complete data if there is an error
                # Adding data to a collection
                
                if flag==1:
                    Errors["investmentu"].append(err)
                
                collection.append(data)
                
            thread_list=[]
            length=len(links)
            for i in range(length):
                thread_list.append(threading.Thread(target=getarticles, args=(links[i], )))
            
            for thread in thread_list:
                thread.start()
            
            for thread in thread_list:
                thread.join()
            
            df = pd.DataFrame(collection, columns=[
                              'title', 'link', 'publish_date', 'scraped_date', 'text'])
            
            
            # print(df) # For debugging. To check if df is created
            # print(err_logs) # For debugging - to check if any errors occoured
            df = FilterFunction(df)
            emptydataframe("investmentu investors", df)
            # df  = link_correction(df)
            return df
        
        except:
            not_working_functions.append("investmentu")
            print("investmentu not working")
    
    def einnews():
        try:
            print("IPO EinNews")
            Errors["Einnews"]=[]

            baseSearchUrl = "https://ipo.einnews.com/"
            domainUrl = "https://ipo.einnews.com"
            keywords = ['IPO', 'pre-IPO', 'initial public offering']

            # use this for faster testing
            scrapedData = {}
            links = []
            titles = []
            err_index = []
            ArticleDates = []
            ScrapeDates = []
            ArticleBody = []
            
            queryUrl = baseSearchUrl
            try:
                session = HTMLSession()
                resp = session.post(queryUrl)
                resp.html.render()
                pageSource = resp.html.html
                parsedSource = BeautifulSoup(pageSource, "html.parser")
            except:
                print("Einnews not working")
                not_working_functions.append('Einnews')
                err = "Main link did not load: " + queryUrl
                Errors["Einnews"].append(err)
                return           
            
            
            try:
            
                for item in parsedSource.find("ul", class_="pr-feed").find_all("li"):
                    requiredTag = item.find("h3")
                    
                    flag=0
                    err=err_dict()
                    
                    try:
                        currentArticleLink = requiredTag.find("a")["href"]
                        # print(currentArticleLink)
                        if currentArticleLink[0] == "/":
                            links.append(domainUrl + currentArticleLink)
                        else:
                            links.append(currentArticleLink)
                    except:
                        err["link"]="Link extractor not working"
                        Errors["Einnews"].append(err)
                        continue
                    
                    try:
                        currentArticleTitle = str(
                            requiredTag.find("a").text).strip()
                        
                        titles.append(currentArticleTitle)
                    except:
                        err["link"]=currentArticleLink
                        err['title']="Error"
                        titles.append("-")
                        flag=1
                    
                    
                    try:    
                        currentArticleDateText = item.find(
                            "span", class_="date").text
                        if re.search("^\d.*", currentArticleDateText):
                                currentArticleDate = datetime.today().strftime("%d-%m-%Y")
                                ArticleDates.append(currentArticleDate)
                                ScrapeDates.append(
                                datetime.today().strftime("%d-%m-%Y"))
                        else:
                            currentArticleDate = datetime.strptime(currentArticleDateText,
                                                                        "%b %d, %Y").strftime("%d-%m-%Y")
                            ArticleDates.append(currentArticleDate)
                            ScrapeDates.append(
                                datetime.today().strftime("%d-%m-%Y"))
                    except:
                        err["link"]=currentArticleLink
                        err['published_date']="Error"
                        ScrapeDates.append("-")
                        flag=1
                    
                    try:
                        articleText = ""
                        for pitem in item.find_all("p"):
                            articleText += pitem.text
                        ArticleBody.append(articleText.strip("\n"))
                    except:
                        err["link"]=currentArticleLink
                        err['text']="Error"
                        ArticleBody.append("-")
                        flag=1
                    
                    if flag==1:
                        Errors["Einnews"].append(err)
            except:
                print("Einnews not working")
                not_working_functions.append('Einnews')
                Errors["Einnews"].append("Extraction of link not working.")
                return

            scrapedData["title"] = titles
            scrapedData["link"] = links
            scrapedData["publish_date"] = ArticleDates
            scrapedData["scraped_date"] = ScrapeDates
            scrapedData["text"] = ArticleBody
                # print(titles)
                # print(links)
                # print(ArticleDates)
                # print(ArticleBody)

            # DataFrame creation
            einnewsDF = pd.DataFrame(scrapedData)
            df = FilterFunction(einnewsDF)
            emptydataframe("Einnews", df)
            return df
        except:
            not_working_functions.append("IPO Einnews")
            print("EINnews not working") 

    def businessinsider():
        try:
            print("businessinsider")
            Errors["businessinsider"]=[]
            
            
            
            url = "https://www.businessinsider.in/searchresult.cms?query=ipo&sortorder=score"
            domain_url = "https://www.businessinsider.in/"
            

            headers = {
                "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10.15; rv:78.0) Gecko/20100101 Firefox/78.0",
                "accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.9",
                'sec-fetch-site': 'none',
                'sec-fetch-mode': 'navigate',
                'sec-fetch-user': '?1',
                'sec-fetch-dest': 'document',
                'accept-language': 'en-GB,en-US;q=0.9,en;q=0.8',
            }
            div_class = "list-bottom-text-wrapper"
            #h1_class = "_1Y-96"
            #h1_div_class = "col-xs-12"
            title_div_class = "mobile_padding"
            date_span_class = ["Date"]
            para_div_class = ["Normal"]
            links=[]
            try:
                page = requests.get(url, headers=headers)
                soup = BeautifulSoup(page.content, "html.parser")
            except:
                print("businessinsider not working")
                not_working_functions.append('businessinsider')
                err = "Main link did not load: " + url
                Errors["businessinsider"].append(err)
                return
            
            
            try:
                
                for h2_tag in soup.find_all("div", {"class": div_class}):
                    for a in h2_tag.find_all("a", href=True):
                        link = a["href"]  # Gets the link
                        # Checking the link if it is a relative link
                        if link[0] == '/':
                            link = domain_url + link[1:]
                        # Filtering advertaisment links
                        link_start = domain_url
                        if link.startswith(link_start):
                            links.append(link)
            except:
                if len(links)==0:
                    print("businessinsider not working")
                    not_working_functions.append('businessinsider')
                    Errors["businessinsider"].append("Extraction of link not working.")
                    return
                        
            # Remove duplicates
            links = list(set(links))
            
            # links # Debugging - if link array is generated
            collection = []
            scrapper_name = "businessinsider"
            
            def getarticles(link):
                flag=0
                err=err_dict()
                try:
                    l_page = requests.get(link, headers=headers)
                    l_soup = BeautifulSoup(l_page.content, 'html.parser')
                except:
                    err["link"]="Link not working: "+link
                    Errors["businessinsider"].append(err)
                    return
                
                data = []
                
                # Scraping the heading
                #h1_ele = l_soup.find("h1", {"class": h1_class})
                
                try:
                    title_ele = l_soup.find("div", {"class": title_div_class})
                    data.append(title_ele.text)
                except:
                    err["link"]=link
                    err['title']="Error"
                    data.append("-")
                    flag=1
                 # drops the complete data if there is an error
                # Adding the link to data
                data.append(link)
                # Scraping the published date
                try:
                    date_ele = l_soup.find("span",{"class":date_span_class})
                    date_text = date_ele.text[0:14]

                    #date_text = (date_text.split('/'))[-1]
                    #date_text = date_text.replace(" Updated: ", "")
                    # The date_text could be further modified to represent a proper date format
                    data.append(date_text)
                except:
                    err["link"]=link
                    err['published_date']="Error"
                    data.append("-")
                    flag=1
              # drops the complete data if there is an error
                # Adding the scraped date to data
                today = date.today()
                cur_date = str(today)
                data.append(cur_date)
                # Scraping the paragraph
                try:
                    para_ele = (l_soup.findAll(
                        "div", {"class": para_div_class}))[-1]
                    data.append(para_ele.text)  # Need to make this better
                except:
                    err["link"]=link
                    err['text']="Error"
                    data.append("-")
                    flag=1
                  # drops the complete data if there is an error
                # Adding data to a collection
                
                if flag==1:
                    Errors["businessinsider"].append(err)
                
                collection.append(data)
                
            thread_list=[]
            length=len(links)
            for i in range(length):
                thread_list.append(threading.Thread(target=getarticles, args=(links[i], )))
            
            for thread in thread_list:
                thread.start()
            
            for thread in thread_list:
                thread.join()
            
            df = pd.DataFrame(collection, columns=[
                              'title', 'link', 'publish_date', 'scraped_date', 'text'])
            
            
            # print(df) # For debugging. To check if df is created
            # print(err_logs) # For debugging - to check if any errors occoured
            df = FilterFunction(df)
            emptydataframe("businessinsider investors", df)
            # df  = link_correction(df)
            return df
        
        except:
            not_working_functions.append("businessinsider")
            print("businessinsider not working")
            
        
    
    def Reuters(keyword):
        print('Reuters')
        Errors["Reuters"]=[]
        headers = {
                "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10.15; rv:78.0) Gecko/20100101 Firefox/78.0",
                "accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.9",
                'sec-fetch-site': 'none',
                'sec-fetch-mode': 'navigate',
                'sec-fetch-user': '?1',
                'sec-fetch-dest': 'document',
                'accept-language': 'en-GB,en-US;q=0.9,en;q=0.8',
            }
        try:
            
            title = []
            text = []
            s_dates = []
            links = []
            pub_date = []
            try:
                url = f'https://www.reuters.com/search/news?blob={keyword}&sortBy=date&dateRange=all'
                url1 = 'https://www.reuters.com'
                try:
                    page = requests.get(url, headers=headers)
                    soup = BeautifulSoup(page.content, 'html.parser')
                except:
                    print("Reuters not working")
                    not_working_functions.append('Reuters')
                    err = "Main link did not load: " + url
                    Errors["Reuters"].append(err)
                    return
                try:    
                    y = soup.findAll("h5", {"class": "search-result-timestamp"})
                    for x in y:
                        import re
                        TAG_RE = re.compile(r'<[^>]+>')
                        pubdate = TAG_RE.sub('', str(x))
                        pub_date.append(str(pubdate))
                    for i in range(1, len(soup.find_all('h3'))):
                        pdd = soup.find_all('h3')[i]
                        for a in pdd.find_all('a', href=True):
                            links.append(url1 + a["href"])
                except:
                    if len(links)==0:
                        print("Reuters not working")
                        not_working_functions.append('Reuters')
                        Errors["Reuters"].append("Extraction of link not working.")
                        return
                
                
                
                
                def getarticles(l):
                    flag=0
                    err=err_dict()
                    try:
                        fetch = requests.get(l, headers=headers)
                        sp = BeautifulSoup(fetch.content, 'lxml')
                    except:
                        err["link"]="Link not working: "+l
                        Errors["Reuters"].append(err)
                        return
                    
                    
                    try:
                        x = sp.find("h1", {
                                    "class": "text__text__1FZLe text__dark-grey__3Ml43 text__medium__1kbOh text__heading_3__1kDhc heading__base__2T28j heading__heading_3__3aL54 article-header__title__3Y2hh"})
                        n = x.text
                    except:
                        err["link"]=l
                        err['title']="Error"
                        n="-"
                        flag=1
                        
                    try:    
                        z = sp.find(
                            "div", {"class": "article-body__content__17Yit paywall-article"})
                        k = z.text
                    except:
                        err["link"]=l
                        err['text']="Error"
                        k="-"
                        flag=1
                    
                    
                    if flag==1:
                        Errors["Reuters"].append(err)
                    # print(z)
                    text.append(k)
                    title.append(n)
                    s_dates.append(cur_date)
                    
                thread_list=[]
                length=len(links)
                for i in range(length):
                    thread_list.append(threading.Thread(target=getarticles, args=(links[i], )))
                
                for thread in thread_list:
                    thread.start()
                
                for thread in thread_list:
                    thread.join()
                
                
            except:
                print('Reuters is not working')
                not_working_functions.append('Reuters')
            
              
                
            
            percentile_list = {'publish_date': pub_date, 'scraped_date': s_dates,
                               'title': title, 'link': links, 'text': text}
            
            reuters = pd.DataFrame.from_dict(percentile_list, orient='index')
            df = reuters.transpose()
            df.dropna(inplace=True)
            # df = FilterFunction(reuters)
            emptydataframe("reuters", df)
            logging.info("Reuters function ended")
            # df  = link_correction(df)
            return df
        except:
            df1 = pd.DataFrame(
                columns=['title', 'link', 'publish_date', 'scraped_date'])
            return df1
    
    
    def google_news():
        try:
            print("Google")
            Errors["Google"]=[]
            try:
                googlenews = GoogleNews(period='24h')
                googlenews.search('ipo listing OR nod for IPO OR approval for IPO OR planning for IPO OR aims IPO OR eyes Ipo')
            except:
                print("Google not working")
                not_working_functions.append('Google')
                err = "Error in Module "
                Errors["Google"].append(err)
                return
            
            links=[]
            
            try:
                for i in range(3):
                    for j in googlenews.page_at(i+1):
                        links.append(j["link"])
            except:
                if len(links)==0:
                            print("Google not working")
                            not_working_functions.append('Google')
                            Errors["Google"].append("Extraction of link not working.")
                            return
            
            final_links = []
            title, text, pub_date, scraped_date = [], [], [], []
            today = date.today()
            
            def getartciles(link):
                    flag=0
                    err=err_dict()
                    try:
                        article = Article(link)
                        article.download()
                        article.parse()
                        article.nlp()
                    except:
                        err["link"]="Link not working: "+link
                        Errors["Google"].append(err)
                        return
                    
                    try:
                        published=date_correction_for_newspaper3k(article.publish_date)
                        pub_date.append(published)
                    except:
                        err["link"]=link
                        err['published_date']="Error"
                        pub_date.append("-")
                        flag=1
                    
                    try:
                        title.append(article.title)
                    except:
                        err["link"]=link
                        err["title"]="Error"
                        title.append("-")
                        flag=1
                    
                    try:
                        text.append(article.text)
                    except:
                        err["link"]=link
                        err["title"]="Error"
                        text.append("-")
                        flag=1

                    scraped_date.append(str(today))
                    
                    if flag==1:
                        Errors["Google"].append(err)

                    final_links.append(link)
            
            thread_list=[]
            length=len(links)
            for i in range(length):
                thread_list.append(threading.Thread(target=getartciles, args=(links[i], )))
            
            for thread in thread_list:
                thread.start()
            
            for thread in thread_list:
                thread.join()
            
            df = pd.DataFrame({"text": text, "link": final_links,
                                "publish_date": pub_date, "scraped_date": scraped_date, "title": title})
            
            df = df.drop_duplicates(subset=["link"])
            df = FilterFunction(df)
            emptydataframe("Google", df)
            
            return df
        
        except:
            print("Google not working")
            not_working_functions.append('Google')

    def defenseworld():
        try:
            print("defenseworld")
            Errors["defenseworld"]=[]
            
            
            
            url = "https://www.defenseworld.net/?s=ipo"
            domain_url = "https://www.defenseworld.net/"
            

            headers = {
                "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10.15; rv:78.0) Gecko/20100101 Firefox/78.0",
                "accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.9",
                'sec-fetch-site': 'none',
                'sec-fetch-mode': 'navigate',
                'sec-fetch-user': '?1',
                'sec-fetch-dest': 'document',
                'accept-language': 'en-GB,en-US;q=0.9,en;q=0.8',
            }
            #h1_class = "_1Y-96"
            #h1_div_class = "col-xs-12"
            section_class = "archive"  # Class name of div containing the a tag
            #h1_class = "_1Y-96"
            #h1_div_class = "col-xs-12"
            title_h1_itemprop = "headline"
            date_span_itemprop = "datePublished dateModified"
            para_div_class = ["entry"]
            links=[]
            try:
                page = requests.get(url, headers=headers)
                soup = BeautifulSoup(page.content, "html.parser")
            except:
                print("defenseworld not working")
                not_working_functions.append('defenseworld')
                err = "Main link did not load: " + url
                Errors["defenseworld"].append(err)
                return
            
            
            try:
                
                for h2_tag in soup.find_all("section", {"class": section_class}):
                    for a in h2_tag.find_all("a", href=True):
                        link = a["href"]  # Gets the link
                        # Checking the link if it is a relative link
                        if link[0] == '/':
                            link = domain_url + link[1:]
                        # Filtering advertaisment links
                        link_start = domain_url
                        if link.startswith(link_start):
                            links.append(link)
            except:
                if len(links)==0:
                    print("defenseworld not working")
                    not_working_functions.append('defenseworld')
                    Errors["defenseworld"].append("Extraction of link not working.")
                    return
                        
            # Remove duplicates
            links = list(set(links))
            
            # links # Debugging - if link array is generated
            collection = []
            scrapper_name = "defenseworld"
            
            def getarticles(link):
                flag=0
                err=err_dict()
                try:
                    l_page = requests.get(link, headers=headers)
                    l_soup = BeautifulSoup(l_page.content, 'html.parser')
                except:
                    err["link"]="Link not working: "+link
                    Errors["defenseworld"].append(err)
                    return
                
                data = []
                
                # Scraping the heading
                #h1_ele = l_soup.find("h1", {"class": h1_class})
                
                try:
                    title_ele = l_soup.find("h1", {"itemprop": title_h1_itemprop})
                    data.append(title_ele.text)
                except:
                    err["link"]=link
                    err['title']="Error"
                    data.append("-")
                    flag=1
                 # drops the complete data if there is an error
                # Adding the link to data
                data.append(link)
                # Scraping the published date
                try:
                    date_ele = l_soup.find("span",{"itemporp":date_span_itemprop})
                    date_text = link[29:39]

                    #date_text = (date_text.split('/'))[-1]
                    #date_text = date_text.replace(" Updated: ", "")
                    # The date_text could be further modified to represent a proper date format
                    data.append(date_text)
                except:
                    err["link"]=link
                    err['published_date']="Error"
                    data.append("-")
                    flag=1
              # drops the complete data if there is an error
                # Adding the scraped date to data
                today = date.today()
                cur_date = str(today)
                data.append(cur_date)
                # Scraping the paragraph
                try:
                    para_ele = (l_soup.findAll(
                        "div", {"class": para_div_class}))[-1]
                    data.append(para_ele.text)  # Need to make this better
                except:
                    err["link"]=link
                    err['text']="Error"
                    data.append("-")
                    flag=1
                  # drops the complete data if there is an error
                # Adding data to a collection
                
                if flag==1:
                    Errors["defenseworld"].append(err)
                
                collection.append(data)
                
            thread_list=[]
            length=len(links)
            for i in range(length):
                thread_list.append(threading.Thread(target=getarticles, args=(links[i], )))
            
            for thread in thread_list:
                thread.start()
            
            for thread in thread_list:
                thread.join()
            
            df = pd.DataFrame(collection, columns=[
                              'title', 'link', 'publish_date', 'scraped_date', 'text'])
            
            
            # print(df) # For debugging. To check if df is created
            # print(err_logs) # For debugging - to check if any errors occoured
            df = FilterFunction(df)
            emptydataframe("defenseworld", df)
            # df  = link_correction(df)
            return df
        
        except:
            not_working_functions.append("defenseworld")
            print("defenseworld not working")

    def technode():
        try:
            print("technode")
            Errors["technode"]=[]
            
            
            
            url = "https://technode.com/?s=ipo"
            domain_url = "https://technode.com/"
            

            headers = {
                "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10.15; rv:78.0) Gecko/20100101 Firefox/78.0",
                "accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.9",
                'sec-fetch-site': 'none',
                'sec-fetch-mode': 'navigate',
                'sec-fetch-user': '?1',
                'sec-fetch-dest': 'document',
                'accept-language': 'en-GB,en-US;q=0.9,en;q=0.8',
            }
            #h1_class = "_1Y-96"
            #h1_div_class = "col-xs-12"
            section_class = "archive"  # Class name of div containing the a tag
            #h1_class = "_1Y-96"
            #h1_div_class = "col-xs-12"
            main_class="site-main"
            date_time_class= ["entry-date published"]
            para_div_class=["entry-content"]
            links=[]
            try:
                page = requests.get(url, headers=headers)
                soup = BeautifulSoup(page.content, "html.parser")
            except:
                print("technode not working")
                not_working_functions.append('technode')
                err = "Main link did not load: " + url
                Errors["technode"].append(err)
                return
            
            
            try:
                
                for h2_tag in soup.find_all("main", {"class": main_class}):
                    for a in h2_tag.find_all("a", href=True):
                        link = a["href"]  # Gets the link
                        # Checking the link if it is a relative link
                        if link[0] == '/':
                            link = domain_url + link[1:]
                        # Filtering advertaisment links
                        link_start = domain_url
                        if link.startswith(link_start):
                            links.append(link)
            except:
                if len(links)==0:
                    print("technode not working")
                    not_working_functions.append('technode')
                    Errors["technode"].append("Extraction of link not working.")
                    return
                        
            # Remove duplicates
            links = list(set(links))
            
            # links # Debugging - if link array is generated
            collection = []
            scrapper_name = "technode"
            
            def getarticles(link):
                flag=0
                err=err_dict()
                try:
                    l_page = requests.get(link, headers=headers)
                    l_soup = BeautifulSoup(l_page.content, 'html.parser')
                except:
                    err["link"]="Link not working: "+link
                    Errors["technode"].append(err)
                    return
                
                data = []
                
                # Scraping the heading
                #h1_ele = l_soup.find("h1", {"class": h1_class})
                
                try:
                    title_ele = l_soup.find("h1")
                    data.append(title_ele.text)
                except:
                    err["link"]=link
                    err['title']="Error"
                    data.append("-")
                    flag=1
                 # drops the complete data if there is an error
                # Adding the link to data
                data.append(link)
                # Scraping the published date
                try:
                    date_ele = l_soup.find()
                    date_text = link[21:31]

                    #date_text = (date_text.split('/'))[-1]
                    #date_text = date_text.replace(" Updated: ", "")
                    # The date_text could be further modified to represent a proper date format
                    data.append(date_text)
                except:
                    err["link"]=link
                    err['published_date']="Error"
                    data.append("-")
                    flag=1
              # drops the complete data if there is an error
                # Adding the scraped date to data
                today = date.today()
                cur_date = str(today)
                data.append(cur_date)
                # Scraping the paragraph
                try:
                    para_ele = (l_soup.findAll(
                        "div", {"class": para_div_class}))[-1]
                    data.append(para_ele.text)  # Need to make this better
                except:
                    err["link"]=link
                    err['text']="Error"
                    data.append("-")
                    flag=1
                  # drops the complete data if there is an error
                # Adding data to a collection
                
                if flag==1:
                    Errors["technode"].append(err)
                
                collection.append(data)
                
            thread_list=[]
            length=len(links)
            for i in range(length):
                thread_list.append(threading.Thread(target=getarticles, args=(links[i], )))
            
            for thread in thread_list:
                thread.start()
            
            for thread in thread_list:
                thread.join()
            
            df = pd.DataFrame(collection, columns=[
                              'title', 'link', 'publish_date', 'scraped_date', 'text'])
            
            
            # print(df) # For debugging. To check if df is created
            # print(err_logs) # For debugging - to check if any errors occoured
            df = FilterFunction(df)
            emptydataframe("technode", df)
            # df  = link_correction(df)
            return df
        
        except:
            not_working_functions.append("technode")
            print("technode not working")

    def globenewswire():
        try:
            print("globenewswire")
            Errors["globenewswire"]=[]
            
            
            
            url = "https://www.globenewswire.com/search/keyword/ipo"
            domain_url = "https://www.globenewswire.com/"
            

            headers = {
                "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10.15; rv:78.0) Gecko/20100101 Firefox/78.0",
                "accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.9",
                'sec-fetch-site': 'none',
                'sec-fetch-mode': 'navigate',
                'sec-fetch-user': '?1',
                'sec-fetch-dest': 'document',
                'accept-language': 'en-GB,en-US;q=0.9,en;q=0.8',
            }
            #h1_class = "_1Y-96"
            #h1_div_class = "col-xs-12"
            div_class="pagging-list-item-text-container"# Class name of div containing the a tag
            #h1_class = "_1Y-96"
            #h1_div_class = "col-xs-12"
            title_h1_class= "article-headline"
            para_div_class=["main-body-container article-body"]
            links=[]
            try:
                page = requests.get(url, headers=headers)
                soup = BeautifulSoup(page.content, "html.parser")
            except:
                print("globenewswire not working")
                not_working_functions.append('globenewswire')
                err = "Main link did not load: " + url
                Errors["globenewswire"].append(err)
                return
            
            
            try:
                
                for h2_tag in soup.find_all("div", {"class": div_class}):
                    for a in h2_tag.find_all("a", href=True):
                        link = a["href"]  # Gets the link
                        # Checking the link if it is a relative link
                        if link[0] == '/':
                            link = domain_url + link[1:]
                        # Filtering advertaisment links
                        link_start = domain_url
                        if link.startswith(link_start):
                            links.append(link)
            except:
                if len(links)==0:
                    print("globenewswire not working")
                    not_working_functions.append('globenewswire')
                    Errors["globenewswire"].append("Extraction of link not working.")
                    return
                        
            # Remove duplicates
            links = list(set(links))
            
            # links # Debugging - if link array is generated
            collection = []
            scrapper_name = "globenewswire"
            
            def getarticles(link):
                flag=0
                err=err_dict()
                try:
                    l_page = requests.get(link, headers=headers)
                    l_soup = BeautifulSoup(l_page.content, 'html.parser')
                except:
                    err["link"]="Link not working: "+link
                    Errors["globenewswire"].append(err)
                    return
                
                data = []
                
                # Scraping the heading
                #h1_ele = l_soup.find("h1", {"class": h1_class})
                
                try:
                    title_ele = l_soup.find("h1",{"class": title_h1_class})
                    data.append(title_ele.text)
                except:
                    err["link"]=link
                    err['title']="Error"
                    data.append("-")
                    flag=1
                 # drops the complete data if there is an error
                # Adding the link to data
                data.append(link)
                # Scraping the published date
                try:
                    date_ele = l_soup.find()
                    date_text = link[43:53]

                    #date_text = (date_text.split('/'))[-1]
                    #date_text = date_text.replace(" Updated: ", "")
                    # The date_text could be further modified to represent a proper date format
                    data.append(date_text)
                except:
                    err["link"]=link
                    err['published_date']="Error"
                    data.append("-")
                    flag=1
              # drops the complete data if there is an error
                # Adding the scraped date to data
                today = date.today()
                cur_date = str(today)
                data.append(cur_date)
                # Scraping the paragraph
                try:
                    para_ele = (l_soup.findAll(
                        "div", {"class": para_div_class}))[-1]
                    data.append(para_ele.text)  # Need to make this better
                except:
                    err["link"]=link
                    err['text']="Error"
                    data.append("-")
                    flag=1
                  # drops the complete data if there is an error
                # Adding data to a collection
                
                if flag==1:
                    Errors["globenewswire"].append(err)
                
                collection.append(data)
                
            thread_list=[]
            length=len(links)
            for i in range(length):
                thread_list.append(threading.Thread(target=getarticles, args=(links[i], )))
            
            for thread in thread_list:
                thread.start()
            
            for thread in thread_list:
                thread.join()
            
            df = pd.DataFrame(collection, columns=[
                              'title', 'link', 'publish_date', 'scraped_date', 'text'])
            
            
            # print(df) # For debugging. To check if df is created
            # print(err_logs) # For debugging - to check if any errors occoured
            df = FilterFunction(df)
            emptydataframe("globenewswire", df)
            # df  = link_correction(df)
            return df
        
        except:
            not_working_functions.append("globenewswire")
            print("globenewswire not working")
            
    def bing_search():
        try:
            print("Bing")
            Errors["Bing"]=[]
            try:

                site = "https://www.bing.com/news/search?q=eyes+Ipo+OR+Ipo+listing+OR+aims+for+Ipo+OR+eyes+Ipo+OR+upcoming+Ipos+Or+going+to+list"

                hdr = {'User-Agent': 'Mozilla/5.0'}
                req = rs(site, headers=hdr)
                page = urlopen(req)
                soup = BeautifulSoup(page, "html.parser")

                x = soup.find("div", id="newsFilterV5")
                x = x.ul.li.ul
                for i in x.find_all("li"):
                    if str(i.text) == "Past 24 hours":
                        y = i.a.get('href')

                time.sleep(0.4)

                site = "https://www.bing.com"+y
                
                options = webdriver.ChromeOptions() 
                options.headless = True
                options.add_experimental_option('excludeSwitches', ['enable-logging']) 
                service = ChromeService(executable_path=ChromeDriverManager().install())
                driver = webdriver.Chrome(service=service, options=options)
                driver.get(site)
                time.sleep(1) 
                scroll_pause_time = 0.8
                screen_height = driver.execute_script("return window.screen.height;")   # get the screen height of the web
                i = 1
                while True:
                    driver.execute_script("window.scrollTo(0, {screen_height}*{i});".format(screen_height=screen_height, i=i))  
                    i += 1
                    time.sleep(scroll_pause_time)

                    scroll_height = driver.execute_script("return document.body.scrollHeight;")  

                    if (screen_height) * i > scroll_height:
                        break 
            except:
                print("Bing not working")
                not_working_functions.append('Bing')
                err = "Error in main link finder"
                Errors["Bing"].append(err)
                return
                

            list_of_titles = []
            list_of_text = []
            list_of_links = []
            list_of_published_dates = []
            scraped_time = []
            try:
                soup = BeautifulSoup(driver.page_source, "html.parser")
            except:
                print("Bing not working")
                not_working_functions.append('Bing')
                err = "driver page didn't load/Error in page produced by driver"
                Errors["Bing"].append(err)
                return

            x= soup.find_all("div", class_="news-card newsitem cardcommon b_cards2")
            
            def getarticles(i):
                current_time = date.today()
                flag=0
                err=err_dict()
                try:
                    link = i.find_all("a")[0].get('href')
                    article = Article(link)
                    article.download()
                    article.parse()
                    article.nlp()
                except:
                    try:
                        link
                        
                        try:
                            name = i.find("div", class_="t_t").a.text
                        except:
                            err["link"]=link
                            err['title']="Error"
                            name="-"
                            flag=1
                            

                        try:
                            text = i.find("div", class_="snippet").text
                        except:
                            err["link"]=link
                            err['text']="Error"
                            text="-"
                            flag=1
                        
                        list_of_titles.append(name)
                        list_of_text.append(text)
                        list_of_links.append(link)
                        list_of_published_dates.append(current_time)
                        scraped_time.append(current_time)
                        
                        if flag==1:
                            Errors["Bing"].append(err)
                        return
                    
                    except:
                        err["link"]="Link not extracted properly"
                        Errors["Bing"].append(err)
                        return
                
                try:
                    name=article.title
                except:
                    err["link"]=link
                    err['title']="Error"
                    name="-"
                    flag=1
                
                try:
                    text=article.text
                except:
                    err["link"]=link
                    err['text']="Error"
                    text="-"
                    flag=1

                list_of_titles.append(name)
                list_of_text.append(text)
                list_of_links.append(link)
                list_of_published_dates.append(current_time)
                scraped_time.append(current_time)
                
                if flag==1:
                    Errors["Bing"].append(err)
            
            
            thread_list=[]
            length=len(x)
            for i in range(length):
                thread_list.append(threading.Thread(target=getarticles, args=(x[i], )))
            
            for thread in thread_list:
                thread.start()
            
            for thread in thread_list:
                thread.join()

            scrapedData = {}

            scrapedData["title"] = list_of_titles
            scrapedData["link"] = list_of_links
            scrapedData["publish_date"] = list_of_published_dates
            scrapedData["scraped_date"] = scraped_time
            scrapedData["text"] = list_of_text
            bing_search = pd.DataFrame(scrapedData)


            df = FilterFunction(bing_search)
            emptydataframe("bing_search", df)
            # df  = link_correction(df)
            return df
        except:
            not_working_functions.append("IPO Bing_search")
            print("Bing Search not working")
            df1 = pd.DataFrame(
                columns=['title', 'link', 'publish_date', 'scraped_date'])
            return df1

    def autonews():
        try:
            print("autonews")
            Errors["autonews"]=[]
            
            
            
            url = "https://www.autonews.com/search?search_phrase=ipo&field_emphasis_image=&sort_by=search_api_relevance"
            domain_url = "https://www.autonews.com/"
            

            headers = {
                "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10.15; rv:78.0) Gecko/20100101 Firefox/78.0",
                "accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.9",
                'sec-fetch-site': 'none',
                'sec-fetch-mode': 'navigate',
                'sec-fetch-user': '?1',
                'sec-fetch-dest': 'document',
                'accept-language': 'en-GB,en-US;q=0.9,en;q=0.8',
            }
            #h1_class = "_1Y-96"
            #h1_div_class = "col-xs-12"
            div_class="views-field views-field-nothing"# Class name of div containing the a tag
            #h1_class = "_1Y-96"
            #h1_div_class = "col-xs-12"
            title_h1_itemprop= "headline"
            date_span_class= ["text-gray article-created-date"]
            para_div_itemprop=["articleBody"]
            links = []
            try:
                page = requests.get(url, headers=headers)
                soup = BeautifulSoup(page.content, "html.parser")
            except:
                print("autonews not working")
                not_working_functions.append('autonews')
                err = "Main link did not load: " + url
                Errors["autonews"].append(err)
                return
            
            
            try:
                
                for h2_tag in soup.find_all("div", {"class": div_class}):
                    for a in h2_tag.find_all("a", href=True):
                        link = a["href"]  # Gets the link
                        # Checking the link if it is a relative link
                        if link[0] == '/':
                            link = domain_url + link[1:]
                        # Filtering advertaisment links
                        link_start = domain_url
                        if link.startswith(link_start):
                            links.append(link)
            except:
                if len(links)==0:
                    print("autonews not working")
                    not_working_functions.append('autonews')
                    Errors["autonews"].append("Extraction of link not working.")
                    return
                        
            # Remove duplicates
            links = list(set(links))
            
            # links # Debugging - if link array is generated
            collection = []
            scrapper_name = "autonews"
            
            def getarticles(link):
                flag=0
                err=err_dict()
                try:
                    l_page = requests.get(link, headers=headers)
                    l_soup = BeautifulSoup(l_page.content, 'html.parser')
                except:
                    err["link"]="Link not working: "+link
                    Errors["autonews"].append(err)
                    return
                
                data = []
                
                # Scraping the heading
                #h1_ele = l_soup.find("h1", {"class": h1_class})
                
                try:
                    title_ele = l_soup.find("h1", {"itemprop": title_h1_itemprop})
                    data.append(title_ele.text)
                except:
                    err["link"]=link
                    err['title']="Error"
                    data.append("-")
                    flag=1
                 # drops the complete data if there is an error
                # Adding the link to data
                data.append(link)
                # Scraping the published date
                try:
                    
                    date_ele = l_soup.find("span", {"class": date_span_class})
                    date_text = date_ele.text
                    date_text = date_text.strip("\n")
                    date_text = date_text.strip(" ")
                    date_text = date_text.strip("\t")
                    l1=date_text.split(" ")
                    date_text=l1[1].strip(",")+" "+l1[0]+" "+l1[2]
                    data.append(date_text)
                    

                    #date_text = (date_text.split('/'))[-1]
                    #date_text = date_text.replace(" Updated: ", "")
                    # The date_text could be further modified to represent a proper date format
                    
                except:
                    err["link"]=link
                    err['published_date']="Error"
                    data.append("-")
                    flag=1
              # drops the complete data if there is an error
                # Adding the scraped date to data
                today = date.today()
                cur_date = str(today)
                data.append(cur_date)
                # Scraping the paragraph
                try:
                    para_ele = (l_soup.findAll(
                        "div", {"itemprop": para_div_itemprop}))[-1]
                    data.append(para_ele.text)  # Need to make this better
                except:
                    err["link"]=link
                    err['text']="Error"
                    data.append("-")
                    flag=1
                  # drops the complete data if there is an error
                # Adding data to a collection
                
                if flag==1:
                    Errors["autonews"].append(err)
                
                collection.append(data)
                
            thread_list=[]
            length=len(links)
            for i in range(length):
                thread_list.append(threading.Thread(target=getarticles, args=(links[i], )))
            
            for thread in thread_list:
                thread.start()
            
            for thread in thread_list:
                thread.join()
            
            df = pd.DataFrame(collection, columns=[
                              'title', 'link', 'publish_date', 'scraped_date', 'text'])
            
            
            # print(df) # For debugging. To check if df is created
            # print(err_logs) # For debugging - to check if any errors occoured
            df = FilterFunction(df)
            emptydataframe("autonews ", df)
            # df  = link_correction(df)
            return df
        
        except:
            not_working_functions.append("autonews")
            print("autonews not working")

    def capacitymedia():
        try:
            print("capacitymedia")
            Errors["capacitymedia"]=[]
            
            
            
            url = "https://www.capacitymedia.com/search?q=IPO&f0=2022-01-27%3A&f0From=2022-01-27&f0To=&s=0"
            domain_url = "https://www.capacitymedia.com/"
            

            headers = {
                "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10.15; rv:78.0) Gecko/20100101 Firefox/78.0",
                "accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.9",
                'sec-fetch-site': 'none',
                'sec-fetch-mode': 'navigate',
                'sec-fetch-user': '?1',
                'sec-fetch-dest': 'document',
                'accept-language': 'en-GB,en-US;q=0.9,en;q=0.8',
            }
            div_class="PromoM-content"# Class name of div containing the a tag
            #h1_class = "_1Y-96"
            #h1_div_class = "col-xs-12"
            title_h1_class= "ArticlePage-headline"
            date_div_class= ["ArticlePage-datePublished"]
            para_div_class=["RichTextArticleBody-body RichTextBody"]
            links=[]
            try:
                page = requests.get(url, headers=headers)
                soup = BeautifulSoup(page.content, "html.parser")
            except:
                print("capacitymedia not working")
                not_working_functions.append('capacitymedia')
                err = "Main link did not load: " + url
                Errors["capacitymedia"].append(err)
                return
            
            
            try:
                
                for h2_tag in soup.find_all("div", {"class": div_class}):
                    for a in h2_tag.find_all("a", href=True):
                        link = a["href"]  # Gets the link
                        # Checking the link if it is a relative link
                        if link[0] == '/':
                            link = domain_url + link[1:]
                        # Filtering advertaisment links
                        link_start = domain_url
                        if link.startswith(link_start):
                            links.append(link)
            except:
                if len(links)==0:
                    print("capacitymedia not working")
                    not_working_functions.append('capacitymedia')
                    Errors["capacitymedia"].append("Extraction of link not working.")
                    return
                        
            # Remove duplicates
            links = list(set(links))
            
            # links # Debugging - if link array is generated
            collection = []
            scrapper_name = "capacitymedia"
            
            def getarticles(link):
                flag=0
                err=err_dict()
                try:
                    l_page = requests.get(link, headers=headers)
                    l_soup = BeautifulSoup(l_page.content, 'html.parser')
                except:
                    err["link"]="Link not working: "+link
                    Errors["capacitymedia"].append(err)
                    return
                
                data = []
                
                # Scraping the heading
                #h1_ele = l_soup.find("h1", {"class": h1_class})
                
                try:
                    title_ele = l_soup.find("h1", {"class": title_h1_class})
                    data.append(title_ele.text)
                except:
                    err["link"]=link
                    err['title']="Error"
                    data.append("-")
                    flag=1
                 # drops the complete data if there is an error
                # Adding the link to data
                data.append(link)
                # Scraping the published date
                try:
                    date_ele = l_soup.find("div", {"class": date_div_class})
                    date_text = date_ele.text
                    date_text = date_text.strip("\n")
                    date_text = date_text.strip(" ")
                    date_text = date_text.strip("\t")
                    l1=date_text.split(" ")
                    date_text=l1[1].strip(",")+" "+l1[0]+" "+l1[2]
                    #date_text = (date_text.split('/'))[-1]
                    #date_text = date_text.replace(" Updated: ", "")
                    # The date_text could be further modified to represent a proper date format
                    data.append(date_text)
                except:
                    err["link"]=link
                    err['published_date']="Error"
                    data.append("-")
                    flag=1
              # drops the complete data if there is an error
                # Adding the scraped date to data
                today = date.today()
                cur_date = str(today)
                data.append(cur_date)
                # Scraping the paragraph
                try:
                    para_ele = (l_soup.findAll("div", {"class": para_div_class}))[-1]
                    data.append(para_ele.text)  # Need to make this better
                except:
                    err["link"]=link
                    err['text']="Error"
                    data.append("-")
                    flag=1
                  # drops the complete data if there is an error
                # Adding data to a collection
                
                if flag==1:
                    Errors["capacitymedia"].append(err)
                
                collection.append(data)
                
            thread_list=[]
            length=len(links)
            for i in range(length):
                thread_list.append(threading.Thread(target=getarticles, args=(links[i], )))
            
            for thread in thread_list:
                thread.start()
            
            for thread in thread_list:
                thread.join()
            
            df = pd.DataFrame(collection, columns=[
                              'title', 'link', 'publish_date', 'scraped_date', 'text'])
            
            
            # print(df) # For debugging. To check if df is created
            # print(err_logs) # For debugging - to check if any errors occoured
            df = FilterFunction(df)
            emptydataframe("capacitymedia ", df)
            # df  = link_correction(df)
            return df
        
        except:
            not_working_functions.append("capacitymedia")
            print("capacitymedia not working")

    def kenyanwallstreet():
        try:
            print("kenyanwallstreet")
            Errors["kenyanwallstreet"]=[]
            
            
            
            url = "https://kenyanwallstreet.com/?s=ipo"
            domain_url = "https://kenyanwallstreet.com/"
            

            headers = {
                "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10.15; rv:78.0) Gecko/20100101 Firefox/78.0",
                "accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.9",
                'sec-fetch-site': 'none',
                'sec-fetch-mode': 'navigate',
                'sec-fetch-user': '?1',
                'sec-fetch-dest': 'document',
                'accept-language': 'en-GB,en-US;q=0.9,en;q=0.8',
            }
            article_class="jeg_post jeg_pl_md_1 format-standard"# Class name of div containing the a tag
            #h1_class = "_1Y-96"
            #h1_div_class = "col-xs-12"
            date_div_class= ["jeg_meta_date"]
            
            para_div_class=["entry-content no-share"]
            links=[]
            try:
                page = requests.get(url, headers=headers)
                soup = BeautifulSoup(page.content, "html.parser")
            except:
                print("kenyanwallstreet not working")
                not_working_functions.append('kenyanwallstreet')
                err = "Main link did not load: " + url
                Errors["kenyanwallstreet"].append(err)
                return
            
            
            try:
                
                for h2_tag in soup.find_all("article", {"class": article_class}):
                    for a in h2_tag.find_all("a", href=True):
                        link = a["href"]  # Gets the link
                        # Checking the link if it is a relative link
                        if link[0] == '/':
                            link = domain_url + link[1:]
                        # Filtering advertaisment links
                        link_start = domain_url
                        if link.startswith(link_start):
                            links.append(link)
            except:
                if len(links)==0:
                    print("kenyanwallstreet not working")
                    not_working_functions.append('kenyanwallstreet')
                    Errors["kenyanwallstreet"].append("Extraction of link not working.")
                    return
                        
            # Remove duplicates
            links = list(set(links))
            
            # links # Debugging - if link array is generated
            collection = []
            scrapper_name = "kenyanwallstreet"
            
            def getarticles(link):
                flag=0
                err=err_dict()
                try:
                    l_page = requests.get(link, headers=headers)
                    l_soup = BeautifulSoup(l_page.content, 'html.parser')
                except:
                    err["link"]="Link not working: "+link
                    Errors["kenyanwallstreet"].append(err)
                    return
                
                data = []
                
                # Scraping the heading
                #h1_ele = l_soup.find("h1", {"class": h1_class})
                
                try:
                    title_ele = l_soup.find("h1")
                    data.append(title_ele.text)
                except:
                    err["link"]=link
                    err['title']="Error"
                    data.append("-")
                    flag=1
                 # drops the complete data if there is an error
                # Adding the link to data
                data.append(link)
                # Scraping the published date
                try:
                    date_ele = l_soup.find("div", {"class": date_div_class})
                    date_text = date_ele.text
                    date_text = date_text.strip("\n")
                    date_text = date_text.strip(" ")
                    date_text = date_text.strip("\t")
                    l1=date_text.split(" ")
                    date_text=l1[1].strip(",")+" "+l1[0]+" "+l1[2]
                    #date_text = (date_text.split('/'))[-1]
                    #date_text = date_text.replace(" Updated: ", "")
                    # The date_text could be further modified to represent a proper date format
                    data.append(date_text)
                except:
                    err["link"]=link
                    err['published_date']="Error"
                    data.append("-")
                    flag=1
              # drops the complete data if there is an error
                # Adding the scraped date to data
                today = date.today()
                cur_date = str(today)
                data.append(cur_date)
                # Scraping the paragraph
                try:
                    para_ele = (l_soup.findAll("div", {"class": para_div_class}))[-1]
                    data.append(para_ele.text)  # Need to make this better
                except:
                    err["link"]=link
                    err['text']="Error"
                    data.append("-")
                    flag=1
                  # drops the complete data if there is an error
                # Adding data to a collection
                
                if flag==1:
                    Errors["kenyanwallstreet"].append(err)
                
                collection.append(data)
                
            thread_list=[]
            length=len(links)
            for i in range(length):
                thread_list.append(threading.Thread(target=getarticles, args=(links[i], )))
            
            for thread in thread_list:
                thread.start()
            
            for thread in thread_list:
                thread.join()
            
            df = pd.DataFrame(collection, columns=[
                              'title', 'link', 'publish_date', 'scraped_date', 'text'])
            
            
            # print(df) # For debugging. To check if df is created
            # print(err_logs) # For debugging - to check if any errors occoured
            df = FilterFunction(df)
            emptydataframe("kenyanwallstreet", df)
            # df  = link_correction(df)
            return df
        
        except:
            not_working_functions.append("kenyanwallstreet")
            print("kenyanwallstreet not working")

    def thesundaily():
        try:
            print("thesundaily")
            Errors["thesundaily"]=[]
            
            
            
            url = "https://www.thesundaily.my/search-result/-/search/ipo/false/false/19801109/20221109/date/true/true/0/0/meta/0/0/0/1"
            domain_url = "https://www.thesundaily.my/"

            headers = {
                "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10.15; rv:78.0) Gecko/20100101 Firefox/78.0",
                "accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.9",
                'sec-fetch-site': 'none',
                'sec-fetch-mode': 'navigate',
                'sec-fetch-user': '?1',
                'sec-fetch-dest': 'document',
                'accept-language': 'en-GB,en-US;q=0.9,en;q=0.8',
            }
            ul_class="noticias"
            date_li_class= ["date"]
            para_div_class=["paragraph"]
            links=[]
            try:
                page = requests.get(url, headers=headers)
                soup = BeautifulSoup(page.content, "html.parser")
            except:
                print("thesundaily not working")
                not_working_functions.append('thesundaily')
                err = "Main link did not load: " + url
                Errors["thesundaily"].append(err)
                return
            
            
            try:
                
                for h2_tag in soup.find_all("ul", {"class": ul_class}):
                    for a in h2_tag.find_all("a", href=True):
                        link = a["href"]  # Gets the link
                        # Checking the link if it is a relative link
                        if link[0] == '/':
                            link = domain_url + link[1:]
                        # Filtering advertaisment links
                        link_start = domain_url
                        if link.startswith(link_start):
                            links.append(link)
            except:
                if len(links)==0:
                    print("thesundaily not working")
                    not_working_functions.append('thesundaily')
                    Errors["thesundaily"].append("Extraction of link not working.")
                    return
                        
            # Remove duplicates
            links = list(set(links))
            
            # links # Debugging - if link array is generated
            collection = []
            scrapper_name = "thesundaily"
            
            def getarticles(link):
                flag=0
                err=err_dict()
                try:
                    l_page = requests.get(link, headers=headers)
                    l_soup = BeautifulSoup(l_page.content, 'html.parser')
                except:
                    err["link"]="Link not working: "+link
                    Errors["thesundaily"].append(err)
                    return
                
                data = []
                
                # Scraping the heading
                #h1_ele = l_soup.find("h1", {"class": h1_class})
                
                try:
                    title_ele = l_soup.find("h1")
                    data.append(title_ele.text)
                except:
                    err["link"]=link
                    err['title']="Error"
                    data.append("-")
                    flag=1
                 # drops the complete data if there is an error
                # Adding the link to data
                data.append(link)
                # Scraping the published date
                try:
                    date_ele = l_soup.find("li",{"class":date_li_class})
                    date_text = date_ele.text
                    date_text.strip("")
                    l1=date_text.split("-")
                    date_text=l1[0]+"-"+l1[1]+"-"+l1[2][0:5].strip()
                    
                    #date_text = (date_text.split('/'))[-1]
                    #date_text = date_text.replace(" Updated: ", "")
                    # The date_text could be further modified to represent a proper date format
                    data.append(date_text)
                except:
                    err["link"]=link
                    err['published_date']="Error"
                    data.append("-")
                    flag=1
              # drops the complete data if there is an error
                # Adding the scraped date to data
                today = date.today()
                cur_date = str(today)
                data.append(cur_date)
                # Scraping the paragraph
                try:
                    para_ele = (l_soup.findAll("div", {"class": para_div_class}))[-1]
                    data.append(para_ele.text)  # Need to make this better
                except:
                    err["link"]=link
                    err['text']="Error"
                    data.append("-")
                    flag=1
                  # drops the complete data if there is an error
                # Adding data to a collection
                
                if flag==1:
                    Errors["thesundaily"].append(err)
                
                collection.append(data)
                
            thread_list=[]
            length=len(links)
            for i in range(length):
                thread_list.append(threading.Thread(target=getarticles, args=(links[i], )))
            
            for thread in thread_list:
                thread.start()
            
            for thread in thread_list:
                thread.join()
            
            df = pd.DataFrame(collection, columns=[
                              'title', 'link', 'publish_date', 'scraped_date', 'text'])
            
            
            # print(df) # For debugging. To check if df is created
            # print(err_logs) # For debugging - to check if any errors occoured
            df = FilterFunction(df)
            emptydataframe("thesundaily", df)
            # df  = link_correction(df)
            return df
        
        except:
            not_working_functions.append("thesundaily")
            print("thesundaily not working")

    def digitaljournal():
        try:
            print("digitaljournal")
            Errors["digitaljournal"]=[]
            
            
            
            url = "https://www.digitaljournal.com/?s=ipo"
            domain_url = "https://www.digitaljournal.com/"

            headers = {
                "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10.15; rv:78.0) Gecko/20100101 Firefox/78.0",
                "accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.9",
                'sec-fetch-site': 'none',
                'sec-fetch-mode': 'navigate',
                'sec-fetch-user': '?1',
                'sec-fetch-dest': 'document',
                'accept-language': 'en-GB,en-US;q=0.9,en;q=0.8',
            }
            section_class="zox-art-wrap zoxrel zox-art-mid infinite-post"
            title_h1_class= "zox-post-title left entry-title"
            date_time_class= ["post-date updated"]
            para_div_class=["zox-post-body left zoxrel zox100"]
            links=[]
            try:
                page = requests.get(url, headers=headers)
                soup = BeautifulSoup(page.content, "html.parser")
            except:
                print("digitaljournal not working")
                not_working_functions.append('digitaljournal')
                err = "Main link did not load: " + url
                Errors["digitaljournal"].append(err)
                return
            
            
            try:
                
                for h2_tag in soup.find_all("section", {"class": section_class}):
                    for a in h2_tag.find_all("a", href=True):
                        link = a["href"]  # Gets the link
                        # Checking the link if it is a relative link
                        if link[0] == '/':
                            link = domain_url + link[1:]
                        # Filtering advertaisment links
                        link_start = domain_url
                        if link.startswith(link_start):
                            links.append(link)
            except:
                if len(links)==0:
                    print("digitaljournal not working")
                    not_working_functions.append('digitaljournal')
                    Errors["digitaljournal"].append("Extraction of link not working.")
                    return
                        
            # Remove duplicates
            links = list(set(links))
            
            # links # Debugging - if link array is generated
            collection = []
            scrapper_name = "digitaljournal"
            
            def getarticles(link):
                flag=0
                err=err_dict()
                try:
                    l_page = requests.get(link, headers=headers)
                    l_soup = BeautifulSoup(l_page.content, 'html.parser')
                except:
                    err["link"]="Link not working: "+link
                    Errors["digitaljournal"].append(err)
                    return
                
                data = []
                
                # Scraping the heading
                #h1_ele = l_soup.find("h1", {"class": h1_class})
                
                try:
                    title_ele = l_soup.find("h1", {"class": title_h1_class})
                    data.append(title_ele.text)
                except:
                    err["link"]=link
                    err['title']="Error"
                    data.append("-")
                    flag=1
                 # drops the complete data if there is an error
                # Adding the link to data
                data.append(link)
                # Scraping the published date
                try:
                    date_ele = l_soup.find("time", {"class": date_time_class})
                    date_text = date_ele.text
                    l1=date_text.split(' ')
                    date_text=l1[1].strip(',')+' '+l1[0]+' '+l1[2]
                    
                    #date_text = (date_text.split('/'))[-1]
                    #date_text = date_text.replace(" Updated: ", "")
                    # The date_text could be further modified to represent a proper date format
                    data.append(date_text)
                except:
                    err["link"]=link
                    err['published_date']="Error"
                    data.append("-")
                    flag=1
              # drops the complete data if there is an error
                # Adding the scraped date to data
                today = date.today()
                cur_date = str(today)
                data.append(cur_date)
                # Scraping the paragraph
                try:
                    para_ele = (l_soup.findAll("div", {"class": para_div_class}))[-1]
                    data.append(para_ele.text)  # Need to make this better
                except:
                    err["link"]=link
                    err['text']="Error"
                    data.append("-")
                    flag=1
                  # drops the complete data if there is an error
                # Adding data to a collection
                
                if flag==1:
                    Errors["digitaljournal"].append(err)
                
                collection.append(data)
                
            thread_list=[]
            length=len(links)
            for i in range(length):
                thread_list.append(threading.Thread(target=getarticles, args=(links[i], )))
            
            for thread in thread_list:
                thread.start()
            
            for thread in thread_list:
                thread.join()
            
            df = pd.DataFrame(collection, columns=[
                              'title', 'link', 'publish_date', 'scraped_date', 'text'])
            
            
            # print(df) # For debugging. To check if df is created
            # print(err_logs) # For debugging - to check if any errors occoured
            df = FilterFunction(df)
            emptydataframe("digitaljournal", df)
            # df  = link_correction(df)
            return df
        
        except:
            not_working_functions.append("digitaljournal")
            print("digitaljournal not working")
        
                
    
            
            
    #                                  Final
    
    
    
    
    
    df1=korea()
    df2=proactive("ipo")
    df3=gulfbusiness()
    df4=investmentu()
    df5=einnews()
    df6=businessinsider()
    df7=Reuters("ipo")
    df8=Reuters("pre ipo")
    df9=Reuters("Initial Public Offering")
    df10=google_news()
    df11=defenseworld()
    df12=technode()
    df13=globenewswire()
    df14=bing_search()
    df15=autonews()
    df16=capacitymedia()
    df17=kenyanwallstreet()
    df18=thesundaily()
    df19=digitaljournal()
    
    df_final_1 = [ df1, df2, df3, df4, df5, df6, df7, df8, df9, df10 , df11, df12, df13, df14, df15, df16, df17, df18, df19]
    
    
    
       
    
    df_final = pd.concat(df_final_1)

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
                        
    
    
    
# multilex_scraper("/home/prachi_multilex2", "/home/prachi_multilex2")       # uncomment this line to run this as a python script


# multilex_scraper( "", "")
logging.info("last line of scraper")

if __name__ == "__main__":
    x=time.time()
    multilex_scraper(r"C:\Users\ujwal\OneDrive\Desktop\test",r"C:\Users\ujwal\OneDrive\Desktop\test")
    y=time.time()
    print()
    print()
    print("time taken by scraper.py: ", y-x)
    print()
    print()
        
        