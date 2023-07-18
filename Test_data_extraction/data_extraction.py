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
from deep_translator import GoogleTranslator
from googletrans import Translator

path_to_csv = r"C:\Users\ujwal\Downloads\PREIPO_Final_Report_2023-07-01.csv"

def get_text(path_to_csv):
    
    def translatedeep(text):
        translation = GoogleTranslator(source='auto', target='en').translate(text)
        return translation
    
    def translate(text):
        translator = Translator()
        translation = translator.translate(text, dest='en')
        return translation.text
    
    df = pd.read_csv(path_to_csv)
    g = Goose({
                    "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10.15; rv:78.0) Gecko/20100101 Firefox/78.0",
                    "accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.9",
                    'sec-fetch-site': 'none',
                    'sec-fetch-mode': 'navigate',
                    'sec-fetch-user': '?1',
                    'sec-fetch-dest': 'document',
                    'accept-language': 'en-GB,en-US;q=0.9,en;q=0.8',
                })
    errors_404 = []

    options = webdriver.ChromeOptions() 
    options.headless = True
    options.add_argument('--no-sandbox')
    options.add_argument('--disable-dev-shm-usage')
    options.add_argument("--window-size=1920,1080")
    options.add_experimental_option('excludeSwitches', ['enable-logging']) 
    service = ChromeService(executable_path=ChromeDriverManager().install())
    driver = webdriver.Chrome(service=service, options=options)


    def reset_driver():
        url = "https://www.ibm.com/demos/live/natural-language-understanding/self-service/home"
        driver.get(url)
        url_parts = driver.find_elements(By.CLASS_NAME, "story-button")
        for url in url_parts:
            if "URL" in str(url.text):
                url.click()
                break
        time.sleep(round(random.uniform(0.5, 1), 2))

    reset_driver()

    def get_from_goose(link):
        """ Fastest way to extract article """
        return g.extract(url=link).cleaned_text

    def get_from_newspaper(link):
        " Mediocre fast "
        article = Article(link)
        article.download()
        article.parse()
        return article.text

    def get_from_ibm(link):
        """ Very Slow """
        try:
            textarea = driver.find_element(By.ID, "nlu-analyze-textbox-1")
            textarea.clear()
            textarea.send_keys(link)
            time.sleep(round(random.uniform(1, 2), 2))
            button = driver.find_element(By.CLASS_NAME, "bx--btn--tertiary")
            button.click()
            text = WebDriverWait(driver, 30).until(EC.element_to_be_clickable((By.CLASS_NAME, 'results-text'))).text
            if not text:
                print(f"\n Error: {link} \n")
            time.sleep(round(random.uniform(1, 2), 2))
            button = driver.find_element(By.CLASS_NAME, "bx--btn--tertiary")
            button.click()
            time.sleep(round(random.uniform(0.6, 1), 2))
            return text
        except Exception as e:
            print(f"\n Exception: {e} \n Error: {link} \n")
            reset_driver()
            return None

    length = len(df)

    for i, row in df.iterrows():
        text=""
        flag=0
        link = row["link"]
        try:
            text = get_from_goose(link)
            if text:
                df.at[i, "text"] = text
            else:
                text = get_from_newspaper(link)
                if text:
                    df.at[i, "text"] = text
                else:
                    flag = 1
                    text = get_from_ibm(link)
                    if text:
                        df.at[i, "text"] = text
        except Exception as error:
            if "404" or "500" in str(error):
                length-=1
                print(length)
                errors_404.append(link)
                continue
            if flag==0:
                try:
                    text = get_from_newspaper(link)
                    if text:
                        df.at[i, "text"] = text
                    else:
                        text = get_from_ibm(link)
                        if text:
                            df.at[i, "text"] = text
                except:
                    text = get_from_ibm(link)
                    if text:
                        df.at[i, "text"] = text
            else:
                text = get_from_ibm(link)
                if text:
                    df.at[i, "text"] = text
            
        length-=1
        print(length)
        
    driver.quit()


    df.to_csv(path_to_csv)

if __name__ == "__main__":
    get_text(path_to_csv)
    