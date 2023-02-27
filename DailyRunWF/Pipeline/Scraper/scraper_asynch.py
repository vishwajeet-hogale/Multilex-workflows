

from newspaper import Article, Config
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
                i = i.replace(" ", "")
            
        
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
                today = date.today()
                yesterday = today - timedelta(days=1)
                yesterday = str(yesterday.strftime("%m/%d/%Y"))
                today = str(today.strftime("%m/%d/%Y"))
                googlenews = GoogleNews(start=yesterday, end=today)
                googlenews.search('IPO')
            except:
                print("Google not working")
                not_working_functions.append('Google')
                err = "Error in Module "
                Errors["Google"].append(err)
                return
            
            links=[]
            titles=[]
            texts=[]
            
            try:
                for i in range(30):
                    for j in googlenews.page_at(i+1):
                        links.append(j["link"])
                        try:
                            titles.append(j["title"])
                        except:
                            titles.append("-")
                        try:
                            texts.append(j["desc"])
                        except:
                            texts.append("-")
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
                        final_links.append(link)
                        title.append(a)
                        text.append(b)
                        scraped_date.append(str(today))
                        pub_date.append(str(today))
                        return

                    
                    try:
                        if article.title:
                            title.append(article.title)
                        else:
                            title.append(a)
                    except:
                        err["link"]=link
                        err["title"]="Error"
                        title.append(a)
                        flag=1
                    
                    try:
                        if article.text:
                            text.append(article.text)
                        else:
                            text.append(b)
                    except:
                        err["link"]=link
                        err["title"]="Error"
                        text.append(b)
                        flag=1

                    scraped_date.append(str(today))
                    pub_date.append(str(today))
                    
                    if flag==1:
                        Errors["Google"].append(err)

                    final_links.append(link)
            
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
            df = FilterFunction(df)
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
            
    def bing_search():
        try:
            print("Bing")
            Errors["Bing"]=[]
            try:

                site = "https://www.bing.com/news/search?q=eyes+Ipo+OR+Ipo+listing+OR+aims+for+Ipo+OR+Spac+OR+IPO"

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
            x= soup.find_all("div", class_="news-card newsitem cardcommon b_cards2")
            for i in x:
                try:
                    links.append(i.get("url"))
                    try:
                        titles.append(i.find("div", class_="t_t").a.text)
                    except:
                        titles.append("-")
                    try:
                        texts.append(i.find("div", class_="snippet").text)
                    except:
                        texts.append("-")
                except:
                    continue
            
                
            
            def getarticles(i, title, text1):
                current_time = date.today()
                flag=0
                err=err_dict()
                try:
                    link = i
                    article = Article(link)
                    article.download()
                    article.parse()
                    article.nlp()
                except:
                    try:
                        err["link"]="Article not working"+link
                        Errors["Bing"].append(err)
                        list_of_titles.append(title)
                        list_of_text.append(text1)
                        list_of_links.append(link)
                        list_of_published_dates.append(current_time)
                        scraped_time.append(current_time)
                        return
                    
                    except:
                        err["link"]="Link not extracted properly"
                        Errors["Bing"].append(err)
                        return
                
                try:
                    name=article.title
                    if name==None:
                        name=title
                except:
                    err["link"]=link
                    err['title']="Error"
                    name=title
                    flag=1
                
                try:
                    text=article.text
                    if text==None:
                        text=text1
                except:
                    err["link"]=link
                    err['text']="Error"
                    text=text1
                    flag=1

                list_of_titles.append(name)
                list_of_text.append(text)
                list_of_links.append(link)
                list_of_published_dates.append(current_time)
                scraped_time.append(current_time)
                
                if flag==1:
                    Errors["Bing"].append(err)
            
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



    #                                  Final
    
    #df152=himalayan_times("ipo")
    df149=bankok_post("ipo")
    df150=bankok_post("fpo")
    df151=bankok_post("spac")
    df55=stock_eastmoney()
    df14=bing_search()
    df10=google_news()
    df1=korea()
    df2=proactive("ipo")
    df3=gulfbusiness("ipo")
    df138=gulfbusiness("fpo")
    df139=gulfbusiness("spac")
    df4=investmentu("ipo")
    df136=investmentu("fpo")
    df137=investmentu("spac")
    df5=einnews()
    df6=businessinsider("ipo")
    df132=businessinsider("fpo")
    df133=businessinsider("spac")
    df7=Reuters("ipo")
    df8=Reuters("pre ipo")
    df9=Reuters("Initial Public Offering")
    df11=defenseworld("ipo")
    df130=defenseworld("fpo")
    df131=defenseworld("spac")
    df12=technode("ipo")
    df128=technode("fpo")
    df129=technode("spac")
    df13=globenewswire("ipo")
    df126=globenewswire("fpo")
    df127=globenewswire("spac")
    df15=autonews("ipo")
    df124=autonews("fpo")
    df125=autonews("spac")
    df16=capacitymedia("ipo")
    df122=capacitymedia("fpo")
    df123=capacitymedia("spac")
    df17=kenyanwallstreet("ipo")
    df120=kenyanwallstreet("fpo")
    df121=kenyanwallstreet("spac")
    df18=thesundaily("ipo")
    df118=thesundaily("fpo")
    df119=thesundaily("spac")
    df19=digitaljournal("ipo")
    df116=digitaljournal("fpo")
    df117=digitaljournal("spac")
    df20=asiafinancial("ipo")
    df114=asiafinancial("fpo")
    df115=asiafinancial("spac")
    df21=stockhead("ipo")
    df112=stockhead("fpo")
    df113=stockhead("spac")
    df22=koreajoongangdaily("ipo")
    df110=koreajoongangdaily("fpo")
    df111=koreajoongangdaily("spac")
    df23=upstreamonline("ipo")
    df108=upstreamonline("fpo")
    df109=upstreamonline("spac")
    df24=etfdailynews("ipo")
    df106=etfdailynews("fpo")
    df107=etfdailynews("spac")
    df25=splash247("ipo")
    df104=splash247("fpo")
    df105=splash247("spac")
    df26=brisbanetimes("ipo")
    df102=brisbanetimes("fpo")
    df103=brisbanetimes("spac")
    df27=zdnet("ipo")
    df100=zdnet("fpo")
    df101=zdnet("spac")
    df28=manilatimes("ipo")
    df98=manilatimes("fpo")
    df99=manilatimes("spac")
    df29=investmentweek("ipo")
    df96=investmentweek("fpo")
    df97=investmentweek("spac")
    df30=sundayobserver("ipo")
    df94=sundayobserver("fpo")
    df95=sundayobserver("spac")
    df31=reinsurancene("ipo")
    df92=reinsurancene("fpo")
    df93=reinsurancene("spac")
    df32=insideretail("ipo")
    df90=insideretail("fpo")
    df91=insideretail("spac")
    df33=EconomicTimes()
    df34=seenews("ipo")
    df88=seenews("fpo")
    df89=seenews("spac")
    df35=shorttermrentalz("ipo")
    df86=shorttermrentalz("fpo")
    df87=shorttermrentalz("spac")
    df36=arabnews("ipo")
    df84=arabnews("fpo")
    df85=arabnews("spac")
    df37=macaubusiness("ipo")
    df38=macaubusiness("fpo")
    df39=macaubusiness("spac")
    #df40=vietnamnet("ipo")
    #df41=vietnamnet("fpo")
    #df42=vietnamnet("spac")
    df43=thesydneymorningherald("ipo")
    df44=thesydneymorningherald("fpo")
    df45=thesydneymorningherald("spac")
    df46=economictimes("ipo")
    df47=economictimes("fpo")
    df48=economictimes("spac")
    df49=nzherald("ipo")
    df50=nzherald("fpo")
    df51=nzherald("spac")
    df52=albaniandailynews("ipo")
    df53=albaniandailynews("fpo")
    df54=albaniandailynews("spac")
    df56=straittimes()
    df57=financialpost("ipo")
    df58=financialpost("fpo")
    df59=financialpost("spac")
    df60=nikkei("ipo")
    df61=nikkei("fpo")
    df62=nikkei("spac")
    df63=albawaba("ipo")
    df64=albawaba("fpo")
    df65=albawaba("spac")
    df66=theaustralianfinancialreview("ipo")
    df67=theaustralianfinancialreview("fpo")
    df68=theaustralianfinancialreview("spac")
    df69=trendnewsagency("ipo")
    df70=trendnewsagency("fpo")
    df71=trendnewsagency("spac")
    df72=globallegalchronicle("ipo")
    df73=globallegalchronicle("fpo")
    df74=globallegalchronicle("spac")
    df75=ewnews("ipo")
    df76=ewnews("fpo")
    df77=ewnews("spac")
    df78=dw("ipo")
    df79=dw("fpo")
    df80=dw("spac")
    df81=uzdaily("ipo")
    df82=uzdaily("fpo")
    df83=uzdaily("spac")
    

    df140=kedglobal("ipo")
    df141=kedglobal("fpo")
    df142=kedglobal("spac")
    df143=pymnts("ipo")
    df144=pymnts("fpo")
    df145=pymnts("spac")
    df146=timesofindia("ipo")
    df147=timesofindia("fpo")
    df148=timesofindia("spac")
    df152=tradingcharts("ipo")
    df153=tradingcharts("fpo")
    df154=tradingcharts("spac")
    df155=kontan("ipo")
    df156=kontan("fpo")
    df157=kontan("spac")
    df158=tagesschau("ipo")
    df159=tagesschau("fpo")
    df160=tagesschau("spac")
    df161=afr("ipo")
    df162=afr("ipo")
    df163=afr("ipo")


    df_final_1 = [ df1, df2, df3, df4, df5, df6, df7, df8, df9, df10 , df11, df12, df13, df14, df15, df16, df17, df18, df19, df20 , df21, df22, df23, df24, df25, df26, df27, df28, df29, df30, df31, df32, df33, df34, df35, df36, df37 ,df38, df39, df43, df44, df45, df46, df47, df48, df49, df50, df51, df52, df53, df54, df55, df56, df57, df58, df59, df60, df61, df62, df63, df64, df65, df66, df67, df68, df69, df70, df71, df72, df73, df74, df75, df76, df77, df78, df79, df80, df81, df82, df83,df84,df85,df86,df87,df88,df89,df90,df91,df92,df93,df94,df95,df96,df97,df98,df99,df100,df101,df102,df103,df104,df105,df106,df107,df108,df109,df110,df111,df112,df113,df114,df115,df116,df117,df118,df119,df120,df121,df122,df123,df124,df125,df126,df127,df128,df129,df130,df131,df132,df133,df136,df137,df138,df139,df140,df141,df142,df143,df144,df145,df146,df147,df148, df149,df150,df151, df152, df153 ,df154, df155, df156, df157, df158, df159, df160, df161, df162, df163]
    
    
    
       
    
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
    multilex_scraper("","")
    y=time.time()
    print()
    print()
    print("time taken by scraper.py: ", y-x)
    print()
    print()
        
        
