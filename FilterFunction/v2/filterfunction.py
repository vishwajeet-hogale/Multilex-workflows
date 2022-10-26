import re
from requests_html import HTMLSession
import pandas as pd
from bs4 import BeautifulSoup
import requests
from advertools import word_tokenize
from googletrans import Translator
from datetime import datetime,date 
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
            # df = FilterFunction(df)
            # emptydataframe("Oman",df)
            # log_errors(err_logs)
        #   df = translate_dataframe(df)
        #   df  = link_correction(df)
        
            return df
        except:
            print("Oman not working")
            # not_working_functions.append("Oman shabiba")
def FilterFunction(final):
    try:
        if(final.empty):
            return final
        key_1_gram = [ 'IPO','IPO','IPO ','SPACs','ipo','pre-IPO','pre-ipo','PRE-IPO','pre-IPO','going public','spac','shares','pre ipo']
        key_2_gram = ["listed on","go public","plan to","going public","offering shares","initial public","public offering","have listed","files for"]
        key_3_gram = ["offer its shares","to the public","going to list","files for ipo","filed for ipo"]
        title,link,published_date,scraped_date,text=[],[],[],[],[]
        for i,row in final.iterrows():
            cases = [0]*3
            article = str(str(row["title"]) + " " + str(row["text"])).lower()
            print(article + "\n\n\n\n")
            text_list = [article]
            key_1_gram = [str(i).lower() for i in key_1_gram]
            key_2_gram = [str(i).lower() for i in key_2_gram]
            key_3_gram = [i.lower() for i in key_3_gram]
            res_1_gram = set(word_tokenize(text_list,1)[0])
            res_2_gram = set(word_tokenize(text_list,2)[0])
            res_3_gram = set(word_tokenize(text_list,3)[0])
            if(len(res_1_gram.intersection(key_1_gram))>0):
                cases[0] = 1
            if(len(res_2_gram.intersection(key_2_gram))>0):
                cases[1] = 1
            if(len(res_3_gram.intersection(key_3_gram))):
                cases[2] = 1
            if(cases[0] or cases[1] or cases[2]):
                title.append(final['title'][i])
                link.append(final['link'][i])
                published_date.append(final['publish_date'][i])
                scraped_date.append(final['scraped_date'][i])
                text.append(final['text'][i])
            cases = [0]*3
        final = pd.DataFrame(list(zip(published_date,scraped_date,title,text,link)), 
                   columns =['title','link','publish_date','scraped_date','text'])
        final = final[~final['title'].isin(["private placement", "reverse merger", "blank check merger"])]
        final = final[~final['text'].isin(["private placement", "reverse merger", "blank check merger"])]
        final.to_csv("Newshab.csv")
        return final
    except:
        print("Issue in Filter Function")

def FilterFunction(final):
    try:
        if(final.empty):
            return final
        key_1_gram = [ 'IPO','IPO','IPO ','SPACs','ipo','pre-IPO','pre-ipo','PRE-IPO','pre-IPO','spac','shares','pre ipo']
        # key_2_gram = ["listed on","go public","plan to","going public","offering shares","initial public","public offering","have listed","files for"]
        # key_3_gram = ["offer its shares","to the public","going to list","files for ipo","filed for ipo"]
        title,link,published_date,scraped_date,text=[],[],[],[],[]
        for i,row in final.iterrows():
            cases = [0]*3
            article = str(str(row["title"]) + " " + str(row["text"])).lower()
            # print(article + "\n\n\n\n")
            text_list = [article]
            key_1_gram = [str(i).lower() for i in key_1_gram]
            # key_2_gram = [str(i).lower() for i in key_2_gram]
            # key_3_gram = [i.lower() for i in key_3_gram]
            res_1_gram = set(word_tokenize(text_list,1)[0])
            # res_2_gram = set(word_tokenize(text_list,2)[0])
            # res_3_gram = set(word_tokenize(text_list,3)[0])
            if(len(res_1_gram.intersection(key_1_gram))>0):
                cases[0] = 1
            # if(len(res_2_gram.intersection(key_2_gram))>0):
            #     cases[1] = 1
            # if(len(res_3_gram.intersection(key_3_gram))):
            #     cases[2] = 1
            if(cases[0] ):
                title.append(final['title'][i])
                link.append(final['link'][i])
                published_date.append(final['publish_date'][i])
                scraped_date.append(final['scraped_date'][i])
                text.append(final['text'][i])
            cases = [0]*3
        final = pd.DataFrame(list(zip(published_date,scraped_date,title,text,link)), 
                   columns =['title','link','publish_date','scraped_date','text'])
        final = final[~final['title'].isin(["private placement", "reverse merger", "blank check merger"])]
        final = final[~final['text'].isin(["private placement", "reverse merger", "blank check merger"])]
        final.to_csv("Newshab.csv")
        return final
    except:
        print("Issue in Filter Function")
