import pandas as pd
from datetime import datetime,date,timedelta
from googletrans import Translator
import pytz
import re
from bs4 import BeautifulSoup
from advertools import word_tokenize
months = ["Jan" , "Feb" , "Mar" , "Apr" , "May" , "Jun" , "Jul" , "Aug" , "Sep" , "Oct" , "Nov" , "Dec","January","February","March","April","May","June","July","August","September","October","November","December"]
    
df = pd.read_csv("todays_report1.csv")
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

def link_correction(data):
    link = data["link"].to_list()
    new = []
    for i in link :
        try :
            if(i.find("&ct")!= -1):
                new.append(i.split("&ct")[0])
            else:
                new.append(i)
        except :
            print("Link is messed up ")

    new_links = pd.DataFrame(new)
    data["link"] = new_links
    return data

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
        df2 = pd.DataFrame(columns=["title","link","publish_date","scraped_date","text"])
        if "Date" in df_final["publish_date"].tolist():
            df2 = df_final[df_final["publish_date"] == "Date"]
        # df_final = df_final[df_final["publish_date"] != "Date"]
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
                if(cases[0] or cases[1] or cases[2]):
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
df1 = correct_navigable_string(df)
df1 = FilterFunction(df1)
df1.to_csv("Test1.csv")