


from newspaper import Article, Config
import requests
import nltk
#nltk.download('punkt')                         # Please uncomment if you're running this program for first time
import threading
from selenium import webdriver
from selenium.webdriver.common.by import By
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.chrome.service import Service as ChromeService
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
            
    
    
    def gulfbusiness(keyword):
        try:
            print("gulfbusiness")
            Errors["gulfbusiness"]=[]
            
            
            
            url = f"https://gulfbusiness.com/?s={keyword}"
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
                    date_text=date_text.strip("\n")
                    l=date_text.split(" ")
                    date_text=l[1].strip(",")+"-"+l[0]+'-'+l[2]

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
    
    def investmentu(keyword):
        try:
            print("investmentu")
            Errors["investmentu"]=[]
            
            
            
            url = f"https://investmentu.com/?s={keyword}"
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
                    l=date_text.split(" ")
                    date_text=l[1].strip(",")+"-"+l[0]+"-"+l[2]

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
            
            headers = {
                "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10.15; rv:78.0) Gecko/20100101 Firefox/78.0",
                "accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.9",
                'sec-fetch-site': 'none',
                'sec-fetch-mode': 'navigate',
                'sec-fetch-user': '?1',
                'sec-fetch-dest': 'document',
                'accept-language': 'en-GB,en-US;q=0.9,en;q=0.8',
            }

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
                pageSource = requests.get(queryUrl, headers=headers).content
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

    def businessinsider(keyword):
        try:
            print("businessinsider")
            Errors["businessinsider"]=[]
            
            
            
            url = f"https://www.businessinsider.in/searchresult.cms?query={keyword}&sortorder=score"
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
                    date_ele = l_soup.find("span",{"class":"Date"})
                    date_text = date_ele.text[0:14]
                    date_text=date_text.split(",")
                    date_text = ",".join([date_text[0], date_text[1]])

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
                
                
                lin=[]
                
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
                    lin.append(l)
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
                               'title': title, 'link': lin, 'text': text}
            
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
    
    
    def google_news(keyword):
        try:
            print("Google")
            print(f"Keyword: {keyword}")
            Errors["Google"]=[]
            options = webdriver.ChromeOptions() 
            options.headless = True
            options.add_argument('--no-sandbox')
            options.add_argument('--disable-dev-shm-usage')
            options.add_experimental_option('excludeSwitches', ['enable-logging']) 
            service = ChromeService(executable_path=ChromeDriverManager().install())
            driver = webdriver.Chrome(service=service, options=options)
            try:
                keyword = urllib.parse.quote(keyword)
                url = f"https://www.google.com/search?q={keyword}"
                website="https://www.google.com"
                driver.get(url)
                news=driver.find_element(By.XPATH, '//*[@id="hdtb-msb"]/div[1]/div/div[2]/a')
                time.sleep(2)
                news.click()
                time.sleep(0.6)
                tools=driver.find_element(By.XPATH, '//*[@id="hdtb-tls"]')
                tools.click()
                
                time.sleep(0.8)
                recent=driver.find_element(By.CLASS_NAME, "KTBKoe")
                recent.click()
                
                time.sleep(0.9)
                past_24_hours=driver.find_element(By.XPATH, '//*[@id="lb"]/div/g-menu/g-menu-item[3]/div/a')
                past_24_hours.click()
                
            except:
                print("Google not working")
                try:
                    driver.quit()
                except:
                    pass
                not_working_functions.append('Google')
                err = "Error in Module "
                Errors["Google"].append(err)
                return
            
            links=[]
            titles=[]
            texts=[]
            
            page_number=0
            try:
                while True:
                    try:
                        flag=0
                        page=BeautifulSoup(driver.page_source, "html.parser")
                        articles=page.find("div", {"class": "MjjYud"}).div.findChildren("div")
                        for i in range(len(articles)):
                            try:
                                link=articles[i].find("a", class_="WlydOe").get("href")
                                try:
                                    if link!=links[-1]:
                                        links.append(link)
                                except:
                                    links.append(link)
                                try:
                                    title=translatedeep(articles[i].find("div", class_="n0jPhd ynAwRc MBeuO nDgy9d").text)
                                    try:
                                        if title!=titles[-1]:
                                            if title:
                                                titles.append(title)
                                            else:
                                                titles.append("-")
                                    except:
                                        if title:
                                            titles.append(title)
                                        else:
                                            titles.append("-")
                                except:
                                    titles.append("-")
                                try:
                                    text=translatedeep(articles[i].find("div", class_="GI74Re nDgy9d").text)
                                    try:
                                        if text!=texts[-1]:
                                            if text:
                                                texts.append(text)
                                            else:
                                                texts.append("-")
                                    except:
                                        if text:
                                            texts.append(text)
                                        else:
                                            texts.append("-")
                                except:
                                    texts.append("-")
                                
                            except:
                                continue
                        page_number+=1
                        print(f"Finished page number: {page_number}")
                        print(f"Numbers of articles collected: {len(links)}")
                        print(f"Number of titles collected: {len(titles)}")
                        print(f"Number of texts collected: {len(texts)}")
                        time.sleep(round(random.uniform(0.5, 1.1), 2))
                        next_page=driver.find_element(By.ID, "pnnext")
                        next_page.click()    
                    except Exception as e:
                        print(e)
                        try:
                            driver.quit()
                        except:
                            ""
                        break
                    
                
            except:
                if len(links)==0:
                            print("Google not working")
                            not_working_functions.append('Google')
                            Errors["Google"].append("Extraction of link not working.")
                            return
            
            final_links = []
            title, text, pub_date, scraped_date = [], [], [], []
            today = date.today()
            
            def getartciles(link, a, b):
                    today=date.today()
                    final_links.append(link)
                    title.append(a)
                    text.append(b)
                    scraped_date.append(str(today))
                    pub_date.append(str(today))

            
            thread_list=[]
            length=len(links)
            for i in range(length):
                thread_list.append(threading.Thread(target=getartciles, args=(links[i],titles[i], texts[i], )))
            
            for thread in thread_list:
                thread.start()
            
            for thread in thread_list:
                thread.join()
            
            df = pd.DataFrame({"text": text, "link": final_links,
                                "publish_date": pub_date, "scraped_date": scraped_date, "title": title})
            
            df = df.drop_duplicates(subset=["link"])
            emptydataframe("Google", df)
            
            return df
        
        except:
            print("Google not working")
            not_working_functions.append('Google')

    def defenseworld(keyword):
        try:
            print("defenseworld")
            Errors["defenseworld"]=[]
            
            
            
            url = f"https://www.defenseworld.net/?s={keyword}"
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

    def technode(keyword):
        try:
            print("technode")
            Errors["technode"]=[]
            
            
            
            url = f"https://technode.com/?s={keyword}"
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

    def globenewswire(keyword):
        try:
            print("globenewswire")
            Errors["globenewswire"]=[]
            
            
            
            url = f"https://www.globenewswire.com/search/keyword/{keyword}"
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
            
    def bing_search(keyword="IPO"):
        try:
            
            print("Bing")
            print(f"Keyword: {keyword}")
            Errors["Bing"]=[]
            keyword = urllib.parse.quote(keyword)
            try:

                site = f"https://www.bing.com/news/search?q={keyword}"

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
                options.add_argument('--no-sandbox')
                options.add_argument('--disable-dev-shm-usage')
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
            except Exception as e:
                print("Bing not working")
                not_working_functions.append('Bing')
                err = "Error in main link finder"
                Errors["Bing"].append(err)
                print("Error: ", e)
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
            driver.close()
            driver.quit()
            titles=[]
            texts=[]
            links=[]
            x= soup.find_all("div", class_="news-card newsitem cardcommon")
            for i in x:
                try:
                    links.append(i.get("url"))
                    try:
                        title=translatedeep(i.find("a", class_="title").get_text())
                        if title:
                            titles.append(title)
                        else:
                           titles.append("-") 
                    except:
                        titles.append("-")
                    try:
                        text=translatedeep(i.find("div", class_="snippet").text)
                        if text:
                            texts.append(text)
                        else:
                            texts.append("-")
                    except:
                        texts.append("-")
                except:
                    continue
            
            print(f"number of links produced = {len(links)}")
            print(f"number of titles produced = {len(titles)}")
            print(f"number of texts produced = {len(texts)}")    
            
            def getarticles(i, title="-", text1="-"):
                current_time = date.today()
                list_of_titles.append(title)
                list_of_text.append(text1)
                list_of_links.append(i)
                list_of_published_dates.append(current_time)
                scraped_time.append(current_time)
                
            
            thread_list=[]
            length=len(links)
            for i in range(length):
                thread_list.append(threading.Thread(target=getarticles, args=(links[i], titles[i], texts[i], )))
            
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


            df = bing_search
            emptydataframe("bing_search", df)
            # df  = link_correction(df)
            return df
        except:
            not_working_functions.append("IPO Bing_search")
            print("Bing Search not working")
            df1 = pd.DataFrame(
                columns=['title', 'link', 'publish_date', 'scraped_date'])
            return df1

    def autonews(keyword):
        try:
            print("autonews")
            Errors["autonews"]=[]
            
            
            
            url = f"https://www.autonews.com/search?search_phrase={keyword}&field_emphasis_image=&sort_by=search_api_relevance"
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

    def capacitymedia(keyword):
        try:
            print("capacitymedia")
            Errors["capacitymedia"]=[]
            
            
            
            url = f"https://www.capacitymedia.com/search?q={keyword}&f0=2022-01-27%3A&f0From=2022-01-27&f0To=&s=0"
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

    def kenyanwallstreet(keyword):
        try:
            print("kenyanwallstreet")
            Errors["kenyanwallstreet"]=[]
            
            
            
            url = f"https://kenyanwallstreet.com/?s={keyword}"
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

    def thesundaily(keyword):
        try:
            print("thesundaily")
            Errors["thesundaily"]=[]
            
            
            
            url = f"https://www.thesundaily.my/search-result/-/search/{keyword}/false/false/19801109/20221109/date/true/true/0/0/meta/0/0/0/1"
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

    def digitaljournal(keyword):
        try:
            print("digitaljournal")
            Errors["digitaljournal"]=[]
            
            
            
            url = f"https://www.digitaljournal.com/?s={keyword}"
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

    def asiafinancial(keyword):
        try:
            print("asiafinancial")
            Errors["asiafinancial"]=[]
            
            
            
            url = f"https://www.asiafinancial.com/?s={keyword}#"
            domain_url = "https://www.asiafinancial.com/"
            headers = {
                "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10.15; rv:78.0) Gecko/20100101 Firefox/78.0",
                "accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.9",
                'sec-fetch-site': 'none',
                'sec-fetch-mode': 'navigate',
                'sec-fetch-user': '?1',
                'sec-fetch-dest': 'document',
                'accept-language': 'en-GB,en-US;q=0.9,en;q=0.8',
            }
            div_class="tt-post has-thumbnail type-6 clearfix post-430 post type-post status-publish format-standard has-post-thumbnail hentry category-business category-culture tag-all tag-health tag-politics"
            date_span_class= ["tt-post-date"]
            para_div_class=["content"]
            links=[]
            try:
                page = requests.get(url, headers=headers)
                soup = BeautifulSoup(page.content, "html.parser")
            except:
                print("asiafinancial not working")
                not_working_functions.append('asiafinancial')
                err = "Main link did not load: " + url
                Errors["asiafinancial"].append(err)
                return
            
            
            try:
                
                for h2_tag in soup.find_all("div",{"class":div_class}):
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
                    print("asiafinancial not working")
                    not_working_functions.append('asiafinancial')
                    Errors["asiafinancial"].append("Extraction of link not working.")
                    return
                        
            # Remove duplicates
            links = list(set(links))
            
            # links # Debugging - if link array is generated
            collection = []
            scrapper_name = "asiafinancial"
            
            def getarticles(link):
                flag=0
                err=err_dict()
                try:
                    l_page = requests.get(link, headers=headers)
                    l_soup = BeautifulSoup(l_page.content, 'html.parser')
                except:
                    err["link"]="Link not working: "+link
                    Errors["asiafinancial"].append(err)
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
                    date_ele = l_soup.find("span",{"class":date_span_class})
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
                    Errors["asiafinancial"].append(err)
                
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
            emptydataframe("asiafinancial", df)
            # df  = link_correction(df)
            return df
        
        except:
            not_working_functions.append("asiafinancial")
            print("asiafinancial not working")


    def stockhead(keyword):
        try:
            print("stockhead")
            Errors["stockhead"]=[]
            
            
            
            url = f"https://stockhead.com.au/?s={keyword}"
            domain_url = "https://stockhead.com.au/"
            headers = {
                "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10.15; rv:78.0) Gecko/20100101 Firefox/78.0",
                "accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.9",
                'sec-fetch-site': 'none',
                'sec-fetch-mode': 'navigate',
                'sec-fetch-user': '?1',
                'sec-fetch-dest': 'document',
                'accept-language': 'en-GB,en-US;q=0.9,en;q=0.8',
            }
            h2_class = "entry-title"  # Class name of div containing the a tag
            #h1_class = "_1Y-96"
            #h1_div_class = "col-xs-12"
            title_span_class = "title-text"
            date_time_class = ["entry-date published updated"]
            para_div_id = ["primary-0"]
            links=[]
            try:
                page = requests.get(url, headers=headers)
                soup = BeautifulSoup(page.content, "html.parser")
            except:
                print("stockhead not working")
                not_working_functions.append('stockhead')
                err = "Main link did not load: " + url
                Errors["stockhead"].append(err)
                return
            
            
            try:
                
                for h2_tag in soup.find_all("h2", {"class": h2_class}):
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
                    print("stockhead not working")
                    not_working_functions.append('stockhead')
                    Errors["stockhead"].append("Extraction of link not working.")
                    return
                        
            # Remove duplicates
            links = list(set(links))
            
            # links # Debugging - if link array is generated
            collection = []
            scrapper_name = "stockhead"
            
            def getarticles(link):
                flag=0
                err=err_dict()
                try:
                    l_page = requests.get(link, headers=headers)
                    l_soup = BeautifulSoup(l_page.content, 'html.parser')
                except:
                    err["link"]="Link not working: "+link
                    Errors["stockhead"].append(err)
                    return
                
                data = []
                
                # Scraping the heading
                #h1_ele = l_soup.find("h1", {"class": h1_class})
                
                try:
                    title_ele = l_soup.find( "span", {"class": title_span_class})
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
                    para_ele = (l_soup.findAll("div", {"id": para_div_id}))[-1]
                    data.append(para_ele.text)  # Need to make this better
                except:
                    err["link"]=link
                    err['text']="Error"
                    data.append("-")
                    flag=1
                  # drops the complete data if there is an error
                # Adding data to a collection
                
                if flag==1:
                    Errors["stockhead"].append(err)
                
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
            emptydataframe("stockhead", df)
            # df  = link_correction(df)
            return df
        
        except:
            not_working_functions.append("stockhead")
            print("stockhead not working")

    def koreajoongangdaily(keyword):
        try:
            print("koreajoongangdaily")
            Errors["koreajoongangdaily"]=[]
            
            
            
            url = f"https://koreajoongangdaily.joins.com/section/searchResult/{keyword}?searchFlag=1"
            domain_url = "https://koreajoongangdaily.joins.com/"
            headers = {
                "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10.15; rv:78.0) Gecko/20100101 Firefox/78.0",
                "accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.9",
                'sec-fetch-site': 'none',
                'sec-fetch-mode': 'navigate',
                'sec-fetch-user': '?1',
                'sec-fetch-dest': 'document',
                'accept-language': 'en-GB,en-US;q=0.9,en;q=0.8',
            }
            div_class = "mid-article3"  # Class name of div containing the a tag
            #h1_class = "_1Y-96"
            #h1_div_class = "col-xs-12"
            title_h1_class = "view-article-title serif"
            date_div_class = ["article-menu-box"]
            para_div_id = ["article_body"]
            links=[]
            try:
                page = requests.get(url, headers=headers)
                soup = BeautifulSoup(page.content, "html.parser")
            except:
                print("koreajoongangdaily not working")
                not_working_functions.append('koreajoongangdaily')
                err = "Main link did not load: " + url
                Errors["koreajoongangdaily"].append(err)
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
                    print("koreajoongangdaily not working")
                    not_working_functions.append('koreajoongangdaily')
                    Errors["koreajoongangdaily"].append("Extraction of link not working.")
                    return
                        
            # Remove duplicates
            links = list(set(links))
            
            # links # Debugging - if link array is generated
            collection = []
            scrapper_name = "koreajoongangdaily"
            
            def getarticles(link):
                flag=0
                err=err_dict()
                try:
                    l_page = requests.get(link, headers=headers)
                    l_soup = BeautifulSoup(l_page.content, 'html.parser')
                except:
                    err["link"]="Link not working: "+link
                    Errors["koreajoongangdaily"].append(err)
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
                    date_text = link[45:47]+"-"+link[42:44]+"-"+link[37:41]
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
                    para_ele = (l_soup.findAll("div", {"id": para_div_id}))[-1]
                    data.append(para_ele.text)  # Need to make this better
                except:
                    err["link"]=link
                    err['text']="Error"
                    data.append("-")
                    flag=1
                  # drops the complete data if there is an error
                # Adding data to a collection
                
                if flag==1:
                    Errors["koreajoongangdaily"].append(err)
                
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
            emptydataframe("koreajoongangdaily", df)
            # df  = link_correction(df)
            return df
        
        except:
            not_working_functions.append("koreajoongangdaily")
            print("koreajoongangdaily not working")

    def upstreamonline(keyword):
        try:
            print("upstreamonline")
            Errors["upstreamonline"]=[]
            
            
            
            url = f"https://www.upstreamonline.com/archive/?languages=en&locale=en&q={keyword}"
            domain_url = "https://www.upstreamonline.com/"
            headers = {
                "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10.15; rv:78.0) Gecko/20100101 Firefox/78.0",
                "accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.9",
                'sec-fetch-site': 'none',
                'sec-fetch-mode': 'navigate',
                'sec-fetch-user': '?1',
                'sec-fetch-dest': 'document',
                'accept-language': 'en-GB,en-US;q=0.9,en;q=0.8',
            }
            div_class = "mb-auto"  # Class name of div containing the a tag
            #h1_class = "_1Y-96"
            #h1_div_class = "col-xs-12"
            title_h1_class = "fs-xxl fw-bold mb-4 article-title ff-sueca-bold"
            date_span_class = ["st-italic"]
            para_div_class = ["article-body"]
            links=[]
            try:
                page = requests.get(url, headers=headers)
                soup = BeautifulSoup(page.content, "html.parser")
            except:
                print("upstreamonline not working")
                not_working_functions.append('upstreamonline')
                err = "Main link did not load: " + url
                Errors["upstreamonline"].append(err)
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
                    print("upstreamonline not working")
                    not_working_functions.append('upstreamonline')
                    Errors["upstreamonline"].append("Extraction of link not working.")
                    return
                        
            # Remove duplicates
            links = list(set(links))
            
            # links # Debugging - if link array is generated
            collection = []
            scrapper_name = "upstreamonline"
            
            def getarticles(link):
                flag=0
                err=err_dict()
                try:
                    l_page = requests.get(link, headers=headers)
                    l_soup = BeautifulSoup(l_page.content, 'html.parser')
                except:
                    err["link"]="Link not working: "+link
                    Errors["upstreamonline"].append(err)
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
                    date_ele = l_soup.find("span",{"class":date_span_class})
                    date_text = date_ele.text
                    l1=date_text.split("\n")
                    l=l1[2].split(" ")
                    date_text=l[2]+" "+l[3]+" "+l[4]
                    
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
                    Errors["upstreamonline"].append(err)
                
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
            emptydataframe("upstreamonline", df)
            # df  = link_correction(df)
            return df
        
        except:
            not_working_functions.append("upstreamonline")
            print("upstreamonline not working")

    def etfdailynews(keyword):
        try:
            print("etfdailynews")
            Errors["etfdailynews"]=[]
            
            
            
            url = f"https://www.etfdailynews.com/?s={keyword}"
            domain_url = "https://www.etfdailynews.com/"
            headers = {
                "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10.15; rv:78.0) Gecko/20100101 Firefox/78.0",
                "accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.9",
                'sec-fetch-site': 'none',
                'sec-fetch-mode': 'navigate',
                'sec-fetch-user': '?1',
                'sec-fetch-dest': 'document',
                'accept-language': 'en-GB,en-US;q=0.9,en;q=0.8',
            }
            section_class = "archive"  # Class name of div containing the a tag
            #h1_class = "_1Y-96"
            #h1_div_class = "col-xs-12"
            title_h1_itemprop = "headline"
            date_span_itemprop = ["datePublished dateModified"]
            para_div_class = ["entry"]
            links=[]
            try:
                page = requests.get(url, headers=headers)
                soup = BeautifulSoup(page.content, "html.parser")
            except:
                print("etfdailynews not working")
                not_working_functions.append('etfdailynews')
                err = "Main link did not load: " + url
                Errors["etfdailynews"].append(err)
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
                    print("etfdailynews not working")
                    not_working_functions.append('etfdailynews')
                    Errors["etfdailynews"].append("Extraction of link not working.")
                    return
                        
            # Remove duplicates
            links = list(set(links))
            
            # links # Debugging - if link array is generated
            collection = []
            scrapper_name = "etfdailynews"
            
            def getarticles(link):
                flag=0
                err=err_dict()
                try:
                    l_page = requests.get(link, headers=headers)
                    l_soup = BeautifulSoup(l_page.content, 'html.parser')
                except:
                    err["link"]="Link not working: "+link
                    Errors["etfdailynews"].append(err)
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
                    
                    date_text=link[37:39]+"-"+link[34:36]+"-"+link[29:33]
                    
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
                    Errors["etfdailynews"].append(err)
                
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
            emptydataframe("etfdailynews", df)
            # df  = link_correction(df)
            return df
        
        except:
            not_working_functions.append("etfdailynews")
            print("etfdailynews not working")
        

    def splash247(keyword):
        try:
            print("splash247")
            Errors["splash247"]=[]
            
            
            
            url = f"https://splash247.com/?s={keyword}"
            domain_url = "https://splash247.com/"
            headers = {
                "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10.15; rv:78.0) Gecko/20100101 Firefox/78.0",
                "accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.9",
                'sec-fetch-site': 'none',
                'sec-fetch-mode': 'navigate',
                'sec-fetch-user': '?1',
                'sec-fetch-dest': 'document',
                'accept-language': 'en-GB,en-US;q=0.9,en;q=0.8',
            }
            div_class = "post-details"  # Class name of div containing the a tag
            #h1_class = "_1Y-96"
            #h1_div_class = "col-xs-12"
            title_h1_class = "post-title entry-title"
            date_span_class = ["date meta-item tie-icon"]
            para_div_class = ["entry-content entry clearfix"]
            links=[]
            try:
                page = requests.get(url, headers=headers)
                soup = BeautifulSoup(page.content, "html.parser")
            except:
                print("splash247 not working")
                not_working_functions.append('splash247')
                err = "Main link did not load: " + url
                Errors["splash247"].append(err)
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
                    print("splash247 not working")
                    not_working_functions.append('splash247')
                    Errors["splash247"].append("Extraction of link not working.")
                    return
                        
            # Remove duplicates
            links = list(set(links))
            
            # links # Debugging - if link array is generated
            collection = []
            scrapper_name = "splash247"
            
            def getarticles(link):
                flag=0
                err=err_dict()
                try:
                    l_page = requests.get(link, headers=headers)
                    l_soup = BeautifulSoup(l_page.content, 'html.parser')
                except:
                    err["link"]="Link not working: "+link
                    Errors["splash247"].append(err)
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
                    
                    date_ele = l_soup.find("span",{"class":date_span_class})
                    date_text = date_ele.text
                    l=date_text.split(" ")
                    date_text=l[1].strip(',')+" "+l[0]+" "+l[2]
                    
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
                    Errors["splash247"].append(err)
                
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
            emptydataframe("splash247", df)
            # df  = link_correction(df)
            return df
        
        except:
            not_working_functions.append("splash247")
            print("splash247 not working")

    def brisbanetimes(keyword):
        try:
            print("brisbanetimes")
            Errors["brisbanetimes"]=[]
            
            
            
            url = f"https://www.brisbanetimes.com.au/search?text={keyword}"
            domain_url = "https://www.brisbanetimes.com.au/"
            headers = {
                "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10.15; rv:78.0) Gecko/20100101 Firefox/78.0",
                "accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.9",
                'sec-fetch-site': 'none',
                'sec-fetch-mode': 'navigate',
                'sec-fetch-user': '?1',
                'sec-fetch-dest': 'document',
                'accept-language': 'en-GB,en-US;q=0.9,en;q=0.8',
            }
            div_class = "_2g9tm"  # Class name of div containing the a tag
            #h1_class = "_1Y-96"
            #h1_div_class = "col-xs-12"
            title_h1_itemprop = "headline"
            date_span_class = ["_2xetH"]
            para_div_class = ["_1665V _2q-Vk"]
            links=[]
            try:
                page = requests.get(url, headers=headers)
                soup = BeautifulSoup(page.content, "html.parser")
            except:
                print("brisbanetimes not working")
                not_working_functions.append('brisbanetimes')
                err = "Main link did not load: " + url
                Errors["brisbanetimes"].append(err)
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
                    print("brisbanetimes not working")
                    not_working_functions.append('brisbanetimes')
                    Errors["brisbanetimes"].append("Extraction of link not working.")
                    return
                        
            # Remove duplicates
            links = list(set(links))
            
            # links # Debugging - if link array is generated
            collection = []
            scrapper_name = "brisbanetimes"
            
            def getarticles(link):
                flag=0
                err=err_dict()
                try:
                    l_page = requests.get(link, headers=headers)
                    l_soup = BeautifulSoup(l_page.content, 'html.parser')
                except:
                    err["link"]="Link not working: "+link
                    Errors["brisbanetimes"].append(err)
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
                    
                    date_ele = l_soup.find("span",{"class":date_span_class})
                    date_text = date_ele.text
                    l=date_text.split(" ")
                    date_text=l[1].strip(',')+" "+l[0]+" "+l[2]
                    
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
                    Errors["brisbanetimes"].append(err)
                
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
            emptydataframe("brisbanetimes", df)
            # df  = link_correction(df)
            return df
        
        except:
            not_working_functions.append("brisbanetimes")
            print("brisbanetimes not working")

    def zdnet(keyword):
        try:
            print("zdnet")
            Errors["zdnet"]=[]
            
            
            
            url = f"https://www.zdnet.com/search/?q={keyword}"
            domain_url = "https://www.zdnet.com/"
            headers = {
                "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10.15; rv:78.0) Gecko/20100101 Firefox/78.0",
                "accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.9",
                'sec-fetch-site': 'none',
                'sec-fetch-mode': 'navigate',
                'sec-fetch-user': '?1',
                'sec-fetch-dest': 'document',
                'accept-language': 'en-GB,en-US;q=0.9,en;q=0.8',
            }
            article_class = "item"  # Class name of div containing the a tag
            #h1_class = "_1Y-96"
            #h1_div_class = "col-xs-12"
            title_h1_class = "c-contentHeader_headline g-outer-spacing-top-medium g-outer-spacing-bottom-medium"
            date_time_class = ["c-globalAuthor_time"]
            para_div_class = ["c-ShortcodeContent"]

            links=[]
            try:
                page = requests.get(url, headers=headers)
                soup = BeautifulSoup(page.content, "html.parser")
            except:
                print("zdnet not working")
                not_working_functions.append('zdnet')
                err = "Main link did not load: " + url
                Errors["zdnet"].append(err)
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
                    print("zdnet not working")
                    not_working_functions.append('zdnet')
                    Errors["zdnet"].append("Extraction of link not working.")
                    return
                        
            # Remove duplicates
            links = list(set(links))
            
            # links # Debugging - if link array is generated
            collection = []
            scrapper_name = "zdnet"
            
            def getarticles(link):
                flag=0
                err=err_dict()
                try:
                    l_page = requests.get(link, headers=headers)
                    l_soup = BeautifulSoup(l_page.content, 'html.parser')
                except:
                    err["link"]="Link not working: "+link
                    Errors["zdnet"].append(err)
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
                    date_text = date_ele.text
                    l=date_text.split(" ")
                    date_text=l[1].strip(",")+" "+l[0].strip(".")+" "+l[2]
                    
                    
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
                    Errors["zdnet"].append(err)
                
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
            emptydataframe("zdnet", df)
            # df  = link_correction(df)
            return df
        
        except:
            not_working_functions.append("zdnet")
            print("zdnet not working")


    def manilatimes(keyword):
        try:
            print("manilatimes")
            Errors["manilatimes"]=[]
            
            
            
            url = f"https://www.manilatimes.net/search?query={keyword}"
            domain_url = "https://www.manilatimes.net/"
            headers = {
                "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10.15; rv:78.0) Gecko/20100101 Firefox/78.0",
                "accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.9",
                'sec-fetch-site': 'none',
                'sec-fetch-mode': 'navigate',
                'sec-fetch-user': '?1',
                'sec-fetch-dest': 'document',
                'accept-language': 'en-GB,en-US;q=0.9,en;q=0.8',
            }
            div_class = "col-content-1"  # Class name of div containing the a tag
            #h1_class = "_1Y-96"
            #h1_div_class = "col-xs-12"
            title_h1_class = "article-title font-700 roboto-slab-3 tdb-title-text"
            date_div_class = ["article-publish-time roboto-a"]
            para_div_class = ["article-body tdb-block-inner"]

            links=[]
            try:
                page = requests.get(url, headers=headers)
                soup = BeautifulSoup(page.content, "html.parser")
            except:
                print("manilatimes not working")
                not_working_functions.append('manilatimes')
                err = "Main link did not load: " + url
                Errors["manilatimes"].append(err)
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
                    print("manilatimes not working")
                    not_working_functions.append('manilatimes')
                    Errors["manilatimes"].append("Extraction of link not working.")
                    return
                        
            # Remove duplicates
            links = list(set(links))
            
            # links # Debugging - if link array is generated
            collection = []
            scrapper_name = "manilatimes"
            
            def getarticles(link):
                flag=0
                err=err_dict()
                try:
                    l_page = requests.get(link, headers=headers)
                    l_soup = BeautifulSoup(l_page.content, 'html.parser')
                except:
                    err["link"]="Link not working: "+link
                    Errors["manilatimes"].append(err)
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
                    
                    date_text=link[36:38]+"-"+link[33:35]+"-"+link[28:32]

                    
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
                    Errors["manilatimes"].append(err)
                
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
            emptydataframe("manilatimes", df)
            # df  = link_correction(df)
            return df
        
        except:
            not_working_functions.append("manilatimes")
            print("manilatimes not working")


    def investmentweek(keyword):
        try:
            print("investmentweek")
            Errors["investmentweek"]=[]
            
            
            
            url = f"https://www.investmentweek.co.uk/search?query={keyword}&per_page=24&sort=relevance1&date=this_year"
            domain_url = "https://www.investmentweek.co.uk/"
            headers = {
                "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10.15; rv:78.0) Gecko/20100101 Firefox/78.0",
                "accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.9",
                'sec-fetch-site': 'none',
                'sec-fetch-mode': 'navigate',
                'sec-fetch-user': '?1',
                'sec-fetch-dest': 'document',
                'accept-language': 'en-GB,en-US;q=0.9,en;q=0.8',
            }
            div_class = "card-body"  # Class name of div containing the a tag
            #h1_class = "_1Y-96"
            #h1_div_class = "col-xs-12"
            title_h1_itemprop = "name"
            date_span_itemprop = ["datePublished"]
            para_div_class = ["linear-gradient"]
            links=[]
            try:
                page = requests.get(url, headers=headers)
                soup = BeautifulSoup(page.content, "html.parser")
            except:
                print("investmentweek not working")
                not_working_functions.append('investmentweek')
                err = "Main link did not load: " + url
                Errors["investmentweek"].append(err)
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
                    print("investmentweek not working")
                    not_working_functions.append('investmentweek')
                    Errors["investmentweek"].append("Extraction of link not working.")
                    return
                        
            # Remove duplicates
            links = list(set(links))
            
            # links # Debugging - if link array is generated
            collection = []
            scrapper_name = "investmentweek"
            
            def getarticles(link):
                flag=0
                err=err_dict()
                try:
                    l_page = requests.get(link, headers=headers)
                    l_soup = BeautifulSoup(l_page.content, 'html.parser')
                except:
                    err["link"]="Link not working: "+link
                    Errors["investmentweek"].append(err)
                    return
                
                data = []
                
                # Scraping the heading
                #h1_ele = l_soup.find("h1", {"class": h1_class})
                
                try:
                    title_ele = l_soup.find( "h1", {"itemprop": title_h1_itemprop})
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
                    date_ele = l_soup.find("span", {"itemprop": date_span_itemprop})
                    date_text = date_ele.text
                    l=date_text.split("\n")[1]
                    l=l.split(" ")
                    date_text=l[0]+" "+l[1]+" "+l[2]
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
                    Errors["investmentweek"].append(err)
                
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
            emptydataframe("investmentweek", df)
            # df  = link_correction(df)
            return df
        
        except:
            not_working_functions.append("investmentweek")
            print("investmentweek not working")

    def sundayobserver(keyword):
        try:
            print("sundayobserver")
            Errors["sundayobserver"]=[]
            
            
            
            url = f"https://www.sundayobserver.lk/search/node/{keyword}"
            domain_url = "https://www.sundayobserver.lk/"
            headers = {
                "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10.15; rv:78.0) Gecko/20100101 Firefox/78.0",
                "accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.9",
                'sec-fetch-site': 'none',
                'sec-fetch-mode': 'navigate',
                'sec-fetch-user': '?1',
                'sec-fetch-dest': 'document',
                'accept-language': 'en-GB,en-US;q=0.9,en;q=0.8',
            }
            li_class = "search-result"  # Class name of div containing the a tag
            #h1_class = "_1Y-96"
            #h1_div_class = "col-xs-12"
            title_h1_class = "title"
            date_span_class = ["date-display-single"]
            para_div_class = ["field-item even"]
            links=[]
            try:
                page = requests.get(url, headers=headers)
                soup = BeautifulSoup(page.content, "html.parser")
            except:
                print("sundayobserver not working")
                not_working_functions.append('sundayobserver')
                err = "Main link did not load: " + url
                Errors["sundayobserver"].append(err)
                return
            
            
            try:
                
                for h2_tag in soup.find_all("li", {"class": li_class}):
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
                    print("sundayobserver not working")
                    not_working_functions.append('sundayobserver')
                    Errors["sundayobserver"].append("Extraction of link not working.")
                    return
                        
            # Remove duplicates
            links = list(set(links))
            
            # links # Debugging - if link array is generated
            collection = []
            scrapper_name = "sundayobserver"
            
            def getarticles(link):
                flag=0
                err=err_dict()
                try:
                    l_page = requests.get(link, headers=headers)
                    l_soup = BeautifulSoup(l_page.content, 'html.parser')
                except:
                    err["link"]="Link not working: "+link
                    Errors["sundayobserver"].append(err)
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
                    date_text=link[38:40]+"-"+link[35:37]+"-"+link[30:34]
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
                    Errors["sundayobserver"].append(err)
                
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
            emptydataframe("sundayobserver", df)
            # df  = link_correction(df)
            return df
        
        except:
            not_working_functions.append("sundayobserver")
            print("sundayobserver not working")

    def reinsurancene(keyword):
        try:
            print("reinsurancene")
            Errors["reinsurancene"]=[]
            
            
            
            url = f"https://www.reinsurancene.ws/?s={keyword}"
            domain_url = "https://www.reinsurancene.ws/"

            headers = {
                "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10.15; rv:78.0) Gecko/20100101 Firefox/78.0",
                "accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.9",
                'sec-fetch-site': 'none',
                'sec-fetch-mode': 'navigate',
                'sec-fetch-user': '?1',
                'sec-fetch-dest': 'document',
                'accept-language': 'en-GB,en-US;q=0.9,en;q=0.8',
            }
            div_class="home-post"# Class name of div containing the a tag
            #h1_class = "_1Y-96"
            #h1_div_class = "col-xs-12"
            date_p_class= ["date"]
            para_div_class=["pf-content"]
            links=[]
            try:
                page = requests.get(url, headers=headers)
                soup = BeautifulSoup(page.content, "html.parser")
            except:
                print("reinsurancene not working")
                not_working_functions.append('reinsurancene')
                err = "Main link did not load: " + url
                Errors["reinsurancene"].append(err)
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
                    print("reinsurancene not working")
                    not_working_functions.append('reinsurancene')
                    Errors["reinsurancene"].append("Extraction of link not working.")
                    return
                        
            # Remove duplicates
            links = list(set(links))
            
            # links # Debugging - if link array is generated
            collection = []
            scrapper_name = "reinsurancene"
            
            def getarticles(link):
                flag=0
                err=err_dict()
                try:
                    l_page = requests.get(link, headers=headers)
                    l_soup = BeautifulSoup(l_page.content, 'html.parser')
                except:
                    err["link"]="Link not working: "+link
                    Errors["reinsurancene"].append(err)
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
                    date_ele = l_soup.find("p",{"class":date_p_class})
                    date_text = date_ele.text
                    l=date_text.split(" ")
                    date_text=l[1][0:2].strip("t").strip("s").strip("n")+"-"+l[2]+"-"+l[3]
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
                    Errors["reinsurancene"].append(err)
                
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
            emptydataframe("reinsurancene", df)
            # df  = link_correction(df)
            return df
        
        except:
            not_working_functions.append("reinsurancene")
            print("reinsurancene not working")

    def insideretail(keyword):
        try:
            print("insideretail")
            Errors["insideretail"]=[]
            
            
            
            url = f"https://insideretail.com.au/?s={keyword}"
            domain_url = "https://insideretail.com.au/"
            headers = {
                "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10.15; rv:78.0) Gecko/20100101 Firefox/78.0",
                "accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.9",
                'sec-fetch-site': 'none',
                'sec-fetch-mode': 'navigate',
                'sec-fetch-user': '?1',
                'sec-fetch-dest': 'document',
                'accept-language': 'en-GB,en-US;q=0.9,en;q=0.8',
            }
            div_class="content-wrap"# Class name of div containing the a tag
            #h1_class = "_1Y-96"
            #h1_div_class = "col-xs-12"
            
            date_span_class= ["date"]
            para_div_class=["has-content-area"]
            links=[]
            try:
                page = requests.get(url, headers=headers)
                soup = BeautifulSoup(page.content, "html.parser")
            except:
                print("insideretail not working")
                not_working_functions.append('insideretail')
                err = "Main link did not load: " + url
                Errors["insideretail"].append(err)
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
                    print("insideretail not working")
                    not_working_functions.append('insideretail')
                    Errors["insideretail"].append("Extraction of link not working.")
                    return
                        
            # Remove duplicates
            links = list(set(links))
            
            # links # Debugging - if link array is generated
            collection = []
            scrapper_name = "insideretail"
            
            def getarticles(link):
                flag=0
                err=err_dict()
                try:
                    l_page = requests.get(link, headers=headers)
                    l_soup = BeautifulSoup(l_page.content, 'html.parser')
                except:
                    err["link"]="Link not working: "+link
                    Errors["insideretail"].append(err)
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
                    date_ele = l_soup.find("span", {"class": date_span_class})
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
                    Errors["insideretail"].append(err)
                
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
            emptydataframe("insideretail", df)
            # df  = link_correction(df)
            return df
        
        except:
            not_working_functions.append("insideretail")
            print("insideretail not working")
    
    
    
    def EconomicTimes():
        try:
            print("EconomicTimes")
            Errors["EconomicTimes"]=[]
            
            url = "https://economictimes.indiatimes.com/markets/markets/ipos/fpos/news"
            domain_url = "https://economictimes.indiatimes.com/"
            title, links, text, pub_date, scraped_date = [], [], [], [], []
            
            try:
                page = requests.get(url)
                soup = BeautifulSoup(page.content, "html.parser")


            except:
                print("EconomicTimes not working")
                not_working_functions.append('EconomicTimes')
                err = "Main link did not load: " + url
                Errors["EconomicTimes"].append(err)
                return
            
            today = date.today()
            
            err=err_dict()
            
            print(len(soup.find_all('div', {'class': 'eachStory'})))
            
            try:
                for a in soup.find_all('div', {'class': 'eachStory'}):
                    try:
                        link=domain_url+str(a.h3.a.get("href"))
                        links.append(link)
                        try:
                            published=a.time.text
                            if "ago" in published:
                                pub_date.append(date.today())
                            else:
                                pub_date.append(published)
                        except:
                            err["link"]=link
                            err['published_date']="Error"
                            pub_date.append("-")
                            flag=1
                        
                        try:
                            title.append(a.h3.text)
                        except:
                            err["link"]=link
                            err["title"]="Error"
                            title.append("-")
                            flag=1
                        
                        try:
                            text.append(a.p.text)
                        except:
                            err["link"]=link
                            err["title"]="Error"
                            text.append("-")
                            flag=1

                        scraped_date.append(str(today))
                        
                        if flag==1:
                            Errors["EconomicTimes"].append(err)
                    except:
                        continue 
            except:
                if len(links)==0:
                    print("EconomicTimes not working")
                    not_working_functions.append('EconomicTimes')
                    Errors["EconomicTimes"].append("Extraction of link not working.")
                    return
                    
            
            
            
            df = pd.DataFrame({"text": text, "link": links,
                              "publish_date": pub_date, "scraped_date": scraped_date, "title": title})
            
            df = df.drop_duplicates(subset=["link"])
            df = FilterFunction(df)
            emptydataframe("EconomicTimes", df)
            
            return df
        except:
            print("EconomicTimes not working")
            not_working_functions.append('EconomicTimes')

    def seenews(keyword):
        try:
            print("seenews")
            Errors["seenews"]=[]
            
            
            
            url = f"https://seenews.com/search-results/?keywords={keyword}&order_by=name&order=asc&optradio=on&company_id=&company_owner=&capital_from=&capital_to=&total_assets_from=&total_assets_to=&total_revenue_from=&total_revenue_to=&number_of_employees_from=&number_of_employees_to=&net_profit_from=&net_profit_to=&net_loss_from=&net_loss_to=&seeci_from=&seeci_to=&ebitda_from=&ebitda_to=&year=&statement_type="
            domain_url = "https://seenews.com/"
            headers = {
                "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10.15; rv:78.0) Gecko/20100101 Firefox/78.0",
                "accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.9",
                'sec-fetch-site': 'none',
                'sec-fetch-mode': 'navigate',
                'sec-fetch-user': '?1',
                'sec-fetch-dest': 'document',
                'accept-language': 'en-GB,en-US;q=0.9,en;q=0.8',
            }
            div_class="block--content block--content_titlemeta"# Class name of div containing the a tag
            #h1_class = "_1Y-96"
            #h1_div_class = "col-xs-12"
            title_div_class= "heading--content f-java"
            date_div_class= ["post-date"]
            para_div_class=["content-description"]
            links=[]
            try:
                page = requests.get(url, headers=headers)
                soup = BeautifulSoup(page.content, "html.parser")
            except:
                print("seenews not working")
                not_working_functions.append('seenews')
                err = "Main link did not load: " + url
                Errors["seenews"].append(err)
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
                    print("seenews not working")
                    not_working_functions.append('seenews')
                    Errors["seenews"].append("Extraction of link not working.")
                    return
                        
            # Remove duplicates
            links = list(set(links))
            
            # links # Debugging - if link array is generated
            collection = []
            scrapper_name = "seenews"
            
            def getarticles(link):
                flag=0
                err=err_dict()
                try:
                    l_page = requests.get(link, headers=headers)
                    l_soup = BeautifulSoup(l_page.content, 'html.parser')
                except:
                    err["link"]="Link not working: "+link
                    Errors["seenews"].append(err)
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
                    l=date_text.split("\n")
                    l1=l[2].split(" ")
                    date_text=l1[1].strip(",")+"-"+l1[0]+"-"+l1[2]
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
                    Errors["seenews"].append(err)
                
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
            emptydataframe("seenews", df)
            # df  = link_correction(df)
            return df
        
        except:
            not_working_functions.append("seenews")
            print("seenews not working")


    def shorttermrentalz(keyword):
        try:
            print("shorttermrentalz")
            Errors["shorttermrentalz"]=[]
            
            
            
            url = f"https://shorttermrentalz.com/?s={keyword}"
            domain_url = "https://shorttermrentalz.com/"
            headers = {
                "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10.15; rv:78.0) Gecko/20100101 Firefox/78.0",
                "accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.9",
                'sec-fetch-site': 'none',
                'sec-fetch-mode': 'navigate',
                'sec-fetch-user': '?1',
                'sec-fetch-dest': 'document',
                'accept-language': 'en-GB,en-US;q=0.9,en;q=0.8',
            }
            div_class="article-content clearfix"# Class name of div containing the a tag
            #h1_class = "_1Y-96"
            #h1_div_class = "col-xs-12"
            title_header_class= "entry-header"
            date_time_class= ["entry-date published"]
            para_div_class=["entry-content clearfix"]
            links=[]
            try:
                page = requests.get(url, headers=headers)
                soup = BeautifulSoup(page.content, "html.parser")
            except:
                print("shorttermrentalz not working")
                not_working_functions.append('shorttermrentalz')
                err = "Main link did not load: " + url
                Errors["shorttermrentalz"].append(err)
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
                    print("shorttermrentalz not working")
                    not_working_functions.append('shorttermrentalz')
                    Errors["shorttermrentalz"].append("Extraction of link not working.")
                    return
                        
            # Remove duplicates
            links = list(set(links))
            
            # links # Debugging - if link array is generated
            collection = []
            scrapper_name = "shorttermrentalz"
            
            def getarticles(link):
                flag=0
                err=err_dict()
                try:
                    l_page = requests.get(link, headers=headers)
                    l_soup = BeautifulSoup(l_page.content, 'html.parser')
                except:
                    err["link"]="Link not working: "+link
                    Errors["shorttermrentalz"].append(err)
                    return
                
                data = []
                
                # Scraping the heading
                #h1_ele = l_soup.find("h1", {"class": h1_class})
                
                try:
                    title_ele = l_soup.find("header",{"class":title_header_class})
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
                    date_text = date_ele.text
                    l1=date_text.split(" ")
                    l1[0]=l1[0].strip("st")
                    l1[0]=l1[0].strip("th")
                    l1[0]=l1[0].strip("nd")
                    l1[0]=l1[0].strip("rd")
                    date_text=l1[0]+"-"+l1[1]+"-"+l1[2]
                    
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
                    Errors["shorttermrentalz"].append(err)
                
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
            emptydataframe("shorttermrentalz", df)
            # df  = link_correction(df)
            return df
        
        except:
            not_working_functions.append("shorttermrentalz")
            print("shorttermrentalz not working")

    def arabnews(keyword):
        try:
            print("arabnews")
            Errors["arabnews"]=[]
            
            
            
            url = f"https://www.arabnews.com/search/site/{keyword}"
            domain_url = "https://www.arabnews.com/"
            headers = {
                "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10.15; rv:78.0) Gecko/20100101 Firefox/78.0",
                "accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.9",
                'sec-fetch-site': 'none',
                'sec-fetch-mode': 'navigate',
                'sec-fetch-user': '?1',
                'sec-fetch-dest': 'document',
                'accept-language': 'en-GB,en-US;q=0.9,en;q=0.8',
            }
            div_class="article-item"# Class name of div containing the a tag
            #h1_class = "_1Y-96"
            #h1_div_class = "col-xs-12"
            
            date_div_class= ["updated-ago"]
            para_div_class=["field-item even"]
            links=[]
            try:
                page = requests.get(url, headers=headers)
                soup = BeautifulSoup(page.content, "html.parser")
            except:
                print("arabnews not working")
                not_working_functions.append('arabnews')
                err = "Main link did not load: " + url
                Errors["arabnews"].append(err)
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
                    print("arabnews not working")
                    not_working_functions.append('arabnews')
                    Errors["arabnews"].append("Extraction of link not working.")
                    return
                        
            # Remove duplicates
            links = list(set(links))
            
            # links # Debugging - if link array is generated
            collection = []
            scrapper_name = "arabnews"
            
            def getarticles(link):
                flag=0
                err=err_dict()
                try:
                    l_page = requests.get(link, headers=headers)
                    l_soup = BeautifulSoup(l_page.content, 'html.parser')
                except:
                    err["link"]="Link not working: "+link
                    Errors["arabnews"].append(err)
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
                    date_ele = l_soup.find("div",{"class": date_div_class})
                    date_text = date_ele.text
                    l=date_text.split("\n")
                    l1=l[1].split(" ")
                    date_text=l1[1]+"-"+l1[2]+"-"+l1[3]
                    
                    
                    
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
                    Errors["arabnews"].append(err)
                
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
            emptydataframe("arabnews", df)
            # df  = link_correction(df)
            return df
        
        except:
            not_working_functions.append("arabnews")
            print("arabnews not working")


    def macaubusiness(keyword):
        try:
            print("macaubusiness")
            Errors["macaubusiness"]=[]
            
            url = f"https://www.macaubusiness.com/?s={keyword}"
            domain_url = "https://www.macaubusiness.com/"
            headers = {
                "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10.15; rv:78.0) Gecko/20100101 Firefox/78.0",
                "accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.9",
                'sec-fetch-site': 'none',
                'sec-fetch-mode': 'navigate',
                'sec-fetch-user': '?1',
                'sec-fetch-dest': 'document',
                'accept-language': 'en-GB,en-US;q=0.9,en;q=0.8',
            }
            div_class="td-block-row"
            date_time_class= ["entry-date updated td-module-date"]
            para_div_class=["td-post-content"]

            links=[]
            try:
                page = requests.get(url, headers=headers)
                soup = BeautifulSoup(page.content, "html.parser")
            except:
                print("macaubusiness not working")
                not_working_functions.append('macaubusiness')
                err = "Main link did not load: " + url
                Errors["macaubusiness"].append(err)
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
                    print("macaubusiness not working")
                    not_working_functions.append('macaubusiness')
                    Errors["macaubusiness"].append("Extraction of link not working.")
                    return
                        
            # Remove duplicates
            links = list(set(links))
            
            # links # Debugging - if link array is generated
            collection = []
            scrapper_name = "macaubusiness"
            
            def getarticles(link):
                flag=0
                err=err_dict()
                try:
                    l_page = requests.get(link, headers=headers)
                    l_soup = BeautifulSoup(l_page.content, 'html.parser')
                except:
                    err["link"]="Link not working: "+link
                    Errors["macaubusiness"].append(err)
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
                    date_ele = l_soup.find("time",{"class": date_time_class})
                    date_text = date_ele.text
                    l=date_text.split(" ")
                    date_text=l[1].strip(",")+"-"+l[0]+"-"+l[2]
                    
                    
                    
                    
                    
                    
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
                    Errors["macaubusiness"].append(err)
                
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
            emptydataframe("macaubusiness", df)
            # df  = link_correction(df)
            return df
        
        except:
            not_working_functions.append("macaubusiness")
            print("macaubusiness not working")

    def vietnamnet(keyword):
        try:
            print("vietnamnet")
            Errors["vietnamnet"]=[]
            
            
            
            url = f"https://vietnamnet.vn/en/tim-kiem?q={keyword}"
            domain_url = "https://vietnamnet.vn/en/"
            headers = {
                "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10.15; rv:78.0) Gecko/20100101 Firefox/78.0",
                "accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.9",
                'sec-fetch-site': 'none',
                'sec-fetch-mode': 'navigate',
                'sec-fetch-user': '?1',
                'sec-fetch-dest': 'document',
                'accept-language': 'en-GB,en-US;q=0.9,en;q=0.8',
            }
            div_class="mt-30 mb-20 main-result"
            title_h1_class= "newsFeature__header-title mt-20"
            date_span_class= ["breadcrumb-box__time"]
            para_div_class=["page"]
            links=[]
            try:
                page = requests.get(url, headers=headers)
                soup = BeautifulSoup(page.content, "html.parser")
            except:
                print("vietnamnet not working")
                not_working_functions.append('vietnamnet')
                err = "Main link did not load: " + url
                Errors["vietnamnet"].append(err)
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
                    print("vietnamnet not working")
                    not_working_functions.append('vietnamnet')
                    Errors["vietnamnet"].append("Extraction of link not working.")
                    return
                        
            # Remove duplicates
            links = list(set(links))
            
            # links # Debugging - if link array is generated
            collection = []
            scrapper_name = "vietnamnet"
            
            def getarticles(link):
                flag=0
                err=err_dict()
                try:
                    l_page = requests.get(link, headers=headers)
                    l_soup = BeautifulSoup(l_page.content, 'html.parser')
                except:
                    err["link"]="Link not working: "+link
                    Errors["vietnamnet"].append(err)
                    return
                
                data = []
                
                # Scraping the heading
                #h1_ele = l_soup.find("h1", {"class": h1_class})
                
                try:
                    title_ele = l_soup.find("h1",{"class":title_h1_class})
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
                    date_ele = l_soup.find("span",{"class": date_span_class})
                    date_text = date_ele.text
                    l1=date_text.split("\n")
                    l=l1[1].strip(" ")
                    l2=l.split(" ")
                    date_text=l2[0]
                    
                    
                    
                    
                    
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
                    Errors["vietnamnet"].append(err)
                
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
            emptydataframe("vietnamnet", df)
            # df  = link_correction(df)
            return df
        
        except:
            not_working_functions.append("vietnamnet")
            print("vietnamnet not working")

    def thesydneymorningherald(keyword):
        try:
            print("thesydneymorningherald")
            Errors["thesydneymorningherald"]=[]
            
            url = f"https://www.smh.com.au/search?text={keyword}"
            domain_url = "https://www.smh.com.au/"
            headers = {
                "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10.15; rv:78.0) Gecko/20100101 Firefox/78.0",
                "accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.9",
                'sec-fetch-site': 'none',
                'sec-fetch-mode': 'navigate',
                'sec-fetch-user': '?1',
                'sec-fetch-dest': 'document',
                'accept-language': 'en-GB,en-US;q=0.9,en;q=0.8',
            }
            div_class="_2g9tm"# Class name of div containing the a tag
            #h1_class = "_1Y-96"
            #h1_div_class = "col-xs-12"
            title_h1_class= "title"
            date_time_class= ["_2_zR-"]
            para_div_class=["_1665V _2q-Vk"]

            links=[]
            try:
                page = requests.get(url, headers=headers)
                soup = BeautifulSoup(page.content, "html.parser")
            except:
                print("thesydneymorningherald not working")
                not_working_functions.append('thesydneymorningherald')
                err = "Main link did not load: " + url
                Errors["thesydneymorningherald"].append(err)
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
                    print("thesydneymorningherald not working")
                    not_working_functions.append('thesydneymorningherald')
                    Errors["thesydneymorningherald"].append("Extraction of link not working.")
                    return
                        
            # Remove duplicates
            links = list(set(links))
            
            # links # Debugging - if link array is generated
            collection = []
            scrapper_name = "thesydneymorningherald"
            
            def getarticles(link):
                flag=0
                err=err_dict()
                try:
                    l_page = requests.get(link, headers=headers)
                    l_soup = BeautifulSoup(l_page.content, 'html.parser')
                except:
                    err["link"]="Link not working: "+link
                    Errors["thesydneymorningherald"].append(err)
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
                    date_ele = l_soup.find("time",{"class": date_time_class})
                    date_text = date_ele.text
                    l=date_text.split(" ")
                    date_text=l[1].strip(",")+"-"+l[0]+"-"+l[2]
                    
                    
                    
                    
                    
                    
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
                    Errors["thesydneymorningherald"].append(err)
                
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
            emptydataframe("thesydneymorningherald", df)
            # df  = link_correction(df)
            return df
        
        except:
            not_working_functions.append("thesydneymorningherald")
            print("thesydneymorningherald not working")


    def economictimes(keyword):
        try:
            print("economictimes")
            Errors["economictimes"]=[]
            
            url = f"https://economictimes.indiatimes.com/definition/{keyword}"
            domain_url = "https://economictimes.indiatimes.com/"
            headers = {
                "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10.15; rv:78.0) Gecko/20100101 Firefox/78.0",
                "accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.9",
                'sec-fetch-site': 'none',
                'sec-fetch-mode': 'navigate',
                'sec-fetch-user': '?1',
                'sec-fetch-dest': 'document',
                'accept-language': 'en-GB,en-US;q=0.9,en;q=0.8',
            }
            li_class="definitionStories"# Class name of div containing the a tag
            #h1_class = "_1Y-96"
            #h1_div_class = "col-xs-12"
            title_h1_class= "artTitle font_faus"
            date_time_class= ["jsdtTime"]
            para_article_class=["artData clr paywall"]

            links=[]
            try:
                page = requests.get(url, headers=headers)
                soup = BeautifulSoup(page.content, "html.parser")
            except:
                print("economictimes not working")
                not_working_functions.append('economictimes')
                err = "Main link did not load: " + url
                Errors["economictimes"].append(err)
                return
            
            
            try:
                
                for h2_tag in soup.find_all("li", {"class": li_class}):
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
                    print("economictimes not working")
                    not_working_functions.append('economictimes')
                    Errors["economictimes"].append("Extraction of link not working.")
                    return
                        
            # Remove duplicates
            links = list(set(links))
            
            # links # Debugging - if link array is generated
            collection = []
            scrapper_name = "economictimes"
            
            def getarticles(link):
                flag=0
                err=err_dict()
                try:
                    l_page = requests.get(link, headers=headers)
                    l_soup = BeautifulSoup(l_page.content, 'html.parser')
                except:
                    err["link"]="Link not working: "+link
                    Errors["economictimes"].append(err)
                    return
                
                data = []
                
                # Scraping the heading
                #h1_ele = l_soup.find("h1", {"class": h1_class})
                
                try:
                    title_ele = l_soup.find("h1",{"class":title_h1_class})
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
                    date_ele = l_soup.find("time",{"class": date_time_class})
                    date_text = date_ele.text
                    l=date_text.split(" ")
                    date_text=l[3].strip(",")+"-"+l[2]+"-"+l[4].strip(",")
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
                    para_ele = (l_soup.findAll("article", {"class": para_article_class}))[-1]
                    data.append(para_ele.text)  # Need to make this better
                except:
                    err["link"]=link
                    err['text']="Error"
                    data.append("-")
                    flag=1
                  # drops the complete data if there is an error
                # Adding data to a collection
                
                if flag==1:
                    Errors["economictimes"].append(err)
                
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
            emptydataframe("economictimes", df)
            # df  = link_correction(df)
            return df
        
        except:
            not_working_functions.append("economictimes")
            print("economictimes not working")

    def nzherald(keyword):
        try:
            print("nzherald")
            Errors["nzherald"]=[]
            
            url = f"https://www.nzherald.co.nz/search/{keyword}/"
            domain_url = "https://www.nzherald.co.nz/"
            headers = {
                "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10.15; rv:78.0) Gecko/20100101 Firefox/78.0",
                "accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.9",
                'sec-fetch-site': 'none',
                'sec-fetch-mode': 'navigate',
                'sec-fetch-user': '?1',
                'sec-fetch-dest': 'document',
                'accept-language': 'en-GB,en-US;q=0.9,en;q=0.8',
            }
            article_class="story-card story-card--summary"# Class name of div containing the a tag
            #h1_class = "_1Y-96"
            #h1_div_class = "col-xs-12"
            title_h1_class= "article__heading"
            date_time_class= ["meta-data__time-stamp"]
            para_section_class=["article__body full-content article__content"] 

            links=[]
            try:
                page = requests.get(url, headers=headers)
                soup = BeautifulSoup(page.content, "html.parser")
            except:
                print("nzherald not working")
                not_working_functions.append('nzherald')
                err = "Main link did not load: " + url
                Errors["nzherald"].append(err)
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
                    print("nzherald not working")
                    not_working_functions.append('nzherald')
                    Errors["nzherald"].append("Extraction of link not working.")
                    return
                        
            # Remove duplicates
            links = list(set(links))
            
            # links # Debugging - if link array is generated
            collection = []
            scrapper_name = "nzherald"
            
            def getarticles(link):
                flag=0
                err=err_dict()
                try:
                    l_page = requests.get(link, headers=headers)
                    l_soup = BeautifulSoup(l_page.content, 'html.parser')
                except:
                    err["link"]="Link not working: "+link
                    Errors["nzherald"].append(err)
                    return
                
                data = []
                
                # Scraping the heading
                #h1_ele = l_soup.find("h1", {"class": h1_class})
                
                try:
                    title_ele = l_soup.find("h1",{"class":title_h1_class})
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
                    date_ele = l_soup.find("time",{"class": date_time_class})
                    date_text = date_ele.text
                    l=date_text.split(" ")
                    date_text=l[0]+"-"+l[1].strip(",")+"-"+l[2]
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
                    para_ele = (l_soup.findAll("section", {"class": para_section_class}))[-1]
                    data.append(para_ele.text)  # Need to make this better
                except:
                    err["link"]=link
                    err['text']="Error"
                    data.append("-")
                    flag=1
                  # drops the complete data if there is an error
                # Adding data to a collection
                
                if flag==1:
                    Errors["nzherald"].append(err)
                
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
            emptydataframe("nzherald", df)
            # df  = link_correction(df)
            return df
        
        except:
            not_working_functions.append("nzherald")
            print("nzherald not working")
    
    def albaniandailynews(keyword):
        try:
            print("albaniandailynews")
            Errors["albaniandailynews"]=[]
            
            url = f"https://www.albaniandailynews.com/search.php?s={keyword}"
            domain_url = "https://albaniandailynews.com/"
            headers = {
                "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10.15; rv:78.0) Gecko/20100101 Firefox/78.0",
                "accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.9",
                'sec-fetch-site': 'none',
                'sec-fetch-mode': 'navigate',
                'sec-fetch-user': '?1',
                'sec-fetch-dest': 'document',
                'accept-language': 'en-GB,en-US;q=0.9,en;q=0.8',
            }
            h3_class = "alith_post_title"  # Class name of h3 containing the a tag
            #h1_class = "_1Y-96"
            #h1_div_class = "col-xs-12"
            title_h3_class= "alith_post_title"
            date_span_class = "meta_date"
            para_div_class = "column-1"

            links=[]
            try:
                page = requests.get(url, headers=headers)
                soup = BeautifulSoup(page.content, "html.parser")
            except:
                print("albaniandailynews not working")
                not_working_functions.append('albaniandailynews')
                err = "Main link did not load: " + url
                Errors["albaniandailynews"].append(err)
                return
            
            
            try:
                
                for h2_tag in soup.find_all("h3", {"class": h3_class}):
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
                    print("albaniandailynews not working")
                    not_working_functions.append('albaniandailynews')
                    Errors["albaniandailynews"].append("Extraction of link not working.")
                    return
                        
            # Remove duplicates
            links = list(set(links))
            
            # links # Debugging - if link array is generated
            collection = []
            scrapper_name = "albaniandailynews"
            
            def getarticles(link):
                flag=0
                err=err_dict()
                try:
                    l_page = requests.get(link, headers=headers)
                    l_soup = BeautifulSoup(l_page.content, 'html.parser')
                except:
                    err["link"]="Link not working: "+link
                    Errors["albaniandailynews"].append(err)
                    return
                
                data = []
                
                # Scraping the heading
                #h1_ele = l_soup.find("h1", {"class": h1_class})
                
                try:
                    title_ele = l_soup.find("h3",{"class":title_h3_class})
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
                    date_ele = l_soup.find("span",{"class": date_span_class})
                    date_text = date_ele.text
                    l=date_text.split(" ")
                    date_text=l[2].strip(",")+"-"+l[1]+"-"+l[3]
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
                    Errors["albaniandailynews"].append(err)
                
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
            emptydataframe("albaniandailynews", df)
            # df  = link_correction(df)
            return df
        
        except:
            not_working_functions.append("albaniandailynews")
            print("albaniandailynews not working")
    
    
    def stock_eastmoney():
        try:
            print("stock_eastmoney")
            Errors["stock_eastmoney"]=[]
            
            url = "http://stock.eastmoney.com/a/cxgyw.html"
            
            title, links, text, pub_date, scraped_date = [], [], [], [], []
            
            try:
                options = webdriver.ChromeOptions() 
                options.headless = True
                options.add_argument('--no-sandbox')
                options.add_argument('--disable-dev-shm-usage')
                options.add_experimental_option('excludeSwitches', ['enable-logging']) 
                service = ChromeService(executable_path=ChromeDriverManager().install())
                driver = webdriver.Chrome(service=service, options=options)
                driver.get(url)
                soup = BeautifulSoup(driver.page_source, features="html.parser")
                driver.close()
                driver.quit()
            except:
                print("stock_eastmoney not working")
                not_working_functions.append('stock_eastmoney')
                err = "Main link did not load: " + url
                Errors["stock_eastmoney"].append(err)
                return
            
            links=[]
            
            try:
                for i in soup.find("ul", id="newsListContent").find_all("li"):
                    links.append(i.find("div", class_="text").find("p", class_="title").a.get("href"))
                
            except Exception as e:
                if len(links)==0:
                    print("stock_eastmoney not working")
                    not_working_functions.append('stock_eastmoney')
                    Errors["stock_eastmoney"].append("Extraction of link not working.")
                    return
                
            final_links=[]
            today = date.today()
            
            def getartciles(link):
                    flag=0
                    err=err_dict()
                    try:
                        page = requests.get(link)
                        soup = BeautifulSoup(page.content, "html.parser")
                        soup = soup.find("div", class_="contentwrap")
                    except:
                        err["link"]="Link not working: "+link
                        Errors["stock_eastmoney"].append(err)
                        return
                    
                    try:
                        published=soup.find("div", class_="infos").div.text
                        match = re.search(r"\d{4}.*\d{2}.*\d{2}", published)
                        date = match.group()

                        year = re.search(r"\d{4}", date).group()
                        month = re.search(r"\d{2}", date[5:]).group()
                        day = re.search(r"\d{2}", date[8:]).group()

                        published = day + "/" + month + "/" + year
                        
                    except:
                        err["link"]=link
                        err['published_date']="Error"
                        published = "-"
                        flag=1
                    
                    try:
                        ti=translate(soup.find("div", class_="title").text)
                        
                    except:
                        err["link"]=link
                        err["title"]="Error"
                        ti="-"
                        flag=1
                    
                    try:
                        para=""
                        for i in soup.find("div", id="ContentBody").find_all("p"):
                            para+=" "+str(i.text)
                        para=translate(para)
                        
                    except:
                        err["link"]=link
                        err["title"]="Error"
                        para="-"
                        flag=1

                    scraped_date.append(str(today))
                    
                    if flag==1:
                        Errors["stock_eastmoney"].append(err)
                    
                    text.append(para)    
                    title.append(ti)
                    final_links.append(link)
                    pub_date.append(published)
            
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
            
            emptydataframe("stock_eastmoney", df)
            
            
            return df
                
        except:
            not_working_functions.append("stock_eastmoney")
            print("stock_eastmoney not working")
            
                
    
    def straittimes():
        #from selenium import webdriver
        #from selenium.webdriver.chrome.options import Options
        # from selenium.webdriver.chrome.service import Service as ChromeService
        #from webdriver_manager.chrome import ChromeDriverManager
        #import requests
        
        #import time
        #from urllib.request import Request, urlopen
        #from bs4 import BeautifulSoup
        #from datetime import datetime,date
        #from newspaper import Article
        #import pandas as pd
        #import threading
    

        try:
            print("straittimes")
            Errors={}

            Errors["straittimes"]=[]
            
            url = "https://www.straitstimes.com/search?searchkey=ipo"
            domain_url = "http://www.straitstimes.com/"
            title, links, text, pub_date, scraped_date = [], [], [], [], []

           
            options = webdriver.ChromeOptions() 
            options.headless = True
            options.add_argument('--no-sandbox')
            options.add_argument('--disable-dev-shm-usage')
            options.add_experimental_option('excludeSwitches', ['enable-logging']) 

            service = ChromeService(executable_path=ChromeDriverManager().install())
            driver = webdriver.Chrome(service=service, options=options)
            driver.get(url)
            time.sleep(2)

            html = driver.page_source
            driver.quit()
            
            try:
                sp=BeautifulSoup(html, 'lxml')

                # we are in ipo page . one news corresponds to queryly_item_row item
                all_divs = sp.find_all('div',{"class":"queryly_item_row"})     


            except:
                print("STrait time not working")
                not_working_functions.append('straitimes')
                err = "Main link did not load: " + url
                Errors["straittimes"].append(err)
                return
            
            try:
                if (all_divs!=None): 
                 for div1 in all_divs:
                    if(div1!=None):
                        date1=div1.find("div",{"class":"queryly_item_description"})
                        
                        #chck news publish date  from front page
                        utext_main=""
                        if (date1 != None):
                            utext_main=date1.text
                            utext_main=utext_main.lstrip()
                            #print(utext_main)
                            if(len(utext_main)>=12):
                                temp1_month_year=utext_main[0:3]+" "+utext_main[8:12]
                                #print(temp1_month_year)
                                
                                currentMonth = datetime.now().month
                                currentYear = datetime.now().year
                                monthdict={1:"Jan",2:"Feb",3:"Mar",4:"Apr",5:"May",6:"Jun",7:"Jul",8:"Aug",9:"Sep",10:"Oct",11:"Nov",12:"Dec"}
                                currentMonthandYear=str(monthdict[currentMonth])+" "+str(currentYear)
                                #print("\n\n...........\n\n")

                                #print("temp1_month_year "+temp1_month_year)
                                #print("currentMonthandYear " +currentMonthandYear)
                                if(temp1_month_year==currentMonthandYear):
                                    #print("Matched....the news belong to current month, proceed with new fetch details")
                                    #pub_date.append(utext_main) 
                                    
                                    a_all=div1.find_all("a")
                                    if(a_all!=None):
                                        link=""
                                        for a1 in a_all:
                                            if((a1['href']!=None)):
                                                link=a1['href']
                                                links.append(link)
                                                
               
            except:
                if len(links)==0:
                    print("straitimes not working")
                    not_working_functions.append('Korea')
                    Errors["straitimes"].append("Extraction of link not working.")
                    return
                    

            final_links = []
            today = date.today()
            
            # function starts 
            def getartciles(link):
                    flag=0
                    err=err_dict()
                    try:
                        #print (" link which is a function parameter" , link)
                        article = Article(link)
                        article.download()
                        article.parse()
                        #article.nlp()
            
                    except:
                        err["link"]="Link not working: "+link
                        Errors["Korea"].append(err)
                        return
                    
                    try:
                        published=date_correction_for_newspaper3k(article.publish_date)
                        pub_date.append(published)
                        #print("publish date", pub_date)
                    except:
                        err["link"]=link
                        err['published_date']="Error"
                        pub_date.append("-")
                        flag=1
                    
                    try:
                        title.append(article.title)
                        #print("title  .......", title)
                    except:
                        err["link"]=link
                        err["title"]="Error"
                        title.append("-")
                        flag=1
                    
                    try:
                        text.append(article.text)
                        #print(" text ......", text)
                    except:
                        err["link"]=link
                        err["title"]="Error"
                        text.append("-")
                        flag=1

                    scraped_date.append(str(today))
                    
                    if flag==1:
                        Errors["straitimes"].append(err)

                    final_links.append(link)
            
            # function ends 

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
            print("straittimes not working")
            not_working_functions.append('straittimes')   

    def financialpost(keyword):
        try:
            print("financialpost")
            Errors["financialpost"]=[]
            
            url = f"https://financialpost.com/search/?search_text={keyword}"
            domain_url = "https://financialpost.com/"
            headers = {
                "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10.15; rv:78.0) Gecko/20100101 Firefox/78.0",
                "accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.9",
                'sec-fetch-site': 'none',
                'sec-fetch-mode': 'navigate',
                'sec-fetch-user': '?1',
                'sec-fetch-dest': 'document',
                'accept-language': 'en-GB,en-US;q=0.9,en;q=0.8',
            }
            div_class="row"# Class name of div containing the a tag
            #h1_class = "_1Y-96"
            #h1_div_class = "col-xs-12"
            title_h1_class= "article-title"
            date_span_class= ["published-date__since"]
            para_section_class=["article-content__content-group"]

            links=[]
            try:
                page = requests.get(url, headers=headers)
                soup = BeautifulSoup(page.content, "html.parser")
            except:
                print("financialpost not working")
                not_working_functions.append('financialpost')
                err = "Main link did not load: " + url
                Errors["financialpost"].append(err)
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
                    print("financialpost not working")
                    not_working_functions.append('financialpost')
                    Errors["financialpost"].append("Extraction of link not working.")
                    return
                        
            # Remove duplicates
            links = list(set(links))
            
            # links # Debugging - if link array is generated
            collection = []
            scrapper_name = "financialpost"
            
            def getarticles(link):
                flag=0
                err=err_dict()
                try:
                    l_page = requests.get(link, headers=headers)
                    l_soup = BeautifulSoup(l_page.content, 'html.parser')
                except:
                    err["link"]="Link not working: "+link
                    Errors["financialpost"].append(err)
                    return
                
                data = []
                
                # Scraping the heading
                #h1_ele = l_soup.find("h1", {"class": h1_class})
                
                try:
                    title_ele = l_soup.find("h1",{"class":title_h1_class})
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
                    date_ele = l_soup.find("span",{"class": date_span_class})
                    date_text = date_ele.text
                    l=date_text.split(" ")
                    date_text=l[2].strip(",")+"-"+l[1]+"-"+l[3]
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
                    para_ele = (l_soup.findAll("section", {"class": para_section_class}))[-1]
                    data.append(para_ele.text)  # Need to make this better
                except:
                    err["link"]=link
                    err['text']="Error"
                    data.append("-")
                    flag=1
                  # drops the complete data if there is an error
                # Adding data to a collection
                
                if flag==1:
                    Errors["financialpost"].append(err)
                
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
            emptydataframe("financialpost", df)
            # df  = link_correction(df)
            return df
        
        except:
            not_working_functions.append("financialpost")
            print("financialpost not working")  

    def nikkei(keyword):
        try:
            print("nikkei")
            Errors["nikkei"]=[]
            
            url = f"https://asia.nikkei.com/search?query={keyword}"
            
            domain_url = "https://asia.nikkei.com/"
            headers = {
                "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10.15; rv:78.0) Gecko/20100101 Firefox/78.0",
                "accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.9",
                'sec-fetch-site': 'none',
                'sec-fetch-mode': 'navigate',
                'sec-fetch-user': '?1',
                'sec-fetch-dest': 'document',
                'accept-language': 'en-GB,en-US;q=0.9,en;q=0.8',
            }
            div_class="card card--search card--search-article"# Class name of div containing the a tag
            #h1_class = "_1Y-96"
            #h1_div_class = "col-xs-12"
            title_span_class= "ezstring-field"
            date_time_class= ["timestamp__time"]
            para_div_class=["ezrichtext-field"]

            links=[]
            try:
                page = requests.get(url, headers=headers)
                soup = BeautifulSoup(page.content, "html.parser")
            except:
                print("nikkei not working")
                not_working_functions.append('nikkei')
                err = "Main link did not load: " + url
                Errors["nikkei"].append(err)
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
                    print("nikkei not working")
                    not_working_functions.append('nikkei')
                    Errors["nikkei"].append("Extraction of link not working.")
                    return
                        
            # Remove duplicates
            links = list(set(links))
            
            # links # Debugging - if link array is generated
            collection = []
            scrapper_name = "nikkei"
            
            def getarticles(link):
                flag=0
                err=err_dict()
                try:
                    l_page = requests.get(link, headers=headers)
                    l_soup = BeautifulSoup(l_page.content, 'html.parser')
                except:
                    err["link"]="Link not working: "+link
                    Errors["nikkei"].append(err)
                    return
                
                data = []
                
                # Scraping the heading
                #h1_ele = l_soup.find("h1", {"class": h1_class})
                
                try:
                    title_ele = l_soup.find("span",{"class":title_span_class})
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
                    date_ele = l_soup.find("time",{"class": date_time_class})
                    date_text = date_ele.text
                    l=date_text.split(" ")
                    date_text=l[1].strip(",")+"-"+l[0]+"-"+l[2]
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
                    Errors["nikkei"].append(err)
                
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
            emptydataframe("nikkei", df)
            # df  = link_correction(df)
            return df
        
        except:
            not_working_functions.append("nikkei")
            print("nikkei not working")   

    def albawaba(keyword):
        try:
            print("albawaba")
            Errors["albawaba"]=[]
            
            url = f"https://www.albawaba.com/search?keyword={keyword}&sort_by=created"
            domain_url = "https://www.albawaba.com/"
            headers = {
                "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10.15; rv:78.0) Gecko/20100101 Firefox/78.0",
                "accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.9",
                'sec-fetch-site': 'none',
                'sec-fetch-mode': 'navigate',
                'sec-fetch-user': '?1',
                'sec-fetch-dest': 'document',
                'accept-language': 'en-GB,en-US;q=0.9,en;q=0.8',
            }
            div_class = "body-container"  # Class name of div containing the a tag
            #h1_class = "_1Y-96"
            #h1_div_class = "col-xs-12"
            title_h1_class = "page-header"
            date_section_class = [
                "block-field-blocknodearticlecreated", "block-entity-fieldnodecreated"]
            para_section_class = [
                "block-field-blocknodearticlebody", "block-field-blocknodepagebody"]

            links=[]
            try:
                page = requests.get(url, headers=headers)
                soup = BeautifulSoup(page.content, "html.parser")
            except:
                print("albawaba not working")
                not_working_functions.append('albawaba')
                err = "Main link did not load: " + url
                Errors["albawaba"].append(err)
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
                    print("albawaba not working")
                    not_working_functions.append('albawaba')
                    Errors["albawaba"].append("Extraction of link not working.")
                    return
                        
            # Remove duplicates
            links = list(set(links))
            
            # links # Debugging - if link array is generated
            collection = []
            scrapper_name = "albawaba"
            
            def getarticles(link):
                flag=0
                err=err_dict()
                try:
                    l_page = requests.get(link, headers=headers)
                    l_soup = BeautifulSoup(l_page.content, 'html.parser')
                except:
                    err["link"]="Link not working: "+link
                    Errors["albawaba"].append(err)
                    return
                
                data = []
                
                # Scraping the heading
                #h1_ele = l_soup.find("h1", {"class": h1_class})
                
                try:
                    title_ele = l_soup.find("h1",{"class":title_h1_class})
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
                    date_ele = l_soup.find("section",{"class": date_section_class})
                    date_text = date_ele.text
                    date_text=date_text.strip("\n")
                    l=date_text.split(" ")
                    date_text=l[2][0:2]+"-"+l[1]+"-"+l[3]
                    
                    
                    
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
                    para_ele = (l_soup.findAll("section", {"class": para_section_class}))[-1]
                    data.append(para_ele.text)  # Need to make this better
                except:
                    err["link"]=link
                    err['text']="Error"
                    data.append("-")
                    flag=1
                  # drops the complete data if there is an error
                # Adding data to a collection
                
                if flag==1:
                    Errors["albawaba"].append(err)
                
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
            emptydataframe("albawaba", df)
            # df  = link_correction(df)
            return df
        
        except:
            not_working_functions.append("albawaba")
            print("albawaba not working")

    def theaustralianfinancialreview(keyword):
        try:
            print("theaustralianfinancialreview")
            Errors["theaustralianfinancialreview"]=[]
            
            url = f"https://www.afr.com/search?text={keyword}"
            domain_url = "https://www.afr.com/"
            headers = {
                "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10.15; rv:78.0) Gecko/20100101 Firefox/78.0",
                "accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.9",
                'sec-fetch-site': 'none',
                'sec-fetch-mode': 'navigate',
                'sec-fetch-user': '?1',
                'sec-fetch-dest': 'document',
                'accept-language': 'en-GB,en-US;q=0.9,en;q=0.8',
            }
            div_class="_3WTn1 undefined"
            title_h1_class= "_3lFzE"
            date_span_class=["ArticleTimestamp-time"]
            para_div_class=["tl7wu"]

            links=[]
            try:
                page = requests.get(url, headers=headers)
                soup = BeautifulSoup(page.content, "html.parser")
            except:
                print("theaustralianfinancialreview not working")
                not_working_functions.append('theaustralianfinancialreview')
                err = "Main link did not load: " + url
                Errors["theaustralianfinancialreview"].append(err)
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
                    print("theaustralianfinancialreview not working")
                    not_working_functions.append('theaustralianfinancialreview')
                    Errors["theaustralianfinancialreview"].append("Extraction of link not working.")
                    return
                        
            # Remove duplicates
            links = list(set(links))
            
            # links # Debugging - if link array is generated
            collection = []
            scrapper_name = "theaustralianfinancialreview"
            
            def getarticles(link):
                flag=0
                err=err_dict()
                try:
                    l_page = requests.get(link, headers=headers)
                    l_soup = BeautifulSoup(l_page.content, 'html.parser')
                except:
                    err["link"]="Link not working: "+link
                    Errors["theaustralianfinancialreview"].append(err)
                    return
                
                data = []
                
                # Scraping the heading
                #h1_ele = l_soup.find("h1", {"class": h1_class})
                
                try:
                    title_ele = l_soup.find("h1",{"class":title_h1_class})
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
                    date_ele = l_soup.find("time", {"data-testid": date_span_class})
                    date_text = date_ele.text
                    l=date_text.split(" ")
                    date_text=l[1].strip(",")+"-"+l[0]+"-"+l[2]
                    
                    
                    
                    
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
                    Errors["theaustralianfinancialreview"].append(err)
                
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
            emptydataframe("theaustralianfinancialreview", df)
            # df  = link_correction(df)
            return df
        
        except:
            not_working_functions.append("theaustralianfinancialreview")
            print("theaustralianfinancialreview not working")

    def trendnewsagency(keyword):
        try:
            print("trendnewsagency")
            Errors["trendnewsagency"]=[]
            
            url = f"https://en.trend.az/search?query={keyword}"
            domain_url = "https://en.trend.az/"
            headers = {
                "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10.15; rv:78.0) Gecko/20100101 Firefox/78.0",
                "accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.9",
                'sec-fetch-site': 'none',
                'sec-fetch-mode': 'navigate',
                'sec-fetch-user': '?1',
                'sec-fetch-dest': 'document',
                'accept-language': 'en-GB,en-US;q=0.9,en;q=0.8',
            }
            div_class = "inlineSearchResults"  # Class name of div containing the a tag
            #h1_class = "_1Y-96"
            #h1_div_class = "col-xs-12"
            title_div_class = "top-part"
            date_span_class = "date-time"
            para_div_class = "article-content"

            links=[]
            try:
                page = requests.get(url, headers=headers)
                soup = BeautifulSoup(page.content, "html.parser")
            except:
                print("trendnewsagency not working")
                not_working_functions.append('trendnewsagency')
                err = "Main link did not load: " + url
                Errors["trendnewsagency"].append(err)
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
                    print("trendnewsagency not working")
                    not_working_functions.append('trendnewsagency')
                    Errors["trendnewsagency"].append("Extraction of link not working.")
                    return
                        
            # Remove duplicates
            links = list(set(links))
            
            # links # Debugging - if link array is generated
            collection = []
            scrapper_name = "trendnewsagency"
            
            def getarticles(link):
                flag=0
                err=err_dict()
                try:
                    l_page = requests.get(link, headers=headers)
                    l_soup = BeautifulSoup(l_page.content, 'html.parser')
                except:
                    err["link"]="Link not working: "+link
                    Errors["trendnewsagency"].append(err)
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
                    date_ele = l_soup.find("span", {"class": date_span_class})
                    date_text = date_ele.text
                    l=date_text.split(" ")
                    date_text=l[0]+"-"+l[1]+"-"+l[2]
                    
                    
                    
                    
                    
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
                    Errors["trendnewsagency"].append(err)
                
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
            emptydataframe("trendnewsagency", df)
            # df  = link_correction(df)
            return df
        
        except:
            not_working_functions.append("trendnewsagency")
            print("trendnewsagency not working")


    def globallegalchronicle(keyword):
        try:
            print("globallegalchronicle")
            Errors["globallegalchronicle"]=[]
            
            url = f"https://globallegalchronicle.com/?s={keyword}"
            domain_url = "https://globallegalchronicle.com/"
            headers = {
                "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10.15; rv:78.0) Gecko/20100101 Firefox/78.0",
                "accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.9",
                'sec-fetch-site': 'none',
                'sec-fetch-mode': 'navigate',
                'sec-fetch-user': '?1',
                'sec-fetch-dest': 'document',
                'accept-language': 'en-GB,en-US;q=0.9,en;q=0.8',
            }
            h3_class = "entry-title"  # Class name of div containing the a tag
            #h1_class = "_1Y-96"
            #h1_div_class = "col-xs-12"
            title_h1_class = "entry-title"
            date_time_class = "entry-date"
            para_div_class = "entry-content"

            links=[]
            try:
                page = requests.get(url, headers=headers)
                soup = BeautifulSoup(page.content, "html.parser")
            except:
                print("globallegalchronicle not working")
                not_working_functions.append('globallegalchronicle')
                err = "Main link did not load: " + url
                Errors["globallegalchronicle"].append(err)
                return
            
            
            try:
                
                for h2_tag in soup.find_all("h3", {"class": h3_class}):
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
                    print("globallegalchronicle not working")
                    not_working_functions.append('globallegalchronicle')
                    Errors["globallegalchronicle"].append("Extraction of link not working.")
                    return
                        
            # Remove duplicates
            links = list(set(links))
            
            # links # Debugging - if link array is generated
            collection = []
            scrapper_name = "globallegalchronicle"
            
            def getarticles(link):
                flag=0
                err=err_dict()
                try:
                    l_page = requests.get(link, headers=headers)
                    l_soup = BeautifulSoup(l_page.content, 'html.parser')
                except:
                    err["link"]="Link not working: "+link
                    Errors["globallegalchronicle"].append(err)
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
                    l=date_text.split(" ")
                    date_text=l[1].strip(",")+"-"+l[0]+"-"+l[2]
                    
                    
                    
                    
                    
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
                    Errors["globallegalchronicle"].append(err)
                
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
            emptydataframe("globallegalchronicle", df)
            # df  = link_correction(df)
            return df
        
        except:
            not_working_functions.append("globallegalchronicle")
            print("globallegalchronicle not working")

    def ewnews(keyword):
        try:
            print("ewnews")
            Errors["ewnews"]=[]
            
            url = f"https://ewnews.com/?s={keyword}"
            domain_url = "https://ewnews.com"
            headers = {
                "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10.15; rv:78.0) Gecko/20100101 Firefox/78.0",
                "accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.9",
                'sec-fetch-site': 'none',
                'sec-fetch-mode': 'navigate',
                'sec-fetch-user': '?1',
                'sec-fetch-dest': 'document',
                'accept-language': 'en-GB,en-US;q=0.9,en;q=0.8',
            }
            div_class = "entry-title"
            h1_class = "entry-title"
            date_div_class = "entry-date published"
            para_div_class = "entry-content col-md-12"

            links=[]
            try:
                page = requests.get(url, headers=headers)
                soup = BeautifulSoup(page.content, "html.parser")
            except:
                print("ewnews not working")
                not_working_functions.append('ewnews')
                err = "Main link did not load: " + url
                Errors["ewnews"].append(err)
                return
            
            
            try:
                
                for h3 in soup.find_all("h3", {"class": "entry-title"}):
                    link = h3.a["href"]
                    if link[0] == '/':
                        link = domain_url + link
                    links.append(link)
            except:
                if len(links)==0:
                    print("ewnews not working")
                    not_working_functions.append('ewnews')
                    Errors["ewnews"].append("Extraction of link not working.")
                    return
                        
            # Remove duplicates
            links = list(set(links))
            
            # links # Debugging - if link array is generated
            collection = []
            scrapper_name = "ewnews"
            
            def getarticles(link):
                flag=0
                err=err_dict()
                try:
                    l_page = requests.get(link, headers=headers)
                    l_soup = BeautifulSoup(l_page.content, 'html.parser')
                except:
                    err["link"]="Link not working: "+link
                    Errors["ewnews"].append(err)
                    return
                
                data = []
                
                # Scraping the heading
                #h1_ele = l_soup.find("h1", {"class": h1_class})
                
                try:
                    title_ele = l_soup.find("h1", {"class": h1_class})
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
                    date_ele = l_soup.find("span", {"class": date_div_class})
                    date_text = date_ele.text
                    l=date_text.split(" ")
                    date_text=l[1].strip(",")+"-"+l[0]+"-"+l[2]
                    
                    
                    
                    
                    
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
                    para_ele = l_soup.find("div", {"class": para_div_class})
                    data.append(para_ele.text)  # Need to make this better
                except:
                    err["link"]=link
                    err['text']="Error"
                    data.append("-")
                    flag=1
                  # drops the complete data if there is an error
                # Adding data to a collection
                
                if flag==1:
                    Errors["ewnews"].append(err)
                
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
            emptydataframe("ewnews", df)
            # df  = link_correction(df)
            return df
        
        except:
            not_working_functions.append("ewnews")
            print("ewnews not working")

    def dw(keyword):
        try:
            print("dw")
            Errors["dw"]=[]
            
            url = f"https://www.dw.com/search/en?searchNavigationId=9097&languageCode=en&origin=gN&item={keyword}"
            domain_url = "https://www.dw.com/"
            headers = {
                "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10.15; rv:78.0) Gecko/20100101 Firefox/78.0",
                "accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.9",
                'sec-fetch-site': 'none',
                'sec-fetch-mode': 'navigate',
                'sec-fetch-user': '?1',
                'sec-fetch-dest': 'document',
                'accept-language': 'en-GB,en-US;q=0.9,en;q=0.8',
            }
            div_class="searchResult"
            title_h1_class= "sc-efBctP gdiwoc sc-bwANAz dPXGty"
            date_time_itemprop=["true"]
            para_div_class=["sc-gicCDI sc-bZkfAO czqpjL hngCMv sc-iLIByi kkWXvA rich-text has-italic"]

            links=[]
            try:
                page = requests.get(url, headers=headers)
                soup = BeautifulSoup(page.content, "html.parser")
            except:
                print("dw not working")
                not_working_functions.append('dw')
                err = "Main link did not load: " + url
                Errors["dw"].append(err)
                return
            
            
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
                    print("dw not working")
                    not_working_functions.append('dw')
                    Errors["dw"].append("Extraction of link not working.")
                    return
                        
            # Remove duplicates
            links = list(set(links))
            
            # links # Debugging - if link array is generated
            collection = []
            scrapper_name = "dw"
            
            def getarticles(link):
                flag=0
                err=err_dict()
                try:
                    l_page = requests.get(link, headers=headers)
                    l_soup = BeautifulSoup(l_page.content, 'html.parser')
                except:
                    err["link"]="Link not working: "+link
                    Errors["dw"].append(err)
                    return
                
                data = []
                
                # Scraping the heading
                #h1_ele = l_soup.find("h1", {"class": h1_class})
                
                try:
                    title_ele = l_soup.find("h1",{"class":title_h1_class})
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
                    date_ele = l_soup.find("time", {"aria-hidden": date_time_itemprop})
                    date_text = date_ele.text
                    l=date_text.split("/")
                    date_text=l[1]+"-"+l[0]+"-"+l[2]
                    
                    
                    
                    
                    
                    
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
                    Errors["dw"].append(err)
                
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
            emptydataframe("dw", df)
            # df  = link_correction(df)
            return df
        
        except:
            not_working_functions.append("dw")
            print("dw not working")

    def uzdaily(keyword):
        try:
            print("uzdaily")
            Errors["uzdaily"]=[]
            
            url = f"https://www.uzdaily.uz/en/search?q={keyword}"
            domain_url = "https://www.uzdaily.uz/en"
            headers = {
                "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10.15; rv:78.0) Gecko/20100101 Firefox/78.0",
                "accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.9",
                'sec-fetch-site': 'none',
                'sec-fetch-mode': 'navigate',
                'sec-fetch-user': '?1',
                'sec-fetch-dest': 'document',
                'accept-language': 'en-GB,en-US;q=0.9,en;q=0.8',
            }
            div_class="dis_flex box_shadow margin_block"# Class name of div containing the a tag
            #h1_class = "_1Y-96"
            #h1_div_class = "col-xs-12"
            title_h3_class= "header"
            date_p_class= ["date"]
            para_div_class=["main links"]

            links=[]
            try:
                page = requests.get(url, headers=headers)
                soup = BeautifulSoup(page.content, "html.parser")
            except:
                print("uzdaily not working")
                not_working_functions.append('uzdaily')
                err = "Main link did not load: " + url
                Errors["uzdaily"].append(err)
                return
            
            
            try:
                
                for divtag in soup.find_all("div", {"class": div_class}):
                    for a in divtag.find_all("a", href=True):
                        link = a["href"]  # Gets the link

                    

                    # Filtering advertaisment links
                        link_start = domain_url
                        if link.startswith(link_start):
                            links.append(link)
            except:
                if len(links)==0:
                    print("uzdaily not working")
                    not_working_functions.append('uzdaily')
                    Errors["uzdaily"].append("Extraction of link not working.")
                    return
                        
            # Remove duplicates
            links = list(set(links))
            
            # links # Debugging - if link array is generated
            collection = []
            scrapper_name = "uzdaily"
            
            def getarticles(link):
                flag=0
                err=err_dict()
                try:
                    l_page = requests.get(link, headers=headers)
                    l_soup = BeautifulSoup(l_page.content, 'html.parser')
                except:
                    err["link"]="Link not working: "+link
                    Errors["uzdaily"].append(err)
                    return
                
                data = []
                
                # Scraping the heading
                #h1_ele = l_soup.find("h1", {"class": h1_class})
                
                try:
                    title_ele = l_soup.find("h3")
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
                    date_ele = l_soup.find("p", {"class": date_p_class})
                    date_text = date_ele.text
                    l=date_text.split(" ")
                    date_text=l[0]
                    
                    
                    
                    
                    
                    
                    
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
                    Errors["uzdaily"].append(err)
                
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
            emptydataframe("uzdaily", df)
            # df  = link_correction(df)
            return df
        
        except:
            not_working_functions.append("uzdaily")
            print("uzdaily not working")

    def kedglobal(keyword):
        try:
            print("kedglobal")
            Errors["kedglobal"]=[]
            
            url = f"https://www.kedglobal.com/newsSearch?keyword={keyword}"
            domain_url = "https://www.kedglobal.com"
            headers = {
                "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10.15; rv:78.0) Gecko/20100101 Firefox/78.0",
                "accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.9",
                'sec-fetch-site': 'none',
                'sec-fetch-mode': 'navigate',
                'sec-fetch-user': '?1',
                'sec-fetch-dest': 'document',
                'accept-language': 'en-GB,en-US;q=0.9,en;q=0.8',
            }

            links=[]
            try:
                page = requests.get(url, headers=headers)
                soup = BeautifulSoup(page.content, "html.parser")
            except:
                print("kedglobal not working")
                not_working_functions.append('kedglobal')
                err = "Main link did not load: " + url
                Errors["kedglobal"].append(err)
                return
            
            
            try:
                
                all_divs = soup.find_all("div", {"class": "box"})
                for div in all_divs:
                    try:
                        links.append(domain_url+div.a["href"])
                    except:
                        continue
            except:
                if len(links)==0:
                    print("kedglobal not working")
                    not_working_functions.append('kedglobal')
                    Errors["kedglobal"].append("Extraction of link not working.")
                    return
                        
            # Remove duplicates
            links = list(set(links))
            
            # links # Debugging - if link array is generated
            collection = []
            scrapper_name = "kedglobal"
            
            def getarticles(link):
                flag=0
                err=err_dict()
                try:
                    l_page = requests.get(link, headers=headers)
                    l_soup = BeautifulSoup(l_page.content, 'html.parser')
                except:
                    err["link"]="Link not working: "+link
                    Errors["kedglobal"].append(err)
                    return
                
                data = []
                
                # Scraping the heading
                #h1_ele = l_soup.find("h1", {"class": h1_class})
                
                try:
                    title_ele = l_soup.find("h1", {"class": "tit"})
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
                    date_ele = l_soup.find("p", {"class": "update_time"})
                    date_text = date_ele.text
                    date_text=date_text.strip("\n")
                    l=date_text.split("\n")
                    l[3]=l[3].strip(" ")
                    l1=l[3].split(" ")
                    date_text=l1[1].strip(",")+"-"+l1[0]+"-"+l1[2]
                    
                    
                    
                    
                    
                    
                    
                    
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
                    para_ele = (l_soup.findAll("div", {"class": "cont"}))[-1]
                    data.append(para_ele.text)  # Need to make this better
                except:
                    err["link"]=link
                    err['text']="Error"
                    data.append("-")
                    flag=1
                  # drops the complete data if there is an error
                # Adding data to a collection
                
                if flag==1:
                    Errors["kedglobal"].append(err)
                
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
            emptydataframe("kedglobal", df)
            # df  = link_correction(df)
            return df
        
        except:
            not_working_functions.append("kedglobal")
            print("kedglobal not working")

    def pymnts(keyword):
        try:
            print("pymnts")
            Errors["pymnts"]=[]
            
            url = f"https://www.pymnts.com/?s={keyword}"
            domain_url = "https://www.pymnts.com/"
            headers = {
                "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10.15; rv:78.0) Gecko/20100101 Firefox/78.0",
                "accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.9",
                'sec-fetch-site': 'none',
                'sec-fetch-mode': 'navigate',
                'sec-fetch-user': '?1',
                'sec-fetch-dest': 'document',
                'accept-language': 'en-GB,en-US;q=0.9,en;q=0.8',
            }
            div_class="row row-cols-1"
            title_h1_class= "mb-4 text-center text-dark fw-bold display-6"
            date_span_class=["small muted text-uppercase d-block d-md-inline"]
            para_div_class=["single lh-article mt-1 lnk-article"]

            links=[]
            try:
                page = requests.get(url, headers=headers)
                soup = BeautifulSoup(page.content, "html.parser")
            except:
                print("pymnts not working")
                not_working_functions.append('pymnts')
                err = "Main link did not load: " + url
                Errors["pymnts"].append(err)
                return
            
            
            try:
                
                for divtag in soup.find_all("div", {"class": div_class}):
                    for a in divtag.find_all("a", href=True):
                        link = a["href"]  # Gets the link
                        if link[0] == '/':
                            link = domain_url + link[1:]

                    

                    # Filtering advertaisment links
                        link_start = domain_url
                        if link.startswith(link_start):
                            links.append(link)
            except:
                if len(links)==0:
                    print("pymnts not working")
                    not_working_functions.append('pymnts')
                    Errors["pymnts"].append("Extraction of link not working.")
                    return
                        
            # Remove duplicates
            links = list(set(links))
            
            # links # Debugging - if link array is generated
            collection = []
            scrapper_name = "pymnts"
            
            def getarticles(link):
                flag=0
                err=err_dict()
                try:
                    l_page = requests.get(link, headers=headers)
                    l_soup = BeautifulSoup(l_page.content, 'html.parser')
                except:
                    err["link"]="Link not working: "+link
                    Errors["pymnts"].append(err)
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
                    date_ele = l_soup.find("span", {"class": date_span_class})
                    date_text = date_ele.text
                    l=date_text.split(" ")
                    date_text=l[1].strip(",")+"-"+l[0]+"-"+l[2]
                    
                    
                    
                    
                    
                    
                    
                    
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
                    Errors["pymnts"].append(err)
                
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
            emptydataframe("pymnts", df)
            # df  = link_correction(df)
            return df
        
        except:
            not_working_functions.append("pymnts")
            print("pymnts not working")

    def timesofindia(keyword):
        try:
            print("timesofindia")
            Errors["timesofindia"]=[]
            
            url = f"https://timesofindia.indiatimes.com/topic/{keyword}/news"
            domain_url = "https://timesofindia.indiatimes.com"
            headers = {
                "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10.15; rv:78.0) Gecko/20100101 Firefox/78.0",
                "accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.9",
                'sec-fetch-site': 'none',
                'sec-fetch-mode': 'navigate',
                'sec-fetch-user': '?1',
                'sec-fetch-dest': 'document',
                'accept-language': 'en-GB,en-US;q=0.9,en;q=0.8',
            }
            div_class = "Mc7GB"
            h1_class = "_1Y-96"
            date_div_class = "yYIu- byline"
            para_div_class = "_3YYSt"

            links=[]
            try:
                page = requests.get(url, headers=headers)
                soup = BeautifulSoup(page.content, "html.parser")
            except:
                print("timesofindia not working")
                not_working_functions.append('timesofindia')
                err = "Main link did not load: " + url
                Errors["timesofindia"].append(err)
                return
            
            
            try:
                
                for divtag in soup.find_all("div", {"class": div_class}):
                    for a in divtag.find_all("a", href=True):
                        link = a["href"]  # Gets the link
                        if link[0] == '/':
                            link = domain_url + link[1:]

                    

                    # Filtering advertaisment links
                        link_start = domain_url
                        if link.startswith(link_start):
                            links.append(link)
            except:
                if len(links)==0:
                    print("timesofindia not working")
                    not_working_functions.append('timesofindia')
                    Errors["timesofindia"].append("Extraction of link not working.")
                    return
                        
            # Remove duplicates
            links = list(set(links))
            
            # links # Debugging - if link array is generated
            collection = []
            scrapper_name = "timesofindia"
            
            def getarticles(link):
                flag=0
                err=err_dict()
                try:
                    l_page = requests.get(link, headers=headers)
                    l_soup = BeautifulSoup(l_page.content, 'html.parser')
                except:
                    err["link"]="Link not working: "+link
                    Errors["timesofindia"].append(err)
                    return
                
                data = []
                
                # Scraping the heading
                #h1_ele = l_soup.find("h1", {"class": h1_class})
                
                try:
                    title_ele = l_soup.find("h1", {"class": h1_class})
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
                    l=date_text.split(" ")
                    date_text=l[-4].strip(",")+"-"+l[-5]+"-"+l[-3].strip(",")

                    
                    
                    

                    
                    
                    
                    
                    
                    
                    
                    
                    
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
                    Errors["timesofindia"].append(err)
                
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
            emptydataframe("timesofindia", df)
            # df  = link_correction(df)
            return df
        
        except:
            not_working_functions.append("timesofindia")
            print("timesofindia not working")



    def bankok_post(param):
        try:
            print("Bangkok Post......")
            Errors["Bangkok_post"]=[]
            title,links,links1,text,pub_date,scraped_date = [],[],[],[],[],[]
            main_url="https://www.bangkokpost.com/"
            ipo_url="https://search.bangkokpost.com/search/result?category=all&&q="+param


            options = webdriver.ChromeOptions() 
            options.headless = True
            options.add_argument('--no-sandbox')
            options.add_argument('--disable-dev-shm-usage')
            options.add_experimental_option('excludeSwitches', ['enable-logging']) 

            service = ChromeService(executable_path=ChromeDriverManager().install())
            driver = webdriver.Chrome(service=service, options=options)
            
            try:
                driver.get(ipo_url)
                html = driver.page_source
                driver.quit()
                soup=BeautifulSoup(html,"html.parser")
            except:
                print("Bangkok_post not working")
                not_working_functions.append('Bangkok_post')
                err = "Main link did not load: " + ipo_url
                Errors["Bangkok_post"].append(err)
                return

            

            #navigating to ul first where class is searchlist 
            
            try:
                al_ul=soup.find("ul",{"class":"SearchList"})
                li=al_ul.find_all("li")
                if (li !=None):
                    for item in li:
                        if (item !=None):

                            link_item=item.find("h3")
                            if (link_item !=None):

                                
                                link_i=link_item.find('a', href=True)
                                
                                if (link_i !=None):
                                    link_i1=link_i['href']

                                    #print("link_i's......",link_i1)
                                    links1.append(link_i1)
            except:
                if len(links1)==0:
                    print("Bangkok_post not working")
                    not_working_functions.append('Bangkok_post')
                    Errors["Bangkok_post"].append("Extraction of link not working.")
                    return

            def getArticles(link1):
                flag=0
                err=err_dict()
                user_agent = 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/108.0.0.0 Safari/537.36'
                config = Config()
                config.browser_user_agent = user_agent
                config.request_timeout = 120
                try:
                    article = Article(link1, config = config)
                    time.sleep(2)
                    article.download()
                    time.sleep(3)
                    article.parse()
                except:
                    err["link"]="Link not working: "+link1
                    Errors["Bangkok_post"].append(err)
                    return

                #link
            

                #title
                try:
                    ti=article.title
                    
                    #print(article.text)
                except:
                    err["link"]=link1
                    err["title"]="Error"
                    ti="-"
                    flag=1

                #text
                try:
                    #print(" text " + article.text)\
                    te=article.text
                    
                    
                except:
                    err["link"]=link1
                    err["text"]="Error"
                    te="-"
                    flag=1
            
                #publish_date
                
                try:
                    headers = {
                                            "User-Agent":"Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/109.0.0.0 Safari/537.36",
                                            "accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.9",
                                            'sec-fetch-site': 'none',
                                            'sec-fetch-mode': 'navigate',
                                            'sec-fetch-user': '?1',
                                            'sec-fetch-dest': 'document',
                                            'accept-language': 'en-GB,en-US;q=0.9,en;q=0.8',
                                        }
                    page11=requests.get(link1,headers=headers)
                    soup1=BeautifulSoup(page11.content,"html.parser")
                    published="-"
                    al_date=soup1.find("div",{"class":"article-info"})
                    if (al_date !=None):
                        date_time=al_date.find("div",{"class":"row"})
                        if(date_time !=None):
                            date_item=date_time.find("div",{"class":"col-15 col-md"})
                            if(date_item !=None):
                                date_para=date_item.find("p")
                                if (date_para.text !=None):
                                    
                                    date_string=date_para.text[11:]
                                    date_string1=date_string.strip()
                                    
                                    publish_date21=date_string1[:11]

                                    # Full month format
                                    full_month_format = "%d %b %Y"

                                    # Convert the string into a datetime object
                                    publish_date2=datetime.strptime(publish_date21, full_month_format)
                                    
                                    published=date_correction_for_newspaper3k(publish_date2)


                    elif (al_date ==None):
                        all_date=soup1.find("div",{"class":"media-headline"})
                        if (all_date !=None):
                            date_para=all_date.find ("div",{"class":"f-icon"})
                            date_string=date_para.text[11:]
                            date_string1=date_string.strip()
                        
                            full_month_format = "%d %b %Y"

                            # Convert the string into a datetime object
                            publish_date2=datetime.strptime(date_string1, full_month_format)
                            
                            published=date_correction_for_newspaper3k(publish_date2)
                
                except:
                    err["link"]=link1
                    err['published_date']="Error"
                    published="-"
                    flag=1
                
                if flag==1:
                    Errors["Bangkok_post"].append(err)
                
                text.append(te)
                links.append (link1)
                title.append(ti)
                pub_date.append(published) 
                today=date.today()
                scraped_date.append(str(today))

                


            length=len(links1)
            thread_list=[]
            for i in range(length):
                    thread_list.append(threading.Thread(target=getArticles, args=(links1[i], )))
                        
            for thread in thread_list:
                    thread.start()
                        
            for thread in thread_list:
                    thread.join()

            
                        
            df = pd.DataFrame({"text": text, "link": links,
                                        "publish_date": pub_date, "scraped_date": scraped_date, "title": title})
                        
            df = df.drop_duplicates(subset=["link"])
            #print("df .................", df)
            df = FilterFunction(df)
            emptydataframe("bankokpost", df)
            return df
                    
        except:
            print("Bangkok post  not working")
            not_working_functions.append('bankokpost') 



    def himalayan_times(param):
        from selenium import webdriver
        from selenium.webdriver.chrome.service import Service as ChromeService
        from webdriver_manager.chrome import ChromeDriverManager
        from newspaper import Article
        from datetime import datetime,date
        import threading

        Errors={}

        Errors["himalayantimes"]=[]
        error_list=[]
        title,links,final_links,text,pub_date,scraped_date=[],[],[],[],[],[]

        try:
            main_url="https://thehimalayantimes.com/"
            ipo_url="https://thehimalayantimes.com/search?query=ipo"
            options = webdriver.ChromeOptions() 
            options.headless = True
            options.add_argument('--no-sandbox')
            options.add_argument('--disable-dev-shm-usage')
            options.add_experimental_option('excludeSwitches', ['enable-logging']) 

            service = ChromeService(executable_path=ChromeDriverManager().install())
            driver = webdriver.Chrome(service=service, options=options)
            driver.get(ipo_url)
            html = driver.page_source
            driver.quit()

            soup=BeautifulSoup(html,"html.parser")

            print("himalayan times")
            #Start Scraping 
            h3_divs=soup.find_all("h3",{"class":"alith_post_title"})

            for h3_div in h3_divs:
                if(h3_div!=None):
                        a_div=h3_div.find('a',href=True)
                        #print("a div",a_div)
                        
                        if(a_div!=None):
                        
                                link1=a_div['href']
                                links.append(link1)
            print("Links\n",links)

            def getarticles(link):
                #title
                flag=0
                err=err_dict()
                for link in links:
                    html1=requests.get(link)
                    soup1=BeautifulSoup(html1.content,"html.parser")
                    try:
                        title_div=soup1.find("h1",{"class":"alith_post_title"})
                        if (title_div !=None):
                            title1=title_div.text
                        
                            title1=title1.strip()
                            #print("title=",title1)
                            title.append(title1)
                    except:
                        err["link"]=link
                        err["title"]="Error"
                        title.append("-")
                        flag=1
                    #print("Title:\n",title)
                    try:
                        text1=""
                        div_find=soup1.find("div",{"class":"dropcap column-1 animate-box"})
                        p_find=div_find.find_all("p")
                        for p in p_find:
                            text1+=p.text
                        #print("Text1=",text1)
                        text.append(text1)
                    except:
                        err["link"]=link
                        err["text"]="Error"
                        text.append("-")
                        flag=1

                    try:

                        publish_date=""
                        date_find=soup1.find("div",{"class":"article_date"})
                        if (date_find!=None):
                            publish_date=date_find.text
                            publish_date=publish_date[20:]
                            publish_date=publish_date.strip()
                            #print("Publish date=",publish_date)
                            publish_date_date=publish_date[4:6]
                            publish_date_month=publish_date[:3]
                            publish_date_year=publish_date[-4:]
                            publish_date1=publish_date_date+" "+publish_date_month+" "+publish_date_year
                            #print("Publish Date=",publish_date1)
                            full_month_format = "%d %b %Y"
                            publish_date2=datetime.strptime(publish_date1, full_month_format)
                            published=date_correction_for_newspaper3k(publish_date2)
                            #print("Published Date=",published)
                            pub_date.append(published)

                    except:
                        err["link"]=link
                        err["pub_date"]="Error"
                        pub_date.append("-")
                        flag=1
                    #scraped date
                    today=date.today()
                    scraped_date.append(str(today))

                    final_links.append(link)

                if flag==1:
                    Errors["himalayantimes"].append(err)
        
            thread_list=[]
            length=len(links)
            for i in range(length):
                thread_list.append(threading.Thread(target=getarticles, args=(links[i], )))
            
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
                    print("Himalayan times not working")
                    not_working_functions.append('himalayantimes')
                    err = "Main link did not load "
                    Errors["himalayantimes"].append(err)
                    return
    

    def tradingcharts(keyword):
        try:
            print("tradingcharts")
            Errors["tradingcharts"]=[]
            
          
            url = f"https://futures.tradingcharts.com/search.php?keywords={keyword}&futures=1"
            domain_url = "https://futures.tradingcharts.com"
            headers = {
                "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10.15; rv:78.0) Gecko/20100101 Firefox/78.0",
                "accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.9",
                'sec-fetch-site': 'none',
                'sec-fetch-mode': 'navigate',
                'sec-fetch-user': '?1',
                'sec-fetch-dest': 'document',
                'accept-language': 'en-GB,en-US;q=0.9,en;q=0.8',
            }

            links=[]
            try:
                page = requests.get(url, headers=headers)
                soup = BeautifulSoup(page.content, "html.parser")
            except:
                print("tradingcharts not working")
                not_working_functions.append('tradingcharts')
                err = "Main link did not load: " + url
                Errors["tradingcharts"].append(err)
                return
            
            
            try:
                
                all_divs = soup.find_all("a", {"class": "clUnSeResItemTitle"})
                for div in all_divs:
                    links.append("https:"+div["href"])
            except:
                if len(links)==0:
                    print("tradingcharts not working")
                    not_working_functions.append('tradingcharts')
                    Errors["tradingcharts"].append("Extraction of link not working.")
                    return
                        
            # Remove duplicates
            links = list(set(links))
            
            # links # Debugging - if link array is generated
            collection = []
            scrapper_name = "tradingcharts"
            
            def getarticles(link):
                
                flag=0
                err=err_dict()
                try:
                    l_page = requests.get(link, headers=headers)
                    l_soup = BeautifulSoup(l_page.content, 'html.parser')
                except:
                    err["link"]="Link not working: "+link
                    Errors["tradingcharts"].append(err)
                    return
                
                data = []
                
                # Scraping the heading
                #h1_ele = l_soup.find("h1", {"class": h1_class})
                
                try:
                    title_ele =l_soup.find("h2", {"class": "fe_heading2"})
                    title_text = title_ele.text
                    data.append(title_text)
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
                    date_ele = l_soup.find("div", {"class": "news_story m-cellblock m-padding"})
                    date_text = date_ele.text
                    date_text=date_text.strip("\n")
                    l=date_text.split("\n")
                    date_text=l[0]
                    l1=date_text.split('(')
                    l2=l1[0].split(",")
                    l3=l2[-2].split(" ")

                    date_text= l3[2]+"-"+l3[1]+"-"+l2[-1]

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
                    para_ele = l_soup.findAll("div", {"class": "news_story m-cellblock m-padding"})[-1]
                    para_text = para_ele.text
                    data.append(para_text)  # Need to make this better
                except:
                    err["link"]=link
                    err['text']="Error"
                    data.append("-")
                    flag=1
                  # drops the complete data if there is an error
                # Adding data to a collection
                
                if flag==1:
                    Errors["tradingcharts"].append(err)
                
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
            emptydataframe("tradingcharts", df)
            # df  = link_correction(df)
            
            return df
        
        except:
            not_working_functions.append("tradingcharts")
            print("tradingcharts not working")

    def kontan(keyword):
        try:
            print("kontan")
            Errors["kontan"]=[]
            
          
            url = f"https://www.kontan.co.id/search/?search={keyword}&Button_search="
            url1 = "https:"
            headers = {
                "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10.15; rv:78.0) Gecko/20100101 Firefox/78.0",
                "accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.9",
                'sec-fetch-site': 'none',
                'sec-fetch-mode': 'navigate',
                'sec-fetch-user': '?1',
                'sec-fetch-dest': 'document',
                'accept-language': 'en-GB,en-US;q=0.9,en;q=0.8',
            }

            links=[]
            try:
                page = requests.get(url, headers=headers)
                soup = BeautifulSoup(page.content, "html.parser")
            except:
                print("kontan not working")
                not_working_functions.append('kontan')
                err = "Main link did not load: " + url
                Errors["kontan"].append(err)
                return
            
            
            try:
                
                for divtag in soup.find_all('div', {'class': 'sp-hl linkto-black'}):
                    for a in divtag.find_all('a', href=True):
                        links.append(url1 + a['href'])
            except:
                if len(links)==0:
                    print("kontan not working")
                    not_working_functions.append('kontan')
                    Errors["kontan"].append("Extraction of link not working.")
                    return
                        
            # Remove duplicates
            links = list(set(links))
            
            # links # Debugging - if link array is generated
            collection = []
            scrapper_name = "kontan"
            
            def getarticles(link):
                
                flag=0
                err=err_dict()
                try:
                    l_page = requests.get(link, headers=headers)
                    l_soup = BeautifulSoup(l_page.content, 'html.parser')
                except:
                    err["link"]="Link not working: "+link
                    Errors["kontan"].append(err)
                    return
                
                data = []
                
                # Scraping the heading
                #h1_ele = l_soup.find("h1", {"class": h1_class})
                
                try:
                    title_ele =l_soup.find("h1", {"class": "detail-desk"})
                    title_text = title_ele.text
                    title_text=translate(title_text)
                    data.append(title_text)
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
                    date_ele = l_soup.find("div", {"class": "fs14 ff-opensans font-gray"})
                    date_text = date_ele.text
                    date_text= translate(date_text)
                    l=date_text.split(" ")
                    l[2]=l[2].strip(",")
                    if l[2].isnumeric() :
                        date_text=l[2].strip(",")+"-"+l[1]+"-"+l[3]
                    else:
                        date_text=l[1]+"-"+l[2].strip(",")+"-"+l[3]
                    

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
                    para_ele = l_soup.findAll("div", {"class": "tmpt-desk-kon"})[-1]
                    para_text = para_ele.text
                    para_text=translate(para_text)
                    data.append(para_text)  # Need to make this better
                except:
                    err["link"]=link
                    err['text']="Error"
                    data.append("-")
                    flag=1
                  # drops the complete data if there is an error
                # Adding data to a collection
                
                if flag==1:
                    Errors["kontan"].append(err)
                
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
            emptydataframe("kontan", df)
            # df  = link_correction(df)
            
            return df
        
        except:
            not_working_functions.append("kontan")
            print("kontan not working")


    def tagesschau(keyword):
        try:
            print("tagesschau")
            Errors["tagesschau"]=[]
            
          
            url = f"https://www.tagesschau.de/suche2.html?query={keyword}&sort_by=date"
            domain_url = "https://www.tagesschau.de"
            headers = {
                "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10.15; rv:78.0) Gecko/20100101 Firefox/78.0",
                "accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.9",
                'sec-fetch-site': 'none',
                'sec-fetch-mode': 'navigate',
                'sec-fetch-user': '?1',
                'sec-fetch-dest': 'document',
                'accept-language': 'en-GB,en-US;q=0.9,en;q=0.8',
            }

            links=[]
            try:
                page = requests.get(url, headers=headers)
                soup = BeautifulSoup(page.content, "html.parser")
            except:
                print("tagesschau not working")
                not_working_functions.append('tagesschau')
                err = "Main link did not load: " + url
                Errors["tagesschau"].append(err)
                return
            
            
            try:
                
                all_divs = soup.find_all("h3", {"class": "headline"})
                for div in all_divs:
                    links.append(domain_url+div.a["href"])
            except:
                if len(links)==0:
                    print("tagesschau not working")
                    not_working_functions.append('tagesschau')
                    Errors["tagesschau"].append("Extraction of link not working.")
                    return
                        
            # Remove duplicates
            links = list(set(links))
            
            # links # Debugging - if link array is generated
            collection = []
            scrapper_name = "tagesschau"
            
            def getarticles(link):
                
                flag=0
                err=err_dict()
                try:
                    l_page = requests.get(link, headers=headers)
                    l_soup = BeautifulSoup(l_page.content, 'html.parser')
                except:
                    err["link"]="Link not working: "+link
                    Errors["tagesschau"].append(err)
                    return
                
                data = []
                
                # Scraping the heading
                #h1_ele = l_soup.find("h1", {"class": h1_class})
                
                try:
                    title_ele =l_soup.find("span", {"class": "seitenkopf__headline--text"})
                    title_text =title_ele.text
                    title_text=translate(title_text)
                    data.append(title_text)
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
                    date_ele = l_soup.findAll("article", {"class": "container content-wrapper__group"})[-1]
                    date_text = date_ele.text
                    date_text=translate(date_text)
                    date_text=date_text.strip("\n")
                    l=date_text.split("\n")
                    date_text=l[5].strip(" ")
                    l1=date_text.split(" ")
                    l=l1[1].split(".")
                    date_text=l[0]+"-"+l[1]+"-"+l[2]

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
                   para_ele = l_soup.findAll("article", {"class": "container content-wrapper__group"})[-1]
                   para_text = para_ele.text
                   para_text=translate(para_text)
                   data.append(para_text)  # Need to make this better
                except:
                    err["link"]=link
                    err['text']="Error"
                    data.append("-")
                    flag=1
                  # drops the complete data if there is an error
                # Adding data to a collection
                
                if flag==1:
                    Errors["tagesschau"].append(err)
                
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
            emptydataframe("tagesschau", df)
            # df  = link_correction(df)
            
            return df
        
        except:
            not_working_functions.append("tagesschau")
            print("tagesschau not working")

    def afr(keyword):
        try:
            print("afr")
            Errors["afr"]=[]
            
          
            url = f"https://www.afr.com/search?text={keyword}"
            domain_url = "https://www.afr.com/"
            headers = {
                "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10.15; rv:78.0) Gecko/20100101 Firefox/78.0",
                "accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.9",
                'sec-fetch-site': 'none',
                'sec-fetch-mode': 'navigate',
                'sec-fetch-user': '?1',
                'sec-fetch-dest': 'document',
                'accept-language': 'en-GB,en-US;q=0.9,en;q=0.8',
            }

            links=[]
            try:
                page = requests.get(url, headers=headers)
                soup = BeautifulSoup(page.content, "html.parser")
            except:
                print("afr not working")
                not_working_functions.append('afr')
                err = "Main link did not load: " + url
                Errors["afr"].append(err)
                return
            
            
            try:
                all_divs = soup.find_all("a", {"class": "_20-Rx"})
                for div in all_divs:
                    links.append(domain_url+div["href"])
            except:
                if len(links)==0:
                    print("afr not working")
                    not_working_functions.append('afr')
                    Errors["afr"].append("Extraction of link not working.")
                    return
                        
            # Remove duplicates
            links = list(set(links))
            
            # links # Debugging - if link array is generated
            collection = []
            scrapper_name = "afr"
            
            def getarticles(link):
                
                flag=0
                err=err_dict()
                try:
                    l_page = requests.get(link, headers=headers)
                    l_soup = BeautifulSoup(l_page.content, 'html.parser')
                except:
                    err["link"]="Link not working: "+link
                    Errors["afr"].append(err)
                    return
                
                data = []
                
                # Scraping the heading
                #h1_ele = l_soup.find("h1", {"class": h1_class})
                
                try:
                    title_ele =l_soup.find("h1", {"class": "_3lFzE"})
                    title_text = title_ele.text
                    
                    data.append(title_text)
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
                    l=link.split('-')
                    l2=l[-2]
                    date_text=l2[6:8]+"-"+l2[4:6]+"-"+l2[0:4]

                    
                    

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
                   para_ele = l_soup.findAll("div", {"class": "tl7wu"})[-1]
                   para_text = para_ele.text
                   
                   data.append(para_text)  # Need to make this better
                except:
                    err["link"]=link
                    err['text']="Error"
                    data.append("-")
                    flag=1
                  # drops the complete data if there is an error
                # Adding data to a collection
                
                if flag==1:
                    Errors["afr"].append(err)
                
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
            emptydataframe("afr", df)
            # df  = link_correction(df)
            
            return df
        
        except:
            not_working_functions.append("afr")
            print("afr not working")

    def asiainsurancereview(keyword):
        try:
            print("asiainsurancereview")
            Errors["asiainsurancereview"]=[]
            
          
            url = f"https://www.asiainsurancereview.com/Search?search_key={keyword}"
            domain_url = "https://www.asiainsurancereview.com"
            headers = {
                "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10.15; rv:78.0) Gecko/20100101 Firefox/78.0",
                "accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.9",
                'sec-fetch-site': 'none',
                'sec-fetch-mode': 'navigate',
                'sec-fetch-user': '?1',
                'sec-fetch-dest': 'document',
                'accept-language': 'en-GB,en-US;q=0.9,en;q=0.8',
            }
            div_class = "items"
            h1_class = "main-title"
            date_div_class = "newsDetailBox"
            para_div_class = "article-wrap"

            links=[]
            try:
                page = requests.get(url, headers=headers)
                soup = BeautifulSoup(page.content, "html.parser")
            except:
                print("asiainsurancereview not working")
                not_working_functions.append('asiainsurancereview')
                err = "Main link did not load: " + url
                Errors["asiainsurancereview"].append(err)
                return
            
            
            try:
                for divtag in soup.find_all("li", {"class": div_class}):
                    for a in divtag.find_all("a", href=True):
                        link = a["href"]  # Gets the link

                        # Checking the link if it is a relative link
                        if link[0] == '/':
                            link = domain_url + link

                        links.append(link)
            except:
                if len(links)==0:
                    print("asiainsurancereview not working")
                    not_working_functions.append('asiainsurancereview')
                    Errors["asiainsurancereview"].append("Extraction of link not working.")
                    return
                        
            # Remove duplicates
            links = list(set(links))
            
            # links # Debugging - if link array is generated
            collection = []
            scrapper_name = "asiainsurancereview"
            
            def getarticles(link):
                
                flag=0
                err=err_dict()
                try:
                    l_page = requests.get(link, headers=headers)
                    l_soup = BeautifulSoup(l_page.content, 'html.parser')
                except:
                    err["link"]="Link not working: "+link
                    Errors["asiainsurancereview"].append(err)
                    return
                
                data = []
                
                # Scraping the heading
                #h1_ele = l_soup.find("h1", {"class": h1_class})
                
                try:
                    title_ele =l_soup.find("h1", {"class": h1_class})
                    title_text = title_ele.text
                    
                    data.append(title_text)
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
                    date_ele =l_soup.find("div", {"class": date_div_class})
                    date_text = date_ele.text
                    date_text=date_text.strip("\n")
                    l=date_text.split("\n")
                    l1=l[0].split(" ")
                    l2=l1[-3]
                    date_text=l2[-2]+l2[-1]+"-"+l1[-2]+"-"+l1[-1]
                    
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
                   para_ele = l_soup.findAll("div", {"class": para_div_class})[-1]
                   para_text = para_ele.text
                   
                   data.append(para_text)  # Need to make this better
                except:
                    err["link"]=link
                    err['text']="Error"
                    data.append("-")
                    flag=1
                  # drops the complete data if there is an error
                # Adding data to a collection
                
                if flag==1:
                    Errors["asiainsurancereview"].append(err)
                
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
            emptydataframe("asiainsurancereview", df)
            # df  = link_correction(df)
            
            return df
        
        except:
            not_working_functions.append("asiainsurancereview")
            print("asiainsurancereview not working")

    def swissinfo(keyword):
        try:
            print("swissinfo")
            Errors["swissinfo"]=[]
            
          
            url = f"https://www.swissinfo.ch/service/search/eng/45808844?query={keyword}"
            domain_url = "https://www.swissinfo.ch"
            headers = {
                "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10.15; rv:78.0) Gecko/20100101 Firefox/78.0",
                "accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.9",
                'sec-fetch-site': 'none',
                'sec-fetch-mode': 'navigate',
                'sec-fetch-user': '?1',
                'sec-fetch-dest': 'document',
                'accept-language': 'en-GB,en-US;q=0.9,en;q=0.8',
            }
            div_class = "items"
            h1_class = "main-title"
            date_div_class = "newsDetailBox"
            para_div_class = "article-wrap"

            links=[]
            try:
                page = requests.get(url, headers=headers)
                soup = BeautifulSoup(page.content, "html.parser")
            except:
                print("swissinfo not working")
                not_working_functions.append('swissinfo')
                err = "Main link did not load: " + url
                Errors["swissinfo"].append(err)
                return
            
            
            try:
                all_divs = soup.find_all("a", {"class": "si-teaser__link"})
                for div in all_divs:
                    links.append(domain_url+div["href"])
            except:
                if len(links)==0:
                    print("swissinfo not working")
                    not_working_functions.append('swissinfo')
                    Errors["swissinfo"].append("Extraction of link not working.")
                    return
                        
            # Remove duplicates
            links = list(set(links))
            
            # links # Debugging - if link array is generated
            collection = []
            scrapper_name = "swissinfo"
            
            def getarticles(link):
                
                flag=0
                err=err_dict()
                try:
                    l_page = requests.get(link, headers=headers)
                    l_soup = BeautifulSoup(l_page.content, 'html.parser')
                except:
                    err["link"]="Link not working: "+link
                    Errors["swissinfo"].append(err)
                    return
                
                data = []
                
                # Scraping the heading
                #h1_ele = l_soup.find("h1", {"class": h1_class})
                
                try:
                    title_ele =l_soup.find("h1", {"class": "si-detail__title"})
                    title_text = title_ele.text
                    
                    data.append(title_text)
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
                    date_ele =l_soup.find("time", {"class": "si-detail__date"})
                    date_text = date_ele.text
                    date_text=date_text.strip("\n")
                    l=date_text.split(" ")
                    date_text=l[1].strip(",")+"-"+l[0]+"-"+l[2]
                    
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
                   para_ele = l_soup.findAll("section", {"class": "si-detail__content"})[-1]
                   para_text = para_ele.text
                   
                   data.append(para_text)  # Need to make this better
                except:
                    err["link"]=link
                    err['text']="Error"
                    data.append("-")
                    flag=1
                  # drops the complete data if there is an error
                # Adding data to a collection
                
                if flag==1:
                    Errors["swissinfo"].append(err)
                
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
            emptydataframe("swissinfo", df)
            # df  = link_correction(df)
            
            return df
        
        except:
            not_working_functions.append("swissinfo")
            print("swissinfo not working")
        
    
    def jamaicaobserver(keyword):
        try:
            print("jamaicaobserver")
            Errors["jamaicaobserver"]=[]
            
          
            url = f"https://www.jamaicaobserver.com/search/?q={keyword}"
            domain_url = "https://www.jamaicaobserver.com"
            headers = {
                "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10.15; rv:78.0) Gecko/20100101 Firefox/78.0",
                "accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.9",
                'sec-fetch-site': 'none',
                'sec-fetch-mode': 'navigate',
                'sec-fetch-user': '?1',
                'sec-fetch-dest': 'document',
                'accept-language': 'en-GB,en-US;q=0.9,en;q=0.8',
            }
            links=[]
            try:
                page = requests.get(url, headers=headers)
                soup = BeautifulSoup(page.content, "html.parser")
            except:
                print("jamaicaobserver not working")
                not_working_functions.append('jamaicaobserver')
                err = "Main link did not load: " + url
                Errors["jamaicaobserver"].append(err)
                return
            
            
            try:
                all_divs = soup.find_all("div", {"class": "entry-title"})
                for div in all_divs:
                   links.append(div.a["href"])
            except:
                if len(links)==0:
                    print("jamaicaobserver not working")
                    not_working_functions.append('jamaicaobserver')
                    Errors["jamaicaobserver"].append("Extraction of link not working.")
                    return
                        
            # Remove duplicates
            links = list(set(links))
            
            # links # Debugging - if link array is generated
            collection = []
            scrapper_name = "jamaicaobserver"
            
            def getarticles(link):
                
                flag=0
                err=err_dict()
                try:
                    l_page = requests.get(link, headers=headers)
                    l_soup = BeautifulSoup(l_page.content, 'html.parser')
                except:
                    err["link"]="Link not working: "+link
                    Errors["jamaicaobserver"].append(err)
                    return
                
                data = []
                
                # Scraping the heading
                #h1_ele = l_soup.find("h1", {"class": h1_class})
                
                try:
                    title_ele =l_soup.find("div", {"class": "headline col-12"})
                    title_text = title_ele.text
                    
                    data.append(title_text)
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
                    date_ele =l_soup.find("div", {"class": "article-pubdate"})
                    date_text = date_ele.text
                    date_text=date_text.strip("\n")
                    date_text=date_text.strip(" ")
                    l=date_text.split(" ")
                    date_text=l[1].strip(",")+"-"+l[0]+"-"+l[2]
            
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
                   para_ele = l_soup.findAll("div", {"class": "article-restofcontent"})[-1]
                   para_text = para_ele.text
                   
                   data.append(para_text)  # Need to make this better
                except:
                    err["link"]=link
                    err['text']="Error"
                    data.append("-")
                    flag=1
                  # drops the complete data if there is an error
                # Adding data to a collection
                
                if flag==1:
                    Errors["jamaicaobserver"].append(err)
                
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
            emptydataframe("jamaicaobserver", df)
            # df  = link_correction(df)
            
            return df
        
        except:
            not_working_functions.append("jamaicaobserver")
            print("jamaicaobserver not working")

    def energyvoice(keyword):
        try:
            print("energyvoice")
            Errors["energyvoice"]=[]
            
          
            url = f"https://www.energyvoice.com/?s={keyword}"
            domain_url = "https://www.energyvoice.com"
            headers = {
                "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10.15; rv:78.0) Gecko/20100101 Firefox/78.0",
                "accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.9",
                'sec-fetch-site': 'none',
                'sec-fetch-mode': 'navigate',
                'sec-fetch-user': '?1',
                'sec-fetch-dest': 'document',
                'accept-language': 'en-GB,en-US;q=0.9,en;q=0.8',
            }
            links=[]
            try:
                page = requests.get(url, headers=headers)
                soup = BeautifulSoup(page.content, "html.parser")
            except:
                print("energyvoice not working")
                not_working_functions.append('energyvoice')
                err = "Main link did not load: " + url
                Errors["energyvoice"].append(err)
                return
            
            
            try:
                all_divs = soup.find_all("h2", {"class": "title title--sm"})
                for div in all_divs:
                    links.append(div.a["href"])
            except:
                if len(links)==0:
                    print("energyvoice not working")
                    not_working_functions.append('energyvoice')
                    Errors["energyvoice"].append("Extraction of link not working.")
                    return
                        
            # Remove duplicates
            links = list(set(links))
            
            # links # Debugging - if link array is generated
            collection = []
            scrapper_name = "energyvoice"
            
            def getarticles(link):
                
                flag=0
                err=err_dict()
                try:
                    l_page = requests.get(link, headers=headers)
                    l_soup = BeautifulSoup(l_page.content, 'html.parser')
                except:
                    err["link"]="Link not working: "+link
                    Errors["energyvoice"].append(err)
                    return
                
                data = []
                
                # Scraping the heading
                #h1_ele = l_soup.find("h1", {"class": h1_class})
                
                try:
                    title_ele =l_soup.find("h1", {"class": "title entry-title"})
                    title_text = title_ele.text
                    
                    data.append(title_text)
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
                    date_ele =l_soup.find("span", {"class": "post-timestamp__published"})
                    date_text = date_ele.text
                    l=date_text.split(" ")
                    l1=l[0].split("/")
                    date_text=l1[0]+"-"+l1[1]+"-"+l1[2].strip(",")
            
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
                   para_ele = l_soup.findAll("div", {"class": "cms clearfix"})[-1]
                   para_text = para_ele.text
                   
                   data.append(para_text)  # Need to make this better
                except:
                    err["link"]=link
                    err['text']="Error"
                    data.append("-")
                    flag=1
                  # drops the complete data if there is an error
                # Adding data to a collection
                
                if flag==1:
                    Errors["energyvoice"].append(err)
                
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
            emptydataframe("energyvoice", df)
            # df  = link_correction(df)
            
            return df
        
        except:
            not_working_functions.append("energyvoice")
            print("energyvoice not working")


    def african_markets(keyword):
        try:
            print("african_markets")
            Errors["african_markets"]=[]
            
          
            url = f"https://www.african-markets.com/en/search?searchword={keyword}&ordering=newest&searchphrase=all&limit=0"
            domain_url = "https://www.african-markets.com/"
            headers = {
                "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10.15; rv:78.0) Gecko/20100101 Firefox/78.0",
                "accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.9",
                'sec-fetch-site': 'none',
                'sec-fetch-mode': 'navigate',
                'sec-fetch-user': '?1',
                'sec-fetch-dest': 'document',
                'accept-language': 'en-GB,en-US;q=0.9,en;q=0.8',
            }
            dt_class = "result-title"  # Class name of div containing the a tag
            #h1_class = "_1Y-96"
            #h1_div_class = "col-xs-12"
            title_div_class = "page-header"
            date_time_itemprop = ["datePublished"]
            para_div_itemprop = ["articleBody"]
            links=[]
            try:
                page = requests.get(url, headers=headers)
                soup = BeautifulSoup(page.content, "html.parser")
            except:
                print("african_markets not working")
                not_working_functions.append('african_markets')
                err = "Main link did not load: " + url
                Errors["african_markets"].append(err)
                return
            
            
            try:
                
                for divtag in soup.find_all("dt", {"class": dt_class}):
                    for a in divtag.find_all("a", href=True):
                        link = a["href"]  # Gets the link

                        # Checking the link if it is a relative link
                        if link[0] == '/':
                            link = domain_url + link[1:]

                        # Filtering advertaisment links
                        link_start = domain_url
                        if link.startswith(link_start):
                            links.append(link)
                # Remove duplicates
                links = list(set(links))
            except:
                if len(links)==0:
                    print("african_markets not working")
                    not_working_functions.append('african_markets')
                    Errors["african_markets"].append("Extraction of link not working.")
                    return
                        
            # Remove duplicates
            links = list(set(links))
            
            # links # Debugging - if link array is generated
            collection = []
            scrapper_name = "african_markets"
            
            def getarticles(link):
                
                flag=0
                err=err_dict()
                try:
                    l_page = requests.get(link, headers=headers)
                    l_soup = BeautifulSoup(l_page.content, 'html.parser')
                except:
                    err["link"]="Link not working: "+link
                    Errors["african_markets"].append(err)
                    return
                
                data = []
                
                # Scraping the heading
                #h1_ele = l_soup.find("h1", {"class": h1_class})
                
                try:
                    title_ele =l_soup.find("div", {"class": title_div_class})
                    title_text = title_ele.text
                    
                    data.append(title_text)
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
                    date_ele =l_soup.find("time", {"itemprop": date_time_itemprop})
                    date_text = date_ele.text
                    date_text=date_text.strip("\n")
                    l=date_text.split(" ")
                    date_text=l[2].strip(",")+"-"+l[1]+"-"+l[3]
            
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
                   para_ele = l_soup.findAll("div", {"itemprop": para_div_itemprop})[-1]
                   para_text = para_ele.text
                   
                   data.append(para_text)  # Need to make this better
                except:
                    err["link"]=link
                    err['text']="Error"
                    data.append("-")
                    flag=1
                  # drops the complete data if there is an error
                # Adding data to a collection
                
                if flag==1:
                    Errors["african_markets"].append(err)
                
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
            emptydataframe("african_markets", df)
            # df  = link_correction(df)
            
            return df
        
        except:
            not_working_functions.append("african_markets")
            print("african_markets not working")

    def newindianexpress(keyword):
        try:
            print("newindianexpress")
            Errors["newindianexpress"]=[]
            
          
            url = f"https://www.newindianexpress.com/topic?term={keyword}&request=ALL&search=short"
            domain_url = "https://www.newindianexpress.com/"
            headers = {
                "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10.15; rv:78.0) Gecko/20100101 Firefox/78.0",
                "accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.9",
                'sec-fetch-site': 'none',
                'sec-fetch-mode': 'navigate',
                'sec-fetch-user': '?1',
                'sec-fetch-dest': 'document',
                'accept-language': 'en-GB,en-US;q=0.9,en;q=0.8',
            }
            div_class = "search-row_type"  # Class name of div containing the a tag
            #h1_class = "_1Y-96"
            #h1_div_class = "col-xs-12"
            title_h1_class = "ArticleHead"
            date_p_class = ["ArticlePublish margin-bottom-10"]
            para_div_id = ["wholeContent"]
            links=[]
            try:
                page = requests.get(url, headers=headers)
                soup = BeautifulSoup(page.content, "html.parser")
            except:
                print("newindianexpress not working")
                not_working_functions.append('newindianexpress')
                err = "Main link did not load: " + url
                Errors["newindianexpress"].append(err)
                return
            
            
            try:
                
                for divtag in soup.find_all("div", {"class": div_class}):
                    for a in divtag.find_all("a", href=True):
                        link = a["href"]  # Gets the link

                        # Checking the link if it is a relative link
                        if link[0] == '/':
                            link = domain_url + link

                        # Filtering advertaisment links
                        link_start = domain_url
                        if link.startswith(link_start):
                            links.append(link)
                # Remove duplicates
                links = list(set(links))
            except:
                if len(links)==0:
                    print("newindianexpress not working")
                    not_working_functions.append('newindianexpress')
                    Errors["newindianexpress"].append("Extraction of link not working.")
                    return
                        
            # Remove duplicates
            links = list(set(links))
            
            # links # Debugging - if link array is generated
            collection = []
            scrapper_name = "newindianexpress"
            
            def getarticles(link):
                
                flag=0
                err=err_dict()
                try:
                    l_page = requests.get(link, headers=headers)
                    l_soup = BeautifulSoup(l_page.content, 'html.parser')
                except:
                    err["link"]="Link not working: "+link
                    Errors["newindianexpress"].append(err)
                    return
                
                data = []
                
                # Scraping the heading
                #h1_ele = l_soup.find("h1", {"class": h1_class})
                
                try:
                    title_ele =l_soup.find("h1", {"class": title_h1_class})
                    title_text = title_ele.text
                    
                    data.append(title_text)
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
                    date_ele =l_soup.find("p", {"class": date_p_class})
                    date_text = date_ele.text
                    date_text=date_text.strip("\n")
                    l=date_text.split(" ")
                    date_text=l[8][0:2]+"-"+l[10]+"-"+l[11]


                   
            
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
                   para_ele = l_soup.findAll("div", {"id": para_div_id})[-1]
                   para_text = para_ele.text
                   
                   data.append(para_text)  # Need to make this better
                except:
                    err["link"]=link
                    err['text']="Error"
                    data.append("-")
                    flag=1
                  # drops the complete data if there is an error
                # Adding data to a collection
                
                if flag==1:
                    Errors["newindianexpress"].append(err)
                
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
            emptydataframe("newindianexpress", df)
            # df  = link_correction(df)
            
            return df
        
        except:
            not_working_functions.append("newindianexpress")
            print("newindianexpress not working")

    def ndtv(keyword):
        try:
            print("ndtv")
            Errors["ndtv"]=[]
            
          
            url = f"https://www.ndtv.com/search?searchtext={keyword}"
            domain_url = "https://www.ndtv.com/"
            headers = {
                "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10.15; rv:78.0) Gecko/20100101 Firefox/78.0",
                "accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.9",
                'sec-fetch-site': 'none',
                'sec-fetch-mode': 'navigate',
                'sec-fetch-user': '?1',
                'sec-fetch-dest': 'document',
                'accept-language': 'en-GB,en-US;q=0.9,en;q=0.8',
            }
            ul_class = "src_lst-ul"  # Class name of div containing the a tag
            #h1_class = "_1Y-96"
            #h1_div_class = "col-xs-12"
            title_h1_class = "sp-ttl"
            date_span_itemprop = ["dateModified"]
            para_div_itemprop = ["articleBody"]
            links=[]
            try:
                page = requests.get(url, headers=headers)
                soup = BeautifulSoup(page.content, "html.parser")
            except:
                print("ndtv not working")
                not_working_functions.append('ndtv')
                err = "Main link did not load: " + url
                Errors["ndtv"].append(err)
                return
            
            
            try:
                
                for divtag in soup.find_all("ul", {"class": ul_class}):
                    for a in divtag.find_all("a", href=True):
                        link = a["href"]  # Gets the link

                        # Checking the link if it is a relative link
                        if link[0] == '/':
                            link = domain_url + link

                        # Filtering advertaisment links
                        link_start = domain_url
                        if link.startswith(link_start):
                            links.append(link)
                # Remove duplicates
                links = list(set(links))
            except:
                if len(links)==0:
                    print("ndtv not working")
                    not_working_functions.append('ndtv')
                    Errors["ndtv"].append("Extraction of link not working.")
                    return
                        
            # Remove duplicates
            links = list(set(links))
            
            # links # Debugging - if link array is generated
            collection = []
            scrapper_name = "ndtv"
            
            def getarticles(link):
                
                flag=0
                err=err_dict()
                try:
                    l_page = requests.get(link, headers=headers)
                    l_soup = BeautifulSoup(l_page.content, 'html.parser')
                except:
                    err["link"]="Link not working: "+link
                    Errors["ndtv"].append(err)
                    return
                
                data = []
                
                # Scraping the heading
                #h1_ele = l_soup.find("h1", {"class": h1_class})
                
                try:
                    title_ele =l_soup.find("h1", {"class": title_h1_class})
                    title_text = title_ele.text
                    
                    data.append(title_text)
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
                    date_ele =l_soup.find("span", {"itemprop": date_span_itemprop})
                    date_text = date_ele.text
                    date_text=date_text.strip("\n")
                    l=date_text.split(" ")
                    date_text=l[2].strip(",")+"-"+l[1]+"-"+l[3]
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
                   para_ele = l_soup.findAll("div", {"itemprop": para_div_itemprop})[-1]
                   para_text = para_ele.text
                   
                   data.append(para_text)  # Need to make this better
                except:
                    err["link"]=link
                    err['text']="Error"
                    data.append("-")
                    flag=1
                  # drops the complete data if there is an error
                # Adding data to a collection
                
                if flag==1:
                    Errors["ndtv"].append(err)
                
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
            emptydataframe("ndtv", df)
            # df  = link_correction(df)
            
            return df
        
        except:
            not_working_functions.append("ndtv")
            print("ndtv not working")


    def theepochtimes(keyword):
        try:
            print("theepochtimes")
            Errors["theepochtimes"]=[]
            
          
            url = f"https://www.theepochtimes.com/search/?q={keyword}&t=ai"
            domain_url = "https://www.theepochtimes.com/"
            headers = {
                "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10.15; rv:78.0) Gecko/20100101 Firefox/78.0",
                "accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.9",
                'sec-fetch-site': 'none',
                'sec-fetch-mode': 'navigate',
                'sec-fetch-user': '?1',
                'sec-fetch-dest': 'document',
                'accept-language': 'en-GB,en-US;q=0.9,en;q=0.8',
            }
            li_class = "post_list"  # Class name of div containing the a tag
            #h1_class = "_1Y-96"
            #h1_div_class = "col-xs-12"
            title_div_class = "title"
            date_span_class = ["time"]
            para_div_class = ["post_content"]
            links=[]
            try:
                page = requests.get(url, headers=headers)
                soup = BeautifulSoup(page.content, "html.parser")
            except:
                print("theepochtimes not working")
                not_working_functions.append('theepochtimes')
                err = "Main link did not load: " + url
                Errors["theepochtimes"].append(err)
                return
            
            
            try:
                
                for divtag in soup.find_all("li", {"class": li_class}):
                    for a in divtag.find_all("a", href=True):
                        link = a["href"]  # Gets the link

                        # Checking the link if it is a relative link
                        if link[0] == '/':
                            link = domain_url + link

                        # Filtering advertaisment links
                        link_start = domain_url
                        if link.startswith(link_start):
                            links.append(link)
                # Remove duplicates
                links = list(set(links))
            except:
                if len(links)==0:
                    print("theepochtimes not working")
                    not_working_functions.append('theepochtimes')
                    Errors["theepochtimes"].append("Extraction of link not working.")
                    return
                        
            # Remove duplicates
            links = list(set(links))
            
            # links # Debugging - if link array is generated
            collection = []
            scrapper_name = "theepochtimes"
            
            def getarticles(link):
                
                flag=0
                err=err_dict()
                try:
                    l_page = requests.get(link, headers=headers)
                    l_soup = BeautifulSoup(l_page.content, 'html.parser')
                except:
                    err["link"]="Link not working: "+link
                    Errors["theepochtimes"].append(err)
                    return
                
                data = []
                
                # Scraping the heading
                #h1_ele = l_soup.find("h1", {"class": h1_class})
                
                try:
                    title_ele =l_soup.find("h1")
                    title_text = title_ele.text
                    
                    data.append(title_text)
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
                    date_ele =l_soup.find("span", {"class": "publish"})
                    date_text = date_ele.text
                    date_text=date_text.strip("\n")
                    l=date_text.split(" ")
                    date_text=l[1].strip(",")+"-"+l[0]+"-"+l[2]
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
                   para_ele = l_soup.findAll("div", {"class": para_div_class})[-1]
                   para_text = para_ele.text
                   
                   data.append(para_text)  # Need to make this better
                except:
                    err["link"]=link
                    err['text']="Error"
                    data.append("-")
                    flag=1
                  # drops the complete data if there is an error
                # Adding data to a collection
                
                if flag==1:
                    Errors["theepochtimes"].append(err)
                
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
            emptydataframe("theepochtimes", df)
            # df  = link_correction(df)
            
            return df
        
        except:
            not_working_functions.append("theepochtimes")
            print("theepochtimes not working")

    def malaymail(keyword):
        try:
            print("malaymail")
            Errors["malaymail"]=[]
            
          
            url = f"https://www.malaymail.com/search?query={keyword}"
            domain_url = "https://www.malaymail.com/"
            headers = {
                "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10.15; rv:78.0) Gecko/20100101 Firefox/78.0",
                "accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.9",
                'sec-fetch-site': 'none',
                'sec-fetch-mode': 'navigate',
                'sec-fetch-user': '?1',
                'sec-fetch-dest': 'document',
                'accept-language': 'en-GB,en-US;q=0.9,en;q=0.8',
            }
            div_class="col-md-3 article-item"# Class name of div containing the a tag
            
            title_h1_class="article-title"
            date_div_class="article-date"
            para_div_class=["article-body"]
            links=[]
            try:
                page = requests.get(url, headers=headers)
                soup = BeautifulSoup(page.content, "html.parser")
            except:
                print("malaymail not working")
                not_working_functions.append('malaymail')
                err = "Main link did not load: " + url
                Errors["malaymail"].append(err)
                return
            
            
            try:
                
                all_divs = soup.find_all("div", {"class": div_class})

                for div in all_divs:
                    links.append(div.a["href"])
            except:
                if len(links)==0:
                    print("malaymail not working")
                    not_working_functions.append('malaymail')
                    Errors["malaymail"].append("Extraction of link not working.")
                    return
                        
            # Remove duplicates
            links = list(set(links))
            
            # links # Debugging - if link array is generated
            collection = []
            scrapper_name = "malaymail"
            
            def getarticles(link):
                
                flag=0
                err=err_dict()
                try:
                    l_page = requests.get(link, headers=headers)
                    l_soup = BeautifulSoup(l_page.content, 'html.parser')
                except:
                    err["link"]="Link not working: "+link
                    Errors["malaymail"].append(err)
                    return
                
                data = []
                
                # Scraping the heading
                #h1_ele = l_soup.find("h1", {"class": h1_class})
                
                try:
                    title_ele =l_soup.find("h1",{"class":title_h1_class})
                    title_text = title_ele.text
                    
                    data.append(title_text)
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
                    date_ele =l_soup.find("div",{"class":date_div_class})
                    date_text = date_ele.text
                    date_text=date_text.strip("\n")
                    l=date_text.split(" ")
                    date_text=l[1]+"-"+l[2]+"-"+l[3]
                    
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
                   para_ele = l_soup.findAll("div", {"class": para_div_class})[-1]
                   para_text = para_ele.text
                   
                   data.append(para_text)  # Need to make this better
                except:
                    err["link"]=link
                    err['text']="Error"
                    data.append("-")
                    flag=1
                  # drops the complete data if there is an error
                # Adding data to a collection
                
                if flag==1:
                    Errors["malaymail"].append(err)
                
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
            emptydataframe("malaymail", df)
            # df  = link_correction(df)
            
            return df
        
        except:
            not_working_functions.append("malaymail")
            print("malaymail not working")


    def nbdpress(keyword):
        try:
            print("nbdpress")
            Errors["nbdpress"]=[]
            
          
            url = f"http://www.nbdpress.com/search/article_search?q={keyword}"
            domain_url = "http://www.nbdpress.com/"
            headers = {
                "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10.15; rv:78.0) Gecko/20100101 Firefox/78.0",
                "accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.9",
                'sec-fetch-site': 'none',
                'sec-fetch-mode': 'navigate',
                'sec-fetch-user': '?1',
                'sec-fetch-dest': 'document',
                'accept-language': 'en-GB,en-US;q=0.9,en;q=0.8',
            }
            date_span_class="date"
            para_div_class=["article-text"]
            links=[]
            try:
                page = requests.get(url, headers=headers)
                soup = BeautifulSoup(page.content, "html.parser")
            except:
                print("nbdpress not working")
                not_working_functions.append('nbdpress')
                err = "Main link did not load: " + url
                Errors["nbdpress"].append(err)
                return
            
            
            try:
                
                all_divs = soup.find_all("li")

                for div in all_divs:
                    links.append(div.a["href"])
            except:
                if len(links)==0:
                    print("nbdpress not working")
                    not_working_functions.append('nbdpress')
                    Errors["nbdpress"].append("Extraction of link not working.")
                    return
                        
            # Remove duplicates
            links = list(set(links))
            
            # links # Debugging - if link array is generated
            collection = []
            scrapper_name = "nbdpress"
            
            def getarticles(link):
                
                flag=0
                err=err_dict()
                try:
                    l_page = requests.get(link, headers=headers)
                    l_soup = BeautifulSoup(l_page.content, 'html.parser')
                except:
                    err["link"]="Link not working: "+link
                    Errors["nbdpress"].append(err)
                    return
                
                data = []
                
                # Scraping the heading
                #h1_ele = l_soup.find("h1", {"class": h1_class})
                
                try:
                    title_ele =l_soup.find("h3")
                    title_text = title_ele.text
                    
                    data.append(title_text)
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
                    date_ele =l_soup.find("span",{"class":date_span_class})
                    date_text = date_ele.text
                    date_text=date_text.strip("\n")
                    date_text=date_text.strip(" ")
                    l=date_text.split(",")
                    date_text=l[0]+"-"+l[1]+"-"+l[2]
                    
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
                   para_ele = l_soup.findAll("div", {"class": para_div_class})[-1]
                   para_text = para_ele.text
                   
                   data.append(para_text)  # Need to make this better
                except:
                    err["link"]=link
                    err['text']="Error"
                    data.append("-")
                    flag=1
                  # drops the complete data if there is an error
                # Adding data to a collection
                
                if flag==1:
                    Errors["nbdpress"].append(err)
                
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
            emptydataframe("nbdpress", df)
            # df  = link_correction(df)
            
            return df
        
        except:
            not_working_functions.append("nbdpress")
            print("nbdpress not working")
            
    
    def gulftoday(keyword):
        try:
            print("gulftoday")
            Errors["gulftoday"]=[]
            
          
            url = f"https://www.gulftoday.ae/search-results?tag=&search={keyword}&sorting=2&date=&removeDate=no"
            domain_url = "https://www.gulftoday.ae"
            headers = {
                "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10.15; rv:78.0) Gecko/20100101 Firefox/78.0",
                "accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.9",
                'sec-fetch-site': 'none',
                'sec-fetch-mode': 'navigate',
                'sec-fetch-user': '?1',
                'sec-fetch-dest': 'document',
                'accept-language': 'en-GB,en-US;q=0.9,en;q=0.8',
            }
            
            links=[]
            try:
                page = requests.get(url, headers=headers)
                soup = BeautifulSoup(page.content, "html.parser")
            except:
                print("gulftoday not working")
                not_working_functions.append('gulftoday')
                err = "Main link did not load: " + url
                Errors["gulftoday"].append(err)
                return
            
            
            try:
                
                all_divs = soup.find_all("a", {"class": "result-card"})

                for div in all_divs:
                    links.append(domain_url+div["href"])
            except:
                if len(links)==0:
                    print("gulftoday not working")
                    not_working_functions.append('gulftoday')
                    Errors["gulftoday"].append("Extraction of link not working.")
                    return
                        
            # Remove duplicates
            links = list(set(links))
            
            # links # Debugging - if link array is generated
            collection = []
            scrapper_name = "gulftoday"
            
            def getarticles(link):
                
                flag=0
                err=err_dict()
                try:
                    l_page = requests.get(link, headers=headers)
                    l_soup = BeautifulSoup(l_page.content, 'html.parser')
                except:
                    err["link"]="Link not working: "+link
                    Errors["gulftoday"].append(err)
                    return
                
                data = []
                
                # Scraping the heading
                #h1_ele = l_soup.find("h1", {"class": h1_class})
                
                try:
                    title_ele =l_soup.find("h1")
                    title_text = title_ele.text
                    
                    data.append(title_text)
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
                    l=link.split("/")
                    date_text=l[6]+"-"+l[5]+"-"+l[4]
                    
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
                   para_ele = l_soup.findAll("div",{"class":"uk-width-expand gt-article-container"})[-1]
                   para_text = para_ele.text
                   
                   data.append(para_text)  # Need to make this better
                except:
                    err["link"]=link
                    err['text']="Error"
                    data.append("-")
                    flag=1
                  # drops the complete data if there is an error
                # Adding data to a collection
                
                if flag==1:
                    Errors["gulftoday"].append(err)
                
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
            emptydataframe("gulftoday", df)
            # df  = link_correction(df)
            
            return df
        
        except:
            not_working_functions.append("gulftoday")
            print("gulftoday not working")

    def emirates247(keyword):
        try:
            print("emirates247")
            Errors["emirates247"]=[]
            
          
            url = f"https://www.emirates247.com/search-7.117?s=d&q={keyword}"
            domain_url = "https://www.emirates247.com/"
            headers = {
                "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10.15; rv:78.0) Gecko/20100101 Firefox/78.0",
                "accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.9",
                'sec-fetch-site': 'none',
                'sec-fetch-mode': 'navigate',
                'sec-fetch-user': '?1',
                'sec-fetch-dest': 'document',
                'accept-language': 'en-GB,en-US;q=0.9,en;q=0.8',
            }
            
            links=[]
            try:
                page = requests.get(url, headers=headers)
                soup = BeautifulSoup(page.content, "html.parser")
            except:
                print("emirates247 not working")
                not_working_functions.append('emirates247')
                err = "Main link did not load: " + url
                Errors["emirates247"].append(err)
                return
            
            
            try:
                
                for divtag in soup.find_all("li"):
                    for a in divtag.find_all("a", href=True):
                        link = a["href"]  # Gets the link

                                            # Checking the link if it is a relative link
                        if link[0] == '/':
                            link = domain_url + link

                                            # Filtering advertaisment links
                        link_start = domain_url
                        if link.startswith(link_start):
                            links.append(link)
                                    # Remove duplicates
                links = list(set(links))
            except:
                if len(links)==0:
                    print("emirates247 not working")
                    not_working_functions.append('emirates247')
                    Errors["emirates247"].append("Extraction of link not working.")
                    return
                        
            # Remove duplicates
            links = list(set(links))
            
            # links # Debugging - if link array is generated
            collection = []
            scrapper_name = "emirates247"
            
            def getarticles(link):
                
                flag=0
                err=err_dict()
                try:
                    l_page = requests.get(link, headers=headers)
                    l_soup = BeautifulSoup(l_page.content, 'html.parser')
                except:
                    err["link"]="Link not working: "+link
                    Errors["emirates247"].append(err)
                    return
                
                data = []
                
                # Scraping the heading
                #h1_ele = l_soup.find("h1", {"class": h1_class})
                
                try:
                    title_ele =l_soup.find("h1")
                    title_text = title_ele.text
                    
                    data.append(title_text)
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
                    l=link.split('.')
                    l1=l[2].split("-")
                    date_text=l1[-2]+"-"+l1[-3]+"-"+l1[-4]
                    
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
                   para_ele = l_soup.findAll("div", {"id": "articledetails"})[-1]
                   para_text = para_ele.text
                   
                   data.append(para_text)  # Need to make this better
                except:
                    err["link"]=link
                    err['text']="Error"
                    data.append("-")
                    flag=1
                  # drops the complete data if there is an error
                # Adding data to a collection
                
                if flag==1:
                    Errors["emirates247"].append(err)
                
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
            emptydataframe("emirates247", df)
            # df  = link_correction(df)
            
            return df
        
        except:
            not_working_functions.append("emirates247")
            print("emirates247 not working")


    def manilabulletin(keyword):
        try:
            print("manilabulletin")
            Errors["manilabulletin"]=[]
            
          
            url = f"https://mb.com.ph/?s={keyword}"
            domain_url = "https://mb.com.ph/"
            headers = {
                "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10.15; rv:78.0) Gecko/20100101 Firefox/78.0",
                "accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.9",
                'sec-fetch-site': 'none',
                'sec-fetch-mode': 'navigate',
                'sec-fetch-user': '?1',
                'sec-fetch-dest': 'document',
                'accept-language': 'en-GB,en-US;q=0.9,en;q=0.8',
            }
            
            links=[]
            try:
                page = requests.get(url, headers=headers)
                soup = BeautifulSoup(page.content, "html.parser")
            except:
                print("manilabulletin not working")
                not_working_functions.append('manilabulletin')
                err = "Main link did not load: " + url
                Errors["manilabulletin"].append(err)
                return
            
            
            try:
                
                for divtag in soup.find_all("li"):
                    for a in divtag.find_all("a", href=True):
                        link = a["href"]  # Gets the link

                        

                                            # Filtering advertaisment links
                        link_start = domain_url
                        if link.startswith(link_start):
                            links.append(link)
                                    # Remove duplicates
                links = list(set(links))
            except:
                if len(links)==0:
                    print("manilabulletin not working")
                    not_working_functions.append('manilabulletin')
                    Errors["manilabulletin"].append("Extraction of link not working.")
                    return
                        
            # Remove duplicates
            links = list(set(links))
            
            # links # Debugging - if link array is generated
            collection = []
            scrapper_name = "manilabulletin"
            
            def getarticles(link):
                
                flag=0
                err=err_dict()
                try:
                    l_page = requests.get(link, headers=headers)
                    l_soup = BeautifulSoup(l_page.content, 'html.parser')
                except:
                    err["link"]="Link not working: "+link
                    Errors["manilabulletin"].append(err)
                    return
                
                data = []
                
                # Scraping the heading
                #h1_ele = l_soup.find("h1", {"class": h1_class})
                
                try:
                    title_ele =l_soup.find("h2")
                    title_text = title_ele.text
                    
                    data.append(title_text)
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
                    l=link.split("/")
                    date_text=l[5]+"-"+l[4]+"-"+l[3]
                    
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
                   para_ele = l_soup.findAll("section", {"class": "article-content"})[-1]
                   para_text = para_ele.text
                   
                   data.append(para_text)  # Need to make this better
                except:
                    err["link"]=link
                    err['text']="Error"
                    data.append("-")
                    flag=1
                  # drops the complete data if there is an error
                # Adding data to a collection
                
                if flag==1:
                    Errors["manilabulletin"].append(err)
                
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
            emptydataframe("manilabulletin", df)
            # df  = link_correction(df)
            
            return df
        
        except:
            not_working_functions.append("manilabulletin")
            print("manilabulletin not working")

            

    def moneycontrol(keyword):
      
        try:
            print("moneycontrol")
            Errors["moneycontrol"]=[]
            url = f"https://www.moneycontrol.com/news/business/{keyword}/"
            
            domain_url = "https://moneycontrol.com/"
            
            li_class ="clearfix"
            date_div_class ="article_schedule"
            para_class ="content_wrapper arti-flow"
        
            headers = {
                "User-Agent": 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/108.0.0.0 Safari/537.36',
                "accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.9",
                'sec-fetch-site': 'none',
                'sec-fetch-mode': 'navigate',
                'sec-fetch-user': '?1',
                'sec-fetch-dest': 'document',
                'accept-language': 'en-GB,en-US;q=0.9,en;q=0.8',
            }

            links=[]
            
            try:
                page = requests.get(url, headers=headers)
                soup = BeautifulSoup(page.content, "html.parser")



            except:
                print("Moneycontrol  not working")
                not_working_functions.append('Moneycontrol')
                Errors["Moneycontrol"].append(err)
                err = "Main link did not load: " + url

                return
            
            try:
                section_id = soup.find("section", {"class":"mid-contener contener clearfix"})
                div_id = section_id.find("div",{"class": "fleft"})
                li_all= section_id.find_all("li", {"class":li_class}) 

                if (li_all !=None):
                    for li in li_all :
                        h2_tag = li.find("h2")
                        if (h2_tag != None):
                            a_link= h2_tag.find("a")
                            if(a_link  != None):
                                link=a_link['href']
                                #print("link", link)
                                links.append(link)
                links = list(set(links))
                
            except:
                if len(links)==0:
                    print("Money Control is  not working")
                    not_working_functions.append('moneycontrol')
                    Errors["moneycontrol"].append("Extraction of link not working.")
                    return
            
            links = list(set(links))
    
            collection = []
            scrapper_name = "moneycontrol"
        
            def getarticles(link):
                flag=0
                err=err_dict()
                try:
                    l_page = requests.get(link, headers=headers)
                    l_soup = BeautifulSoup(l_page.content, 'html.parser')
                except:
                    err["link"]="Link not working: "+link
                    Errors["moneycontrol"].append(err)
                    return 
                data = [] 

                #title
                try:
                    title_ele = l_soup.find("h1",{"class","article_title artTitle"})
                    title_text = title_ele.text
                    data.append(title_text)
                except:
                    err["link"]=link
                    err['title']="Error"
                    data.append("-")
                    flag=1
                
                
                
                data.append(link)   
                    
                #publish_date
                try:
                    date_ele =l_soup.find("div",{"class":date_div_class})
                    date_text = date_ele.text
                    date_text=date_text.strip("\n")
                    l=date_text.split(" ")
                    s=l[2].replace(",","")
                    date_text=s+"-"+l[1]+"-"+l[3]

                    data.append(date_text)
                    
                except:
                    err["link"]=link
                    err['published_date']="Error"
                    data.append("-")
                    flag=1
                
                #scrape_date
                today = date.today()
                cur_date = str(today)
                data.append(cur_date)
                
                #text
                try:
                    para_ele = l_soup.find("div", {"class": para_class})
                    text=""
                    p_tag = para_ele.find_all("p")
                    for p in p_tag:
                        para_text = para_ele.text
                        text =text + para_text
                    data.append(text)  
                except:
                    err["link"]=link
                    err['text']="Error"
                    data.append("-")
                    flag=1
                
                if flag==1:
                    Errors["moneycontrol"].append(err)
                
                collection.append(data)
            
            
            thread_list=[]
            length=len(links)
            for i in range(length):
                thread_list.append(threading.Thread(target=getarticles, args=(links[i], )))
            
            for thread in thread_list:
                thread.start()
            
            for thread in thread_list:
                thread.join()      
            
            df = pd.DataFrame(collection, columns=['title', 'link', 'publish_date', 'scraped_date', 'text'])
                
            df = FilterFunction(df)
            emptydataframe("moneycontrol", df)
            return df          

        except:
            print("Money control --  not working")
            not_working_functions.append('moneyControl')  
                    

    
    def businessoutreach(keyword):
        import requests
        import time
        from urllib.request import Request, urlopen
        from bs4 import BeautifulSoup
        from datetime import datetime,date
        import pandas as pd
        import threading
        try:
            print("businessoutreach")
            Errors["businessoutreach"]=[]
            
          
            url = f"https://www.businessoutreach.in/?s={keyword}"

            domain_url = "https://www.businessoutreach.in/"
            headers = {
                "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10.15; rv:78.0) Gecko/20100101 Firefox/78.0",
                "accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.9",
                'sec-fetch-site': 'none',
                'sec-fetch-mode': 'navigate',
                'sec-fetch-user': '?1',
                'sec-fetch-dest': 'document',
                'accept-language': 'en-GB,en-US;q=0.9,en;q=0.8',
            }
            
            links=[]
            try:
                page = requests.get(url, headers=headers)
                soup = BeautifulSoup(page.content, "html.parser")
            except:
                print("businessoutreach link not working")
                not_working_functions.append('businessoutreach')
                err = "Main link did not load: " + url
                Errors["businessoutreach"].append(err)
                return
            
            
            try:
                for divtag in soup.find_all("div",{"class":"postdetails"}):
                    for a in divtag.find_all("a", href=True):
                        link = a["href"]  # Gets the link

                                            # Filtering advertaisment links
                        link_start = domain_url
                        if link.startswith(link_start):
                            links.append(link)
                                    # Remove duplicates
                links = list(set(links))
            except:
                if len(links)==0:
                    print("businessoutreach  process link not working")
                    not_working_functions.append('businessoutreach')
                    Errors["businessoutreach"].append("Extraction of link not working.")
                    return
                        
            # Remove duplicates
            links = list(set(links))
            
            # links # Debugging - if link array is generated
            collection = []
            scrapper_name = "businessoutreach"
            
            def getarticles(link):
                
                flag=0
                err=err_dict()
                try:
                    l_page = requests.get(link, headers=headers)
                    l_soup = BeautifulSoup(l_page.content, 'html.parser')
                except:
                    err["link"]="Link not working: "+link
                    Errors["businessoutreach"].append(err)
                    return
                
                data = []
                
                
                # Scraping title
                
                try:
                    title_ele =l_soup.find("div",{"class","postmetadata"})
                    title_h1=title_ele.find("h1",{"class","font-tnr"})

                    title_text = title_h1.text
                    data.append(title_text)
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
                    post_date=l_soup.find("span",{"class", "postdate"})
                    post_date_text= post_date.text
                        
                    
                    l=post_date_text.split(" ")
                    s=l[2].replace(",","")
                    date_text=s+"-"+l[1]+"-"+l[3]
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
                    para_ele = l_soup.find("div", {"class": "postcontent relative"})
                    text=""
                    p_tag = para_ele.find_all("p")
                    for p in p_tag:
                        para_text = para_ele.text
                        text =text + para_text
                    data.append(para_text)  # Need to make this better
                except:
                    err["link"]=link
                    err['text']="Error"
                    data.append("-")
                    flag=1
                  # drops the complete data if there is an error
                # Adding data to a collection
                
                if flag==1:
                    Errors["businessoutreach"].append(err)
                
                collection.append(data)
                
           
            thread_list=[]
            length=len(links)
            for i in range(length):
                thread_list.append(threading.Thread(target=getarticles, args=(links[i], )))
            
            for thread in thread_list:
                thread.start()
            
            for thread in thread_list:
                thread.join()
            
            df = pd.DataFrame(collection, columns=['title', 'link', 'publish_date', 'scraped_date', 'text'])
            
            
            # print(df) # For debugging. To check if df is created
            # print(err_logs) # For debugging - to check if any errors occoured
            df = FilterFunction(df)
            emptydataframe("businessoutreach", df)
            # df  = link_correction(df)
            
            return df
           
        
        except:
            not_working_functions.append("businessoutreach")
            print("businessoutreach not working")


    def gccbusinessnews(keyword):
        try:
            print("gccbusinessnews")
            Errors["gccbusinessnews"]=[]
            
          
            url = f"https://www.gccbusinessnews.com/?s={keyword}"
            domain_url = "https://www.gccbusinessnews.com/"
            headers = {
                "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10.15; rv:78.0) Gecko/20100101 Firefox/78.0",
                "accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.9",
                'sec-fetch-site': 'none',
                'sec-fetch-mode': 'navigate',
                'sec-fetch-user': '?1',
                'sec-fetch-dest': 'document',
                'accept-language': 'en-GB,en-US;q=0.9,en;q=0.8',
            }
            
            links=[]
            try:
                page = requests.get(url, headers=headers)
                soup = BeautifulSoup(page.content, "html.parser")
            except:
                print("gccbusinessnews not working")
                not_working_functions.append('gccbusinessnews')
                err = "Main link did not load: " + url
                Errors["gccbusinessnews"].append(err)
                return
            
            
            try:
                
                all_divs = soup.find_all("div",{"class":"td_module_16 td_module_wrap td-animation-stack"})

                for div in all_divs:
                    links.append(div.a["href"])
            except:
                if len(links)==0:
                    print("gccbusinessnews not working")
                    not_working_functions.append('gccbusinessnews')
                    Errors["gccbusinessnews"].append("Extraction of link not working.")
                    return
                        
            # Remove duplicates
            links = list(set(links))
            
            # links # Debugging - if link array is generated
            collection = []
            scrapper_name = "gccbusinessnews"
            
            def getarticles(link):
                
                flag=0
                err=err_dict()
                try:
                    l_page = requests.get(link, headers=headers)
                    l_soup = BeautifulSoup(l_page.content, 'html.parser')
                except:
                    err["link"]="Link not working: "+link
                    Errors["gccbusinessnews"].append(err)
                    return
                
                data = []
                
                # Scraping the heading
                #h1_ele = l_soup.find("h1", {"class": h1_class})
                
                try:
                    title_ele =l_soup.find("h1")
                    title_text = title_ele.text
                    
                    data.append(title_text)
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
                    date_ele = l_soup.find("time")
                    date_text = date_ele.text
                    l=date_text.split(",")
                    l2=l[1].split(" ")
                    date_text=l2[1]+"-"+l2[2]+"-"+l[2]
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
                   para_ele = (l_soup.find("div",{"class":"td-post-content"}))
                   para_text = para_ele.text
                   
                   data.append(para_text)  # Need to make this better
                except:
                    err["link"]=link
                    err['text']="Error"
                    data.append("-")
                    flag=1
                  # drops the complete data if there is an error
                # Adding data to a collection
                
                if flag==1:
                    Errors["gccbusinessnews"].append(err)
                
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
            emptydataframe("gccbusinessnews", df)
            # df  = link_correction(df)
            
            return df
        
        except:
            not_working_functions.append("gccbusinessnews")
            print("gccbusinessnews not working")

    def saltwire(keyword):
        try:
            print("saltwire")
            Errors["saltwire"]=[]
            
          
            url = f"https://www.saltwire.com/search/?search={keyword}&order=newest"
            domain_url = "https://www.saltwire.com/"
            headers = {
                "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10.15; rv:78.0) Gecko/20100101 Firefox/78.0",
                "accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.9",
                'sec-fetch-site': 'none',
                'sec-fetch-mode': 'navigate',
                'sec-fetch-user': '?1',
                'sec-fetch-dest': 'document',
                'accept-language': 'en-GB,en-US;q=0.9,en;q=0.8',
            }
            div_class="col"# Class name of div containing the a tag
            #h1_class = "_1Y-96"
            #h1_div_class = "col-xs-12"
            title_h1_class= "sw-article__headline"
            date_span_class= ["sw-article__author-byline"]
            para_section_class=["sw-content article-content"]
            
            links=[]
            try:
                page = requests.get(url, headers=headers)
                soup = BeautifulSoup(page.content, "html.parser")
            except:
                print("saltwire not working")
                not_working_functions.append('saltwire')
                err = "Main link did not load: " + url
                Errors["saltwire"].append(err)
                return
            
            
            try:
                
                for divtag in soup.find_all("div", {"class": div_class}):
                    for a in divtag.find_all("a", href=True):
                        link = a["href"]  # Gets the link
                        
                        # Checking the link if it is a relative link
                        if link[0] == '/':
                            link = domain_url + link
                        
                        # Filtering advertaisment links
                        link_start = domain_url 
                        if link.startswith(link_start):
                            links.append(link)
            # Remove duplicates
                links = list(set(links))
            except:
                if len(links)==0:
                    print("saltwire not working")
                    not_working_functions.append('saltwire')
                    Errors["saltwire"].append("Extraction of link not working.")
                    return
                        
            # Remove duplicates
            links = list(set(links))
            
            # links # Debugging - if link array is generated
            collection = []
            scrapper_name = "saltwire"
            
            def getarticles(link):
                
                flag=0
                err=err_dict()
                try:
                    l_page = requests.get(link, headers=headers)
                    l_soup = BeautifulSoup(l_page.content, 'html.parser')
                except:
                    err["link"]="Link not working: "+link
                    Errors["saltwire"].append(err)
                    return
                
                data = []
                
                # Scraping the heading
                #h1_ele = l_soup.find("h1", {"class": h1_class})
                
                try:
                    title_ele =l_soup.find("h1", {"class": title_h1_class})
                    title_text = title_ele.text
                    
                    data.append(title_text)
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
                    date_text=date_text.strip(" ")
                    l=date_text.split(" ")
                    for i in range(0,len(l)):
                        if(l[i]=="Posted:"):
                            date_text=l[i+2].strip(",")+"-"+l[i+1].strip(".")+"-"+l[i+3].strip(",")
                    if(date_text=="day-a-ago"):
                        l= datetime.now() - timedelta(1)
                        date_text=str(l)
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
                   para_ele = (l_soup.find("section", {"class": para_section_class}))
                   para_text = para_ele.text
                   
                   data.append(para_text)  # Need to make this better
                except:
                    err["link"]=link
                    err['text']="Error"
                    data.append("-")
                    flag=1
                  # drops the complete data if there is an error
                # Adding data to a collection
                
                if flag==1:
                    Errors["saltwire"].append(err)
                
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
            emptydataframe("saltwire", df)
            # df  = link_correction(df)
            
            return df
        
        except:
            not_working_functions.append("saltwire")
            print("saltwire not working")

    def manilastandard(keyword):
        try:
            print("manilastandard")
            Errors["manilastandard"]=[]
            
          
            url = f"https://www.manilastandard.net/?s={keyword}"
            domain_url = "https://www.manilastandard.net/"
            headers = {
                "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10.15; rv:78.0) Gecko/20100101 Firefox/78.0",
                "accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.9",
                'sec-fetch-site': 'none',
                'sec-fetch-mode': 'navigate',
                'sec-fetch-user': '?1',
                'sec-fetch-dest': 'document',
                'accept-language': 'en-GB,en-US;q=0.9,en;q=0.8',
            }
           
            
            links=[]
            try:
                page = requests.get(url, headers=headers)
                soup = BeautifulSoup(page.content, "html.parser")
            except:
                print("manilastandard not working")
                not_working_functions.append('manilastandard')
                err = "Main link did not load: " + url
                Errors["manilastandard"].append(err)
                return
            
            
            try:
                
                all_divs = soup.find_all("article",{"class":"jeg_post jeg_pl_lg_2 format-standard"})
                for div in all_divs:
                    links.append(div.a["href"])
            except:
                if len(links)==0:
                    print("manilastandard not working")
                    not_working_functions.append('manilastandard')
                    Errors["manilastandard"].append("Extraction of link not working.")
                    return
                        
            # Remove duplicates
            links = list(set(links))
            
            # links # Debugging - if link array is generated
            collection = []
            scrapper_name = "manilastandard"
            
            def getarticles(link):
                
                flag=0
                err=err_dict()
                try:
                    l_page = requests.get(link, headers=headers)
                    l_soup = BeautifulSoup(l_page.content, 'html.parser')
                except:
                    err["link"]="Link not working: "+link
                    Errors["manilastandard"].append(err)
                    return
                
                data = []
                
                # Scraping the heading
                #h1_ele = l_soup.find("h1", {"class": h1_class})
                
                try:
                    title_ele =l_soup.find("h1",{"class":"jeg_post_title"})
                    title_text = title_ele.text
                    
                    data.append(title_text)
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
                    date_ele = l_soup.find("div",{"class":"jeg_meta_date"})
                    date_text = date_ele.text
                    date_text=date_text.strip("\n")
                    l=date_text.split(" ")
                    date_text=l[1].strip(",")+"-"+l[0]+"-"+l[2].strip(",")

                    
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
                   para_ele = (l_soup.find("div",{"class":"entry-content no-share"}))
                   para_text = para_ele.text
                   
                   data.append(para_text)  # Need to make this better
                except:
                    err["link"]=link
                    err['text']="Error"
                    data.append("-")
                    flag=1
                  # drops the complete data if there is an error
                # Adding data to a collection
                
                if flag==1:
                    Errors["manilastandard"].append(err)
                
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
            emptydataframe("manilastandard", df)
            # df  = link_correction(df)
            
            return df
        
        except:
            not_working_functions.append("manilastandard")
            print("manilastandard not working")


    def tradewindsnews(keyword):
        try:
            print("tradewindsnews")
            Errors["tradewindsnews"]=[]
            
          
            url = f"https://www.tradewindsnews.com/archive/?languages=en&locale=en&q={keyword}"
            domain_url = "https://www.tradewindsnews.com/"
            headers = {
                "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10.15; rv:78.0) Gecko/20100101 Firefox/78.0",
                "accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.9",
                'sec-fetch-site': 'none',
                'sec-fetch-mode': 'navigate',
                'sec-fetch-user': '?1',
                'sec-fetch-dest': 'document',
                'accept-language': 'en-GB,en-US;q=0.9,en;q=0.8',
            }
           
            
            links=[]
            try:
                page = requests.get(url, headers=headers)
                soup = BeautifulSoup(page.content, "html.parser")
            except:
                print("tradewindsnews not working")
                not_working_functions.append('tradewindsnews')
                err = "Main link did not load: " + url
                Errors["tradewindsnews"].append(err)
                return
            
            
            try:
                
                all_divs = soup.find_all("a",{"class":"card-link text-reset"})
                for div in all_divs:
                    links.append(domain_url+div["href"])
            except:
                if len(links)==0:
                    print("tradewindsnews not working")
                    not_working_functions.append('tradewindsnews')
                    Errors["tradewindsnews"].append("Extraction of link not working.")
                    return
                        
            # Remove duplicates
            links = list(set(links))
            
            # links # Debugging - if link array is generated
            collection = []
            scrapper_name = "tradewindsnews"
            
            def getarticles(link):
                
                flag=0
                err=err_dict()
                try:
                    l_page = requests.get(link, headers=headers)
                    l_soup = BeautifulSoup(l_page.content, 'html.parser')
                except:
                    err["link"]="Link not working: "+link
                    Errors["tradewindsnews"].append(err)
                    return
                
                data = []
                
                # Scraping the heading
                #h1_ele = l_soup.find("h1", {"class": h1_class})
                
                try:
                    title_ele =l_soup.find("h1",{"class":"fs-xxl fw-bold mb-4 article-title ff-sueca-bold"})
                    title_text = title_ele.text
                    
                    data.append(title_text)
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
                    date_ele = l_soup.find("span",{"class":"pr-3"})
                    date_text = date_ele.text
                    date_text=date_text.strip("\n")
                    date_text=date_text.strip(" ")
                    l=date_text.split(" ")
                    date_text=l[0]+"-"+l[1]+"-"+l[2]

                    
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
                   para_ele = (l_soup.find("div",{"class":"article-body"}))
                   para_text = para_ele.text
                   
                   data.append(para_text)  # Need to make this better
                except:
                    err["link"]=link
                    err['text']="Error"
                    data.append("-")
                    flag=1
                  # drops the complete data if there is an error
                # Adding data to a collection
                
                if flag==1:
                    Errors["tradewindsnews"].append(err)
                
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
            emptydataframe("tradewindsnews", df)
            # df  = link_correction(df)
            
            return df
        
        except:
            not_working_functions.append("tradewindsnews")
            print("tradewindsnews not working")

    def khaleejtimes(keyword):
        try:
            print("khaleejtimes")
            Errors["khaleejtimes"]=[]
            
          
            url = f"https://www.khaleejtimes.com/search?q={keyword}"
            domain_url = "https://www.khaleejtimes.com/"
            headers = {
                "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10.15; rv:78.0) Gecko/20100101 Firefox/78.0",
                "accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.9",
                'sec-fetch-site': 'none',
                'sec-fetch-mode': 'navigate',
                'sec-fetch-user': '?1',
                'sec-fetch-dest': 'document',
                'accept-language': 'en-GB,en-US;q=0.9,en;q=0.8',
            }
           
            
            links=[]
            try:
                page = requests.get(url, headers=headers)
                soup = BeautifulSoup(page.content, "html.parser")
            except:
                print("khaleejtimes not working")
                not_working_functions.append('khaleejtimes')
                err = "Main link did not load: " + url
                Errors["khaleejtimes"].append(err)
                return
            
            
            try:
                
                all_divs = soup.find_all("article",{"class":"post left-image-right-content-subsection"})
                for div in all_divs:
                    links.append(div.a["href"])
            except:
                if len(links)==0:
                    print("khaleejtimes not working")
                    not_working_functions.append('khaleejtimes')
                    Errors["khaleejtimes"].append("Extraction of link not working.")
                    return
                        
            # Remove duplicates
            links = list(set(links))
            
            # links # Debugging - if link array is generated
            collection = []
            scrapper_name = "khaleejtimes"
            
            def getarticles(link):
                
                flag=0
                err=err_dict()
                try:
                    l_page = requests.get(link, headers=headers)
                    l_soup = BeautifulSoup(l_page.content, 'html.parser')
                except:
                    err["link"]="Link not working: "+link
                    Errors["khaleejtimes"].append(err)
                    return
                
                data = []
                
                # Scraping the heading
                #h1_ele = l_soup.find("h1", {"class": h1_class})
                
                try:
                    title_ele =l_soup.find("h1")
                    title_text = title_ele.text
                    
                    data.append(title_text)
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
                    date_ele = l_soup.find("div",{"class":"article-top-author-nw-nf-right"})
                    date_text = date_ele.text
                    date_text=date_text.strip("\n")
                    date_text=date_text.strip(" ")
                    l=date_text.split(" ")
                    date_text=l[2]+"-"+l[3]+"-"+l[4].strip(",")
                    
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
                   para_ele = (l_soup.find("div",{"class":"article-paragraph-wrapper"}))
                   para_text = para_ele.text
                   
                   data.append(para_text)  # Need to make this better
                except:
                    err["link"]=link
                    err['text']="Error"
                    data.append("-")
                    flag=1
                  # drops the complete data if there is an error
                # Adding data to a collection
                
                if flag==1:
                    Errors["khaleejtimes"].append(err)
                
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
            emptydataframe("khaleejtimes", df)
            # df  = link_correction(df)
            
            return df
        
        except:
            not_working_functions.append("khaleejtimes")
            print("khaleejtimes not working")

    def albayan(keyword):
        try:
            print("albayan")
            Errors["albayan"]=[]
            
          
            url = f"https://www.albayan.ae/search-7.3263153?s=d&q={keyword}"
            domain_url = "https://www.albayan.ae/"
            headers = {
                "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10.15; rv:78.0) Gecko/20100101 Firefox/78.0",
                "accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.9",
                'sec-fetch-site': 'none',
                'sec-fetch-mode': 'navigate',
                'sec-fetch-user': '?1',
                'sec-fetch-dest': 'document',
                'accept-language': 'en-GB,en-US;q=0.9,en;q=0.8',
            }
           
            
            links=[]
            try:
                page = requests.get(url, headers=headers)
                soup = BeautifulSoup(page.content, "html.parser")
            except:
                print("albayan not working")
                not_working_functions.append('albayan')
                err = "Main link did not load: " + url
                Errors["albayan"].append(err)
                return
            
            
            try:
                
                for divtag in soup.find_all("li"):
                    for a in divtag.find_all("a", href=True):
                        link = a["href"]  # Gets the link

                        

                                            # Filtering advertaisment links
                        link_start = domain_url
                        if link.startswith(link_start):
                            links.append(link)
                                    # Remove duplicates
                links = list(set(links))
            except:
                if len(links)==0:
                    print("albayan not working")
                    not_working_functions.append('albayan')
                    Errors["albayan"].append("Extraction of link not working.")
                    return
                        
            # Remove duplicates
            links = list(set(links))
            
            # links # Debugging - if link array is generated
            collection = []
            scrapper_name = "albayan"
            
            def getarticles(link):
                
                flag=0
                err=err_dict()
                try:
                    l_page = requests.get(link, headers=headers)
                    l_soup = BeautifulSoup(l_page.content, 'html.parser')
                except:
                    err["link"]="Link not working: "+link
                    Errors["albayan"].append(err)
                    return
                
                data = []
                
                # Scraping the heading
                #h1_ele = l_soup.find("h1", {"class": h1_class})
                
                try:
                    title_ele =l_soup.find("h1")
                    title_text = translate(title_ele.text)
                    
                    data.append(title_text)
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
                    date_text=link.split("/")
                    l=date_text[5]
                    l1=l.split("-")
                    date_text=l1[2]+"-"+l1[1]+"-"+l1[0]

                   
                    
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
                   para_ele = (l_soup.findAll("section",{"class":"twocolumnsctky"}))[-1]
                   para_text = translate(para_ele.text)
                   
                   data.append(para_text)  # Need to make this better
                except:
                    err["link"]=link
                    err['text']="Error"
                    data.append("-")
                    flag=1
                  # drops the complete data if there is an error
                # Adding data to a collection
                
                if flag==1:
                    Errors["albayan"].append(err)
                
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
            emptydataframe("albayan", df)
            # df  = link_correction(df)
            
            return df
        
        except:
            not_working_functions.append("albayan")
            print("albayan not working")

    def ipocentral(keyword):
        try:
            print("ipocentral")
            Errors["ipocentral"]=[]
            
          
            url = f"https://ipocentral.in/?s={keyword}"
            domain_url = "https://ipocentral.in/"
            headers = {
                "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10.15; rv:78.0) Gecko/20100101 Firefox/78.0",
                "accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.9",
                'sec-fetch-site': 'none',
                'sec-fetch-mode': 'navigate',
                'sec-fetch-user': '?1',
                'sec-fetch-dest': 'document',
                'accept-language': 'en-GB,en-US;q=0.9,en;q=0.8',
            }
           
            
            links=[]
            try:
                page = requests.get(url, headers=headers)
                soup = BeautifulSoup(page.content, "html.parser")
            except:
                print("ipocentral not working")
                not_working_functions.append('ipocentral')
                err = "Main link did not load: " + url
                Errors["ipocentral"].append(err)
                return
            
            
            try:
                
                all_divs = soup.find_all("div",{"class":"td_module_16 td_module_wrap td-animation-stack"})
                for div in all_divs:
                    links.append(div.a["href"])
            except:
                if len(links)==0:
                    print("ipocentral not working")
                    not_working_functions.append('ipocentral')
                    Errors["ipocentral"].append("Extraction of link not working.")
                    return
                        
            # Remove duplicates
            links = list(set(links))
            
            # links # Debugging - if link array is generated
            collection = []
            scrapper_name = "ipocentral"
            
            def getarticles(link):
                
                flag=0
                err=err_dict()
                try:
                    l_page = requests.get(link, headers=headers)
                    l_soup = BeautifulSoup(l_page.content, 'html.parser')
                except:
                    err["link"]="Link not working: "+link
                    Errors["ipocentral"].append(err)
                    return
                
                data = []
                
                # Scraping the heading
                #h1_ele = l_soup.find("h1", {"class": h1_class})
                
                try:
                    title_ele =l_soup.find("h1")
                    title_text = title_ele.text
                    
                    data.append(title_text)
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
                    date_ele = l_soup.find("time",{"class":"entry-date updated td-module-date"})
                    date_text = date_ele.text
                    l=date_text.split(" ")
                    date_text=l[1].strip(",")+"-"+l[0]+"-"+l[2]    
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
                   para_ele = (l_soup.findAll("div",{"class":"td-post-content tagdiv-type"}))[-1]
                   para_text = para_ele.text
                   para_text = para_text.strip("\n ")
                   data.append(para_text)
                    # Need to make this better
                except:
                    err["link"]=link
                    err['text']="Error"
                    data.append("-")
                    flag=1
                  # drops the complete data if there is an error
                # Adding data to a collection
                
                if flag==1:
                    Errors["ipocentral"].append(err)
                
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
            emptydataframe("ipocentral", df)
            # df  = link_correction(df)
            
            return df
        
        except:
            not_working_functions.append("ipocentral")
            print("ipocentral not working")

    def kmib(keyword):
        try:
            print("kmib")
            Errors["kmib"]=[]
            
          
            url = f"https://www.kmib.co.kr/search/searchResult.asp?searchWord={keyword}"
            domain_url = "https://www.kmib.co.kr/"
            headers = {
                "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10.15; rv:78.0) Gecko/20100101 Firefox/78.0",
                "accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.9",
                'sec-fetch-site': 'none',
                'sec-fetch-mode': 'navigate',
                'sec-fetch-user': '?1',
                'sec-fetch-dest': 'document',
                'accept-language': 'en-GB,en-US;q=0.9,en;q=0.8',
            }
           
            
            links=[]
            try:
                page = requests.get(url, headers=headers)
                soup = BeautifulSoup(page.content, "html.parser")
            except:
                print("kmib not working")
                not_working_functions.append('kmib')
                err = "Main link did not load: " + url
                Errors["kmib"].append(err)
                return
            
            
            try:
                
                all_divs = soup.find_all("div",{"class":"search_nws"})
                for div in all_divs:
                    links.append(div.a["href"])
            except:
                if len(links)==0:
                    print("kmib not working")
                    not_working_functions.append('kmib')
                    Errors["kmib"].append("Extraction of link not working.")
                    return
                        
            # Remove duplicates
            links = list(set(links))
            
            # links # Debugging - if link array is generated
            collection = []
            scrapper_name = "kmib"
            
            def getarticles(link):
                
                flag=0
                err=err_dict()
                try:
                    l_page = requests.get(link, headers=headers)
                    l_soup = BeautifulSoup(l_page.content, 'html.parser')
                except:
                    err["link"]="Link not working: "+link
                    Errors["kmib"].append(err)
                    return
                
                data = []
                
                # Scraping the heading
                #h1_ele = l_soup.find("h1", {"class": h1_class})
                
                try:
                    title_ele =l_soup.find("h3")
                    title_text = translate(title_ele.text)
                    
                    data.append(title_text)
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
                    date_ele = l_soup.find("span",{"class":"t11"})
                    date_text = date_ele.text
                    l=date_text.split(" ")
                    date_text=l[0]
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
                   para_ele = (l_soup.findAll("div",{"class":"nws_arti"}))[-1]
                   para_text = translate(para_ele.text)
                   para_text = para_text.strip("\n ")
                   data.append(para_text)
                    # Need to make this better
                except:
                    err["link"]=link
                    err['text']="Error"
                    data.append("-")
                    flag=1
                  # drops the complete data if there is an error
                # Adding data to a collection
                
                if flag==1:
                    Errors["kmib"].append(err)
                
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
            emptydataframe("kmib", df)
            # df  = link_correction(df)
            
            return df
        
        except:
            not_working_functions.append("kmib")
            print("kmib not working")

    def seoul(keyword):
        try:
            print("seoul")
            Errors["seoul"]=[]
            
          
            url = f"https://search.seoul.co.kr/index.php?keyword={keyword}"
            domain_url = "https://www.seoul.co.kr/"
            headers = {
                "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10.15; rv:78.0) Gecko/20100101 Firefox/78.0",
                "accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.9",
                'sec-fetch-site': 'none',
                'sec-fetch-mode': 'navigate',
                'sec-fetch-user': '?1',
                'sec-fetch-dest': 'document',
                'accept-language': 'en-GB,en-US;q=0.9,en;q=0.8',
            }
           
            
            links=[]
            try:
                page = requests.get(url, headers=headers)
                soup = BeautifulSoup(page.content, "html.parser")
            except:
                print("seoul not working")
                not_working_functions.append('seoul')
                err = "Main link did not load: " + url
                Errors["seoul"].append(err)
                return
            
            
            try:
                
                all_divs = soup.find_all("dl",{"class":"article"})
                for div in all_divs:
                    links.append(div.a["href"])
            except:
                if len(links)==0:
                    print("seoul not working")
                    not_working_functions.append('seoul')
                    Errors["seoul"].append("Extraction of link not working.")
                    return
                        
            # Remove duplicates
            links = list(set(links))
            
            # links # Debugging - if link array is generated
            collection = []
            scrapper_name = "seoul"
            
            def getarticles(link):
                
                flag=0
                err=err_dict()
                try:
                    l_page = requests.get(link, headers=headers)
                    l_soup = BeautifulSoup(l_page.content, 'html.parser')
                except:
                    err["link"]="Link not working: "+link
                    Errors["seoul"].append(err)
                    return
                
                data = []
                
                # Scraping the heading
                #h1_ele = l_soup.find("h1", {"class": h1_class})
                
                try:
                    title_ele =l_soup.find("h1")
                    title_text = translate(title_ele.text)
                    
                    data.append(title_text)
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
                    
                    l=link.split("=")
                    l1=l[1]
                    date_text=l1[6:8]+"-"+l1[4:6]+"-"+l1[0:4]
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
                   para_ele = (l_soup.findAll("div",{"class":"S20_v_article"}))[-1]
                   para_text = translate(para_ele.text)
                   para_text = para_text.strip("\n ")
                   data.append(para_text)
                    # Need to make this better
                except:
                    err["link"]=link
                    err['text']="Error"
                    data.append("-")
                    flag=1
                  # drops the complete data if there is an error
                # Adding data to a collection
                
                if flag==1:
                    Errors["seoul"].append(err)
                
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
            emptydataframe("seoul", df)
            # df  = link_correction(df)
            
            return df
        
        except:
            not_working_functions.append("seoul")
            print("seoul not working")
          
          
          
    def headline_daily(keyword):
        try:
            print("headline_daily")
            Errors["headline_daily"]=[]
            
          
            url = f"https://hd.stheadline.com/search?keyword={keyword}"
            domain_url = "https://hd.stheadline.com/"
            headers = {
                "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10.15; rv:78.0) Gecko/20100101 Firefox/78.0",
                "accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.9",
                'sec-fetch-site': 'none',
                'sec-fetch-mode': 'navigate',
                'sec-fetch-user': '?1',
                'sec-fetch-dest': 'document',
                'accept-language': 'en-GB,en-US;q=0.9,en;q=0.8',
            }
            # count =2
            collection = []
            # while True:
            #     if not count:
            #         break   
            links=[]
            try:
                page = requests.get(url, headers=headers)
                soup = BeautifulSoup(page.content, "html.parser")
            except:
                print("headline_daily not working")
                not_working_functions.append('headline_daily')
                err = "Main link did not load: " + url
                Errors["headline_daily"].append(err)
                return
            
            # next_link = soup.find('a', attrs={'aria-label': 'Next'})
            
            # url =domain_url+ next_link['href'][1:]
            # print(url)
                
            # count-=1
            # print(count)
            
            try:
                div_id = soup.find_all("div",{"class": "col-xs-12"})
                for div in div_id :
                    a_link= div.find("a")
                    link=a_link['href']
                                            # Checking the link if it is a relative link
                    if link[0] == '/':
                        link = domain_url + link[1:]

                                            # Filtering advertaisment links
                    # link_start = domain_url
                    # if link.startswith(link_start):
                    links.append(link)
                                    # Remove duplicates
                links = list(set(links))
                
            except:
                if len(links)==0:
                    print("headline_daily not working")
                    not_working_functions.append('headline_daily')
                    Errors["headline_daily"].append("Extraction of link not working.")
                    return
                        
            
            # links # Debugging - if link array is generated
            # collection = []
            scrapper_name = "headline_daily"
            
            def getarticles(link):

                # print(link)
                flag=0
                err=err_dict()
                try:
                    l_page = requests.get(link, headers=headers)
                    l_soup = BeautifulSoup(l_page.content, 'html.parser')
                except:
                    err["link"]="Link not working: "+link
                    Errors["headline_daily"].append(err)
                    return
                
                data = []
                
                # Scraping the heading
                #h1_ele = l_soup.find("h1", {"class": h1_class})
                
                try:
                    title_ele =l_soup.find("div",class_="article-title")
                    title_text = translatedeep(title_ele.text)
                    # print(title_text)
                    data.append(title_text)
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
                    date_ele =l_soup.find("div",{"class":"time"})
                    date_text = date_ele.text
                    date_obj = datetime.strptime(date_text.split(' ')[-1], '%Y-%m-%d').date()
                    

                    # Convert datetime object to desired date format
                    formatted_date = date_obj.strftime('%d-%m-%y')

                    
                    data.append(formatted_date)
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
                    para_eles = l_soup.find_all("p")
                    p_text =""
                    for para in para_eles:
                        para_text = translatedeep(para.text)
                        # print(para_text)
                        p_text +=para_text
                    data.append(p_text)  # Need to make this better
                except:
                    err["link"]=link
                    err['text']="Error"
                    data.append("-")
                    flag=1
                # drops the complete data if there is an error
                # Adding data to a collection
                
                if flag==1:
                    Errors["headline_daily"].append(err)
                
                collection.append(data)
                
                # for x in data:
                #     print(x)
                # print()
        
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
            emptydataframe("headline_daily", df)
                # df  = link_correction(df)
                
            return df
        
        except:
            not_working_functions.append("headline_daily")
            print("headline_daily not working")


    def aljazeera(keyword):
        try:
            print("aljazeera")
            Errors["aljazeera"]=[]
            
          
            url = f"https://aljazeera.com/search/{keyword}"
            domain_url = "https://aljazeera.com/"
            headers = {
                "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10.15; rv:78.0) Gecko/20100101 Firefox/78.0",
                "accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.9",
                'sec-fetch-site': 'none',
                'sec-fetch-mode': 'navigate',
                'sec-fetch-user': '?1',
                'sec-fetch-dest': 'document',
                'accept-language': 'en-GB,en-US;q=0.9,en;q=0.8',
            }
            
            links=[]
            try:
                page = requests.get(url, headers=headers)
                soup = BeautifulSoup(page.content, "html.parser")
            except:
                print("aljazeera not working")
                not_working_functions.append('aljazeera')
                err = "Main link did not load: " + url
                Errors["aljazeera"].append(err)
                return
            
            # print(url)
            try:
                div_id = soup.find_all("div",{"class": "gc__content"})
                for div in div_id :
                    a_link= div.find("a")
                    link=a_link['href']
                                            # Checking the link if it is a relative link
                    if link[0] == '/':
                        link = domain_url + link

                    #                         # Filtering advertaisment links
                    # link_start = domain_url
                    # if link.startswith(link_start):
                    links.append(link)
                                    # Remove duplicates
                links = list(set(links))
                
            except:
                if len(links)==0:
                    print("aljazeera not working")
                    not_working_functions.append('aljazeera')
                    Errors["aljazeera"].append("Extraction of link not working.")
                    return
                        
            
            # links # Debugging - if link array is generated
            collection = []
            scrapper_name = "aljazeera"
            
            def getarticles(link):

                # print(link)
                flag=0
                err=err_dict()
                try:
                    l_page = requests.get(link, headers=headers)
                    l_soup = BeautifulSoup(l_page.content, 'html.parser')
                except:
                    err["link"]="Link not working: "+link
                    Errors["aljazeera"].append(err)
                    return
                
                data = []
                
                # Scraping the heading
                #h1_ele = l_soup.find("h1", {"class": h1_class})
                
                try:
                    title_ele =l_soup.find("h1")
                    title_text = title_ele.text
                    
                    data.append(title_text)
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
                    date_ele =l_soup.find("div",{"class":"date-simple"})
                    date_ele_y=date_ele.find("span",{"class":"screen-reader-text"})
                    date_text = date_ele_y.text
                   
                 


                    # Convert datetime object to desired date format
                    date_str = date_text.split(" ")[2] + "-" + datetime.strptime(date_text.split(" ")[3], '%b').strftime('%m') + "-" + date_text.split(" ")[4][-2:]
                    
                    
                    data.append(date_str)
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
                   para_ele = l_soup.find_all("p")
                   para_text = para_ele.text
                   
                   data.append(para_text)  # Need to make this better
                except:
                    err["link"]=link
                    err['text']="Error"
                    data.append("-")
                    flag=1
                  # drops the complete data if there is an error
                # Adding data to a collection
                
                if flag==1:
                    Errors["aljazeera"].append(err)
                
                collection.append(data)
                
                # for x in data:
                #     print(x)
                # print()
           
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
            emptydataframe("aljazeera", df)
            # df  = link_correction(df)
            
            return df
        
        except:
            not_working_functions.append("aljazeera")
            print("aljazeera not working")

    def a_163(keyword):
        try:
            print("a_163")
            Errors["a_163"]=[]
            
          
            url = f"https://www.163.com/search?keyword={keyword}"
            domain_url = "https://www.163.com/"
            headers = {
                "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10.15; rv:78.0) Gecko/20100101 Firefox/78.0",
                "accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.9",
                'sec-fetch-site': 'none',
                'sec-fetch-mode': 'navigate',
                'sec-fetch-user': '?1',
                'sec-fetch-dest': 'document',
                'accept-language': 'en-GB,en-US;q=0.9,en;q=0.8',
            }
            # count =2
            collection = []
            # while True:
            #     if not count:
            #         break   
            links=[]
            try:
                page = requests.get(url, headers=headers)
                soup = BeautifulSoup(page.content, "html.parser")
            except:
                print("a_163 not working")
                not_working_functions.append('a_163')
                err = "Main link did not load: " + url
                Errors["a_163"].append(err)
                return
            
            # next_link = soup.find('a', attrs={'aria-label': 'Next'})
            
            # url =domain_url+ next_link['href'][1:]
            # print(url)
                
            # count-=1
            # print(count)
            
            try:
                div_id = soup.find_all("div",{"class":"keyword_img"})
                for div in div_id :
                    a_link= div.find("a")
                    link=a_link['href']
                                            # Checking the link if it is a relative link
                    if link[0] == '/':
                        link = domain_url + link[1:]

                                            # Filtering advertaisment links
                    link_start = domain_url +"dy/article/"
                    if link.startswith(link_start):
                         links.append(link)
                                    # Remove duplicates
                links = list(set(links))
                
            except:
                if len(links)==0:
                    print("a_163 not working")
                    not_working_functions.append('a_163')
                    Errors["a_163"].append("Extraction of link not working.")
                    return
                        
            
            # links # Debugging - if link array is generated
            # collection = []
            scrapper_name = "a_163"
            
            def getarticles(link):
                
                print(link)
                flag=0
                err=err_dict()
                try:
                    l_page = requests.get(link, headers=headers)
                    l_soup = BeautifulSoup(l_page.content, 'html.parser')
                except:
                    err["link"]="Link not working: "+link
                    Errors["a_163"].append(err)
                    return
                
                data = []
                
                # Scraping the heading
                #h1_ele = l_soup.find("h1", {"class": h1_class})
                
                try:
                    title_ele =l_soup.find("h1")
                    title_text = translatedeep(title_ele.text)
                    # print(title_text)
                    data.append(title_text)
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
                    date_ele =soup.find("div",{"class":"keyword_time"})
                    date_text = date_ele.text
                    # print(date_text)
                    date_parts = date_text.split('-')
                    formatted_date = f"{date_parts[2]}-{date_parts[1]}-{date_parts[0]}"
                    # formatted_date=date_text
                    print(formatted_date)                    
                    data.append(formatted_date)
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
                    para_eles = l_soup.find_all("p")
                    p_text =""
                    for para in para_eles:
                        para_text = translatedeep(para.text)
                        print(para_text)
                        p_text +=para_text
                    data.append(p_text)  # Need to make this better
                except:
                    err["link"]=link
                    err['text']="Error"
                    data.append("-")
                    flag=1
                # drops the complete data if there is an error
                # Adding data to a collection
                
                if flag==1:
                    Errors["a_163"].append(err)
                
                collection.append(data)
                
                # for x in data:
                #     print(x)
                # print()
        
            thread_list=[]
            length=len(links)
            for i in range(10):
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
            emptydataframe("a_163", df)
                # df  = link_correction(df)
                
            return df
        
        except:
            not_working_functions.append("a_163")
            print("a_163 not working")

    def montsame(keyword):
        try:
            print("montsame")
            Errors["montsame"]=[]
            
          
            url = f"https://www.montsame.mn/mn/search?keyword={keyword}"
            domain_url = "https://www.montsame.mn/"
            headers = {
                "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10.15; rv:78.0) Gecko/20100101 Firefox/78.0",
                "accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.9",
                'sec-fetch-site': 'none',
                'sec-fetch-mode': 'navigate',
                'sec-fetch-user': '?1',
                'sec-fetch-dest': 'document',
                'accept-language': 'en-GB,en-US;q=0.9,en;q=0.8',
            }
            # count =2
            collection = []
            # while True:
            #     if not count:
            #         break   
            links=[]
            try:
                page = requests.get(url, headers=headers)
                soup = BeautifulSoup(page.content, "html.parser")
            except:
                print("montsame not working")
                not_working_functions.append('montsame')
                err = "Main link did not load: " + url
                Errors["montsame"].append(err)
                return
            
            # next_link = soup.find('a', attrs={'aria-label': 'Next'})
            
            # url =domain_url+ next_link['href'][1:]
            # print(url)
                
            # count-=1
            # print(count)
            
            try:
                div_id = soup.find_all("div",{"class": "news-box-list"})
                for div in div_id :
                    a_link= div.find("a")
                    link=a_link['href']
                                            # Checking the link if it is a relative link
                    if link[0] == '/':
                        link = domain_url + link[1:]

                                            # Filtering advertaisment links
                    # link_start = domain_url
                    # if link.startswith(link_start):
                    links.append(link)
                                    # Remove duplicates
                links = list(set(links))
                
            except:
                if len(links)==0:
                    print("montsame not working")
                    not_working_functions.append('montsame')
                    Errors["montsame"].append("Extraction of link not working.")
                    return
                        
            
            # links # Debugging - if link array is generated
            # collection = []
            scrapper_name = "montsame"
            
            def getarticles(link):

                #  print(link)
                flag=0
                err=err_dict()
                try:
                    l_page = requests.get(link, headers=headers)
                    l_soup = BeautifulSoup(l_page.content, 'html.parser')
                except:
                    err["link"]="Link not working: "+link
                    Errors["montsame"].append(err)
                    return
                
                data = []
                
                # Scraping the heading
                #h1_ele = l_soup.find("h1", {"class": h1_class})
                
                try:
                    title_ele =l_soup.find("title")
                    title_text = translatedeep(title_ele.text)
                    # print(title_text)
                    data.append(title_text)
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
                    date_ele =l_soup.find("span",{"class":"stat"})
                    date_text = date_ele.text.strip()
                    # print(date_text)
                    datetime_obj = datetime.strptime(date_text, '%Y-%m-%d %H:%M:%S')
                    formatted_date = datetime_obj.strftime('%d-%m-%y')
                    # print(formatted_date)

                    
                    data.append(formatted_date)
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
                    para_eles = l_soup.find_all("p")
                    p_text =""
                    for para in para_eles:
                        para_text = translatedeep(para.text)
                        # print(para_text)
                        p_text +=para_text
                    data.append(p_text)  # Need to make this better
                except:
                    err["link"]=link
                    err['text']="Error"
                    data.append("-")
                    flag=1
                # drops the complete data if there is an error
                # Adding data to a collection
                
                if flag==1:
                    Errors["montsame"].append(err)
                
                collection.append(data)
                
                # for x in data:
                #     print(x)
                # print()
        
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
            emptydataframe("montsame", df)
                # df  = link_correction(df)
                
            return df
        
        except:
            not_working_functions.append("montsame")
            print("montsame not working")
            
    def timesofoman(keyword):
        try:
            print("timesofoman")
            Errors["timesofoman"]=[]
            
          
            url = f"https://timesofoman.com/search?search={keyword}"
            domain_url = "https://timesofoman.com/"
            headers = {
                "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10.15; rv:78.0) Gecko/20100101 Firefox/78.0",
                "accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.9",
                'sec-fetch-site': 'none',
                'sec-fetch-mode': 'navigate',
                'sec-fetch-user': '?1',
                'sec-fetch-dest': 'document',
                'accept-language': 'en-GB,en-US;q=0.9,en;q=0.8',
            }
           
            
            links=[]
            try:
                page = requests.get(url, headers=headers)
                soup = BeautifulSoup(page.content, "html.parser")
            except:
                print("timesofoman not working")
                not_working_functions.append('timesofoman')
                err = "Main link did not load: " + url
                Errors["timesofoman"].append(err)
                return
            
            
            try:
                
                all_divs = soup.find_all("article")
                for div in all_divs:
                    links.append(domain_url+div.a["href"])
            except:
                if len(links)==0:
                    print("timesofoman not working")
                    not_working_functions.append('timesofoman')
                    Errors["timesofoman"].append("Extraction of link not working.")
                    return
                        
            # Remove duplicates
            links = list(set(links))
            
            # links # Debugging - if link array is generated
            collection = []
            scrapper_name = "timesofoman"
            
            def getarticles(link):
                
                flag=0
                err=err_dict()
                try:
                    l_page = requests.get(link, headers=headers)
                    l_soup = BeautifulSoup(l_page.content, 'html.parser')
                except:
                    err["link"]="Link not working: "+link
                    Errors["timesofoman"].append(err)
                    return
                
                data = []
                
                # Scraping the heading
                #h1_ele = l_soup.find("h1", {"class": h1_class})
                
                try:
                    title_ele =l_soup.find("h1")
                    title_text = translate(title_ele.text)
                    
                    data.append(title_text)
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
                    
                    date_ele = l_soup.find("span",{"class":"text-muted"})
                    date_text = date_ele.text
                    l=date_text.split(" ")
                    l1=l[1].split("/")
                    date_text=l1[0]+"-"+l1[1]+"-"+l1[2]
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
                   para_ele = (l_soup.findAll("div",{"class":"post-single"}))[-1]
                   para_text = translate(para_ele.text)
                   para_text = para_text.strip("\n ")
                   data.append(para_text)
                    # Need to make this better
                except:
                    err["link"]=link
                    err['text']="Error"
                    data.append("-")
                    flag=1
                  # drops the complete data if there is an error
                # Adding data to a collection
                
                if flag==1:
                    Errors["timesofoman"].append(err)
                
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
            emptydataframe("timesofoman", df)
            # df  = link_correction(df)
            
            return df
        
        except:
            not_working_functions.append("timesofoman")
            print("timesofoman not working")

    def omanobserver(keyword):
        try:
            print("omanobserver")
            Errors["omanobserver"]=[]


            url = f"https://www.omanobserver.om/search?query={keyword}"
            domain_url = "https://www.omanobserver.om/"
            headers = {
                "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10.15; rv:78.0) Gecko/20100101 Firefox/78.0",
                "accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.9",
                'sec-fetch-site': 'none',
                'sec-fetch-mode': 'navigate',
                'sec-fetch-user': '?1',
                'sec-fetch-dest': 'document',
                'accept-language': 'en-GB,en-US;q=0.9,en;q=0.8',
            }


            links=[]
            try:
                page = requests.get(url, headers=headers)
                soup = BeautifulSoup(page.content, "html.parser")
            except:
                print("omanobserver not working")
                not_working_functions.append('omanobserver')
                err = "Main link did not load: " + url
                Errors["omanobserver"].append(err)
                return


            try:

                all_divs = soup.find_all("div",{"class":"col-sm-3 article"})
                for div in all_divs:
                    links.append(div.a["href"])
            except:
                if len(links)==0:
                    print("omanobserver not working")
                    not_working_functions.append('omanobserver')
                    Errors["omanobserver"].append("Extraction of link not working.")
                    return

            # Remove duplicates
            links = list(set(links))

            # links # Debugging - if link array is generated
            collection = []
            scrapper_name = "omanobserver"

            def getarticles(link):

                flag=0
                err=err_dict()
                try:
                    l_page = requests.get(link, headers=headers)
                    l_soup = BeautifulSoup(l_page.content, 'html.parser')
                except:
                    err["link"]="Link not working: "+link
                    Errors["omanobserver"].append(err)
                    return

                data = []

                # Scraping the heading
                #h1_ele = l_soup.find("h1", {"class": h1_class})

                try:
                    title_ele =l_soup.find("h1",{"class":"title-article"})
                    title_text = translate(title_ele.text)

                    data.append(title_text)
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

                    date_ele = l_soup.find("div",{"class":"publishing-date"})
                    date_text = date_ele.text
                    date_text=date_text.strip("\n")
                    date_text=date_text.strip(" ")
                    l=date_text.split(",")
                    l1=l[1].split(" ")
                    date_text=l1[2]+"-"+l1[1]+"-"+l[2].strip(" ")
                   
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
                   para_ele = (l_soup.findAll("div",{"class":"article-desc"}))[-1]
                   para_text = translate(para_ele.text)
                   para_text = para_text.strip("\n ")
                   data.append(para_text)
                    # Need to make this better
                except:
                    err["link"]=link
                    err['text']="Error"
                    data.append("-")
                    flag=1
                  # drops the complete data if there is an error
                # Adding data to a collection

                if flag==1:
                    Errors["omanobserver"].append(err)

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
            emptydataframe("omanobserver", df)
            # df  = link_correction(df)

            return df

        except:
            not_working_functions.append("omanobserver")
            print("omanobserver not working")
    def thearabianstories(keyword):
        try:
            print("thearabianstories")
            Errors["thearabianstories"]=[]


            url = f"https://www.thearabianstories.com/?s={keyword}"
            domain_url = "https://www.thearabianstories.com/"
            headers = {
                "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10.15; rv:78.0) Gecko/20100101 Firefox/78.0",
                "accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.9",
                'sec-fetch-site': 'none',
                'sec-fetch-mode': 'navigate',
                'sec-fetch-user': '?1',
                'sec-fetch-dest': 'document',
                'accept-language': 'en-GB,en-US;q=0.9,en;q=0.8',
            }


            links=[]
            try:
                page = requests.get(url, headers=headers)
                soup = BeautifulSoup(page.content, "html.parser")
            except:
                print("thearabianstories not working")
                not_working_functions.append('thearabianstories')
                err = "Main link did not load: " + url
                Errors["thearabianstories"].append(err)
                return


            try:

                all_divs = soup.find_all("div",{"class":"col-lg-4 col-md-6"})
                for div in all_divs:
                    links.append(div.a["href"])
            except:
                if len(links)==0:
                    print("thearabianstories not working")
                    not_working_functions.append('thearabianstories')
                    Errors["thearabianstories"].append("Extraction of link not working.")
                    return

            # Remove duplicates
            links = list(set(links))

            # links # Debugging - if link array is generated
            collection = []
            scrapper_name = "thearabianstories"

            def getarticles(link):

                flag=0
                err=err_dict()
                try:
                    l_page = requests.get(link, headers=headers)
                    l_soup = BeautifulSoup(l_page.content, 'html.parser')
                except:
                    err["link"]="Link not working: "+link
                    Errors["thearabianstories"].append(err)
                    return

                data = []

                # Scraping the heading
                #h1_ele = l_soup.find("h1", {"class": h1_class})

                try:
                    title_ele =l_soup.find("h3")
                    title_text = translate(title_ele.text)

                    data.append(title_text)
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

                    l = link.split("/")
                    date_text=l[5]+"-"+l[4]+"-"+l[3]
                   
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
                   para_ele = (l_soup.findAll("div",{"class":"inner-left"}))[-1]
                   para_text = translate(para_ele.text)
                   para_text = para_text.strip("\n ")
                   data.append(para_text)
                    # Need to make this better
                except:
                    err["link"]=link
                    err['text']="Error"
                    data.append("-")
                    flag=1
                  # drops the complete data if there is an error
                # Adding data to a collection

                if flag==1:
                    Errors["thearabianstories"].append(err)

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
            emptydataframe("thearabianstories", df)
            # df  = link_correction(df)

            return df

        except:
            not_working_functions.append("thearabianstories")
            print("thearabianstories not working")

    def romania_insider(keyword):
        try:
            print("romania_insider")
            Errors["romania_insider"]=[]


            url = f"https://www.romania-insider.com/search/node?keys={keyword}"
            domain_url = "https://www.romania-insider.com/"
            headers = {
                "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10.15; rv:78.0) Gecko/20100101 Firefox/78.0",
                "accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.9",
                'sec-fetch-site': 'none',
                'sec-fetch-mode': 'navigate',
                'sec-fetch-user': '?1',
                'sec-fetch-dest': 'document',
                'accept-language': 'en-GB,en-US;q=0.9,en;q=0.8',
            }


            links=[]
            try:
                page = requests.get(url, headers=headers)
                soup = BeautifulSoup(page.content, "html.parser")
            except:
                print("romania_insider not working")
                not_working_functions.append('romania_insider')
                err = "Main link did not load: " + url
                Errors["romania_insider"].append(err)
                return


            try:

                all_divs = soup.find_all("h3",{"class":"search-result__title"})
                for div in all_divs:
                    links.append(div.a["href"])
            except:
                if len(links)==0:
                    print("romania_insider not working")
                    not_working_functions.append('romania_insider')
                    Errors["romania_insider"].append("Extraction of link not working.")
                    return

            # Remove duplicates
            links = list(set(links))

            # links # Debugging - if link array is generated
            collection = []
            scrapper_name = "romania_insider"

            def getarticles(link):

                flag=0
                err=err_dict()
                try:
                    l_page = requests.get(link, headers=headers)
                    l_soup = BeautifulSoup(l_page.content, 'html.parser')
                except:
                    err["link"]="Link not working: "+link
                    Errors["romania_insider"].append(err)
                    return

                data = []

                # Scraping the heading
                #h1_ele = l_soup.find("h1", {"class": h1_class})

                try:
                    title_ele =l_soup.find("h1")
                    title_text = translate(title_ele.text)

                    data.append(title_text)
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

                   date_ele = l_soup.find("div",{"class":"field field--name-field-date field--type-datetime field--label-hidden field__item"})
                   date_text = date_ele.text
                   date_text=date_text.strip("\n")
                   date_text=date_text.strip(" ")
                   l=date_text.split(" ")
                   date_text=l[0]+"-"+l[1]+"-"+l[2]
                   
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
                   para_ele = (l_soup.findAll("div",{"class":"node__content"}))[-1]
                   para_text = translate(para_ele.text)
                   para_text = para_text.strip("\n ")
                   data.append(para_text)
                    # Need to make this better
                except:
                    err["link"]=link
                    err['text']="Error"
                    data.append("-")
                    flag=1
                  # drops the complete data if there is an error
                # Adding data to a collection

                if flag==1:
                    Errors["romania_insider"].append(err)

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
            emptydataframe("romania_insider", df)
            # df  = link_correction(df)

            return df

        except:
            not_working_functions.append("romania_insider")
            print("romania_insider not working")

    def ziarul(keyword):
        try:
            print("ziarul")
            Errors["ziarul"]=[]
            
          
            url = f"https://www.zf.ro/search?q={keyword}"
            domain_url = "https://www.zf.ro/"
            headers = {
                "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10.15; rv:78.0) Gecko/20100101 Firefox/78.0",
                "accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.9",
                'sec-fetch-site': 'none',
                'sec-fetch-mode': 'navigate',
                'sec-fetch-user': '?1',
                'sec-fetch-dest': 'document',
                'accept-language': 'en-GB,en-US;q=0.9,en;q=0.8',
            }
            # count =2
            collection = []
            # while True:
            #     if not count:
            #         break   
            links=[]
            try:
                page = requests.get(url, headers=headers)
                soup = BeautifulSoup(page.content, "html.parser")
            except:
                print("ziarul not working")
                not_working_functions.append('ziarul')
                err = "Main link did not load: " + url
                Errors["ziarul"].append(err)
                return
            
            # next_link = soup.find('a', attrs={'aria-label': 'Next'})
            
            # url =domain_url+ next_link['href'][1:]
            # print(url)
                
            # count-=1
            # print(count)
            
            try:
                div_id = soup.find_all("div",{"class": "articleThumb"})
                for div in div_id :
                    a_link= div.find("a")
                    link=a_link['href']
                                            # Checking the link if it is a relative link
                    if link[0] == '/':
                        link = domain_url + link[1:]

                                            # Filtering advertaisment links
                    # link_start = domain_url
                    # if link.startswith(link_start):
                    links.append(link)
                                    # Remove duplicates
                links = list(set(links))
                
            except:
                if len(links)==0:
                    print("ziarul not working")
                    not_working_functions.append('ziarul')
                    Errors["ziarul"].append("Extraction of link not working.")
                    return
                        
            
            # links # Debugging - if link array is generated
            # collection = []
            scrapper_name = "ziarul"
            
            def getarticles(link):

                # print(link)
                flag=0
                err=err_dict()
                try:
                    l_page = requests.get(link, headers=headers)
                    l_soup = BeautifulSoup(l_page.content, 'html.parser')
                except:
                    err["link"]="Link not working: "+link
                    Errors["ziarul"].append(err)
                    return
                
                data = []
                
                # Scraping the heading
                #h1_ele = l_soup.find("h1", {"class": h1_class})
                
                try:
                    title_ele =l_soup.find("title")
                    title_text = title_ele.text
                    # print(title_text)
                    data.append(title_text)
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
                    date_ele = l_soup.find('span', {'class': 'date'})
                    date_text = date_ele.text.strip()
                    # print(date_text)
                    date_obj = datetime.strptime(date_text, "%d.%m.%Y, %H:%M")
                    formatted_date = date_obj.strftime("%d-%m-%y")
                    data.append(formatted_date)
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
                    para_eles = l_soup.find_all("p")
                    p_text =""
                    for para in para_eles:
                        para_text = para.text
                        # print(para_text)
                        p_text +=para_text
                    data.append(p_text)  # Need to make this better
                except:
                    err["link"]=link
                    err['text']="Error"
                    data.append("-")
                    flag=1
                # drops the complete data if there is an error
                # Adding data to a collection
                
                if flag==1:
                    Errors["ziarul"].append(err)
                
                collection.append(data)
                
                # for x in data:
                #     print(x)
                # print()
        
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
            emptydataframe("ziarul", df)
                # df  = link_correction(df)
                
            return df
        
        except:
            not_working_functions.append("ziarul")
            print("ziarul not working")

    def vir(keyword):
        try:
            print("vir")
            Errors["vir"]=[]


            url = f"https://vir.com.vn/search_enginer.html?p=search&q={keyword}"
            domain_url = "https://vir.com.vn/"
            headers = {
                "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10.15; rv:78.0) Gecko/20100101 Firefox/78.0",
                "accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.9",
                'sec-fetch-site': 'none',
                'sec-fetch-mode': 'navigate',
                'sec-fetch-user': '?1',
                'sec-fetch-dest': 'document',
                'accept-language': 'en-GB,en-US;q=0.9,en;q=0.8',
            }


            links=[]
            try:
                page = requests.get(url, headers=headers)
                soup = BeautifulSoup(page.content, "html.parser")
            except:
                print("vir not working")
                not_working_functions.append('vir')
                err = "Main link did not load: " + url
                Errors["vir"].append(err)
                return


            try:

                all_divs = soup.find_all("div",{"class":"article"})
                for div in all_divs:
                    links.append(domain_url+div.a["href"])
                   
                    
            except:
                if len(links)==0:
                    print("vir not working")
                    not_working_functions.append('vir')
                    Errors["vir"].append("Extraction of link not working.")
                    return

            # Remove duplicates
            links = list(set(links))

            # links # Debugging - if link array is generated
            collection = []
            scrapper_name = "vir"

            def getarticles(link):

                flag=0
                err=err_dict()
                try:
                    l_page = requests.get(link, headers=headers)
                    l_soup = BeautifulSoup(l_page.content, 'html.parser')
                except:
                    err["link"]="Link not working: "+link
                    Errors["vir"].append(err)
                    return

                data = []

                # Scraping the heading
                #h1_ele = l_soup.find("h1", {"class": h1_class})

                try:
                    title_ele =l_soup.find("h1")
                    title_text = title_ele.text

                    data.append(title_text)
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

                    date_ele = l_soup.find("span",{"class":"date-detail f-13 lt"})
                    date_text = date_ele.text
                    l=date_text.split(" ")
                    date_text=l[1].strip(",")+"-"+l[0]+"-"+l[2]
                   
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
                   para_ele = (l_soup.findAll("div",{"class":"htmlContent clearfix"}))[-1]
                   para_text = para_ele.text
                   para_text = para_text.strip("\n ")
                   data.append(para_text)
                    # Need to make this better
                except:
                    err["link"]=link
                    err['text']="Error"
                    data.append("-")
                    flag=1
                  # drops the complete data if there is an error
                # Adding data to a collection

                if flag==1:
                    Errors["vir"].append(err)

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
            emptydataframe("vir", df)
            # df  = link_correction(df)

            return df

        except:
            not_working_functions.append("vir")
            print("vir not working")


    def adgully(keyword):
        try:
            print("adgully")
            Errors["adgully"]=[]


            url = f"https://www.adgully.com/search/?keyword={keyword}"
            domain_url = "https://www.adgully.com/"
            headers = {
                "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10.15; rv:78.0) Gecko/20100101 Firefox/78.0",
                "accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.9",
                'sec-fetch-site': 'none',
                'sec-fetch-mode': 'navigate',
                'sec-fetch-user': '?1',
                'sec-fetch-dest': 'document',
                'accept-language': 'en-GB,en-US;q=0.9,en;q=0.8',
            }


            links=[]
            try:
                page = requests.get(url, headers=headers)
                soup = BeautifulSoup(page.content, "html.parser")
            except:
                print("adgully not working")
                not_working_functions.append('adgully')
                err = "Main link did not load: " + url
                Errors["adgully"].append(err)
                return


            try:

                all_divs = soup.find_all("div",{"class":"read-share-overlay"})
                for div in all_divs:
                    links.append(domain_url+div.a["href"])
                   
                    
            except:
                if len(links)==0:
                    print("adgully not working")
                    not_working_functions.append('adgully')
                    Errors["adgully"].append("Extraction of link not working.")
                    return

            # Remove duplicates
            links = list(set(links))

            # links # Debugging - if link array is generated
            collection = []
            scrapper_name = "adgully"

            def getarticles(link):

                flag=0
                err=err_dict()
                try:
                    l_page = requests.get(link, headers=headers)
                    l_soup = BeautifulSoup(l_page.content, 'html.parser')
                except:
                    err["link"]="Link not working: "+link
                    Errors["adgully"].append(err)
                    return

                data = []

                # Scraping the heading
                #h1_ele = l_soup.find("h1", {"class": h1_class})

                try:
                    title_ele =l_soup.find("h1")
                    title_text = title_ele.text

                    data.append(title_text)
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

                    date_ele = l_soup.find("time",{"class":"post-date updated"})
                    date_text = date_ele.text
                    date_text=date_text.strip("\n")
                    l=date_text.split(" ")
                    date_text=l[1].strip(",")+"-"+l[0]+"-"+l[2]
                   
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
                   para_ele = (l_soup.findAll("div",{"class":"post_data"}))[-1]
                   para_text = para_ele.text
                   para_text = para_text.strip("\n ")
                   data.append(para_text)
                    # Need to make this better
                except:
                    err["link"]=link
                    err['text']="Error"
                    data.append("-")
                    flag=1
                  # drops the complete data if there is an error
                # Adding data to a collection

                if flag==1:
                    Errors["adgully"].append(err)

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
            emptydataframe("adgully", df)
            # df  = link_correction(df)

            return df

        except:
            not_working_functions.append("adgully")
            print("adgully not working")

    def theprint(keyword):
        try:
            print("theprint")
            Errors["theprint"]=[]
            
          
            url = f"https://theprint.in/?s={keyword}"
            domain_url = "https://theprint.in/"
            headers = {
                "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10.15; rv:78.0) Gecko/20100101 Firefox/78.0",
                "accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.9",
                'sec-fetch-site': 'none',
                'sec-fetch-mode': 'navigate',
                'sec-fetch-user': '?1',
                'sec-fetch-dest': 'document',
                'accept-language': 'en-GB,en-US;q=0.9,en;q=0.8',
            }
            # count =2
            collection = []
            # while True:
            #     if not count:
            #         break   
            links=[]
            try:
                page = requests.get(url, headers=headers)
                soup = BeautifulSoup(page.content, "html.parser")
            except:
                print("theprint not working")
                not_working_functions.append('theprint')
                err = "Main link did not load: " + url
                Errors["theprint"].append(err)
                return
            
            # next_link = soup.find('a', attrs={'aria-label': 'Next'})
            
            # url =domain_url+ next_link['href'][1:]
            # print(url)
                
            # count-=1
            # print(count)
            
            try:
                div_id = soup.find_all("div",{"class":"td-module-thumb"})
                for div in div_id :
                    a_link= div.find("a")
                    link=a_link['href']
                                            # Checking the link if it is a relative link
                    if link[0] == '/':
                        link = domain_url + link[1:]

                                            # Filtering advertaisment links
                    link_start = domain_url
                    if link.startswith(link_start):
                         links.append(link)
                                    # Remove duplicates
                links = list(set(links))
                
            except:
                if len(links)==0:
                    print("theprint not working")
                    not_working_functions.append('theprint')
                    Errors["theprint"].append("Extraction of link not working.")
                    return
                        
            
            # links # Debugging - if link array is generated
            # collection = []
            scrapper_name = "theprint"
            
            def getarticles(link):
                
                # print(link)
                flag=0
                err=err_dict()
                try:
                    l_page = requests.get(link, headers=headers)
                    l_soup = BeautifulSoup(l_page.content, 'html.parser')
                except:
                    err["link"]="Link not working: "+link
                    Errors["theprint"].append(err)
                    return
                
                data = []
                
                # Scraping the heading
                #h1_ele = l_soup.find("h1", {"class": h1_class})
                
                try:
                    title_ele =l_soup.find("title")
                    title_text = title_ele.text
                    # print(title_text)
                    data.append(title_text)
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
                    date_elems = l_soup.find_all('time')
                    # print(date_elems)
                    if date_elems:
                        date_str = date_elems[0].text
                        # print(date_str)
                    date_obj = datetime.strptime(date_str, '%d %B, %Y %I:%M %p %Z')
                    formatted_date = date_obj.strftime("%d-%m-%Y")
                    # print(formatted_date)                    
                    data.append(formatted_date)
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
                    para_eles = l_soup.find_all("p")
                    p_text =""
                    for para in para_eles:
                        para_text = para.text
                        # print(para_text)
                        p_text +=para_text
                    data.append(p_text)  # Need to make this better
                except:
                    err["link"]=link
                    err['text']="Error"
                    data.append("-")
                    flag=1
                # drops the complete data if there is an error
                # Adding data to a collection
                
                if flag==1:
                    Errors["theprint"].append(err)
                
                collection.append(data)
                
                # for x in data:
                #     print(x)
                # print()
        
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
            emptydataframe("theprint", df)
                # df  = link_correction(df)
                
            return df
        
        except:
            not_working_functions.append("theprint")
            print("theprint not working")

    def prnewswire(keyword):
        try:
            print("prnewswire")
            Errors["prnewswire"]=[]


            url = f"https://www.prnewswire.com/search/all/?keyword={keyword}"
            domain_url = "https://www.prnewswire.com/"
            headers = {
                "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10.15; rv:78.0) Gecko/20100101 Firefox/78.0",
                "accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.9",
                'sec-fetch-site': 'none',
                'sec-fetch-mode': 'navigate',
                'sec-fetch-user': '?1',
                'sec-fetch-dest': 'document',
                'accept-language': 'en-GB,en-US;q=0.9,en;q=0.8',
            }


            links=[]
            try:
                page = requests.get(url, headers=headers)
                soup = BeautifulSoup(page.content, "html.parser")
            except:
                print("prnewswire not working")
                not_working_functions.append('prnewswire')
                err = "Main link did not load: " + url
                Errors["prnewswire"].append(err)
                return


            try:

                all_divs = soup.find_all("a",{"class":"news-release"})
                for div in all_divs:
                    links.append(domain_url+div["href"])
                   
                    
            except:
                if len(links)==0:
                    print("prnewswire not working")
                    not_working_functions.append('prnewswire')
                    Errors["prnewswire"].append("Extraction of link not working.")
                    return

            # Remove duplicates
            links = list(set(links))

            # links # Debugging - if link array is generated
            collection = []
            scrapper_name = "prnewswire"

            def getarticles(link):

                flag=0
                err=err_dict()
                try:
                    l_page = requests.get(link, headers=headers)
                    l_soup = BeautifulSoup(l_page.content, 'html.parser')
                except:
                    err["link"]="Link not working: "+link
                    Errors["prnewswire"].append(err)
                    return

                data = []

                # Scraping the heading
                #h1_ele = l_soup.find("h1", {"class": h1_class})

                try:
                    title_ele =l_soup.find("h1")
                    title_text = title_ele.text

                    data.append(title_text)
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

                    date_ele = l_soup.find("p",{"class":"mb-no"})
                    date_text = date_ele.text
                    date_text=date_text.strip("\n")
                    l=date_text.split(" ")
                    date_text=l[1].strip(",")+"-"+l[0]+"-"+l[2].strip(",")
                   
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
                    para_ele = (l_soup.findAll("article",{"class":"news-release inline-gallery-template"}))[-1]
                    para_text = para_ele.text
                    para_text = para_text.strip("\n ")
                    data.append(para_text)
                    # Need to make this better
                except:
                    err["link"]=link
                    err['text']="Error"
                    data.append("-")
                    flag=1
                  # drops the complete data if there is an error
                # Adding data to a collection

                if flag==1:
                    Errors["prnewswire"].append(err)

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
            emptydataframe("prnewswire", df)
            # df  = link_correction(df)

            return df

        except:
            not_working_functions.append("prnewswire")
            print("prnewswire not working")

    def pulsenews():
        try:
            print("pulsenews")
            Errors["pulsenews"]=[]
            
          
            url = f"https://pulse.zerodha.com/"
            # domain_url = "https://pulsenews.in/"
            headers = {
                "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10.15; rv:78.0) Gecko/20100101 Firefox/78.0",
                "accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.9",
                'sec-fetch-site': 'none',
                'sec-fetch-mode': 'navigate',
                'sec-fetch-user': '?1',
                'sec-fetch-dest': 'document',
                'accept-language': 'en-GB,en-US;q=0.9,en;q=0.8',
            }
            # count =2
            collection = []
            # while True:
            #     if not count:
            #         break   
            links=[]
            try:
                page = requests.get(url, headers=headers)
                soup = BeautifulSoup(page.content, "html.parser")
            except:
                print("pulsenews not working")
                not_working_functions.append('pulsenews')
                err = "Main link did not load: " + url
                Errors["pulsenews"].append(err)
                return
            
            
            
            try:
                
                a_link= soup.find_all("a")
                ipo_links = [link for link in a_link if 'ipo' in link.get('href') or 'IPO' in link.get('href') or 'initial public offering' in link.text]
                
                
                
                for link in ipo_links:
                    domain = link.get('href')
                    if 'facebook.com' not in domain and 'twitter.com' not in domain:
                        links.append(link.get('href'))
                                    # Remove duplicates
                links = list(set(links))
                
            except:
                if len(links)==0:
                    print("pulsenews not working")
                    not_working_functions.append('pulsenews')
                    Errors["pulsenews"].append("Extraction of link not working.")
                    return
                        
            
          
            scrapper_name = "pulsenews"
            
            def getarticles(link):
                
                # print(link)
                flag=0
                err=err_dict()
                try:
                    article = Article(link)
                    article.download()
                    article.parse()
                except:
                    err["link"]="Link not working: "+link
                    Errors["pulsenews"].append(err)
                    return
                
                data = []
                
                # Scraping the heading
                #h1_ele = l_soup.find("h1", {"class": h1_class})
                
                try:
                    # print(article.title)
                    data.append(article.title)
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
                    
                    pub = date_correction_for_newspaper3k(article.publish_date)
                    # print(article.publish_date)
                    data.append(pub)
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
                    data.append(article.text)
                except:
                    err["link"]=link
                    err['text']="Error"
                    data.append("-")
                    flag=1
                # drops the complete data if there is an error
                # Adding data to a collection
                
                if flag==1:
                    Errors["pulsenews"].append(err)
                
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
                                        'title', 'link', 'publish_date','scraped_date' ,'text'])
                
                
                # print(df) # For debugging. To check if df is created
                # print(err_logs) # For debugging - to check if any errors occoured
            df = FilterFunction(df)
            emptydataframe("pulsenews", df)
                # df  = link_correction(df)
                
            return df
        
        except:
            not_working_functions.append("pulsenews")
            print("pulsenews not working")
    
    def marketwatch(keyword):
        try:
            print("marketwatch")
            Errors["marketwatch"]=[]


            url = f"https://www.marketwatch.com/investing/fund/{keyword}"
            domain_url = "https://www.marketwatch.com/"
            headers = {
                "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10.15; rv:78.0) Gecko/20100101 Firefox/78.0",
                "accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.9",
                'sec-fetch-site': 'none',
                'sec-fetch-mode': 'navigate',
                'sec-fetch-user': '?1',
                'sec-fetch-dest': 'document',
                'accept-language': 'en-GB,en-US;q=0.9,en;q=0.8',
            }


            links=[]
            try:
                page = requests.get(url, headers=headers)
                soup = BeautifulSoup(page.content, "html.parser")
            except:
                print("marketwatch not working")
                not_working_functions.append('marketwatch')
                err = "Main link did not load: " + url
                Errors["marketwatch"].append(err)
                return


            try:

                for divtag in soup.find_all("h3",{"class":"article__headline"}):
                    for a in divtag.find_all("a", href=True):
                        link = a["href"]  # Gets the link

                        if link[0] == '/':
                                link = domain_url + link[1:]
                                            # Filtering advertaisment links
                        link_start = domain_url
                        if link.startswith(link_start):
                            links.append(link)
                                    # Remove duplicates
                links = list(set(links))
                   
                    
            except:
                if len(links)==0:
                    print("marketwatch not working")
                    not_working_functions.append('marketwatch')
                    Errors["marketwatch"].append("Extraction of link not working.")
                    return

            # Remove duplicates
            links = list(set(links))

            # links # Debugging - if link array is generated
            collection = []
            scrapper_name = "marketwatch"

            def getarticles(link):

                flag=0
                err=err_dict()
                try:
                    l_page = requests.get(link, headers=headers)
                    l_soup = BeautifulSoup(l_page.content, 'html.parser')
                except:
                    err["link"]="Link not working: "+link
                    Errors["marketwatch"].append(err)
                    return

                data = []

                # Scraping the heading
                #h1_ele = l_soup.find("h1", {"class": h1_class})

                try:
                    title_ele =l_soup.find("h1",{"class":"article__headline"})
                    title_text = title_ele.text

                    data.append(title_text)
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

                    date_ele = l_soup.find("time")
                    date_text = date_ele.text
                    date_text=date_text.strip("\n")
                    date_text=date_text.strip(" ")
                    l=date_text.split(" ")
                    if(l[0]=="Last"):
                        date_text=l[3].strip(",")+"-"+l[2].strip(".")+"-"+l[4]
                    else:
                        date_text=l[2].strip(",")+"-"+l[1].strip(".")+"-"+l[3]
                   
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
                    para_ele = (l_soup.findAll("div",{"itemprop":"articleBody"}))[-1]
                    para_text = para_ele.text
                    para_text = para_text.strip("\n ")
                    data.append(para_text)
                    # Need to make this better
                except:
                    err["link"]=link
                    err['text']="Error"
                    data.append("-")
                    flag=1
                  # drops the complete data if there is an error
                # Adding data to a collection

                if flag==1:
                    Errors["marketwatch"].append(err)

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
            emptydataframe("marketwatch", df)
            # df  = link_correction(df)

            return df

        except:
            not_working_functions.append("marketwatch")
            print("marketwatch not working")

    def futures_tradingcharts(keyword):
        try:
            print("futures_tradingcharts")
            Errors["futures_tradingcharts"]=[]


            url = f"https://futures.tradingcharts.com/search.php?keywords={keyword}&futures=1"
            domain_url = "https://futures.tradingcharts.com"
            headers = {
                "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10.15; rv:78.0) Gecko/20100101 Firefox/78.0",
                "accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.9",
                'sec-fetch-site': 'none',
                'sec-fetch-mode': 'navigate',
                'sec-fetch-user': '?1',
                'sec-fetch-dest': 'document',
                'accept-language': 'en-GB,en-US;q=0.9,en;q=0.8',
            }


            links=[]
            try:
                page = requests.get(url, headers=headers)
                soup = BeautifulSoup(page.content, "html.parser")
            except:
                print("futures_tradingcharts not working")
                not_working_functions.append('futures_tradingcharts')
                err = "Main link did not load: " + url
                Errors["futures_tradingcharts"].append(err)
                return


            try:

                all_divs = soup.find_all("div",{"class":"clUnSeResultItem"})
                for div in all_divs:
                    links.append("https:"+div.a["href"])

            except:
                if len(links)==0:
                    print("futures_tradingcharts not working")
                    not_working_functions.append('futures_tradingcharts')
                    Errors["futures_tradingcharts"].append("Extraction of link not working.")
                    return

            # Remove duplicates
            links = list(set(links))

            # links # Debugging - if link array is generated
            collection = []
            scrapper_name = "futures_tradingcharts"

            def getarticles(link):

                flag=0
                err=err_dict()
                try:
                    l_page = requests.get(link, headers=headers)
                    l_soup = BeautifulSoup(l_page.content, 'html.parser')
                except:
                    err["link"]="Link not working: "+link
                    Errors["futures_tradingcharts"].append(err)
                    return

                data = []

                # Scraping the heading
                #h1_ele = l_soup.find("h1", {"class": h1_class})

                try:
                    title_ele =l_soup.find("h2")
                    title_text = title_ele.text

                    data.append(title_text)
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

                    date_ele = l_soup.find("i")
                    date_text = date_ele.text
                    date_text=date_text.strip("\n")
                    l=date_text.split(",")
                    l1=l[0].split(" ")
                    l2=l[1].split("(")
                    if(l1[2].isnumeric()):
                        date_text=l1[2]+"-"+l1[1]+"-"+l2[0]
                    else:
                        date_text=""
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
                   para_ele = (l_soup.findAll("div",{"class":"news_story m-cellblock m-padding"}))[-1]
                   para_text = para_ele.text
                   para_text = para_text.strip("\n ")
                   data.append(para_text)
                    # Need to make this better
                except:
                    err["link"]=link
                    err['text']="Error"
                    data.append("-")
                    flag=1
                  # drops the complete data if there is an error
                # Adding data to a collection

                if flag==1:
                    Errors["futures_tradingcharts"].append(err)

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
            emptydataframe("futures_tradingcharts", df)
            # df  = link_correction(df)

            return df

        except:
            not_working_functions.append("futures_tradingcharts")
            print("futures_tradingcharts not working")

    def zawya(keyword):
        try:
            print("zawya")
            Errors["zawya"]=[]
            
          
            url = f"https://www.zawya.com/en/search?q={keyword}"
            domain_url = "https://www.zawya.com/"
            headers = {
                "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10.15; rv:78.0) Gecko/20100101 Firefox/78.0",
                "accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.9",
                'sec-fetch-site': 'none',
                'sec-fetch-mode': 'navigate',
                'sec-fetch-user': '?1',
                'sec-fetch-dest': 'document',
                'accept-language': 'en-GB,en-US;q=0.9,en;q=0.8',
            }
            
            links=[]
            try:
                page = requests.get(url, headers=headers)
                soup = BeautifulSoup(page.content, "html.parser")
            except:
                print("zawya not working")
                not_working_functions.append('zawya')
                err = "Main link did not load: " + url
                Errors["zawya"].append(err)
                return
            
            # print(url)
            try:
                div_id = soup.find_all("h2",{"class": "teaser-title"})
                for div in div_id :
                    a_link= div.find("a")
                    link=a_link['href']
                                            # Checking the link if it is a relative link
                    if link[0] == '/':
                        link = domain_url + link

                    #                         # Filtering advertaisment links
                    # link_start = domain_url
                    # if link.startswith(link_start):
                    links.append(link)
                                    # Remove duplicates
                links = list(set(links))
                
            except:
                if len(links)==0:
                    print("zawya not working")
                    not_working_functions.append('zawya')
                    Errors["zawya"].append("Extraction of link not working.")
                    return
                        
            
            # links # Debugging - if link array is generated
            collection = []
            scrapper_name = "zawya"
            
            def getarticles(link):

                # print(link)
                flag=0
                err=err_dict()
                try:
                    l_page = requests.get(link, headers=headers)
                    l_soup = BeautifulSoup(l_page.content, 'html.parser')
                except:
                    err["link"]="Link not working: "+link
                    Errors["zawya"].append(err)
                    return
                
                data = []
                
                # Scraping the heading
                #h1_ele = l_soup.find("h1", {"class": h1_class})
                
                try:
                    title_ele = l_soup.find("title")
                    title_text = title_ele.text
                    # print(title_text)
                    data.append(title_text)
                
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
                    date_ele =l_soup.find("div",{"class":"article-date"})
                    date_text = date_ele.text
                   
                    # print(date_text)


                    # Convert datetime object to desired date format
                    date_obj = datetime.strptime(date_text, '%B %d, %Y')
                    formatted_date = date_obj.strftime('%d-%m-%Y')

                    # print(formatted_date)

                    data.append(formatted_date)
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
                    article_body = l_soup.find("script", {"type": "application/ld+json"}).string
                    # print(article_body)
                    article_body = json.loads(article_body)
                    article_body = article_body["articleBody"]

                    # print(article_body)
                                     
                    data.append(article_body)  # Need to make this better
                except:
                    err["link"]=link
                    err['text']="Error"
                    data.append("-")
                    flag=1
                  # drops the complete data if there is an error
                # Adding data to a collection
                
                if flag==1:
                    Errors["zawya"].append(err)
                
                collection.append(data)
                
                # for x in data:
                #     print(x)
                # print()
           
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
            emptydataframe("zawya", df)
            # df  = link_correction(df)
            
            return df
        
        except:
            not_working_functions.append("zawya")
            print("zawya not working")

    def businesstoday(keyword):
        try:
            print("businesstoday")
            Errors["businesstoday"]=[]
            
          
            url = f"https://www.businesstoday.in/topic/{keyword}"
            domain_url = "https://www.businesstoday.in/"
            headers = {
                "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10.15; rv:78.0) Gecko/20100101 Firefox/78.0",
                "accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.9",
                'sec-fetch-site': 'none',
                'sec-fetch-mode': 'navigate',
                'sec-fetch-user': '?1',
                'sec-fetch-dest': 'document',
                'accept-language': 'en-GB,en-US;q=0.9,en;q=0.8',
            }
            
            links=[]
            try:
                page = requests.get(url, headers=headers)
                soup = BeautifulSoup(page.content, "html.parser")
            except:
                print("businesstoday not working")
                not_working_functions.append('businesstoday')
                err = "Main link did not load: " + url
                Errors["businesstoday"].append(err)
                return
            
            # print(url)
            try:
                div_id = soup.find_all("h2")
                for div in div_id :
                    a_link= div.find("a")
                    link=a_link['href']
                                            # Checking the link if it is a relative link
                    if link[0] == '/':
                        link = domain_url + link[1:]

                    #                         # Filtering advertaisment links
                    link_start = domain_url
                    if link.startswith(link_start):
                        links.append(link)
                                    # Remove duplicates
                links = list(set(links))
                
            except:
                if len(links)==0:
                    print("businesstoday not working")
                    not_working_functions.append('businesstoday')
                    Errors["businesstoday"].append("Extraction of link not working.")
                    return
                        
            
            # links # Debugging - if link array is generated
            collection = []
            scrapper_name = "businesstoday"
            
            def getarticles(link):

                # print(link)
                flag=0
                err=err_dict()
                try:
                    l_page = requests.get(link, headers=headers)
                    l_soup = BeautifulSoup(l_page.content, 'html.parser')
                except:
                    err["link"]="Link not working: "+link
                    Errors["businesstoday"].append(err)
                    return
                
                data = []
                
                # Scraping the heading
                #h1_ele = l_soup.find("h1", {"class": h1_class})
                
                try:
                    title_ele = l_soup.find("title")
                    title_text = title_ele.text
                    # print(title_text)
                    data.append(title_text)
                
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
                    date_ele =l_soup.find("div",{"class":"brand-detial-main"})
                    date_ele_next = date_ele.find("li")
                    date_text = date_ele_next.text.strip()
                   
                    # print(date_text)


                    # Convert datetime object to desired date format
                    date_obj = datetime.strptime(date_text, "Updated %b %d, %Y, %I:%M %p IST")
                    formatted_date = date_obj.strftime("%d-%m-%Y")

                    # print(formatted_date)

                    data.append(formatted_date)
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
                    para_eles = l_soup.find_all("p")
                    p_text =""
                    for para in para_eles:
                        para_text = para.text
                        # print(para_text)
                        p_text +=para_text
                    data.append(p_text)  # Need to make this better
                
                except:
                    err["link"]=link
                    err['text']="Error"
                    data.append("-")
                    flag=1
                  # drops the complete data if there is an error
                # Adding data to a collection
                
                if flag==1:
                    Errors["businesstoday"].append(err)
                
                collection.append(data)
                
                # for x in data:
                #     print(x)
                # print()
           
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
            emptydataframe("businesstoday", df)
            # df  = link_correction(df)
            
            return df
        
        except:
            not_working_functions.append("businesstoday")
            print("businesstoday not working")


    #                                  Final
    #df149=bankok_post("ipo")
    #df150=bankok_post("fpo")
    #df151=bankok_post("spac")
    
    search_list=[]
    
    keywords_for_search_engines=["首次公开上市", "IPO", "FPO", "SPAC", "新規株式公開", "eyes for IPO", "Planning for IPO", "lising", "files for IPO", "plans to list"]
    
    for search in keywords_for_search_engines:
        df14=bing_search(search)
        search_list.append(df14)
        df14=google_news(search)
        search_list.append(df14)
    
    df14=pd.concat(search_list)
    df14.drop_duplicates(subset=["link"])
    df14.drop_duplicates(subset=["title"])
    
    
    df55=stock_eastmoney()
    df1=korea()
    df2=proactive("ipo")
    df3=gulfbusiness("ipo")
    #df138=gulfbusiness("fpo")
    #df139=gulfbusiness("spac")
    df4=investmentu("ipo")
    #df136=investmentu("fpo")
    #df137=investmentu("spac")
    df5=einnews()
    df6=businessinsider("ipo")
    #df132=businessinsider("fpo")
    #df133=businessinsider("spac")
    df7=Reuters("ipo")
    #df8=Reuters("pre ipo")
    #df9=Reuters("Initial Public Offering")
    df11=defenseworld("ipo")
    #df130=defenseworld("fpo")
    #df131=defenseworld("spac")
    df12=technode("ipo")
    #df128=technode("fpo")
    #df129=technode("spac")
    df13=globenewswire("ipo")
    #df126=globenewswire("fpo")
    #df127=globenewswire("spac")
    df15=autonews("ipo")
    #df124=autonews("fpo")
    #df125=autonews("spac")
    df16=capacitymedia("ipo")
    ##df122=capacitymedia("fpo")
    #df123=capacitymedia("spac")
    df17=kenyanwallstreet("ipo")
    #df120=kenyanwallstreet("fpo")
    #df121=kenyanwallstreet("spac")
    df18=thesundaily("ipo")
    #df118=thesundaily("fpo")
    #df119=thesundaily("spac")
    df19=digitaljournal("ipo")
    ##df116=digitaljournal("fpo")
    #df117=digitaljournal("spac")
    df20=asiafinancial("ipo")
    #df114=asiafinancial("fpo")
    #df115=asiafinancial("spac")
    df21=stockhead("ipo")
    #df112=stockhead("fpo")
    #df113=stockhead("spac")
    df22=koreajoongangdaily("ipo")
    #df110=koreajoongangdaily("fpo")
    #df111=koreajoongangdaily("spac")
    df23=upstreamonline("ipo")
    #df108=upstreamonline("fpo")
    #df109=upstreamonline("spac")
    df24=etfdailynews("ipo")
    #df106=etfdailynews("fpo")
    #df107=etfdailynews("spac")
    df25=splash247("ipo")
    ##df104=splash247("fpo")
    #df105=splash247("spac")
    df26=brisbanetimes("ipo")
    #df102=brisbanetimes("fpo")
    #df103=brisbanetimes("spac")
    df27=zdnet("ipo")
    ##df100=zdnet("fpo")
    #df101=zdnet("spac")
    df28=manilatimes("ipo")
    #df98=manilatimes("fpo")
    #df99=manilatimes("spac")
    df29=investmentweek("ipo")
    #df96=investmentweek("fpo")
    #df97=investmentweek("spac")
    df30=sundayobserver("ipo")
    #df94=sundayobserver("fpo")
    #df95=sundayobserver("spac")
    df31=reinsurancene("ipo")
    #df92=reinsurancene("fpo")
    #df93=reinsurancene("spac")
    df32=insideretail("ipo")
    #df90=insideretail("fpo")
    #df91=insideretail("spac")
    df33=EconomicTimes()
    df34=seenews("ipo")
    #df88=seenews("fpo")
    #df89=seenews("spac")
    df35=shorttermrentalz("ipo")
    #df86=shorttermrentalz("fpo")
    #df87=shorttermrentalz("spac")
    df36=arabnews("ipo")
    ##df84=arabnews("fpo")
    #df85=arabnews("spac")
    df37=macaubusiness("ipo")
    #df38=macaubusiness("fpo")
    #df39=macaubusiness("spac")
    df40=vietnamnet("ipo")
    #df41=vietnamnet("fpo")
    #df42=vietnamnet("spac")
    df43=thesydneymorningherald("ipo")
    #df44=thesydneymorningherald("fpo")
    #df45=thesydneymorningherald("spac")
    df46=economictimes("ipo")
    ##df47=economictimes("fpo")
    #df48=economictimes("spac")
    df49=nzherald("ipo")
    #df50=nzherald("fpo")
    #df51=nzherald("spac")
    df52=albaniandailynews("ipo")
    #df53=albaniandailynews("fpo")
    #df54=albaniandailynews("spac")
    #df56=straittimes()
    df57=financialpost("ipo")
    #df58=financialpost("fpo")
    #df59=financialpost("spac")
    df60=nikkei("ipo")
    #df61=nikkei("fpo")
    #df62=nikkei("spac")
    df63=albawaba("ipo")
    #df64=albawaba("fpo")
    #df65=albawaba("spac")
    df66=theaustralianfinancialreview("ipo")
    #df67=theaustralianfinancialreview("fpo")
    #df68=theaustralianfinancialreview("spac")
    df69=trendnewsagency("ipo")
    #df70=trendnewsagency("fpo")
    #df71=trendnewsagency("spac")
    df72=globallegalchronicle("ipo")
    #df73=globallegalchronicle("fpo")
    #df74=globallegalchronicle("spac")
    df75=ewnews("ipo")
    #df76=ewnews("fpo")
    #df77=ewnews("spac")
    df78=dw("ipo")
    #df79=dw("fpo")
    #df80=dw("spac")
    df81=uzdaily("ipo")
    #df82=uzdaily("fpo")
    #df83=uzdaily("spac")
    

    df140=kedglobal("ipo")
    #df141=kedglobal("fpo")
    #df142=kedglobal("spac")
    #df143=pymnts("ipo")
    ##df144=pymnts("fpo")
    #df145=pymnts("spac")
    df146=timesofindia("ipo")
    #df147=timesofindia("fpo")
    #df148=timesofindia("spac")
    df152=tradingcharts("ipo")
    #df153=tradingcharts("fpo")
    #df154=tradingcharts("spac")
    df155=kontan("ipo")
    ##df156=kontan("fpo")
    #df157=kontan("spac")
    df158=tagesschau("ipo")
    #df159=tagesschau("fpo")
    #df160=tagesschau("spac")
    df161=afr("ipo")
    #df162=afr("fpo")
    #df163=afr("spac")
    df164=asiainsurancereview("ipo")
    #df165=asiainsurancereview("fpo")
    #df166=asiainsurancereview("spac")
    df167=swissinfo("ipo")
    #df168=swissinfo("fpo")
    #df169=swissinfo("spac")
    df170=jamaicaobserver("ipo")
    #df171=jamaicaobserver("fpo")
    #df172=jamaicaobserver("spac")
    df173=energyvoice("ipo")
    #df174=energyvoice("fpo")
    #df175=energyvoice("spac")
    df176=african_markets("ipo")
    #df177=african_markets("fpo")
    #df178=african_markets("spac")
    df179=newindianexpress("ipo")
    #df180=newindianexpress("fpo")
    #df181=newindianexpress("spac")
    df182=ndtv("ipo")
    ##df183=ndtv("fpo")
    #df184=ndtv("spac")
    df185=theepochtimes("ipo")
    #df186=theepochtimes("fpo")
    #df187=theepochtimes("spac")
    df188=malaymail("ipo")
    #df189=malaymail("fpo")
    #df190=malaymail("spac")
    df191=nbdpress("ipo")
    #df192=nbdpress("fpo")
    #df193=nbdpress("spac")
    df194=gulftoday("ipo")
    #df195=gulftoday("fpo")
    #df196=gulftoday("spac")
    df197=emirates247("ipo")
    ##df198=emirates247("fpo")
    #df199=emirates247("spac")
    df200=manilabulletin("ipo")
    #df201=manilabulletin("fpo")
    #df202=manilabulletin("spac")
    df203=moneycontrol("ipo")
    df204=businessoutreach("ipo")
    #df205=businessoutreach("fpo")
    #df206=businessoutreach("spac")
    df207=gccbusinessnews("ipo")
    #df208=gccbusinessnews("fpo")
    #df209=gccbusinessnews("spac")
    df210=saltwire("ipo")
    #df211=saltwire("fpo")
    #df212=saltwire("spac")
    df213=manilastandard("ipo")
    #df214=manilastandard("fpo")
    #df215=manilastandard("spac")
    df216=tradewindsnews("ipo")
    ##df217=tradewindsnews("fpo")
    #df218=tradewindsnews("spac")
    df219=khaleejtimes("ipo")
    #df220=khaleejtimes("fpo")
    #df221=khaleejtimes("spac")
    df222=albayan("ipo")
    #df223=albayan("fpo")
    #df224=albayan("spac")
    df225=ipocentral("ipo")
    #df226=ipocentral("fpo")
    #df227=ipocentral("spac")
    df228=kmib("ipo")
    #df229=kmib("fpo")
    #df230=kmib("spac")
    df231=seoul("ipo")
    #df232=seoul("fpo")
    #df233=seoul("spac")
    df234=headline_daily("ipo")
    #df235=headline_daily("fpo")
    #df236=headline_daily("spac")
    df237=timesofoman("ipo")
    #df238=timesofoman("fpo")
    #df239=timesofoman("spac")
    df240=aljazeera("ipo")
    #df241=aljazeera("fpo")
    #df242=aljazeera("spac")
    df243=a_163("ipo")
    #df244=a_163("fpo")
    #df245=a_163("spac")
    df246=montsame("ipo") 
    #df247=montsame("fpo") 
    #df248=montsame("spac")
    df249=omanobserver("ipo")
    #df250=omanobserver("fpo")
    #df251=omanobserver("spac") 
    df252=thearabianstories("ipo")
    #df253=thearabianstories("fpo")
    #df254=thearabianstories("spac")
    df255=romania_insider("ipo")
    #df256=romania_insider("fpo")
    #df257=romania_insider("spac")
    df258=ziarul("ipo")
    #df259=ziarul("fpo")
    #df260=ziarul("spac")
    df261=vir("ipo")
    #df262=vir("fpo")
    ##df263=vir("spac")
    df264=adgully("ipo")
    #df265=adgully("fpo")
    #df266=adgully("spac")
    df257=theprint("ipo")
    #df258=theprint("fpo")
    #df259=theprint("spac")
    df260=prnewswire("ipo")
    #df261=prnewswire("fpo")
    #df262=prnewswire("spac")
    df263=pulsenews()
    df264=marketwatch("ipo")
    #df265=marketwatch("fpo")
    #df266=marketwatch("spac")
    df267=futures_tradingcharts("ipo")
    #df268=futures_tradingcharts("fpo")
    #df269=futures_tradingcharts("spac")
    df270=zawya("ipo")
    #df271=zawya("fpo")
    #df272=zawya("spac")
    df273=businesstoday("ipo")
    #df274=businesstoday("fpo")
    #df275=businesstoday("spac")




    df_final_1 = [df170, df1, df2, df3, df4, df5, df6, df7, df11, df12, df13, df14, df15, df16, df17, df18, df19, df20 , df21, df22, df23, df24, df25, df26, df27, df28, df29, df30, df31, df32, df33, df34, df35, df36, df37 , df43,  df46, df49, df52,  df55, df57,  df60,  df63,  df66,  df69,  df72,  df75,  df78,  df81, df140,df146, df152,  df155,  df158,  df161,  df164,  df167,  df173,  df176,  df179,  df182,  df185,  df40,  df188,  df191,  df194,  df197,  df200,  df203, df207,  df210,  df213,  df216,  df219, df222,df225,df228,df231,df234,df237,df240,df243,df246,df249,df252,df255,df257,df258,df260,df261,df263,df264,df257,df258,df260,df261,df263,df264,df267,df270,df273]
    
    
       
    
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
    multilex_scraper(r"C:\Users\ujwal\OneDrive\Desktop\abc",r"C:\Users\ujwal\OneDrive\Desktop\abc")
    y=time.time()
    print()
    print()
    print("time taken by scraper.py: ", y-x)
    print()
    print()
        
        
