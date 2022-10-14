import pandas as pd
import re
from datetime import datetime , date
cur_date = str(date.today())
import requests
import numpy as np
import logging
import pandas as pd
import matplotlib.pyplot as plt
from bs4 import BeautifulSoup
import pytz
import os
import pandas as pd 
import html
from datetime import datetime
def get_time_valid(): #Returns the hour from the time 
        IST = pytz.timezone('Asia/Kolkata')
        time = datetime.now(IST)
        time = time.time()
        return time.hour
def CleaningData(data):
    cleaned_text =[]
    for text in data:
        text =str(text) 
        text= text.lower().replace("don't","do not")
        text = text.replace('â€¦', '').replace('<span class="match">', '').replace('</span>','').replace('\n','').replace('     ','')
        text = text.replace(",,",",")
        if text != 'nan':
            new_text = re.sub('[^A-Za-z0-9%,]+', ' ', text)
            cleaned_text.append(new_text.title())
        else:
            cleaned_text.append('nan')
    return cleaned_text

def CleanedReport(file_name, input_dir, output_dir):

    input_file_fullpath=os.path.join(input_dir,file_name)

    logging.info("reading input artifact " + input_file_fullpath)
    data = pd.read_csv(input_file_fullpath)
    logging.info("completed reading input artifact " + input_file_fullpath)

    data['text'] = CleaningData(data['text'].tolist())
    data['title'] = CleaningData(data['title'].tolist())
    data['Companies'] = CleaningData(data['Companies'].tolist())
    data["Country"] = " "
    data["Comments"] = " "
    data["update"] = " "
    
    data =data[['publish_date','scraped_date','title','text','Companies','Country','link','Comments','update']]

    
    final_report_fullpath = os.path.join( output_dir, 'FinalReport_{}.csv').format(cur_date)
    final_report_fullpath1 = os.path.join( output_dir, 'FinalReport_{}_1.csv').format(cur_date)
    logging.info("writing output artifact " + final_report_fullpath + " to " + output_dir)
    data = data.drop_duplicates(subset=["text","link","title"])
    if(int(get_time_valid()) >= 16):
         data.to_csv(final_report_fullpath1,index=False)
    else:
         data.to_csv(final_report_fullpath,index=False)
    
    logging.info("completed writing output artifact " + final_report_fullpath + " to " + output_dir)

    return 'Report is Successfully Generated !!!!'
# CleanedReport("EDI_PREIPO_report.csv","/home/prachi_multilex2", "/home/prachi_multilex2")