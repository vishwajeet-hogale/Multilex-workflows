from selenium import webdriver
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.support.wait import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import time
 
# connect to google.com
driver = webdriver.Chrome(options=Options())
driver.get("https://opencorporates.com")
 
#time.sleep(5)
#driver.implicitly_wait(5.5)
element = WebDriverWait(driver, 10).until(EC.presence_of_element_located(('xpath', "//input[@name='q']")))
# find the search input field
search_field = driver.find_element('xpath',"//input[@name='q']")
 
# type the search string
search_field.send_keys("DESTREZA SALESFORCE CONSULTING LLC")

element1 = WebDriverWait(driver, 3).until(EC.presence_of_element_located((By.CLASS_NAME,"oc-home-search_button")))
 
# send enter key to get the search results!
button1= driver.find_element(By.CLASS_NAME,"oc-home-search_button")


time.sleep(3)
button1.click()

#time.sleep(3)


firstLinkXPath = "//div[@id='results']/ul/li[1]/a[2]"

element2 = WebDriverWait(driver, 3).until(EC.presence_of_element_located(('xpath',firstLinkXPath)))

alink=driver.find_element('xpath',firstLinkXPath);
#time.sleep(5)

alink.click()

#time.sleep(5)

dlXpath = "//div[@id='attributes']/dl"

element3 = WebDriverWait(driver, 3).until(EC.presence_of_element_located(('xpath',dlXpath)))
wedl=driver.find_element('xpath',dlXpath);

#create list objects to store the data 

wesdt=[]
wesdd=[]

wesdt=wedl.find_elements('xpath',"./dt");
wesdd=wedl.find_elements('xpath',"./dd")

print("The length of list is: ", len(wesdt))

dtCount = len(wesdt)

sample_dict = dict()


#put the data in a dictionary object 
for i in range(dtCount):
	wedt = wesdt[i]
	wedd = wesdd[i]
	header=wedt.text
	value=wedd.text
	sample_dict[header] = value

	print("header -> ", header , "value ->", value) 

time.sleep(2)

driver.quit()
