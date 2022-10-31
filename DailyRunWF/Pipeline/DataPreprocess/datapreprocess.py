"""
Functionality : Cleans the code after scraping and prediction of companies and makes it ready
to be sent as a file for eyeballing
"""
import logging
import os
import re
from datetime import datetime, date
import pytz
import pandas as pd


def get_time_valid():
    """Returns the hour from the time"""
    ist = pytz.timezone('Asia/Kolkata')
    time = datetime.now(ist)
    time = time.time()
    return time.hour
def cleaningData(data):
    """Cleans a list passed to it and returns a list"""
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

def cleanedReport(file_name, input_dir, output_dir):
    """Cleans the report"""
    cur_date = str(date.today())
    input_file_fullpath=os.path.join(input_dir,file_name)
    logging.info("reading input artifact " + input_file_fullpath)
    data = pd.read_csv(input_file_fullpath)
    logging.info("completed reading input artifact " + input_file_fullpath)
    data['text'] = cleaningData(data['text'].tolist())
    data['title'] = cleaningData(data['title'].tolist())
    data['Companies'] = cleaningData(data['Companies'].tolist())
    data["Country"] = " "
    data["Comments"] = " "
    data["update"] = " "
    data =data[['publish_date','scraped_date','title','text','Companies',
    'Country','link','Comments','update']]
    final_report_fullpath = os.path.join( output_dir, 'FinalReport_{}.csv').format(cur_date)
    final_report_fullpath1 = os.path.join( output_dir, 'FinalReport_{}_1.csv').format(cur_date)
    logging.info("writing output artifact " + final_report_fullpath + " to " + output_dir)
    data = data.drop_duplicates(subset=["text","link","title"])
    if int(get_time_valid()) >= 16:
        data.to_csv(final_report_fullpath1,index=False)
    else:
        data.to_csv(final_report_fullpath,index=False)
    logging.info("completed writing output artifact " + final_report_fullpath + " to " + output_dir)
    return 'Report is Successfully Generated !!!!'

if __name__ == "__main__":
    cleanedReport("EDI_PREIPO_report.csv","", "")
