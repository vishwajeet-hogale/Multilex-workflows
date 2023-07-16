from goose3 import Goose
import pandas as pd
import time
from newspaper import Article
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.service import Service as ChromeService
from webdriver_manager.chrome import ChromeDriverManager
import random
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import requests as rs
from bs4 import BeautifulSoup as bs
import threading
import googletrans



"""
This script is used to extract text from the links provided in the csv file.
"""



def get_text(path_to_csv):
    df = pd.read_excel(path_to_csv) #Converting given csv file to pands 
    
    """
    Initialising Selenium Webdriver
    """
    
    options = webdriver.ChromeOptions() 
    options.headless = True  #The headless property is set to True, which enables the browser to run in headless mode (without a graphical interface).
    
    """
    Several additional arguments are added to the options:
    '--no-sandbox': Disables the sandbox for the Chrome browser, which may be necessary in certain environments.
    '--disable-dev-shm-usage': Disables the usage of /dev/shm (shared memory) for the Chrome browser, which can help reduce memory usage.
    "--window-size=1920,1080": Sets the window size of the browser to 1920x1080 pixels.
    """
    
    options.add_argument('--no-sandbox') 
    options.add_argument('--disable-dev-shm-usage')
    options.add_argument("--window-size=1920,1080")
    
    """
    The add_experimental_option() method is used to exclude the 'enable-logging' switch. This switch disables logging, which can help reduce the output verbosity during execution.
    The ChromeService class from selenium.webdriver.chrome.service is instantiated, providing the path to the ChromeDriver executable obtained using ChromeDriverManager().install(). 
    This ensures the correct version of the ChromeDriver is downloaded and used for compatibility with the installed Chrome browser.

    """ 
    options.add_experimental_option('excludeSwitches', ['enable-logging']) 
    service = ChromeService(executable_path=ChromeDriverManager().install())
    
    text_extraction = {}
    
    
    for i, row in df.iterrows():
        text_extraction[row['link']]=[row['text'], 0]
    
    print(f"\n\n Number of links that are gonna be passed through Goose are: {len(text_extraction)} \n\n")
    
    def translate_text(text, target_language):
        
        """Translates the given text from the source language to the target language.

        Args:
            text (str): The text to translate.
            source_language (str): The source language of the text.
            target_language (str): The target language of the text.

        Returns:
            str: The translated text.
        """

        translator = googletrans.Translator()
        translated_text = translator.translate(text[0], dest=target_language)

        return [translated_text.text, text[1]]
    
    def translate_text_dict(link):
        
        """Translates the given text from the source language to the target language.

        Args:
            text (str): The text to translate.
            source_language (str): The source language of the text.
            target_language (str): The target language of the text.

        Returns:
            str: The translated text.
        """

        translator = googletrans.Translator()
        translated_text = translator.translate(text_extraction[link][0], dest='en')

        text_extraction[link] = [translated_text.text, 1]

    
    
    def get_from_goose(link):
        """ Fastest way to extract article """
        try:
            g = Goose({
                        "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10.15; rv:78.0) Gecko/20100101 Firefox/78.0",
                        "accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.9",
                        'sec-fetch-site': 'none',
                        'sec-fetch-mode': 'navigate',
                        'sec-fetch-user': '?1',
                        'sec-fetch-dest': 'document',
                        'accept-language': 'en-GB,en-US;q=0.9,en;q=0.8',
                    }) #Initialising Goose module
            
            text = g.extract(url=link).cleaned_text #Extracting Article body by passing link
            
            if text:
                text_extraction[link] = [text, 1] #Append extraction link if and only if text is extracted
        except:
            pass
    
    def get_from_newspaper(link):
        """ Mediocre fast """
        
        """
        Uses newspaper3k module to get the article text.
        """
        try:
            article = Article(link)
            article.download()
            article.parse()
            text = article.text
            if text:
                text_extraction[link] = [text, 1]
        except:
            pass
    
    
        


    def ibm(links):
        try:
            driver = webdriver.Chrome(service=service, options=options)
            url = "https://www.ibm.com/demos/live/natural-language-understanding/self-service/home"
            driver.get(url)
            url_parts = driver.find_elements(By.CLASS_NAME, "story-button")
            for url in url_parts:
                if "URL" in str(url.text):
                    url.click()
                    break
            time.sleep(round(random.uniform(0.5, 2), 2))
            for link in links:
                try:
                    textarea = driver.find_element(By.ID, "nlu-analyze-textbox-1")
                    textarea.clear()
                    textarea.send_keys(link)
                    time.sleep(round(random.uniform(1, 2), 2))
                    button = driver.find_element(By.CLASS_NAME, "bx--btn--tertiary")
                    button.click()
                    text = WebDriverWait(driver, 30).until(EC.element_to_be_clickable((By.CLASS_NAME, 'results-text'))).text
                    if text:
                        text_extraction[link] = [text, 1]
                    time.sleep(round(random.uniform(1, 2), 2))
                    button = driver.find_element(By.CLASS_NAME, "bx--btn--tertiary")
                    button.click()
                    time.sleep(round(random.uniform(0.5, 2), 2))
                except:
                    driver.quit()
                    driver = webdriver.Chrome(service=service, options=options)
                    url = "https://www.ibm.com/demos/live/natural-language-understanding/self-service/home"
                    driver.get(url)
                    url_parts = driver.find_elements(By.CLASS_NAME, "story-button")
                    for url in url_parts:
                        if "URL" in str(url.text):
                            url.click()
                            break
                    time.sleep(round(random.uniform(0.5, 2), 2))    
            
            driver.quit()
        except:
            driver.quit()
    
    article_html = {} 
            
    def get_text_via_logic(link):
        try:
            headers = {
                    "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10.15; rv:78.0) Gecko/20100101 Firefox/78.0",
                    "accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,/;q=0.8,application/signed-exchange;v=b3;q=0.9",
                    'sec-fetch-site': 'none',
                    'sec-fetch-mode': 'navigate',
                    'sec-fetch-user': '?1',
                    'sec-fetch-dest': 'document',
                    'accept-language': 'en-GB,en-US;q=0.9,en;q=0.8',
                }
            response = rs.get(link, headers=headers)
            data = bs(response.content, "html.parser")
            article_html[link] = data
        except:
            pass
        
    def parsing_with_pattern_matching(link):
        try:
            data = article_html[link]
            thread_list = []
            text = data.get_text().split('\n')
            new_text=[]
            length=len(text)
            def translatedeep(text):
                translation = translate_text(text, 'en')
                new_text.append(translation)
            for i in range(length):
                thread_list.append(threading.Thread(target=translatedeep, args=([text[i], i], )))
            

            for thread in thread_list:
                thread.start()
                
            for thread in thread_list:
                thread.join()
            
            data = ""
            new_text = sorted(new_text, key=lambda x: x[1])
            text = []
            for i in new_text:
                if i[0]=="":
                    if data:
                        text.append(" " + data)
                    data = ""
                else:
                    data += i[0]
            if data:
                text.append(" " + data)
                
            final_text = ""
                        
            for i in text:
                if i:
                    if len(i)>280:
                        final_text+=i         
            if len(final_text)>1.5*len(text_extraction[link][0]):
                text_extraction[link] = [final_text, 1]
        except:
            pass
    
    
    
    
    thread_list=[]
    for i in text_extraction.keys():
        thread_list.append(threading.Thread(target=get_from_goose, args=(i, )))
    

    for thread in thread_list:
        thread.start()
        
    for thread in thread_list:
        thread.join()
    
    left = 0
    for i in text_extraction.keys():
        if text_extraction[i][1]==0:
            left+=1
    print(f"\n\n Links that are gonna be passed through newspaper3k:{left} \n\n")
    
    thread_list=[]
    for i in text_extraction.keys():
        if text_extraction[i][1]==0:
            thread_list.append(threading.Thread(target=get_from_newspaper, args=(i, )))
    

    for thread in thread_list:
        thread.start()
        
    for thread in thread_list:
        thread.join()
    
    left = 0
    for i in text_extraction.keys():
        if text_extraction[i][1]==0:
            left+=1
    print(f"\n\n Links that are gonna be passed through ibm nlp page:{left} \n\n")
    
    thread_list = []
    max_concurrent_threads = 10
    semaphore = threading.Semaphore(max_concurrent_threads)

    def execute_ibm(i):
        with semaphore:
            ibm(i)
    
    value = left//10
    start = 0
    
    data = []

    for i in text_extraction.keys():
        if text_extraction[i][1] == 0:
            if start%value==0:
                data.append([i])
            else:
                data[-1].append(i)
            start+=1
        
    for i in data:
        thread = threading.Thread(target=execute_ibm, args=(i,))
        thread.start()
        thread_list.append(thread)

    for thread in thread_list:
        thread.join()
    
    left = 0
    for i in text_extraction.keys():
        if text_extraction[i][1]==0:
            left+=1
    print(f"\n\n Links that are gonna be passed through pattern matching:{left} \n\n")
    
    
    thread_list=[]
    for i in text_extraction.keys():
        if text_extraction[i][1]==0:
            thread_list.append(threading.Thread(target=get_text_via_logic, args=(i, )))
    

    for thread in thread_list:
        thread.start()
        
    for thread in thread_list:
        thread.join()
        
    thread_list=[]
    for i in text_extraction.keys():
        if text_extraction[i][1]==0:
            thread_list.append(threading.Thread(target=translate_text_dict, args=(i, )))
    

    for thread in thread_list:
        thread.start()
        
    for thread in thread_list:
        thread.join()
        
    for i in article_html.keys():
        parsing_with_pattern_matching(i)
    
        
    for i, row in df.iterrows():
        if text_extraction[row['link']][0] != df.loc[i, 'text']:
            df.loc[i, 'text'] = text_extraction[row['link']][0]
    

    
    
    
    

    path_to_csv=path_to_csv.replace(".csv", ".xlsx")
    df.to_excel(path_to_csv)

if __name__ == "__main__":
    path_to_csv = r"C:\Users\ujwal\Downloads\PREIPO_Final_Report_2023-07-12 (1).xlsx"
    get_text(path_to_csv)