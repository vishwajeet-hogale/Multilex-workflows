from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.service import Service as ChromeService
from webdriver_manager.chrome import ChromeDriverManager
from selenium import webdriver
from bs4 import BeautifulSoup as bs

options = webdriver.ChromeOptions() 
options.headless = True
options.add_argument('--no-sandbox')
options.add_argument('--disable-dev-shm-usage')
options.add_argument("--window-size=1920,1080")
options.add_experimental_option('excludeSwitches', ['enable-logging']) 
service = ChromeService(executable_path=ChromeDriverManager().install())

driver = webdriver.Chrome(service=service, options=options)

driver.get("https://www.amazon.com/s?k=Kitchen&i=kitchen-intl-ship")

soup = bs(driver.page_source, "html.parser")

print(soup.prettify())

driver.quit()