def FilterFunction4(final):
            try:
                if(final.empty):
                    return final
                key_1_gram = [ 'IPO','IPO','IPO ','SPACs','ipo','pre-IPO','pre-ipo','PRE-IPO','pre-IPO','spac','shares','pre ipo']
                key_2_gram = ["listed on","go public","plan to","going public","offering shares","initial public","public offering","have listed","files for"]
                key_3_gram = ["offer its shares","to the public","going to list","files for ipo","filed for ipo"]
                title,link,published_date,scraped_date,text=[],[],[],[],[]
                for i,row in final.iterrows():
                    cases = [0]*3
                    article = str(str(row["title"]) + " " + str(row["text"])).lower()
                    # print(article + "\n\n\n\n")
                    text_list = [article]
                    key_1_gram = [str(i).lower() for i in key_1_gram]
                    key_2_gram = [str(i).lower() for i in key_2_gram]
                    key_3_gram = [i.lower() for i in key_3_gram]
                    res_1_gram = set(word_tokenize(text_list,1)[0])
                    res_2_gram = set(word_tokenize(text_list,2)[0])
                    res_3_gram = set(word_tokenize(text_list,3)[0])
                    if(len(res_1_gram.intersection(key_1_gram))>0):
                        cases[0] = 1
                        if(len(res_2_gram.intersection(key_2_gram))>0):
                            cases[1] = 1
                            if(len(res_3_gram.intersection(key_3_gram))):
                                cases[2] = 1
                                # if(cases[0] and ( cases[1] or cases[2])):
                                title.append(final['title'][i])
                                link.append(final['link'][i])
                                published_date.append(final['publish_date'][i])
                                scraped_date.append(final['scraped_date'][i])
                                text.append(final['text'][i])
                    cases = [0]*3
                final = pd.DataFrame(list(zip(title,link,published_date,scraped_date,text)), 
                        columns =['title','link','publish_date','scraped_date','text'])
                final = final[~final['title'].isin(["private placement", "reverse merger", "blank check merger"])]
                final = final[~final['text'].isin(["private placement", "reverse merger", "blank check merger"])]
                final.to_csv("Newshab.csv")
                return final
            except:
                print("Issue in Filter Function")
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
            # log_errors(err_logs)
            # df = FilterFunction(df)
            # emptydataframe("Star",df)
            return df
        except:
            print("Star is not working")
            # not_working_functions.append("Star")
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
            # df = FilterFunction(df)
            # emptydataframe("Vccircle",df)
            # df  = link_correction(df)
            return df
        except :
            print("Vccircle not working")
            # not_working_functions.append('Vccircle')
if __name__ == "__main__":


    # df = vccircle()
    # df.head(10))
    # df = pd.read_csv("PREIPO_Final_Report_2022-06-28.csv")
    # df.to_csv("new.csv")
    # df = FilterFunction(df)
    # df.to_csv("PREIPO_Final_Report.csv")
    df = pd.read_csv("todays_report.csv")
    df = FilterFunction4(df)
    df.to_csv("test1.csv")