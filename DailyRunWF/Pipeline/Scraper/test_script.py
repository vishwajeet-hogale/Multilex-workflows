

 #Import required Libraries

'''import requests
from bs4 import BeautifulSoup
import pandas as pd
import re
from datetime import datetime,date
import threading
from advertools import word_tokenize
import time

not_working_functions = []
Errors = {}

def err_dict(link="", published_date="", title="", text=""):
        return {
            "link": link,
            "published_date": published_date,
            "title": title,
            "text": text
        }
def emptydataframe(name, df):
        if df.empty:
            not_working_functions.append(name+" : err : Empty datframe")

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

def koreatimes(keyword):
        try:
            scrapper_name = 'koreatimes'
            print(scrapper_name)
            Errors[scrapper_name]=[]
            
            url = f'https://www.koreatimes.co.kr/www2/common/search.asp?kwd={keyword}'
            domain_url = 'https://www.koreatimes.co.kr/'
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
                print(scrapper_name," not working")
                not_working_functions.append(scrapper_name)
                err = "Main link did not load: " + url
                Errors[scrapper_name].append(err)          
                return
            # Debugging - if soup is working correctly
        
        
            links = []
            try:
                for divtag in soup.find_all("div", {"class": 'list_article_headline LoraMedium'}):
                    link = divtag.find("a")['href']   # Gets the link
                    # Checking the link if it is a relative link
                    if link[0] == '/':
                        link = domain_url + link[1:]
                    # Filtering advertaisment links
                    link_start = domain_url
                    if link.startswith(link_start):
                        links.append(link)
            except:
                if len(links)==0:
                    print(scrapper_name," not working")
                    not_working_functions.append(scrapper_name)
                    Errors[scrapper_name].append("Extraction of link not working.")
                    return
            
            # Remove duplicates
            links = list(set(links))
        
            collection = []
        
            def getarticle(link):
                flag=0
                err=err_dict()
                try:
                    l_page = requests.get(link, headers=headers)
                    l_soup = BeautifulSoup(l_page.content, 'html.parser')
                except:
                    err["link"]="Link not working: "+link
                    Errors[scrapper_name].append(err)
                    return
                
                data = []
            
                # Scraping the heading
                        
                try:
                    title_ele = l_soup.find('div' , {'class': 'view_headline LoraMedium'})
                    data.append(title_ele.text)
                except:
                    err["link"]=link
                    err['title']="Error"
                    data.append("-")
                    flag=1
            
                # Adding the link to data
                data.append(link)
            
                # Scraping the published date
                try:
                    date_ele = l_soup.find("div", {"class":'view_date'})
                    date_text = date_ele.text.split('Posted : ')[1]
                    data.append(date_text)
                except:
                    err["link"]=link
                    err['published_date']="Error"
                    data.append("-")
                    flag=1
            
                # Adding the scraped date to data
                cur_date = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
                data.append(cur_date)
            
                # Scraping the paragraph
                try:
                    para_ele = l_soup.find('div' , {'id': 'startts'})
                    para_text = para_ele.text.strip("\n ")
                    data.append(para_text)  
                except:
                    err["link"]=link
                    err['text']="Error"
                    data.append("-")
                    flag=1
                # drops the complete data if there is an error
                # Adding data to a collection
                
                if flag==1:
                    Errors[scrapper_name].append(err)              
            
                collection.append(data)
         
        
            thread_list=[]
            length=len(links)
            for i in range(length):
                thread_list.append(threading.Thread(target=getarticle, args=(links[i], )))
        
    
            for thread in thread_list:
                thread.start()
            
            for thread in thread_list:
                thread.join()
            
            df = pd.DataFrame(collection, columns=[
                              'title', 'link', 'publish_date', 'scraped_date', 'text'])
            df = FilterFunction(df)
            emptydataframe(scrapper_name, df)
            return df
        
        except:
            not_working_functions.append(scrapper_name)
            print(scrapper_name," not working")
'''

import time
import scraper_asynch

print(scraper_asynch.koreatimes('ipo'))
if __name__ == "__main__":
    x=time.time()
    print(scraper_asynch.koreatimes('ipo'))
    y=time.time()
    print()
    print()
    print("time taken by scraper.py: ", y-x)
    print()
    print()