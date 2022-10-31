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
from datetime import datetime, date
from datetime import timedelta
from newspaper import Article
import importlib.util
import warnings
import pytz
import lxml
from bs4 import BeautifulSoup
from advertools import word_tokenize
warnings.simplefilter("ignore", UserWarning)
logging.basicConfig(level=logging.INFO,format="%(asctime)s - %(process)d - %(name)s - %(levelname)s - %(message)s")
logging.info("first line of multilex_scraper_xform")
# def infin_transform_all_objects(input_dir, output_dir, **kwargs):
#     logging.info("input_dir=" + input_dir + ", output_dir=" + output_dir)
#     for path, subdirs, files in os.walk(input_dir):
#           for name in files:
#             logging.info("file in directory %s = %s. size = %d", path, os.path.join(path, name), Path(os.path.join(path, name)).stat().st_size)
#     multilex_scraper(input_dir, output_dir)
def dynamic_module_import(file_path, module_name):
    spec = importlib.util.spec_from_file_location(module_name, file_path)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    logging.info("dynamically loaded module %s contents = %s", file_path, dir(module))
    return module
def multilex_scraper(input_dir, output_dir):
    cur_date = str(date.today())
    not_working_functions = []
    log_format = (
        '[%(asctime)s] %(levelname)-8s %(name)-12s %(message)s')
    def emptydataframe(name,df):
        if df.empty:
            not_working_functions.append(name+" : err : Empty datframe")
    months = ["Jan" , "Feb" , "Mar" , "Apr" , "May" , "Jun" , "Jul" , "Aug" , "Sep" , "Oct" , "Nov" , "Dec","January","February","March","April","May","June","July","August","September","October","November","December"]
    logging.basicConfig(
        level=logging.DEBUG,
        format=log_format,
        filename=os.path.join(output_dir,'debug.log'),
    )
    def get_time_valid(): #Returns the hour from the time 
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
            for i,row in df.iterrows():
                # row["publish_date"]= translate(row["publish_date"])
                row["title"] = translate(row["title"])
                row["text"] = translate(row["text"])

                # time.sleep(0.2)
            return df
        except:
            for i,row in df.iterrows():
                # row["publish_date"]= translate(row["publish_date"])
                row["title"] = translate(row["title"])
                # row["text"] = translate(row["text"])

                # time.sleep(0.2)
            return df
    def correct_link(link):
        link = str(link)
        if(link.find("&ct")!=-1):
            link = link.split("&ct")[0]
        return link
    def get_date_mname_d_y(date):
        #Apr 21, 2022 
        #21 Apr 2022
        month = re.findall(r'''(Jan(uary)?|Feb(ruary)?|Mar(ch)?|Apr(il)?|May|Jun(e)?|Jul(y)?|Aug(ust)?|Sep(tember)?|Oct(ober)?|Nov(ember)?|Dec(ember)?)''',date)
        m = str(months.index(month[0][0].strip()) % 12 + 1)
        y = str(re.findall(r'\d{4}',date)[0])
        day = str(re.findall(r'\d{1,2}',date)[0])
        return "-".join([day,m,y])
    def get_date_min_read(date):
    #2min read . Updated: 21 Apr 2022, time
        return get_date_mname_d_y(date.split(":")[1].split(",")[0].strip())
    def correct_publish_date(i):
        try:
            i = str(i)
            i = i.strip()
            if len(re.findall("\d{1,2}/\d{1,2}/\d{4}",i)):
                hi = re.findall("\d{1,2}/\d{1,2}/\d{4}",i)
                l1 = hi[0].split("/")
                temp = l1[0]
                l1[0] = l1[1]
                l1[1] = temp
                i = "-".join(l1)
                return i
            elif(re.findall("\d{1,2}/\w{3}/\d{4}",i)):
                i = get_date_mname_d_y(re.findall("\d{1,2}/\w{3}/\d{4}",i)[0])
                return i
            elif(len(re.findall("\d{1,2}\s\w{3}\s\d{4}",i))):

                i = get_date_mname_d_y(re.findall("\d{1,2}\s\w{3}\s\d{4}",i)[0])
                # print(i)
                return i
            elif(re.findall(r'min read . Updated:',i)):
                i = get_date_min_read(i)   
                return i   
            elif(len(i.split(".")) == 3):
                if(len(i.split(".")[0]) == 4):
                    i = "-".join(i.split(".")[::-1])
                    return i
                else:
                    i = i.replace(".","-")
                    return i  
            elif len(re.findall(r'\d{1,2}.\d{1,2}.\d{4}',i)) and i.find(":"):
                if len(i.split(" "))>1:
                    i = i.split(" ")[2].replace(".","-")
                    return i
            elif(re.findall(r'\d{1,2}-\d{1,2}-\d{4}',i)):
                return i
            
            elif(i.count(":") >= 2):
                if len(re.findall(r'T',i)):
                    i = "-".join(i.split("T")[0].split("-")[::-1])
                    return i
                if len(re.findall(r'Newswire',i)):
                    i = "-".join(i.strip().split(" ")[-3].split("-")[::-1])
                    return i
                i = i.split(" ")[0].strip()
                if len(re.findall(r'[a-zA-Z]+',i)):
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
            month = re.findall(r'''(Jan(uary)?|Feb(ruary)?|Mar(ch)?|Apr(il)?|May|Jun(e)?|Jul(y)?|Aug(ust)?|Sep(tember)?|Oct(ober)?|Nov(ember)?|Dec(ember)?)''',i)
            if not len(month):
                i = "Date"
                return i
            m = str(months.index(month[0][0].strip()) % 12 + 1)
            y = str(re.findall(r'\d{4}',i)[0])
            day = str(re.findall(r'\d{1,2}',i)[0])
            i = "-".join([day,m,y])
            return i
    def correct_navigable_string(df1):
        try:
            err = []
            for i , row in df1.iterrows():
                try:
                    if(row["publish_date"] == None):
                        row["publish_date"] = "Date"
                        continue

                    
                    soup = BeautifulSoup('''
                    <html>
                        ''' + str(row["publish_date"]) + '''
                    </html>
                    ''', "lxml")

                # Get the whole h2 tag
                    row["publish_date"]=str(soup.p.string)
                    row["publish_date"] = str(row["publish_date"]).strip()
                    row["publish_date"] = correct_publish_date(str(row["publish_date"]))
                    row["link"] = correct_link(str(row["link"]))
                except:
                #     # print(row)
                #     # print("\n")
                    err.append(i)
            print(err)
            df_final=df1
            # df2 = pd.DataFrame(columns=["title","link","publish_date","scraped_date","text"])
            # if "Date" in df_final["publish_date"].tolist():
            df2 = df_final[df_final["publish_date"] == "Date"]
            df_final = df_final[df_final["publish_date"] != "Date"]
            df_final['publish_date']=pd.to_datetime(df_final['publish_date'],format="%d-%m-%Y",errors='coerce',utc=True).dt.strftime("%d/%b/%Y" " " "%H:%M:%S")
            one_year_from_now = datetime.now()
            date_formated = one_year_from_now.strftime("%d/%b/%Y" " " "%H:%M:%S")
            df_final['scraped_date'] = date_formated

            public_date = pd.to_datetime(df_final['publish_date'],errors='coerce',utc=True).dt.strftime('%d-%m-%Y')
            scrap_date= pd.to_datetime(df_final['scraped_date'],errors='coerce',utc=True).dt.strftime('%d-%m-%Y')

            ## morning 
            yesterday = (date.today() - timedelta(days=1)).strftime('%d-%m-%Y')
            daybefore = (date.today() - timedelta(days=2)).strftime('%d-%m-%Y')
            final_1 = df_final.loc[public_date == yesterday]
            final_2 = df_final.loc[public_date == scrap_date]
            final_3 = df_final.loc[public_date == daybefore]
            ## evening 
            fn = []
            if(int(get_time_valid()) >= 16):
                fn = [final_2,df2]
            else:
                fn = [final_1,final_2,final_3,df2]
            final = pd.concat(fn)
            return final
        except:
            return df1
    def conver_to_lower(li):
        return [str(i).lower() for i in li]
    def tokenize_no_words(text_list,val):
        return set(word_tokenize(text_list,val)[0])
    def FilterFunction(final):
            try:
                if(final.empty):
                    return final
                key_1_gram = [ 'IPO','IPO','IPO ','SPACs','ipo','pre-IPO','pre-ipo','PRE-IPO','pre-IPO','spac','shares','pre ipo']
                key_2_gram = ['offering ipo',"listed on","go public","plan to","going public","offering shares","initial public","public offering","have listed","files for"]
                key_3_gram = ["an initial public","offer its shares","to the public","going to list","files for ipo","filed for ipo","initial public offering","public offering ipo"]
                key_4_gram = ["an initial public offering","the initial public offering","its initial public offering","initial public offering b","b initial public offering","The Initial Public Offering","Its Initial Public Offering ","Has Set Its Ipo","Targeting A 2023 Ipo"]
                key_5_gram = ["initial public offering b b'","an b initial public offering","Planning An Initial Public Offering","Files A Prospectus For Ipo","Considering An Initial Public Offering",]
                
                key_6_gram = ['an b initial public offering b', 'standards the thomson reuters trust principles', 'b initial public offering b ipo', 'its b initial public offering b', 'sebagai ungkapan terimakasih atas perhatian anda', 'ungkapan terimakasih atas perhatian anda tersedia', 'terimakasih atas perhatian anda tersedia voucer', 'atas perhatian anda tersedia voucer gratis', 'perhatian anda tersedia voucer gratis senilai', 'anda tersedia voucer gratis senilai donasi', 'tersedia voucer gratis senilai donasi yang', 'voucer gratis senilai donasi yang bisa', 'gratis senilai donasi yang bisa digunakan', 'senilai donasi yang bisa digunakan berbelanja', 'donasi yang bisa digunakan berbelanja di', 'b initial public offering b b', 'b initial public offering b of', 'initial public offering b b ipo', 'public offering b b ipo b', 'the b initial public offering b',"Will Hold An Initial Public Offering","On Its Potential Initial Public Offering"]
                key_7_gram = ['sebagai ungkapan terimakasih atas perhatian anda tersedia', 'ungkapan terimakasih atas perhatian anda tersedia voucer', 'terimakasih atas perhatian anda tersedia voucer gratis', 'atas perhatian anda tersedia voucer gratis senilai', 'perhatian anda tersedia voucer gratis senilai donasi', 'anda tersedia voucer gratis senilai donasi yang', 'tersedia voucer gratis senilai donasi yang bisa', 'voucer gratis senilai donasi yang bisa digunakan', 'gratis senilai donasi yang bisa digunakan berbelanja', 'senilai donasi yang bisa digunakan berbelanja di', 'b initial public offering b b ipo', 'initial public offering b b ipo b', 'for an b initial public offering b', 'an b initial public offering b ipo', 'dapat voucer gratis sebagai ungkapan terimakasih atas', 'voucer gratis sebagai ungkapan terimakasih atas perhatian', 'gratis sebagai ungkapan terimakasih atas perhatian anda', 'donasi yang bisa digunakan berbelanja di dukungan', 'yang bisa digunakan berbelanja di dukungan anda', 'bisa digunakan berbelanja di dukungan anda akan',"Raise Funds Through An Initial Public Offering"]
                key_8_gram = ["Has Filed For An B Initial Public Offering"]
                title,link,published_date,scraped_date,text=[],[],[],[],[]
                for i,row in final.iterrows():
                    cases = [0]*8
                    article = str(str(row["title"]) + " " + str(row["text"])).lower()
                    # print(article + "\n\n\n\n")
                    text_list = [article]
                    key_1_gram = conver_to_lower(key_1_gram)
                    key_2_gram = conver_to_lower(key_2_gram)
                    key_3_gram = conver_to_lower(key_3_gram)
                    res_1_gram = tokenize_no_words(text_list,1)
                    res_2_gram = tokenize_no_words(text_list,2)
                    res_3_gram = tokenize_no_words(text_list,3)
                    res_4_gram = tokenize_no_words(text_list,4)
                    res_5_gram = tokenize_no_words(text_list,5)
                    res_6_gram = tokenize_no_words(text_list,6)
                    res_7_gram = tokenize_no_words(text_list,7)
                    res_8_gram = tokenize_no_words(text_list,8)
                    if(len(res_1_gram.intersection(key_1_gram))>0):
                        cases[0] = 1
                    if(len(res_2_gram.intersection(key_2_gram))>0):
                        cases[1] = 1
                    if(len(res_3_gram.intersection(key_3_gram))):
                        cases[2] = 1
                    if(len(res_4_gram.intersection(key_4_gram))):
                        cases[3] = 1
                    if(len(res_5_gram.intersection(key_5_gram))):
                        cases[4] = 1
                    if(len(res_6_gram.intersection(key_6_gram))):
                        cases[5] = 1
                    if(len(res_7_gram.intersection(key_7_gram))):
                        cases[6] = 1
                    if(len(res_8_gram.intersection(key_8_gram))):
                        cases[7] = 1
                    if(cases[0] and ( cases[1] or cases[2] or cases[3]or cases[4]or cases[5]or cases[6]or cases[7])):
                            title.append(final['title'][i])
                            link.append(final['link'][i])
                            published_date.append(final['publish_date'][i])
                            scraped_date.append(final['scraped_date'][i])
                            text.append(final['text'][i])
                    cases = [0]*8
                final = pd.DataFrame(list(zip(title,link,published_date,scraped_date,text)), 
                        columns =['title','link','publish_date','scraped_date','text'])
                final = final[~final['title'].isin(["private placement", "reverse merger", "blank check merger"])]
                final = final[~final['text'].isin(["private placement", "reverse merger", "blank check merger"])]
                final.to_csv("Newshab.csv")
                return final
            except:
                print("Issue in Filter Function")
    
    def log_errors(err_logs):
        for i in err_logs:
            print(i)
    
    def MoneyControl():
        try:
            print("Moneycontrol")
            err_logs = []
            baseSearchUrl = "https://www.moneycontrol.com/rss/iponews.xml"
            scrapedData = {}
            links = []
            titles = []
            err_index = []
            ArticleDates = []
            ScrapeDates = []
            queryUrl = baseSearchUrl
            try:
                pageSource = requests.get(baseSearchUrl)
            except:
                err = "moneycontrol: err: Failed to access search url: " + queryUrl + " and convert it to soup object"
                err_logs.append(err)
                exit()
            parsedSource = BeautifulSoup(pageSource.content, "xml")
            for eachItem in parsedSource.find_all("item"):
                currentArticleTitle = eachItem.find("title").text
                currentArticleLink = eachItem.find("link").text
                currentArticleDate = datetime.strptime(str(eachItem.find("pubDate").text).split("+", maxsplit=2)[0].strip(),
                                                    "%a, %d %b %Y %H:%M:%S").strftime("%d-%m-%Y")
                titles.append(currentArticleTitle)
                links.append(currentArticleLink)
                ArticleDates.append(currentArticleDate)
                ScrapeDates.append(datetime.today().strftime("%d-%m-%Y"))
            scrapedData["title"] = titles
            scrapedData["link"] = links
            scrapedData["publish_date"] = ArticleDates
            scrapedData["scraped_date"] = ScrapeDates
            ArticleBody = []
            for link in links:
                articleText = ""
                try:
                    headers = {
                        'User-Agent': "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 Chrome/58.0.3029.110 Safari/537.36"}
                    pageSource = requests.get(link, headers=headers)
                    parsedSource = BeautifulSoup(pageSource.content, "html.parser", from_encoding="iso-8859-1")
                except:
                    err = "moneycontrol: err: Failed to access article link : " + link
                    ArticleDates.append("Error")
                    err_index.append(links.append(link))
                    err_logs.append(err)
                    continue
                requiredDiv = parsedSource.find("div", class_="content_wrapper arti-flow")
                if not requiredDiv:
                    articleText = titles[links.index(link)]
                    ArticleBody.append(articleText)
                    continue
                else:
                    for item in requiredDiv.find_all("p"):
                        try:
                            if not (re.search("/Click Here/gm", item.text) or re.search("/Also read/gm", item.text) or
                                    re.search("/Disclaimer/gm", item.text)):
                                articleText += (" " + item.text)
                            else:
                                continue
                        except:
                            continue
                    ArticleBody.append(articleText)
                scrapedData["text"] = ArticleBody
            moneycontrolDF = pd.DataFrame(scrapedData)
            moneycontrolDF = moneycontrolDF.drop_duplicates(subset=["link"])
            if moneycontrolDF.empty:
                err = "moneycontrol: err: Empty dataframe"
                err_logs.append(err)
            df = FilterFunction(moneycontrolDF)
            emptydataframe("Moneycontrol",df)
            log_errors(err_logs)
            # df  = link_correction(moneycontrolDF)
            return df
        except:
            print("Moneycontrol not working")
            not_working_functions.append("Moneycontrol")
    def Cnbc_Seeking():
        try:
            print('2')
            s_dates=[]  
            title = []
            text = []
            dates = []
            links = []
            try:
                urls="https://www.cnbc.com/id/10000666/device/rss"
                logging.info("cnbc.com: invoking requests.url()=" + urls)
                page=requests.get(urls,verify = False)
                logging.info("cnbc.com: completed requests.url()=" + urls)
                soup=BeautifulSoup(page.content,features='lxml')
                soup.find_all()
                # print(soup)
                import datetime
                x=datetime.datetime.now()
                y=x.date()
                x=x.date()
                x=str(x)
                x=x.split('-')
                curr_date=x[2]
                curr_date=int(curr_date)
                curr_date=curr_date-1
                curr_date=str(curr_date)
                # print(curr_date)
                for i in soup.find_all("item"):
                    dates.append(i.find('pubdate').text)
                    text.append(i.find('description').text)
                    s_dates.append(y)
                    title.append(i.find('title').text)
                    l1 = re.findall(r'''(http|ftp|https):\/\/([\w_-]+(?:(?:\.[\w_-]+)+))([\w.,@?^=%&:\/~+#-]*[\w@?^=%&\/~+#-])''',i.text)[0]
                    l = l1[0]+"://"+l1[1]+l1[2]
                    links.append(l)
            except:
                print('CNDC_seeking is not working')
                not_working_functions.append('Cnbc')

            cnbc = pd.DataFrame(list(zip(title,dates,s_dates,links,text)), 
                            columns =['title','publish_date','scraped_date','link','text'],index=None)
            df = FilterFunction(cnbc)
            emptydataframe("Cnbc",df)
            # logging.info("CNBC_seeking function ended")
            # df  = link_correction(df)
            return cnbc
        except:
            df1 = pd.DataFrame(columns =['title','link','publish_date','scraped_date'])
            return df1
    def korea():
        try :
            print("Korea")
            err_logs = []
            url = "http://www.koreaherald.com/search/index.php?kr=0&q=IPO"
            domain_url = "http://www.koreaherald.com/"
            title,links,text,pub_date,scraped_date = [],[],[],[],[]
            try:
                page = requests.get(url)
                soup = BeautifulSoup(page.content,"html.parser")
                # print(soup)
                
            except:
                err = "Korea : err : Couldn't fetch " + url 
                err_logs.append(err)
                return 
            for a in soup.find_all('ul', {'class':'main_sec_li'}):
                            #links.append(a["href"])
                for l in a.find_all('a',href=True):
                                #print(l['href'])
                    links.append(domain_url + l["href"])
            #Fetch all the necessary data 
            # print(links)
            final_links = []
            today = date.today()
            for link in links:
                try:
                    page = requests.get(link)
                    soup = BeautifulSoup(page.content,"html.parser")
                # print(soup)
                # print(link)
                except:
                    err = "Korea : err : Couldn't fetch url " + link 
                    err_logs.append(err)
                    
                    continue
                #Published Date
                pdate = soup.find("div" , {"class" : "view_tit_byline_r"}).text
                month = re.findall(r'''(Jan(uary)?|Feb(ruary)?|Mar(ch)?|Apr(il)?|May|Jun(e)?|Jul(y)?|Aug(ust)?|Sep(tember)?|Oct(ober)?|Nov(ember)?|Dec(ember)?)''',pdate)
                nums = re.findall(r'[0-9]+',pdate)
                m = str(months.index(month[0][0].strip()) % 12 + 1)
                pub_date.append("-".join([nums[0],m,nums[1]]))
                #Title of article 
                title.append(soup.find("h1" , {"class" : "view_tit"}).text)       
                #Text of article
                text.append(soup.find("div" , {"class" :"view_con article"}).text)
                # print(text)
                #Scrapped date 
                scraped_date.append(str(today))
                #Working links
                final_links.append(link)
            df = pd.DataFrame({"text":text,"link":final_links,"publish_date":pub_date,"scraped_date":scraped_date,"title":title})
            if df.empty:
                err = "Korea : err: Empty dataframe"
                err_logs.append(err)
            df = df.drop_duplicates(subset=["link"])
            df = FilterFunction(df)
            emptydataframe("Korea",df)
            # df  = link_correction(df)
            return df
        except :
            print("Korea not working")
            not_working_functions.append('Korea')
    def proactive(keyword):
        try:
            print("proactive")
            err_logs = []
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
            page = requests.get(url, headers=headers)
            soup = BeautifulSoup(page.content, "html.parser")
            #soup  # Debugging - if soup is working correctly
            # Class names of the elements to be scraped
            div_class = "advanced-search-block"  # Class name of div containing the a tag
            #h1_class = "_1Y-96"
            #h1_div_class = "col-xs-12"
            title_h1_class = "h2"
            date_p_itemprop = "datePublished"
            para_div_itemprop = "articleBody"
            links = []
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
            # Remove duplicates
            links = list(set(links))
            #links # Debugging - if link array is generated
            collection = []
            scrapper_name = "proactiveinvestors"
            for link in links:
                try:
                    l_page = requests.get(link, headers=headers)
                    l_soup = BeautifulSoup(l_page.content, 'html.parser')
                except:
                    err = scrapper_name + ": err: Failed to retrieve data from link: " + link + " and convert it to soup object"
                    err_logs.append(err)
                    continue
                data = []
                # Scraping the heading
                #h1_ele = l_soup.find("h1", {"class": h1_class})
                try:
                    title_ele = l_soup.find("h1", {"class": title_h1_class})
                    data.append(title_ele.text)
                except:
                    err = scrapper_name + ": err: Failed to find title in page. Link: " + link
                    err_logs.append(err)
                    continue  # drops the complete data if there is an error
                # Adding the link to data
                data.append(link)
                # Scraping the published date
                try:
                    date_ele = l_soup.find("p", {"itemprop": date_p_itemprop})
                    date_text = date_ele.text
                    #date_text = (date_text.split('/'))[-1]
                    #date_text = date_text.replace(" Updated: ", "")
                    data.append(date_text)  # The date_text could be further modified to represent a proper date format
                except:
                    err = scrapper_name + ": err: Failed to find date in page. Link: " + link
                    err_logs.append(err)
                    continue  # drops the complete data if there is an error
                # Adding the scraped date to data
                cur_date = str(datetime.today())
                data.append(cur_date)
                # Scraping the paragraph
                try:
                    para_ele = (l_soup.findAll("div", {"itemprop": para_div_itemprop}))[-1]
                    data.append(para_ele.text)  # Need to make this better
                except:
                    err = scrapper_name + ": err: Failed to find paragraph in page. Link: " + link
                    err_logs.append(err)
                    continue  # drops the complete data if there is an error
                # Adding data to a collection
                collection.append(data)
            df = pd.DataFrame(collection, columns =['title', 'link','publish_date','scraped_date','text'])
            if df.empty:
                err = scrapper_name + ": err: Empty dataframe"
                err_logs.append(err)
            #print(df) # For debugging. To check if df is created
            #print(err_logs) # For debugging - to check if any errors occoured
            df = FilterFunction(df)
            emptydataframe("Proactive investors",df)
            # df  = link_correction(df)
            return df
        except:
            not_working_functions.append("Proactive Inverstors")
            print("Proactive investors not working")
    def Reuters(keyword):
        print('7')
        try:
            title = []
            text = []
            s_dates = []
            links=[]
            pub_date=[]
            try:
                url = f'https://www.reuters.com/search/news?blob={keyword}&sortBy=date&dateRange=all'
                url1 = 'https://www.reuters.com'
                page=requests.get(url,verify = False)
                soup=BeautifulSoup(page.content,'html.parser')
                y = soup.findAll("h5", {"class" : "search-result-timestamp"})
                for x in y:
                    import re
                    TAG_RE = re.compile(r'<[^>]+>')
                    pubdate = TAG_RE.sub('',str(x))
                    pub_date.append(str(pubdate))
                for i in range(1,len(soup.find_all('h3'))):
                    pdd=soup.find_all('h3')[i]
                    for a in pdd.find_all('a',href=True):
                        links.append(url1 + a["href"])
                # print(links)
                for l in links:
                    fetch = requests.get(l)
                    sp = BeautifulSoup(fetch.content, 'lxml')
                    t = sp
                    x=sp.find("h1", { "class" : "text__text__1FZLe text__dark-grey__3Ml43 text__medium__1kbOh text__heading_2__1K_hh heading__base__2T28j heading__heading_2__3Fcw5" })
                    if x is not None:
                        n = x.text
                    else:
                        n = None
                    z=sp.find("div", { "class":"article-body__content__17Yit paywall-article" })
                    if z is not None:
                        k = z.text
                    else:
                        k = None
                    #print(z)
                    text.append(k)
                    title.append(n)
                    s_dates.append(cur_date)
            except:
                print('Reuters is not working')
                # not_working_functions.append('Reuters')
            percentile_list ={'publish_date': pub_date,'scraped_date': s_dates,'title': title,'link': links,'text':text}
            reuters = pd.DataFrame.from_dict(percentile_list, orient='index')
            df= reuters.transpose()
            df.dropna(inplace=True)
            # df = FilterFunction(reuters)
            emptydataframe("reuters",df)
            logging.info("Reuters function ended")
            # df  = link_correction(df)
            return df
        except:
            df1 = pd.DataFrame(columns =['title','link','publish_date','scraped_date'])
            return df1
    def TradingChart():
        try :
            print("FTC")
            err_logs = []
            url = "https://futures.tradingcharts.com/search.php?keywords=IPO&futures=1"
            domain_url = "https://futures.tradingcharts.com"
            title,links,text,pub_date,scraped_date = [],[],[],[],[]
            try:
                page = requests.get(url)
                soup = BeautifulSoup(page.content,"html.parser")
                # print(soup)
                
            except:
                err = "FTC : err : Couldn't fetch " + url 
                err_logs.append(err)
                return 
            all_divs = soup.find_all("a",{"class":"clUnSeResItemTitle"})
            for div in all_divs:
                links.append("https:"+div["href"])
            #Fetch all the necessary data 
            # print(links)
            final_links = []
            today = date.today()
            for link in links:
                try:
                    page = requests.get(link)
                    soup = BeautifulSoup(page.content,"html.parser")
                # print("hi")
                # print(soup)
                # print(link)
                except:
                    err = "FTC : err : Couldn't fetch url " + link 
                    err_logs.append(err)
                    continue

                #Title of article

                title.append(soup.find("h2" , {"class" : "fe_heading2"}).text)
                # print(title)
                #Published Date
                div = soup.find("div" , {"class" : "news_story m-cellblock m-padding"})
                t = ""
                for i in div.find_all("i"):
                    t += i.text + " "
                pub_date.append(t)
               
                #Text of article
                div = soup.find("div" , {"class" : "news_story m-cellblock m-padding"})
                t = ""
                for i in div.find_all("p"):
                    t += i.text + " "
                text.append(t)
                # print(text)

                #Scrapped date 
                scraped_date.append(str(today))

                #Working links
                final_links.append(link)
            df = pd.DataFrame({"text":text,"link":final_links,"publish_date":pub_date,"scraped_date":scraped_date,"title":title})
            if df.empty:
                err = "FTC : err: Empty datframe"
                err_logs.append(err)
            df = df.drop_duplicates(subset=["link"])
            df = FilterFunction(df)
            emptydataframe("FTC",df)
            # df  = link_correction(df)
            return df
        except :
            print("FTC not working")
            not_working_functions.append('FTC')
    def einnews():
        try:
            print("IPO EinNews")
            err_logs = []

            baseSearchUrl = "https://ipo.einnews.com/"
            domainUrl = "https://ipo.einnews.com"
            keywords = ['IPO', 'pre-IPO', 'initial public offering']

            # use this for faster testing
            tkeywords = ["IPO"]
            scrapedData = {}
            links = []
            titles = []
            err_index = []
            ArticleDates = []
            ScrapeDates = []
            ArticleBody = []
            for keyword in tkeywords:
                queryUrl = baseSearchUrl
                try:
                    session = HTMLSession()
                    resp = session.post(queryUrl)
                    resp.html.render()
                    pageSource = resp.html.html
                    parsedSource = BeautifulSoup(pageSource, "html.parser")
                except:
                    err = "einnews: err: Failed to access search url: " + queryUrl + " and convert it to soup object"
                    err_logs.append(err)
                    continue
                # with open("response.html", "w") as f:
                #     f.write(pageSource)
                # break
                for item in parsedSource.find("ul", class_="pr-feed").find_all("li"):
                    requiredTag = item.find("h3")
                    currentArticleTitle = str(requiredTag.find("a").text).strip()
                    # print(currentArticleTitle)
                    currentArticleLink = requiredTag.find("a")["href"]
                    # print(currentArticleLink)
                    if currentArticleLink[0] == "/":
                        links.append(domainUrl + currentArticleLink)
                    else:
                        links.append(currentArticleLink)
                    titles.append(currentArticleTitle)
                    currentArticleDateText = item.find("span", class_="date").text
                    if re.search("^\d.*", currentArticleDateText):
                        try:
                            currentArticleDate = datetime.today().strftime("%d-%m-%Y")
                        except:
                            err = "einnews: err: Failed to retrieve date from article : " + currentArticleLink
                            ArticleDates.append("Error")
                            err_index.append(links.append(currentArticleLink))
                            err_logs.append(err)
                            continue
                        ArticleDates.append(currentArticleDate)
                        ScrapeDates.append(datetime.today().strftime("%d-%m-%Y"))
                    else:
                        try:
                            currentArticleDate = datetime.strptime(currentArticleDateText,
                                                                "%b %d, %Y").strftime("%d-%m-%Y")
                        except:
                            err = "einnews: err: Failed to retrieve date from article : " + currentArticleLink
                            ArticleDates.append("Error")
                            err_index.append(links.append(currentArticleLink))
                            err_logs.append(err)
                            continue
                        ArticleDates.append(currentArticleDate)
                        ScrapeDates.append(datetime.today().strftime("%d-%m-%Y"))
                    articleText = ""
                    for pitem in item.find_all("p"):
                        articleText += pitem.text
                    ArticleBody.append(articleText.strip("\n"))

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
            if einnewsDF.empty:
                err = "einnews: err: Empty dataframe"
                err_logs.append(err)
            df = FilterFunction(einnewsDF)
            emptydataframe("Einnews",df)
            # df  = link_correction(df)
            return df
        except:
            not_working_functions.append("IPO Einnews")
            print("EINnews not working")
            df1 = pd.DataFrame(columns =['title','link','publish_date','scraped_date'])
            return df1
    def rss():
        try:
            articles=[]
            links=[]
            dates=[]
            description=[]
            scraped_date=[]
            cleaned_description=[]
            try:
                print('9')
                URL="https://ipo.einnews.com/rss/cpCdwuL2w4azHHGe"
                # logging.info("go_rss.com: invoking requests.url()=" + URL)
                page=requests.get(URL,verify = False)
                # logging.info("go_rss.com: completed requests.url()=" + URL)
                soup=BeautifulSoup(page.content,features='xml')


                import datetime  

                # using now() to get current time  
                current_time = datetime.datetime.now() 
                import html
                for item in soup.find_all("item"):
                    articles.append(item.find('title').text)
                    links.append(item.find('link').text)
                    dates.append(item.find('pubDate').text)
                    description.append(html.unescape(item.find('description').text))
                    scraped_date.append(current_time)

                #cleaning description
                
                import re
                for i in range(0,len(description)-1):
                    art=description[i]
                    art= art.lower().replace("don't","do not")
                    art = art.replace('â€¦', '').replace('<span class="match">', '').replace('</span>','').replace('\n','').replace('     ','')
                    art = art.replace(",,",",")
                    cleaned_description.append(re.sub('\n','',art))

                cleaned_description

            except:
                print('Rss not working')
                not_working_functions.append('RSS')
            df1 = pd.DataFrame(list(zip(articles,links,cleaned_description,dates,scraped_date)), 
                        columns =['title', 'link','text','publish_date','scraped_date'])

            import html
            for i in range(0,df1.shape[0]):
                df1['title'][i]=html.unescape(df1['title'][i])


            for i in range(0,df1.shape[0]):
    #             print(df1['link'][i])
                response=requests.get(df1['link'][i])
                df1['link'][i]=response.url

            Rss = FilterFunction(df1)
            emptydataframe("RSS",Rss)
            # logging.info("Rss function ended")
            # Rss  = link_correction(Rss)
            return Rss
        except:
            df1 = pd.DataFrame(columns =['title','link','publish_date','scraped_date'])
            return df1

    def GoogleAlert():
        try:
            articles=[]
            links=[]
            dates=[]
            scraped_date=[]
            try:
                print('10')
                import html
                url="https://www.google.co.in/alerts/feeds/15296043414695393299/12391429027627390948"
                page=requests.get(url)
                soup=BeautifulSoup(page.content,features='xml')

                #print(soup.prettify())
                for i in range(0,len(soup.find_all('entry'))):
                    pdd=soup.find_all('entry')[i]
                    for title in pdd.find_all('title'):
                        articles.append(html.unescape(title.text))
                    for link in pdd.find_all('link'):
                        links.append(html.unescape(link['href']))
                    for date in pdd.find_all('published'):
                        dates.append(date.text)
                        scraped_date.append(date.text)
            except:
                print('Google Alert is not working')
                not_working_functions.append('Google Alert')
                
            df_google = pd.DataFrame(list(zip(articles,articles,links,dates,scraped_date)), 
                        columns =['title','text', 'link','publish_date','scraped_date'])

            def clean_link(u):
                    u = u.replace('https://www.google.com/url?rct=j&sa=t&url=', '')

                    return(u)

            urls = df_google['link']

            clean_url = []
            for url in urls:
                clean_url.append(clean_link(url))

            df_google['link'] = clean_url
            
            df = FilterFunction(df_google)
            emptydataframe("Google alert",df)
            logging.info("GoogleAlert function ended")
            # df_google  = link_correction(df_google)
            return df_google
        except:
            df1 = pd.DataFrame(columns =['title','link','publish_date','scraped_date'])
            return df1
            

    def live(keyword):
        try:
            print('11')
            links = []
            title = []
            dates = []
            s_date = []
            text = []
            try:
                print('11')
                url = f'https://www.livemint.com/Search/Link/Keyword/{keyword}'
                url1 = 'https://www.livemint.com'
                logging.info("live.com: invoking requests.url()=" + url)
                page = requests.get(url,verify = False)
                logging.info("live.com: completed requests.url()=" + url)

                soup = BeautifulSoup(page.content, 'html.parser')
                for a in soup.find_all('h2', {'class': 'headline'}):
                    for i in a.find_all('a',href=True):
                        #print(i['href'])
                        links.append(url1 + i["href"])

                for l in links:
                    fetch = requests.get(l)
                    sp = BeautifulSoup(fetch.content, 'html.parser')
                    x=sp.find("h1", { "class" : "headline" }).text
                    #print(x)
                    title.append(x)
                    y = sp.find("span", { "class" : "articleInfo pubtime" }).text
                    dates.append(y)
                    z = sp.find("div", { "class" : "mainArea" }).text
                    #print(z)
                    from datetime import datetime, date
                    cur_date = str(datetime.today())
                    s_date.append(cur_date)
                    text.append(z)
            except:
                print('Live is not working')
                not_working_functions.append('Live mint')

            live = pd.DataFrame(list(zip(title,links,dates,s_date,text)), 
                                columns =['title', 'link','publish_date','scraped_date','text'])
            
            df = FilterFunction(live)
            emptydataframe("Livemint",df)
            logging.info("Live function ended")
            # df  = link_correction(df)
            return df
        except:
            df1 = pd.DataFrame(columns =['title','link','publish_date','scraped_date'])
            return df1
    
    def xinhuanet():
        try:
            try:
                print('13')
                url = "http://www.xinhuanet.com/english/mobile/business.htm"
                logging.info("www.xinhuanet.com: invoking requests.url()=" + url)
                page=requests.get(url)
                logging.info("www.xinhuanet.com: completed invoking requests.url()=" + url)
                soup=BeautifulSoup(page.content,'lxml')
                lists = []
                title = []
                dates = []
                text = []
                s_date = []
                for h in soup.findAll('li'):
                    for k in h.findAll('a'):
                        lists.append(k['href'])

                links= [line for line in lists if 'c_' in line]

                for link in links:
                    fetch = requests.get(link)
                    sp = BeautifulSoup(fetch.content, 'html.parser')
                    x=sp.find("h1", { "class" : "Btitle" })
                    if x is not None:
                        s = x.text
                    else:
                        s = None
                    #print(s)
                        #print(s)
                    title.append(s)
                    y = sp.find("i", { "class" : "time" }).text
                        #print(y)
                    dates.append(y)
                    z = sp.find("div", { "class" : "content" })
                    if z is not None:
                        n = z.text
                    else:
                        n = None
                    #print(n)
                    #print(n)
                    text.append(n)
                    s_date.append(cur_date)
            except:
                print('xinhuanet is not working')
                not_working_functions.append('Xinhuanet')
            import pandas as pd


            df2 = pd.DataFrame(list(zip(title,links,dates,s_date,text)), 
                            columns =['title', 'link','publish_date','scraped_date','text']) 
            df = FilterFunction(df2)
            emptydataframe("Xinhuanet",df)
            # df  = link_correction(df)
            return df
        except:
            df1 = pd.DataFrame(columns =['title','link','publish_date','scraped_date'])
            return df1
    

    def kontan(keyword):
        try:
            links = []
            title = []
            dates = []
            text = []
            s_date = []
            try:
                print('14')
                
                url = f"https://www.kontan.co.id/search/?search={keyword}&Button_search="
                url1 = "https:"
                logging.info("www.kontan.co.id: invoking requests.url()=" + url)
                page=requests.get(url)
                logging.info("www.kontan.co.id: completed invoking requests.url()=" + url)
                soup=BeautifulSoup(page.content,'lxml')
                for divtag in soup.find_all('div', {'class': 'sp-hl linkto-black'}):
                        for a in divtag.find_all('a',href=True):
                            links.append(url1 + a['href'])
                for link in links:
                    fetch = requests.get(link)
                    sp = BeautifulSoup(fetch.content, 'html.parser')
                    x=sp.find("h1", { "class" : "detail-desk" })
                    if x is not None:
                        s = x.text
                    else:
                        s = None
                    #print(s)
                        #print(s)
                    title.append(s)
                    y = sp.find("div", { "class" : "fs14 ff-opensans font-gray" })
                    if y is not None:
                        k = y.text
                        k = k.replace('Mei','May')
                        k = k.split(',')
                        k = k[1]
                    else:
                        k = None
                        #print(y)
                    dates.append(k)
                    z = sp.find("div", { "class" : "tmpt-desk-kon" })
                    if z is not None:
                        n = z.text
                    else:
                        n = None
                    #print(n)
                    #print(n)
                    text.append(n)
                    s_date.append(cur_date)
            except:
                print('kontan not working')
                not_working_functions.append("Kontan")
            import pandas as pd


            df2 = pd.DataFrame(list(zip(title,links,dates,s_date,text)), 
                            columns =['title', 'link','publish_date','scraped_date','text'])
            
            df = translate_dataframe(df2)
            df = FilterFunction(df2)
            emptydataframe("Kontan",df)
            # df  = link_correction(df)
            return df
        except:
            df1 = pd.DataFrame(columns =['title','link','publish_date','scraped_date'])
            return df1

    
    def AZ(keyword):
        try:
            print("AZ")
            err_logs = []
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
            page = requests.get(url, headers=headers)
            soup = BeautifulSoup(page.content, "html.parser")
            #soup  # Debugging - if soup is working correctly

            # Class names of the elements to be scraped
            div_class = "inlineSearchResults"  # Class name of div containing the a tag
            #h1_class = "_1Y-96"
            #h1_div_class = "col-xs-12"
            title_div_class = "top-part"
            date_span_class = "date-time"
            para_div_class = "article-content"

            links = []

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
            #links # Debugging - if link array is generated

            collection = []
            scrapper_name = "trend.az"

            for link in links:
                try:
                    l_page = requests.get(link)
                    l_soup = BeautifulSoup(l_page.content, 'html.parser')
                except:
                    err = scrapper_name + ": err: Failed to retrieve data from link: " + link + " and convert it to soup object"
                    err_logs.append(err)
                    continue

                data = []
                # Scraping the heading
                #h1_ele = l_soup.find("h1", {"class": h1_class})
                
                try:
                    title_ele = l_soup.find("div", {"class": title_div_class})
                    data.append(title_ele.text)
                except:
                    err = scrapper_name + ": err: Failed to find title in page. Link: " + link
                    err_logs.append(err)
                    continue  # drops the complete data if there is an error


                # Adding the link to data
                data.append(link)

                # Scraping the published date
                date_ele = l_soup.find("span", {"class": date_span_class})
                try:
                    date_text = date_ele.text
                    #date_text = (date_text.split('/'))[-1]
                    #date_text = date_text.replace(" Updated: ", "")
                    data.append(date_text)  # The date_text could be further modified to represent a proper date format
                except:
                    err = scrapper_name + ": err: Failed to find date in page. Link: " + link
                    err_logs.append(err)
                    continue  # drops the complete data if there is an error
                
                # Adding the scraped date to data
                cur_date = str(datetime.today())
                data.append(cur_date)
                

                # Scraping the paragraph
                try:
                    para_ele = (l_soup.findAll("div", {"class": para_div_class}))[-1]
                    data.append(para_ele.text)  # Need to make this better
                except:
                    err = scrapper_name + ": err: Failed to find paragraph in page. Link: " + link
                    err_logs.append(err)
                    continue  # drops the complete data if there is an error
                # Adding data to a collection
                collection.append(data)

            df = pd.DataFrame(collection, columns =['title', 'link','publish_date','scraped_date','text'])
            if df.empty:
                err = scrapper_name + ": err: Empty dataframe"
                err_logs.append(err)
            #print(df) # For debugging. To check if df is created
            #print(err_logs) # For debugging - to check if any errors occoured
            df = FilterFunction(df)
            emptydataframe("AZ",df)
            log_errors(err_logs)
            # df  = link_correction(df)
            return df
        except:
            print("AZ is not working")
            not_working_functions.append("AZ")
    def German():
        try :
            print("German")
            err_logs = []
            url = "https://www.tagesschau.de/suche2.html?query=IPO&sort_by=date"
            domain_url = "https://www.tagesschau.de"
            title,links,text,pub_date,scraped_date = [],[],[],[],[]
            try:
                page = requests.get(url)
                soup = BeautifulSoup(page.content,"html.parser")
                # print(soup)
                
            except:
                err = "German : err : Couldn't fetch " + url 
                err_logs.append(err)
                return 
            all_divs = soup.find_all("h3",{"class":"headline"})
            for div in all_divs:
                links.append(domain_url+div.a["href"])
            #Fetch all the necessary data 
            print(links)
            final_links = []
            today = date.today()
            for link in links:
                try:
                    page = requests.get(link)
                    soup = BeautifulSoup(page.content,"html.parser")
                # print("hi")
                # print(soup)
                # print(link)
                except:
                    err = "German : err : Couldn't fetch url " + link 
                    err_logs.append(err)
                    continue

                #Title of article

                title.append(soup.find("span" , {"class" : "seitenkopf__headline--text"}).text)
                # print(title)
                #Published Date
                pub_date.append(soup.find("div" , {"class" :"metatextline"}).text)
                # print(pub_date)

                #Text of article
                div = soup.find("main" , {"class" : "content-wrapper content-wrapper--show-cuts"})
                t = ""
                for i in div.find_all("p" , {"class" : "m-ten  m-offset-one l-eight l-offset-two textabsatz columns twelve"}):
                    t += i.text + " "
                text.append(t)
                # print(text)

                #Scrapped date 
                scraped_date.append(str(today))

                #Working links
                final_links.append(link)
            df = pd.DataFrame({"text":text,"link":final_links,"publish_date":pub_date,"scraped_date":scraped_date,"title":title})
            if df.empty:
                err = "German : err: Empty datframe"
                err_logs.append(err)
            df = df.drop_duplicates(subset=["link"])
            # df = FilterFunction(df)
            emptydataframe("German",df)
            # df  = link_correction(df)
            return df
        except :
            print("German not working")
            not_working_functions.append('German')
    def Japannews():
        try:
            title=[]
            text=[]
            dates = []
            s_date = []
            text = []
            try:
                print('Japannews')
                url = "https://www.japantimes.co.jp/tag/ipo/"
                # logging.info("Japannews: invoking requests.url()=" + url)
                page=requests.get(url)
                # logging.info("Japannews: Completed invoking requests.url()=" + url)
                soup=BeautifulSoup(page.content,'html.parser')
                #print(soup)
                links=[]
                for divtag in soup.find_all('div', {'class': 'main_content'}):
                        for a in divtag.find_all('a',href=True):
                            if a["href"].startswith("http"):
    #                             print(a["href"])
                                links.append(a["href"])


                for l in links:
                    try:
                        fetch = requests.get(l)
                        sp = BeautifulSoup(fetch.content, 'html.parser')
                        #print(sp)
                        title.append(sp.find("h1").text)

                        t=sp.find("div", {'class': 'entry'})
                        x=t.find_all("p")
                        tet=[]
                        for i in x:
                            tet.append(i.text)
                        text.append(''.join(tet))   

                        j=sp.find('div',{'class': 'meta-right'})
                        m=j.find_all('li')
        #                 print(m[2].text)
                        dates.append(m[2].text.strip())
                        from datetime import datetime, date
                        cur_date = str(datetime.today())
                        s_date.append(cur_date)     
                    except:
                        continue
            except:
                print('japan not working')
                # not_working_functions.append("Japan")
            print(title)
            japanese = pd.DataFrame(list(zip(title,links,dates,s_date,text)), 
                                columns =['title', 'link','publish_date','scraped_date','text'])
            japanese['publish_date']  = pd.to_datetime(japanese['publish_date'],errors='coerce',utc=True).dt.strftime('%d-%m-%Y' )
            df = FilterFunction(japanese)
            emptydataframe("Japan",df)
            # df  = link_correction(df)
            return df
        except:
            df1 = pd.DataFrame(columns =['title','link','publish_date','scraped_date'])
            return df1

    def Romania():
        try:
            try:
                print('Romania')
                url = "https://adevarul.ro/cauta/?terms=ofert%C4%83%20public%C4%83%20ini%C8%9Bial%C4%83&fromDate=2012-1-1&toDate=2021-3-10&tab=mrarticle&page=1&sortBy=cronologic"
                url1 = "https://adevarul.ro"
                logging.info("Romania: invoking requests.url()=" + url)
                page=requests.get(url).content
                logging.info("Romania: Completed invoking requests.url()=" + url)
                unicode_str = page.decode("utf-8")
                encoded_str = unicode_str.encode("ascii",'ignore')
                soup = BeautifulSoup(encoded_str, "html.parser")

                links = []
                dates = []
                s_date = []
                text = []
                title = []

                for divtag in soup.find_all('h2', {'class': 'defaultTitle'}):
                    for a in divtag.find_all('a',href=True):
                        links.append(url1 + a["href"])

                for link in links:
                    fetch = requests.get(link)
                    sp = BeautifulSoup(fetch.content, 'html.parser')
                    x=sp.find('h1').text
                    title.append(x)

                    y = sp.findAll("aside", { "class" : "tools clearfix" })

                    for i in y:
                        date_time = str(i.time['datetime'])
                        day = date_time.split("-")[0]
                        mon = date_time.split("-")[1]
                        year = "20" + date_time.split("-")[2]
                        print("-".join([day,mon,year]))
                        dates.append("-".join([year,mon,day]))

                    z = sp.find("div", { "class" : "article-body" }).text
            #         print(z)
                    text.append(z)
                    s_date.append(cur_date)
            except:
                print('romania is not working')
                not_working_functions("Romania")
            romania = pd.DataFrame(list(zip(title,links,dates,s_date,text)), 
                            columns =['title', 'link','publish_date','scraped_date','text'])
            # romania['publish_date']  = pd.to_datetime(romania['publish_date'],errors='coerce',utc=True).dt.strftime('%d-%b-%Y' " " "%H:%M:%S")
            # df = FilterFunction(romania)
            romania = translate_dataframe(romania)
            romania = FilterFunction(romania)
            emptydataframe("Romania",romania)
            #nonenglish
            # romania  = link_correction(romania)
            return romania
        except:
            df1 = pd.DataFrame(columns =['title','link','publish_date','scraped_date'])
            return df1

    def Swedish():
        try:
            import pandas as pd
            try:
                print('Swedish')
                url = "https://www.svd.se/sok?q=ipo"
                url1 = "https://www.svd.se"
                logging.info("Swedish: invoking requests.url()=" + url)
                page=requests.get(url).content
                logging.info("Swedish: Completed invoking requests.url()=" + url)
                unicode_str = page.decode("utf-8")
                encoded_str = unicode_str.encode("ascii",'ignore')
                soup = BeautifulSoup(encoded_str, "html.parser")

                links = []
                dates = []
                s_date = []
                text = []
                title = []

                for divtag in soup.find_all('a', {'class': 'Teaser-link'}):
                    links.append(url1 + divtag['href'])
                for link in links:
                    try:
                        fetch = requests.get(link)
                    except requests.exceptions.ConnectionError:
                        requests.status_code = "Connection refused"


                    sp = BeautifulSoup(fetch.content, 'html.parser')
                    x=sp.find('h1', {'class': 'ArticleHead-heading'})
                    if x is not None:
                            ementa = x.text
                    else:
                            ementa = None
                    title.append(ementa)

                    y = sp.findAll("div", { "class" : "Meta-part Meta-part--published" })
                    for x in y:
                        x = x.get_text()
                        x = re.sub('[^0-9-:.]+', ' ', x)
                        dates.append(x)

                    z = sp.find("div", { "class" : "Body"})
                    if z is not None:
                            n = z.text
                    else:
                            n = None
                    text.append(n)
                    s_date.append(cur_date)

            except:
                print('swedish is not working')
                not_working_functions.append("Swedish")
            swedish = pd.DataFrame(list(zip(title,links,dates,s_date,text)), 
                            columns =['title', 'link','publish_date','scraped_date','text'])
            # swedish['publish_date']  = pd.to_datetime(swedish['publish_date'],errors='coerce',utc=True).dt.strftime('%d-%b-%Y' " " "%H:%M:%S")
            df = FilterFunction(swedish)
            # emptydataframe("Swedish",df)
            # swedish  = link_correction(swedish)
            return df
        except:
            df1 = pd.DataFrame(columns =['title','link','publish_date','scraped_date'])
            return df1

    def Spanish():
        try:
            try:
                print('Spanish')
                urls=[
                    "https://www.abc.es/rss/feeds/abc_EspanaEspana.xml",
                    "http://ep01.epimg.net/rss/elpais/inenglish.xml",
                    "https://feeds.thelocal.com/rss/es",
                    "http://www.tenerifenews.com/feed/"
                ]
                # logging.info("www.fr.de: invoking requests.url()=" + url)
                page=requests.get(urls[0])
                soup=BeautifulSoup(page.content,features='lxml')
                soup.find_all()



                title=[]
                link=[]
                publish_date=[]
                scraped_date=[]
                #finding date for the above script
                import datetime
                x=datetime.datetime.now()
                x=x.date()
                x=str(x)
                x=x.split('-')
                date=x[2]
                #print(date)
                month=x[1]
                month=str(month)
                #print(month)
                if (month=='01'):
                    mon='Jan'
                elif (month=='02'):
                    mon='Feb'
                elif (month=='03'):
                    mon='Mar'
                elif (month=='04'):
                    mon='Apr'
                elif (month=='05'):
                    mon='May'
                elif (month=='06'):
                    mon='Jun'
                elif (month=='07'):
                    mon='Jul'
                elif (month=='08'):
                    mon='Aug'
                elif (month=='09'):
                    mon='Sep'
                elif (month=='10'):
                    mon=='Oct'
                elif (month=='11'):
                    mon='Nov'
                else:
                    mon='Dec'
                date=str(date)
    
                date=int(date)
                date_int=date-1
                date_int=str(date_int)
                if(len(date_int)==1):
                    date_int='0'+date_int
                date_int=str(date_int)
                date=str(date)
                date_int=str(date_int)
    

                for i in range(0,len(soup.find_all('title'))):
                    pub_date=soup.find_all('pubdate')[i-1].text
                #print(pub_date)
                    pub_date=pub_date.split(' ')
                    pub_date = str(pub_date)
                    pub_date = re.sub('[^A-Za-z0-9%:]+', ' ', pub_date)
                    act_date=pub_date[1]
                    act_mon=pub_date[2]
                    #print(act_date,act_mon)
                    act_date=str(act_date)
                    act_mon=str(act_mon)
                    #print(act_mon,mon)

                    if(act_mon==mon):
                        if(act_date==date or act_date==date_int):
                            title.append(soup.find_all('title')[i].text)
                            link.append(soup.find_all('guid')[i-1].text)
                            scraped_date.append(pub_date)
                            publish_date.append(pub_date)

            except:
                print('Spanish not working')
                not_working_functions("Spanish")

            import pandas as pd 
            df2 = pd.DataFrame(list(zip(title,link,publish_date,scraped_date)), 
                        columns =['title','link','publish_date','scraped_date'])
            df2


            # In[175]:


            title=[]
            link=[]
            publish_date=[]
            scraped_date=[]


            try:
                page=requests.get(urls[2])
                soup=BeautifulSoup(page.content,features='lxml')
                soup.find_all()


                # In[176]:


                for i in range(0,len(soup.find_all('title'))):
                        pub_date=soup.find_all('pubdate')[i-1].text
                        #print(pub_date)
                        pub_date=pub_date.split(' ')

                        act_date=pub_date[1]
                        act_mon=pub_date[2]
                        #print(act_date,act_mon)
                        act_date=str(act_date)
                        act_mon=str(act_mon)
                        #print(act_mon,mon)

                        if(act_mon==mon):
                            if(act_date==date or act_date==date_int):
                                title.append(soup.find_all('title')[i].text)
                                link.append(soup.find_all('guid')[i-1].text)
                                scraped_date.append(pub_date)
                                publish_date.append(pub_date)


                # In[177]:
            except:
                print('Spanish not working')
                not_working_functions.append("Spanish")

            import pandas as pd 
            df3 = pd.DataFrame(list(zip(title,link,publish_date,scraped_date)), 
                        columns =['title','link','publish_date','scraped_date'])
            df3


            # In[178]:


            title=[]
            link=[]
            publish_date=[]
            scraped_date=[]

            try:
                page=requests.get(urls[3])
                soup=BeautifulSoup(page.content,features='lxml')
                soup.find_all()


                # In[179]:


                for i in range(0,len(soup.find_all('lastBuildDate'))):
                        pub_date=soup.find_all('pubdate')[i-1].text
                #print(pub_date)
                        pub_date=pub_date.split(' ')
                        act_date=pub_date[1]
                        act_mon=pub_date[2]
                #print(act_date,act_mon)
                        act_date=str(act_date)
                        act_mon=str(act_mon)
                #print(act_mon,mon)

                        if(act_mon==mon):
                            if(act_date==date or act_date==date_int):
                                title.append(soup.find_all('title')[i].text)
                                link.append(soup.find_all('guid')[i-1].text)
                                scraped_date.append(pub_date)
                                publish_date.append(pub_date)


                # In[180]:
            except:
                print('Spanish not working')
                not_working_functions.append(("Spanish"))

            import pandas as pd 
            df4 = pd.DataFrame(list(zip(title,link,publish_date,scraped_date)), 
                        columns =['title','link','publish_date','scraped_date'])

            frames = [df2,df3,df4]
            fin=pd.concat(frames)
            fin=fin.reset_index()

            fin=fin.drop(['index'],axis=1)

    #         get_ipython().system('pip install googletrans==3.1.0a0')
            import sys


            from googletrans import Translator
            import googletrans


            translator = Translator()
            #translated=translator.translate(listtt[0][:2000],dest='en')


            title=[]
            link=[]
            scraped_date=[]
            publish_date=[]
            for i in range(0,fin.shape[0]):
                    translations=translator.translate(fin['title'][i])
                    title.append(translations.text)
                    link.append(fin['link'][i])
                    scraped_date.append(fin['scraped_date'][i])
                    publish_date.append(fin['publish_date'][i])
            fin = pd.DataFrame(list(zip(title,link,publish_date,scraped_date)), 
                        columns =['title','link','publish_date','scraped_date'])
            fin['publish_date']  = pd.to_datetime(fin['publish_date'],errors='coerce',utc=True).dt.strftime('%d-%b-%Y' " " "%H:%M:%S")
            Fin = FilterFunction(fin)
            emptydataframe("Spanish",Fin)
            # Fin  = link_correction(Fin)
            return Fin
        except:
            df1 = pd.DataFrame(columns =['title','link','publish_date','scraped_date'])
            return df1

    def Russian():
        try :
            print("Russian")
            err_logs = []
            url = "https://ipo.einnews.com/search/IPO/?search%5B%5D=news&search%5B%5D=press&order=relevance"
            domain_url = "https://ipo.einnews.com"
            title,links,text,pub_date,scraped_date = [],[],[],[],[]
            try:
                page = requests.get(url)
                soup = BeautifulSoup(page.content,"html.parser")
                # print(soup)
                
            except:
                err = "Russian : err : Couldn't fetch " + url 
                err_logs.append(err)
                return 
            all_divs = soup.find_all("div",{"class":"article-content"})
            for div in all_divs:
                links.append(domain_url+div.h3.a["href"])
            #Fetch all the necessary data 
            print(links)
            final_links = []
            today = date.today()
            for link in links:
                try:
                    page = Article(link)
                    page.download()
                    page.parse()
                    title.append(page.title)  
                  
                    pub_date.append(page.publish_date)
                    
                    text.append(page.text)
                    # print(text)

                    #Scrapped date 
                    scraped_date.append(str(today))

                    #Working links
                    final_links.append(link)
                except:
                  continue
            df = pd.DataFrame({"text":text,"link":final_links,"publish_date":pub_date,"scraped_date":scraped_date,"title":title})
            if df.empty:
                err = "Russian : err: Empty dataframe"
                err_logs.append(err)
            df = df.drop_duplicates(subset=["link"])
            df = FilterFunction(df)
            emptydataframe("Russian",df)
            # df  = link_correction(df)
            return df
        except :
            print("Russian not working")
            not_working_functions.append('Russian')


    def GoogleAlert1():
        try:
            articles=[]
            links=[]
            dates=[]
            scraped_date=[]
            text = []
            try:
                print('GoogleAlert1')
                import html
                url="https://www.google.com/alerts/feeds/01154643345605641334/12910713483086187784"
                page=requests.get(url)
                soup=BeautifulSoup(page.content,features='xml')

                #print(soup.prettify())
                for i in range(0,len(soup.find_all('entry'))):
                        pdd=soup.find_all('entry')[i]
                        for title in pdd.find_all('title'):
                            articles.append(html.unescape(title.text))
                        for content in pdd.find_all('content'):
                            text.append(html.unescape(content.text))
                        for link in pdd.find_all('link'):
                            links.append(html.unescape(link['href']))
                        for date in pdd.find_all('published'):
                            dates.append(date.text)
                            scraped_date.append(date.text)
            except:
                print('Google Alert is not working')
                not_working_functions.append("Google alert 1")
            df_google = pd.DataFrame(list(zip(articles,text,links,dates,scraped_date)), 
                        columns =['title','text', 'link','publish_date','scraped_date'])

            def clean_link(u):
                    u = u.replace('https://www.google.com/url?rct=j&sa=t&url=', '')

                    return(u)

            urls = df_google['link']

            clean_url = []
            for url in urls:
                clean_url.append(clean_link(url))

            df_google['link'] = clean_url
            Df2 = FilterFunction(df_google)
            emptydataframe("Google alert1",Df2)
            # Df2  = link_correction(Df2)
            return Df2
        except:
            df1 = pd.DataFrame(columns =['title','link','publish_date','scraped_date'])
            return df1
    def GoogleAlert2():
        try:
            articles=[]
            links=[]
            dates=[]
            scraped_date=[]
            text = []
            try:
                print('GoogleAlert2')
                import html
                url="https://www.google.com/alerts/feeds/01154643345605641334/6308064720496016673"
                page=requests.get(url)
                soup=BeautifulSoup(page.content,features='xml')

                #print(soup.prettify())
                for i in range(0,len(soup.find_all('entry'))):
                        pdd=soup.find_all('entry')[i]
                        for title in pdd.find_all('title'):
                            articles.append(html.unescape(title.text))
                        for content in pdd.find_all('content'):
                            text.append(html.unescape(content.text))
                        for link in pdd.find_all('link'):
                            links.append(html.unescape(link['href']))
                        for date in pdd.find_all('published'):
                            dates.append(date.text)
                            scraped_date.append(date.text)
            except:
                print('Google Alert2 is not working')
                not_working_functions.append("Google Alert2")
            df_google = pd.DataFrame(list(zip(articles,text,links,dates,scraped_date)), 
                        columns =['title','text', 'link','publish_date','scraped_date'])

            def clean_link(u):
                    u = u.replace('https://www.google.com/url?rct=j&sa=t&url=', '')

                    return(u)

            urls = df_google['link']

            clean_url = []
            for url in urls:
                clean_url.append(clean_link(url))

            df_google['link'] = clean_url
            Df2 = FilterFunction(df_google)
            emptydataframe("Google Alert 2",Df2)
            # Df2  = link_correction(Df2)
            return Df2
        except:
            df1 = pd.DataFrame(columns =['title','link','publish_date','scraped_date'])
            return df1

    def GoogleAlert3():
        try:
            articles=[]
            links=[]
            dates=[]
            scraped_date=[]
            text = []
            try:
                print('GoogleAlert3')
                import html
                url="https://www.google.com/alerts/feeds/01154643345605641334/13304767747222280933"
                page=requests.get(url)
                soup=BeautifulSoup(page.content,features='xml')

                #print(soup.prettify())
                for i in range(0,len(soup.find_all('entry'))):
                        pdd=soup.find_all('entry')[i]
                        for title in pdd.find_all('title'):
                            articles.append(html.unescape(title.text))
                        for content in pdd.find_all('content'):
                            text.append(html.unescape(content.text))
                        for link in pdd.find_all('link'):
                            links.append(html.unescape(link['href']))
                        for date in pdd.find_all('published'):
                            dates.append(date.text)
                            scraped_date.append(date.text)
            except:
                print('Google Alert 3 is not working')
                not_working_functions.append("Google Alert 3")
            df_google = pd.DataFrame(list(zip(articles,text,links,dates,scraped_date)), 
                        columns =['title','text', 'link','publish_date','scraped_date'])

            def clean_link(u):
                    u = u.replace('https://www.google.com/url?rct=j&sa=t&url=', '')

                    return(u)

            urls = df_google['link']

            clean_url = []
            for url in urls:
                clean_url.append(clean_link(url))

            df_google['link'] = clean_url
            Df2 = FilterFunction(df_google)
            emptydataframe("Google Alert 3",Df2)
            # Df2  = link_correction(Df2)
            return Df2
        except:
            df1 = pd.DataFrame(columns =['title','link','publish_date','scraped_date'])
            return df1

    def GoogleAlert4():
        try:
            articles=[]
            links=[]
            dates=[]
            scraped_date=[]
            text = []
            try:
                print('GoogleAlert4')
                import html
                url="https://www.google.com/alerts/feeds/01154643345605641334/3217985541207435755"
                page=requests.get(url)
                soup=BeautifulSoup(page.content,features='xml')

                #print(soup.prettify())
                for i in range(0,len(soup.find_all('entry'))):
                        pdd=soup.find_all('entry')[i]
                        for title in pdd.find_all('title'):
                            articles.append(html.unescape(title.text))
                        for content in pdd.find_all('content'):
                            text.append(html.unescape(content.text))
                        for link in pdd.find_all('link'):
                            links.append(html.unescape(link['href']))
                        for date in pdd.find_all('published'):
                            dates.append(date.text)
                            scraped_date.append(date.text)
            except:
                print('Google Alert4 is not working')
                not_working_functions("Google Alert 4")
            df_google = pd.DataFrame(list(zip(articles,text,links,dates,scraped_date)), 
                        columns =['title','text', 'link','publish_date','scraped_date'])

            def clean_link(u):
                    u = u.replace('https://www.google.com/url?rct=j&sa=t&url=', '')

                    return(u)

            urls = df_google['link']

            clean_url = []
            for url in urls:
                clean_url.append(clean_link(url))

            df_google['link'] = clean_url
            Df2 = FilterFunction(df_google)
            emptydataframe("Google Alert 4",Df2)
            # Df2  = link_correction(Df2)
            return Df2
        except:
            df1 = pd.DataFrame(columns =['title','link','publish_date','scraped_date'])
            return df1

    def GoogleAlert5():
        try:
            articles=[]
            links=[]
            dates=[]
            scraped_date=[]
            text = []
            try:
                print('GoogleAlert5')
                import html
                url="https://www.google.com/alerts/feeds/01154643345605641334/6882160862931884057"
                page=requests.get(url)
                soup=BeautifulSoup(page.content,features='xml')

                #print(soup.prettify())
                for i in range(0,len(soup.find_all('entry'))):
                        pdd=soup.find_all('entry')[i]
                        for title in pdd.find_all('title'):
                            articles.append(html.unescape(title.text))
                        for content in pdd.find_all('content'):
                            text.append(html.unescape(content.text))
                        for link in pdd.find_all('link'):
                            links.append(html.unescape(link['href']))
                        for date in pdd.find_all('published'):
                            dates.append(date.text)
                            scraped_date.append(date.text)
            except:
                print('Google Alert5 is not working')
                not_working_functions.append("Google alert 5")
            df_google = pd.DataFrame(list(zip(articles,text,links,dates,scraped_date)), 
                        columns =['title','text', 'link','publish_date','scraped_date'])

            def clean_link(u):
                    u = u.replace('https://www.google.com/url?rct=j&sa=t&url=', '')

                    return(u)

            urls = df_google['link']

            clean_url = []
            for url in urls:
                clean_url.append(clean_link(url))

            df_google['link'] = clean_url
            Df2 = FilterFunction(df_google)
            emptydataframe("Google Alert 5",Df2)
            # df_google  = link_correction(df_google)
            return df_google
        except:
            df1 = pd.DataFrame(columns =['title','link','publish_date','scraped_date'])
            return df1
    
    def IPOMonitor():
        try:
            links = []
            title = []
            dates = []
            s_date = []
            text = []
            try:
                print('IPOmonitor')
                url = "https://www.ipomonitor.com/pages/ipo-news.html"
                page=requests.get(url)
                soup=BeautifulSoup(page.content,'html.parser')
                for divtag in soup.find_all('span'):
                    for a in divtag.find_all('a',href=True):

                        links.append(a["href"])
                        title.append(a.text)
                for i in soup.find_all('dd'):
                    for k in i.find_all('span'):
                        s = k.text
                        dates.append(s)
                        s_date.append(cur_date)
                        text.append(' ')
            except:
                print('Ipo monitor not working')
                not_working_functions.append("IPOMonitor")
            
            df2 = pd.DataFrame(list(zip(title,links,dates,s_date,text)), 
                            columns =['title', 'link','publish_date','scraped_date','text'])
            df = FilterFunction(df2)
            emptydataframe("IPO Monitor",df)
            # df  = link_correction(df)
            return df
        except:
            df1 = pd.DataFrame(columns =['title','link','publish_date','scraped_date'])
            return df1
    
    def Seenews():
        try:
            links = [] 
            title = []
            dates = []
            text = []
            s_date = []
            try:
                print('Seenews')
                urls = "https://seenews.com/news/search_results/?keywords=ipo&order_by=name&order=asc&optradio=on&company_id=&company_owner=&capital_from=&capital_to=&total_assets_from=&total_assets_to=&total_revenue_from=&total_revenue_to=&number_of_employees_from=&number_of_employees_to=&net_profit_from=&net_profit_to=&net_loss_from=&net_loss_to=&seeci_from=&seeci_to=&ebitda_from=&ebitda_to=&year=&statement_type="
                url1 = "https://seenews.com"
                page=requests.get(urls)
                soup=BeautifulSoup(page.content,'html')
                divs = soup.find_all('dt',{'class':'search-result-title'})
                for i in divs:
                    links.append(url1 + i.a["href"])
                for l in links:
                    fetch = requests.get(l)
                    sp = BeautifulSoup(fetch.content, 'html.parser')
                    x=sp.find("div", { "class" : "heading--content f-java" })
                    if x is not None:
                        ementa = x.text
                    else:
                        ementa = None
                    title.append(ementa)
                    y=sp.find("div", { "class" : "post-date" })
                    if y is not None:
                        d = y.text
                        d = d.split()
                        d = d[1:5]
                        d = ' '.join(d)
                    else:
                        d = None
                    dates.append(d)
                    z=sp.find("div", { "class" : "content-description" })
                    if z is not None:
                        n = z.text
                    else:
                        n = None
                    text.append(n)
                    from datetime import datetime, date
                    cur_date = str(datetime.today())
                    s_date.append(cur_date)
            except:
                print('Seenews not working')
                not_working_functions.append("Seenews")
            df2 = pd.DataFrame(list(zip(title,links,dates,s_date,text)), 
                    columns =['title', 'link','publish_date','scraped_date','text'])
            df = FilterFunction(df2)
            emptydataframe("Seenews",df)
            # df  = link_correction(df)
            return df
        except:
            df1 = pd.DataFrame(columns =['title','link','publish_date','scraped_date'])
            return df1

    def Bisnis():
        try :
            print("Bisnis")
            err_logs = []
            url = "https://search.bisnis.com/?q=IPO"
            domain_url = "https://www.reuters.com"
            title,links,text,pub_date,scraped_date = [],[],[],[],[]
            try:
                page = requests.get(url)
                soup = BeautifulSoup(page.content,"html.parser")
                # print(soup)
                
            except:
                err = "Bisnis : err : Couldn't fetch " + url 
                err_logs.append(err)
                return 
            all_divs = soup.find_all("div",{"class":"col-sm-8"})
            for div in all_divs:
                links.append(div.a["href"])
            #Fetch all the necessary data 
            print(links)
            final_links = []
            today = date.today()
            for link in links:
                try:
                    page = requests.get(link)
                    soup = BeautifulSoup(page.content,"html.parser")
                # print(soup)
                # print(link)
                except:
                    err = "Bisnis : err : Couldn't fetch url " + link 
                    err_logs.append(err)
                    continue
            
                #Title of article 
                if(soup.find("h1" , {"class" : "title-only"}) == None):
                    continue
                title.append(soup.find("h1" , {"class" : "title-only"}).text)  
                # print(title)

                if(soup.find("div" , {"class" :"author"}) == None):
                    continue 
                pub_date.append(soup.find("div" , {"class" :"author"}).span)
                #Text of article
                if(soup.find("div" , {"class" : "col-sm-10"}) == None ) :
                    continue 
                div = soup.find("div" , {"class" : "col-sm-10"})
                t = ""
                for i in div.find_all("p"):
                    t += i.text + " "
                text.append(t)
                

                #Scrapped date 
                scraped_date.append(str(today))

                #Working links
                final_links.append(link)
            df = pd.DataFrame({"text":text,"link":final_links,"publish_date":pub_date,"scraped_date":scraped_date,"title":title})
            if df.empty:
                err = "Bisnis : err: Empty dataframe"
                err_logs.append(err)
            df = df.drop_duplicates(subset=["link"])
            df = translate_dataframe(df)
            df.head(10)
            df = FilterFunction(df)
            emptydataframe("Bisnis",df)
            # df  = link_correction(df)
            return df
        except :
            print("Bisnis not working")
            not_working_functions.append('bisnis')
    def RomaniaNew():
        try:
            try:
                print('RomaniaNew')
                urls = "https://www.romania-insider.com/search/node?keys=ipo"
                links = [] 
                title = []
                dates= []
                s_date = []
                text = []
                page=requests.get(urls)
                soup=BeautifulSoup(page.content,'html')
                h = soup.find_all('h3',{'class':'search-result__title'})
                for i in h:
                    links.append(i.a["href"])
                for l in links:
                    fetch = requests.get(l)
                    sp = BeautifulSoup(fetch.content, 'html.parser')
                    x=sp.find("h1", {"class" : "field field--name-field-title field--type-string field--label-hidden field__item" })
                    if x is not None:
                        ementa = x.text
                    else:
                        ementa = None
                    title.append(ementa)
                    y=sp.find("div", { "class" : "field field--name-field-date field--type-datetime field--label-hidden field__item" })
                    if y is not None:
                        d = str(y.text).strip()
                        d = datetime.strptime(d,"%d %B %Y").strftime("%Y-%m-%d")
                    else:
                        d = None
                    dates.append(d)
                    z=sp.find("div", { "class" : "clearfix text-formatted field field--name-body field--type-text-with-summary field--label-hidden field__item" })
                    if z is not None:
                        n = z.text
                    else:
                        n = None
                    text.append(n)
                    cur_date = str(datetime.today())
                    s_date.append(cur_date)
                
                df2 = pd.DataFrame({"text":text,"link":links,"publish_date":dates,"scraped_date":s_date,"title":title})
                df2 = FilterFunction(df2)
                emptydataframe("Romania New ",df2)
                # df2  = link_correction(df2)
                return df2
            except:
                print('RomaniaNew not working')
                # not_working_functions.append("Romania New")
        except:
            df1 = pd.DataFrame(columns =['title','link','publish_date','scraped_date'])
            return df1   

    def romania_insider():
        try:
            print("Romania Insider Dominician Republic")
            err_logs = []
            err_index = []
            baseSearchUrl = "https://www.romania-insider.com/search/node?keys=ipo"
            domainUrl = "https://www.romania-insider.com"

            scrapedData = {}
            links = []
            titles = []
            queryUrl = baseSearchUrl
            try:
                headers = {
                    'User-Agent': "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 Chrome/58.0.3029.110 Safari/537.36"}
                pageSource = requests.get(queryUrl, headers=headers)
            except:
                err = "romania_insider: err: Failed to access search url: " + queryUrl + " and convert it to soup object"
                err_logs.append(err)
            # with open("response.html", "wb") as f:
            #     f.write(pageSource.content)
            parsedSource = BeautifulSoup(pageSource.content, "html.parser", from_encoding="iso-8859-1")
            for item in parsedSource.find("ol", class_="search-results node_search-results").find_all("li"):
                requiredTag = item.find("h3").find("a")
                currentArticleTitle = requiredTag.text
                # print(currentArticleTitle)
                currentArticleLink = requiredTag["href"]
                # print(currentArticleLink)
                if currentArticleLink[0] == "/":
                    links.append(domainUrl + currentArticleLink)
                else:
                    links.append(currentArticleLink)
                titles.append(currentArticleTitle)

            scrapedData["title"] = titles
            scrapedData["link"] = links
            # print(titles)
            # print(links)

            # Article's date and description scraping
            ArticleDates = []
            ScrapeDates = []
            ArticleBody = []
            for link in links:
                articleText = ""
                try:
                    pageSource = requests.get(link, headers=headers)
                    parsedSource = BeautifulSoup(pageSource.content, "html.parser", from_encoding="iso-8859-1")
                except:
                    err = "romania_insider: err: Failed to access article link : " + link
                    ArticleDates.append("Error")
                    err_logs.append(err)
                    err_index.append(link)
                    continue
                # with open("response.html", "wb") as f:
                #     f.write(pageSource.content)
                # break
                if parsedSource.find("div", class_="field field--name-field-date field--type-datetime field--label-hidden field__item"):
                    sourceDateTimeTag = parsedSource.find("div", class_="field field--name-field-date field--type-datetime field--label-hidden field__item")
                else:
                    err = "romania_insider: err: Failed to retrieve date from article : " + link
                    ArticleDates.append("Error")
                    err_logs.append(err)
                    err_index.append(link)
                    continue
                sourceDateTime = datetime.strptime(sourceDateTimeTag.text, "%d %B %Y").strftime("%Y-%m-%d")
                # print(sourceDateTime)
                ArticleDates.append(sourceDateTime)
                ScrapeDates.append(datetime.today().strftime("%d-%m-%Y"))
                # print(ArticleDates)
                # if parsedSource.find("div", class_="entry-content"):
                #     textBodyDiv = parsedSource.find("div", class_="entry-content")
                # else:
                #     err = "romania_insider: err: Failed to retrieve article text: " + link
                #     ArticleBody.append("Error")
                #     err_logs.append(err)
                #     err_index.append(link)
                #     continue
                for item in parsedSource.find("div", class_="clearfix text-formatted field field--name-body field--type-text-with-summary field--label-hidden field__item").find_all("p"):
                    articleText += item.text.strip()
                print(articleText)
                ArticleBody.append(articleText)
            scrapedData["publish_date"] = ArticleDates
            scrapedData["scraped_date"] = ScrapeDates
            scrapedData["text"] = ArticleBody
            # print(ArticleBody)

            # Clean and Normalize links
            if len(err_index) != 0:
                for e in err_index:
                    idx = scrapedData["link"].index(e)
                    scrapedData["link"].pop(idx)
                    scrapedData["title"].pop(idx)
                    scrapedData["publish_date"].pop(idx)

            # DataFrame creation
            romania_insiderDF = pd.DataFrame(scrapedData)
            romania_insiderDF = romania_insiderDF.drop_duplicates(subset=["link"])
            if romania_insiderDF.empty:
                err = "romania_insider: err: Empty dataframe"
                err_logs.append(err)
            df = FilterFunction(romania_insiderDF)
            emptydataframe("Romania Insider",df)
            log_errors(err_logs)
            # df  = link_correction(df)
            return df
        except:
            print("Romania Insider Dominic Republic not working")
            not_working_functions.append("Romania Insider Dominic Rep")
    def cnbc1():
        try:
            print("CNBC Barbados")
            err_logs = []
            baseSearchUrl = "https://www.cnbc.com/id/10000666/device/rss"
            scrapedData = {}
            links = []
            titles = []
            err_index = []
            ArticleDates = []
            ScrapeDates = []
            ArticleBody = []
            queryUrl = baseSearchUrl
            try:
                pageSource = requests.get(baseSearchUrl)
            except:
                err = "cnbc: err: Failed to access search url: " + queryUrl + " and convert it to soup object"
                err_logs.append(err)
                exit()
            # with open("response.xml", "wb") as f:
            #     f.write(pageSource.content)
            # break
            parsedSource = BeautifulSoup(pageSource.content, "xml")
            for eachItem in parsedSource.find_all("item"):
                currentArticleTitle = eachItem.find("title").text
                currentArticleLink = eachItem.find("link").text
                currentArticleDate = datetime.strptime(str(eachItem.find("pubDate").text).split("GMT", maxsplit=2)[0].strip(),
                                                    "%a, %d %b %Y %H:%M").strftime("%Y-%m-%d")
                # articleText = str(eachItem.find("description").text).split("CDATA[ ", maxsplit=2)[1].rstrip(" ]]")
                articleText = str(eachItem.find("description").text).split("CDATA[ ", maxsplit=2)[0].replace("#039;", "")
                ArticleBody.append(articleText)

                titles.append(currentArticleTitle)
                links.append(currentArticleLink)
                ArticleDates.append(currentArticleDate)
                ScrapeDates.append(datetime.today().strftime("%d-%m-%Y"))
            scrapedData["title"] = titles
            scrapedData["link"] = links
            scrapedData["publish_date"] = ArticleDates
            scrapedData["scraped_date"] = ScrapeDates
            scrapedData["text"] = ArticleBody

            # DataFrame creation
            cnbcDF = pd.DataFrame(scrapedData)
            cnbcDF = cnbcDF.drop_duplicates(subset=["link"])
            if cnbcDF.empty:
                err = "cnbc: err: Empty dataframe"
                err_logs.append(err)
            df = FilterFunction(cnbcDF)
            emptydataframe("Cnbc barbados",df)
            log_errors(err_logs)
            # df  = link_correction(df)
            return df       
        except:
            not_working_functions.append("CNBC Barbados")
            print("CNBC Barbados not working")
    def RomaniaInsider():
        try:
            try:
                print('RomaniaInsider')
                urls = "https://www.romania-insider.com/index.php/daily-news/capital-markets?page=0"
                url1 = "https://www.romania-insider.com"

                links = [] 
                title = []
                dates= []
                s_date = []
                text = []
                page=requests.get(urls)
                soup=BeautifulSoup(page.content,'html')
                h = soup.find_all('div',{'class':'field field--name-field-title field--type-string field--label-hidden field__item'})
                for i in h:
                    links.append(url1 + i.a["href"])
                for l in links:
                    fetch = requests.get(l)
                    sp = BeautifulSoup(fetch.content, 'html.parser')

                    x=sp.find("h1", {"class" : "field field--name-field-title field--type-string field--label-hidden field__item" })
                    if x is not None:
                        ementa = x.text
                    else:
                        ementa = None
                    title.append(ementa)
                    y=sp.find("div", { "class" : "field field--name-field-date field--type-datetime field--label-hidden field__item" })
                    if y is not None:
                        d = y.text
                        d = datetime.strptime(d,"%d %B %Y").strftime("%Y-%m-%d")
                    else:
                        d = None
                    dates.append(d)
                    z=sp.find("div", { "class" : "clearfix text-formatted field field--name-body field--type-text-with-summary field--label-hidden field__item" })
                    if z is not None:
                        n = z.text
                    else:
                        n = None
                    text.append(n)
                    from datetime import datetime, date
                    cur_date = str(datetime.today())
                    s_date.append(cur_date)
            except:
                print('RomaniaInsider not working')
                not_working_functions.append("RomaniaInsider")

            df2 = pd.DataFrame({"text":text,"link":links,"publish_date":dates,"scraped_date":s_date,"title":title})
            df2 = FilterFunction(df2)
            emptydataframe("RomaniaInsider",df2)
            # df2  = link_correction(df2)
            return df2
        except:
            df1 = pd.DataFrame(columns =['title','link','publish_date','scraped_date'])
            return df1
    
    def SpaceMoney():
        try:
            try:
                print('spacemoney')
                urls = "https://www.spacemoney.com.br/noticias/ipos/"
                links = [] 
                title = []
                dates = []
                s_date = []
                text = []
                page=requests.get(urls)
                soup=BeautifulSoup(page.content,'html')
                divs = soup.find_all('div',{'class':'linkNoticia crop'})
                for i in divs:
                    links.append(i.a["href"])
                for l in links:
                    fetch = requests.get(l)
                    sp = BeautifulSoup(fetch.content, 'html.parser')

                    x=sp.find("h1")
                    if x is not None:
                        ementa = x.text
                    else:
                        ementa = None
                    title.append(ementa)
                    y=sp.find("section", { "class" : "dataAutor" })
                    if y is not None:
                        d = y.text
                    else:
                        d = None
                    dates.append(d)
                    z=sp.find("article", { "class" : "grid_8 alpha" })
                    if z is not None:
                        n = z.text
                    else:
                        n = None
                    text.append(n)
                    from datetime import datetime, date
                    cur_date = str(datetime.today())
                    s_date.append(cur_date)
            except:
                print('Spacemoney not working')
                not_working_functions.append("Spacemoney")

            df2 = pd.DataFrame({"text":text,"link":links,"publish_date":dates,"scraped_date":s_date,"title":title})
            # df2 = FilterFunction(df2)
            df = translate_dataframe(df2)
            df = FilterFunction(df)
            emptydataframe("Spacemoney",df)
            # df  = link_correction(df)
            return df
        except:
            df1 = pd.DataFrame(columns =['title','link','publish_date','scraped_date'])
            return df1

    def Carteira():
        try:
            # print("Carteira")
            body = [] 
            link = []
            date = []
            title=[]
            # link=[]
            pub_date=[]
            scraped_date=[]
            try:
                print('Carteira')
                urls = "https://carteirasa.com.br/?s=Ipo"
                def get_links(urls):

                        links = [] 
                        page=requests.get(urls)
                        soup=BeautifulSoup(page.content,'html')
                        divs = soup.find_all('div',{'class':'item-mid'})
                        for i in divs:
                            links.append(i.a["href"])
                        return links
                
                links1 = get_links(urls)
                
                from datetime import datetime

                now = datetime.now()

                current_time = now.strftime("%H:%M:%S")
                from newspaper import Article
                for ur in links1:
                    try:
                        article = Article(ur)
                        article.download()
                        article.parse()
                        # print(article.text)

                        link.append(ur)
                        scraped_date.append(current_time)
                        body.append(article.text)
                        title.append(article.title)

                        date.append(article.publish_date)

                    except:

                        continue
                    time.sleep(0.5)

                df = pd.DataFrame({"Article":body,"Link":link,"Publish Date":date,"Scrape Date":scraped_date,"Title":title})

                links1 = get_links(urls)
                from datetime import datetime

                now = datetime.now()

                current_time = now.strftime("%H:%M:%S")
                from newspaper import Article
                for ur in links1:
                    try:
                        article = Article(ur)
                        article.download()
                        article.parse()
                        link.append(ur)
                        scraped_date.append(current_time)
                        body.append(article.text)
                        title.append(article.title)
                        date.append(article.publish_date)

                    except:

                        continue
                    time.sleep(0.5)

                df = pd.DataFrame({"Article":body,"Link":link,"Publish Date":date,"Scrape Date":scraped_date,"Title":title})

                from datetime import datetime

                now = datetime.now()

                current_time = now.strftime("%H:%M:%S")
                from newspaper import Article
                for ur in links1:
                    try:
                        article = Article(ur)
                        article.download()
                        article.parse()
                        # print(article.text)

                        link.append(ur)
                        scraped_date.append(current_time)
                        body.append(article.text)
                        title.append(article.title)

                        date.append(article.publish_date)

                    except:
                        continue
                    time.sleep(0.5)
            except:
                print('Carteira is not working')
                not_working_functions.append("Carteira")
            dic = {"text":body,"link":link,"publish_date":date,"scraped_date":scraped_date,"title":title}

            df = pd.DataFrame.from_dict(dic,orient='index')
            df = df.transpose()
            df.dropna(inplace=True)
            df = FilterFunction(df)
            emptydataframe("Carteira",df)
            # df  = link_correction(df)
            return df
        except:
            df1 = pd.DataFrame(columns =['title','link','publish_date','scraped_date'])
            return df1
    
    def Kontan1():
        try :
            print("Kontan1")
            err_logs = []
            url = "https://www.kontan.co.id/search/?search=ipo&Button_search="
            domain_url = "https://www.kontan.co.id"
            title,links,text,pub_date,scraped_date = [],[],[],[],[]
            try:
                page = requests.get(url)
                soup = BeautifulSoup(page.content,"html.parser")
                # print(soup)
                
            except:
                err = "Kontan1 : err : Couldn't fetch " + url 
                err_logs.append(err)
                return 
            all_divs = soup.find_all("div",{"class":"sp-hl linkto-black"})
            for div in all_divs:
                links.append("https:"+div.a["href"])
            #Fetch all the necessary data 
            print(links)
            final_links = []
            today = date.today()
            for link in links:
                try:
                    page = requests.get(link)
                    soup = BeautifulSoup(page.content,"html.parser")
                # print("hi")
                # print(soup)
                # print(link)
                except:
                    err = "Kontan1 : err : Couldn't fetch url " + link 
                    err_logs.append(err)
                    continue

                #Title of article
                if(soup.find("h1" , {"class" : "detail-desk"})== None):
                    continue
                title.append(soup.find("h1" , {"class" : "detail-desk"}).text)
                print(title)
                #Published Date
                pub_date.append(soup.find("div" , {"class" :"fs14 ff-opensans font-gray"}))
                # print(pub_date)

                #Text of article
                div = soup.find("div" , {"class" : "tmpt-desk-kon"})
                t = ""
                for i in div.find_all("p"):
                    t += i.text + " "
                text.append(t)
                # print(text)

                #Scrapped date 
                scraped_date.append(str(today))

                #Working links
                final_links.append(link)
            df = pd.DataFrame({"text":text,"link":final_links,"publish_date":scraped_date,"scraped_date":scraped_date,"title":title})
            if df.empty:
                err = "Kontan1 : err: Empty datKontan1ame"
                err_logs.append(err)
            df = df.drop_duplicates(subset=["link"])
            df = translate_dataframe(df)
            df = FilterFunction(df)
            emptydataframe("Kontan1",df)
            # df  = link_correction(df)
            return df
        except :
            print("Kontan1 not working")
            not_working_functions.append('Kontan1')
    
    def franchdailynews():
        try:
            print("Franchdailynews")
            try:
                urls = "https://frenchdailynews.com/?s=ipo"
                def get_links(urls):
                    links = [] 
                    page=requests.get(urls)
                    print(page)
                    soup=BeautifulSoup(page.content,'html')
                    divs = soup.find_all('h2',{'class':'entry-title'})
                    for i in divs:
            #         print('hi')
                        links.append(i.a["href"])
                    return links
                title=[]
                link=[]
                pub_date=[]
                scraped_date=[]
                links1 = get_links(urls)
                body = [] 
                link = []
                date = []
                from datetime import datetime
                now = datetime.now()
                current_time = now.strftime("%H:%M:%S")
                from newspaper import Article
                for ur in links1:
            #       print(ur)
                    try:
                        article = Article(ur)
                        article.download()
                        article.parse()
                        # print(article.text)
                        link.append(ur)
                        scraped_date.append(now)
                        body.append(article.text)
                        title.append(article.title)
                        date.append(article.publish_date)

                    except:

                        continue
                    time.sleep(0.5)
            except:
                    print("franchdailynew not working")
                    not_working_functions.append("French Daily news")
            df2 = pd.DataFrame({"text":body,"link":link,"publish_date":date,"scraped_date":scraped_date,"title":title})
            df = FilterFunction(df2)
            emptydataframe("French daily news " ,df)
            # df  = link_correction(df)
            return df
        except:
            df1 = pd.DataFrame(columns =['title','link','publish_date','scraped_date'])
            return df1
   
    def norway():
        try:
            print("Norway")
            try:
                urls = "https://www.thelocal.no/?s=ipo"
                def get_links(urls):

                    links = [] 
                    page=requests.get(urls)
            #       print(page)
                    soup=BeautifulSoup(page.content,'html')
                    divs = soup.find_all('div',{'class':'article-search-title'})
                    for i in divs:
                #         print('hi')
                        links.append(i.a["href"])
                    return links
                title=[]
                link=[]
                pub_date=[]
                scraped_date=[]
                links1 = get_links(urls)
                body = [] 
                link = []
                date = []
                from datetime import datetime

                now = datetime.now()

                current_time = now.strftime("%H:%M:%S")
                from newspaper import Article
                for ur in links1:
            #       print(ur)

                    try:
                        article = Article(ur)
                        article.download()
                        article.parse()
                        # print(article.text)

                        link.append(ur)
                        scraped_date.append(current_time)
                        body.append(article.text)
                        title.append(article.title)

                        date.append(article.publish_date)

                    except:

                        continue
                    time.sleep(0.5)
            except:
                print("Normay is not working")
                not_working_functions.append("Norway")
            df2 = pd.DataFrame({"text":body,"link":link,"publish_date":date,"scraped_date":scraped_date,"title":title})
            df = FilterFunction(df2)
            emptydataframe("Norway",df)
            return df
        except:
            df1 = pd.DataFrame(columns =['title','link','publish_date','scraped_date'])
            return df1
    
    def localde():
        try:
            print("localde")
            try:
                urls = "https://www.thelocal.de/?s=ipo"
                def get_links(urls):

                    links = [] 
                    page=requests.get(urls)
                #       print(page)
                    soup=BeautifulSoup(page.content,'html')
                    divs = soup.find_all('div',{'class':'article-search-title'})
                    for i in divs:
                #         print('hi')
                        links.append(i.a["href"])
                    return links
                title=[]
                link=[]
                pub_date=[]
                scraped_date=[]
                links1 = get_links(urls)
                body = [] 
                link = []
                date = []
                from datetime import datetime

                now = datetime.now()

                current_time = now.strftime("%H:%M:%S")
                from newspaper import Article
                for ur in links1:
            #       print(ur)

                    try:
                        article = Article(ur)
                        article.download()
                        article.parse()
                        # print(article.text)

                        link.append(ur)
                        scraped_date.append(now)
                        body.append(article.text)
                        title.append(article.title)

                        date.append(article.publish_date)

                    except:

                        continue
                    time.sleep(0.5)
            except:
                    print("localde not working")
                    not_working_functions.append("localde")
            df2 = pd.DataFrame({"text":body,"link":link,"publish_date":date,"scraped_date":scraped_date,"title":title})
            df = FilterFunction(df2)
            emptydataframe("localde",df)
            return df
        except:
            df1 = pd.DataFrame(columns =['title','link','publish_date','scraped_date'])
            return df1
    def chinatoday():
        try:
            print("chinatoday")
            try:
                urls = "http://www.chinatoday.com/inv/a.htm"
                def get_links(urls):

                    links = [] 
                    page=requests.get(urls, timeout=10)
                    #   print(page)
                    soup=BeautifulSoup(page.content,'html')
                    divs = soup.find_all('li')
                    for i in divs:
                    #     print('hi')
                        try:
                            links.append(i.a["href"])
                        except:
                            pass
                    return links
                title=[]
                link=[]
                pub_date=[]
                scraped_date=[]
                links1 = get_links(urls)
                body = [] 
                link = []
                date = []
                from datetime import datetime

                now = datetime.now()

                current_time = now.strftime("%H:%M:%S")
                from newspaper import Article
                for ur in links1:
            #       print(ur)

                    try:
                        article = Article(ur)
                        article.download()
                        article.parse()
                        # print(article.text)

                        link.append(ur)
                        scraped_date.append(now)
                        body.append(article.text)
                        title.append(article.title)

                        date.append(article.publish_date)

                    except:

                        continue
                    time.sleep(0.5)
            except:
                    print("chinatoday not working")
                    not_working_functions.append("Chinatoday")
            df2 = pd.DataFrame({"text":body,"link":link,"publish_date":date,"scraped_date":scraped_date,"title":title})
            df = FilterFunction(df2)
            emptydataframe("Chinatoday",df)
            # df  = link_correction(df)
            return df
        except:
            df1 = pd.DataFrame(columns =['title','link','publish_date','scraped_date'])
            return df1
    def Koreatimes():
        try :
            print("Koreatimes")
            err_logs = []
            url = "https://www.koreatimes.co.kr/www2/common/search.asp?kwd=IPO"
            domain_url = "https://www.kontan.co.id"
            title,links,text,pub_date,scraped_date = [],[],[],[],[]
            try:
                page = requests.get(url)
                soup = BeautifulSoup(page.content,"html.parser")
                # print(soup)
                
            except:
                err = "Koreatimes : err : Couldn't fetch " + url 
                err_logs.append(err)
                return 
            all_divs = soup.find_all("div",{"class":"list_article_headline HD"})
            for div in all_divs:
                links.append(div.a["href"])
            #Fetch all the necessary data 
            # print(links)
            final_links = []
            today = date.today()
            for link in links:
                try:
                    page = requests.get(link)
                    soup = BeautifulSoup(page.content,"html.parser")
                # print(soup)
                # print(link)
                except:
                    err = "Koreatimes : err : Couldn't fetch url " + link 
                    err_logs.append(err)
                    continue

                if (soup.find("div" , {"class" : "view_headline HD"}) == None):
                    continue
                title.append(soup.find("div" , {"class" : "view_headline HD"}).text)  
                # print(title)
                #Published Date
                pdate = soup.find_all("div" , {"class" :"view_date"})[0].text
                pdate = "-".join(pdate.split(":")[1].strip().split(" ")[0].split()[0].split("-")[::-1])
                pub_date.append(pdate)
                # print(pub_date)

                #Title of article 
                

                #Text of article
                div = soup.find("div" , {"class" : "view_article"})
                t = ""
                for i in div.find_all("span"):
                    t += i.text + " "
                text.append(t)
                # print(text)

                #Scrapped date 
                scraped_date.append(str(today))

                #Working links
                final_links.append(link)
            
            df = pd.DataFrame({"text":text,"link":final_links,"publish_date":pub_date,"scraped_date":scraped_date,"title":title})
            if df.empty:
                err = "Koreatimes : err: Empty dataframe"
                err_logs.append(err)
            df = df.drop_duplicates(subset=["link"])
            df = FilterFunction(df)
            emptydataframe("Koreatimes",df)
            # df  = link_correction(df)
            return df
        except :
            print("Koreatimes not working")
            not_working_functions.append('Koreatimes')

 
        
  
  # TODO: commented out for testing.  Uncomment later
  # CombineFunction()


  
    def zdnet():
        try :
            print("zdnet")
            err_logs = []
            url = "https://www.zdnet.com/search/?q=IPO"
            domain_url = "https://www.zdnet.com"
            title,links,text,pub_date,scraped_date = [],[],[],[],[]
            try:
                page = requests.get(url)
                soup = BeautifulSoup(page.content,"html.parser")
                # print(soup)
                
            except:
                err = "zdnet : err : Couldn't fetch " + url 
                err_logs.append(err)
                return 
            all_divs = soup.find_all("article",{"class":"item"})
            for div in all_divs:
                links.append(domain_url+div.a["href"])
            #Fetch all the necessary data 
            # print(links)
            final_links = []
            today = date.today()
            for link in links:
                try:
                    page = requests.get(link)
                    soup = BeautifulSoup(page.content,"html.parser")
                # print("hi")
                # print(soup)
                # print(link)
                except:
                    err = "zdnet : err : Couldn't fetch url " + link 
                    err_logs.append(err)
                    continue

                #Title of article

                title.append(soup.find("header" , {"class" : "storyHeader precap-variation article"}).h1.text)
                # print(title)
                #Published Date
                pub_date.append(soup.find("div" , {"class" :"byline-details"}).time.text)
                # print(pub_date)

                #Text of article
                div = soup.find("div" , {"class" : "storyBody"})
                t = ""
                for i in div.find_all("p"):
                    t += i.text + " "
                text.append(t)
                # print(text)

                #Scrapped date 
                scraped_date.append(str(today))

                #Working links
                final_links.append(link)
            df = pd.DataFrame({"text":text,"link":final_links,"publish_date":pub_date,"scraped_date":scraped_date,"title":title})
            if df.empty:
                err = "zdnet : err: Empty datframe"
                err_logs.append(err)
            df = df.drop_duplicates(subset=["link"])
            df = FilterFunction(df)
            emptydataframe("zdnet",df)
            # df  = link_correction(df)
            return df
        except :
            print("zdnet not working")
            not_working_functions.append('zdnet')

    def arabNews():
        try:
            print("Arabnews")
            err_logs = []
            err_index = []
            baseSearchUrl = "https://www.arabnews.com/search/site/"
            domainUrl = "https://www.arabnews.com"
            keywords = ['IPO', 'pre-IPO', 'Public', 'Initial', 'Offering', 'initial']

            # use this for faster testing
            tkeywords = ["IPO"]
            scrapedData = {}
            links = []
            titles = []
            for keyword in tkeywords:
                queryUrl = baseSearchUrl + keyword
                try:
                    headers = {
                        'User-Agent': "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 Chrome/58.0.3029.110 Safari/537.36"}
                    pageSource = requests.get(queryUrl, headers=headers)
                    parsedSource = BeautifulSoup(pageSource.content, "html.parser", from_encoding="iso-8859-1")
                except:
                    err = "arabNews: err: Failed to access search url: " + queryUrl + " and convert it to soup object"
                    err_logs.append(err)
                    continue
                # with open("response.html", "wb") as f:
                #     f.write(pageSource.content)
                # break
                for item in parsedSource.find_all("div", class_="article-item-title"):
                    requiredTag = item.find("h4").find("a")
                    currentArticleTitle = requiredTag.text
                    # print(currentArticleTitle)
                    currentArticleLink = requiredTag["href"]
                    # print(currentArticleLink)
                    if currentArticleLink[0] == "/":
                        links.append(domainUrl + currentArticleLink)
                    else:
                        links.append(currentArticleLink)
                    titles.append(currentArticleTitle)

                scrapedData["title"] = titles
                scrapedData["link"] = links
                # print(titles)
                # print(links)
                #
                # Article's date and description scraping
                ArticleDates = []
                ScrapeDates = []
                ArticleBody = []
                for link in links:
                    articleText = ""
                    try:
                        pageSource = requests.get(link, headers=headers)
                        parsedSource = BeautifulSoup(pageSource.content, "html.parser", from_encoding="iso-8859-1")
                    except:
                        err = "arabNews: err: Failed to access article link : " + link
                        ArticleDates.append("Error")
                        err_logs.append(err)
                        err_index.append(link)
                        continue
                    # with open("response.html", "wb") as f:
                    #     f.write(pageSource.content)
                    # break
                    if parsedSource.find("div", class_="entry-date"):
                        sourceDateTimeTag = parsedSource.find("div", class_="entry-date").find("time")
                    else:
                        err = "arabNews: err: Failed to retrieve date from article : " + link
                        ArticleDates.append("Error")
                        err_logs.append(err)
                        err_index.append(link)
                        continue
                    sourceDateTime = datetime.strptime(sourceDateTimeTag.text, "%B %d, %Y %H:%M").strftime("%Y-%m-%d")
                    # print(sourceDateTime)
                    ArticleDates.append(sourceDateTime)
                    ScrapeDates.append(datetime.today().strftime("%d-%m-%Y"))
                    # print(ArticleDates)
                    if parsedSource.find("div", class_="entry-content"):
                        textBodyDiv = parsedSource.find("div", class_="entry-content")
                    else:
                        err = "arabNews: err: Failed to retrieve article text: " + link
                        ArticleBody.append("Error")
                        err_logs.append(err)
                        err_index.append(link)
                        continue
                    for item in textBodyDiv.find_all("p"):
                        articleText += item.text.strip()
                    ArticleBody.append(articleText)
                scrapedData["publish_date"] = ArticleDates
                scrapedData["scraped_date"] = ScrapeDates
                scrapedData["text"] = ArticleBody
                # print(ArticleBody)

            # Clean and Normalize links
            if len(err_index) != 0:
                for e in err_index:
                    idx = scrapedData["link"].index(e)
                    scrapedData["link"].pop(idx)
                    scrapedData["title"].pop(idx)
                    scrapedData["publish_date"].pop(idx)

            # DataFrame creation
            arabNewsDF = pd.DataFrame(scrapedData)
            arabNewsDF = arabNewsDF.drop_duplicates(subset=["link"])
            if arabNewsDF.empty:
                err = "arabNews: err: Empty dataframe"
                err_logs.append(err)
            df = FilterFunction(arabNewsDF)
            emptydataframe("Arabnews",df)
            log_errors(err_logs)
            # df  = link_correction(df)
            return df
        except:
            print("Arabnews not working")
            not_working_functions.append("Arabnews")
    def chosun():
        try:
            try:
                print("Chosun")
                err_logs = []

                # baseSearchUrl = f"http://english.chosun.com/svc/list_in/search.html?query={keyword}&sort=1&catid="
                domainUrl = "https://english.chosun.com"
                keywords = ['IPO', 'pre-IPO', 'Public', 'Initial', 'Offering', 'initial']

                # use this for faster testing
                tkeywords = ["IPO"]
                scrapedData = {}
                links = []
                titles = []
                err_index = []
                for keyword in tkeywords:
                    queryUrl = f"http://english.chosun.com/svc/list_in/search.html?query={keyword}&sort=1&catid="
                    try:
                        headers = {'User-Agent': "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 Chrome/58.0.3029.110 Safari/537.36"}
                        pageSource = requests.get(queryUrl, headers=headers)
                        parsedSource = BeautifulSoup(pageSource.content, "html.parser", from_encoding="iso-8859-1")
                    except:
                        err = "chosun: err: Failed to access search url: " + queryUrl + " and convert it to soup object"
                        err_logs.append(err)
                        continue
                    # with open("response.html", "wb") as f:
                    #     f.write(pageSource.content)
                    # break
                    for item in parsedSource.find_all("dl", class_="list_item"):
                        requiredTag = item.find("a")
                        currentArticleTitle = requiredTag.text
                        currentArticleLink = requiredTag["href"]
                        if currentArticleLink[0] == "/":
                            links.append(domainUrl + currentArticleLink)
                        else:
                            links.append(currentArticleLink)
                        titles.append(currentArticleTitle)

                    scrapedData["title"] = titles
                    scrapedData["link"] = links
                # print(titles)
                # print(links)

                    # Article's date and description scraping
                    ArticleDates = []
                    ScrapeDates = []
                    ArticleBody = []
                    for link in links:
                        articleText = ""
                        try:
                            pageSource = requests.get(link, headers=headers)
                            parsedSource = BeautifulSoup(pageSource.content, "html.parser", from_encoding="iso-8859-1")
                        except:
                            err = "chosun: err: Failed to access article link : " + link
                            ArticleDates.append("Error")
                            err_index.append(links.append(link))
                            err_logs.append(err)
                            continue
                        # with open("response.html", "wb") as f:
                        #     f.write(pageSource.content)
                        # break
                        try:
                            sourceDateTimeTag = parsedSource.find("p", id="date_text")
                        except:
                            err = "chosun: err: Failed to retrieve date from article : " + link
                            ArticleDates.append("Error")
                            err_index.append(links.append(link))
                            err_logs.append(err)
                            continue
                        sourceDateTime = sourceDateTimeTag.text.strip()
                        sourceDateTime = datetime.strptime(sourceDateTime, "%B %d, %Y %H:%M").strftime("%Y-%m-%d")
                        ArticleDates.append(sourceDateTime)
                        ScrapeDates.append(datetime.today().strftime("%d-%m-%Y"))
                    # print(ArticleDates)
                        try:
                            textBodyDiv = parsedSource.find("div", class_="par")
                        except:
                            err = "chosun: err: Failed to retrieve article text: " + link
                            ArticleBody.append("Error")
                            err_index.append(links.append(link))
                            err_logs.append(err)
                            continue
                        for item in textBodyDiv.find_all("p"):
                            articleText = textBodyDiv.text.replace(item.text, "")
                        # print(articleText)
                        ArticleBody.append(articleText)
                    scrapedData["publish_date"] = ArticleDates
                    scrapedData["scraped_date"] = ScrapeDates
                    scrapedData["text"] = ArticleBody
                    # print(ArticleBody)

                # Clean data
                if len(err_index) != 0:
                    for index in err_index:
                        del scrapedData["title"][index]
                        del scrapedData["link"][index]
                        if scrapedData["publish_date"][index] == "Error":
                            del scrapedData["publish_date"][index]
                        if scrapedData["article"][index] == "Error":
                            del scrapedData["article"][index]

                # DataFrame creation
                chosunDF = pd.DataFrame(scrapedData)
                if chosunDF.empty:
                    err = "Chosun news : err : Empty dataframe"
                    err_logs.append(err)
                # log_errors(err_logs)
                df = FilterFunction(chosunDF)
                # emptydataframe("Chosun",df)
                # df  = link_correction(df)
                return df
            except:
                print("Chosun not working")
                # not_working_functions.append("Chosun")
        except:
            df1 = pd.DataFrame(columns =['title','link','publish_date','scraped_date'])
            return df1
    def Forbes():
        try :
            print("Forbes")
            err_logs = []
            url = "https://www.forbes.com/search/?q=IPO&sh=8e278c4279f4"
            domain_url = "https://www.forbes.com"
            title,links,text,pub_date,scraped_date = [],[],[],[],[]
            try:
                page = requests.get(url)
                soup = BeautifulSoup(page.content,"html.parser")
                # print(soup)
                
            except:
                err = "Forbes : err : Couldn't fetch " + url 
                err_logs.append(err)
                return 
            all_divs = soup.find_all("a",{"class":"stream-item__title"})
            for div in all_divs:
                links.append(div["href"])
            #Fetch all the necessary data 
            # print(links)
            final_links = []
            today = date.today()
            for link in links:
                try:
                    page = requests.get(link)
                    soup = BeautifulSoup(page.content,"html.parser")
                # print(soup)
                # print(link)
                except:
                    err = "Forbes : err : Couldn't fetch url " + link 
                    err_logs.append(err)
                    continue
                #Published Date

                if(soup.find("div" , {"class" :"metrics-channel light-text with-border"}) == None):
                    continue
                pub_date.append(soup.find("div" , {"class" :"metrics-channel light-text with-border"}).time.text)
            
                #Title of article 
                title.append(soup.find("h1" , {"class" : "fs-headline speakable-headline font-base font-size should-redesign"}))  
                # print(title)
            
            
                #Text of article
                div = soup.find("div" , {"class" : "article-body fs-article fs-responsive-text current-article"})
                t = ""
                for i in div.find_all("p"):
                    t += i.text + " "
                text.append(t)
                # print(text)

                #Scrapped date 
                scraped_date.append(str(today))

                #Working links
                final_links.append(link)
            # print(len(text) , len(final_links))
            df = pd.DataFrame({"text":text,"link":final_links,"publish_date":pub_date,"scraped_date":scraped_date,"title":title})
            if df.empty:
                err = "Forbes : err: Empty dataframe"
                err_logs.append(err)
            df = df.drop_duplicates(subset=["link"])
            df = FilterFunction(df)
            emptydataframe("Forbes",df)
            return df
        except :
            print("Forbes not working")
            not_working_functions.append('Forbes')
    def kedg():
        try :
            print("kedg")
            err_logs = []
            url = "https://www.kedglobal.com/newsSearch?keyword=IPO"
            domain_url = "https://www.kedglobal.com"
            title,links,text,pub_date,scraped_date = [],[],[],[],[]
            try:
                page = requests.get(url)
                soup = BeautifulSoup(page.content,"html.parser")
                # print(soup)
                
            except:
                err = "kedg : err : Couldn't fetch " + url 
                err_logs.append(err)
                return 
            all_divs = soup.find_all("div",{"class":"box"})
            for div in all_divs:
                try :
                    links.append(domain_url+div.a["href"])
                except : 
                    continue
            #Fetch all the necessary data 
            # print(links)
            final_links = []
            today = date.today()
            for link in links:
                try:
                    page = requests.get(link)
                    soup = BeautifulSoup(page.content,"html.parser")
                # print(soup)
                # print(link)
                except:
                    err = "kedg : err : Couldn't fetch url " + link 
                    err_logs.append(err)
                    continue

                #Title of article
                try:
                    if not (soup.find("p" , {"class" :"update_time"})):
                        continue
                    if not (soup.find("h1" , {"class" : "tit"})):
                        continue
                    if not (soup.find("div" , {"class" : "cont"})):
                        continue
                # print(text)

                #Scrapped date 

                #Working links
                except :
                    continue 
                pub_date.append(soup.find("p" , {"class" :"update_time"}).text)
                title.append(soup.find("h1" , {"class" : "tit"}).text)
                text.append(soup.find("div" , {"class" : "cont"}).text)
                scraped_date.append(str(today))
                final_links.append(link)
            df = pd.DataFrame({"text":text,"link":final_links,"publish_date":pub_date,"scraped_date":scraped_date,"title":title})
            if df.empty:
                err = "kedg : err: Empty datframe"
                err_logs.append(err)
            df = df.drop_duplicates(subset=["link"])
            df = FilterFunction(df)
            emptydataframe("kedg",df)
            # df  = link_correction(df)
            return df
        except :
            print("kedg not working")
            not_working_functions.append('kedg')
    def kngnet():
        try:
            try:
                print("kngnet")
                err_logs = []

                baseSearchUrl = "https://www.koreanewsgazette.com/?s="
                domainUrl = "https://www.koreanewsgazette.com"
                keywords = ['IPO', 'pre-IPO', 'Public', 'Initial', 'Offering', 'initial']

                # use this for faster testing
                tkeywords = ["IPO"]
                scrapedData = {}
                links = []
                titles = []
                err_index = []
                for keyword in tkeywords:
                    queryUrl = baseSearchUrl + keyword
                    try:
                        pageSource = requests.get(queryUrl)
                        parsedSource = BeautifulSoup(pageSource.content, "html.parser")
                    except:
                        err = "kng: err: Failed to access search url: " + queryUrl + " and convert it to soup object"
                        err_logs.append(err)
                        continue
                    for item in parsedSource.find_all("h2", class_="entry-title"):
                        # requiredTag = item.find("h2")
                        currentArticleLink = item.a["href"]
                        currentArticleTitle = item.text
                        if currentArticleLink[0] == "/":
                            links.append(domainUrl + currentArticleLink)
                        else:
                            links.append(currentArticleLink)
                        titles.append(currentArticleTitle)
                    scrapedData["title"] = titles
                    scrapedData["link"] = links
                    print(links)
                    # Article's date and description scraping
                    ArticleDates = []
                    ScrapeDates = []
                    ArticleBody = []
                    for link in links:
                      page = Article(link)
                      page.download()
                      page.parse()
                      ArticleDates.append(page.publish_date)
                      ArticleBody.append(page.text)
                      ScrapeDates.append(datetime.today().strftime("%d-%m-%Y"))
                    scrapedData["publish_date"] = ArticleDates
                    scrapedData["scraped_date"] = ScrapeDates
                    scrapedData["text"] = ArticleBody

                # Clean data
                if len(err_index) != 0:
                    for index in err_index:
                        del scrapedData["title"][index]
                        del scrapedData["link"][index]
                        if scrapedData["publish_date"][index] == "Error":
                            del scrapedData["publish_date"][index]
                        if scrapedData["article"][index] == "Error":
                            del scrapedData["article"][index]

                # DataFrame creation
                kngDF = pd.DataFrame(scrapedData)
                if kngDF.empty:
                    err = "Kngnet news : err : Empty dataframe"
                    err_logs.append(err)
                log_errors(err_logs)
                df = FilterFunction(kngDF)
                emptydataframe("Kngnet news",df)
                # df  = link_correction(df)
                return df
            except:
                print("Kngnet news is not working")
                not_working_functions.append("Kngnet news")
        except:
            df1 = pd.DataFrame(columns =['title','link','publish_date','scraped_date'])
            return df1
    def pymnts():
        try:
            try:
                print("Pymnts")
                err_logs = []

                baseSearchUrl = "https://www.pymnts.com/?s="
                domainUrl = "https://www.pymnts.com"
                keywords = ['IPO', 'pre-IPO', 'Public', 'Initial', 'Offering', 'initial']

                # use this for faster testing
                tkeywords = ["IPO"]
                scrapedData = {}
                links = []
                titles = []
                err_index = []
                for keyword in tkeywords:
                    queryUrl = baseSearchUrl + keyword
                    try:
                        headers = {'User-Agent': "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 Chrome/58.0.3029.110 Safari/537.36"}
                        pageSource = requests.get(queryUrl, headers=headers)
                        parsedSource = BeautifulSoup(pageSource.content, "html.parser")
                    except:
                        err = "pymnts: err: Failed to access search url: " + queryUrl + " and convert it to soup object"
                        err_logs.append(err)
                        continue
                    for item in parsedSource.find_all("li", class_="infinite-post"):
                        requiredTag = item.find("a")
                        currentArticleTitle = requiredTag["title"]
                        currentArticleLink = requiredTag["href"]
                        if currentArticleLink[0] == "/":
                            links.append(domainUrl + currentArticleLink)
                        else:
                            links.append(currentArticleLink)
                        titles.append(currentArticleTitle)

                    scrapedData["title"] = titles
                    scrapedData["link"] = links

                    # Article's date and description scraping
                    ArticleDates = []
                    ScrapeDates = []
                    ArticleBody = []
                    for link in links:
                        articleText = ""
                        try:
                            pageSource = requests.get(link, headers=headers)
                            parsedSource = BeautifulSoup(pageSource.content, "html.parser")
                        except:
                            err = "pymnts: err: Failed to access article link : " + link
                            ArticleDates.append("Error")
                            err_index.append(links.append(link))
                            err_logs.append(err)
                            continue
                        try:
                            sourceDateTime = parsedSource.find("time", class_="post-date updated")
                        except:
                            err = "pymnts: err: Failed to retrieve date from article : " + link
                            ArticleDates.append("Error")
                            err_index.append(links.append(link))
                            err_logs.append(err)
                            continue
                        sourceDateTime = datetime.strptime(sourceDateTime["datetime"], "%Y-%m-%d").strftime("%d-%m-%Y")
                        ArticleDates.append(sourceDateTime)
                        ScrapeDates.append(datetime.today().strftime("%d-%m-%Y"))
                        try:
                            textBodyDiv = parsedSource.find("div", id=re.compile("pymnts-content"))
                        except:
                            err = "pymnts: err: Failed to retrieve article text: " + link
                            ArticleBody.append("Error")
                            err_index.append(links.append(link))
                            err_logs.append(err)
                            continue
                        for item in textBodyDiv.find_all("p"):
                            articleText += item.text
                        ArticleBody.append(articleText)
                    scrapedData["publish_date"] = ArticleDates
                    scrapedData["scraped_date"] = ScrapeDates
                    scrapedData["text"] = ArticleBody

                # Clean data
                if len(err_index) != 0:
                    for index in err_index:
                        del scrapedData["title"][index]
                        del scrapedData["link"][index]
                        if scrapedData["publish_date"][index] == "Error":
                            del scrapedData["publish_date"][index]
                        if scrapedData["article"][index] == "Error":
                            del scrapedData["article"][index]

                # DataFrame creation
                pymntsDF = pd.DataFrame(scrapedData)
                df = FilterFunction(pymntsDF)
                emptydataframe("Pymnts",df)
                return df
            except:
                print("Pymnts not working")
                not_working_functions.append("Pymnts")
        except:
            df1 = pd.DataFrame(columns =['title','link','publish_date','scraped_date'])
            return df1
    def toi():
        try:
            try:
                print("Toi")
                err_logs = []  # Access to view error logs
                url = "https://timesofindia.indiatimes.com/topic/pre-ipo/news"
                domain_url = "https://timesofindia.indiatimes.com"

                try:
                    page = requests.get(url)
                    soup = BeautifulSoup(page.content, "html.parser")
                except:
                    err = "toi: err: Failed to access main url: " + url + " and convert it to soup object"
                    err_logs.append(err)
                    return None

                # Class names of the elements to be scraped - change if the website to be scraped changes them
                div_class = "Mc7GB"
                h1_class = "_1Y-96"
                date_div_class = "yYIu- byline"
                para_div_class = "_3YYSt"

                links = []

                for divtag in soup.find_all("div", {"class": div_class}):
                    for a in divtag.find_all("a", href=True):
                        link = a["href"]  # Gets the link

                    # Checking the link if it is a relative link
                        if link[0] == '/':
                                link = domain_url + link

                        links.append(link)

                collection = []

                for link in links:
                    try:
                        l_page = requests.get(link)
                        l_soup = BeautifulSoup(l_page.content, 'html.parser')
                    except:
                        err = "toi: err: Failed to retrieve data from link: " + link + " and convert it to soup object"
                        err_logs.append(err)
                        continue

                    data = []
                    # Scraping the heading
                    h1_ele = l_soup.find("h1", {"class": h1_class})
                    try:
                        data.append(h1_ele.text)
                    except:
                        err = "toi: err: Failed to find title in page. Link: " + link
                        err_logs.append(err)
                        continue  # drops the complete data if there is an error

                    # Adding the link to data
                    data.append(link)

                    # Scraping the published date
                    date_ele = l_soup.find("div", {"class": date_div_class})
                    try:
                        date_text = date_ele.text
                        date_text = (date_text.split('/'))[-1]
                        date_text = date_text.replace(" Updated: ", "")
                        data.append(date_text)  # The date_text could be further modified to represent a proper date format

                    except:
                        err = "toi: err: Failed to find date in page. Link: " + link
                        err_logs.append(err)
                        continue  # drops the complete data if there is an error

                    # Adding the scraped date to data
                    cur_date = str(datetime.today())
                    data.append(cur_date)

                    # Scraping the paragraph
                    para_ele = l_soup.find("div", {"class": para_div_class})
                    try:
                        data.append(para_ele.text)  # Need to make this better
                    except:
                        err = "toi: err: Failed to find paragraph in page. Link: " + link
                        err_logs.append(err)
                        continue  # drops the complete data if there is an error

                    # Adding data to the collection
                    collection.append(data)

                df = pd.DataFrame(collection, columns =['title', 'link','publish_date','scraped_date','text'])
                if df.empty:
                        err = "Arab news : err : Empty dataframe"
                        err_logs.append(err)
                log_errors(err_logs)
                df = FilterFunction(df)
                emptydataframe("Toi",df)
                # df  = link_correction(df)
                return df
            except:
                print("Toi not working ")
                not_working_functions.append("Toi")
        except:
            df1 = pd.DataFrame(columns =['title','link','publish_date','scraped_date'])
            return df1
    def wealthx():
        try:
            try:
                print("Wealthx")
                err_logs = []

                baseSearchUrl = "https://www.wealthx.com/?s="
                domainUrl = "https://www.wealthx.com"
                keywords = ['IPO', 'pre-IPO', 'Public', 'Initial', 'Offering', 'initial']

                # use this for faster testing
                tkeywords = ["IPO"]
                scrapedData = {}
                links = []
                titles = []
                err_index = []
                for keyword in tkeywords:
                    queryUrl = baseSearchUrl + keyword
                    try:
                        headers = {'User-Agent': "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 Chrome/58.0.3029.110 Safari/537.36"}
                        pageSource = requests.get(queryUrl, headers=headers)
                        parsedSource = BeautifulSoup(pageSource.content, "html.parser", from_encoding="iso-8859-1")
                    except:
                        err = "wealthx: err: Failed to access search url: " + queryUrl + " and convert it to soup object"
                        err_logs.append(err)
                        continue
                    # with open("response.html", "wb") as f:
                    #     f.write(pageSource.content)
                    # break
                    for item in parsedSource.find_all("article", class_="result"):
                        requiredTag = item.find("h2", class_="title").find("a")
                        currentArticleTitle = requiredTag.text
                        currentArticleLink = requiredTag["href"]
                        if currentArticleLink[0] == "/":
                            links.append(domainUrl + currentArticleLink)
                        else:
                            links.append(currentArticleLink)
                        titles.append(currentArticleTitle)

                    scrapedData["title"] = titles
                    scrapedData["link"] = links
                # print(titles)
                # print(links)

                    # Article's date and description scraping
                    ArticleDates = []
                    ScrapeDates = []
                    ArticleBody = []
                    for link in links:
                        articleText = ""
                        try:
                            pageSource = requests.get(link, headers=headers)
                            parsedSource = BeautifulSoup(pageSource.content, "html.parser", from_encoding="iso-8859-1")
                        except:
                            err = "wealthx: err: Failed to access article link : " + link
                            ArticleDates.append("Error")
                            err_index.append(links.append(link))
                            err_logs.append(err)
                            continue
                        # with open("response.html", "wb") as f:
                        #     f.write(pageSource.content)
                        # break
                        try:
                            sourceDateTimeTag = parsedSource.find("span", class_="meta-date date updated")
                        except:
                            err = "wealthx: err: Failed to retrieve date from article : " + link
                            ArticleDates.append("Error")
                            err_index.append(links.append(link))
                            err_logs.append(err)
                            continue
                        sourceDateTime = datetime.strptime(sourceDateTimeTag.text, "%B %d, %Y").strftime("%Y-%m-%d")
                        ArticleDates.append(sourceDateTime)
                        ScrapeDates.append(datetime.today().strftime("%d-%m-%Y"))
                    # print(ArticleDates)
                        try:
                            textBodyDiv = parsedSource.find("div", class_="content-inner")
                        except:
                            err = "wealthx: err: Failed to retrieve article text: " + link
                            ArticleBody.append("Error")
                            err_index.append(links.append(link))
                            err_logs.append(err)
                            continue
                        for item in textBodyDiv.find_all("p"):
                            articleText += item.text.strip()
                        # print(articleText)
                        ArticleBody.append(articleText)
                    scrapedData["publish_date"] = ArticleDates
                    scrapedData["scraped_date"] = ScrapeDates
                    scrapedData["text"] = ArticleBody
                    # print(ArticleBody)

                # Clean data
                if len(err_index) != 0:
                    for index in err_index:
                        del scrapedData["title"][index]
                        del scrapedData["link"][index]
                        if scrapedData["publish_date"][index] == "Error":
                            del scrapedData["publish_date"][index]
                        if scrapedData["article"][index] == "Error":
                            del scrapedData["article"][index]

                # DataFrame creation
                wealthxDF = pd.DataFrame(scrapedData)
                if wealthxDF.empty:
                    err = "Wealthx news : err : Empty dataframe"
                    err_logs.append(err)
                # log_errors(err_logs)
                df = FilterFunction(wealthxDF)
                emptydataframe("WealthX",df)
                # df  = link_correction(df)
                return df
            except:
                print("Wealth x not working")
                not_working_functions.append("Wealth x")
        except:
            df1 = pd.DataFrame(columns =['title','link','publish_date','scraped_date'])
            return df1
    def AFR():
        try :
            print("AFR")
            err_logs = []
            url = "https://www.afr.com/search?text=ipo"
            domain_url = "https://www.afr.com"
            title,links,text,pub_date,scraped_date = [],[],[],[],[]
            try:
                page = requests.get(url)
                soup = BeautifulSoup(page.content,"html.parser")
                # print(soup)
                
            except:
                err = "AFR : err : Couldn't fetch " + url 
                err_logs.append(err)
                return 
            all_divs = soup.find_all("a",{"class":"_20-Rx"})
            for div in all_divs:
                links.append(domain_url+div["href"])
            #Fetch all the necessary data 
            # print(links)
            final_links = []
            today = date.today()
            for link in links:
                try:
                    page = requests.get(link)
                    soup = BeautifulSoup(page.content,"html.parser")
                # print(soup)
                # print(link)
                except:
                    err = "AFR : err : Couldn't fetch url " + link 
                    err_logs.append(err)
                    continue

                #Title of article
                # if(soup.find("h1" , {"class" : "primary-font__PrimaryFontStyles-o56yd5-0 dEdODy headline"}) == None):
                #   continue
                if(soup.find("h1" , {"class" : "_3lFzE"})== None):
                    continue
                title.append(soup.find("h1" , {"class" : "_3lFzE"}).text)
                # print(title)
                #Published Date
                pub_date.append(soup.find("div" , {"class" :"_2cdD4"}).time.text)
                # print(pub_date)

                #Text of article
                div = soup.find("div" , {"class" : "tl7wu"})
                t = ""
                for i in div.find_all("p"):
                    t += i.text + " "
                text.append(t)
                # # print(text)

                #Scrapped date 
                scraped_date.append(str(today))

                #Working links
                final_links.append(link)
            df = pd.DataFrame({"text":text,"link":final_links,"publish_date":pub_date,"scraped_date":scraped_date,"title":title})
            if df.empty:
                err = "AFR : err: Empty dataframe"
                err_logs.append(err)
            df = df.drop_duplicates(subset=["link"])
            df = FilterFunction(df)
            emptydataframe("AFR",df)
            # df  = link_correction(df)
            return df
        except :
            print("AFR not working")
            not_working_functions.append('AFR')
    def indonesia():

        try :
            print("Antara")
            err_logs = []
            url = "https://en.antaranews.com/search?q=ipo"
            domain_url = "https://en.antaranews.com"
            title,links,text,pub_date,scraped_date = [],[],[],[],[]
            try:
                page = requests.get(url)
                soup = BeautifulSoup(page.content,"html.parser")
                # print(soup)
                
            except:
                err = "Indonesia : err : Couldn't fetch " + url 
                err_logs.append(err)
                return 
            all_divs = soup.find_all("article",{"class":"simple-post simple-big clearfix"})
            for div in all_divs:
                links.append(div.a["href"])
            #Fetch all the necessary data 
            # print(links)
            final_links = []
            today = date.today()
            for link in links:
                try:
                    page = requests.get(link)
                    soup = BeautifulSoup(page.content,"html.parser")
                # print(soup)
                # print(link)
                except:
                    err = "Indonesia : err : Couldn't fetch url " + link 
                    err_logs.append(err)
                    continue
                #Published Date

                # if(soup.find("div" , {"class" :"metrics-channel light-text with-border"}) == None):
                #   continue
                pub_date.append(soup.find("i" , {"class" :"fa fa-clock-o"}).text)
            
                #Title of article 
                title.append(soup.find("h1" , {"class" : "post-title"}).text)  
                # print(title)
            
            
                #Text of article
                div = soup.find("div" , {"class" : "post-content clearfix"})
                t = ""
                for i in div.find_all("div"):
                # if(i != None):
                    t += i.text + " "
                text.append(t)
                
                # print(text)

                #Scrapped date 
                scraped_date.append(str(today))

                #Working links
                final_links.append(link)
            # print(len(text) , len(final_links))
            df = pd.DataFrame({"text":text,"link":final_links,"publish_date":pub_date,"scraped_date":scraped_date,"title":title})
            if df.empty:
                err = "Indonesia : err: Empty dataframe"
                err_logs.append(err)
            df = df.drop_duplicates(subset=["link"])
            df = FilterFunction(df)
            emptydataframe("indonesia",df)
            # df  = link_correction(df)
            return df
        except :
            print("Indonesia not working")
            not_working_functions.append('Indonesia')
            
    def asiainsurancereview():
        try:
            try:
                print("Asia Insurance")
                err_logs = []  # Access to view error logs
                url = "https://www.asiainsurancereview.com/Search?search_key=IPO"
                domain_url = "https://www.asiainsurancereview.com"

                try:
                    page = requests.get(url)
                    soup = BeautifulSoup(page.content, "html.parser")
                except:
                    err = "asiainsurancereview: err: Failed to access main url: " + url + " and convert it to soup object"
                    err_logs.append(err)
                    return None

                # Class names of the elements to be scraped - change if the website to be scraped changes them
                div_class = "items"
                h1_class = "main-title"
                date_div_class = "title-right"
                para_div_class = "article-wrap"

                links = []

                for divtag in soup.find_all("li", {"class": div_class}):
                    for a in divtag.find_all("a", href=True):
                        link = a["href"]  # Gets the link

                        # Checking the link if it is a relative link
                        if link[0] == '/':
                            link = domain_url + link

                        links.append(link)

                collection = []

                for link in links:
                    try:
                        l_page = requests.get(link)
                        l_soup = BeautifulSoup(l_page.content, 'html.parser')
                    except:
                        err = "asiainsurancereview: err: Failed to retrieve data from link: " + link + " and convert it to soup object"
                        err_logs.append(err)
                        continue

                    data = []
                    # Scraping the heading
                    h1_ele = l_soup.find("h1", {"class": h1_class})
                    try:
                        data.append(h1_ele.text)
                    except:
                        err = "asiainsurancereview: err: Failed to find title in page. Link: " + link
                        err_logs.append(err)
                        continue  # drops the complete data if there is an error

                    # Adding the link to data
                    data.append(link)

                    # Scraping the published date
                    date_ele = l_soup.find("span", {"class": date_div_class})
                    try:
                        date_text = date_ele.text
                        date_text = (date_text.split('/'))[-1]
                        date_text = date_text.replace(" Updated: ", "")
                        data.append(date_text)  # The date_text could be further modified to represent a proper date format

                    except:
                        err = "asiainsurancereview: err: Failed to find date in page. Link: " + link
                        err_logs.append(err)
                        continue  # drops the complete data if there is an error

                    # Adding the scraped date to data
                    cur_date = str(datetime.today())
                    data.append(cur_date)

                    # Scraping the paragraph
                    para_ele = l_soup.find("div", {"class": para_div_class})
                    try:
                        data.append(para_ele.text)  # Need to make this better
                    except:
                        err = "asiainsurancereview: err: Failed to find paragraph in page. Link: " + link
                        err_logs.append(err)
                        continue  # drops the complete data if there is an error

                    # Adding data to the collection
                    collection.append(data)

                df = pd.DataFrame(collection, columns =['title', 'link','publish_date','scraped_date','text'])
                if df.empty:
                    print("Antara indonesia review : err : Empty dataframe")
                #     err_logs.append(err)
                # log_errors(err_logs)
                df = FilterFunction(df)
                # df  = link_correction(df)
                return df
            except:
                print("Asia insurance not working")
                not_working_functions.append("Asia Insurance")
        except:
            df1 = pd.DataFrame(columns =['title','link','publish_date','scraped_date'])
            return df1
    def economic_times():
        try :
            print("economic_times")
            err_logs = []
            url = "https://economictimes.indiatimes.com/markets/ipo"
            domain_url = "https://economictimes.indiatimes.com"
            title,links,text,pub_date,scraped_date = [],[],[],[],[]
            try:
                page = requests.get(url)
                soup = BeautifulSoup(page.content,"html.parser")
                # print(soup)
                
            except:
                err = "economic_times : err : Couldn't fetch " + url 
                err_logs.append(err)
                return 
            all_divs = soup.find_all("a",{"class":"wrapLines l1"})
            for div in all_divs:
                links.append(domain_url+div["href"])
            #Fetch all the necessary data 
            print(links)
            final_links = []
            today = date.today()
            for link in links:
                try:
                    page = requests.get(link)
                    soup = BeautifulSoup(page.content,"html.parser")
                # print(soup)
                # print(link)
                except:
                    err = "economic_times : err : Couldn't fetch url " + link 
                    err_logs.append(err)
                    continue

                #Title of article

                title.append(soup.find("h1" , {"class" : "artTitle font_faus"}).text)
                # print(title)
                #Published Date
                pub_date.append(soup.find("time" , {"class" :"jsdtTime"}).text)
                # print(pub_date)

                #Text of article
                # div = soup.find("div" , {"class" : "storyBody"})
                # t = ""
                # for i in div.find_all("p"):
                #   t += i.text + " "
                # text.append(t)
                text.append(soup.find("div" , {"class" :"pageContent flt"}).text)
                # print(text)

                #Scrapped date 
                scraped_date.append(str(today))

                #Working links
                final_links.append(link)
            df = pd.DataFrame({"text":text,"link":final_links,"publish_date":pub_date,"scraped_date":scraped_date,"title":title})
            if df.empty:
                err = "economic_times : err: Empty datframe"
                err_logs.append(err)
            df = df.drop_duplicates(subset=["link"])
            df = FilterFunction(df)
            emptydataframe("economic_times",df)
            # df  = link_correction(df)
            return df
        except :
            print("economic_times not working")
            not_working_functions.append('economic_times')
    def prnewswire():
        try:
            try:
                print("prnnewswire")
                err_logs = []
                url = "https://www.prnewswire.com/search/news/?keyword=pre%20ipo"
                domain_url = "https://www.prnewswire.com/"

                page = requests.get(url)
                soup = BeautifulSoup(page.content, "html.parser")

                # Class names of the elements to be scraped
                div_class = "card"
                #h1_class = "_1Y-96"
                h1_div_class = "col-xs-12"
                date_div_class = "mb-no"
                para_div_class = "col-sm-10"

                links = []

                for divtag in soup.find_all("div", {"class": div_class}):
                    for a in divtag.find_all("a", href=True):
                        link = a["href"]  # Gets the link

                        # Checking the link if it is a relative link
                        if link[0] == '/':
                            link = domain_url + link

                        link_start = "https://www.prnewswire.com//news-releases"
                        if link.startswith(link_start):
                            links.append(link)
                # Remove duplicates
                links = list(set(links))

                collection = []

                for link in links:
                    try:
                        l_page = requests.get(link)
                        l_soup = BeautifulSoup(l_page.content, 'html.parser')
                    except:
                        err = "prnewswire: err: Failed to retrieve data from link: " + link + " and convert it to soup object"
                        err_logs.append(err)
                        continue

                    data = []
                # Scraping the heading
                #h1_ele = l_soup.find("h1", {"class": h1_class})
                
                    try:
                        div_ele = l_soup.find("div", {"class": h1_div_class})
                        h1_ele = div_ele.find("h1")
                        data.append(h1_ele.text)
                    except:
                        err = "prnewswire: err: Failed to find title in page. Link: " + link
                        err_logs.append(err)
                        continue  # drops the complete data if there is an error


                # Adding the link to data
                    data.append(link)

                # Scraping the published date
                    date_ele = l_soup.find("p", {"class": date_div_class})
                    try:
                        date_text = date_ele.text
                        date_text = (date_text.split('/'))[-1]
                        date_text = date_text.replace(" Updated: ", "")
                        data.append(date_text)  # The date_text could be further modified to represent a proper date format
                    except:
                        err = "prnewswire: err: Failed to find date in page. Link: " + link
                        err_logs.append(err)
                        continue  # drops the complete data if there is an error
                
                # Adding the scraped date to data
                    cur_date = str(datetime.today())
                    data.append(cur_date)
                

                # Scraping the paragraph
                    para_ele = (l_soup.findAll("div", {"class": para_div_class}))[-1]
                    try:
                        data.append(para_ele.text)  # Need to make this better
                    except:
                        err = "prnewswire: err: Failed to find paragraph in page. Link: " + link
                        err_logs.append(err)
                        continue  # drops the complete data if there is an error
                # Adding data to a collection
                    collection.append(data)

                df = pd.DataFrame(collection, columns =['title', 'link','publish_date','scraped_date','text'])
                if df.empty:
                    err = "prnewswire: err: Empty dataframe"
                    err_logs.append(err)
                df = FilterFunction(df)
                emptydataframe("Prnewswire",df)
                # df  = link_correction(df)
                return df
            except:
                print("Prnewswire not working")
                not_working_functions.append("Prnewswire")
        except:
            df1 = pd.DataFrame(columns =['title','link','publish_date','scraped_date'])
            return df1
    def arabfinance():
        try:
            try:
                print("Arab Finanace")
                err_logs = []
                url = "https://www.albawaba.com/search?keyword=IPO&sort_by=created"
                domain_url = "https://www.albawaba.com"
                title,links,text,pub_date,scraped_date = [],[],[],[],[]
                try:
                    page = requests.get(url)
                    soup = BeautifulSoup(page.content,"html.parser")
                except:
                    err = "Arab Finance : err : Couldn't fetch " + url 
                    err_logs.append(err)
                    return 
                # Fetching all links 
                all_divs = soup.find_all("div",{"class":"field-content title"})
                for div in all_divs:
                    links.append(domain_url + div.a["href"])
                #Fetch all the necessary data 
                final_links = []
                today = date.today()
                for link in links:
                    try:
                        page = requests.get(link)
                        soup = BeautifulSoup(page.content,"html.parser")
                    except:
                        err = "Arab Finance : err : Couldn't fetch url " + link 
                        err_logs.append(err)
                        continue
                    #get date of the article 
                    pub_date.append("Date")
                    #get title of the article 
                    title.append(soup.find("h1",{"class":"page-header"}).text)
                    #get text of the article 
                    # print(soup.find("div",{"class":"field field--name-body field--type-text-with-summary field--label-hidden field--item"}).text)
                    text.append(soup.find("div",{"class":"field field--name-body field--type-text-with-summary field--label-hidden field--item"}).text)
                    #get today's date i.r scrape date 
                    scraped_date.append(str(today))
                    # get links that works 
                    final_links.append(link)
                df = pd.DataFrame({"text":text,"link":final_links,"publish_date":pub_date,"scraped_date":scraped_date,"title":title})
                if df.empty:
                    err = "Arab Finance : err: Empty dataframe"
                    err_logs.append(err)
                df = df.drop_duplicates(subset=["link"])
                log_errors(err_logs)
                df = FilterFunction(df)
                emptydataframe("Arab finance",df)
                # df  = link_correction(df)
                return df
            except:
                print("Arab Finanace is not working")
                not_working_functions.append("Arab Finance")
        except:
            df1 = pd.DataFrame(columns =['title','link','publish_date','scraped_date'])
            return df1

    def star():
        try:
            print("Star")
            err_logs = []
            url = "https://www.thestar.com.my/news/latest?tag=Business"
            domain_url = "https://mb.com.ph"
            try:
                page = requests.get(url)
    #             print(page.content)
                soup = BeautifulSoup(page.content,"html.parser")
                # print(soup)
            except:
                err = "The star : err : Couldn't fetch the url "+ url
                err_logs.append(err)
                return
            pub_date,scraped_date,links,final_links,title,text = [],[],[],[],[],[]
            #get all links 
            for h4 in soup.find_all("h2",{"class":"f18"}):
                links.append(h4.a["href"])
            # Fetch all the required data for the dataframe 
            today = date.today()
            for link in links:
                try:
                    page = requests.get(link)
                    soup = BeautifulSoup(page.content,"html.parser")
                except:
                    err = "The star : err : Couldn't fetch the url "+ link
                    err_logs.append(err)
                    continue
                # Fetch all other data 
                title.append(soup.find("div",{"class":"headline story-pg"}).h1.text)
                pub_date.append(soup.find("p",{"class":"date"}).text)
                text.append(soup.find("div",{"class":"story bot-15 relative"}).text)
                scraped_date.append(today)
                final_links.append(link)
            df = pd.DataFrame({"text":text,"link":final_links,"publish_date":pub_date,"scraped_date":scraped_date,"title":title})
            if df.empty:
                err = "the star: err: Empty dataframe"
                err_logs.append(err)
            df = df.drop_duplicates(subset=["link"])
            log_errors(err_logs)
            df = FilterFunction(df)
            emptydataframe("Star",df)
            return df
        except:
            print("Star is not working")
            not_working_functions.append("Star")
    
    def interfax():
        try:
            err_logs = []  # Access to view error logs
            url = "https://en.interfax.com.ua/news/search.html?q=ipo"
            domain_url = "https://en.interfax.com.ua/"

            try:
                page = requests.get(url)
                soup = BeautifulSoup(page.content, "html.parser")
            except:
                err = "toi: err: Failed to access main url: " + url + " and convert it to soup object"
                err_logs.append(err)
                return None

            # Class names of the elements to be scraped - change if the website to be scraped changes them
            div_class = "col-57"
            h1_class = "article-content-title"
            date_div_class = "col-18 article-time"
            para_div_class = "article-content"

            links = []

            for divtag in soup.find_all("div", {"class": div_class}):
                for a in divtag.find_all("a", href=True):
                    link = a["href"]  # Gets the link

                    # Checking the link if it is a relative link
                    if link[0] == '/':
                        link = domain_url + link

                    links.append(link)

            collection = []

            for link in links:
                try:
                    l_page = requests.get(link)
                    l_soup = BeautifulSoup(l_page.content, 'html.parser')
                except:
                    err = "err: Failed to retrieve data from link: " + link + " and convert it to soup object"
                    err_logs.append(err)
                    continue

                data = []
                # Scraping the heading
                h1_ele = l_soup.find("h1", {"class": h1_class})
                try:
                    data.append(h1_ele.text)
                except:
                    err = "err: Failed to find title in page. Link: " + link
                    err_logs.append(err)
                    continue  # drops the complete data if there is an error

                # Adding the link to data
                data.append(link)

                # Scraping the published date
                date_ele = l_soup.find("div", {"class": date_div_class})
                try:
                    date_text = date_ele.text
                    date_text = (date_text.split('/'))[-1]
                    date_text = date_text.replace(" Updated: ", "")
                    data.append(date_text)  # The date_text could be further modified to represent a proper date format

                except:
                    err = "err: Failed to find date in page. Link: " + link
                    err_logs.append(err)
                    continue  # drops the complete data if there is an error

                # Adding the scraped date to data
                cur_date = str(datetime.today())
                data.append(cur_date)

                # Scraping the paragraph
                para_ele = l_soup.find("div", {"class": para_div_class})
                try:
                    data.append(para_ele.text)  # Need to make this better
                except:
                    err = "toi: err: Failed to find paragraph in page. Link: " + link
                    err_logs.append(err)
                    continue  # drops the complete data if there is an error

                # Adding data to the collection
                collection.append(data)

            df = pd.DataFrame(collection, columns =['title', 'link','publish_date','scraped_date','text'])
            if df.empty:
                err = "err: Empty dataframe"
                err_logs.append(err)
            df = FilterFunction(df)
            emptydataframe("Interfax Ukraine",df)
            # df  = link_correction(df)
            return df
        except:
            print("Interfax_Ukraine not working")
            not_working_functions.append("Interfax_ukraine")
    def vccircle():
        try :
            print("Vccircle")
            err_logs = []
            url = "https://www.vccircle.com/search/result/ipo/all"
            domain_url = "https://www.vccircle.com"
            title,links,text,pub_date,scraped_date = [],[],[],[],[]
            try:
                page = requests.get(url)
                soup = BeautifulSoup(page.content,"html.parser")
                # print(soup)
                
            except:
                err = "Vccircle : err : Couldn't fetch " + url 
                err_logs.append(err)
                return 
            all_divs = soup.find_all("div",{"class":"title"})
            for div in all_divs:
                links.append(div.a["href"])
            #Fetch all the necessary data 
            # print(links)
            final_links = []
            today = date.today()
            for link in links:
                try:
                    page = requests.get(link)
                    soup = BeautifulSoup(page.content,"html.parser")
                # print(soup)
                # print(link)
                except:
                    err = "Vccircle : err : Couldn't fetch url " + link 
                    err_logs.append(err)
                    continue
                #Published Date
                pub_date.append(soup.find("span" , {"class" :"publish-time"})["content"])
                # print(pub_date)

                #Title of article 
                title.append(soup.find("div" , {"class" : "premium-txt-container"}).text)  
                # print(title)

                #Text of article
                div = soup.find("div" , {"class" : "col-sm-9 mid-content"})
                t = ""
                for i in div.find_all("p"):
                    t += i.text + " "
                text.append(t)
                # print(text)

                #Scrapped date 
                scraped_date.append(str(today))

                #Working links
                final_links.append(link)
            df = pd.DataFrame({"text":text,"link":final_links,"publish_date":pub_date,"scraped_date":scraped_date,"title":title})
            if df.empty:
                err = "Vccircle : err: Empty dataframe"
                err_logs.append(err)
            df = df.drop_duplicates(subset=["link"])
            df = FilterFunction(df)
            emptydataframe("Vccircle",df)
            # df  = link_correction(df)
            return df
        except :
            print("Vccircle not working")
            not_working_functions.append('Vccircle')

    def allafrica():
        try:
            try:
                print("Allafrica")
                err_logs = []
                url = "https://allafrica.com/search/?search_string=pre+ipo&search_submit=Search"
                domain_url = "https://allafrica.com/"

                page = requests.get(url)
                soup = BeautifulSoup(page.content, "html.parser")
                #soup  # Debugging - if soup is working correctly

                # Class names of the elements to be scraped
                div_class = "search-results"  # Class name of div containing the a tag
                #h1_class = "_1Y-96"
                #h1_div_class = "col-xs-12"
                h2_class = "headline"
                date_div_class = "publication-date"
                para_div_class = "story-body"

                links = []

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
                #links # Debugging - if link array is generated

                collection = []
                scrapper_name = "allafrica"

                for link in links:
                    try:
                        l_page = requests.get(link)
                        l_soup = BeautifulSoup(l_page.content, 'html.parser')
                    except:
                        err = scrapper_name + ": err: Failed to retrieve data from link: " + link + " and convert it to soup object"
                        err_logs.append(err)
                        continue

                    data = []
                    # Scraping the heading
                    #h1_ele = l_soup.find("h1", {"class": h1_class})
                    
                    try:
                        h2_ele = l_soup.find("h2", {"class": h2_class})
                        data.append(h2_ele.text)
                    except:
                        err = scrapper_name + ": err: Failed to find title in page. Link: " + link
                        err_logs.append(err)
                        continue  # drops the complete data if there is an error


                    # Adding the link to data
                    data.append(link)

                    # Scraping the published date
                    date_ele = l_soup.find("div", {"class": date_div_class})
                    try:
                        date_text = date_ele.text
                        #date_text = (date_text.split('/'))[-1]
                        #date_text = date_text.replace(" Updated: ", "")
                        data.append(date_text)  # The date_text could be further modified to represent a proper date format
                    except:
                        err = scrapper_name + ": err: Failed to find date in page. Link: " + link
                        err_logs.append(err)
                        continue  # drops the complete data if there is an error
                    
                    # Adding the scraped date to data
                    cur_date = str(datetime.today())
                    data.append(cur_date)
                    

                    # Scraping the paragraph
                    para_ele = (l_soup.findAll("div", {"class": para_div_class}))[-1]
                    try:
                        data.append(para_ele.text)  # Need to make this better
                    except:
                        err = scrapper_name + ": err: Failed to find paragraph in page. Link: " + link
                        err_logs.append(err)
                        continue  # drops the complete data if there is an error
                    # Adding data to a collection
                    collection.append(data)

                df = pd.DataFrame(collection, columns =['title', 'link','publish_date','scraped_date','text'])
                if df.empty:
                    err = scrapper_name + ": err: Empty dataframe"
                    err_logs.append(err)
                df = FilterFunction(df)
                # emptydataframe("Allafrica",df)
                # df  = link_correction(df)

                return df
            except:
              # pass
                not_working_functions.append("Allafrica")
        except:
            df1 = pd.DataFrame(columns =['title','link','publish_date','scraped_date'])
            return df1
    def zawya():
        try :
            print("zawya")
            err_logs = []
            url = "https://www.zawya.com/en/search?q=pre+ipo"
            domain_url = "https://www.zawya.com"
            title,links,text,pub_date,scraped_date = [],[],[],[],[]
            try:
                page = requests.get(url)
                soup = BeautifulSoup(page.content,"html.parser")
                # print(soup)
                
            except:
                err = "zawya : err : Couldn't fetch " + url 
                err_logs.append(err)
                return 
            all_divs = soup.find_all("h2",{"class":"teaser-title"})
            for div in all_divs:
                links.append(div.a["href"])
            #Fetch all the necessary data 
            print(links)
            final_links = []
            today = date.today()
            for link in links:
                try:
                    page = requests.get(link)
                    soup = BeautifulSoup(page.content,"html.parser")
                # print("hi")
                # print(soup)
                # print(link)
                except:
                    err = "zawya : err : Couldn't fetch url " + link 
                    err_logs.append(err)
                    continue

                #Title of article

                title.append(soup.find("h1" , {"class" : "article-title"}).text)
                # print(title)
                #Published Date
                pub_date.append(soup.find("div" , {"class" :"article-date"}).text)
                # print(pub_date)

                #Text of article
                div = soup.find("div" , {"class" : "article-body"})
                t = ""
                for i in div.find_all("p"):
                    t += i.text + " "
                text.append(t)
                # print(text)

                #Scrapped date 
                scraped_date.append(str(today))

                #Working links
                final_links.append(link)
            df = pd.DataFrame({"text":text,"link":final_links,"publish_date":scraped_date,"scraped_date":scraped_date,"title":title})
            if df.empty:
                err = "zawya : err: Empty datzawyaame"
                err_logs.append(err)
            df = df.drop_duplicates(subset=["link"])
            df = FilterFunction(df)
            emptydataframe("zawya",df)
            # df  = link_correction(df)
            return df
        except :
            print("zawya not working")
            not_working_functions.append('zawya')
    def phnompenhpost():
        try:
            try:
                print("Phnompenhpost")
                err_logs = []

                baseSearchUrl = "https://www.phnompenhpost.com/search/node/"
                domainUrl = "https://www.phnompenhpost.com"
                keywords = ['IPO', 'pre-IPO', 'Public', 'Initial', 'Offering', 'initial']

                # use this for faster testing
                tkeywords = ["IPO"]
                scrapedData = {}
                links = []
                titles = []
                err_index = []
                ArticleDates = []
                ScrapeDates = []
                for keyword in tkeywords:
                    queryUrl = baseSearchUrl + keyword
                    try:
                        session = HTMLSession()
                        resp = session.post(queryUrl)
                        resp.html.render()
                        pageSource = resp.html.html
                        parsedSource = BeautifulSoup(pageSource, "html.parser")
                    except:
                        err = "phnompenhpost: err: Failed to access search url: " + queryUrl + " and convert it to soup object"
                        err_logs.append(err)
                        continue
                    # with open("response.html", "w") as f:
                    #     f.write(pageSource)
                    # break
                    for item in parsedSource.find_all("li", class_="search-result"):
                        requiredTag = item.find("h3", class_="title")
                        currentArticleTitle = str(requiredTag.text).strip()
                        # print(currentArticleTitle)
                        currentArticleLink = requiredTag.find("a")["href"]
                        # print(currentArticleLink)
                        if currentArticleLink[0] == "/":
                            links.append(domainUrl + currentArticleLink)
                        else:
                            links.append(currentArticleLink)
                        titles.append(currentArticleTitle)
                        currentArticleDateText = str(item.find("div", class_="posted-date").find("span").text).split("by")[0].strip()
                        try:
                            currentArticleDate = datetime.strptime(currentArticleDateText,
                                                                "%d %b %Y").strftime("%d-%m-%Y")
                        except:
                            err = "phnompenhpost: err: Failed to retrieve date from article : " + currentArticleLink
                            ArticleDates.append("Error")
                            err_index.append(links.append(currentArticleLink))
                            err_logs.append(err)
                            continue
                        ArticleDates.append(currentArticleDate)
                        ScrapeDates.append(datetime.today().strftime("%d-%m-%Y"))
                    scrapedData["title"] = titles
                    scrapedData["link"] = links
                    scrapedData["publish_date"] = ArticleDates
                    scrapedData["scraped_date"] = ScrapeDates
                    # print(titles)
                    # print(links)
                    # print(ArticleDates)

                    # Article's date and description scraping
                    ArticleBody = []
                    for link in links:
                        articleText = ""
                        try:
                            # session = HTMLSession()
                            # resp = session.get(link)
                            # resp.html.render()
                            # pageSource = resp.html.html
                            # parsedSource = BeautifulSoup(pageSource, "html.parser")
                            headers = {
                                'User-Agent': "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 Chrome/58.0.3029.110 Safari/537.36"}
                            pageSource = requests.get(link, headers=headers)
                            parsedSource = BeautifulSoup(pageSource.content, "html.parser", from_encoding="iso-8859-1")
                        except:
                            err = "phnompenhpost: err: Failed to access article link : " + link
                            ArticleDates.append("Error")
                            err_index.append(links.append(link))
                            err_logs.append(err)
                            continue
                        # with open("response.html", "wb") as f:
                        #     f.write(pageSource.content)
                        # break
                        divTag = parsedSource.find("div", id="ArticleBody")
                        for item in divTag.find_all("p"):
                            articleText += item.text
                        ArticleBody.append(articleText)
                    scrapedData["text"] = ArticleBody
                    # print(ArticleBody)

                # DataFrame creation
                phnompenhpostDF = pd.DataFrame(scrapedData)
                if phnompenhpostDF.empty:
                    err = "phnompenhpost: err: Empty dataframe"
                    err_logs.append(err)
                df = FilterFunction(phnompenhpostDF)
                emptydataframe(df)
                return df
            except:
                not_working_functions.append("Phnompenhpost")
                print("Phnompenhpost not working")
        except:
            df1 = pd.DataFrame(columns =['title','link','publish_date','scraped_date'])
            return df1
    def scmp():
        try:
            try:
                print("Scmp")
                err_logs = []

                baseSearchUrl = "https://www.scmp.com/search/"
                domainUrl = "https://www.scmp.com"
                keywords = ['IPO', 'pre-IPO', 'Public', 'Initial', 'Offering', 'initial']

                # use this for faster testing
                tkeywords = ["IPO"]
                scrapedData = {}
                links = []
                titles = []
                err_index = []
                ArticleDates = []
                ScrapeDates = []
                for keyword in tkeywords:
                    queryUrl = baseSearchUrl + keyword
                    try:
                        session = HTMLSession()
                        resp = session.get(queryUrl)
                        resp.html.render()
                        pageSource = resp.html.html
                        parsedSource = BeautifulSoup(pageSource, "html.parser")
                    except:
                        err = "scmp: err: Failed to access search url: " + queryUrl + " and convert it to soup object"
                        err_logs.append(err)
                        continue
                    # with open("response.html", "wb") as f:
                    #     f.write(pageSource.content)
                    # break
                    for item in parsedSource.find_all("li", class_="search-results__item item"):
                        requiredTag = item.find("span", class_="content-link__title")
                        currentArticleTitle = requiredTag.text
                        # print(currentArticleTitle)
                        currentArticleLink = item.find("a", class_="content__content-link content-link")["href"]
                        # print(currentArticleLink)
                        if currentArticleLink[0] == "/":
                            links.append(domainUrl + currentArticleLink)
                        else:
                            links.append(currentArticleLink)
                        titles.append(currentArticleTitle)
                        try:
                            currentArticleDate = datetime.strptime(item.find("div", class_="wrapper__published-date").text,
                                                                "%d %b %Y - %H:%M%p").strftime("%d-%m-%Y")
                        except:
                            err = "scmp: err: Failed to retrieve date from article : " + currentArticleLink
                            ArticleDates.append("Error")
                            err_index.append(links.append(currentArticleLink))
                            err_logs.append(err)
                            continue
                        ArticleDates.append(currentArticleDate)
                        ScrapeDates.append(datetime.today().strftime("%d-%m-%Y"))
                    scrapedData["title"] = titles
                    scrapedData["link"] = links
                    scrapedData["publish_date"] = ArticleDates
                    scrapedData["scraped_date"] = ScrapeDates
                    # print(titles)
                    # print(links)
                    # print(ArticleDates)

                    # Article's date and description scraping
                    ArticleBody = []
                    for link in links:
                        articleText = ""
                        try:
                            # session = HTMLSession()
                            # resp = session.get(link)
                            # resp.html.render()
                            # pageSource = resp.html.html
                            # parsedSource = BeautifulSoup(pageSource, "html.parser")
                            headers = {
                                'User-Agent': "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 Chrome/58.0.3029.110 Safari/537.36"}
                            pageSource = requests.get(link, headers=headers)
                            parsedSource = BeautifulSoup(pageSource.content, "html.parser", from_encoding="iso-8859-1")
                        except:
                            err = "scmp: err: Failed to access article link : " + link
                            ArticleDates.append("Error")
                            err_index.append(links.append(link))
                            err_logs.append(err)
                            continue
                        # with open("response.html", "w") as f:
                        #     f.write(pageSource)
                        # break
                        for item in parsedSource.find_all("script", type="application/ld+json"):
                            tempDict = json.loads(item.text)
                            try:
                                ArticleText = tempDict["articleBody"]
                            except:
                                continue
                        ArticleBody.append(articleText)
                    scrapedData["text"] = ArticleBody
                    # print(ArticleBody)

                # DataFrame creation
                scmpDF = pd.DataFrame(scrapedData)
                if scmpDF.empty:
                    err = "scmp: err: Empty dataframe"
                    err_logs.append(err)
                df =FilterFunction(scmpDF)
                emptydataframe("Scmp",df)
                return scmpDF
            except:
                print("Scmp not working")
                not_working_functions.append("Scmp")
        except:
            df1 = pd.DataFrame(columns =['title','link','publish_date','scraped_date'])
            return df1

    # def theoutreach():
    #     try:
    #         try:
    #             print("The out reach")
    #             err_logs = []

    #             baseSearchUrl = "https://theoutreach.in/?s="
    #             domainUrl = "hhttps://theoutreach.in"
    #             keywords = ['IPO', 'initial public offering','Pre IPO']

    #             # use this for faster testing
    #             tkeywords = ["IPO"]
    #             scrapedData = {}
    #             links = []
    #             titles = []
    #             err_index = []
    #             ArticleDates = []
    #             ScrapeDates = []
    #             for keyword in tkeywords:
    #                 queryUrl = baseSearchUrl + keyword
    #                 try:
    #                     session = HTMLSession()
    #                     resp = session.post(queryUrl)
    #                     resp.html.render()
    #                     pageSource = resp.html.html
    #                     parsedSource = BeautifulSoup(pageSource, "html.parser")
    #                 except:
    #                     err = "theoutreach: err: Failed to access search url: " + queryUrl + " and convert it to soup object"
    #                     err_logs.append(err)
    #                     continue
    #                 # with open("response.html", "w") as f:
    #                 #     f.write(pageSource)
    #                 # break
    #                 for item in parsedSource.find("div", class_="article-container").find_all("article"):
    #                     requiredTag = item.find("h2", class_="entry-title")
    #                     currentArticleTitle = str(requiredTag.find("a")["title"]).strip()
    #                     # print(currentArticleTitle)
    #                     currentArticleLink = requiredTag.find("a")["href"]
    #                     # print(currentArticleLink)
    #                     if currentArticleLink[0] == "/":
    #                         links.append(domainUrl + currentArticleLink)
    #                     else:
    #                         links.append(currentArticleLink)
    #                     titles.append(currentArticleTitle)
    #                     currentArticleDateText = item.find("time", class_="entry-date published updated").text
    #                     try:
    #                         currentArticleDate = datetime.strptime(currentArticleDateText,
    #                                                             "%B %d, %Y").strftime("%d-%m-%Y")
    #                     except:
    #                         err = "theoutreach: err: Failed to retrieve date from article : " + currentArticleLink
    #                         ArticleDates.append("Error")
    #                         err_index.append(links.append(currentArticleLink))
    #                         err_logs.append(err)
    #                         continue
    #                     ArticleDates.append(currentArticleDate)
    #                     ScrapeDates.append(datetime.today().strftime("%d-%m-%Y"))
    #                 scrapedData["title"] = titles
    #                 scrapedData["link"] = links
    #                 scrapedData["publish_date"] = ArticleDates
    #                 scrapedData["scraped_date"] = ScrapeDates
    #                 # print(titles)
    #                 # print(links)
    #                 # print(ArticleDates)

    #                 # Article's date and description scraping
    #                 ArticleBody = []
    #                 for link in links:
    #                     articleText = ""
    #                     try:
    #                         session = HTMLSession()
    #                         resp = session.get(link)
    #                         resp.html.render()
    #                         pageSource = resp.html.html
    #                         parsedSource = BeautifulSoup(pageSource, "html.parser")
    #                         # headers = {
    #                         #     'User-Agent': "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 Chrome/58.0.3029.110 Safari/537.36"}
    #                         # pageSource = requests.get(link, headers=headers)
    #                         # parsedSource = BeautifulSoup(pageSource.content, "html.parser", from_encoding="iso-8859-1")
    #                     except:
    #                         err = "theoutreach: err: Failed to access article link : " + link
    #                         ArticleDates.append("Error")
    #                         err_index.append(links.append(link))
    #                         err_logs.append(err)
    #                         continue
    #                     # with open("response.html", "w") as f:
    #                     #     f.write(pageSource)
    #                     # break
    #                     divTag = parsedSource.find("div", class_="entry-content clearfix")
    #                     for item in divTag.find_all("p"):
    #                         articleText += item.text
    #                     ArticleBody.append(articleText)
    #                 scrapedData["text"] = ArticleBody
    #                 # print(ArticleBody)

    #             # DataFrame creation
    #             theoutreachDF = pd.DataFrame(scrapedData)
    #             if theoutreachDF.empty:
    #                 err = "theoutreach: err: Empty dataframe"
    #                 err_logs.append(err)
    #             df = FilterFunction(theoutreachDF)
    #             emptydataframe("The out reach",df)
    #             return df
    #         except:
    #             print("The outreach is not working")
    #             not_working_functions("The out reach")
    #     except:
    #         df1 = pd.DataFrame(columns =['title','link','publish_date','scraped_date'])
    #         return df1
    # def dealstreetasia():
    #     try:
    #         try:
    #             print("Dealstreetasia")
    #             err_logs = []  # Access to view error logs
    #             url = "https://www.dealstreetasia.com/?s=ipo"
    #             domain_url = "https://www.dealstreetasia.com/"

    #             try:
    #                 page = requests.get(url)
    #                 soup = BeautifulSoup(page.content, "html.parser")
    #             except:
    #                 err = "err: Failed to access main url: " + url + " and convert it to soup object"
    #                 err_logs.append(err)
    #                 return None

    #             # Class names of the elements to be scraped - change if the website to be scraped changes them
    #             div_class = "category-link"
    #             h1_class = "col-xl-8 col-lg-10 col-main"
    #             date_div_class = "published-date"
    #             para_div_class = "content-section"

    #             links = []

    #             for divtag in soup.find_all("p", {"class": div_class}):
    #                 for a in divtag.find_all("a", href=True):
    #                     link = a["href"]  # Gets the link

    #                     # Checking the link if it is a relative link
    #                     if link[0] == '/':
    #                         link = domain_url + link

    #                     links.append(link)



    #             collection = []

    #             for link in links:
    #                 try:
    #                     l_page = requests.get(link)
    #                     l_soup = BeautifulSoup(l_page.content, 'html.parser')
    #                 except:
    #                     err = "err: Failed to retrieve data from link: " + link + " and convert it to soup object"
    #                     err_logs.append(err)
    #                     continue

    #                 data = []
    #                 # Scraping the heading
    #                 h1_ele = l_soup.find("div", {"class": h1_class})
    #                 try:
    #                     data.append(h1_ele.text)
    #                 except:
    #                     err = "err: Failed to find title in page. Link: " + link
    #                     err_logs.append(err)
    #                     continue  # drops the complete data if there is an error

    #                 # Adding the link to data
    #                 data.append(link)

    #                 # Scraping the published date
    #                 date_ele = l_soup.find("p", {"class": date_div_class})
    #                 try:
    #                     date_text = date_ele.text
    #                     date_text = (date_text.split('/'))[-1]
    #                     date_text = date_text.replace(" Updated: ", "")
    #                     data.append(date_text)  # The date_text could be further modified to represent a proper date format

    #                 except:
    #                     err = "err: Failed to find date in page. Link: " + link
    #                     err_logs.append(err)
    #                     continue  # drops the complete data if there is an error

    #                 # Adding the scraped date to data
    #                 cur_date = str(datetime.today())
    #                 data.append(cur_date)

    #                 # Scraping the paragraph
    #                 para_ele = l_soup.find("div", {"class": para_div_class})
    #                 try:
    #                     data.append(para_ele.text)  # Need to make this better
    #                 except:
    #                     err = "err: Failed to find paragraph in page. Link: " + link
    #                     err_logs.append(err)
    #                     continue  # drops the complete data if there is an error

    #                 # Adding data to the collection
    #                 collection.append(data)

    #             df = pd.DataFrame(collection, columns =['title', 'link','publish_date','scraped_date','text'])
    #             if df.empty:
    #                 err = "err: Empty dataframe"
    #                 err_logs.append(err)
    #             df =FilterFunction(df)
    #             emptydataframe("Dealstreetasia",df)
    #             log_errors(err_logs)
    #             return df
    #         except:
    #             print("Dealstreetasia not working")
    #             not_working_functions.append("Dealstreetasia")
    #     except:
    #         df1 = pd.DataFrame(columns =['title','link','publish_date','scraped_date'])
    #         return df1
    def livemint():
        try:
            print("Livemint India")
            err_logs = []
            url = "https://www.livemint.com/Search/Link/Keyword/ipo"
            domain_url = "https://www.livemint.com/"

            headers = {
                "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10.15; rv:78.0) Gecko/20100101 Firefox/78.0",
                "accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.9",
                'sec-fetch-site': 'none',
                'sec-fetch-mode': 'navigate',
                'sec-fetch-user': '?1',
                'sec-fetch-dest': 'document',
                'accept-language': 'en-GB,en-US;q=0.9,en;q=0.8',
            }
            page = requests.get(url, headers=headers)
            soup = BeautifulSoup(page.content, "html.parser")
            #soup  # Debugging - if soup is working correctly

            # Class names of the elements to be scraped
            h2_class = "headline"  # Class name of div containing the a tag
            #h1_class = "_1Y-96"
            #h1_div_class = "col-xs-12"
            title_h1_class = "headline"
            date_span_class = "pubtime"
            para_ul_class = "highlights"

            links = []

            for divtag in soup.find_all("h2", {"class": h2_class}):
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
            #links # Debugging - if link array is generated

            collection = []
            scrapper_name = "livemint"

            for link in links:
                try:
                    l_page = requests.get(link)
                    l_soup = BeautifulSoup(l_page.content, 'html.parser')
                except:
                    err = scrapper_name + ": err: Failed to retrieve data from link: " + link + " and convert it to soup object"
                    err_logs.append(err)
                    continue

                data = []
                # Scraping the heading
                #h1_ele = l_soup.find("h1", {"class": h1_class})
                
                try:
                    title_ele = l_soup.find("h1", {"class": title_h1_class})
                    data.append(title_ele.text)
                except:
                    err = scrapper_name + ": err: Failed to find title in page. Link: " + link
                    err_logs.append(err)
                    continue  # drops the complete data if there is an error


                # Adding the link to data
                data.append(link)

                # Scraping the published date
                date_ele = l_soup.find("span", {"class": date_span_class})
                try:
                    date_text = date_ele.text
                    date_text = ''.join((date_text.split(':'))[1:])
                    #date_text = date_text.replace(" Updated: ", "")
                    data.append(date_text)  # The date_text could be further modified to represent a proper date format
                except:
                    err = scrapper_name + ": err: Failed to find date in page. Link: " + link
                    err_logs.append(err)
                    continue  # drops the complete data if there is an error
                
                # Adding the scraped date to data
                cur_date = str(datetime.today())
                data.append(cur_date)
                

                # Scraping the paragraph
                try:
                    para_ele = (l_soup.findAll("ul", {"class": para_ul_class}))[-1]
                    data.append(para_ele.text)  # Need to make this better
                except:
                    new_para_p_class = "summary"
                    try:
                        para_ele = (l_soup.findAll("p", {"class": new_para_p_class}))[-1]
                        data.append(para_ele.text)  # Need to make this better
                    except:
                        err = scrapper_name + ": err: Failed to find paragraph in page. Link: " + link
                        err_logs.append(err)
                        continue  # drops the complete data if there is an error
                # Adding data to a collection
                collection.append(data)

            df = pd.DataFrame(collection, columns =['title', 'link','publish_date','scraped_date','text'])
            if df.empty:
                err = scrapper_name + ": err: Empty dataframe"
                err_logs.append(err)
            #print(df) # For debugging. To check if df is created
            #print(err_logs) # For debugging - to check if any errors occoured
            df = FilterFunction(df)
            emptydataframe("Livemint India ",df)
            log_errors(err_logs)
            # df  = link_correction(df)
            return df
        except:
            not_working_functions.append("Livemint India")
            print("Livemint not working")
    def guardian():
        try:
            print("Bahamas")
            err_logs = []  # Access to view error logs
            url = "https://bahamaspress.com/"
            domain_url = "https://bahamaspress.com/?s=ipo"

            try:
                page = requests.get(url)
                soup = BeautifulSoup(page.content, "html.parser")
            except:
                err = "err: Failed to access main url: " + url + " and convert it to soup object"
                err_logs.append(err)
                return None

            # Class names of the elements to be scraped - change if the website to be scraped changes them
            div_class = "item-details"
            h1_class = "entry-title"
            date_div_class = "td-post-date"
            para_div_class = "td-post-content"

            links = []
            for h3 in soup.find_all("h3",{"class":"entry-title td-module-title"}):
                link = h3.a["href"]
                if link[0] == '/':
                    link = domain_url + link
                links.append(link)
            collection = []

            for link in links:
                try:
                    l_page = requests.get(link)
                    l_soup = BeautifulSoup(l_page.content, 'html.parser')
                except:
                    err = "err: Failed to retrieve data from link: " + link + " and convert it to soup object"
                    err_logs.append(err)
                    continue

                data = []
                # Scraping the heading
                h1_ele = l_soup.find("h1", {"class": h1_class})
                try:
                    data.append(h1_ele.text)
                except:
                    err = "err: Failed to find title in page. Link: " + link
                    err_logs.append(err)
                    continue  # drops the complete data if there is an error

                # Adding the link to data
                data.append(link)

                # Scraping the published date
                date_ele = l_soup.find("span", {"class": date_div_class})
                try:
                    date_text = date_ele.text
                    #date_text = (date_text.split('/'))[-1]
                    #date_text = date_text.replace(" Updated: ", "")
                    data.append(date_text)  # The date_text could be further modified to represent a proper date format

                except:
                    err = "err: Failed to find date in page. Link: " + link
                    err_logs.append(err)
                    continue  # drops the complete data if there is an error

                # Adding the scraped date to data
                cur_date = str(datetime.today())
                data.append(cur_date)

                # Scraping the paragraph
                para_ele = l_soup.find("div", {"class": para_div_class})
                try:
                    data.append(para_ele.text)  # Need to make this better
                except:
                    err = "err: Failed to find paragraph in page. Link: " + link
                    err_logs.append(err)
                    continue  # drops the complete data if there is an error

                # Adding data to the collection
                collection.append(data)

            df = pd.DataFrame(collection, columns =['title', 'link','publish_date','scraped_date','text'])
            if df.empty:
                err = "err: Empty dataframe"
                err_logs.append(err)
            df = FilterFunction(df)
            emptydataframe("Guardian Bahamas",df)
            log_errors(err_logs)
            # df  = link_correction(df)
            return df
        except:
            not_working_functions.append("Guardian bahamas")
            print("Guardian bahamas not working")
    def azernews():
        try:
            print("Azernews")
            err_logs = []
            url = "https://www.azernews.az/search.php?query=ipo"
            domain_url = "https://www.azernews.az/"

            headers = {
                "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10.15; rv:78.0) Gecko/20100101 Firefox/78.0",
                "accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.9",
                'sec-fetch-site': 'none',
                'sec-fetch-mode': 'navigate',
                'sec-fetch-user': '?1',
                'sec-fetch-dest': 'document',
                'accept-language': 'en-GB,en-US;q=0.9,en;q=0.8',
            }
            page = requests.get(url, headers=headers)
            soup = BeautifulSoup(page.content, "html.parser")
            links = []

            for a in soup.find_all("a",{"class":"news-item shadow"}, href=True):
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
            #links # Debugging - if link array is generated
            print(links)
            collection = []
            scrapper_name = "azernews"

            for link in links:
                try:
                    l_page = requests.get(link)
                    l_soup = BeautifulSoup(l_page.content, 'html.parser')
                except:
                    err = scrapper_name + ": err: Failed to retrieve data from link: " + link + " and convert it to soup object"
                    err_logs.append(err)
                    continue

                data = []
                # Scraping the heading
                #h1_ele = l_soup.find("h1", {"class": h1_class})
                
                try:
                    title_ele = l_soup.find("div", {"class": "article-content-wrapper"}).h2
                    data.append(title_ele.text)
                except:
                    err = scrapper_name + ": err: Failed to find title in page. Link: " + link
                    err_logs.append(err)
                    continue  # drops the complete data if there is an error


                # Adding the link to data
                data.append(link)

                # Scraping the published date
                date_ele = l_soup.find("span", {"class": "me-3"})
                try:
                    date_text = date_ele.text
                    #date_text = (date_text.split('/'))[-1]
                    #date_text = date_text.replace(" Updated: ", "")
                    data.append(date_text)  # The date_text could be further modified to represent a proper date format
                except:
                    err = scrapper_name + ": err: Failed to find date in page. Link: " + link
                    err_logs.append(err)
                    continue  # drops the complete data if there is an error
                
                # Adding the scraped date to data
                cur_date = str(datetime.today())
                data.append(cur_date)
                

                # Scraping the paragraph
                para_ele = l_soup.find("div", {"class": "article-content"})
                try:
                    data.append(para_ele.text)  # Need to make this better
                except:
                    err = scrapper_name + ": err: Failed to find paragraph in page. Link: " + link
                    err_logs.append(err)
                    continue  # drops the complete data if there is an error
                # Adding data to a collection
                collection.append(data)
            # print(err_logs)
            df = pd.DataFrame(collection, columns =['title', 'link','publish_date','scraped_date','text'])
            if df.empty:
                err = scrapper_name + ": err: Empty dataframe"
                err_logs.append(err)
            # print(df) # For debugging. To check if df is created
            # print(err_logs) # For debugging - to check if any errors occoured
            df = FilterFunction(df)
            emptydataframe("Azernews",df)
            log_errors(err_logs)
            # df  = link_correction(df)
            return df
        except:
            not_working_functions.append("Azernews")
            print("Azernews is not working")
    def chosenilboenglish():
        try:
            print("chosenilboenglish")
            err_logs = []
            url = "https://english.chosun.com/svc/list_in/search.html?query=ipo&pageconf=total"
            domain_url = "http://english.chosun.com/"

            headers = {
                "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10.15; rv:78.0) Gecko/20100101 Firefox/78.0",
                "accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.9",
                'sec-fetch-site': 'none',
                'sec-fetch-mode': 'navigate',
                'sec-fetch-user': '?1',
                'sec-fetch-dest': 'document',
                'accept-language': 'en-GB,en-US;q=0.9,en;q=0.8',
            }
            page = requests.get(url, headers=headers)
            soup = BeautifulSoup(page.content, "html.parser")
            #soup  # Debugging - if soup is working correctly

            # Class names of the elements to be scraped
            dl_class = "list_item"  # Class name of div containing the a tag
            #h1_class = "_1Y-96"
            #h1_div_class = "col-xs-12"
            title_h1_id = "news_title_text_id"
            date_p_id = "date_text"
            para_div_class = "par"

            links = []

            # for divtag in soup.find_all("dl", {"class": dl_class}):
            for a in soup.find_all("dl",{"class":"list_item"}):
                    link = a.dt.a["href"]  # Gets the link
                    
                    # Checking the link if it is a relative link
                    if link[0] == '/':
                        link = domain_url + link
                    
                    # Filtering advertaisment links
                    link_start = domain_url 
                    if link.startswith(link_start):
                        links.append(link)
            # Remove duplicates
            links = list(set(links))
            #links # Debugging - if link array is generated
            print(links)
            collection = []
            scrapper_name = "azernews"

            for link in links:
                try:
                    l_page = requests.get(link)
                    l_soup = BeautifulSoup(l_page.content, 'html.parser')
                except:
                    err = scrapper_name + ": err: Failed to retrieve data from link: " + link + " and convert it to soup object"
                    err_logs.append(err)
                    continue

                data = []
                # Scraping the heading
                #h1_ele = l_soup.find("h1", {"class": h1_class})
                
                try:
                    title_ele = l_soup.find("h1", {"id": title_h1_id})
                    data.append(title_ele.text)
                except:
                    err = scrapper_name + ": err: Failed to find title in page. Link: " + link
                    err_logs.append(err)
                    continue  # drops the complete data if there is an error


                # Adding the link to data
                data.append(link)

                # Scraping the published date
                date_ele = l_soup.find("p", {"id": date_p_id})
                try:
                    date_text = date_ele.text
                    #date_text = (date_text.split('/'))[-1]
                    #date_text = date_text.replace(" Updated: ", "")
                    data.append(date_text)  # The date_text could be further modified to represent a proper date format
                except:
                    err = scrapper_name + ": err: Failed to find date in page. Link: " + link
                    err_logs.append(err)
                    continue  # drops the complete data if there is an error
                
                # Adding the scraped date to data
                cur_date = str(datetime.today())
                data.append(cur_date)
                

                # Scraping the paragraph
                para_ele = (l_soup.findAll("div", {"class": para_div_class}))[-1]
                try:
                    data.append(para_ele.text)  # Need to make this better
                except:
                    err = scrapper_name + ": err: Failed to find paragraph in page. Link: " + link
                    err_logs.append(err)
                    continue  # drops the complete data if there is an error
                # Adding data to a collection
                collection.append(data)

            df = pd.DataFrame(collection, columns =['title', 'link','publish_date','scraped_date','text'])
            if df.empty:
                err = scrapper_name + ": err: Empty dataframe"
                err_logs.append(err)
            #print(df) # For debugging. To check if df is created
            #print(err_logs) # For debugging - to check if any errors occoured
            df = FilterFunction(df)
            emptydataframe("chosenilboenglish",df)
            log_errors(err_logs)
            return df
        except:
            not_working_functions.append("chosenilboenglish")
            print("chosenilboenglish not working")
    def otempo():
        try:
            print("Brazil")

            err_logs = []
            url = "https://www.otempo.com.br/busca-portal-o-tempo-7.6253516?q=IPO"
            domain_url = "https://www.otempo.com.br/"
            title,links,text,pub_date,scraped_date = [],[],[],[],[]
            try:
                page = requests.get(url)
                soup = BeautifulSoup(page.content,"html.parser")
                # print(soup)
                
            except:
                err = "Otempo : err : Couldn't fetch " + url 
                err_logs.append(err)
                return 

            all_divs = soup.find_all("h2",{"class":"titulo"})
            for div in all_divs:
                links.append(domain_url+div.a["href"])
            #Fetch all the necessary data 
            # print(links)
            final_links = []
            today = date.today()
            # print(links)
            for link in links:
                try:
                    try:
                        page = requests.get(link)
                        soup = BeautifulSoup(page.content,"html.parser")
                    # print(soup)
                    # print(link)
                    except:
                        err = "Otempo : err : Couldn't fetch url " + link 
                        err_logs.append(err)
                        continue

                    #Published Date
                    pub_date.append(soup.find("div" , {"class" : "data-publicacao"}).text)
                    

                    #Title of article 
                    title.append(soup.find("div" , {"class" : "cell titulo"}).h1.text)       

                    #Text of article
                    text.append(soup.find("div" , {"class" : "cell chamada"}).h2.text)

                    #Scrapped date 
                    scraped_date.append(str(today))

                    #Working links
                    final_links.append(link)
                except:
                    continue
            df = pd.DataFrame({"text":text,"link":final_links,"publish_date":pub_date,"scraped_date":scraped_date,"title":title})
            if df.empty:
                err = "otempo : err: Empty dataframe"
                err_logs.append(err)
            df = df.drop_duplicates(subset=["link"])
            df = translate_dataframe(df)
            df = FilterFunction(df)
            emptydataframe("Otempo brazil",df)
            # df  = link_correction(df)
            return df
        except:
            print("Otempo brazil not working")
            not_working_functions.append("Otempo Brazil")
    def elicudadona():
        try:
            print("Chile")
            err_logs = []
            url = "https://www.elciudadano.com/?s=oferta+p%C3%BAblica+inicial"
            domain_url = "https://www.elciudadano.com/"
            title,links,text,pub_date,scraped_date = [],[],[],[],[]
            try:
                page = requests.get(url,timeout=10)
                soup = BeautifulSoup(page.content,"html.parser")
                # print(soup)
                
            except:
                err = "Elicudadona : err : Couldn't fetch " + url 
                err_logs.append(err)
                return 

            all_divs = soup.find_all("h3",{"class":"mb-3"})
            for div in all_divs:
                links.append(div.a["href"])
            #Fetch all the necessary data 
            # print(links)
            final_links = []
            today = date.today()
            for link in links:
                try:
                    page = requests.get(link)
                    soup = BeautifulSoup(page.content,"html.parser")
                # print(soup)
                # print(link)
                except:
                    err = "Elicudadona : err : Couldn't fetch url " + link 
                    err_logs.append(err)
                    continue
                #Published Date
                pub_date.append(soup.find("span",{"class":"time-ago time-now"})["data-date"])
                # print(pub_date) 

                #Title of article 
                title.append(soup.find("h1" , {"class" : "mb-4 the_title"}).text)      
                # print(title) 

                #Text of article
                text.append(soup.find("div" , {"class" : "the-excerpt-"}).text)

                #Scrapped date 
                scraped_date.append(str(today))

                #Working links
                final_links.append(link)
            df = pd.DataFrame({"text":text,"link":final_links,"publish_date":pub_date,"scraped_date":scraped_date,"title":title})
            if df.empty:
                err = "Folha : err: Empty dataframe"
                err_logs.append(err)
            df = df.drop_duplicates(subset=["link"])
            df = translate_dataframe(df)
            df =FilterFunction(df)
            emptydataframe("Elicudadona Chile",df)
            # df  = link_correction(df)
            return df
        except:
            not_working_functions.append("elicudadona chile")
            print("elicudadona not working")
    
    def standartnews(keyword):
        try:
            print("standartnews bulgaria")
            err_logs = []
            url = f"https://www.standartnews.com/articles/search.html?keywords={keyword}&author=&category=-1&date_from=&date_to="
            domain_url = "https://www.standartnews.com/"
            title,links,text,pub_date,scraped_date = [],[],[],[],[]
            try:
                page = requests.get(url)
                soup = BeautifulSoup(page.content,"html.parser")
                # print(soup)
                
            except:
                err = "Standartnews : err : Couldn't fetch " + url 
                err_logs.append(err)
                return 

            all_divs = soup.find_all("a",{"class":"news-general-link"})
            for div in all_divs:
                links.append(div["href"])
            #Fetch all the necessary data 
            # print(links)
            final_links = []
            today = date.today()
            for link in links:
                try:
                    page = requests.get(link)
                    soup = BeautifulSoup(page.content,"html.parser")
                    # print(soup)
                    # print(link)
                except:
                    err = "Standartnews : err : Couldn't fetch url " + link 
                    err_logs.append(err)
                    continue
                #Published Date
                pub_date.append(soup.find("time")["datetime"])
                

                #Title of article 
                title.append(soup.find("div" , {"class" : "title-cont"}).h1.text)       

                #Text of article
                text.append(soup.find("div" , {"class" : "content"}).p.text)

                #Scrapped date 
                scraped_date.append(str(today))

                #Working links
                final_links.append(link)
            df = pd.DataFrame({"text":text,"link":final_links,"publish_date":pub_date,"scraped_date":scraped_date,"title":title})
            if df.empty:
                err = "Folha : err: Empty dataframe"
                err_logs.append(err)
            df = df.drop_duplicates(subset=["link"])
            df = translate_dataframe(df)
            df = FilterFunction(df)
            emptydataframe("standartnews bulgaria",df)
            # df  = link_correction(df)
            return df
        except:
            print("standartnews bulgaria not working")
            not_working_functions.append("standartnews bulgaria")
    def lastampa():
        try:
            print("lastampa Italy")
            err_logs = []
            url = "https://www.lastampa.it/ricerca?query=IPO&tracking=LSHHD-S"
            domain_url = ""
            title,links,text,pub_date,scraped_date = [],[],[],[],[]
            try:
                page = requests.get(url)
                soup = BeautifulSoup(page.content,"html.parser")
                # print(soup)
                
            except:
                err = "Lastampa : err : Couldn't fetch " + url 
                err_logs.append(err)
                return 

            all_divs = soup.find_all("div",{"class":"entry__content__top"})
            for div in all_divs:
                links.append(div.a["href"])
            #Fetch all the necessary data 
            # print(links)
            final_links = []
            today = date.today()
            for link in links:
                try:
                    page = requests.get(link)
                    soup = BeautifulSoup(page.content,"html.parser")
                # print(soup)
                # print(link)
                except:
                    err = "lastampa : err : Couldn't fetch url " + link 
                    err_logs.append(err)
                    continue

                if(soup.find("div" , {"class" : "story__content"}).p == None or len(soup.find("div" , {"class" : "story__content"}).p) == 0 ):
                    continue
                text.append(soup.find("div" , {"class" : "story__content"}).p)
                #Published Date
                pub_date.append(soup.find("time",{"class":"story__date"})["datetime"])
                

                #Title of article 
                title.append(soup.find("h1" , {"class" : "story__title"}).text)       
                # print(title)
                #Text of article
                
            
                #Scrapped date 
                scraped_date.append(str(today))

                #Working links
                final_links.append(link)
            df = pd.DataFrame({"text" : text , "link":final_links,"publish_date":pub_date,"scraped_date":scraped_date,"title":title})
            if df.empty:
                err = "lastampa : err: Empty dataframe"
                err_logs.append(err)
            df = df.drop_duplicates(subset=["link"])
            df = translate_dataframe(df)
            df = FilterFunction(df)
            emptydataframe("Lastampa Italy",df)
            # df  = link_correction(df)
            return df
        except:
            print("Lastampa Italy not working")
            not_working_functions.append("Lastampa Italy")
    def liputan6():
        try:
            print("Liputan Indo")
            err_logs = []
            url = "https://www.liputan6.com/search?q=IPO"
            domain_url = "https://www.liputan6.com/"
            title,links,text,pub_date,scraped_date = [],[],[],[],[]
            try:
                page = requests.get(url)
                soup = BeautifulSoup(page.content,"html.parser")
                # print(soup)
                
            except:
                err = "Liputan6 : err : Couldn't fetch " + url 
                err_logs.append(err)
                return 

            all_divs = soup.find_all("a",{"class":"ui--a articles--iridescent-list--text-item__title-link"})
            for div in all_divs:
                links.append(div["href"])
            #Fetch all the necessary data 
            # print(links)
            final_links = []
            today = date.today()
            for link in links:
                try:
                    page = requests.get(link)
                    soup = BeautifulSoup(page.content,"html.parser")
                # print(soup)
                # print(link)
                except:
                    err = "Liputan6 : err : Couldn't fetch url " + link 
                    err_logs.append(err)
                    continue
                #Published Date
                pub_date.append(soup.find("time",{"class":"read-page--header--author__datetime updated"})["datetime"])
                

                #Title of article 
                title.append(soup.find("h1" , {"class" : "read-page--header--title entry-title"}).text)       

                #Text of article
                text.append(soup.find("div" , {"class" : "article-content-body__item-content"}).p.text)

                #Scrapped date 
                scraped_date.append(str(today))

                #Working links
                final_links.append(link)
            df = pd.DataFrame({"text":text,"link":final_links,"publish_date":pub_date,"scraped_date":scraped_date,"title":title})
            if df.empty:
                err = "Folha : err: Empty dataframe"
                err_logs.append(err)
            df = df.drop_duplicates(subset=["link"])
            df = translate_dataframe(df)
            df = FilterFunction(df)
            emptydataframe("Liputan",df)
            # df  = link_correction(df)
            return df
        except:
            print("Liputan indo not working")
            not_working_functions.append("Liputan indo")
    def milenio():
        try:
            print("Mexico")
            err_logs = []
            url = "https://www.milenio.com/buscador?text=oferta+p%C3%BAblica+inicial"
            domain_url = "https://www.milenio.com/"
            title,links,text,pub_date,scraped_date = [],[],[],[],[]
            try:
                page = requests.get(url)
                soup = BeautifulSoup(page.content,"html.parser")
                # print(soup)
                
            except:
                err = "Milenio : err : Couldn't fetch " + url 
                err_logs.append(err)
                return 

            all_divs = soup.find_all("div",{"class":"title"})
            for div in all_divs:
                links.append(domain_url + div.a["href"])
            #Fetch all the necessary data 
            # print(links)
            final_links = []
            today = date.today()
            for link in links:
                try:
                    page = requests.get(link)
                    soup = BeautifulSoup(page.content,"html.parser")
                # print(soup)
                # print(link)
                except:
                    err = "Milenio : err : Couldn't fetch url " + link 
                    err_logs.append(err)
                    continue
                #Published Date
                pub_date.append(soup.find("div" , {"class" : "content-date"}).time.text)
                

                #Title of article 
                title.append(soup.find("h1" , {"class" : "title"}).text)       
            
                #Text of article
                text.append(soup.find("div" , {"class" : "media-container news"}).p.text)
            
                #Scrapped date 
                scraped_date.append(str(today))

                #Working links
                final_links.append(link)
            df = pd.DataFrame({"text":text,"link":final_links,"publish_date":pub_date,"scraped_date":scraped_date,"title":title})
            if df.empty:
                err = "Milenio : err: Empty dataframe"
                err_logs.append(err)
            df = df.drop_duplicates(subset=["link"])
            df = translate_dataframe(df)
            df = FilterFunction(df)
            emptydataframe("Millenio Mexico",df)
            # df  = link_correction(df)
            return df
        except:
            print("Mexico not working")
            not_working_functions.append("Millenio Mexico")
    def scoop():
        try:
            print("New Zealand")
            err_logs = []
            url = "https://search.scoop.co.nz/search?q=IPO&submit="
            domain_url = "https://search.scoop.co.nz/"
            title,links,text,pub_date,scraped_date = [],[],[],[],[]
            try:
                page = requests.get(url)
                soup = BeautifulSoup(page.content,"html.parser")
                # print(soup)
                
            except:
                err = "Scoop : err : Couldn't fetch " + url 
                err_logs.append(err)
                return 

            all_divs = soup.find_all("div",{"class":"result"})
            for div in all_divs:
                links.append(div.a["href"])
            #Fetch all the necessary data 
            # print(links)
            final_links = []
            today = date.today()
            for link in links:
                try:
                    page = requests.get(link)
                    soup = BeautifulSoup(page.content,"html.parser")
                # print(soup)
                # print(link)
                except:
                    err = "Scoop : err : Couldn't fetch url " + link 
                    err_logs.append(err)
                    continue
                #Published Date
                pub_date.append(soup.find("span" , {"class" : "byline"}).b.text)
                

                #Title of article 
                title.append(soup.find("div" , {"class" : "story-top"}).h1.text)     

                #Text of article
                text.append(soup.find("div" , {"id" : "article"}).p.text)
                
                #Scrapped date 
                scraped_date.append(str(today))

                #Working links
                final_links.append(link)
            df = pd.DataFrame({"text":text,"link":final_links,"publish_date":pub_date,"scraped_date":scraped_date,"title":title})
            if df.empty:
                err = "Scoop : err: Empty dataframe"
                err_logs.append(err)
            df = df.drop_duplicates(subset=["link"])
            df = FilterFunction(df)
            emptydataframe("New Zealand",df)
            log_errors(err_logs)
            # df  = link_correction(df)
            return df
        except:
            not_working_functions.append("New Zealand")
            print("New Zealand not working")
    def globallegalchronicle():
        try:
            print("Globallegal")
            err_logs = []
            url = "https://globallegalchronicle.com/?s=ipo"
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
            page = requests.get(url, headers=headers)
            soup = BeautifulSoup(page.content, "html.parser")
            #soup  # Debugging - if soup is working correctly

            # Class names of the elements to be scraped
            h3_class = "entry-title"  # Class name of div containing the a tag
            #h1_class = "_1Y-96"
            #h1_div_class = "col-xs-12"
            title_h1_class = "entry-title"
            date_time_class = "entry-date"
            para_div_class = "entry-content"

            links = []

            for divtag in soup.find_all("h3", {"class": h3_class}):
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
            #links # Debugging - if link array is generated

            collection = []
            scrapper_name = "globallegalchronicle"

            for link in links:
                try:
                    l_page = requests.get(link, headers=headers)
                    l_soup = BeautifulSoup(l_page.content, 'html.parser')
                except:
                    err = scrapper_name + ": err: Failed to retrieve data from link: " + link + " and convert it to soup object"
                    err_logs.append(err)
                    continue

                data = []
                # Scraping the heading
                #h1_ele = l_soup.find("h1", {"class": h1_class})
                
                try:
                    title_ele = l_soup.find("h1", {"class": title_h1_class})
                    data.append(title_ele.text)
                except:
                    err = scrapper_name + ": err: Failed to find title in page. Link: " + link
                    err_logs.append(err)
                    continue  # drops the complete data if there is an error


                # Adding the link to data
                data.append(link)

                # Scraping the published date
                date_ele = l_soup.find("time", {"class": date_time_class})
                try:
                    date_text = date_ele.text
                    #date_text = (date_text.split('/'))[-1]
                    #date_text = date_text.replace(" Updated: ", "")
                    data.append(date_text)  # The date_text could be further modified to represent a proper date format
                except:
                    err = scrapper_name + ": err: Failed to find date in page. Link: " + link
                    err_logs.append(err)
                    continue  # drops the complete data if there is an error
                
                # Adding the scraped date to data
                cur_date = str(datetime.today())
                data.append(cur_date)
                

                # Scraping the paragraph
                para_ele = (l_soup.findAll("div", {"class": para_div_class}))[-1]
                try:
                    data.append(para_ele.text)  # Need to make this better
                except:
                    err = scrapper_name + ": err: Failed to find paragraph in page. Link: " + link
                    err_logs.append(err)
                    continue  # drops the complete data if there is an error
                # Adding data to a collection
                collection.append(data)

            df = pd.DataFrame(collection, columns =['title', 'link','publish_date','scraped_date','text'])
            if df.empty:
                err = scrapper_name + ": err: Empty dataframe"
                err_logs.append(err)
            #print(df) # For debugging. To check if df is created
            #print(err_logs) # For debugging - to check if any errors occoured
            df = FilterFunction(df)
            emptydataframe("globalillegalchronicle",df)
            # df  = link_correction(df)
            return df
        except:
            print("Globallegal not working")
            not_working_functions.append("Global legal")
    
    def supchina():
        try:
            print("supchina")
            err_logs = []
            url = "https://supchina.com/?s=ipo"
            domain_url = "https://supchina.com/"

            headers = {
                "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10.15; rv:78.0) Gecko/20100101 Firefox/78.0",
                "accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.9",
                'sec-fetch-site': 'none',
                'sec-fetch-mode': 'navigate',
                'sec-fetch-user': '?1',
                'sec-fetch-dest': 'document',
                'accept-language': 'en-GB,en-US;q=0.9,en;q=0.8',
            }
            page = requests.get(url, headers=headers)
            soup = BeautifulSoup(page.content, "html.parser")
            #soup  # Debugging - if soup is working correctly

            # Class names of the elements to be scraped
            h3_class = "card__title"  # Class name of div containing the a tag
            #h1_class = "_1Y-96"
            #h1_div_class = "col-xs-12"
            title_h1_class = "h1"
            date_time_class = "post__date"
            para_div_class = "post__chunk"

            links = []

            for divtag in soup.find_all("h3", {"class": h3_class}):
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
            #links # Debugging - if link array is generated

            collection = []
            scrapper_name = "supchina"

            for link in links:
                try:
                    l_page = requests.get(link, headers=headers)
                    l_soup = BeautifulSoup(l_page.content, 'html.parser')
                except:
                    err = scrapper_name + ": err: Failed to retrieve data from link: " + link + " and convert it to soup object"
                    err_logs.append(err)
                    continue

                data = []
                # Scraping the heading
                #h1_ele = l_soup.find("h1", {"class": h1_class})
                
                try:
                    title_ele = l_soup.find("h1", {"class": title_h1_class})
                    data.append(title_ele.text)
                except:
                    err = scrapper_name + ": err: Failed to find title in page. Link: " + link
                    err_logs.append(err)
                    continue  # drops the complete data if there is an error


                # Adding the link to data
                data.append(link)

                # Scraping the published date
                date_ele = l_soup.find("time", {"class": date_time_class})
                try:
                    date_text = "".join(((" ".join((date_ele.text.split(" "))[1:])).split("\t"))[0])
                    #date_text = (date_text.split('/'))[-1]
                    #date_text = date_text.replace(" Updated: ", "")
                    data.append(date_text)  # The date_text could be further modified to represent a proper date format
                except:
                    err = scrapper_name + ": err: Failed to find date in page. Link: " + link
                    err_logs.append(err)
                    continue  # drops the complete data if there is an error
                
                # Adding the scraped date to data
                cur_date = str(datetime.today())
                data.append(cur_date)
                

                # Scraping the paragraph
                para_ele = (l_soup.findAll("div", {"class": para_div_class}))[-1]
                try:
                    data.append(para_ele.text)  # Need to make this better
                except:
                    err = scrapper_name + ": err: Failed to find paragraph in page. Link: " + link
                    err_logs.append(err)
                    continue  # drops the complete data if there is an error
                # Adding data to a collection
                collection.append(data)

            df = pd.DataFrame(collection, columns =['title', 'link','publish_date','scraped_date','text'])
            if df.empty:
                err = scrapper_name + ": err: Empty dataframe"
                err_logs.append(err)
            #print(df) # For debugging. To check if df is created
            #print(err_logs) # For debugging - to check if any errors occoured
            df = FilterFunction(df)
            emptydataframe("Supchina",df)
            # df  = link_correction(df)
            return df
        except:
            print("Supchina not working")
            not_working_functions.append("Supchina")
    def aljazeera():
        try:
            print("Al jazeera Qatar")
            err_logs = []
            url = "https://www.aljazeera.com/search/IPO"
            domain_url = "https://www.aljazeera.com/"
            title,links,text,pub_date,scraped_date = [],[],[],[],[]
            try:
                page = requests.get(url)
                soup = BeautifulSoup(page.content,"html.parser")
                # print(soup)
                
            except:
                err = "Aljazeera : err : Couldn't fetch " + url 
                err_logs.append(err)
                return 

            all_divs = soup.find_all("h3",{"class":"gc__title"})
            for div in all_divs:
                links.append(div.a["href"])
            #Fetch all the necessary data 
            # print(links)
            final_links = []
            today = date.today()
            for link in links:
                try:
                    page = requests.get(link)
                    soup = BeautifulSoup(page.content,"html.parser")
                # print(soup)
                # print(link)
                except:
                    err = "Aljazeera : err : Couldn't fetch url " + link 
                    err_logs.append(err)
                    continue
                #Published Date
                pub_date.append(soup.find("div" ,{"class" : "date-simple css-1yjq2zp"}).text)
                

                #Title of article 
                title.append(soup.find("header" , {"class" : "article-header"}).h1.text)       

                #Text of article
                div = soup.find("div" , {"class" : "wysiwyg wysiwyg--all-content css-1ck9wyi"})
                t = ""
                for i in div.find_all("p"):
                    t += i.text + " "
                text.append(t)
            
            
                #Scrapped date 
                scraped_date.append(str(today))

                #Working links
                final_links.append(link)
            df = pd.DataFrame({"text":text,"link":final_links,"publish_date":pub_date,"scraped_date":scraped_date,"title":title})
            if df.empty:
                err = "Aljazeera: err: Empty dataframe"
                err_logs.append(err)
            df = df.drop_duplicates(subset=["link"])
            df = FilterFunction(df)
            emptydataframe("Aljazeera Qatar",df)
            log_errors(err_logs)
            # df  = link_correction(df)
            return df
        except:
            print("Al Jazeera not working")
            not_working_functions.append("Al Jazeera Qatar")
    def aif():
            try:
                print("AIF Russia")
                err_logs = []
                url = "https://aif.ru/search?text=IPO"
                domain_url = "https://aif.ru/"
                title,links,text,pub_date,scraped_date = [],[],[],[],[]
                try:
                    page = requests.get(url)
                    soup = BeautifulSoup(page.content,"html.parser")
                    # print(soup)
                    
                except:
                    err = "Aif : err : Couldn't fetch " + url 
                    err_logs.append(err)
                    return 

                all_divs = soup.find_all("div",{"class":"text_box"})
                for div in all_divs:
                    links.append(div.a["href"])
                #Fetch all the necessary data 
                # print(links)
                final_links = []
                today = date.today()
                for link in links:
                    try:
                        page = requests.get(link)
                        soup = BeautifulSoup(page.content,"html.parser")
                        # print(soup)
                    # print(link)
                    except:
                        err = "Aif : err : Couldn't fetch url " + link 
                        err_logs.append(err)
                        continue

                    div = soup.find("div" , {"class" : "article_text"})
                    t = ""
                    for i in div.find_all("p"):
                        t += i.text + " "
                    text.append(t) 
                    # print(text)
                    #Published Date
                    pub_date.append(soup.find("div" , {"class" : "date"}).text)
                    

                    #Title of article 
                    title.append(soup.find("h1" , {"itemprop" : "headline"}).text)       

                    #Text of article
                
                
                    #Scrapped date 
                    scraped_date.append(str(today))

                    #Working links
                    final_links.append(link)
                df = pd.DataFrame({"text":text,"link":final_links,"publish_date":pub_date,"scraped_date":scraped_date,"title":title})
                if df.empty:
                    err = "Aif : err: Empty dataframe"
                    err_logs.append(err)
                df = df.drop_duplicates(subset=["link"])
                # df = FilterFunction(df)
                emptydataframe("Aif Russia",df)
                log_errors(err_logs)
                df = df[df["text"] != ""]
                df = translate_dataframe(df)
                # df = FilterFunction(df)
                # df  = link_correction(df)
                return df
            except:
                print("AIF Russia not working")
                not_working_functions.append("AIF")
    def monitor():
        try:
            print("Monitor uganda")
            err_logs = []
            url = "https://www.monitor.co.ug/service/search/uganda/1822068?pageNum=0&query=IPO%20offering&sortByDate=true&channelId=1448278"
            domain_url = "https://www.monitor.co.ug/"
            title,links,text,pub_date,scraped_date = [],[],[],[],[]
            try:
                page = requests.get(url)
                soup = BeautifulSoup(page.content,"html.parser")
                # print(soup)
                
            except:
                err = "Monitor : err : Couldn't fetch " + url 
                err_logs.append(err)
                return 

            all_divs = soup.find_all("li",{"class":"search-result"})
            for div in all_divs:
                links.append(domain_url+div.a["href"])
            #Fetch all the necessary data 
            # print(links)
            final_links = []
            today = date.today()
            for link in links:
                try:
                    try:
                        page = requests.get(link)
                        soup = BeautifulSoup(page.content,"html.parser")
                  # print(soup)
                  # print(link)
                    except:
                        err = "Monitor : err : Couldn't fetch url " + link 
                        err_logs.append(err)
                        continue
                  #Published Date
                    pub_dat = soup.find("time" , {"class" : "date"}).text
                  

                  #Title of article 
                    titl  = soup.find("h1" , {"class" : "title-medium"}).text      

                  #Text of article
                    div = soup.find("div" , {"class" : "paragraph-wrapper"})
                    t = ""
                    for i in div.find_all("p"):
                        t += i.text + " "
                    text.append(t)
                  #Scrapped date 
                    scraped_date.append(str(today))
                    pub_date.append(pub_dat)
                    title.append(titl)
                  #Working links
                    final_links.append(link)
                except:
                    continue
            df = pd.DataFrame({"text":text,"link":final_links,"publish_date":pub_date,"scraped_date":scraped_date,"title":title})
            if df.empty:
                err = "Monitor : err: Empty dataframe"
                err_logs.append(err)
            df = df.drop_duplicates(subset=["link"])
            df = FilterFunction(df)
            emptydataframe("Monitor Uganda",df)
            log_errors(err_logs)
            # df  = link_correction(df)
            return df
        except:
            print("Monitor Uganda not working")
            not_working_functions.append("Uganda Monitor")
    def thesun():
        try:
            print("the sun UK")
            err_logs = []
            url = "https://www.thesun.co.uk/?s=IPO"
            domain_url = "https://www.thesun.co.uk/"
            title,links,text,pub_date,scraped_date = [],[],[],[],[]
            try:
                page = requests.get(url)
                soup = BeautifulSoup(page.content,"html.parser")
                # print(soup)
                
            except:
                err = "The sun  : err : Couldn't fetch " + url 
                err_logs.append(err)
                return 

            all_divs = soup.find_all("a",{"class":"teaser-anchor teaser-anchor--search"})
            for div in all_divs:
                links.append(div["href"])
            #Fetch all the necessary data 
            # print(links)
            final_links = []
            today = date.today()
            for link in links:
                try:
                    page = requests.get(link)
                    soup = BeautifulSoup(page.content,"html.parser")
                # print(soup)
                # print(link)
                except:
                    err = "The sun : err : Couldn't fetch url " + link 
                    err_logs.append(err)
                    continue
                #Published Date
                pub_date.append(soup.find("span" , {"class" :"article__timestamp"}).text)
                

                #Title of article 
                
                title.append(soup.find("h1" , {"class" : "article__headline"}).text)       

                #Text of article     
                div = soup.find("div" , {"class" : "article__content"})
                t = ""
                for i in div.find_all("p"):
                    t += i.text + " "
                text.append(t)
            

                #Scrapped date 
                scraped_date.append(str(today))

                #Working links
                final_links.append(link)
            df = pd.DataFrame({"text":text,"link":final_links,"publish_date":pub_date,"scraped_date":scraped_date,"title":title})
            if df.empty:
                err = "The sun  : err: Empty dataframe"
                err_logs.append(err)
            df = df.drop_duplicates(subset=["link"])
            df = FilterFunction(df)
            emptydataframe("The sun UK",df)
            log_errors(err_logs)
            # df  = link_correction(df)
            return df
        except:
            print("The sun uk not working")
            not_working_functions.append("The sun UK")



    def koreannewsgazette():
        try :
            print("Koreannewsgazette")
            err_logs = []
            url = "https://www.koreanewsgazette.com/?s=IPO"
            domain_url = "https://www.koreanewsgazette.com"
            title,links,text,pub_date,scraped_date = [],[],[],[],[]
            try:
                page = requests.get(url)
                soup = BeautifulSoup(page.content,"html.parser")
                # print(soup)
                
            except:
                err = "koreannewsgazette : err : Couldn't fetch " + url 
                err_logs.append(err)
                return 
            all_divs = soup.find_all("header",{"class":"entry-header"})
            for div in all_divs:
                links.append(div.a["href"])
            #Fetch all the necessary data 
            print(links)
            final_links = []
            today = date.today()
            for link in links:
                try:
                    page = requests.get(link)
                    soup = BeautifulSoup(page.content,"html.parser")
                # print(soup)
                # print(link)
                except:
                    err = "koreannewsgazette : err : Couldn't fetch url " + link 
                    err_logs.append(err)
                    continue
                #Published Date
                pub_date.append(soup.find("time" , {"class" :"entry-date published updated"}).text)
                # print(pub_date)

                #Title of article 
                title.append(soup.find("h1" , {"class" : "entry-title"}).text)  
                # print(title)

                #Text of article
                div = soup.find("div" , {"class" : "entry-content clearfix"})
                t = ""
                for i in div.find_all("p"):
                    t += i.text + " "
                text.append(t)
                # print(text)

                #Scrapped date 
                scraped_date.append(str(today))

                #Working links
                final_links.append(link)
            df = pd.DataFrame({"text":text,"link":final_links,"publish_date":pub_date,"scraped_date":scraped_date,"title":title})
            if df.empty:
                err = "koreannewsgazette : err: Empty dataframe"
                err_logs.append(err)
            df = df.drop_duplicates(subset=["link"])
            df = FilterFunction(df)
            emptydataframe("koreannewsgazette",df)
            # df  = link_correction(df)
            return df
        except :
            print("koreannewsgazette not working")
            not_working_functions.append('koreannewsgazette')
    
    def parool():
        try:
            print("Parool Netherlands")
            err_logs = []
            url = "https://www.parool.nl/search?query=beursgang"
            domain_url = "https://www.parool.nl"
            title,links,text,pub_date,scraped_date = [],[],[],[],[]
            try:
                page = requests.get(url)
                soup = BeautifulSoup(page.content,"html.parser")
                # print(soup)
                
            except:
                err = "Parool : err : Couldn't fetch " + url 
                err_logs.append(err)
                return 

            all_divs = soup.find_all("article",{"class":"fjs-teaser-compact teaser--compact"})
            for div in all_divs:
                links.append(domain_url+div.a["href"])
            #Fetch all the necessary data 
            # print(links)
            final_links = []
            today = date.today()
            for link in links:
                try:
                    page = requests.get(link)
                    soup = BeautifulSoup(page.content,"html.parser")
                # print(soup)
                # print(link)
                except:
                    err = "Parool : err : Couldn't fetch url " + link 
                    err_logs.append(err)
                    continue
                #Published Date
                pub_date.append(str(soup.find("time" , {"class" : "artstyle__production__datetime"})["datetime"]))
                

                #Title of article 
                title.append(soup.find("h1" , {"class" : "artstyle__header-title"}).text)       
            

                #Text of article
                div = soup.find("section" , {"class" : "artstyle__main"})
                t = ""
                for i in div.find_all("p" , {"class" : "artstyle__paragraph "}):
                    t += i.text + " "
                text.append(t)
                
                
                #Scrapped date 
                scraped_date.append(str(today))

                #Working links
                final_links.append(link)
            df = pd.DataFrame({"text":text,"link":final_links,"publish_date":pub_date,"scraped_date":scraped_date,"title":title})
            if df.empty:
                err = "Parool : err: Empty dataframe"
                err_logs.append(err)
            df = df.drop_duplicates(subset=["link"])
            df = translate_dataframe(df)
            df = FilterFunction(df)
            emptydataframe("Parool Netherlands")
            log_errors(err_logs)
            # df  = link_correction(df)
            return df
        except:
            print("Netherlands is not working")
            not_working_functions.append("Netherlands parool")
    def shabiba():
        try:
            print("Oman shabiba")
            err_logs = []
            url = "https://shabiba.com/search?search=%D8%A7%D9%84%D8%B7%D8%B1%D8%AD+%D8%A7%D9%84%D8%B9%D8%A7%D9%85+%D8%A7%D9%84%D8%A3%D9%88%D9%84%D9%8A"
            domain_url = "https://shabiba.com"
            title,links,text,pub_date,scraped_date = [],[],[],[],[]
            try:
                page = requests.get(url)
                soup = BeautifulSoup(page.content,"html.parser")
              # print(soup)

            except:
                err = "Shabiba : err : Couldn't fetch " + url 
                err_logs.append(err)
                return 

            all_divs = soup.find_all("h2",{"class":"post-title"})
            for div in all_divs:
                links.append(domain_url+div.a["href"])
          #Fetch all the necessary data 
          # print(links)
            final_links = []
            today = date.today()
            for link in links:
                try:
                    page = requests.get(link)
                    soup = BeautifulSoup(page.content,"html.parser")
              # print(soup)
              # print(link)
                except:
                    err = "Shabiba : err : Couldn't fetch url " + link 
                    err_logs.append(err)
                    continue
              #Published Date
                pub_date.append(soup.find("span" , {"class" : "text-muted"}).text)


              #Title of article 
                title.append(soup.find("h1" , {"class" : "my-3"}).text)       

              #Text of article
                div = soup.find("div" , {"class" : "mb-5 post-details"})
                t = ""
                for i in div.find_all("p"):
                    t += i.text + " "
                text.append(t)
              # print(t)

              #Scrapped date 
                scraped_date.append(str(today))

              #Working links
                final_links.append(link)
            df = pd.DataFrame({"text":text,"link":final_links,"publish_date":pub_date,"scraped_date":scraped_date,"title":title})
            if df.empty:
                err = "Shabiba : err: Empty dataframe"
                err_logs.append(err)
            df = df.drop_duplicates(subset=["link"])
            df = translate_dataframe(df)
            df = FilterFunction(df)
            emptydataframe("Oman",df)
            log_errors(err_logs)
        #   df = translate_dataframe(df)
        #   df  = link_correction(df)
        
            return df
        except:
            print("Oman not working")
            not_working_functions.append("Oman shabiba")
    def sabah():
        try :
            print("Sabah")
            err_logs = []
            url = "https://www.sabah.com.tr/arama?query=IPO"
            domain_url = "https://www.sabah.com.tr"
            title,links,text,pub_date,scraped_date = [],[],[],[],[]
            try:
                page = requests.get(url)
                soup = BeautifulSoup(page.content,"html.parser")
                # print(soup)
                
            except:
                err = "Sabah : err : Couldn't fetch " + url 
                err_logs.append(err)
                return 
            all_divs = soup.find_all("figure",{"class":"multiple boxShadowSet"})
            for div in all_divs:
                links.append(domain_url+div.a["href"])
            #Fetch all the necessary data 
            # print(links)
            final_links = []
            today = date.today()
            for link in links:
                try:
                    page = requests.get(link)
                    soup = BeautifulSoup(page.content,"html.parser")
                # print(soup)
                # print(link)
                except:
                    err = "Sabah : err : Couldn't fetch url " + link 
                    err_logs.append(err)
                    continue

                #Title of article
                if(soup.find("h1" , {"class" : "pageTitle"}) == None or soup.find("span" , {"class" :"textInfo align-center"}) == None):
                    continue
                title.append(soup.find("h1" , {"class" : "pageTitle"}).text)
                #Published Date
                pub_date.append(soup.find("span" , {"class" :"textInfo align-center"}).text)
                # print(pub_date)

                #Text of article
                text.append(soup.find("div" , {"class" : "newsBox"}).text)
            
                # print(text)

                #Scrapped date 
                scraped_date.append(str(today))

                #Working links
                final_links.append(link)
            df = pd.DataFrame({"text":text,"link":final_links,"publish_date":pub_date,"scraped_date":scraped_date,"title":title})
            if df.empty:
                err = "Sabah : err: Empty dataframe"
                err_logs.append(err)
            df = df.drop_duplicates(subset=["link"])
            df = translate_dataframe(df)
            df = FilterFunction(df)
            emptydataframe("Sabah",df)
            # df  = link_correction(df)
            return df
        except :
            print("Sabah not working")
            not_working_functions.append('Sabah')
    def swissinfo():
        try :
            print("Swissinfo")
            err_logs = []
            url = "https://www.swissinfo.ch/service/search/eng/45808844?query=IPO"
            domain_url = "https://www.swissinfo.ch"
            title,links,text,pub_date,scraped_date = [],[],[],[],[]
            try:
                page = requests.get(url)
                soup = BeautifulSoup(page.content,"html.parser")
                # print(soup)
                
            except:
                err = "Swissinfo : err : Couldn't fetch " + url 
                err_logs.append(err)
                return 
            all_divs = soup.find_all("a",{"class":"si-teaser__link"})
            for div in all_divs:
                links.append(domain_url+div["href"])
            #Fetch all the necessary data 
            # print(links)
            final_links = []
            today = date.today()
            for link in links:
                try:
                    page = requests.get(link)
                    soup = BeautifulSoup(page.content,"html.parser")
                # print(soup)
                # print(link)
                except:
                    err = "koreannewsgazette : err : Couldn't fetch url " + link 
                    err_logs.append(err)
                    continue

                #Title of article
                title.append(soup.find("h1" , {"class" : "si-detail__title"}).text)
                #Published Date
                pub_date.append(soup.find("time" , {"class" :"si-detail__date"})["datetime"])
                # print(pub_date)

                #Text of article
                div = soup.find("section" , {"class" : "si-detail__content"})
                t = ""
                for i in div.find_all("p"):
                    t += i.text + " "
                text.append(t)
                # print(text)

                #Scrapped date 
                scraped_date.append(str(today))

                #Working links
                final_links.append(link)
            df = pd.DataFrame({"text":text,"link":final_links,"publish_date":pub_date,"scraped_date":scraped_date,"title":title})
            if df.empty:
                err = "Swissinfo : err: Empty dataframe"
                err_logs.append(err)
            df = df.drop_duplicates(subset=["link"])
            df = FilterFunction(df)
            emptydataframe("Swissinfo",df)
            # df  = link_correction(df)
            return df
        except :
            print("Swissinfo not working")
            not_working_functions.append('Swissinfo')
    def dziennik():
        try :
            print("Dziennik")
            err_logs = []
            url = "https://www.dziennik.pl/szukaj?c=1&b=1&o=1&s=0&search_term=&q=IPO"
            domain_url = "https://www.thelocal.se"
            title,links,text,pub_date,scraped_date = [],[],[],[],[]
            try:
                page = requests.get(url)
                soup = BeautifulSoup(page.content,"html.parser")
                # print(soup)
                
            except:
                err = "Dziennik : err : Couldn't fetch " + url 
                err_logs.append(err)
                return 
            all_divs = soup.find_all("div",{"class":"resultContent"})
            for div in all_divs:
                links.append(div.a["href"])
            #Fetch all the necessary data 
            # print(links)
            final_links = []
            today = date.today()
            for link in links:
                try:
                    page = requests.get(link)
                    soup = BeautifulSoup(page.content,"html.parser")
                # print(soup)
                # print(link)
                except:
                    err = "Dziennik : err : Couldn't fetch url " + link 
                    err_logs.append(err)
                    continue

                #Title of article
                title.append(soup.find("h1" , {"class" : "mainTitle"}).text)
                #Published Date
                pub_date.append(soup.find("span" , {"class" :"datePublished"}).text)
                # print(pub_date)

                #Text of article
                div = soup.find("div" , {"class" : "detail intext articleBody"}) 
                t = ""
                for i in div.find_all("p" , {"class" : "hyphenate"}):
                    t += i.text + " "
                text.append(t)
                # print(text)

                #Scrapped date 
                scraped_date.append(str(today))

                #Working links
                final_links.append(link)
            df = pd.DataFrame({"text":text,"link":final_links,"publish_date":pub_date,"scraped_date":scraped_date,"title":title})
            if df.empty:
                err = "Dziennik : err: Empty dataframe"
                err_logs.append(err)
            df = df.drop_duplicates(subset=["link"])
            df = translate_dataframe(df)
            df = FilterFunction(df)
            emptydataframe("Dziennik",df)
            # df  = link_correction(df)
            return df
        except :
            print("Dziennik not working")
            not_working_functions.append('dziennik')
    def aljarida():
        try :
            print("Aljarida")
            err_logs = []
            url = "https://www.aljarida.com/search/%D8%A7%D9%84%D8%B7%D8%B1%D8%AD%20%D8%A7%D9%84%D8%B9%D8%A7%D9%85%20%D8%A7%D9%84%D8%A3%D9%88%D9%84%D9%8A/"
            domain_url = "https://www.aljarida.com"
            title,links,text,pub_date,scraped_date = [],[],[],[],[]
            try:
                page = requests.get(url)
                soup = BeautifulSoup(page.content,"html.parser")
                # print(soup)
                
            except:
                err = "Aljarida : err : Couldn't fetch " + url 
                err_logs.append(err)
                return 
            all_divs = soup.find_all("div",{"class":"text"})
            for div in all_divs:
                links.append(domain_url+div.a["href"])
            #Fetch all the necessary data 
            print(links)
            final_links = []
            today = date.today()
            for link in links:
                try:
                    page = requests.get(link)
                    soup = BeautifulSoup(page.content,"html.parser")
                # print(soup)
                # print(link)
                except:
                    err = "Aljarida : err : Couldn't fetch url " + link 
                    err_logs.append(err)
                    continue

                #Title of article
                title.append(soup.find("div" , {"class" : "title"}).h1.text)
                #Published Date
                pub_date.append(soup.find("span" , {"class" :"date"}).text)
                # print(pub_date)

                #Text of article
                div = soup.find("section" , {"id" : "main"})
                t = ""
                for i in div.find_all("p" , {"class" : "ar"}):
                    t += i.text + " "
                text.append(t)
                # print(text)

                #Scrapped date 
                scraped_date.append(str(today))

                #Working links
                final_links.append(link)
            df = pd.DataFrame({"text":text,"link":final_links,"publish_date":pub_date,"scraped_date":scraped_date,"title":title})
            if df.empty:
                err = "Aljarida : err: Empty dataframe"
                err_logs.append(err)
            df = df.drop_duplicates(subset=["link"])
            df = translate_dataframe(df)
            df = FilterFunction(df)
            emptydataframe("Aljarida",df)
            # df  = link_correction(df)
            return df
        except :
            print("aljarida not working")
            not_working_functions.append('aljarida')
    def hungary():
        try :
            print("Hungary")
            err_logs = []
            url = "https://444.hu/kereses?q=IPO"
            domain_url = "https://444.hu/"
            title,links,text,pub_date,scraped_date = [],[],[],[],[]
            try:
                page = requests.get(url)
                soup = BeautifulSoup(page.content,"html.parser")
                # print(soup)
                
            except:
                err = "Hungary : err : Couldn't fetch " + url 
                err_logs.append(err)
                return 
            all_divs = soup.find_all("h1",{"class":"kJ eR eF eT eU eV eW kI eZ"})
            for div in all_divs:
                links.append(div.a["href"])
            #Fetch all the necessary data 
            # print(links)
            final_links = []
            today = date.today()
            for link in links:
                try:
                    page = requests.get(link)
                    soup = BeautifulSoup(page.content,"html.parser")
                # print(soup)
                # print(link)
                except:
                    err = "Hungary : err : Couldn't fetch url " + link 
                    err_logs.append(err)
                    continue

                #Title of article
                title.append(soup.find("h1" , {"class" : "kH eR eF eT eU eV eW fa eZ kG"}).text)
                #Published Date
                pub_date.append(soup.find("span" , {"class" :"eE f5 eT eU eV eW fa fh"}).text)
                # print(pub_date)

                #Text of article
                div = soup.find("div" , {"class" : "eA f- fG eu eT he hf eW hg lp"})
                t = ""
                for i in div.find_all("p"):
                    t += i.text + " "
                text.append(t)
                # print(text)

                #Scrapped date 
                scraped_date.append(str(today))

                #Working links
                final_links.append(link)
            df = pd.DataFrame({"text":text,"link":final_links,"publish_date":pub_date,"scraped_date":scraped_date,"title":title})
            if df.empty:
                err = "Hungary : err: Empty dataframe"
                err_logs.append(err)
            df = df.drop_duplicates(subset=["link"])
            df = translate_dataframe(df)
            df = FilterFunction(df)
            emptydataframe("Hungary",df)
            # df  = link_correction(df)
            return df
        except :
            print("Hungary not working")
            not_working_functions.append('Hungary')
    def jauns():
        try :
            print("jauns")
            err_logs = []
            url = "https://jauns.lv/meklet?q=IPO"
            domain_url = "https://jauns.lv"
            title,links,text,pub_date,scraped_date = [],[],[],[],[]
            try:
                page = requests.get(url)
                soup = BeautifulSoup(page.content,"html.parser")
                # print(soup)
                
            except:
                err = "jauns : err : Couldn't fetch " + url 
                err_logs.append(err)
                return 
            all_divs = soup.find_all("a",{"class":"article-small__link"})
            for div in all_divs:
                links.append(div["href"])
            #Fetch all the necessary data 
            print(links)
            final_links = []
            today = date.today()
            for link in links:
                try:
                    page = requests.get(link)
                    soup = BeautifulSoup(page.content,"html.parser")
                # print(soup)
                # print(link)
                except:
                    err = "Jaus : err : Couldn't fetch url " + link 
                    err_logs.append(err)
                    continue

                #Title of article
                title.append(soup.find("span" , {"class" : "heading__text"}).text)
                #Published Date
                pub_date.append(soup.find("span" , {"class" :"meta-info__publish-date-full"}).text)
                # print(pub_date)

                #Text of article
                div = soup.find("div" , {"class" : "data-io"})
                t = ""
                for i in div.find_all("p"):
                    t += i.text + " "
                text.append(t)
                # print(text)

                #Scrapped date 
                scraped_date.append(str(today))

                #Working links
                final_links.append(link)
            df = pd.DataFrame({"text":text ,"link":final_links,"publish_date":pub_date,"scraped_date":scraped_date,"title":title})
            if df.empty:
                err = "jauns : err: Empty dataframe"
                err_logs.append(err)
            df = df.drop_duplicates(subset=["link"])
            df = translate_dataframe(df)
            df = FilterFunction(df)
            emptydataframe("jauns",df)
            # df  = link_correction(df)
            return df
        except :
            print("jauns not working")
            not_working_functions.append('jauns')
    def pulse():
        try :
            print("Pulse")
            err_logs = []
            url = "https://www.pulse.ng/search?q=IPO"
            domain_url = "https://www.pulse.ng"
            title,links,text,pub_date,scraped_date = [],[],[],[],[]
            try:
                page = requests.get(url)
                soup = BeautifulSoup(page.content,"html.parser")
                # print(soup)
                
            except:
                err = "Pulse : err : Couldn't fetch " + url 
                err_logs.append(err)
                return 
            all_divs = soup.find_all("div",{"class":"gradient-overlay"})
            for div in all_divs:
                links.append(div.a["href"])
            #Fetch all the necessary data 
            # print(links)
            final_links = []
            today = date.today()
            for link in links:
                try:
                    page = requests.get(link)
                    soup = BeautifulSoup(page.content,"html.parser")
                # print(soup)
                # print(link)
                except:
                    err = "Pulse : err : Couldn't fetch url " + link 
                    err_logs.append(err)
                    continue

                #Title of article
                title.append(soup.find("h1" , {"class" : "article-headline "}).span.text)
                # print(title)
                #Published Date
                pub_date.append(soup.find("time" , {"class" :"detail-article-date date-type-publicationDate"})["datetime"])
                # print(pub_date)

                #Text of article
                div = soup.find("div" , {"class" : "article-content "})
                t = ""
                for i in div.find_all("p"):
                    t += i.text + " "
                text.append(t)
                # print(text)

                #Scrapped date 
                scraped_date.append(str(today))

                #Working links
                final_links.append(link)
            df = pd.DataFrame({"text":text,"link":final_links,"publish_date":pub_date,"scraped_date":scraped_date,"title":title})
            if df.empty:
                err = "Pulse : err: Empty dataframe"
                err_logs.append(err)
            df = df.drop_duplicates(subset=["link"])
            df = FilterFunction(df)
            emptydataframe("Pulse",df)
            df = df[df["text"] != ""]
            # df  = link_correction(df)
            return df
        except :
            print("Pulse not working")
            not_working_functions.append('Pulse')
    def vnexpress():
        try :
            print("vnexpress")
            err_logs = []
            url = "https://timkiem.vnexpress.net/?q=IPO"
            domain_url = "https://timkiem.vnexpress.net"
            title,links,text,pub_date,scraped_date = [],[],[],[],[]
            try:
                page = requests.get(url)
                soup = BeautifulSoup(page.content,"html.parser")
                # print(soup)
                
            except:
                err = "vnexpress : err : Couldn't fetch " + url 
                err_logs.append(err)
                return 
            all_divs = soup.find_all("h3",{"class":"title-news"})
            for div in all_divs:
                links.append(div.a["href"])
            #Fetch all the necessary data 
            print(links)
            final_links = []
            today = date.today()
            for link in links:
                try:
                    page = requests.get(link)
                    soup = BeautifulSoup(page.content,"html.parser")
                # print(soup)
                # print(link)
                except:
                    err = "vnexpress : err : Couldn't fetch url " + link 
                    err_logs.append(err)
                    continue

                #Title of article
                if(soup.find("h1" , {"class" : "title-detail"})== None):
                    continue
                title.append(soup.find("h1" , {"class" : "title-detail"}))
                #Published Date
                pub_date.append(soup.find("span" , {"class" :"date"}).text)
                # print(pub_date)

                #Text of article
                div = soup.find("article" , {"class" : "fck_detail "})
                t = ""
                for i in div.find_all("p"):
                    t += i.text + " "
                text.append(t)
                # print(text)

                #Scrapped date 
                scraped_date.append(str(today))

                #Working links
                final_links.append(link)
            df = pd.DataFrame({"text":text ,"link":final_links,"publish_date":pub_date,"scraped_date":scraped_date,"title":title})
            if df.empty:
                err = "vnexpress : err: Empty dataframe"
                err_logs.append(err)
            df = df.drop_duplicates(subset=["link"])
            df = translate_dataframe(df)
            df = FilterFunction(df)
            emptydataframe("vnexpress",df)
            # df  = link_correction(df)
            return df
        except :
            print("vnexpress not working")
            not_working_functions.append('vnexpress')
    def jamaicaobserver():
        try :
            print("jamaicaobserver")
            err_logs = []
            url = "https://www.jamaicaobserver.com/search/?q=IPO"
            domain_url = "https://www.jamaicaobserver.com"
            title,links,text,pub_date,scraped_date = [],[],[],[],[]
            try:
                page = requests.get(url)
                soup = BeautifulSoup(page.content,"html.parser")
                # print(soup)
                
            except:
                err = "jamaicaobserver : err : Couldn't fetch " + url 
                err_logs.append(err)
                return 
            all_divs = soup.find_all("div",{"class":"entry-title"})
            for div in all_divs:
                links.append(div.a["href"])
            #Fetch all the necessary data 
            # print(links)
            final_links = []
            today = date.today()
            for link in links:
                try:
                    page = requests.get(link)
                    soup = BeautifulSoup(page.content,"html.parser")
                # print(soup)
                # print(link)
                except:
                    err = "Jamaice Observer : err : Couldn't fetch url " + link 
                    err_logs.append(err)
                    continue

                #Title of article
                title.append(soup.find("div" , {"class" : "headline col-12"}).text)
                #Published Date
                pub_date.append(soup.find("div" , {"class" :"article-pubdate"}).text)
                # print(pub_date)

                #Text of article
                div = soup.find("div" , {"class" : "article-restofcontent"})
                t = ""
                for i in div.find_all("p" , {"class" : "article__body"}):
                    t += i.text + " "
                text.append(t)
                # print(text)

                #Scrapped date 
                scraped_date.append(str(today))

                #Working links
                final_links.append(link)
            df = pd.DataFrame({"text":text ,"link":final_links,"publish_date":pub_date,"scraped_date":scraped_date,"title":title})
            if df.empty:
                err = "jamaicaobserver : err: Empty dataframe"
                err_logs.append(err)
            df = df.drop_duplicates(subset=["link"])
            df = FilterFunction(df)
            emptydataframe("jamaicaobserver",df)
            # df  = link_correction(df)
            return df
        except :
            print("jamaicaobserver not working")
            not_working_functions.append('jamaicaobserver') 
    def independent():
        try :
            print("independent")
            err_logs = []
            url = "https://www.independent.ie/search/?q=IPO"
            domain_url = "https://www.independent.ie"
            title,links,text,pub_date,scraped_date = [],[],[],[],[]
            try:
                page = requests.get(url)
                soup = BeautifulSoup(page.content,"html.parser")
                # print(soup)
                
            except:
                err = "independent : err : Couldn't fetch " + url 
                err_logs.append(err)
                return 
            all_divs = soup.find_all("a",{"class":"c-card1-textlink -d:b -as:1"})
            for div in all_divs:
                links.append(div["href"])
            #Fetch all the necessary data 
            # print(links)
            final_links = []
            today = date.today()
            for link in links:
                try:
                    try:
                        page = requests.get(link)
                        soup = BeautifulSoup(page.content,"html.parser")
                    # print(soup)
                    # print(link)
                    except:
                        err = "independent : err : Couldn't fetch url " + link 
                        err_logs.append(err)
                        continue

                    #Title of article
                    title.append(soup.find("h1" , {"class" : "title1-main"}).text)
                    #Published Date
                    pub_date.append(soup.find("time" , {"class" :"time1"}).text)
                    # print(pub_date)

                    #Text of article
                    div = soup.find("div" , {"class" : "n-body1"})
                    t = ""
                    for i in div.find_all("p"):
                        t += i.text + " "
                    text.append(t)
                    # print(text)

                    #Scrapped date 
                    scraped_date.append(str(today))

                    #Working links
                    final_links.append(link)
                except:
                    continue
            df = pd.DataFrame({"text":text ,"link":final_links,"publish_date":pub_date,"scraped_date":scraped_date,"title":title})
            if df.empty:
                err = "independent : err: Empty dataframe"
                err_logs.append(err)
            df = df.drop_duplicates(subset=["link"])
            df = FilterFunction(df)
            emptydataframe("independent",df)
            # df  = link_correction(df)
            return df
        except :
            print("independent not working")
            not_working_functions.append('independent')
    def albaniandailynews():
        try:
            print("Albania")
            err_logs = []
            url = "https://www.albaniandailynews.com/search.php?s=ipo"
            domain_url = "https://albaniandailynews.com/"

            headers = {
                "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10.15; rv:78.0) Gecko/20100101 Firefox/78.0"
            }
            page = requests.get(url, headers=headers)
            soup = BeautifulSoup(page.content, "html.parser")
            #soup  # Debugging - if soup is working correctly

            # Class names of the elements to be scraped
            h3_class = "alith_post_title"  # Class name of h3 containing the a tag
            #h1_class = "_1Y-96"
            #h1_div_class = "col-xs-12"
            h3_class_title = "alith_post_title"
            date_span_class = "meta_date"
            para_div_class = "column-1"

            links = []

            for divtag in soup.find_all("h3", {"class": h3_class}):
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
            #links # Debugging - if link array is generated

            collection = []
            scrapper_name = "albaniandailynews"

            for link in links:
                try:
                    l_page = requests.get(link, headers=headers)
                    l_soup = BeautifulSoup(l_page.content, 'html.parser')
                except:
                    err = scrapper_name + ": err: Failed to retrieve data from link: " + link + " and convert it to soup object"
                    err_logs.append(err)
                    continue

                data = []
                # Scraping the heading
                #h1_ele = l_soup.find("h1", {"class": h1_class})
                
                try:
                    h2_ele = l_soup.find("h3", {"class": h3_class_title})
                    data.append(h2_ele.text)
                except:
                    err = scrapper_name + ": err: Failed to find title in page. Link: " + link
                    err_logs.append(err)
                    continue  # drops the complete data if there is an error


                # Adding the link to data
                data.append(link)

                # Scraping the published date
                date_ele = l_soup.find("span", {"class": date_span_class})
                try:
                    date_text = date_ele.text
                    #date_text = (date_text.split('/'))[-1]
                    #date_text = date_text.replace(" Updated: ", "")
                    data.append(date_text)  # The date_text could be further modified to represent a proper date format
                except:
                    err = scrapper_name + ": err: Failed to find date in page. Link: " + link
                    err_logs.append(err)
                    continue  # drops the complete data if there is an error
                
                # Adding the scraped date to data
                cur_date = str(datetime.today())
                data.append(cur_date)
                

                # Scraping the paragraph
                para_ele = (l_soup.findAll("div", {"class": para_div_class}))[-1]
                try:
                    data.append(para_ele.text)  # Need to make this better
                except:
                    err = scrapper_name + ": err: Failed to find paragraph in page. Link: " + link
                    err_logs.append(err)
                    continue  # drops the complete data if there is an error
                # Adding data to a collection
                collection.append(data)

            df = pd.DataFrame(collection, columns =['title', 'link','publish_date','scraped_date','text'])
            if df.empty:
                err = scrapper_name + ": err: Empty dataframe"
                err_logs.append(err)
            #print(df) # For debugging. To check if df is created
            #print(err_logs) # For debugging - to check if any errors occoured
            df = FilterFunction(df)
            emptydataframe("Albania daily news",df)
            log_errors(err_logs)
            # df  = link_correction(df)
            return df
        except:
            print("Albaniadailynews not working")
            not_working_functions.append("Albania")
    def ewn():
        try:
            print("EWN")
            err_logs = []  # Access to view error logs
            url = "https://ewnews.com/?s=ipo"
            domain_url = "https://ewnews.com"

            try:
                page = requests.get(url)
                soup = BeautifulSoup(page.content, "html.parser")
            except:
                err = "err: Failed to access main url: " + url + " and convert it to soup object"
                err_logs.append(err)
                return None

            # Class names of the elements to be scraped - change if the website to be scraped changes them
            div_class = "entry-title"
            h1_class = "entry-title"
            date_div_class = "entry-date published"
            para_div_class = "entry-content col-md-12"

            links = []

            for h3 in soup.find_all("h3",{"class":"entry-title"}):
                link = h3.a["href"]
                if link[0] == '/':
                    link = domain_url + link
                links.append(link)

            collection = []

            for link in links:
                try:
                    l_page = requests.get(link)
                    l_soup = BeautifulSoup(l_page.content, 'html.parser')
                except:
                    err = "err: Failed to retrieve data from link: " + link + " and convert it to soup object"
                    err_logs.append(err)
                    continue

                data = []
                # Scraping the heading
                h1_ele = l_soup.find("h1", {"class": h1_class})
                try:
                    data.append(h1_ele.text)
                except:
                    err = "err: Failed to find title in page. Link: " + link
                    err_logs.append(err)
                    continue  # drops the complete data if there is an error

                # Adding the link to data
                data.append(link)

                # Scraping the published date
                date_ele = l_soup.find("span", {"class": date_div_class})
                try:
                    date_text = date_ele.text
                    #date_text = (date_text.split('/'))[-1]
                    #date_text = date_text.replace(" Updated: ", "")
                    data.append(date_text)  # The date_text could be further modified to represent a proper date format

                except:
                    err = "err: Failed to find date in page. Link: " + link
                    err_logs.append(err)
                    continue  # drops the complete data if there is an error

                # Adding the scraped date to data
                cur_date = str(datetime.today())
                data.append(cur_date)

                # Scraping the paragraph
                para_ele = l_soup.find("div", {"class": para_div_class})
                try:
                    data.append(para_ele.text)  # Need to make this better
                except:
                    err = "err: Failed to find paragraph in page. Link: " + link
                    err_logs.append(err)
                    continue  # drops the complete data if there is an error

                # Adding data to the collection
                collection.append(data)

            df = pd.DataFrame(collection, columns =['title', 'link','publish_date','scraped_date','text'])
            if df.empty:
                err = "err: Empty dataframe"
                err_logs.append(err)
            df = FilterFunction(df)
            emptydataframe("EWN",df)
            log_errors(err_logs)
            # df  = link_correction(df)
            return df
        except:
            print("EWN not working")
            not_working_functions.append("Ewn")
    def bloombergquint():
        try:
            print("Bloombergquint")
            err_logs = []  # Access to view error logs
            keywords = ["ipo","pre-ipo","pre ipo","listing"]
            url = "https://www.bloombergquint.com/search?q="
            domain_url = "https://www.bloombergquint.com"
            links = []
            pub_date = []
            scraped_date = []
            title = []
            text = []
            for keyword in keywords:
                try:
                    page = requests.get(url+keyword)
                    soup = BeautifulSoup(page.content, "html.parser")
                except:
                    err = "Bllomberg quint: err: Failed to access main url: " + url + keyword + " and convert it to soup object"
                    err_logs.append(err)
                    return None
                for a in soup.find_all("a",{"class":"list-story-m__item__link__2mfId"}):
                    links.append(a["href"])
            today = date.today()
            final_links = []
            for link in links:
                try:
                    # if(link.startswith("/")):
                    link = domain_url + link
                    try:
                        print(link)
                        page = requests.get(link)
                        soup = BeautifulSoup(page.content,"html.parser")
                    except:
                        err = "Bloomberg Quint: err: Failed to access main url: " + link + " and convert it to soup object"
                        err_logs.append(err)
                    # return None
                    pub_date.append(soup.find("time",{"class":"desktop-only published-info-module__updated-on__2JWey"}).string)
                    title.append(soup.find("h1",{"class":"story-base-template-m__story-headline__2cNwS"}).text)
                    t = [ i.text for i in soup.find_all("div",{"class":"story-element story-element-text"})]
                    text.append(" ".join(t))
                    scraped_date.append(today)
                    final_links.append(link)
                except:
                    err = "Bloomberg Quint : err: None type object found for " + link 
                    err_logs.append(err)
                    continue


            # print(len(pub_date),len(scraped_date),len(title),len(links),len(text))
            df = pd.DataFrame({"text":text,"link":final_links,"publish_date":pub_date,"scraped_date":scraped_date,"title":title})
            if df.empty:
                err = "Bloomberg Quint: err: Empty dataframe"
                err_logs.append(err)
            df = df.drop_duplicates(subset=["link"])
            df = FilterFunction(df)
            log_errors(err_logs)
            # df  = link_correction(df)
            return df
        except:
            print("Bloombergquint not working")
            not_working_functions.append("Bloombergquint")
    def ecns():
        try:
            print("ECNS")
            err_logs = []
            baseSearchUrl = "http://www.ecns.cn/rss/rss.xml"
            scrapedData = {}
            links = []
            titles = []
            err_index = []
            ArticleDates = []
            ScrapeDates = []
            ArticleBody = []
            queryUrl = baseSearchUrl
            try:
                pageSource = requests.get(baseSearchUrl)
            except:
                err = "ecns: err: Failed to access search url: " + queryUrl + " and convert it to soup object"
                err_logs.append(err)
                exit()
            # with open("response.xml", "wb") as f:
            #     f.write(pageSource.content)
            # break
            parsedSource = BeautifulSoup(pageSource.content, "xml")
            for eachItem in parsedSource.find_all("item"):
                currentArticleTitle = eachItem.find("title").text
                currentArticleLink = eachItem.find("link").text
                currentArticleDate = datetime.strptime(str(eachItem.find("pubDate").text).split("GMT", maxsplit=2)[0].strip(),
                                                    "%Y-%m-%d %H:%M:%S").strftime("%d-%m-%Y")
                # articleText = str(eachItem.find("description").text).split("CDATA[ ", maxsplit=2)[1].rstrip(" ]]")
                articleText = str(eachItem.find("description").text).split("CDATA[ ", maxsplit=2)[0].replace("#039;", "")
                ArticleBody.append(articleText)

                titles.append(currentArticleTitle)
                links.append(currentArticleLink)
                ArticleDates.append(currentArticleDate)
                ScrapeDates.append(datetime.today().strftime("%d-%m-%Y"))
            scrapedData["title"] = titles
            scrapedData["link"] = links
            scrapedData["publish_date"] = ArticleDates
            scrapedData["scraped_date"] = ScrapeDates
            scrapedData["text"] = ArticleBody
            print(scrapedData)
            # DataFrame creation
            ecnsDF = pd.DataFrame(scrapedData)
            ecnsDF = ecnsDF.drop_duplicates(subset=["link"])
            if ecnsDF.empty:
                err = "ecns: err: Empty dataframe"
                err_logs.append(err)
            df = FilterFunction(ecnsDF)
            # emptydataframe("ECNS Canada",df)
            # log_errors(err_logs)
            # df  = link_correction(df)
            return df
        except:
            print("ECNS canada not working")
            not_working_functions.append("ECNS")
    def energy_voice():
        try :
            print("energy voice")
            err_logs = []
            url = "https://www.energyvoice.com/?s=ipo"
            domain_url = "https://www.energyvoice.com"
            title,links,text,pub_date,scraped_date = [],[],[],[],[]
            try:
                page = requests.get(url)
                soup = BeautifulSoup(page.content,"html.parser")
                # print(soup)
                
            except:
                err = "energy voice : err : Couldn't fetch " + url 
                err_logs.append(err)
                return 
            all_divs = soup.find_all("h2",{"class":"title title--sm"})
            for div in all_divs:
                links.append(div.a["href"])
            #Fetch all the necessary data 
            # print(links)
            final_links = []
            today = date.today()
            for link in links:
                try:
                    page = requests.get(link)
                    soup = BeautifulSoup(page.content,"html.parser")
                # print("hi")
                # print(soup)
                # print(link)
                except:
                    err = "energy voice : err : Couldn't fetch url " + link 
                    err_logs.append(err)
                    continue

                #Title of article

                title.append(soup.find("h1" , {"class" : "title entry-title"}).text)
                # print(title)
                #Published Date
                pub_date.append(soup.find("span" , {"class" :"post-timestamp__published"}).text)
                # print(pub_date)

                #Text of article
                div = soup.find("div" , {"class" : "cms clearfix"})
                t = ""
                for i in div.find_all("p"):
                    t += i.text + " "
                text.append(t)
                # print(text)

                #Scrapped date 
                scraped_date.append(str(today))

                #Working links
                final_links.append(link)
            df = pd.DataFrame({"text":text,"link":final_links,"publish_date":pub_date,"scraped_date":scraped_date,"title":title})
            if df.empty:
                err = "energy voice : err: Empty datenergy voiceame"
                err_logs.append(err)
            df = df.drop_duplicates(subset=["link"])
            df = FilterFunction(df)
            emptydataframe("energy voice",df)
            # df  = link_correction(df)
            return df
        except :
            print("energy voice not working")
            not_working_functions.append('energy voice')
    def euroNews():
        try:
            print("Euronews")
            err_logs = []
            err_index = []
            ArticleDates = []
            ScrapeDates = []
            ArticleBody = []
            baseSearchUrl = "https://www.euronews.com/search?query=ipo"
            domainUrl = "https://www.euronews.com"

            scrapedData = {}
            links = []
            titles = []
            queryUrl = baseSearchUrl
            try:
                headers = {
                    'User-Agent': "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 Chrome/58.0.3029.110 Safari/537.36"}
                pageSource = requests.get(queryUrl, headers=headers)
            except:
                err = "euroNews: err: Failed to access search url: " + queryUrl + " and convert it to soup object"
                err_logs.append(err)
            # with open("response.html", "wb") as f:
            #     f.write(pageSource.content)
            parsedSource = BeautifulSoup(pageSource.content, "html.parser", from_encoding="iso-8859-1")
            # if parsedSource.find("div", class_="fpj_bignews"):
            #     bigNews = parsedSource.find("div", class_="fpj_bignews")
            #     currentArticleTitle = bigNews.find("h3").text
            #     titles.append(currentArticleTitle)
            #     currentArticleLink = bigNews.find("a")["href"]
            #     links.append(currentArticleLink)
            #     sourceDateTime = datetime.strptime(bigNews.find("span", class_="dateTime").text, "%d %B %Y, %I:%M %p").strftime(
            #         "%d-%m-%Y")
            #     ArticleDates.append(sourceDateTime)
            #     ScrapeDates.append(datetime.today().strftime("%d-%m-%Y"))

            for item in parsedSource.find("div", class_="o-block-listing__content").find_all("article"):
                requiredTag = item.find("h3").find("a")
                currentArticleTitle = requiredTag["title"]
                # print(currentArticleTitle)
                currentArticleLink = requiredTag["href"]
                # print(currentArticleLink)
                if currentArticleLink[0] == "/":
                    links.append(domainUrl + currentArticleLink)
                else:
                    links.append(currentArticleLink)
                titles.append(currentArticleTitle)
                sourceDateTime = datetime.strptime(item.find("time", class_="c-article-date").text.strip(), "%d/%m/%Y").strftime(
                    "%d-%m-%Y")
                ArticleDates.append(sourceDateTime)
                ScrapeDates.append(datetime.today().strftime("%d-%m-%Y"))

            scrapedData["title"] = titles
            scrapedData["link"] = links
            scrapedData["publish_date"] = ArticleDates
            scrapedData["scraped_date"] = ScrapeDates
            # print(len(titles), titles)
            # print(len(links), links)
            # print(len(ArticleDates), ArticleDates)

            # Article's date and description scraping
            for link in links:
                articleText = ""
                try:
                    pageSource = requests.get(link, headers=headers)
                    parsedSource = BeautifulSoup(pageSource.content, "html.parser", from_encoding="iso-8859-1")
                except:
                    err = "euroNews: err: Failed to access article link : " + link
                    ArticleDates.append("Error")
                    err_logs.append(err)
                    err_index.append(link)
                    continue
                # with open("response.html", "wb") as f:
                #     f.write(pageSource.content)
                # break
                requiredTag = parsedSource.find("div", class_="c-article__full_article")
                if requiredTag:
                    for item in requiredTag.find_all("p"):
                        articleText += item.text.strip()
                    # print(articleText)
                    ArticleBody.append(articleText)
                else:
                    articleText = titles[links.index(link)]
                    ArticleBody.append(articleText)

            scrapedData["text"] = ArticleBody
            # print(len(ArticleBody), ArticleBody)

            # Clean and Normalize links
            if len(err_index) != 0:
                for e in err_index:
                    idx = scrapedData["link"].index(e)
                    scrapedData["link"].pop(idx)
                    scrapedData["title"].pop(idx)
                    scrapedData["publish_date"].pop(idx)

            # DataFrame creation
            euroNewsDF = pd.DataFrame(scrapedData)
            euroNewsDF = euroNewsDF.drop_duplicates(subset=["link"])
            if euroNewsDF.empty:
                err = "euroNews: err: Empty dataframe"
                err_logs.append(err)
            df = FilterFunction(euroNewsDF)
            emptydataframe("Euro news",df)
            # df  = link_correction(df)
            return df
        except:
            print("Euronews not working")
            not_working_functions.append("Euro news europe")
    
    import requests

    def theFreePressJournal():
            try:
                print("The free press journal")
                err_logs = []
                err_index = []
                ArticleDates = []
                ScrapeDates = []
                ArticleBody = []
                baseSearchUrl = "https://www.freepressjournal.in/search?q=ipo"
                domainUrl = "https://www.freepressjournal.in"

                scrapedData = {}
                links = []
                titles = []
                queryUrl = baseSearchUrl
                try:
                    headers = {
                        'User-Agent': "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 Chrome/58.0.3029.110 Safari/537.36"}
                    pageSource = requests.get(queryUrl, headers=headers)
                except:
                    err = "theFreePressJournal: err: Failed to access search url: " + queryUrl + " and convert it to soup object"
                    err_logs.append(err)
                # with open("response.html", "wb") as f:
                #     f.write(pageSource.content)
                parsedSource = BeautifulSoup(pageSource.content, "html.parser", from_encoding="iso-8859-1")
                if parsedSource.find("div", class_="fpj_bignews"):
                    bigNews = parsedSource.find("div", class_="fpj_bignews")
                    currentArticleTitle = bigNews.find("h3").text
                    titles.append(currentArticleTitle)
                    currentArticleLink = bigNews.find("a")["href"]
                    links.append(currentArticleLink)
                    sourceDateTime = datetime.strptime(bigNews.find("span", class_="dateTime").text, "%d %B %Y, %I:%M %p").strftime(
                        "%d-%m-%Y")
                    ArticleDates.append(sourceDateTime)
                    ScrapeDates.append(datetime.today().strftime("%d-%m-%Y"))

                for item in parsedSource.find("div", class_="fpj_newList").find_all("li"):
                    requiredTag = item.find("span", class_="fpj_title")
                    currentArticleTitle = requiredTag.text
                    # print(currentArticleTitle)
                    currentArticleLink = item.find("a")["href"]
                    # print(currentArticleLink)
                    if currentArticleLink[0] == "/":
                        links.append(domainUrl + currentArticleLink)
                    else:
                        links.append(currentArticleLink)
                    titles.append(currentArticleTitle)
                    sourceDateTime = datetime.strptime(item.find("i", class_="dateTime").text, "%d %B %Y, %I:%M %p").strftime(
                        "%d-%m-%Y")
                    ArticleDates.append(sourceDateTime)
                    ScrapeDates.append(datetime.today().strftime("%d-%m-%Y"))

                for item in parsedSource.find("div", class_="fpj_lsh").find_all("li"):
                    requiredTag = item.find("h3")
                    currentArticleTitle = requiredTag.text
                    # print(currentArticleTitle)
                    currentArticleLink = item.find("a")["href"]
                    # print(currentArticleLink)
                    if currentArticleLink[0] == "/":
                        links.append(domainUrl + currentArticleLink)
                    else:
                        links.append(currentArticleLink)
                    titles.append(currentArticleTitle)
                    sourceDateTime = datetime.strptime(item.find("span", class_="dateTime").text, "%d %B %Y, %I:%M %p").strftime(
                        "%d-%m-%Y")
                    ArticleDates.append(sourceDateTime)
                    ScrapeDates.append(datetime.today().strftime("%d-%m-%Y"))

                scrapedData["title"] = titles
                scrapedData["link"] = links
                scrapedData["publish_date"] = ArticleDates
                scrapedData["scraped_date"] = ScrapeDates
                # print(len(titles), titles)
                # print(len(links), links)
                # print(len(ArticleDates), ArticleDates)

                # Article's date and description scraping
                for link in links:
                    articleText = ""
                    try:
                        pageSource = requests.get(link, headers=headers)
                        parsedSource = BeautifulSoup(pageSource.content, "html.parser", from_encoding="iso-8859-1")
                    except:
                        err = "theFreePressJournal: err: Failed to access article link : " + link
                        ArticleDates.append("Error")
                        err_logs.append(err)
                        err_index.append(link)
                        continue
                    # with open("response.html", "wb") as f:
                    #     f.write(pageSource.content)
                    # break

                    for item in parsedSource.find("article",{"id":"fjp-article"}).find_all("p"):
                        articleText += item.text.strip()
                    # print(articleText)
                    ArticleBody.append(articleText)

                scrapedData["text"] = ArticleBody
                # print(len(ArticleBody), ArticleBody)

                # Clean and Normalize links
                if len(err_index) != 0:
                    for e in err_index:
                        idx = scrapedData["link"].index(e)
                        scrapedData["link"].pop(idx)
                        scrapedData["title"].pop(idx)
                        scrapedData["publish_date"].pop(idx)

                # DataFrame creation
                theFreePressJournalDF = pd.DataFrame(scrapedData)
                theFreePressJournalDF = theFreePressJournalDF.drop_duplicates(subset=["link"])
                if theFreePressJournalDF.empty:
                    err = "theFreePressJournal: err: Empty dataframe"
                    err_logs.append(err)
                df = FilterFunction(theFreePressJournalDF)
                emptydataframe("The free press journal",df)
                # df  = link_correction(df)
                return df
            except:
                print("thefreepressjournal not working")
                not_working_functions.append("Thefreepressjournal")
    def aylien():

        import time
        import aylien_news_api
        from aylien_news_api.rest import ApiException
        from datetime import datetime,date
        from pprint import pprint
        import json
        import pandas as pd
        def setup_alyien_api():
            configuration = aylien_news_api.Configuration()
            # Configure API key authorization: app_id
            configuration.api_key['X-AYLIEN-NewsAPI-Application-ID'] = '6104f1f4'
            # Configure API key authorization: app_key
            configuration.api_key['X-AYLIEN-NewsAPI-Application-Key'] = 'f5ddb80c14739c18cc5e40cd260ba9b1'
            # Defining host is optional and default to https://api.aylien.com/news
            configuration.host = "https://api.aylien.com/news"
            # Create an instance of the API class
            api_instance = aylien_news_api.DefaultApi(aylien_news_api.ApiClient(configuration))
            return api_instance
        def convert_to_dict(stories):
            for index,value in enumerate(stories):
                stories[index] = stories[index].to_dict()
            return stories
        def fetch_news_stories(api_instance, params={}):
            fetched_strories = []
            stories = None 
            while (stories is None or len(stories) > 0) and len(fetched_strories)<1300:
                try:
                    response = api_instance.list_stories(**params)
                except ApiException as e:
                    print("Exception when calling DefaultApi->list_stories: %s\n" % e)
                stories = response.stories
                stories = convert_to_dict(stories)
                params['cursor'] = response.next_page_cursor
                fetched_strories += stories
                print("Fetched %d stories.Total story count so far : %d"%(len(stories),len(fetched_strories)))
                return fetched_strories
        # # Current date with correct format for the API option 
        # today = datetime.now()
        # time = str(today.strftime("%Y-%m-%dT%H:%M:%SZ"))


        params = {
            'text': 'IPO',
            'published_at_start': '2022-05-12T00:00:00Z',
            'published_at_end': '2022-05-13T23:59:00Z',
            'cursor':'*',
            'per_page':50
        }
        api_instance = setup_alyien_api()
        today = datetime.now()
        day = today.strftime("%d")
        month = today.strftime("%m")
        year = today.strftime("%y")
        stories = fetch_news_stories(api_instance,params)
        text = []
        link = []
        pub_date = []
        title = []
        scraped_date = []
        today = str(datetime.now())
        for i in stories:
            text.append(i["body"])
            title.append(i["title"])
            pub_date.append("-".join(str(i["published_at"]).strip().split(" ")[0].split("-")[::-1]))
            link.append(i["links"]["permalink"])
            scraped_date.append(today)

        df = pd.DataFrame({"text":text,"link":link,"publish_date":pub_date,"scraped_date":scraped_date,"title":title})
        return df
    def dw():
        try:
            print("DW")
            err_logs = []
            url = "https://www.dw.com/search/en?searchNavigationId=9097&languageCode=en&origin=gN&item=ipo"
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
            page = requests.get(url, headers=headers)
            soup = BeautifulSoup(page.content, "html.parser")
            #soup  # Debugging - if soup is working correctly

            # Class names of the elements to be scraped
            div_class = "searchResult"  # Class name of div containing the a tag
            #h1_class = "_1Y-96"
            #h1_div_class = "col-xs-12"
            title_h1_class = "" # There exists no title here
            date_ul_class = "smallList"
            para_p_class = "intro"

            links = []

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
            # Remove duplicates
            links = list(set(links))
            #links # Debugging - if link array is generated

            collection = []
            scrapper_name = "dw"

            for link in links:
                try:
                    l_page = requests.get(link, headers=headers)
                    l_soup = BeautifulSoup(l_page.content, 'html.parser')
                except:
                    err = scrapper_name + ": err: Failed to retrieve data from link: " + link + " and convert it to soup object"
                    err_logs.append(err)
                    continue

                data = []
                # Scraping the heading
                #h1_ele = l_soup.find("h1", {"class": h1_class})
                
                try:
                    # title_ele = l_soup.find("h1", {"class": title_h1_class})
                    title_ele = l_soup.find("h1") # There exists only 1 h1 ele in the page
                    data.append(title_ele.text)
                except:
                    err = scrapper_name + ": err: Failed to find title in page. Link: " + link
                    err_logs.append(err)
                    continue  # drops the complete data if there is an error


                # Adding the link to data
                data.append(link)

                # Scraping the published date
                try:
                    date_ele_container = l_soup.find("ul", {"class": date_ul_class})
                    date_text =  date_ele_container.text.split("\n")[2]
                    #date_text = (date_text.split('/'))[-1]
                    #date_text = date_text.replace(" Updated: ", "")
                    data.append(date_text.replace(".","-").strip())  # The date_text could be further modified to represent a proper date format
                except:
                    err = scrapper_name + ": err: Failed to find date in page. Link: " + link
                    err_logs.append(err)
                    continue  # drops the complete data if there is an error
                
                # Adding the scraped date to data
                cur_date = str(datetime.today())
                data.append(cur_date)
                

                # Scraping the paragraph
                try:
                    para_ele = (l_soup.findAll("p", {"class": para_p_class}))[-1]
                    data.append(para_ele.text)  # Need to make this better
                except:
                    err = scrapper_name + ": err: Failed to find paragraph in page. Link: " + link
                    err_logs.append(err)
                    continue  # drops the complete data if there is an error
                # Adding data to a collection
                collection.append(data)
            print(collection)
            df = pd.DataFrame(collection, columns =['title', 'link','publish_date','scraped_date','text'])
            if df.empty:
                err = scrapper_name + ": err: Empty dataframe"
                err_logs.append(err)
            #print(df) # For debugging. To check if df is created
            #print(err_logs) # For debugging - to check if any errors occoured
            df = FilterFunction(df)
            emptydataframe("DW",df)
            # df  = link_correction(df)
            return df
        except:
            not_working_functions.append("DW")
            print("DW not working")
    def thehindubusinessline():
        try:
            print("Hindubusinessline")
            err_logs = []
            url = "https://www.thehindubusinessline.com/search/?q=ipo&pd=pastweek&type=story&type=storyline&sort=newest"
            domain_url = "https://www.thehindubusinessline.com/"

            headers = {
                "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10.15; rv:78.0) Gecko/20100101 Firefox/78.0",
                "accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.9",
                'sec-fetch-site': 'none',
                'sec-fetch-mode': 'navigate',
                'sec-fetch-user': '?1',
                'sec-fetch-dest': 'document',
                'accept-language': 'en-GB,en-US;q=0.9,en;q=0.8',
            }
            page = requests.get(url, headers=headers)
            soup = BeautifulSoup(page.content, "html.parser")
            #soup  # Debugging - if soup is working correctly

            # Class names of the elements to be scraped
            div_class = "searchPage"  # Class name of div containing the a tag
            #h1_class = "_1Y-96"
            #h1_div_class = "col-xs-12"
            title_h1_class = "tp-title-inf"
            date_span_class = "update-time"
            para_div_class = "contentbody"

            links = []

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
            #links # Debugging - if link array is generated

            collection = []
            scrapper_name = "thehindubusinessline"

            for link in links:
                try:
                    l_page = requests.get(link)
                    l_soup = BeautifulSoup(l_page.content, 'html.parser')
                except:
                    err = scrapper_name + ": err: Failed to retrieve data from link: " + link + " and convert it to soup object"
                    err_logs.append(err)
                    continue

                data = []
                # Scraping the heading
                #h1_ele = l_soup.find("h1", {"class": h1_class})

                try:
                    title_ele = l_soup.find("h1", {"class": title_h1_class})
                    data.append(title_ele.text)
                except:
                    err = scrapper_name + ": err: Failed to find title in page. Link: " + link
                    err_logs.append(err)
                    continue  # drops the complete data if there is an error


                # Adding the link to data
                data.append(link)

                # Scraping the published date
                date_ele = l_soup.find("span", {"class": date_span_class})
                try:
                    date_text = date_ele.text
                    date_text = (date_text.split('\n'))[-2]
                    #date_text = date_text.replace(" Updated: ", "")
                    data.append(date_text)  # The date_text could be further modified to represent a proper date format
                except:
                    err = scrapper_name + ": err: Failed to find date in page. Link: " + link
                    err_logs.append(err)
                    continue  # drops the complete data if there is an error

                # Adding the scraped date to data
                cur_date = str(datetime.today())
                data.append(cur_date)


                # Scraping the paragraph
                try:
                    para_ele = (l_soup.findAll("div", {"class": para_div_class}))[-1]
                    # para_ele = para_ele.strip("\n")
                    data.append(para_ele.text)  # Need to make this better
                except:
                    err = scrapper_name + ": err: Failed to find paragraph in page. Link: " + link
                    err_logs.append(err)
                    continue  # drops the complete data if there is an error
                # Adding data to a collection
                collection.append(data)

            df = pd.DataFrame(collection, columns =['title', 'link','publish_date','scraped_date','text'])
            if df.empty:
                err = scrapper_name + ": err: Empty dataframe"
                err_logs.append(err)
            #print(df) # For debugging. To check if df is created
            #print(err_logs) # For debugging - to check if any errors occoured
            df = FilterFunction(df)
            emptydataframe("Hundustanbusinessline",df)
            return df
        except:
            print("Hindubusinessline")
            not_working_functions.append("Hindubusinessline")
    # def kedgsel():
    #     driver = webdriver.Chrome()
    #     err_logs = []
    #     title, links, text, pub_date, scraped_date = [], [], [], [], []
    #     #url for each year
    #     url = "https://www.kedglobal.com/newsSearch?keyword=IPO"
    #     domain_url = "https://www.kedglobal.com"
    #     driver.get(url)

    #     #wait till DOM is loaded
    #     try:
    #         element = WebDriverWait(driver, 20).until(EC.presence_of_element_located((By.CLASS_NAME, "tit")))
            
    #     except:
    #         err = "kedg : err : Couldn't fetch " + url
    #         err_logs.append(err)
    #         return

    #     #extract page source
    #     links = []
    #     element = driver.page_source
    #     print(element)
    #     soup = BeautifulSoup(element, "html.parser")
    #     all_divs = soup.find("ul", {"class": "list_news hfix type02"}).find_all("li")
        
    #     for div in all_divs:
    #         try:
    #             links.append(domain_url + div.find("div",{"class":"box"}).a["href"])
    #             pub_date.append(div.find("p", {"class": "update_time"}).text)
    #         except:
    #             continue

    #     #   print(links)
    #     #print(len(links))
    #     final_links = []
    #     today = date.today()
    #     #   today = str(today.strftime("%d-%m-%Y"))
    #     for link in links:
    #         try:
    #             page = driver.get(link)
    #             content = driver.page_source
    #             soup = BeautifulSoup(content, "html.parser")
    #             #print(soup)
    #             #print(link)
    #         except:
    #             err = "kedg : err : Couldn't fetch url " + link
    #             err_logs.append(err)
    #             continue
    #         #Title of article
    #         try:
    #             t = soup.find("div", {"class": "cont"}).text
    #             #Text of article
    #             text.append(t)
    #             #print(text)

    #         except:
    #             continue
            
    #         title.append(soup.find("h1", {"class": "tit"}).text.strip())

    #         scraped_date.append(str(today))
    #         final_links.append(link)
    #         #print(title)
    #         #print(pub_date)
    #         #print(scraped_date)
    #         #print(text)
    #     #print(len(text),len(links),len(pub_date),len(scraped_date),len(title))
    #     df = pd.DataFrame({"text": text, "link": final_links,
    #                         "publish_date": pub_date, "scraped_date": scraped_date, "title": title})
    #     if df.empty:
    #         err = "kedg : err: Empty datframe"
    #         err_logs.append(err)
    #     df = df.drop_duplicates(subset=["link"])
    #     #df = FilterFunction(df)
    #     #emptydataframe("channelnewsasia",df)
    #     df.to_csv("data.csv")
    #     return df
    def albawaba():
        try:
            print("Albawaba")
            url = "https://www.albawaba.com/search?keyword=IPO&sort_by=created"
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
            page = requests.get(url, headers=headers)
            soup = BeautifulSoup(page.content, "html.parser")
            #soup  # Debugging - if soup is working correctly

            # Class names of the elements to be scraped
            div_class = "body-container"  # Class name of div containing the a tag
            #h1_class = "_1Y-96"
            #h1_div_class = "col-xs-12"
            title_h1_class = "page-header"
            date_section_class = ["block-field-blocknodearticlecreated", "block-entity-fieldnodecreated"]
            para_section_class = ["block-field-blocknodearticlebody", "block-field-blocknodepagebody"]

            links = []

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
            #links # Debugging - if link array is generated

            collection = []
            err_logs = []
            scrapper_name = "albawaba"

            for link in links:
                try:
                    l_page = requests.get(link)
                    l_soup = BeautifulSoup(l_page.content, 'html.parser')
                except:
                    err = scrapper_name + ": err: Failed to retrieve data from link: " + link + " and convert it to soup object"
                    err_logs.append(err)
                    continue

                data = []
                # Scraping the heading
                #h1_ele = l_soup.find("h1", {"class": h1_class})
                
                try:
                    title_ele = l_soup.find("h1", {"class": title_h1_class})
                    data.append(title_ele.text)
                except:
                    err = scrapper_name + ": err: Failed to find title in page. Link: " + link
                    err_logs.append(err)
                    continue  # drops the complete data if there is an error


                # Adding the link to data
                data.append(link)

                # Scraping the published date
                date_ele = l_soup.find("section", {"class": date_section_class})
                try:
                    date_text = date_ele.text
                    # date_text = (date_text.split('\n'))[-2]
                    #date_text = date_text.replace(" Updated: ", "")
                    data.append(date_text)  # The date_text could be further modified to represent a proper date format
                except:
                    err = scrapper_name + ": err: Failed to find date in page. Link: " + link
                    err_logs.append(err)
                    continue  # drops the complete data if there is an error
                
                # Adding the scraped date to data
                cur_date = str(datetime.today())
                data.append(cur_date)
                

                # Scraping the paragraph
                try:
                    para_ele = (l_soup.findAll("section", {"class": para_section_class}))[-1]
                    # para_ele = para_ele.strip("\n")
                    data.append(para_ele.text)  # Need to make this better
                except:
                    err = scrapper_name + ": err: Failed to find paragraph in page. Link: " + link
                    err_logs.append(err)
                    continue  # drops the complete data if there is an error
                # Adding data to a collection
                collection.append(data)

            df = pd.DataFrame(collection, columns =['title', 'link','publish_date','scraped_date','text'])
            if df.empty:
                err = scrapper_name + ": err: Empty dataframe"
                err_logs.append(err)
            #print(df) # For debugging. To check if df is created
            #print(err_logs) # For debugging - to check if any errors occoured
            df = FilterFunction(df)
            emptydataframe("Albawaba",df)
            # log_errors(err_logs)
            return df
        except:
            print("Albawaba not working")
            not_working_functions.append("Albawaba")
    def fr():
        try:
            print("Fr german")
            url = "https://www.fr.de/suche/?tt=1&tx=&sb=&td=&fd=&qr=ipo"
            domain_url = "https://www.fr.de/"

            headers = {
                "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10.15; rv:78.0) Gecko/20100101 Firefox/78.0",
                "accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.9",
                'sec-fetch-site': 'none',
                'sec-fetch-mode': 'navigate',
                'sec-fetch-user': '?1',
                'sec-fetch-dest': 'document',
                'accept-language': 'en-GB,en-US;q=0.9,en;q=0.8',
            }
            page = requests.get(url, headers=headers)
            soup = BeautifulSoup(page.content, "html.parser")
            # print(soup)  # Debugging - if soup is working correctly

            # Class names of the elements to be scraped
            div_class = "id-LB-e--XS12_0c "  # Class name of div containing the a tag
            #h1_class = "_1Y-96"
            #h1_div_class = "col-xs-12"
            title_h1_class = "id-StoryElement-headline"
            date_span_class = "id-StoryElement-timestamp-published"
            para_p_class = "id-StoryElement-paragraph"

            links = []

            for divtag in soup.find_all("div", {"class": div_class}):
                for a in divtag.find_all("a", href=True):
                    link = a["href"]  # Gets the link
                    
                    # Checking the link if it is a relative link
                    # if link[0] == '/':
                    #   link = domain_url + link
                    
                    # # Filtering advertaisment links
                    # link_start = domain_url 
                    # if link.startswith(link_start):
                    #   links.append(link)
                    link = "https:" + link
                    links.append(link)
            # Remove duplicates
            links = list(set(links))
            # print(links) # Debugging - if link array is generated

            collection = []
            err_logs = []
            scrapper_name = "fr"

            for link in links:
                try:
                    l_page = requests.get(link, headers)
                    l_soup = BeautifulSoup(l_page.content, 'html.parser')
                except:
                    err = scrapper_name + ": err: Failed to retrieve data from link: " + link + " and convert it to soup object"
                    err_logs.append(err)
                    continue

                data = []
                # Scraping the heading
                #h1_ele = l_soup.find("h1", {"class": h1_class})
                
                try:
                    title_ele = l_soup.find("h1", {"class": title_h1_class})
                    data.append(title_ele.text)
                except:
                    err = scrapper_name + ": err: Failed to find title in page. Link: " + link
                    err_logs.append(err)
                    continue  # drops the complete data if there is an error


                # Adding the link to data
                data.append(link)

                # Scraping the published date
                try:
                    date_ele = l_soup.find("span", {"class": date_span_class})
                    date_text = date_ele.text
                    date_text = (date_text.split())[1]
                    #date_text = date_text.replace(" Updated: ", "")
                    data.append(date_text)  # The date_text could be further modified to represent a proper date format
                except:
                    err = scrapper_name + ": err: Failed to find date in page. Link: " + link
                    err_logs.append(err)
                    continue  # drops the complete data if there is an error
                
                # Adding the scraped date to data
                cur_date = str(datetime.today())
                data.append(cur_date)
                

                # Scraping the paragraph
                try:
                    # para_ele = (l_soup.findAll("p", {"class": para_p_class}))[-1]
                    para_text = ""
                    for para_ele in l_soup.findAll("p", {"class": para_p_class}):
                        para_text += para_ele.text
                    # para_ele = para_ele.strip("\n")
                    data.append(para_text)  # Need to make this better
                except:
                    err = scrapper_name + ": err: Failed to find paragraph in page. Link: " + link
                    err_logs.append(err)
                    continue  # drops the complete data if there is an error
                # Adding data to a collection
                collection.append(data)

            df = pd.DataFrame(collection, columns =['title', 'link','publish_date','scraped_date','text'])
            if df.empty:
                err = scrapper_name + ": err: Empty dataframe"
                err_logs.append(err)
            # print(df) # For debugging. To check if df is created
            # print(err_logs) # For debugging - to check if any errors occoured
            df = FilterFunction(df)
            emptydataframe("Fr",df)
            return df
        except:
            print("Fr not working")
            not_working_functions.append("Fr")
    def astanatimes():
        try:
            print("Astanatimes")
            url = "https://astanatimes.com/?s=ipo"
            domain_url = "https://astanatimes.com/"

            headers = {
                "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10.15; rv:78.0) Gecko/20100101 Firefox/78.0",
                "accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.9",
                'sec-fetch-site': 'none',
                'sec-fetch-mode': 'navigate',
                'sec-fetch-user': '?1',
                'sec-fetch-dest': 'document',
                'accept-language': 'en-GB,en-US;q=0.9,en;q=0.8',
            }
            page = requests.get(url, headers=headers)
            soup = BeautifulSoup(page.content, "html.parser")
            # soup  # Debugging - if soup is working correctly

            # Class names of the elements to be scraped
            div_class = "search-result"  # Class name of div containing the a tag
            #h1_class = "_1Y-96"
            #h1_div_class = "col-xs-12"
            title_div_class = "eight columns"
            date_p_class = ["byline"]
            para_div_class = ["post"]

            links = []

            for divtag in soup.find_all("div", {"class": div_class}):
                for h4_ele in divtag.find_all("h4"):
                    for a in h4_ele.find_all("a", href=True):
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
            # links # Debugging - if link array is generated

            collection = []
            err_logs = []
            scrapper_name = "astanatimes"

            for link in links:
                try:
                    l_page = requests.get(link, headers)
                    l_soup = BeautifulSoup(l_page.content, 'html.parser')
                except:
                    err = scrapper_name + ": err: Failed to retrieve data from link: " + link + " and convert it to soup object"
                    err_logs.append(err)
                    continue

                data = []
                # Scraping the heading
                #h1_ele = l_soup.find("h1", {"class": h1_class})
                
                try:
                    # title_ele = l_soup.find("div", {"class": title_div_class})
                    title_ele_container = l_soup.find("div", {"class": title_div_class})
                    title_ele = (title_ele_container.find_all("h1"))[0]
                    data.append(title_ele.text)
                except:
                    err = scrapper_name + ": err: Failed to find title in page. Link: " + link
                    err_logs.append(err)
                    continue  # drops the complete data if there is an error


                # Adding the link to data
                data.append(link)

                # Scraping the published date
                try:
                    date_ele = l_soup.find("p", {"class": date_p_class})
                    date_text = date_ele.text
                    date_text = " ".join(((date_text.strip()).split())[-3:])
                    #date_text = date_text.replace(" Updated: ", "")
                    data.append(date_text)  # The date_text could be further modified to represent a proper date format
                except:
                    err = scrapper_name + ": err: Failed to find date in page. Link: " + link
                    err_logs.append(err)
                    continue  # drops the complete data if there is an error
                
                # Adding the scraped date to data
                cur_date = str(datetime.today())
                data.append(cur_date)
                

                # Scraping the paragraph
                try:
                    para_ele = (l_soup.findAll("div", {"class": para_div_class}))[0]
                    # para_ele = para_ele.strip("\n")
                    data.append(para_ele.text)  # Need to make this better
                    # print(para_ele.text)
                except:
                    err = scrapper_name + ": err: Failed to find paragraph in page. Link: " + link
                    err_logs.append(err)
                    continue  # drops the complete data if there is an error
                # Adding data to a collection
                collection.append(data)

            df = pd.DataFrame(collection, columns =['title', 'link','publish_date','scraped_date','text'])
            if df.empty:
                err = scrapper_name + ": err: Empty dataframe"
                err_logs.append(err)
            # print(df) # For debugging. To check if df is created
            # print(err_logs) # For debugging - to check if any errors occoured
            df = FilterFunction(df)
            emptydataframe("Astanatimes",df)
            return df
        except:
            print("Astanatimes not working")
            not_working_functions.append("Astanatimes")
    def bankokpost():
        try:
            print("Bankokpost")
            url = "https://search.bangkokpost.com/search/result?category=all&&q=ipo"
            domain_url = "https://www.bangkokpost.com/"

            headers = {
                "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10.15; rv:78.0) Gecko/20100101 Firefox/78.0",
                "accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.9",
                'sec-fetch-site': 'none',
                'sec-fetch-mode': 'navigate',
                'sec-fetch-user': '?1',
                'sec-fetch-dest': 'document',
                'accept-language': 'en-GB,en-US;q=0.9,en;q=0.8',
            }
            page = requests.get(url, headers=headers)
            soup = BeautifulSoup(page.content, "html.parser")
            # soup  # Debugging - if soup is working correctly

            # Class names of the elements to be scraped
            div_class = "detail"  # Class name of div containing the a tag
            #h1_class = "_1Y-96"
            #h1_div_class = "col-xs-12"
            title_div_class = "article-headline"
            date_div_class = ["col-15 col-md"]
            para_div_class = ["articl-content"]

            links = []

            for divtag in soup.find_all("div", {"class": div_class}):
                for a in ((divtag.find_all("h3"))[0]).find_all("a", href=True):
                    link = a["href"]  # Gets the link
                    link = link.split("?href=")[-1]
                    link = "/".join(link.split("%2F"))
                    link = ":".join(link.split("%3A"))
                    link = link.split("&")[0]
                    links.append(link)
            # Remove duplicates
            links = list(set(links))
            # links # Debugging - if link array is generated

            collection = []
            err_logs = []
            scrapper_name = "albawaba"

            for link in links:
                try:
                    l_page = requests.get(link)
                    l_soup = BeautifulSoup(l_page.content, 'html.parser')
                except:
                    err = scrapper_name + ": err: Failed to retrieve data from link: " + link + " and convert it to soup object"
                    err_logs.append(err)
                    continue

                data = []
                # Scraping the heading
                #h1_ele = l_soup.find("h1", {"class": h1_class})
                
                try:
                    title_ele = (l_soup.find("div", {"class": title_div_class})).find("h1")
                    text = title_ele.text
                    text = text.strip("\n")
                    text = text.strip("\t")
                    data.append(text)
                except:
                    err = scrapper_name + ": err: Failed to find title in page. Link: " + link
                    err_logs.append(err)
                    continue  # drops the complete data if there is an error


                # Adding the link to data
                data.append(link)

                # Scraping the published date
                try:
                    date_ele = l_soup.find("div", {"class": date_div_class})
                    date_text = date_ele.text
                    date_text = date_text.split(":")[1]
                    date_text = date_text.strip("\n")
                    date_text = date_text.strip("\t")
                    date_text = " ".join((date_text.split())[:3])
                    #date_text = date_text.replace(" Updated: ", "")
                    data.append(date_text)  # The date_text could be further modified to represent a proper date format
                except:
                    err = scrapper_name + ": err: Failed to find date in page. Link: " + link
                    err_logs.append(err)
                    continue  # drops the complete data if there is an error
                
                # Adding the scraped date to data
                cur_date = str(datetime.today())
                data.append(cur_date)
                

                # Scraping the paragraph
                try:
                    para_ele = (l_soup.findAll("div", {"class": para_div_class}))[-1]
                    para_ele_text = para_ele.text
                    para_ele_text = para_ele_text.strip("\n")
                    para_ele_text = para_ele_text.strip("\t")
                    data.append(para_ele_text)  # Need to make this better
                except:
                    err = scrapper_name + ": err: Failed to find paragraph in page. Link: " + link
                    err_logs.append(err)
                    continue  # drops the complete data if there is an error
                # Adding data to a collection
                collection.append(data)

            df = pd.DataFrame(collection, columns =['title', 'link','publish_date','scraped_date','text'])
            if df.empty:
                err = scrapper_name + ": err: Empty dataframe"
                err_logs.append(err)
            # print(df) # For debugging. To check if df is created
            # print(err_logs) # For debugging - to check if any errors occoured
            df = FilterFunction(df)
            emptydataframe("Bankokpost",df)
            return df
        except:
            print("bankokpost not working")
            not_working_functions.append("Bankokpost")
    def globalnewswire():
        try:
            print("Global news wire")
            source=requests.get("https://www.globenewswire.com/search/keyword/IPO")
            content=BeautifulSoup(source.content, 'html.parser')
            head=content.find("div", style="margin-top: 2.3rem; min-height: 1000px")
            links=["https://www.globenewswire.com"+str(i.a.get('href')) for i in head.find_all('div',{"class":"pagging-list-item-text-container"})]
            list(set(links))
            
            err_links=[]
            title=[]
            published=[]
            scraped=[]
            link=[]
            data=[]
            
            for i in links:
                try:
                    source=requests.get(i)
                    content=BeautifulSoup(source.content, 'html.parser')
                    now=datetime.now()
                    headline=content.find("h1", class_="article-headline")
                    if headline.text in title:
                        continue
                    date=content.find('span', class_="article-published")
                    body=content.find('div', class_="main-scroll-container")
                    text="  ".join([j.text for j in body.find_all("p")])
                    data.append(text)
                    scraped.append(now)
                    published.append(date.time.text)
                    title.append(headline.text)
                    link.append(i)
                except:
                    err_links.append(i)
                    continue
            df = pd.DataFrame({"text":data,"link":link,"publish_date":published,"scraped_date":scraped,"title":title})
            df = FilterFunction(df)
            emptydataframe("Global news wire",df)
            return df
        except:
            print("Globalnewswire not working")
            not_working_functions.append("Globalnewswire")
    def headlinesoftoday():
        try:
            print("Headlinesoftoday")
            source=requests.get("https://www.headlinesoftoday.com/?s=IPO")
            content=BeautifulSoup(source.content, 'html.parser')
            # body=content.find('div', class_="col-sm-8 content-column")
            latest_links=[i.get('href') for i in content.find_all("a",{"class":"post-url post-title"})]
            list(set(latest_links))
            err_links=[]
            title=[]
            published=[]
            scraped=[]
            link=[]
            data=[]
            for i in latest_links:
                try:
                    source=requests.get(i)
                    content=BeautifulSoup(source.content, "html.parser")
                    now=datetime.now()
                    headline=content.find('h1', class_="single-post-title")
                    if headline.span.text in title:
                        continue
                    date=content.find('span', class_="time")
                    body=content.find('div', class_="entry-content clearfix single-post-content")
                    text=" ".join([i.text for i in body.find_all('p')])
                    data.append(text)
                    published.append(date.time.b.text)
                    title.append(headline.span.text)
                    scraped.append(now)
                    link.append(i)
                except:
                        err_links.append(i)
                        continue
            frame = pd.DataFrame({"text":data,"link":link,"publish_date":published,"scraped_date":scraped,"title":title})
            frame = FilterFunction(frame)
            emptydataframe("Headlines of today",frame)
            return frame  
        except:
            print("Headlinesoftoday not working")
            not_working_functions.append("Headlinesoftoday")
    def africabusinessinsider():
        try:
            print("Africa business insider")
            url = "https://africa.businessinsider.com/search?q=ipo"
            domain_url = "https://africa.businessinsider.com/"

            headers = {
                "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10.15; rv:78.0) Gecko/20100101 Firefox/78.0",
                "accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.9",
                'sec-fetch-site': 'none',
                'sec-fetch-mode': 'navigate',
                'sec-fetch-user': '?1',
                'sec-fetch-dest': 'document',
                'accept-language': 'en-GB,en-US;q=0.9,en;q=0.8',
            }
            page = requests.get(url, headers=headers)
            soup = BeautifulSoup(page.content, "html.parser")
            # soup  # Debugging - if soup is working correctly

            # Class names of the elements to be scraped
            div_class = "link"  # Class name of div containing the a tag
            #h1_class = "_1Y-96"
            #h1_div_class = "col-xs-12"
            title_h1_class = "article-headline"
            date_time_class = ["detail-article-date", "date-type-publicationDate"]
            para_div_class = ["article-body-text"]

            links = []

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
            # links # Debugging - if link array is generated
            
            collection = []
            err_logs = []
            scrapper_name = "africabusinessinsider"

            for link in links:
                try:
                    l_page = requests.get(link, headers=headers)
                    l_soup = BeautifulSoup(l_page.content, 'html.parser')
                except:
                    err = scrapper_name + ": err: Failed to retrieve data from link: " + link + " and convert it to soup object"
                    err_logs.append(err)
                    continue

                data = []
                # Scraping the heading
                #h1_ele = l_soup.find("h1", {"class": h1_class})
                
                try:
                    title_ele = l_soup.find("h1", {"class": title_h1_class})
                    title_text = title_ele.text
                    title_text = title_text.strip("\n")
                    title_text = title_text.strip()
                    data.append(title_text)
                except:
                    err = scrapper_name + ": err: Failed to find title in page. Link: " + link
                    err_logs.append(err)
                    continue  # drops the complete data if there is an error


                # Adding the link to data
                data.append(link)

                # Scraping the published date
                try:
                    date_ele = l_soup.find("time", {"class": date_time_class})
                    date_text = date_ele.text
                    date_text = date_text.strip("\n")
                    date_text = date_text.strip()
                    # date_text = (date_text.split('\n'))[-2]
                    #date_text = date_text.replace(" Updated: ", "")
                    data.append(date_text)  # The date_text could be further modified to represent a proper date format
                except:
                    err = scrapper_name + ": err: Failed to find date in page. Link: " + link
                    err_logs.append(err)
                    continue  # drops the complete data if there is an error
                
                # Adding the scraped date to data
                cur_date = str(datetime.today())
                data.append(cur_date)
                

                # Scraping the paragraph
                try:
                    para_ele = (l_soup.findAll("div", {"class": para_div_class}))[-1]
                    para_text = para_ele.text
                    para_text = para_text.strip("\n")
                    para_text = para_text.strip()
                    data.append(para_text)
                except:
                    err = scrapper_name + ": err: Failed to find paragraph in page. Link: " + link
                    err_logs.append(err)
                    continue  # drops the complete data if there is an error
                # Adding data to a collection
                collection.append(data)

            df = pd.DataFrame(collection, columns =['title', 'link','publish_date','scraped_date','text'])
            if df.empty:
                err = scrapper_name + ": err: Empty dataframe"
                err_logs.append(err)
            # print(df) # For debugging. To check if df is created
            # print(err_logs) # For debugging - to check if any errors occoured
            df = FilterFunction(df)
            return df
        except:
            print("Africa business Insider")
            not_working_functions.append("Africa business insider")
    def africanmarkets():
        try:
            print("African Markets")
            url = "https://www.african-markets.com/en/search?searchword=ipo&ordering=newest&searchphrase=all&limit=0"
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
            page = requests.get(url, headers=headers)
            soup = BeautifulSoup(page.content, "html.parser")
            # soup  # Debugging - if soup is working correctly

            # Class names of the elements to be scraped
            dt_class = "result-title"  # Class name of div containing the a tag
            #h1_class = "_1Y-96"
            #h1_div_class = "col-xs-12"
            title_div_class = "page-header"
            date_time_itemprop = ["datePublished"]
            para_div_itemprop = ["articleBody"]

            links = []

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
            # links # Debugging - if link array is generated

            collection = []
            err_logs = []
            scrapper_name = "africanmarkets"

            for link in links:
                try:
                    l_page = requests.get(link, headers=headers)
                    l_soup = BeautifulSoup(l_page.content, 'html.parser')
                except:
                    err = scrapper_name + ": err: Failed to retrieve data from link: " + link + " and convert it to soup object"
                    err_logs.append(err)
                    continue

                data = []
                # Scraping the heading
                #h1_ele = l_soup.find("h1", {"class": h1_class})
                
                try:
                    title_ele = l_soup.find("div", {"class": title_div_class})
                    title_text = title_ele.text
                    title_text = title_text.strip("\n")
                    title_text = title_text.strip()
                    data.append(title_text)
                except:
                    err = scrapper_name + ": err: Failed to find title in page. Link: " + link
                    err_logs.append(err)
                    continue  # drops the complete data if there is an error


                # Adding the link to data
                data.append(link)

                # Scraping the published date
                try:
                    date_ele = l_soup.find("time", {"itemprop": date_time_itemprop})
                    date_text = date_ele.text
                    date_text = date_text.strip("\n")
                    date_text = date_text.strip()
                    date_text = date_text.split("Published:")[-1]
                    # date_text = (date_text.split('\n'))[-2]
                    #date_text = date_text.replace(" Updated: ", "")
                    data.append(date_text)  # The date_text could be further modified to represent a proper date format
                except:
                    err = scrapper_name + ": err: Failed to find date in page. Link: " + link
                    err_logs.append(err)
                    continue  # drops the complete data if there is an error
                
                # Adding the scraped date to data
                cur_date = str(datetime.today())
                data.append(cur_date)
                

                # Scraping the paragraph
                try:
                    para_ele = (l_soup.findAll("div", {"itemprop": para_div_itemprop}))[-1]
                    para_text = para_ele.text
                    para_text = para_text.strip("\n")
                    para_text = para_text.strip()
                    data.append(para_text)
                except:
                    err = scrapper_name + ": err: Failed to find paragraph in page. Link: " + link
                    err_logs.append(err)
                    continue  # drops the complete data if there is an error
                # Adding data to a collection
                collection.append(data)

            df = pd.DataFrame(collection, columns =['title', 'link','publish_date','scraped_date','text'])
            if df.empty:
                err = scrapper_name + ": err: Empty dataframe"
                err_logs.append(err)
            # print(df) # For debugging. To check if df is created
            # print(err_logs) # For debugging - to check if any errors occoured
            df = FilterFunction(df)
            emptydataframe("African markets",df)
            return df
        except:
            print("African Markets not working")
            not_working_functions.append("African markets")
    def globalcapital():
        try:
            print("Global capital")
            url = "https://www.globalcapital.com/search?q=ipo"
            domain_url = "https://www.globalcapital.com/"

            headers = {
                "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10.15; rv:78.0) Gecko/20100101 Firefox/78.0",
                "accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.9",
                'sec-fetch-site': 'none',
                'sec-fetch-mode': 'navigate',
                'sec-fetch-user': '?1',
                'sec-fetch-dest': 'document',
                'accept-language': 'en-GB,en-US;q=0.9,en;q=0.8',
            }
            page = requests.get(url, headers=headers)
            soup = BeautifulSoup(page.content, "html.parser")
            # soup  # Debugging - if soup is working correctly

            # Class names of the elements to be scraped
            div_class = "PromoB-title"  # Class name of div containing the a tag
            #h1_class = "_1Y-96"
            #h1_div_class = "col-xs-12"
            title_h1_class = "ArticlePage-headline"
            date_div_class = ["ArticlePage-datePublished"]
            para_h2_class = ["ArticlePage-subHeadline"]

            links = []

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
            # links # Debugging - if link array is generated

            collection = []
            err_logs = []
            scrapper_name = "globalcapital"

            for link in links:
                try:
                    l_page = requests.get(link, headers=headers)
                    l_soup = BeautifulSoup(l_page.content, 'html.parser')
                except:
                    err = scrapper_name + ": err: Failed to retrieve data from link: " + link + " and convert it to soup object"
                    err_logs.append(err)
                    continue

                data = []
                # Scraping the heading
                #h1_ele = l_soup.find("h1", {"class": h1_class})
                
                try:
                    title_ele = l_soup.find("h1", {"class": title_h1_class})
                    title_text = title_ele.text
                    title_text = title_text.strip("\n ")
                    data.append(title_text)
                except:
                    err = scrapper_name + ": err: Failed to find title in page. Link: " + link
                    err_logs.append(err)
                    continue  # drops the complete data if there is an error


                # Adding the link to data
                data.append(link)

                # Scraping the published date
                try:
                    date_ele = l_soup.find("div", {"class": date_div_class})
                    date_text = date_ele.text
                    date_text = date_text.strip("\n ")
                    date_text = " ".join(date_text.split()[:3])
                    #date_text = date_text.replace(" Updated: ", "")
                    data.append(date_text)  # The date_text could be further modified to represent a proper date format
                except:
                    err = scrapper_name + ": err: Failed to find date in page. Link: " + link
                    err_logs.append(err)
                    continue  # drops the complete data if there is an error
                
                # Adding the scraped date to data
                cur_date = str(datetime.today())
                data.append(cur_date)
                

                # Scraping the paragraph
                try:
                    para_ele = (l_soup.findAll("h2", {"class": para_h2_class}))[-1]
                    para_text = para_ele.text
                    para_text = para_text.strip("\n ")
                    data.append(para_text)  # Need to make this better
                except:
                    err = scrapper_name + ": err: Failed to find paragraph in page. Link: " + link
                    err_logs.append(err)
                    continue  # drops the complete data if there is an error
                # Adding data to a collection
                collection.append(data)

            df = pd.DataFrame(collection, columns =['title', 'link','publish_date','scraped_date','text'])
            if df.empty:
                err = scrapper_name + ": err: Empty dataframe"
                err_logs.append(err)
            # print(df) # For debugging. To check if df is created
            # print(err_logs) # For debugging - to check if any errors occoured
            df = FilterFunction(df)
            emptydataframe("Gobal Capital",df)
            return df
        except:
            print("Global capital not working")
            not_working_functions.append("Global Capital")
    def dominicantoday():
        try:
            print("Dominican Today")
            url = "https://dominicantoday.com/?s=ipo"
            domain_url = "https://dominicantoday.com/"

            headers = {
                "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10.15; rv:78.0) Gecko/20100101 Firefox/78.0",
                "accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.9",
                'sec-fetch-site': 'none',
                'sec-fetch-mode': 'navigate',
                'sec-fetch-user': '?1',
                'sec-fetch-dest': 'document',
                'accept-language': 'en-GB,en-US;q=0.9,en;q=0.8',
            }
            page = requests.get(url, headers=headers)
            soup = BeautifulSoup(page.content, "html.parser")
            # soup  # Debugging - if soup is working correctly

            # Class names of the elements to be scraped
            # ul_class = "search-results-list"  # Class name of div containing the a tag
            #h1_class = "_1Y-96"
            #h1_div_class = "col-xs-12"
            title_h1_itemprop = "headline"
            date_span_class = ["fecha"]
            para_span_itemprop = ["description"]

            links = []

            try:
                for h2_tag in soup.find_all("h2")[1:]:
                    for a in h2_tag.find_all("a", href=True):
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
            # links # Debugging - if link array is generated
            except:
                links = []
            # print(links)  # Debugging - if link array is generated

            collection = []
            err_logs = []
            scrapper_name = "dominicantoday"

            for link in links:
                try:
                    l_page = requests.get(link, headers=headers)
                    l_soup = BeautifulSoup(l_page.content, 'html.parser')
                except:
                    err = scrapper_name + ": err: Failed to retrieve data from link: " + link + " and convert it to soup object"
                    err_logs.append(err)
                    continue

                data = []
                # Scraping the heading
                #h1_ele = l_soup.find("h1", {"class": h1_class})
                
                try:
                    title_ele = l_soup.find("h1", {"itemprop": title_h1_itemprop})
                    title_text = title_ele.text
                    title_text = title_text.strip("\n")
                    title_text = title_text.strip()
                    data.append(title_text)
                except:
                    err = scrapper_name + ": err: Failed to find title in page. Link: " + link
                    err_logs.append(err)
                    continue  # drops the complete data if there is an error


                # Adding the link to data
                data.append(link)

                # Scraping the published date
                try:
                    date_ele = l_soup.find("span", {"class": date_span_class})
                    date_text = date_ele.text
                    date_text = date_text.strip("\n")
                    date_text = date_text.strip()
                    date_text = date_text.split("|")[0]
                    # date_text = (date_text.split('\n'))[-2]
                    #date_text = date_text.replace(" Updated: ", "")
                    data.append(date_text)  # The date_text could be further modified to represent a proper date format
                except:
                    err = scrapper_name + ": err: Failed to find date in page. Link: " + link
                    err_logs.append(err)
                    continue  # drops the complete data if there is an error
                
                # Adding the scraped date to data
                cur_date = str(datetime.today())
                data.append(cur_date)
                

                # Scraping the paragraph
                try:
                    para_ele = (l_soup.findAll("span", {"itemprop": para_span_itemprop}))[-1]
                    para_text = para_ele.text
                    para_text = para_text.strip("\n")
                    para_text = para_text.strip()
                    data.append(para_text)
                except:
                    err = scrapper_name + ": err: Failed to find paragraph in page. Link: " + link
                    err_logs.append(err)
                    continue  # drops the complete data if there is an error
                # Adding data to a collection
                collection.append(data)

            df = pd.DataFrame(collection, columns =['title', 'link','publish_date','scraped_date','text'])
            if df.empty:
                err = scrapper_name + ": err: Empty dataframe"
                err_logs.append(err)
            # print(df) # For debugging. To check if df is created
            # print(err_logs) # For debugging - to check if any errors occoured
            df = FilterFunction(df)
            emptydataframe("Dominican Today",df)
            return df
        except:
            print("Dominican today not working")
            not_working_functions.append("Dominicantoday")
    def businesstoday():
        try:
            print("businesstoday")
            url = "https://www.businesstoday.in/topic/ipo"
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
            page = requests.get(url, headers=headers)
            soup = BeautifulSoup(page.content, "html.parser")
            # soup  # Debugging - if soup is working correctly

            # Class names of the elements to be scraped
            div_class = "newcon-main"  # Class name of div containing the a tag
            #h1_class = "_1Y-96"
            #h1_div_class = "col-xs-12"
            title_div_class = "story-heading"
            date_div_class = ["newcon-main_innner_sec"]
            para_div_class=["text-formatted field field--name-body field--type-text-with-summary field--label-hidden field__item"]

            links = []

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
            # links # Debugging - if link array is generated

            collection = []
            err_logs = []
            scrapper_name = "businesstoday"

            for link in links:
                try:
                    l_page = requests.get(link, headers=headers)
                    l_soup = BeautifulSoup(l_page.content, 'html.parser')
                except:
                    err = scrapper_name + ": err: Failed to retrieve data from link: " + link + " and convert it to soup object"
                    err_logs.append(err)
                    continue

                data = []
                # Scraping the heading
                #h1_ele = l_soup.find("h1", {"class": h1_class})
                
                try:
                    title_ele = l_soup.find("div", {"class": title_div_class})
                    title_text = title_ele.text
                    title_text = title_text.strip("\n ")
                    data.append(title_text)
                except:
                    err = scrapper_name + ": err: Failed to find title in page. Link: " + link
                    err_logs.append(err)
                    continue  # drops the complete data if there is an error


                # Adding the link to data
                data.append(link)

                # Scraping the published date
                try:
                    date_ele = l_soup.find("div", {"class": date_div_class})
                    date_text = date_ele.text
                    date_text = date_text.strip("\n ")
                    date_text = " ".join(date_text.split()[:3])
                    #date_text = date_text.replace(" Updated: ", "")
                    data.append(date_text)  # The date_text could be further modified to represent a proper date format
                except:
                    err = scrapper_name + ": err: Failed to find date in page. Link: " + link
                    err_logs.append(err)
                    continue  # drops the complete data if there is an error
                
                # Adding the scraped date to data
                cur_date = str(datetime.today())
                data.append(cur_date)
                

                # Scraping the paragraph
                try:
                    para_ele = (l_soup.findAll("div", {"class": para_div_class}))[-1]
                    para_text = para_ele.text
                    para_text = para_text.strip("\n ")
                    data.append(para_text)  # Need to make this better
                except:
                    err = scrapper_name + ": err: Failed to find paragraph in page. Link: " + link
                    err_logs.append(err)
                    continue  # drops the complete data if there is an error
                # Adding data to a collection
                collection.append(data)

            df = pd.DataFrame(collection, columns =['title', 'link','publish_date','scraped_date','text'])
            if df.empty:
                err = scrapper_name + ": err: Empty dataframe"
                err_logs.append(err)
            # print(df) # For debugging. To check if df is created
            # print(err_logs) # For debugging - to check if any errors occoured
            df = FilterFunction(df)
            emptydataframe("businesstoday",df)
            return df
        except:
            print("businesstoday not working")
            not_working_functions.append("businesstoday")
    def investmentu():
    
        try:
            print("investmentu")
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
            page = requests.get(url, headers=headers)
            soup = BeautifulSoup(page.content, "html.parser")
            # soup  # Debugging - if soup is working correctly

            # Class names of the elements to be scraped
            div_class="articlePreview container"  # Class name of div containing the a tag
            #h1_class = "_1Y-96"
            #h1_div_class = "col-xs-12"
            title_h1_class = "page-title"
            date_time_class = ["updated"]
            para_div_role=["main"]

            links = []

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
            # links # Debugging - if link array is generated

            collection = []
            err_logs = []
            scrapper_name = "investmentu"

            for link in links:
                try:
                    l_page = requests.get(link, headers=headers)
                    l_soup = BeautifulSoup(l_page.content, 'html.parser')
                except:
                    err = scrapper_name + ": err: Failed to retrieve data from link: " + link + " and convert it to soup object"
                    err_logs.append(err)
                    continue

                data = []
                # Scraping the heading
                #h1_ele = l_soup.find("h1", {"class": h1_class})
                
                try:
                    title_ele = l_soup.find("h1", {"class": title_h1_class})
                    title_text = title_ele.text
                    title_text = title_text.strip("\n ")
                    data.append(title_text)
                except:
                    err = scrapper_name + ": err: Failed to find title in page. Link: " + link
                    err_logs.append(err)
                    continue  # drops the complete data if there is an error


                # Adding the link to data
                data.append(link)

                # Scraping the published date
                try:
                    date_ele = l_soup.find("time", {"class": date_time_class})
                    date_text = date_ele.text
                    date_text = date_text.strip("\n ")
                    date_text = " ".join(date_text.split()[:3])
                    #date_text = date_text.replace(" Updated: ", "")
                    data.append(date_text)  # The date_text could be further modified to represent a proper date format
                except:
                    err = scrapper_name + ": err: Failed to find date in page. Link: " + link
                    err_logs.append(err)
                    continue  # drops the complete data if there is an error
                
                # Adding the scraped date to data
                cur_date = str(datetime.today())
                data.append(cur_date)
                

                # Scraping the paragraph
                try:
                    para_ele = (l_soup.findAll("div", {"role": para_div_role}))[-1]
                    para_text = para_ele.text
                    para_text = para_text.strip("\n ")
                    data.append(para_text)  # Need to make this better
                except:
                    err = scrapper_name + ": err: Failed to find paragraph in page. Link: " + link
                    err_logs.append(err)
                    continue  # drops the complete data if there is an error
                # Adding data to a collection
                collection.append(data)

            df = pd.DataFrame(collection, columns =['title', 'link','publish_date','scraped_date','text'])
            if df.empty:
                err = scrapper_name + ": err: Empty dataframe"
                err_logs.append(err)
            # print(df) # For debugging. To check if df is created
            # print(err_logs) # For debugging - to check if any errors occoured
            df = FilterFunction(df)
            emptydataframe("investmentu",df)
            return df
        except:
            print("investmentu not working")
            not_working_functions.append("investmentu")
    def altassets():
    
        try:
            print("altassets")
            url = "https://www.altassets.net/?s=ipo"
            domain_url = "https://www.altassets.net/"

            headers = {
                "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10.15; rv:78.0) Gecko/20100101 Firefox/78.0",
                "accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.9",
                'sec-fetch-site': 'none',
                'sec-fetch-mode': 'navigate',
                'sec-fetch-user': '?1',
                'sec-fetch-dest': 'document',
                'accept-language': 'en-GB,en-US;q=0.9,en;q=0.8',
            }
            page = requests.get(url, headers=headers)
            soup = BeautifulSoup(page.content, "html.parser")
            # soup  # Debugging - if soup is working correctly

            # Class names of the elements to be scraped
            h3_class="entry-title td-module-title"# Class name of div containing the a tag
            #h1_class = "_1Y-96"
            #h1_div_class = "col-xs-12"
            title_h1_class = "entry-title"
            date_time_class = ["entry-date updated td-module-date"]
            para_div_class=["td-post-content"]

            links = []

            for divtag in soup.find_all("h3", {"class": h3_class}):
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
            # links # Debugging - if link array is generated

            collection = []
            err_logs = []
            scrapper_name = "altassets"

            for link in links:
                try:
                    l_page = requests.get(link, headers=headers)
                    l_soup = BeautifulSoup(l_page.content, 'html.parser')
                except:
                    err = scrapper_name + ": err: Failed to retrieve data from link: " + link + " and convert it to soup object"
                    err_logs.append(err)
                    continue

                data = []
                # Scraping the heading
                #h1_ele = l_soup.find("h1", {"class": h1_class})
                
                try:
                    title_ele = l_soup.find("h1", {"class": title_h1_class})
                    title_text = title_ele.text
                    title_text = title_text.strip("\n ")
                    data.append(title_text)
                except:
                    err = scrapper_name + ": err: Failed to find title in page. Link: " + link
                    err_logs.append(err)
                    continue  # drops the complete data if there is an error


                # Adding the link to data
                data.append(link)

                # Scraping the published date
                try:
                    date_ele = l_soup.find("time", {"class": date_time_class})
                    date_text = date_ele.text
                    date_text = date_text.strip("\n ")
                    date_text = " ".join(date_text.split()[:3])
                    #date_text = date_text.replace(" Updated: ", "")
                    data.append(date_text)  # The date_text could be further modified to represent a proper date format
                except:
                    err = scrapper_name + ": err: Failed to find date in page. Link: " + link
                    err_logs.append(err)
                    continue  # drops the complete data if there is an error
                
                # Adding the scraped date to data
                cur_date = str(datetime.today())
                data.append(cur_date)
                

                # Scraping the paragraph
                try:
                    para_ele = (l_soup.findAll("div", {"class": para_div_class}))[-1]
                    para_text = para_ele.text
                    para_text = para_text.strip("\n ")
                    data.append(para_text)  # Need to make this better
                except:
                    err = scrapper_name + ": err: Failed to find paragraph in page. Link: " + link
                    err_logs.append(err)
                    continue  # drops the complete data if there is an error
                # Adding data to a collection
                collection.append(data)

            df = pd.DataFrame(collection, columns =['title', 'link','publish_date','scraped_date','text'])
            if df.empty:
                err = scrapper_name + ": err: Empty dataframe"
                err_logs.append(err)
            # print(df) # For debugging. To check if df is created
            # print(err_logs) # For debugging - to check if any errors occoured
            df = FilterFunction(df)
            emptydataframe("altassets",df)
            return df
        except:
            print("altassets not working")
            not_working_functions.append("altassets")
    def techtarget():
        try:
            print("techtarget")
            url = "https://www.techtarget.com/search/query?q=ipo"
            domain_url = "https://www.techtarget.com/"

            headers = {
                "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10.15; rv:78.0) Gecko/20100101 Firefox/78.0",
                "accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.9",
                'sec-fetch-site': 'none',
                'sec-fetch-mode': 'navigate',
                'sec-fetch-user': '?1',
                'sec-fetch-dest': 'document',
                'accept-language': 'en-GB,en-US;q=0.9,en;q=0.8',
            }
            page = requests.get(url, headers=headers)
            soup = BeautifulSoup(page.content, "html.parser")
            # soup  # Debugging - if soup is working correctly

            # Class names of the elements to be scraped
            div_class="search-result-body"  # Class name of div containing the a tag
            #h1_class = "_1Y-96"
            #h1_div_class = "col-xs-12"
            title_h4_class = "section-title"
            date_div_class = ["main-article-author-date"]
            para_section_id=["content-body"]

            links = []

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
            # links # Debugging - if link array is generated

            collection = []
            err_logs = []
            scrapper_name = "techtarget"

            for link in links:
                try:
                    l_page = requests.get(link, headers=headers)
                    l_soup = BeautifulSoup(l_page.content, 'html.parser')
                except:
                    err = scrapper_name + ": err: Failed to retrieve data from link: " + link + " and convert it to soup object"
                    err_logs.append(err)
                    continue

                data = []
                # Scraping the heading
                #h1_ele = l_soup.find("h1", {"class": h1_class})
                
                try:
                    title_ele = l_soup.find("h4", {"class": title_h4_class})
                    title_text = title_ele.text
                    title_text = title_text.strip("\n ")
                    data.append(title_text)
                except:
                    err = scrapper_name + ": err: Failed to find title in page. Link: " + link
                    err_logs.append(err)
                    continue  # drops the complete data if there is an error


                # Adding the link to data
                data.append(link)

                # Scraping the published date
                try:
                    date_ele = l_soup.find("div", {"class": date_div_class})
                    date_text = date_ele.text
                    date_text = date_text.strip("\n ")
                    date_text = " ".join(date_text.split()[:3])
                    #date_text = date_text.replace(" Updated: ", "")
                    data.append(date_text)  # The date_text could be further modified to represent a proper date format
                except:
                    err = scrapper_name + ": err: Failed to find date in page. Link: " + link
                    err_logs.append(err)
                    continue  # drops the complete data if there is an error
                
                # Adding the scraped date to data
                cur_date = str(datetime.today())
                data.append(cur_date)
                

                # Scraping the paragraph
                try:
                    para_ele = (l_soup.findAll("section", {"id": para_section_id}))[-1]
                    para_text = para_ele.text
                    para_text = para_text.strip("\n ")
                    data.append(para_text)  # Need to make this better
                except:
                    err = scrapper_name + ": err: Failed to find paragraph in page. Link: " + link
                    err_logs.append(err)
                    continue  # drops the complete data if there is an error
                # Adding data to a collection
                collection.append(data)

            df = pd.DataFrame(collection, columns =['title', 'link','publish_date','scraped_date','text'])
            if df.empty:
                err = scrapper_name + ": err: Empty dataframe"
                err_logs.append(err)
            # print(df) # For debugging. To check if df is created
            # print(err_logs) # For debugging - to check if any errors occoured
            df = FilterFunction(df)
            emptydataframe("techtarget",df)
            return df
        except:
            print("techtarget not working")
            not_working_functions.append("techtarget")
    def stockhead():
        try:
            print("stockhead")
            url = "https://stockhead.com.au/?s=ipo"
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
            page = requests.get(url, headers=headers)
            soup = BeautifulSoup(page.content, "html.parser")
            # soup  # Debugging - if soup is working correctly

            # Class names of the elements to be scraped
            h2_class="entry-title"  # Class name of div containing the a tag
            #h1_class = "_1Y-96"
            #h1_div_class = "col-xs-12"
            title_span_class = "title-text"
            date_time_class = ["entry-date published updated"]
            para_div_id=["primary-0"]

            links = []

            for divtag in soup.find_all("h2", {"class": h2_class}):
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
            # links # Debugging - if link array is generated

            collection = []
            err_logs = []
            scrapper_name = "stockhead"

            for link in links:
                try:
                    l_page = requests.get(link, headers=headers)
                    l_soup = BeautifulSoup(l_page.content, 'html.parser')
                except:
                    err = scrapper_name + ": err: Failed to retrieve data from link: " + link + " and convert it to soup object"
                    err_logs.append(err)
                    continue

                data = []
                # Scraping the heading
                #h1_ele = l_soup.find("h1", {"class": h1_class})
                
                try:
                    title_ele = l_soup.find("span", {"class": title_span_class})
                    title_text = title_ele.text
                    title_text = title_text.strip("\n ")
                    data.append(title_text)
                except:
                    err = scrapper_name + ": err: Failed to find title in page. Link: " + link
                    err_logs.append(err)
                    continue  # drops the complete data if there is an error


                # Adding the link to data
                data.append(link)

                # Scraping the published date
                try:
                    date_ele = l_soup.find("time", {"class": date_time_class})
                    date_text = date_ele.text
                    date_text = date_text.strip("\n ")
                    date_text = " ".join(date_text.split()[:3])
                    #date_text = date_text.replace(" Updated: ", "")
                    data.append(date_text)  # The date_text could be further modified to represent a proper date format
                except:
                    err = scrapper_name + ": err: Failed to find date in page. Link: " + link
                    err_logs.append(err)
                    continue  # drops the complete data if there is an error
                
                # Adding the scraped date to data
                cur_date = str(datetime.today())
                data.append(cur_date)
                

                # Scraping the paragraph
                try:
                    para_ele = (l_soup.findAll("div", {"id": para_div_id}))[-1]
                    para_text = para_ele.text
                    para_text = para_text.strip("\n ")
                    data.append(para_text)  # Need to make this better
                except:
                    err = scrapper_name + ": err: Failed to find paragraph in page. Link: " + link
                    err_logs.append(err)
                    continue  # drops the complete data if there is an error
                # Adding data to a collection
                collection.append(data)

            df = pd.DataFrame(collection, columns =['title', 'link','publish_date','scraped_date','text'])
            if df.empty:
                err = scrapper_name + ": err: Empty dataframe"
                err_logs.append(err)
            # print(df) # For debugging. To check if df is created
            # print(err_logs) # For debugging - to check if any errors occoured
            df = FilterFunction(df)
            emptydataframe("stockhead",df)
            return df
        except:
            print("stockhead not working")
            not_working_functions.append("stockhead")
    def theindianwire():
        try:
            print("theindianwire")
            url = "https://www.theindianwire.com/?s=ipo"
            domain_url = "https://www.theindianwire.com/"

            headers = {
                "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10.15; rv:78.0) Gecko/20100101 Firefox/78.0",
                "accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.9",
                'sec-fetch-site': 'none',
                'sec-fetch-mode': 'navigate',
                'sec-fetch-user': '?1',
                'sec-fetch-dest': 'document',
                'accept-language': 'en-GB,en-US;q=0.9,en;q=0.8',
            }
            page = requests.get(url, headers=headers)
            soup = BeautifulSoup(page.content, "html.parser")
            # soup  # Debugging - if soup is working correctly

            # Class names of the elements to be scraped
            h2_class="entry-title h3" # Class name of div containing the a tag
            #h1_class = "_1Y-96"
            #h1_div_class = "col-xs-12"
            title_h1_class = "entry-title h1"
            date_span_class = ["updated"]
            para_div_class=["entry-content herald-entry-content"]

            links = []

            for divtag in soup.find_all("h2", {"class": h2_class}):
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
            # links # Debugging - if link array is generated

            collection = []
            err_logs = []
            scrapper_name = "theindianwire"

            for link in links:
                try:
                    l_page = requests.get(link, headers=headers)
                    l_soup = BeautifulSoup(l_page.content, 'html.parser')
                except:
                    err = scrapper_name + ": err: Failed to retrieve data from link: " + link + " and convert it to soup object"
                    err_logs.append(err)
                    continue

                data = []
                # Scraping the heading
                #h1_ele = l_soup.find("h1", {"class": h1_class})
                
                try:
                    title_ele = l_soup.find("h1", {"class": title_h1_class})
                    title_text = title_ele.text
                    title_text = title_text.strip("\n ")
                    data.append(title_text)
                except:
                    err = scrapper_name + ": err: Failed to find title in page. Link: " + link
                    err_logs.append(err)
                    continue  # drops the complete data if there is an error


                # Adding the link to data
                data.append(link)

                # Scraping the published date
                try:
                    date_ele = l_soup.find("span", {"class": date_span_class})
                    date_text = date_ele.text
                    date_text = date_text.strip("\n ")
                    date_text = " ".join(date_text.split()[:3])
                    #date_text = date_text.replace(" Updated: ", "")
                    data.append(date_text)  # The date_text could be further modified to represent a proper date format
                except:
                    err = scrapper_name + ": err: Failed to find date in page. Link: " + link
                    err_logs.append(err)
                    continue  # drops the complete data if there is an error
                
                # Adding the scraped date to data
                cur_date = str(datetime.today())
                data.append(cur_date)
                

                # Scraping the paragraph
                try:
                    para_ele = (l_soup.findAll("div", {"class": para_div_class}))[-1]
                    para_text = para_ele.text
                    para_text = para_text.strip("\n ")
                    data.append(para_text)  # Need to make this better
                except:
                    err = scrapper_name + ": err: Failed to find paragraph in page. Link: " + link
                    err_logs.append(err)
                    continue  # drops the complete data if there is an error
                # Adding data to a collection
                collection.append(data)

            df = pd.DataFrame(collection, columns =['title', 'link','publish_date','scraped_date','text'])
            if df.empty:
                err = scrapper_name + ": err: Empty dataframe"
                err_logs.append(err)
            # print(df) # For debugging. To check if df is created
            # print(err_logs) # For debugging - to check if any errors occoured
            df = FilterFunction(df)
            emptydataframe("theindianwire",df)
            return df
        except:
            print("theindianwire not working")
            not_working_functions.append("theindianwire")
    def indianexpress():
        try:
            print("indianexpress")
            url = "https://indianexpress.com/?s=ipo"
            domain_url = "https://indianexpress.com/"

            headers = {
                "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10.15; rv:78.0) Gecko/20100101 Firefox/78.0",
                "accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.9",
                'sec-fetch-site': 'none',
                'sec-fetch-mode': 'navigate',
                'sec-fetch-user': '?1',
                'sec-fetch-dest': 'document',
                'accept-language': 'en-GB,en-US;q=0.9,en;q=0.8',
            }
            page = requests.get(url, headers=headers)
            soup = BeautifulSoup(page.content, "html.parser")
            # soup  # Debugging - if soup is working correctly

            # Class names of the elements to be scraped
            div_class="details" # Class name of div containing the a tag
            #h1_class = "_1Y-96"
            #h1_div_class = "col-xs-12"
            title_h1_itemprop = "headline"
            date_span_itemprop = ["dateModified"]
            para_div_id=["pcl-full-content"]

            links = []

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
            # links # Debugging - if link array is generated

            collection = []
            err_logs = []
            scrapper_name = "indianexpress"

            for link in links:
                try:
                    l_page = requests.get(link, headers=headers)
                    l_soup = BeautifulSoup(l_page.content, 'html.parser')
                except:
                    err = scrapper_name + ": err: Failed to retrieve data from link: " + link + " and convert it to soup object"
                    err_logs.append(err)
                    continue

                data = []
                # Scraping the heading
                #h1_ele = l_soup.find("h1", {"class": h1_class})
                
                try:
                    title_ele = l_soup.find("h1", {"itemprop": title_h1_itemprop})
                    title_text = title_ele.text
                    title_text = title_text.strip("\n ")
                    data.append(title_text)
                except:
                    err = scrapper_name + ": err: Failed to find title in page. Link: " + link
                    err_logs.append(err)
                    continue  # drops the complete data if there is an error


                # Adding the link to data
                data.append(link)

                # Scraping the published date
                try:
                    date_ele = l_soup.find("span", {"itemprop": date_span_itemprop})
                    date_text = date_ele.text
                    date_text = date_text.strip("\n ")
                    date_text = " ".join(date_text.split()[:3])
                    #date_text = date_text.replace(" Updated: ", "")
                    data.append(date_text)  # The date_text could be further modified to represent a proper date format
                except:
                    err = scrapper_name + ": err: Failed to find date in page. Link: " + link
                    err_logs.append(err)
                    continue  # drops the complete data if there is an error
                
                # Adding the scraped date to data
                cur_date = str(datetime.today())
                data.append(cur_date)
                

                # Scraping the paragraph
                try:
                    para_ele = (l_soup.findAll("div", {"id": para_div_id}))[-1]
                    para_text = para_ele.text
                    para_text = para_text.strip("\n ")
                    data.append(para_text)  # Need to make this better
                except:
                    err = scrapper_name + ": err: Failed to find paragraph in page. Link: " + link
                    err_logs.append(err)
                    continue  # drops the complete data if there is an error
                # Adding data to a collection
                collection.append(data)

            df = pd.DataFrame(collection, columns =['title', 'link','publish_date','scraped_date','text'])
            if df.empty:
                err = scrapper_name + ": err: Empty dataframe"
                err_logs.append(err)
            # print(df) # For debugging. To check if df is created
            # print(err_logs) # For debugging - to check if any errors occoured
            df = FilterFunction(df)
            emptydataframe("indianexpress",df)
            return df
        except:
            print("indianexpress not working")
            not_working_functions.append("indianexpress")
    def newindianexpress():
        try:
            print("newindianexpress")
            url = "https://www.newindianexpress.com/topic?term=ipo&request=ALL&search=short"
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
            page = requests.get(url, headers=headers)
            soup = BeautifulSoup(page.content, "html.parser")
            # soup  # Debugging - if soup is working correctly

            # Class names of the elements to be scraped
            div_class="search-row_type" # Class name of div containing the a tag
            #h1_class = "_1Y-96"
            #h1_div_class = "col-xs-12"
            title_h1_class = "ArticleHead"
            date_p_class = ["ArticlePublish margin-bottom-10"]
            para_div_id=["wholeContent"]

            links = []

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
            # links # Debugging - if link array is generated

            collection = []
            err_logs = []
            scrapper_name = "newindianexpress"

            for link in links:
                try:
                    l_page = requests.get(link, headers=headers)
                    l_soup = BeautifulSoup(l_page.content, 'html.parser')
                except:
                    err = scrapper_name + ": err: Failed to retrieve data from link: " + link + " and convert it to soup object"
                    err_logs.append(err)
                    continue

                data = []
                # Scraping the heading
                #h1_ele = l_soup.find("h1", {"class": h1_class})
                
                try:
                    title_ele = l_soup.find("h1", {"class": title_h1_class})
                    title_text = title_ele.text
                    title_text = title_text.strip("\n ")
                    data.append(title_text)
                except:
                    err = scrapper_name + ": err: Failed to find title in page. Link: " + link
                    err_logs.append(err)
                    continue  # drops the complete data if there is an error


                # Adding the link to data
                data.append(link)

                # Scraping the published date
                try:
                    date_ele = l_soup.find("p", {"class": date_p_class})
                    date_text = date_ele.text
                    date_text = date_text.strip("\n ")
                    date_text = " ".join(date_text.split()[:3])
                    #date_text = date_text.replace(" Updated: ", "")
                    data.append(date_text)  # The date_text could be further modified to represent a proper date format
                except:
                    err = scrapper_name + ": err: Failed to find date in page. Link: " + link
                    err_logs.append(err)
                    continue  # drops the complete data if there is an error
                
                # Adding the scraped date to data
                cur_date = str(datetime.today())
                data.append(cur_date)
                

                # Scraping the paragraph
                try:
                    para_ele = (l_soup.findAll("div", {"id": para_div_id}))[-1]
                    para_text = para_ele.text
                    para_text = para_text.strip("\n ")
                    data.append(para_text)  # Need to make this better
                except:
                    err = scrapper_name + ": err: Failed to find paragraph in page. Link: " + link
                    err_logs.append(err)
                    continue  # drops the complete data if there is an error
                # Adding data to a collection
                collection.append(data)

            df = pd.DataFrame(collection, columns =['title', 'link','publish_date','scraped_date','text'])
            if df.empty:
                err = scrapper_name + ": err: Empty dataframe"
                err_logs.append(err)
            # print(df) # For debugging. To check if df is created
            # print(err_logs) # For debugging - to check if any errors occoured
            df = FilterFunction(df)
            emptydataframe("newindianexpress",df)
            return df
        except:
            print("newindianexpress not working")
            not_working_functions.append("newindianexpress")
    def hindustannewshub():
        try:
            print("hindustannewshub")
            url = "https://hindustannewshub.com/?s=ipo"
            domain_url = "https://hindustannewshub.com/"

            headers = {
                "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10.15; rv:78.0) Gecko/20100101 Firefox/78.0",
                "accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.9",
                'sec-fetch-site': 'none',
                'sec-fetch-mode': 'navigate',
                'sec-fetch-user': '?1',
                'sec-fetch-dest': 'document',
                'accept-language': 'en-GB,en-US;q=0.9,en;q=0.8',
            }
            page = requests.get(url, headers=headers)
            soup = BeautifulSoup(page.content, "html.parser")
            # soup  # Debugging - if soup is working correctly

            # Class names of the elements to be scraped
            div_class="td-module-meta-info" # Class name of div containing the a tag
            #h1_class = "_1Y-96"
            #h1_div_class = "col-xs-12"
            title_h1_class = "tdb-title-text"
            date_time_class = ["entry-date updated td-module-date"]
            para_div_class=["td_block_wrap tdb_single_content tdi_21 td-pb-border-top td_block_template_1 td-post-content tagdiv-type"]

            links = []

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
            # links # Debugging - if link array is generated

            collection = []
            err_logs = []
            scrapper_name = "hindustannewshub"

            for link in links:
                try:
                    l_page = requests.get(link, headers=headers)
                    l_soup = BeautifulSoup(l_page.content, 'html.parser')
                except:
                    err = scrapper_name + ": err: Failed to retrieve data from link: " + link + " and convert it to soup object"
                    err_logs.append(err)
                    continue

                data = []
                # Scraping the heading
                #h1_ele = l_soup.find("h1", {"class": h1_class})
                
                try:
                    title_ele = l_soup.find("h1", {"class": title_h1_class})
                    title_text = title_ele.text
                    title_text = title_text.strip("\n ")
                    data.append(title_text)
                except:
                    err = scrapper_name + ": err: Failed to find title in page. Link: " + link
                    err_logs.append(err)
                    continue  # drops the complete data if there is an error


                # Adding the link to data
                data.append(link)

                # Scraping the published date
                try:
                    date_ele = l_soup.find("time", {"class": date_time_class})
                    date_text = date_ele.text
                    date_text = date_text.strip("\n ")
                    date_text = " ".join(date_text.split()[:3])
                    #date_text = date_text.replace(" Updated: ", "")
                    data.append(date_text)  # The date_text could be further modified to represent a proper date format
                except:
                    err = scrapper_name + ": err: Failed to find date in page. Link: " + link
                    err_logs.append(err)
                    continue  # drops the complete data if there is an error
                
                # Adding the scraped date to data
                cur_date = str(datetime.today())
                data.append(cur_date)
                

                # Scraping the paragraph
                try:
                    para_ele = (l_soup.findAll("div", {"class": para_div_class}))[-1]
                    para_text = para_ele.text
                    para_text = para_text.strip("\n ")
                    data.append(para_text)  # Need to make this better
                except:
                    err = scrapper_name + ": err: Failed to find paragraph in page. Link: " + link
                    err_logs.append(err)
                    continue  # drops the complete data if there is an error
                # Adding data to a collection
                collection.append(data)

            df = pd.DataFrame(collection, columns =['title', 'link','publish_date','scraped_date','text'])
            if df.empty:
                err = scrapper_name + ": err: Empty dataframe"
                err_logs.append(err)
            # print(df) # For debugging. To check if df is created
            # print(err_logs) # For debugging - to check if any errors occoured
            df = FilterFunction(df)
            emptydataframe("hindustannewshub",df)
            return df
        except:
            print("hindustannewshub not working")
            not_working_functions.append("hindustannewshub")
    def businessinsider():
        try:
            print("businessinsider")
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
            page = requests.get(url, headers=headers)
            soup = BeautifulSoup(page.content, "html.parser")
            # soup  # Debugging - if soup is working correctly

            # Class names of the elements to be scraped
            div_class="list-bottom-text-wrapper" # Class name of div containing the a tag
            #h1_class = "_1Y-96"
            #h1_div_class = "col-xs-12"
            title_div_class= "mobile_padding"
            date_span_class = ["Date"]
            para_div_class=["Normal"]

            links = []

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
            # links # Debugging - if link array is generated

            collection = []
            err_logs = []
            scrapper_name = "businessinsider"

            for link in links:
                try:
                    l_page = requests.get(link, headers=headers)
                    l_soup = BeautifulSoup(l_page.content, 'html.parser')
                except:
                    err = scrapper_name + ": err: Failed to retrieve data from link: " + link + " and convert it to soup object"
                    err_logs.append(err)
                    continue

                data = []
                # Scraping the heading
                #h1_ele = l_soup.find("h1", {"class": h1_class})
                
                try:
                    title_ele = l_soup.find("div", {"class": title_div_class})
                    title_text = title_ele.text
                    title_text = title_text.strip("\n ")
                    data.append(title_text)
                except:
                    err = scrapper_name + ": err: Failed to find title in page. Link: " + link
                    err_logs.append(err)
                    continue  # drops the complete data if there is an error


                # Adding the link to data
                data.append(link)

                # Scraping the published date
                try:
                    date_ele = l_soup.find("span", {"class": date_span_class})
                    date_text = date_ele.text
                    date_text = date_text.strip("\n ")
                    date_text = " ".join(date_text.split()[:3])
                    #date_text = date_text.replace(" Updated: ", "")
                    data.append(date_text)  # The date_text could be further modified to represent a proper date format
                except:
                    err = scrapper_name + ": err: Failed to find date in page. Link: " + link
                    err_logs.append(err)
                    continue  # drops the complete data if there is an error
                
                # Adding the scraped date to data
                cur_date = str(datetime.today())
                data.append(cur_date)
                

                # Scraping the paragraph
                try:
                    para_ele = (l_soup.findAll("div", {"class": para_div_class}))[-1]
                    para_text = para_ele.text
                    para_text = para_text.strip("\n ")
                    data.append(para_text)  # Need to make this better
                except:
                    err = scrapper_name + ": err: Failed to find paragraph in page. Link: " + link
                    err_logs.append(err)
                    continue  # drops the complete data if there is an error
                # Adding data to a collection
                collection.append(data)

            df = pd.DataFrame(collection, columns =['title', 'link','publish_date','scraped_date','text'])
            if df.empty:
                err = scrapper_name + ": err: Empty dataframe"
                err_logs.append(err)
            # print(df) # For debugging. To check if df is created
            # print(err_logs) # For debugging - to check if any errors occoured
            df = FilterFunction(df)
            emptydataframe("businessinsider",df)
            return df
        except:
            print("businessinsider not working")
            not_working_functions.append("businessinsider")
    def ndtv():
        try:
            print("ndtv")
            url = "https://www.ndtv.com/search?searchtext=ipo"
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
            page = requests.get(url, headers=headers)
            soup = BeautifulSoup(page.content, "html.parser")
            # soup  # Debugging - if soup is working correctly

            # Class names of the elements to be scraped
            ul_class="src_lst-ul" # Class name of div containing the a tag
            #h1_class = "_1Y-96"
            #h1_div_class = "col-xs-12"
            title_h1_class= "sp-ttl"
            date_span_itemprop = ["dateModified"]
            para_div_itemprop=["articleBody"]

            links = []

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
            # links # Debugging - if link array is generated

            collection = []
            err_logs = []
            scrapper_name = "ndtv"

            for link in links:
                try:
                    l_page = requests.get(link, headers=headers)
                    l_soup = BeautifulSoup(l_page.content, 'html.parser')
                except:
                    err = scrapper_name + ": err: Failed to retrieve data from link: " + link + " and convert it to soup object"
                    err_logs.append(err)
                    continue

                data = []
                # Scraping the heading
                #h1_ele = l_soup.find("h1", {"class": h1_class})
                
                try:
                    title_ele = l_soup.find("h1", {"class": title_h1_class})
                    title_text = title_ele.text
                    title_text = title_text.strip("\n ")
                    data.append(title_text)
                except:
                    err = scrapper_name + ": err: Failed to find title in page. Link: " + link
                    err_logs.append(err)
                    continue  # drops the complete data if there is an error


                # Adding the link to data
                data.append(link)

                # Scraping the published date
                try:
                    date_ele = l_soup.find("span", {"itemporp": date_span_itemprop})
                    date_text = date_ele.text
                    date_text = date_text.strip("\n ")
                    date_text = " ".join(date_text.split()[:3])
                    #date_text = date_text.replace(" Updated: ", "")
                    data.append(date_text)  # The date_text could be further modified to represent a proper date format
                except:
                    err = scrapper_name + ": err: Failed to find date in page. Link: " + link
                    err_logs.append(err)
                    continue  # drops the complete data if there is an error
                
                # Adding the scraped date to data
                cur_date = str(datetime.today())
                data.append(cur_date)
                

                # Scraping the paragraph
                try:
                    para_ele = (l_soup.findAll("div", {"itemprop": para_div_itemprop}))[-1]
                    para_text = para_ele.text
                    para_text = para_text.strip("\n ")
                    data.append(para_text)  # Need to make this better
                except:
                    err = scrapper_name + ": err: Failed to find paragraph in page. Link: " + link
                    err_logs.append(err)
                    continue  # drops the complete data if there is an error
                # Adding data to a collection
                collection.append(data)

            df = pd.DataFrame(collection, columns =['title', 'link','publish_date','scraped_date','text'])
            if df.empty:
                err = scrapper_name + ": err: Empty dataframe"
                err_logs.append(err)
            # print(df) # For debugging. To check if df is created
            # print(err_logs) # For debugging - to check if any errors occoured
            df = FilterFunction(df)
            emptydataframe("ndtv",df)
            return df
        except:
            print("ndtv not working")
            not_working_functions.append("ndtv")
    def detroitnews():
        try:
            print("detroitnews")
            url = "https://www.detroitnews.com/search/?q=ipo"
            domain_url = "https://www.detroitnews.com/"

            headers = {
                "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10.15; rv:78.0) Gecko/20100101 Firefox/78.0",
                "accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.9",
                'sec-fetch-site': 'none',
                'sec-fetch-mode': 'navigate',
                'sec-fetch-user': '?1',
                'sec-fetch-dest': 'document',
                'accept-language': 'en-GB,en-US;q=0.9,en;q=0.8',
            }
            page = requests.get(url, headers=headers)
            soup = BeautifulSoup(page.content, "html.parser")
            # soup  # Debugging - if soup is working correctly

            # Class names of the elements to be scraped
            div_class="gnt_pr" # Class name of div containing the a tag
            #h1_class = "_1Y-96"
            #h1_div_class = "col-xs-12"
            title_h1_elementtiming= "ar-headline"
            date_div_class = ["gnt_ar_dt"]
            para_div_class=["gnt_ar_b"]

            links = []

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
            # links # Debugging - if link array is generated

            collection = []
            err_logs = []
            scrapper_name = "detroitnews"

            for link in links:
                try:
                    l_page = requests.get(link, headers=headers)
                    l_soup = BeautifulSoup(l_page.content, 'html.parser')
                except:
                    err = scrapper_name + ": err: Failed to retrieve data from link: " + link + " and convert it to soup object"
                    err_logs.append(err)
                    continue

                data = []
                # Scraping the heading
                #h1_ele = l_soup.find("h1", {"class": h1_class})
                
                try:
                    title_ele = l_soup.find("h1", {"elementtiming": title_h1_elementtiming})
                    title_text = title_ele.text
                    title_text = title_text.strip("\n ")
                    data.append(title_text)
                except:
                    err = scrapper_name + ": err: Failed to find title in page. Link: " + link
                    err_logs.append(err)
                    continue  # drops the complete data if there is an error


                # Adding the link to data
                data.append(link)

                # Scraping the published date
                try:
                    date_ele = l_soup.find("div", {"class": date_div_class})
                    date_text = date_ele.text
                    date_text = date_text.strip("\n ")
                    date_text = " ".join(date_text.split()[:3])
                    #date_text = date_text.replace(" Updated: ", "")
                    data.append(date_text)  # The date_text could be further modified to represent a proper date format
                except:
                    err = scrapper_name + ": err: Failed to find date in page. Link: " + link
                    err_logs.append(err)
                    continue  # drops the complete data if there is an error
                
                # Adding the scraped date to data
                cur_date = str(datetime.today())
                data.append(cur_date)
                

                # Scraping the paragraph
                try:
                    para_ele = (l_soup.findAll("div", {"class": para_div_class}))[-1]
                    para_text = para_ele.text
                    para_text = para_text.strip("\n ")
                    data.append(para_text)  # Need to make this better
                except:
                    err = scrapper_name + ": err: Failed to find paragraph in page. Link: " + link
                    err_logs.append(err)
                    continue  # drops the complete data if there is an error
                # Adding data to a collection
                collection.append(data)

            df = pd.DataFrame(collection, columns =['title', 'link','publish_date','scraped_date','text'])
            if df.empty:
                err = scrapper_name + ": err: Empty dataframe"
                err_logs.append(err)
            # print(df) # For debugging. To check if df is created
            # print(err_logs) # For debugging - to check if any errors occoured
            df = FilterFunction(df)
            emptydataframe("detroitnews",df)
            return df
        except:
            print("detroitnews not working")
            not_working_functions.append("detroitnews")


    def koreajoongangdailyjoins():
        try:
            print("koreajoongangdailyjoins")
            url = "https://koreajoongangdaily.joins.com/section/searchResult/ipo?searchFlag=1"
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
            page = requests.get(url, headers=headers)
            soup = BeautifulSoup(page.content, "html.parser")
            # soup  # Debugging - if soup is working correctly

            # Class names of the elements to be scraped
            div_class="mid-article3" # Class name of div containing the a tag
            #h1_class = "_1Y-96"
            #h1_div_class = "col-xs-12"
            title_h1_class= "view-article-title serif"
            date_div_class = ["article-menu-box"]
            para_div_id=["article_body"]

            links = []

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
            # links # Debugging - if link array is generated

            collection = []
            err_logs = []
            scrapper_name = "koreajoongangdailyjoins"

            for link in links:
                try:
                    l_page = requests.get(link, headers=headers)
                    l_soup = BeautifulSoup(l_page.content, 'html.parser')
                except:
                    err = scrapper_name + ": err: Failed to retrieve data from link: " + link + " and convert it to soup object"
                    err_logs.append(err)
                    continue

                data = []
                # Scraping the heading
                #h1_ele = l_soup.find("h1", {"class": h1_class})

                try:
                    title_ele = l_soup.find("h1", {"class": title_h1_class})
                    title_text = title_ele.text
                    title_text = title_text.strip("\n ")
                    data.append(title_text)
                except:
                    err = scrapper_name + ": err: Failed to find title in page. Link: " + link
                    err_logs.append(err)
                    continue  # drops the complete data if there is an error


                # Adding the link to data
                data.append(link)

                # Scraping the published date
                try:
                    date_ele = l_soup.find("div", {"class": date_div_class})
                    date_text = date_ele.text
                    date_text = date_text.strip("\n ")
                    date_text = " ".join(date_text.split()[:3])
                    #date_text = date_text.replace(" Updated: ", "")
                    data.append(date_text)  # The date_text could be further modified to represent a proper date format
                except:
                    err = scrapper_name + ": err: Failed to find date in page. Link: " + link
                    err_logs.append(err)
                    continue  # drops the complete data if there is an error

                # Adding the scraped date to data
                cur_date = str(datetime.today())
                data.append(cur_date)


                # Scraping the paragraph
                try:
                    para_ele = (l_soup.findAll("div", {"id": para_div_id}))[-1]
                    para_text = para_ele.text
                    para_text = para_text.strip("\n ")
                    data.append(para_text)  # Need to make this better
                except:
                    err = scrapper_name + ": err: Failed to find paragraph in page. Link: " + link
                    err_logs.append(err)
                    continue  # drops the complete data if there is an error
                # Adding data to a collection
                collection.append(data)

            df = pd.DataFrame(collection, columns =['title', 'link','publish_date','scraped_date','text'])
            if df.empty:
                err = scrapper_name + ": err: Empty dataframe"
                err_logs.append(err)
            # print(df) # For debugging. To check if df is created
            # print(err_logs) # For debugging - to check if any errors occoured
            df = FilterFunction(df)
            emptydataframe("koreajoongangdailyjoins",df)
            return df
        except:
            print("koreajoongangdailyjoins not working")
            not_working_functions.append("koreajoongangdailyjoins")
    

    def upstreamonline():
        try:
            print("upstreamonline")
            url = "https://www.upstreamonline.com/archive/?languages=en&locale=en&q=ipo"
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
            page = requests.get(url, headers=headers)
            soup = BeautifulSoup(page.content, "html.parser")
            # soup  # Debugging - if soup is working correctly

            # Class names of the elements to be scraped
            div_class="mb-auto" # Class name of div containing the a tag
            #h1_class = "_1Y-96"
            #h1_div_class = "col-xs-12"
            title_h1_class= "fs-xxl fw-bold mb-4 article-title ff-sueca-bold"
            date_span_class = ["st-italic"]
            para_div_class=["article-body"]

            links = []

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
            # links # Debugging - if link array is generated

            collection = []
            err_logs = []
            scrapper_name = "upstreamonline"

            for link in links:
                try:
                    l_page = requests.get(link, headers=headers)
                    l_soup = BeautifulSoup(l_page.content, 'html.parser')
                except:
                    err = scrapper_name + ": err: Failed to retrieve data from link: " + link + " and convert it to soup object"
                    err_logs.append(err)
                    continue

                data = []
                # Scraping the heading
                #h1_ele = l_soup.find("h1", {"class": h1_class})

                try:
                    title_ele = l_soup.find("h1", {"class": title_h1_class})
                    title_text = title_ele.text
                    title_text = title_text.strip("\n ")
                    data.append(title_text)
                except:
                    err = scrapper_name + ": err: Failed to find title in page. Link: " + link
                    err_logs.append(err)
                    continue  # drops the complete data if there is an error


                # Adding the link to data
                data.append(link)

                # Scraping the published date
                try:
                    date_ele = l_soup.find("span", {"class": date_span_class})
                    date_text = date_ele.text
                    date_text = date_text.strip("\n ")
                    date_text = " ".join(date_text.split()[:3])
                    #date_text = date_text.replace(" Updated: ", "")
                    data.append(date_text)  # The date_text could be further modified to represent a proper date format
                except:
                    err = scrapper_name + ": err: Failed to find date in page. Link: " + link
                    err_logs.append(err)
                    continue  # drops the complete data if there is an error

                # Adding the scraped date to data
                cur_date = str(datetime.today())
                data.append(cur_date)


                # Scraping the paragraph
                try:
                    para_ele = (l_soup.findAll("div", {"class": para_div_class}))[-1]
                    para_text = para_ele.text
                    para_text = para_text.strip("\n ")
                    data.append(para_text)  # Need to make this better
                except:
                    err = scrapper_name + ": err: Failed to find paragraph in page. Link: " + link
                    err_logs.append(err)
                    continue  # drops the complete data if there is an error
                # Adding data to a collection
                collection.append(data)

            df = pd.DataFrame(collection, columns =['title', 'link','publish_date','scraped_date','text'])
            if df.empty:
                err = scrapper_name + ": err: Empty dataframe"
                err_logs.append(err)
            # print(df) # For debugging. To check if df is created
            # print(err_logs) # For debugging - to check if any errors occoured
            df = FilterFunction(df)
            emptydataframe("upstreamonline",df)
            return df
        except:
            print("upstreamonline not working")
            not_working_functions.append("upstreamonline") 

    # def businessstandard():
    #     try:
    #         print("Business Standard IPO")
    #         err_logs = []
    #         title,links,text,pub_date,scraped_date = [],[],[],[],[]

    #         test_url = "https://www.business-standard.com/search?q=ipo"
    #         domain_url = "https://www.business-standard.com"
    #         options = Options()
    #         options.headless = True
    #         driver = webdriver.Firefox(options=options)
    #         driver.get(test_url)
    #         time.sleep(2)
    #         html = driver.page_source
    #         driver.quit()
    #         sp=BeautifulSoup(html, 'lxml')
    #         all_ul = sp.find_all('ul',{"class":"listing"})
    #         #print(all_ul)
    #         for ul1 in all_ul:
    #                     h2_all=ul1.find_all("h2")
    #                     for h2 in h2_all:
    #                         a_all=h2.find_all("a")
    #                         link=""
    #                         for a1 in a_all:
    #                             if((a1['href']!=None) and (a1.text != None)):
    #                                 #get news link
    #                                 #print("\n\n inside ..................................\n\n")
    #                                 link=domain_url +a1['href']
    #                                 links.append(link)

    #                                 #print(link)
                            
    #                                 today = date.today()
                    
    #                                 try:
    #                                         page1 = requests.get(link)
    #                                         soup1 = BeautifulSoup(page1.content,"html.parser")
    #                                         #print(soup)
    #                                         #get news details

    #                                 except:
    #                                         err = "Businessstandard : err : Couldn't fetch url " + link 
    #                                         print("inside_except")
    #                                         err_logs.append(err)
    #                                         continue
    #                                         #news tile
                                            
    #                                 title1=""
    #                                 if(soup1.find("h1" , {"class" : "headline"}).text !=None):
    #                                     title1=soup1.find("h1" , {"class" : "headline"}).text

                                    
    #                                 #print("title:",title1) 
    #                                 title1=title1.strip()
    #                                 title.append(title1)
                                                            
    #                                 #news content
    #                                 text2=[]
    #                                 text3=""
    #                                 if (soup1.find("div" , {"class" : "story-content"})!=None):
    #                                     articlebody=soup1.find("div" , {"class" : "story-content"})
    #                                     if(articlebody.find("span",{"class":"p-content"})!=None):
    #                                         span_class=articlebody.find("span",{"class":"p-content"})
                                            
    #                                         p_all =span_class.find_all("p")
    #                                         if(p_all !=None):
    #                                             for p in p_all:
    #                                                 if(p.text!=None):                                                
    #                                                     text1 = p.text
    #                                                     text1=text1.strip()
    #                                                     text3=text3+text1
                                                       
    #                                         #print(text1)
                                    
    #                                 text.append(text3)
                                    
                                
    #                                 #news publish date 
    #                                 pubDate1=""
    #                                 nd=soup1.find("div" , {"class" : "pubDate"})
    #                                 if(nd!=None) :
    #                                     pubDate1=nd.text
                                        
    #                                 elif(soup1.find('div',{"class":"publish-date"})!=None):
    #                                     pubDate1=soup1.find('div',{"class":"publish-date"}).h4.i.text
    #                                 pubDate1=pubDate1.strip()
    #                                 pubDate1 =pubDate1[17:]
                                
    #                                 pub_date.append(pubDate1)
    #                                 #print(pubDate1)
                                    

    #                                 #Scrapped date 
    #                                 scraped_date.append(str(today))
            
    #         df = pd.DataFrame({"text" : text , "link":links,"publish_date":pub_date,"scraped_date":scraped_date,"title":title})
        
    #         #df=pd.DataFrame({'Title': title,'link':links,'news body':text,'pubdate':pub_date,'Scrape date':scraped_date})
    #         #print(df)
    #         if df.empty:
    #             err = "businessstandard : err: Empty dataframe"
    #             err_logs.append(err)
    #         df = df.drop_duplicates(subset=["link"])
    #         df = FilterFunction(df)
    #         emptydataframe("Business Standard",df)
    #         return df
        
                                            
    #     except:
    #         print(" Business Standard not working")
    #         not_working_functions.append("Business  Standard")
              
    
    # def straitimes():
    #     try:
    #         print("Strait Times IPO")
    #         err_logs = []
    #         title,links,text,pub_date,scraped_date = [],[],[],[],[]

    #         test_url = "https://www.straitstimes.com/search?searchkey=ipo"
    #         domain_url = "https://www.straitstimes.com/"
    #         options = Options()
    #         options.headless = True

    #         driver = webdriver.Firefox(options=options)

    #         driver.get(test_url)
    #         time.sleep(2)

    #         html = driver.page_source
    #         driver.quit()
            
    #         sp=BeautifulSoup(html, 'lxml')
    #         all_divs = sp.find_all('div',{"class":"queryly_item_row"})            
            
    #         if (all_divs!=None): 
    #             for div1 in all_divs:
    #                 if(div1!=None):
    #                     date1=div1.find("div",{"class":"queryly_item_description"})
                        
    #                     #chck news publish date  from front page
    #                     utext_main=""
    #                     if (date1 != None):
    #                         utext_main=date1.text
    #                         utext_main=utext_main.lstrip()
    #                         #print(utext_main)
    #                         if(len(utext_main)>=12):
    #                             temp1_month_year=utext_main[0:3]+" "+utext_main[8:12]
    #                             #print(temp1_month_year)
                                
    #                             currentMonth = datetime.now().month
    #                             currentYear = datetime.now().year
    #                             monthdict={1:"Jan",2:"Feb",3:"Mar",4:"Apr",5:"May",6:"Jun",7:"Jul",8:"Aug",9:"Sep",10:"Oct",11:"Nov",12:"Dec"}
    #                             currentMonthandYear=str(monthdict[currentMonth])+" "+str(currentYear)
    #                             #print("\n\n...........\n\n")

    #                             #print("temp1_month_year "+temp1_month_year)
    #                             #print("currentMonthandYear " +currentMonthandYear)
    #                             if(temp1_month_year==currentMonthandYear):
    #                                 #print("Matched....the news belong to current month, proceed with new fetch details")
    #                                 #pub_date.append(utext_main) 
                                    
    #                                 a_all=div1.find_all("a")
    #                                 if(a_all!=None):
    #                                     link=""
    #                                     for a1 in a_all:
    #                                         if((a1['href']!=None)):
    #                                             link=a1['href']
    #                                             links.append(link)
    #                                             #print("\n")
    #                                             #print(link)

    #                                             today = date.today()
                                
    #                                             try:
                                                        
    #                                                     headers = {
    #                                                         "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10.15; rv:78.0) Gecko/20100101 Firefox/78.0",
    #                                                         "accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.9",
    #                                                         'sec-fetch-site': 'none',
    #                                                         'sec-fetch-mode': 'navigate',
    #                                                         'sec-fetch-user': '?1',
    #                                                         'sec-fetch-dest': 'document',
    #                                                         'accept-language': 'en-GB,en-US;q=0.9,en;q=0.8',
    #                                                     }
    #                                                     page = requests.get(link, headers=headers)
    #                                                     soup1 = BeautifulSoup(page.content, "html.parser")
    #                                                     #print(sp1)
                                                        

    #                                             except:
    #                                                     err = "Straitimes : err : Couldn't fetch url " + link 
    #                                                     print("inside_except")
    #                                                     err_logs.append(err)
    #                                                     continue
                                                
    #                                             #news tile
                                                        
                                                        
    #                                             title1=""
    #                                             if(soup1.find("h1" , {"class" : "headline"}).text !=None):
    #                                                 title1=soup1.find("h1" , {"class" : "headline"}).text
    #                                                 title1 =title1.replace("\n", "")
    #                                                 title1=title1.strip()
                                            
                                                
    #                                             #print("title:",title1) 
    #                                             title.append(title1)
                                                
    #                                             #news content
    #                                             text1=""
    #                                             if (soup1.find("div" , {"class" : "ds-field-item"})!=None):
    #                                                 articlebody=soup1.find("div" , {"class" : "ds-field-item"})
    #                                                 p_all =articlebody.find_all("p")
    #                                                 if(p_all !=None):
    #                                                     for p in p_all:
    #                                                         if(p.text!=None):                                                
    #                                                             text1 = text1 + p.text
    #                                                             #text2.append(text1)
                                                        
    #                                             #print(text1)
    #                                             text.append(text1)
                                                
                                            
    #                                             #news publish date 
    #                                             pubDate1=""
    #                                             nd=soup1.find("div" , {"class" : "group-story-postdate"})
    #                                             if(nd!=None):
    #                                                 div_postdate=nd.find("div" , {"class" : "story-postdate"})
    #                                                 if (div_postdate != None):
    #                                                     pubDate1=div_postdate.text
    #                                                     pubDate1 =pubDate1.lstrip()
    #                                             #print("pubDate1",pubDate1)
    #                                             pub_date.append(pubDate1)
                                                        
                                            
                                                

    #                                             #Scrapped date 
    #                                             scraped_date.append(str(today))
    
            
                                
    #         df = pd.DataFrame({"text" : text , "link":links,"publish_date":pub_date,"scraped_date":scraped_date,"title":title})

    #         #df=pd.DataFrame({'Title': title,'link':links,'news body':text,'pubdate':pub_date,'Scrape date':scraped_date})
    #         #print(df)
    #         if df.empty:
    #             err = "Strait times : err: Empty dataframe"
    #             err_logs.append(err)
    #         df = df.drop_duplicates(subset=["link"])
    #         df = FilterFunction(df)
    #         emptydataframe("Strait times ",df)
    #         return df
                    
    #     except:
    #         print(" Strait times not working")
    #         not_working_functions.append("Strait times")
            
    def sumatrabinis():
        
        def pageDetails(soup,err_logs,url):
            #flag to check if ,new publish date belongs to current month
            flag =0
            all_ul = soup.find_all("ul",{"class":"list-news"})
            print(len(all_ul))
            list_count=0
            for ul in all_ul:
                listitem=ul.find_all("li")
                print(len(listitem))
                for i in listitem:
                        list_count+=1
                        date1=i.find("div",{"class":"date"})
                        #chck news publish date  from front page
                        utext_main=""
                        if (date1 != None):
                            utext_main=date1.text
                            utext_main=utext_main.lstrip()
                            print(utext_main)
                            temp1_month_year=utext_main[3:7]+" "+utext_main[8:12]
                            #print(temp1_month_year)
                            currentMonth = datetime.now().month
                            currentYear = datetime.now().year
                            monthdict={1:"Januari",2:"Februari",3:"Maret",4:"April",5:"Mei",6:"Juni",7:"Juli",8:"Agustus",9:"September",10:"Oktober",11:"November",12:"Desember"}
                            currentMonthandYear=str(monthdict[currentMonth])+" "+str(currentYear)
                            print("\n\n...........\n\n")

                            print("temp1_month_year "+temp1_month_year)
                            print("currentMonthandYear " +currentMonthandYear)
                            if(temp1_month_year==currentMonthandYear):
                                print("Matched....the news belong to current month, proceed with new fetch details")
                                pub_date.append(utext_main) 
                                newDetails(i,err_logs)
                            else:
                                flag=1
                                print("inside else break")
                                break

                #print("go to next page when news are still from current month and first page listitems are read)
                if ((list_count ==10) and (flag==0) ) :
                    page11 = requests.get(url)
                    soup11 = BeautifulSoup(page11.content,"html.parser") 
                    pageobj=soup11.find('ul',{"class":"pages"})
                    print("Inside pageobj......")
                    #print(pageobj)

                    if(pageobj!=None):
                        pageobj2=pageobj.find('a',{"rel":"next"})
                        print("Inside pageob2.....")
                        if(pageobj2!=None):
                            url2=pageobj2['href']
                            print("Inside pageobj3.......")
                            #print("url",url2)
                            if (url2!=None):
                                #print("url",url2)
                                pageDetails(soup11,err_logs,url2)
        
        def newDetails(i,err_logs):
            if(i.find('h2')!=None):
                link=i.h2.a['href']
                today = date.today()
                try:
                    page1 = requests.get(link)
                    soup1 = BeautifulSoup(page1.content,"html.parser")                       
                except:
                    err = "Sumatra Bisnis : err : Couldn't fetch url " + link 
                    print("inside_except")
                    err_logs.append(err)
                    #continue

                #print(link)

                if(link!=None):
                    links.append(link)


                    #news tile
                    title1=""
                    if(soup1.find("h1" , {"class" : "title-only"}) !=None):
                        title1=soup1.find("h1" , {"class" : "title-only"}).text
                    
                    elif(soup1.find("h1",{"class":"title-premium"})!=None):
                        title1=soup1.find("h1",{"class":"title-premium"}).text
                        
                    title.append(title1)
                    print(title1)
                    
                    #news content
                    if(soup1.find("div" , {"class" : "description"})!=None):
                        articlebody=soup1.find("div" , {"class" : "description"})
                    elif(soup1.find("div" , {"itemprop" : "articleBody"})!=None):
                        articlebody=soup1.find("div" , {"itemprop" : "articleBody"})
                    text2=[]
                    if(articlebody!=None):
                        p_all =articlebody.find_all("p")
                        
                        if(p_all!=None):                               
                            for p in p_all:
                                text1=p.text
                                if(text1!=None):
                                    text2.append(text1)
                        text.append(text2)
                    #print(text2)
                    

                    #Scrapped date                      
                    scraped_date.append(str(today))
                    #print(today)      
        
        title,links,text,pub_date,scraped_date = [],[],[],[],[]
        try:
            print("Sumatra")

            
            url="https://search.bisnis.com/?q=ipo"
            domain_url = "https://sumatra.bisnis.com"
            err_logs = [] 
            try:
                page = requests.get(url)
                soup = BeautifulSoup(page.content,"html.parser")
                
            except:
                err = "Sumatra bisnis : err : Couldn't fetch " + url 
                err_logs.append(err)
                return 
            
            # for each page call the page details function
            pageDetails(soup,err_logs,url)
            
            
            #Adding to excel sheet 
            df = pd.DataFrame({"text" : text , "link":links,"publish_date":pub_date,"scraped_date":scraped_date,"title":title})
             
            #df=pd.DataFrame({'Title':title,'Link':links,'Text':text,'Publish Date':pub_date,'Scraping Date':scraped_date})
            if df.empty:
                err = "Sumatra Bisnis : err: Empty dataframe"
                err_logs.append(err)
            df = df.drop_duplicates(subset=["link"])
            df = FilterFunction(df)
            emptydataframe("Sumatra bisnis",df)
            
            return df
            
              
                
        except:
            print(" Sumatra bisnis not working")
            not_working_functions.append("Sumatra Bisnis")
    
    def techstory():
        
        import traceback
        titles,links,text,pub_date,scrape_date=[],[],[],[],[]
        err_logs=[]
        url="https://techstory.in/?s=ipo"

        try:
            
            html=requests.get(url)
            soup1=BeautifulSoup(html.content,"html.parser")
            articles=soup1.find_all('article')
        
            # to get the news details that are published in the current month       
                            
            if (articles!= None):
                for article in articles:
                    publishdatecheck=article.find('time')
                    publishdateold=publishdatecheck.text.strip()
                    if (len(publishdateold) ==15):
                        publishdateold=publishdateold[0:3]+" "+publishdateold[11:15]
                    elif (len(publishdateold)==14):
                        publishdateold=publishdateold[0:3]+" "+publishdateold[10:14]
                    #print(currentmonthandyear)
                    currentMonth = datetime.now().month
                    currentYear = datetime.now().year
                    monthdict={1:"Jan",2:"Feb",3:"Mar",4:"Apr",5:"May",6:"Jun",7:"Jul",8:"Aug",9:"Sep",10:"Oct",11:"Nov",12:"Dec"}
                    currentmonthandyear=str(monthdict[currentMonth])+" "+str(currentYear)
                    
                    
                    if(publishdateold==currentmonthandyear):

                        h2find=article.find('h2',{"class":"cb-post-title"})
                        #print(h2find)
                        if (h2find !=None):
                            a=h2find.find('a')
                            href=a['href']
                            links.append(href)
                            if (href!=None):
                            
                                html1=requests.get(href).text
                            
                                soup2=BeautifulSoup(html1,'lxml')
                                #get news title
                                
                                title=soup2.find('h1',{"class":"entry-title cb-entry-title entry-title cb-title"})
                                titletext=""
                                if(title!=None):
                                    titletext=title.text
                                titles.append(titletext)
                                #print(titletext)
                                
                                # News Content
                                text1=soup2.find('span',{"class":"cb-itemprop"})
                                paragraph_main=""
                                if (text1 !=None) :
                                    ptagsfind=text1.find_all('p')
                                    if (ptagsfind!=None):
                                        for p in ptagsfind:
                                            paragraph_main=paragraph_main+p.text
                                text.append(paragraph_main)
                                
                                # Publish Date
                                publish_date=""
                                datefind=soup2.find('time',{"class":"updated"})
                                if (datefind!=None):
                                    publish_date=datefind.text
                                pub_date.append(publish_date)
                                #Scrape date 

                                today=date.today()
                                scrape_date.append(today)
                    
                    df = pd.DataFrame({"text" : text , "link":links,"publish_date":pub_date,"scraped_date":scrape_date,"title":titles})

                    #df=pd.DataFrame({'Title': titles,'link':links,'news body':text,'pubdate':pub_date,'Scrape date':scrape_date})
                    if df.empty:
                        err = "techstory : err: Empty dataframe"
                        err_logs.append(err)
                    df = df.drop_duplicates(subset=["link"])
                    df = FilterFunction(df)
                    emptydataframe("Techstory",df)
                    return df




        except:
            print("Techstory Not Working")  
            not_working_functions.append("Techstory ") 
    def etfdailynews():
        try:
            print("etfdailynews")
            url = "https://www.etfdailynews.com/?s=ipo"
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
            page = requests.get(url, headers=headers)
            soup = BeautifulSoup(page.content, "html.parser")
            # soup  # Debugging - if soup is working correctly

            # Class names of the elements to be scraped
            section_class="archive" # Class name of div containing the a tag
            #h1_class = "_1Y-96"
            #h1_div_class = "col-xs-12"
            title_h1_itemprop= "headline"
            date_span_itemprop= ["datePublished dateModified"]
            para_div_class=["entry"]

            links = []

            for divtag in soup.find_all("section", {"class": section_class}):
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
            # links # Debugging - if link array is generated

            collection = []
            err_logs = []
            scrapper_name = "etfdailynews"

            for link in links:
                try:
                    l_page = requests.get(link, headers=headers)
                    l_soup = BeautifulSoup(l_page.content, 'html.parser')
                except:
                    err = scrapper_name + ": err: Failed to retrieve data from link: " + link + " and convert it to soup object"
                    err_logs.append(err)
                    continue

                data = []
                # Scraping the heading
                #h1_ele = l_soup.find("h1", {"class": h1_class})
                
                try:
                    title_ele = l_soup.find("h1", {"itemprop": title_h1_itemprop})
                    title_text = title_ele.text
                    title_text = title_text.strip("\n ")
                    data.append(title_text)
                except:
                    err = scrapper_name + ": err: Failed to find title in page. Link: " + link
                    err_logs.append(err)
                    continue  # drops the complete data if there is an error


                # Adding the link to data
                data.append(link)

                # Scraping the published date
                try:
                    date_ele = l_soup.find("span", {"itemprop": date_span_itemprop})
                    date_text = date_ele.text
                    date_text = date_text.strip("\n ")
                    date_text = " ".join(date_text.split()[:3])
                    #date_text = date_text.replace(" Updated: ", "")
                    data.append(date_text)  # The date_text could be further modified to represent a proper date format
                except:
                    err = scrapper_name + ": err: Failed to find date in page. Link: " + link
                    err_logs.append(err)
                    continue  # drops the complete data if there is an error
                
                # Adding the scraped date to data
                cur_date = str(datetime.today())
                data.append(cur_date)
                

                # Scraping the paragraph
                try:
                    para_ele = (l_soup.findAll("div", {"class": para_div_class}))[-1]
                    para_text = para_ele.text
                    para_text = para_text.strip("\n ")
                    data.append(para_text)  # Need to make this better
                except:
                    err = scrapper_name + ": err: Failed to find paragraph in page. Link: " + link
                    err_logs.append(err)
                    continue  # drops the complete data if there is an error
                # Adding data to a collection
                collection.append(data)

            df = pd.DataFrame(collection, columns =['title', 'link','publish_date','scraped_date','text'])
            if df.empty:
                err = scrapper_name + ": err: Empty dataframe"
                err_logs.append(err)
            # print(df) # For debugging. To check if df is created
            # print(err_logs) # For debugging - to check if any errors occoured
            df = FilterFunction(df)
            emptydataframe("etfdailynews",df)
            return df
        except:
            print("etfdailynews not working")
            not_working_functions.append("etfdailynews") 
    def splash247():
        try:
            print("splash247")
            url = "https://splash247.com/?s=ipo"
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
            page = requests.get(url, headers=headers)
            soup = BeautifulSoup(page.content, "html.parser")
            # soup  # Debugging - if soup is working correctly

            # Class names of the elements to be scraped
            div_class="post-details" # Class name of div containing the a tag
            #h1_class = "_1Y-96"
            #h1_div_class = "col-xs-12"
            title_h1_class= "post-title entry-title"
            date_span_class= ["date meta-item tie-icon"]
            para_div_class=["entry-content entry clearfix"]

            links = []

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
            # links # Debugging - if link array is generated

            collection = []
            err_logs = []
            scrapper_name = "splash247"

            for link in links:
                try:
                    l_page = requests.get(link, headers=headers)
                    l_soup = BeautifulSoup(l_page.content, 'html.parser')
                except:
                    err = scrapper_name + ": err: Failed to retrieve data from link: " + link + " and convert it to soup object"
                    err_logs.append(err)
                    continue

                data = []
                # Scraping the heading
                #h1_ele = l_soup.find("h1", {"class": h1_class})
                
                try:
                    title_ele = l_soup.find("h1", {"class": title_h1_class})
                    title_text = title_ele.text
                    title_text = title_text.strip("\n ")
                    data.append(title_text)
                except:
                    err = scrapper_name + ": err: Failed to find title in page. Link: " + link
                    err_logs.append(err)
                    continue  # drops the complete data if there is an error


                # Adding the link to data
                data.append(link)

                # Scraping the published date
                try:
                    date_ele = l_soup.find("span", {"class": date_span_class})
                    date_text = date_ele.text
                    date_text = date_text.strip("\n ")
                    date_text = " ".join(date_text.split()[:3])
                    #date_text = date_text.replace(" Updated: ", "")
                    data.append(date_text)  # The date_text could be further modified to represent a proper date format
                except:
                    err = scrapper_name + ": err: Failed to find date in page. Link: " + link
                    err_logs.append(err)
                    continue  # drops the complete data if there is an error
                
                # Adding the scraped date to data
                cur_date = str(datetime.today())
                data.append(cur_date)
                

                # Scraping the paragraph
                try:
                    para_ele = (l_soup.findAll("div", {"class": para_div_class}))[-1]
                    para_text = para_ele.text
                    para_text = para_text.strip("\n ")
                    data.append(para_text)  # Need to make this better
                except:
                    err = scrapper_name + ": err: Failed to find paragraph in page. Link: " + link
                    err_logs.append(err)
                    continue  # drops the complete data if there is an error
                # Adding data to a collection
                collection.append(data)

            df = pd.DataFrame(collection, columns =['title', 'link','publish_date','scraped_date','text'])
            if df.empty:
                err = scrapper_name + ": err: Empty dataframe"
                err_logs.append(err)
            # print(df) # For debugging. To check if df is created
            # print(err_logs) # For debugging - to check if any errors occoured
            df = FilterFunction(df)
            emptydataframe("splash247",df)
            return df
        except:
            print("splash247 not working")
            not_working_functions.append("splash247")
    def theepochtimes():
        try:
            print("theepochtimes")
            url = "https://www.theepochtimes.com/search/?q=ipo&t=ai"
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
            page = requests.get(url, headers=headers)
            soup = BeautifulSoup(page.content, "html.parser")
            # soup  # Debugging - if soup is working correctly

            # Class names of the elements to be scraped
            li_class="post_list" # Class name of div containing the a tag
            #h1_class = "_1Y-96"
            #h1_div_class = "col-xs-12"
            title_div_class= "title"
            date_span_class= ["time"]
            para_div_class=["post_content"]

            links = []

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
            # links # Debugging - if link array is generated

            collection = []
            err_logs = []
            scrapper_name = "theepochtimes"

            for link in links:
                try:
                    l_page = requests.get(link, headers=headers)
                    l_soup = BeautifulSoup(l_page.content, 'html.parser')
                except:
                    err = scrapper_name + ": err: Failed to retrieve data from link: " + link + " and convert it to soup object"
                    err_logs.append(err)
                    continue

                data = []
                # Scraping the heading
                #h1_ele = l_soup.find("h1", {"class": h1_class})
                
                try:
                    title_ele = l_soup.find("div", {"class": title_div_class})
                    title_text = title_ele.text
                    title_text = title_text.strip("\n ")
                    data.append(title_text)
                except:
                    err = scrapper_name + ": err: Failed to find title in page. Link: " + link
                    err_logs.append(err)
                    continue  # drops the complete data if there is an error


                # Adding the link to data
                data.append(link)

                # Scraping the published date
                try:
                    date_ele = l_soup.find("span", {"class": date_span_class})
                    date_text = date_ele.text
                    date_text = date_text.strip("\n ")
                    date_text = " ".join(date_text.split()[:3])
                    #date_text = date_text.replace(" Updated: ", "")
                    data.append(date_text)  # The date_text could be further modified to represent a proper date format
                except:
                    err = scrapper_name + ": err: Failed to find date in page. Link: " + link
                    err_logs.append(err)
                    continue  # drops the complete data if there is an error
                
                # Adding the scraped date to data
                cur_date = str(datetime.today())
                data.append(cur_date)
                

                # Scraping the paragraph
                try:
                    para_ele = (l_soup.findAll("div", {"class": para_div_class}))[-1]
                    para_text = para_ele.text
                    para_text = para_text.strip("\n ")
                    data.append(para_text)  # Need to make this better
                except:
                    err = scrapper_name + ": err: Failed to find paragraph in page. Link: " + link
                    err_logs.append(err)
                    continue  # drops the complete data if there is an error
                # Adding data to a collection
                collection.append(data)

            df = pd.DataFrame(collection, columns =['title', 'link','publish_date','scraped_date','text'])
            if df.empty:
                err = scrapper_name + ": err: Empty dataframe"
                err_logs.append(err)
            # print(df) # For debugging. To check if df is created
            # print(err_logs) # For debugging - to check if any errors occoured
            df = FilterFunction(df)
            emptydataframe("theepochtimes",df)
            return df
        except:
            print("theepochtimes not working")
            not_working_functions.append("theepochtimes")
    def brisbanetimes():
        try:
            print("brisbanetimes")
            url = "https://www.brisbanetimes.com.au/search?text=ipo"
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
            page = requests.get(url, headers=headers)
            soup = BeautifulSoup(page.content, "html.parser")
            # soup  # Debugging - if soup is working correctly

            # Class names of the elements to be scraped
            div_class="_2g9tm" # Class name of div containing the a tag
            #h1_class = "_1Y-96"
            #h1_div_class = "col-xs-12"
            title_h1_itemprop= "headline"
            date_span_class= ["_2xetH"]
            para_div_class=["_1665V _2q-Vk"]

            links = []

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
            # links # Debugging - if link array is generated

            collection = []
            err_logs = []
            scrapper_name = "brisbanetimes"

            for link in links:
                try:
                    l_page = requests.get(link, headers=headers)
                    l_soup = BeautifulSoup(l_page.content, 'html.parser')
                except:
                    err = scrapper_name + ": err: Failed to retrieve data from link: " + link + " and convert it to soup object"
                    err_logs.append(err)
                    continue

                data = []
                # Scraping the heading
                #h1_ele = l_soup.find("h1", {"class": h1_class})
                
                try:
                    title_ele = l_soup.find("h1", {"itemprop": title_h1_itemprop})
                    title_text = title_ele.text
                    title_text = title_text.strip("\n ")
                    data.append(title_text)
                except:
                    err = scrapper_name + ": err: Failed to find title in page. Link: " + link
                    err_logs.append(err)
                    continue  # drops the complete data if there is an error


                # Adding the link to data
                data.append(link)

                # Scraping the published date
                try:
                    date_ele = l_soup.find("span", {"class": date_span_class})
                    date_text = date_ele.text
                    date_text = date_text.strip("\n ")
                    date_text = " ".join(date_text.split()[:3])
                    #date_text = date_text.replace(" Updated: ", "")
                    data.append(date_text)  # The date_text could be further modified to represent a proper date format
                except:
                    err = scrapper_name + ": err: Failed to find date in page. Link: " + link
                    err_logs.append(err)
                    continue  # drops the complete data if there is an error
                
                # Adding the scraped date to data
                cur_date = str(datetime.today())
                data.append(cur_date)
                

                # Scraping the paragraph
                try:
                    para_ele = (l_soup.findAll("div", {"class": para_div_class}))[-1]
                    para_text = para_ele.text
                    para_text = para_text.strip("\n ")
                    data.append(para_text)  # Need to make this better
                except:
                    err = scrapper_name + ": err: Failed to find paragraph in page. Link: " + link
                    err_logs.append(err)
                    continue  # drops the complete data if there is an error
                # Adding data to a collection
                collection.append(data)

            df = pd.DataFrame(collection, columns =['title', 'link','publish_date','scraped_date','text'])
            if df.empty:
                err = scrapper_name + ": err: Empty dataframe"
                err_logs.append(err)
            # print(df) # For debugging. To check if df is created
            # print(err_logs) # For debugging - to check if any errors occoured
            df = FilterFunction(df)
            emptydataframe("brisbanetimes",df)
            return df
        except:
            print("brisbanetimes not working")
            not_working_functions.append("brisbanetimes")
    def thenewsminute():
        try:
            print("thenewsminute")
            url = "https://www.thenewsminute.com/search?s=ipo"
            domain_url = "https://www.thenewsminute.com/"

            headers = {
                "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10.15; rv:78.0) Gecko/20100101 Firefox/78.0",
                "accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.9",
                'sec-fetch-site': 'none',
                'sec-fetch-mode': 'navigate',
                'sec-fetch-user': '?1',
                'sec-fetch-dest': 'document',
                'accept-language': 'en-GB,en-US;q=0.9,en;q=0.8',
            }
            page = requests.get(url, headers=headers)
            soup = BeautifulSoup(page.content, "html.parser")
            # soup  # Debugging - if soup is working correctly

            # Class names of the elements to be scraped
            div_class="col-8 col-md-9 text-wrap" # Class name of div containing the a tag
            #h1_class = "_1Y-96"
            #h1_div_class = "col-xs-12"
            title_h1_class= "article-title"
            date_span_class= ["time createddate"]
            para_p_class=["_yeti_done"]

            links = []

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
            # links # Debugging - if link array is generated

            collection = []
            err_logs = []
            scrapper_name = "thenewsminute"

            for link in links:
                try:
                    l_page = requests.get(link, headers=headers)
                    l_soup = BeautifulSoup(l_page.content, 'html.parser')
                except:
                    err = scrapper_name + ": err: Failed to retrieve data from link: " + link + " and convert it to soup object"
                    err_logs.append(err)
                    continue

                data = []
                # Scraping the heading
                #h1_ele = l_soup.find("h1", {"class": h1_class})
                
                try:
                    title_ele = l_soup.find("h1", {"class": title_h1_class})
                    title_text = title_ele.text
                    title_text = title_text.strip("\n ")
                    data.append(title_text)
                except:
                    err = scrapper_name + ": err: Failed to find title in page. Link: " + link
                    err_logs.append(err)
                    continue  # drops the complete data if there is an error


                # Adding the link to data
                data.append(link)

                # Scraping the published date
                try:
                    date_ele = l_soup.find("span", {"class": date_span_class})
                    date_text = date_ele.text
                    date_text = date_text.strip("\n ")
                    date_text = " ".join(date_text.split()[:3])
                    #date_text = date_text.replace(" Updated: ", "")
                    data.append(date_text)  # The date_text could be further modified to represent a proper date format
                except:
                    err = scrapper_name + ": err: Failed to find date in page. Link: " + link
                    err_logs.append(err)
                    continue  # drops the complete data if there is an error
                
                # Adding the scraped date to data
                cur_date = str(datetime.today())
                data.append(cur_date)
                

                # Scraping the paragraph
                try:
                    para_ele = (l_soup.findAll("p"))[-1]
                    para_text = para_ele.text
                    para_text = para_text.strip("\n ")
                    data.append(para_text)  # Need to make this better
                except:
                    err = scrapper_name + ": err: Failed to find paragraph in page. Link: " + link
                    err_logs.append(err)
                    continue  # drops the complete data if there is an error
                # Adding data to a collection
                collection.append(data)

            df = pd.DataFrame(collection, columns =['title', 'link','publish_date','scraped_date','text'])
            if df.empty:
                err = scrapper_name + ": err: Empty dataframe"
                err_logs.append(err)
            # print(df) # For debugging. To check if df is created
            # print(err_logs) # For debugging - to check if any errors occoured
            df = FilterFunction(df)
            emptydataframe("thenewsminute",df)
            return df
        except:
            print("thenewsminute not working")
            not_working_functions.append("thenewsminute")
    def koreatechdesk():
        try:
            print("koreatechdesk")
            url = "https://www.koreatechdesk.com/?s=ipo"
            domain_url = "https://www.koreatechdesk.com/"

            headers = {
                "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10.15; rv:78.0) Gecko/20100101 Firefox/78.0",
                "accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.9",
                'sec-fetch-site': 'none',
                'sec-fetch-mode': 'navigate',
                'sec-fetch-user': '?1',
                'sec-fetch-dest': 'document',
                'accept-language': 'en-GB,en-US;q=0.9,en;q=0.8',
            }
            page = requests.get(url, headers=headers)
            soup = BeautifulSoup(page.content, "html.parser")
            # soup  # Debugging - if soup is working correctly

            # Class names of the elements to be scraped
            div_class="jeg_postblock_content" # Class name of div containing the a tag
            #h1_class = "_1Y-96"
            #h1_div_class = "col-xs-12"
            title_h1_class= "jeg_post_title"
            date_div_class= ["jeg_meta_date"]
            para_div_class=["jeg_post_excerpt"]

            links = []

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
            # links # Debugging - if link array is generated

            collection = []
            err_logs = []
            scrapper_name = "koreatechdesk"

            for link in links:
                try:
                    l_page = requests.get(link, headers=headers)
                    l_soup = BeautifulSoup(l_page.content, 'html.parser')
                except:
                    err = scrapper_name + ": err: Failed to retrieve data from link: " + link + " and convert it to soup object"
                    err_logs.append(err)
                    continue

                data = []
                # Scraping the heading
                #h1_ele = l_soup.find("h1", {"class": h1_class})
                
                try:
                    title_ele = l_soup.find("h1", {"class": title_h1_class})
                    title_text = title_ele.text
                    title_text = title_text.strip("\n ")
                    data.append(title_text)
                except:
                    err = scrapper_name + ": err: Failed to find title in page. Link: " + link
                    err_logs.append(err)
                    continue  # drops the complete data if there is an error


                # Adding the link to data
                data.append(link)

                # Scraping the published date
                try:
                    date_ele = l_soup.find("div", {"class": date_div_class})
                    date_text = date_ele.text
                    date_text = date_text.strip("\n ")
                    date_text = " ".join(date_text.split()[:3])
                    #date_text = date_text.replace(" Updated: ", "")
                    data.append(date_text)  # The date_text could be further modified to represent a proper date format
                except:
                    err = scrapper_name + ": err: Failed to find date in page. Link: " + link
                    err_logs.append(err)
                    continue  # drops the complete data if there is an error
                
                # Adding the scraped date to data
                cur_date = str(datetime.today())
                data.append(cur_date)
                

                # Scraping the paragraph
                try:
                    para_ele = (l_soup.findAll("p"))[-1]
                    para_text = para_ele.text
                    para_text = para_text.strip("\n ")
                    data.append(para_text)  # Need to make this better
                except:
                    err = scrapper_name + ": err: Failed to find paragraph in page. Link: " + link
                    err_logs.append(err)
                    continue  # drops the complete data if there is an error
                # Adding data to a collection
                collection.append(data)

            df = pd.DataFrame(collection, columns =['title', 'link','publish_date','scraped_date','text'])
            if df.empty:
                err = scrapper_name + ": err: Empty dataframe"
                err_logs.append(err)
            # print(df) # For debugging. To check if df is created
            # print(err_logs) # For debugging - to check if any errors occoured
            df = FilterFunction(df)
            emptydataframe("koreatechdesk",df)
            return df
        except:
            print("koreatechdesk not working")
            not_working_functions.append("koreatechdesk")
    def globalonlinemony():
        try:
            print("globalonlinemony")
            url = "https://globalonlinemony.com/?s=ipo"
            domain_url = "https://globalonlinemony.com/"

            headers = {
                "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10.15; rv:78.0) Gecko/20100101 Firefox/78.0",
                "accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.9",
                'sec-fetch-site': 'none',
                'sec-fetch-mode': 'navigate',
                'sec-fetch-user': '?1',
                'sec-fetch-dest': 'document',
                'accept-language': 'en-GB,en-US;q=0.9,en;q=0.8',
            }
            page = requests.get(url, headers=headers)
            soup = BeautifulSoup(page.content, "html.parser")
            # soup  # Debugging - if soup is working correctly

            # Class names of the elements to be scraped
            div_class="item-details" # Class name of div containing the a tag
            #h1_class = "_1Y-96"
            #h1_div_class = "col-xs-12"
            title_h1_class= "entry-title"
            date_time_class= ["entry-date updated td-module-date"]
            para_div_class=["td-post-content"]

            links = []

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
            # links # Debugging - if link array is generated

            collection = []
            err_logs = []
            scrapper_name = "globalonlinemony"

            for link in links:
                try:
                    l_page = requests.get(link, headers=headers)
                    l_soup = BeautifulSoup(l_page.content, 'html.parser')
                except:
                    err = scrapper_name + ": err: Failed to retrieve data from link: " + link + " and convert it to soup object"
                    err_logs.append(err)
                    continue

                data = []
                # Scraping the heading
                #h1_ele = l_soup.find("h1", {"class": h1_class})
                
                try:
                    title_ele = l_soup.find("h1", {"class": title_h1_class})
                    title_text = title_ele.text
                    title_text = title_text.strip("\n ")
                    data.append(title_text)
                except:
                    err = scrapper_name + ": err: Failed to find title in page. Link: " + link
                    err_logs.append(err)
                    continue  # drops the complete data if there is an error


                # Adding the link to data
                data.append(link)

                # Scraping the published date
                try:
                    date_ele = l_soup.find("time", {"class": date_time_class})
                    date_text = date_ele.text
                    date_text = date_text.strip("\n ")
                    date_text = " ".join(date_text.split()[:3])
                    #date_text = date_text.replace(" Updated: ", "")
                    data.append(date_text)  # The date_text could be further modified to represent a proper date format
                except:
                    err = scrapper_name + ": err: Failed to find date in page. Link: " + link
                    err_logs.append(err)
                    continue  # drops the complete data if there is an error
                
                # Adding the scraped date to data
                cur_date = str(datetime.today())
                data.append(cur_date)
                

                # Scraping the paragraph
                try:
                    para_ele = (l_soup.findAll("div", {"class": para_div_class}))[-1]
                    para_text = para_ele.text
                    para_text = para_text.strip("\n ")
                    data.append(para_text)  # Need to make this better
                except:
                    err = scrapper_name + ": err: Failed to find paragraph in page. Link: " + link
                    err_logs.append(err)
                    continue  # drops the complete data if there is an error
                # Adding data to a collection
                collection.append(data)

            df = pd.DataFrame(collection, columns =['title', 'link','publish_date','scraped_date','text'])
            if df.empty:
                err = scrapper_name + ": err: Empty dataframe"
                err_logs.append(err)
            # print(df) # For debugging. To check if df is created
            # print(err_logs) # For debugging - to check if any errors occoured
            df = FilterFunction(df)
            emptydataframe("globalonlinemony",df)
            return df
        except:
            print("globalonlinemony not working")
            not_working_functions.append("globalonlinemony")
    def zdnet():
        try:
            print("zdnet")
            url = "https://www.zdnet.com/search/?q=ipo"
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
            page = requests.get(url, headers=headers)
            soup = BeautifulSoup(page.content, "html.parser")
            # soup  # Debugging - if soup is working correctly

            # Class names of the elements to be scraped
            article_class="item"# Class name of div containing the a tag
            #h1_class = "_1Y-96"
            #h1_div_class = "col-xs-12"
            title_h1_class= "c-contentHeader_headline g-outer-spacing-top-medium g-outer-spacing-bottom-medium"
            date_time_class= ["c-globalAuthor_time"]
            para_div_class=["c-ShortcodeContent"]

            links = []

            for divtag in soup.find_all("article", {"class": article_class}):
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
            # links # Debugging - if link array is generated

            collection = []
            err_logs = []
            scrapper_name = "zdnet"

            for link in links:
                try:
                    l_page = requests.get(link, headers=headers)
                    l_soup = BeautifulSoup(l_page.content, 'html.parser')
                except:
                    err = scrapper_name + ": err: Failed to retrieve data from link: " + link + " and convert it to soup object"
                    err_logs.append(err)
                    continue

                data = []
                # Scraping the heading
                #h1_ele = l_soup.find("h1", {"class": h1_class})
                
                try:
                    title_ele = l_soup.find("h1", {"class": title_h1_class})
                    title_text = title_ele.text
                    title_text = title_text.strip("\n ")
                    data.append(title_text)
                except:
                    err = scrapper_name + ": err: Failed to find title in page. Link: " + link
                    err_logs.append(err)
                    continue  # drops the complete data if there is an error


                # Adding the link to data
                data.append(link)

                # Scraping the published date
                try:
                    date_ele = l_soup.find("time", {"class": date_time_class})
                    date_text = date_ele.text
                    date_text = date_text.strip("\n ")
                    date_text = " ".join(date_text.split()[:3])
                    #date_text = date_text.replace(" Updated: ", "")
                    data.append(date_text)  # The date_text could be further modified to represent a proper date format
                except:
                    err = scrapper_name + ": err: Failed to find date in page. Link: " + link
                    err_logs.append(err)
                    continue  # drops the complete data if there is an error
                
                # Adding the scraped date to data
                cur_date = str(datetime.today())
                data.append(cur_date)
                

                # Scraping the paragraph
                try:
                    para_ele = (l_soup.findAll("div", {"class": para_div_class}))[-1]
                    para_text = para_ele.text
                    para_text = para_text.strip("\n ")
                    data.append(para_text)  # Need to make this better
                except:
                    err = scrapper_name + ": err: Failed to find paragraph in page. Link: " + link
                    err_logs.append(err)
                    continue  # drops the complete data if there is an error
                # Adding data to a collection
                collection.append(data)

            df = pd.DataFrame(collection, columns =['title', 'link','publish_date','scraped_date','text'])
            if df.empty:
                err = scrapper_name + ": err: Empty dataframe"
                err_logs.append(err)
            # print(df) # For debugging. To check if df is created
            # print(err_logs) # For debugging - to check if any errors occoured
            df = FilterFunction(df)
            emptydataframe("zdnet",df)
            return df
        except:
            print("zdnet not working")
            not_working_functions.append("zdnet")
    def manilatimes():
        try:
            print("manilatimes")
            url = "https://www.manilatimes.net/search?query=ipo"
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
            page = requests.get(url, headers=headers)
            soup = BeautifulSoup(page.content, "html.parser")
            # soup  # Debugging - if soup is working correctly

            # Class names of the elements to be scraped
            div_class="col-content-1"# Class name of div containing the a tag
            #h1_class = "_1Y-96"
            #h1_div_class = "col-xs-12"
            title_h1_class= "article-title font-700 roboto-slab-3 tdb-title-text"
            date_div_class= ["article-publish-time roboto-a"]
            para_div_class=["article-body tdb-block-inner"]

            links = []

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
            # links # Debugging - if link array is generated

            collection = []
            err_logs = []
            scrapper_name = "manilatimes"

            for link in links:
                try:
                    l_page = requests.get(link, headers=headers)
                    l_soup = BeautifulSoup(l_page.content, 'html.parser')
                except:
                    err = scrapper_name + ": err: Failed to retrieve data from link: " + link + " and convert it to soup object"
                    err_logs.append(err)
                    continue

                data = []
                # Scraping the heading
                #h1_ele = l_soup.find("h1", {"class": h1_class})
                
                try:
                    title_ele = l_soup.find("h1", {"class": title_h1_class})
                    title_text = title_ele.text
                    title_text = title_text.strip("\n ")
                    data.append(title_text)
                except:
                    err = scrapper_name + ": err: Failed to find title in page. Link: " + link
                    err_logs.append(err)
                    continue  # drops the complete data if there is an error


                # Adding the link to data
                data.append(link)

                # Scraping the published date
                try:
                    date_ele = l_soup.find("div", {"class": date_div_class})
                    date_text = date_ele.text
                    date_text = date_text.strip("\n ")
                    date_text = " ".join(date_text.split()[:3])
                    #date_text = date_text.replace(" Updated: ", "")
                    data.append(date_text)  # The date_text could be further modified to represent a proper date format
                except:
                    err = scrapper_name + ": err: Failed to find date in page. Link: " + link
                    err_logs.append(err)
                    continue  # drops the complete data if there is an error
                
                # Adding the scraped date to data
                cur_date = str(datetime.today())
                data.append(cur_date)
                

                # Scraping the paragraph
                try:
                    para_ele = (l_soup.findAll("div", {"class": para_div_class}))[-1]
                    para_text = para_ele.text
                    para_text = para_text.strip("\n ")
                    data.append(para_text)  # Need to make this better
                except:
                    err = scrapper_name + ": err: Failed to find paragraph in page. Link: " + link
                    err_logs.append(err)
                    continue  # drops the complete data if there is an error
                # Adding data to a collection
                collection.append(data)

            df = pd.DataFrame(collection, columns =['title', 'link','publish_date','scraped_date','text'])
            if df.empty:
                err = scrapper_name + ": err: Empty dataframe"
                err_logs.append(err)
            # print(df) # For debugging. To check if df is created
            # print(err_logs) # For debugging - to check if any errors occoured
            df = FilterFunction(df)
            emptydataframe("manilatimes",df)
            return df
        except:
            print("manilatimes not working")
            not_working_functions.append("manilatimes")
    def alphastreet():
        try:
            print("alphastreet")
            url = "https://news.alphastreet.com/?post_type=post&s=ipo"
            domain_url = "https://news.alphastreet.com/"

            headers = {
                "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10.15; rv:78.0) Gecko/20100101 Firefox/78.0",
                "accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.9",
                'sec-fetch-site': 'none',
                'sec-fetch-mode': 'navigate',
                'sec-fetch-user': '?1',
                'sec-fetch-dest': 'document',
                'accept-language': 'en-GB,en-US;q=0.9,en;q=0.8',
            }
            page = requests.get(url, headers=headers)
            soup = BeautifulSoup(page.content, "html.parser")
            # soup  # Debugging - if soup is working correctly

            # Class names of the elements to be scraped
            div_class="post_wrapper post_wrap_170616 post_1"# Class name of div containing the a tag
            #h1_class = "_1Y-96"
            #h1_div_class = "col-xs-12"
            title_h1_class= "post-title"
            date_time_class= ["entry-date published"]
            para_div_class=["col-md-9"]

            links = []

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
            # links # Debugging - if link array is generated

            collection = []
            err_logs = []
            scrapper_name = "alphastreet"

            for link in links:
                try:
                    l_page = requests.get(link, headers=headers)
                    l_soup = BeautifulSoup(l_page.content, 'html.parser')
                except:
                    err = scrapper_name + ": err: Failed to retrieve data from link: " + link + " and convert it to soup object"
                    err_logs.append(err)
                    continue

                data = []
                # Scraping the heading
                #h1_ele = l_soup.find("h1", {"class": h1_class})
                
                try:
                    title_ele = l_soup.find("h1", {"class": title_h1_class})
                    title_text = title_ele.text
                    title_text = title_text.strip("\n ")
                    data.append(title_text)
                except:
                    err = scrapper_name + ": err: Failed to find title in page. Link: " + link
                    err_logs.append(err)
                    continue  # drops the complete data if there is an error


                # Adding the link to data
                data.append(link)

                # Scraping the published date
                try:
                    date_ele = l_soup.find("time", {"class": date_time_class})
                    date_text = date_ele.text
                    date_text = date_text.strip("\n ")
                    date_text = " ".join(date_text.split()[:3])
                    #date_text = date_text.replace(" Updated: ", "")
                    data.append(date_text)  # The date_text could be further modified to represent a proper date format
                except:
                    err = scrapper_name + ": err: Failed to find date in page. Link: " + link
                    err_logs.append(err)
                    continue  # drops the complete data if there is an error
                
                # Adding the scraped date to data
                cur_date = str(datetime.today())
                data.append(cur_date)
                

                # Scraping the paragraph
                try:
                    para_ele = (l_soup.findAll("div", {"class": para_div_class}))[-1]
                    para_text = para_ele.text
                    para_text = para_text.strip("\n ")
                    data.append(para_text)  # Need to make this better
                except:
                    err = scrapper_name + ": err: Failed to find paragraph in page. Link: " + link
                    err_logs.append(err)
                    continue  # drops the complete data if there is an error
                # Adding data to a collection
                collection.append(data)

            df = pd.DataFrame(collection, columns =['title', 'link','publish_date','scraped_date','text'])
            if df.empty:
                err = scrapper_name + ": err: Empty dataframe"
                err_logs.append(err)
            # print(df) # For debugging. To check if df is created
            # print(err_logs) # For debugging - to check if any errors occoured
            df = FilterFunction(df)
            emptydataframe("alphastreet",df)
            return df
        except:
            print("alphastreet not working")
            not_working_functions.append("alphastreet")
    def defenseworld():
        try:
            print("defenseworld")
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
            page = requests.get(url, headers=headers)
            soup = BeautifulSoup(page.content, "html.parser")
            # soup  # Debugging - if soup is working correctly

            # Class names of the elements to be scraped
            div_class="entry"# Class name of div containing the a tag
            #h1_class = "_1Y-96"
            #h1_div_class = "col-xs-12"
            title_h1_itemprop= "headline"
            date_span_itemprop= ["datePublished dateModified"]
            para_div_class=["entry"]

            links = []

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
            # links # Debugging - if link array is generated

            collection = []
            err_logs = []
            scrapper_name = "defenseworld"

            for link in links:
                try:
                    l_page = requests.get(link, headers=headers)
                    l_soup = BeautifulSoup(l_page.content, 'html.parser')
                except:
                    err = scrapper_name + ": err: Failed to retrieve data from link: " + link + " and convert it to soup object"
                    err_logs.append(err)
                    continue

                data = []
                # Scraping the heading
                #h1_ele = l_soup.find("h1", {"class": h1_class})
                
                try:
                    title_ele = l_soup.find("h1", {"itemprop": title_h1_itemprop})
                    title_text = title_ele.text
                    title_text = title_text.strip("\n ")
                    data.append(title_text)
                except:
                    err = scrapper_name + ": err: Failed to find title in page. Link: " + link
                    err_logs.append(err)
                    continue  # drops the complete data if there is an error


                # Adding the link to data
                data.append(link)

                # Scraping the published date
                try:
                    date_ele = l_soup.find("span", {"itemprop": date_span_itemprop})
                    date_text = date_ele.text
                    date_text = date_text.strip("\n ")
                    date_text = " ".join(date_text.split()[:3])
                    #date_text = date_text.replace(" Updated: ", "")
                    data.append(date_text)  # The date_text could be further modified to represent a proper date format
                except:
                    err = scrapper_name + ": err: Failed to find date in page. Link: " + link
                    err_logs.append(err)
                    continue  # drops the complete data if there is an error
                
                # Adding the scraped date to data
                cur_date = str(datetime.today())
                data.append(cur_date)
                

                # Scraping the paragraph
                try:
                    para_ele = (l_soup.findAll("div", {"class": para_div_class}))[-1]
                    para_text = para_ele.text
                    para_text = para_text.strip("\n ")
                    data.append(para_text)  # Need to make this better
                except:
                    err = scrapper_name + ": err: Failed to find paragraph in page. Link: " + link
                    err_logs.append(err)
                    continue  # drops the complete data if there is an error
                # Adding data to a collection
                collection.append(data)

            df = pd.DataFrame(collection, columns =['title', 'link','publish_date','scraped_date','text'])
            if df.empty:
                err = scrapper_name + ": err: Empty dataframe"
                err_logs.append(err)
            # print(df) # For debugging. To check if df is created
            # print(err_logs) # For debugging - to check if any errors occoured
            df = FilterFunction(df)
            emptydataframe("defenseworld",df)
            return df
        except:
            print("defenseworld not working")
            not_working_functions.append("defenseworld")
    def investmentweek():
        try:
            print("investmentweek")
            url = "https://www.investmentweek.co.uk/search?query=ipo&per_page=24&sort=relevance1&date=this_year"
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
            page = requests.get(url, headers=headers)
            soup = BeautifulSoup(page.content, "html.parser")
            # soup  # Debugging - if soup is working correctly

            # Class names of the elements to be scraped
            div_class="card-body"# Class name of div containing the a tag
            #h1_class = "_1Y-96"
            #h1_div_class = "col-xs-12"
            title_h1_itemprop= "name"
            date_span_itemprop= ["datePublished"]
            para_div_class=["linear-gradient"]

            links = []

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
            # links # Debugging - if link array is generated

            collection = []
            err_logs = []
            scrapper_name = "investmentweek"

            for link in links:
                try:
                    l_page = requests.get(link, headers=headers)
                    l_soup = BeautifulSoup(l_page.content, 'html.parser')
                except:
                    err = scrapper_name + ": err: Failed to retrieve data from link: " + link + " and convert it to soup object"
                    err_logs.append(err)
                    continue

                data = []
                # Scraping the heading
                #h1_ele = l_soup.find("h1", {"class": h1_class})
                
                try:
                    title_ele = l_soup.find("h1", {"itemprop": title_h1_itemprop})
                    title_text = title_ele.text
                    title_text = title_text.strip("\n ")
                    data.append(title_text)
                except:
                    err = scrapper_name + ": err: Failed to find title in page. Link: " + link
                    err_logs.append(err)
                    continue  # drops the complete data if there is an error


                # Adding the link to data
                data.append(link)

                # Scraping the published date
                try:
                    date_ele = l_soup.find("span", {"itemprop": date_span_itemprop})
                    date_text = date_ele.text
                    date_text = date_text.strip("\n ")
                    date_text = " ".join(date_text.split()[:3])
                    #date_text = date_text.replace(" Updated: ", "")
                    data.append(date_text)  # The date_text could be further modified to represent a proper date format
                except:
                    err = scrapper_name + ": err: Failed to find date in page. Link: " + link
                    err_logs.append(err)
                    continue  # drops the complete data if there is an error
                
                # Adding the scraped date to data
                cur_date = str(datetime.today())
                data.append(cur_date)
                

                # Scraping the paragraph
                try:
                    para_ele = (l_soup.findAll("div", {"class": para_div_class}))[-1]
                    para_text = para_ele.text
                    para_text = para_text.strip("\n ")
                    data.append(para_text)  # Need to make this better
                except:
                    err = scrapper_name + ": err: Failed to find paragraph in page. Link: " + link
                    err_logs.append(err)
                    continue  # drops the complete data if there is an error
                # Adding data to a collection
                collection.append(data)

            df = pd.DataFrame(collection, columns =['title', 'link','publish_date','scraped_date','text'])
            if df.empty:
                err = scrapper_name + ": err: Empty dataframe"
                err_logs.append(err)
            # print(df) # For debugging. To check if df is created
            # print(err_logs) # For debugging - to check if any errors occoured
            df = FilterFunction(df)
            emptydataframe("investmentweek",df)
            return df
        except:
            print("investmentweek not working")
            not_working_functions.append("investmentweek")
    def sundayobserver():
        try:
            print("sundayobserver")
            url = "https://www.sundayobserver.lk/search/node/ipo"
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
            page = requests.get(url, headers=headers)
            soup = BeautifulSoup(page.content, "html.parser")
            # soup  # Debugging - if soup is working correctly

            # Class names of the elements to be scraped
            li_class="search-result"# Class name of div containing the a tag
            #h1_class = "_1Y-96"
            #h1_div_class = "col-xs-12"
            title_h1_class= "title"
            date_span_class= ["date-display-single"]
            para_div_class=["field-item even"]
            links = []

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
            # links # Debugging - if link array is generated

            collection = []
            err_logs = []
            scrapper_name = "sundayobserver"

            for link in links:
                try:
                    l_page = requests.get(link, headers=headers)
                    l_soup = BeautifulSoup(l_page.content, 'html.parser')
                except:
                    err = scrapper_name + ": err: Failed to retrieve data from link: " + link + " and convert it to soup object"
                    err_logs.append(err)
                    continue

                data = []
                # Scraping the heading
                #h1_ele = l_soup.find("h1", {"class": h1_class})
                
                try:
                    title_ele = l_soup.find("h1", {"class": title_h1_class})
                    title_text = title_ele.text
                    title_text = title_text.strip("\n ")
                    data.append(title_text)
                except:
                    err = scrapper_name + ": err: Failed to find title in page. Link: " + link
                    err_logs.append(err)
                    continue  # drops the complete data if there is an error


                # Adding the link to data
                data.append(link)

                # Scraping the published date
                try:
                    date_ele = l_soup.find("span", {"class": date_span_class})
                    date_text = date_ele.text
                    date_text = date_text.strip("\n ")
                    date_text = " ".join(date_text.split()[:3])
                    #date_text = date_text.replace(" Updated: ", "")
                    data.append(date_text)  # The date_text could be further modified to represent a proper date format
                except:
                    err = scrapper_name + ": err: Failed to find date in page. Link: " + link
                    err_logs.append(err)
                    continue  # drops the complete data if there is an error
                
                # Adding the scraped date to data
                cur_date = str(datetime.today())
                data.append(cur_date)
                

                # Scraping the paragraph
                try:
                    para_ele = (l_soup.findAll("div", {"class": para_div_class}))[-1]
                    para_text = para_ele.text
                    para_text = para_text.strip("\n ")
                    data.append(para_text)  # Need to make this better
                except:
                    err = scrapper_name + ": err: Failed to find paragraph in page. Link: " + link
                    err_logs.append(err)
                    continue  # drops the complete data if there is an error
                # Adding data to a collection
                collection.append(data)

            df = pd.DataFrame(collection, columns =['title', 'link','publish_date','scraped_date','text'])
            if df.empty:
                err = scrapper_name + ": err: Empty dataframe"
                err_logs.append(err)
            # print(df) # For debugging. To check if df is created
            # print(err_logs) # For debugging - to check if any errors occoured
            df = FilterFunction(df)
            emptydataframe("sundayobserver",df)
            return df
        except:
            print("sundayobserver not working")
            not_working_functions.append("sundayobserver")
    def mercomindia():
        try:
            print("mercomindia")
            url = "https://mercomindia.com/?s=ipo"
            domain_url = "https://mercomindia.com/"

            headers = {
                "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10.15; rv:78.0) Gecko/20100101 Firefox/78.0",
                "accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.9",
                'sec-fetch-site': 'none',
                'sec-fetch-mode': 'navigate',
                'sec-fetch-user': '?1',
                'sec-fetch-dest': 'document',
                'accept-language': 'en-GB,en-US;q=0.9,en;q=0.8',
            }
            page = requests.get(url, headers=headers)
            soup = BeautifulSoup(page.content, "html.parser")
            # soup  # Debugging - if soup is working correctly

            # Class names of the elements to be scraped
            div_class="pt-cv-ifield"# Class name of div containing the a tag
            #h1_class = "_1Y-96"
            #h1_div_class = "col-xs-12"
            title_div_class= "col-xs-12 col-sm-6 col-md-6 col-lg-6"
            #date_span_class= ["date-display-single"]
            para_div_class=["entry-content"]
            links = []

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
            # links # Debugging - if link array is generated

            collection = []
            err_logs = []
            scrapper_name = "mercomindia"

            for link in links:
                try:
                    l_page = requests.get(link, headers=headers)
                    l_soup = BeautifulSoup(l_page.content, 'html.parser')
                except:
                    err = scrapper_name + ": err: Failed to retrieve data from link: " + link + " and convert it to soup object"
                    err_logs.append(err)
                    continue

                data = []
                # Scraping the heading
                #h1_ele = l_soup.find("h1", {"class": h1_class})
                
                try:
                    title_ele = l_soup.find("div", {"class": title_div_class})
                    title_text = title_ele.text
                    title_text = title_text.strip("\n ")
                    data.append(title_text)
                except:
                    err = scrapper_name + ": err: Failed to find title in page. Link: " + link
                    err_logs.append(err)
                    continue  # drops the complete data if there is an error


                # Adding the link to data
                data.append(link)

                # Scraping the published date
                try:
                    date_ele = l_soup.find("time")
                    date_text = date_ele.text
                    date_text = date_text.strip("\n ")
                    date_text = " ".join(date_text.split()[:3])
                    #date_text = date_text.replace(" Updated: ", "")
                    data.append(date_text)  # The date_text could be further modified to represent a proper date format
                except:
                    err = scrapper_name + ": err: Failed to find date in page. Link: " + link
                    err_logs.append(err)
                    continue  # drops the complete data if there is an error
                
                # Adding the scraped date to data
                cur_date = str(datetime.today())
                data.append(cur_date)
                

                # Scraping the paragraph
                try:
                    para_ele = (l_soup.findAll("div", {"class": para_div_class}))[-1]
                    para_text = para_ele.text
                    para_text = para_text.strip("\n ")
                    data.append(para_text)  # Need to make this better
                except:
                    err = scrapper_name + ": err: Failed to find paragraph in page. Link: " + link
                    err_logs.append(err)
                    continue  # drops the complete data if there is an error
                # Adding data to a collection
                collection.append(data)

            df = pd.DataFrame(collection, columns =['title', 'link','publish_date','scraped_date','text'])
            if df.empty:
                err = scrapper_name + ": err: Empty dataframe"
                err_logs.append(err)
            # print(df) # For debugging. To check if df is created
            # print(err_logs) # For debugging - to check if any errors occoured
            df = FilterFunction(df)
            emptydataframe("mercomindia",df)
            return df
        except:
            print("mercomindia not working")
            not_working_functions.append("mercomindia")
    def koreanewsgazette():
        try:
            print("koreanewsgazette")
            url = "https://www.koreanewsgazette.com/?s=ipo"
            domain_url = "https://www.koreanewsgazette.com/"

            headers = {
                "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10.15; rv:78.0) Gecko/20100101 Firefox/78.0",
                "accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.9",
                'sec-fetch-site': 'none',
                'sec-fetch-mode': 'navigate',
                'sec-fetch-user': '?1',
                'sec-fetch-dest': 'document',
                'accept-language': 'en-GB,en-US;q=0.9,en;q=0.8',
            }
            page = requests.get(url, headers=headers)
            soup = BeautifulSoup(page.content, "html.parser")
            # soup  # Debugging - if soup is working correctly

            # Class names of the elements to be scraped
            div_class="read-more"# Class name of div containing the a tag
            #h1_class = "_1Y-96"
            #h1_div_class = "col-xs-12"
            title_h1_class= "entry-title"
            date_time_class= ["entry-date published updated"]
            para_div_class=["entry-content clearfix"]
            links = []

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
            # links # Debugging - if link array is generated

            collection = []
            err_logs = []
            scrapper_name = "koreanewsgazette"

            for link in links:
                try:
                    l_page = requests.get(link, headers=headers)
                    l_soup = BeautifulSoup(l_page.content, 'html.parser')
                except:
                    err = scrapper_name + ": err: Failed to retrieve data from link: " + link + " and convert it to soup object"
                    err_logs.append(err)
                    continue

                data = []
                # Scraping the heading
                #h1_ele = l_soup.find("h1", {"class": h1_class})
                
                try:
                    title_ele = l_soup.find("h1", {"class": title_h1_class})
                    title_text = title_ele.text
                    title_text = title_text.strip("\n ")
                    data.append(title_text)
                except:
                    err = scrapper_name + ": err: Failed to find title in page. Link: " + link
                    err_logs.append(err)
                    continue  # drops the complete data if there is an error


                # Adding the link to data
                data.append(link)

                # Scraping the published date
                try:
                    date_ele = l_soup.find("time", {"class": date_time_class})
                    date_text = date_ele.text
                    date_text = date_text.strip("\n ")
                    date_text = " ".join(date_text.split()[:3])
                    #date_text = date_text.replace(" Updated: ", "")
                    data.append(date_text)  # The date_text could be further modified to represent a proper date format
                except:
                    err = scrapper_name + ": err: Failed to find date in page. Link: " + link
                    err_logs.append(err)
                    continue  # drops the complete data if there is an error
                
                # Adding the scraped date to data
                cur_date = str(datetime.today())
                data.append(cur_date)
                

                # Scraping the paragraph
                try:
                    para_ele = (l_soup.findAll("div", {"class": para_div_class}))[-1]
                    para_text = para_ele.text
                    para_text = para_text.strip("\n ")
                    data.append(para_text)  # Need to make this better
                except:
                    err = scrapper_name + ": err: Failed to find paragraph in page. Link: " + link
                    err_logs.append(err)
                    continue  # drops the complete data if there is an error
                # Adding data to a collection
                collection.append(data)

            df = pd.DataFrame(collection, columns =['title', 'link','publish_date','scraped_date','text'])
            if df.empty:
                err = scrapper_name + ": err: Empty dataframe"
                err_logs.append(err)
            # print(df) # For debugging. To check if df is created
            # print(err_logs) # For debugging - to check if any errors occoured
            df = FilterFunction(df)
            emptydataframe("koreanewsgazette",df)
            return df
        except:
            print("koreanewsgazette not working")
            not_working_functions.append("koreanewsgazette")
            

    df1 = korea()
    df2 = proactive("ipo")
    df3 = Reuters("ipo")
    df4 = TradingChart()
    df5 = GoogleAlert()
    df6 = live("ipo")
    df7 = standartnews("ipo")
    df8 = kontan("ipo")
    df9 = AZ("ipo")
    df10 = xinhuanet()
    df11 = AFR()
    df12 = MoneyControl()
    df13 = Cnbc_Seeking()
    df14 = toi()
    df15 = German()
    # df16 = Italian()
    df17 = Japannews()
    df18 = Romania()
    df19 = Russian()
    df20 = Swedish()
    df21 = GoogleAlert1()
    df22 = GoogleAlert2()
    df23 = GoogleAlert3()
    df24 = GoogleAlert4()
    df25 = GoogleAlert5()
    df26 = IPOMonitor()
    df27 = globallegalchronicle()
    df28 = Seenews()
    df29 = Bisnis()
    df30 = RomaniaNew()
    #df31 = RomaniaInsider() not working 6th Sept 2022 
    df32 = SpaceMoney()
    # df33 = Carteira()
    df34 = Kontan1() ##
    # df35 = euronews()
    # df36 = franchdailynews()
    # df37 = norway()
    # df38 = localde()
    #df39 = chinatoday() # chinatoday not working - 6 Sept 2022
    #df40 = aljazeera() not working 6th Sept 2022
    df41 = Koreatimes()
    df42 = zdnet()
    df43 = arabNews()
    df44 = chosun()
    # df45 = Forbes()
    df46 = kngnet()
    df47 = kedg()
    df48 = wealthx()
    df49 = indonesia()
    df50 = asiainsurancereview()
    df51 = economic_times()
    df52 = prnewswire()
    df53 = arabfinance()
    df54 = interfax()
    df55 = vccircle()
    # df56 = allafrica()
    df57 = zawya()
    df58 = aljarida()
    df59 = dziennik()
    df60 = swissinfo()
    df61 = einnews()
    df62 = sabah()
    df63 = livemint()
    df64 = guardian()
    df65 = azernews()
    # df66 = chosenilboenglish()
    df67 = otempo()
    df68 = elicudadona()
    df69 = lastampa()
    df70 = liputan6()
    df71 = milenio()
    df72 = scoop()
    df73 = supchina()
    df74 = romania_insider()
    df75 = cnbc1()
    df76 = aif()
    df77 = monitor()
    df78 = thesun()
    #df79 = parool() not working 6th Sept 2022
    df80 = shabiba()
    df81 = koreannewsgazette()
    df82 = hungary()
    df83 = jauns()
    #df84 = pulse() not working 6th Sept 2022
    #df85 = vnexpress()  not working 6th Sept 2022
    df86 = jamaicaobserver()
    df87 = independent()
    df88 = albaniandailynews()
    df89 = ewn()
    df90 = bloombergquint()
    df91 = ecns()
    df92 = energy_voice()
    #df93 = euroNews()  not working 6th Sept 2022
    #df94 = theFreePressJournal() not working 6th Sept 2022
    # df95 = aylien()
    df96 = dw()
    df97 = star()
    df98 = Reuters("pre ipo")
    df99 = Reuters("Initial Public Offering")
    df100 = rss()
    df101 = thehindubusinessline()
    df102 = albawaba()
    df103 = fr()
    df104 = astanatimes()
    df105 = bankokpost()
    df106 = globalnewswire()
    df107 = headlinesoftoday()
    df108 = africabusinessinsider()
    df109 = africanmarkets()
    df110 = globalcapital()
    df111 = dominicantoday()
    df112 = businesstoday()
    df113 = investmentu()
    df114 = altassets()
    df115 = techtarget()
    df116 = stockhead()
    df117 = theindianwire()
    df118 = indianexpress()
    df119 = newindianexpress()
    df120 = hindustannewshub()
    df121 = businessinsider()
    df122 = ndtv()
    #df123 = koreatimesco()
    df124 = detroitnews()
    df125 = koreajoongangdailyjoins()
    df126 = upstreamonline()
    df127 = etfdailynews()
    df128 = splash247()
    df129 = theepochtimes()
    df130 = brisbanetimes()
    df131 = thenewsminute()
    df132 = koreatechdesk()
    df133 = globalonlinemony()


    # df134 = businessstandard()  #Selenium used
    # df135 = straitimes()  #selenium issue
    df136 = sumatrabinis()
    df137 = techstory()

 
    df139 = zdnet()
    df140 = manilatimes()
    df141 = alphastreet()
    df142 = defenseworld()
    df143 = investmentweek()
    df145 = sundayobserver()
    df146 = mercomindia()
    df147 = koreanewsgazette()	

    
    # df102 = kedgsel()
    # df67 = scmp()
    # df66 = phnompenhpost()
    #df_final_1 = [df137,df12,df121,df122]
    df_final_1 = [df147,df146,df145,df143,df142,df141,df140,df139,df137,df136,df133,df132,df131,df130,df129,df128,df127,df126,df125,df124,df122,df121,df120,df119,df118,df117,df116,df115,df114,df113,df112,df111,df110,df109,df108,df107,df106,df105,df104,df103,df102,df101,df100,df46,df19,df99,df98,df97,df96,df92,df91,df90,df89,df88,df87,df86,df83,df81,df80, df1,df2,df3,df4,df5,df6,df7,df8,df9,df10,df11, df12,df13,df14,df15, df17,df18,df21,df22 ,df23,df24,df25,df26, df27, df28, df29,df30,df32, df34, df41,df42,df43,df44,df47,df48,df49,df50,df52,df53,df54,df55,df57, df58, df59, df60,df61,  df62,df63,df64,df65,df67, df68, df69, df70, df71, df72,df73,  df74, df75, df76, df77,df78]
    #df_final_1 = [df124,df123,df122,df121,df120,df119,df118,df117,df116,df115,df114,df113,df112,df111,df110,df109,df108,df107,df106,df105,df104,df103,df102,df101,df100,df46,df19,df99,df98,df97,df96,df92,df91,df90,df89,df88,df87,df86,df83,df81,df80, df1,df2,df3,df4,df5,df6,df7,df8,df9,df10,df11, df12,df13,df14,df15, df17,df18,df21,df22 ,df23,df24,df25,df26, df27, df28, df29,df30,df32, df34, df41,df42,df43,df44,df47,df48,df49,df50,df52,df53,df54,df55,df57, df58, df59, df60,df61,  df62,df63,df64,df65,df67, df68, df69, df70, df71, df72,df73,  df74, df75, df76, df77,df78]

    # df_final_1 = [df85,df83,df80,df79,df7,df8,df18,df29,df32,df34,df58,df59,df62,df67, df68, df69, df70, df71,df76]
    # df_final_1 = [df102]
    df_final = pd.concat(df_final_1)
#     df_final = FilterFunction(df_fin)
    # TODO: commented out for testing as it takes too long.  uncomment later
    
    

    
    # df_final = remove_navigablestring(df_final)
    todays_report_filename = os.path.join(output_dir, 'todays_report.csv')
    todays_report_filename1 = os.path.join(output_dir, 'todays_report1.csv')
    df_final.to_csv(todays_report_filename1,index=False)
    final = correct_navigable_string(df_final)
    # final = FilterFunction(final)
    final.to_csv(todays_report_filename,index=False)
    logfile = ""
    if(get_time_valid() < 16):
        logfile = "logs.txt"
    else:
        logfile = "logs1.txt"
    textfile = open(logfile,"w")
    for i in not_working_functions:
        textfile.write(i+"\n")
    textfile.close()
    logging.info("writing output artifact " + todays_report_filename + " to " + output_dir)
    final.to_csv(todays_report_filename,index=False)
    logging.info("completed writing output artifact " + todays_report_filename + " to " + output_dir)

  # # final =final.loc[public_date == scrap_date]

# multilex_scraper("/home/prachi_multilex2", "/home/prachi_multilex2")       # uncomment this line to run this as a python script

# multilex_scraper( "", "")  
logging.info("last line of scraper")
