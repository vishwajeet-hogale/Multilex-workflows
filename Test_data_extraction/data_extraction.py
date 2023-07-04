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
from google.cloud import translate

path_to_csv = r"C:\Users\ujwal\Downloads\PREIPO_Final_Report_2023-07-01.csv"

def get_text(path_to_csv):
    df = pd.read_csv(path_to_csv)
    
    errors_404 = []

    options = webdriver.ChromeOptions() 
    options.headless = True
    options.add_argument('--no-sandbox')
    options.add_argument('--disable-dev-shm-usage')
    options.add_argument("--window-size=1920,1080")
    options.add_experimental_option('excludeSwitches', ['enable-logging']) 
    service = ChromeService(executable_path=ChromeDriverManager().install())
    
    text_extraction = {}
    
    
    for i, row in df.iterrows():
        text_extraction[row['link']]=[row['text'], 0]
    
    print(len(text_extraction))
        
    def translate_text(link, text):
        translate_client = translate.TranslationServiceClient()

        text = [text]
        target_language_code = "en"

        response = translate_client.translate_text(
            parent="projects/your-project-id/locations/global",
            contents=text,
            mime_type="text/plain",
            target_language_code=target_language_code,
        )
        translated = []
        for translation in response.translations:
            translated.append(translation.translated_text)
        translated = " ".join(translated)
        value = text_extraction[link][1]
        text_extraction[link] = [translated, value]
    
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
                    })
            text = g.extract(url=link).cleaned_text
            if text:
                text_extraction[link] = [text, 1]
        except:
            pass
    
    def get_from_newspaper(link):
        " Mediocre fast "
        try:
            article = Article(link)
            article.download()
            article.parse()
            text = article.text
            if text:
                text_extraction[link] = [text, 1]
        except:
            pass
    
    
        


    def ibm(link):
        try:
            driver = webdriver.Chrome(service=service, options=options)
            url = "https://www.ibm.com/demos/live/natural-language-understanding/self-service/home"
            driver.get(url)
            url_parts = driver.find_elements(By.CLASS_NAME, "story-button")
            for url in url_parts:
                if "URL" in str(url.text):
                    url.click()
                    break
            time.sleep(round(random.uniform(0.5, 1), 2))
            textarea = driver.find_element(By.ID, "nlu-analyze-textbox-1")
            textarea.clear()
            textarea.send_keys(link)
            time.sleep(round(random.uniform(1, 2), 2))
            button = driver.find_element(By.CLASS_NAME, "bx--btn--tertiary")
            button.click()
            text = WebDriverWait(driver, 30).until(EC.element_to_be_clickable((By.CLASS_NAME, 'results-text'))).text
            if text:
                text_extraction[link] = [text, 1]
            driver.quit()
        except:
            driver.quit()
    
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
    print(left)
    
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
    print(left)
    
    thread_list = []
    max_concurrent_threads = 10
    semaphore = threading.Semaphore(max_concurrent_threads)

    def execute_ibm(i):
        with semaphore:
            ibm(i)

    for i in text_extraction.keys():
        if text_extraction[i][1] == 0:
            thread = threading.Thread(target=execute_ibm, args=(i,))
            thread.start()
            thread_list.append(thread)

    for thread in thread_list:
        thread.join()
    
    left = 0
    for i in text_extraction.keys():
        if text_extraction[i][1]==0:
            left+=1
    print(left)
    
    time.sleep(1000)
    
    def get_text_via_logic(link):
        """
        response = rs.get(link)
        data = bs(response.content, "html.parser")
        thread_list = []
        text = data.get_text().split('\n')
        new_text=[]
        length=len(text)
        def translatedeep(text):
            translation = GoogleTranslator(source='auto', target='en').translate(text)
            new_text.append(translation)
        for i in range(length):
            thread_list.append(threading.Thread(target=translatedeep, args=(text[i], )))
        

        for thread in thread_list:
            thread.start()
            
        for thread in thread_list:
            thread.join()
        
        text = new_text
        texts =[i.strip() for i in text if len(i)>400]
        final_text = []
        for text in texts:
            val=text.split("  ")
            final_text.append(sorted(val, key= lambda x: len(x))[-1])
        final_text = " ".join(final_text)
        print(final_text)
        """


    df.to_csv(path_to_csv)

if __name__ == "__main__":
    get_text(path_to_csv)