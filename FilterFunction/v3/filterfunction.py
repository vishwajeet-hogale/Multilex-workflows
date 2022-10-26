import re
from requests_html import HTMLSession
import pandas as pd
from bs4 import BeautifulSoup
import requests
from advertools import word_tokenize
from googletrans import Translator
from datetime import datetime,date 

def FilterFunction2(final):
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
            if(cases[0] and (cases[1] or cases[2])):
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