

import requests
import json
import pandas as pd
from bs4 import BeautifulSoup
import requests
from pygleif import PyGleif
from selenium import webdriver
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.support.wait import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import time
from webdriver_manager.chrome import ChromeDriverManager

filename ="FinalFile.xlsx"
 
def opencorporates(company,driver,country):
    link_main ="https://opencorporates.com"
    driver.get("https://opencorporates.com")
    time.sleep(3)
	# find the search input field
    element = WebDriverWait(driver, 10).until(EC.presence_of_element_located(('xpath', "//input[@name='q']")))
    search_field = driver.find_element('xpath',"//input[@name='q']")
    
	# type the search string
    search_field.send_keys(company)
    element1 = WebDriverWait(driver, 10).until(EC.presence_of_element_located((By.CLASS_NAME,"oc-home-search_button")))
	
	# send enter key to get the search results!
    button1= driver.find_element(By.CLASS_NAME,"oc-home-search_button")
    time.sleep(3)
    button1.click()
    time.sleep(10)
    
    #firstLinkXPath = "//div[@id='results']/ul/li[1]/a[2]"
    resultSet1 = driver.find_elements('xpath',"//div[@id='results']/ul")
    if(len(resultSet1)==0):
        return None
   
    resultSet=resultSet1[0]
    options = resultSet.find_elements('xpath', "./li")
    
    a_jur_filter = "a[contains(@class, 'jurisdiction_filter')]"
    print("options count ................", len(options))
    sample_dict = None
    for option in options:
        
        time.sleep(3)
        element2 = None
        link1 = None
        print("inside loop ............\n ")
        try:
            link1 = option.find_element('xpath', "./" + a_jur_filter)
            str_jur = link1.get_attribute('class')
            print("jur .....", str_jur)
            print("xls country .....", country)

            last = str_jur.rsplit(" ",1)[-1]
            country2 = last.strip()
            country1 =country2.upper()
            print("opencorporate country .....", country1)

            
            if(country1 ==country):
                print("country matched")
                #click on the link and get details a[2]"
                link2=option.find_element('xpath', "./a[2]")
                link2.click()
                #link2_href = link2.get_attribute("href")
                #link_full =link_main + link2_href
                #print("full link to click " + link2_href)
                #link2_href1 = link.find_element(By.LINK_TEXT,link2_href )
                #link2_href.click()
                print("after click")
                time.sleep(10)
                print("after  sleep")

                dlXpath = "//div[@id='attributes']/dl"
                print("before  find element")

                #element3 = WebDriverWait(driver, 10).until(EC.presence_of_element_located(('xpath',dlXpath)))
                wedl=driver.find_element('xpath',dlXpath)
                print("after  find element")
                #create list objects to store the data 
                #wesdt=[]
                #wesdd=[]
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
                            
                return sample_dict
        except:
            return None
    
       
    
    
    return sample_dict



def company_info1(companyname,iso):
        api_url="https://api.gleif.org/api/v1/fuzzycompletions?field=entity.legalName&q="+str(companyname)
        response = requests.get(api_url)
        json_format = json.loads(response.text)
        res_obj = {"company_name":None,"legalAddress":None,"officeAddress":None,"country":None,"LEI":None}
        objects = []
        try:
                for i in json_format['data']:

                        key='relationships'
                        x = list(i.keys())
                        if(x.count(key) == 1):
                                api_url1=i['relationships']['lei-records']['links']['related']
                                response1=requests.get(api_url1)
                                json_format1 = json.loads(response1.text)
                                res_obj["company_name"] = json_format1['data']['attributes']['entity']['legalName']['name']
                                legalAddress_details=""
                                for j in json_format1['data']['attributes']['entity']['legalAddress']['addressLines']:
                                        legalAddress_details=str(legalAddress_details) + str(j)
                                legalAddress=str(legalAddress_details)+" "+str(json_format1['data']['attributes']['entity']['legalAddress']['city'])+ " "+str(json_format1['data']['attributes']['entity']['legalAddress']['region'])+ " "+str(json_format1['data']['attributes']['entity']['legalAddress']['country'])
                                res_obj["legalAddress"] = legalAddress
                                res_obj["country"] = json_format1['data']['attributes']['entity']['legalAddress']['country']
                                HQAddress_details = ""
                                for j in json_format1['data']['attributes']['entity']['headquartersAddress']['addressLines']:
                                        HQAddress_details=str(HQAddress_details) + str(j)
                                
                                headquarterAddress = str(HQAddress_details) + " " + str(json_format1['data']['attributes']['entity']['headquartersAddress']['city']) + " "+ str(json_format1['data']['attributes']['entity']['headquartersAddress']['region'])+ " "+str(json_format1['data']['attributes']['entity']['headquartersAddress']['country'])
                                res_obj["officeAddress"] = headquarterAddress
                                res_obj["LEI"] = json_format['data'][0]["relationships"]["lei-records"]["data"]["id"]
                                if iso in headquarterAddress.strip().split():
                                        print("country matched in gleif record")
                                        objects.append(res_obj)
        except:
                return {"company_name":None,"legalAddress":None,"officeAddress":None,"country":None,"LEI":None}
        if len(objects) == 0:
                return {"company_name":None,"legalAddress":None,"officeAddress":None,"country":None,"LEI":None}
        return objects[0] 
    
def get_jurisdiction_info(lei):
        try:
                gleif = PyGleif(lei)
                return gleif.response.data.attributes.entity.jurisdiction
        except:
                return ""
            
def extract_gleif_data(df,company,country ,la,oa,lei):
    
                #from gleif APi 
                data = company_info1(company,country)
                print ("using gleif data")

                if(data["legalAddress"] !=None):    
                    xls_country =country
                    gleif_country =  data["country"]  
                    print("xls_country ", xls_country)  
                    print("gleif_country ", gleif_country)            
                    if (xls_country.strip() == gleif_country.strip()):
                        print("processing  gleif data ......")
                        la.append(data["legalAddress"])
                        oa.append(data["officeAddress"])
                        lei.append(data["LEI"])
                        
                else:
                        la.append("")
                        oa.append("")
                        lei.append("")
                        
                
                
                
def extract_opencorporate_data(df1, driver,country,  company, comnum,incopdat,comtyp,jurs,ra):
            # Opencoreporates 
                
                print("executing opencorporate")
                        
                data1 = opencorporates(company,driver,country)
                if(data1 !=None):
                    print("data1[Company Number]",data1["Company Number"])
                    comnum.append(data1["Company Number"])
                    incopdat.append(data1["Incorporation Date"])
                    comtyp.append(data1["Company Type"])
                    jurs.append(data1["Jurisdiction"])
                    ra.append(data1["Registered Address"])
                else:
                    comnum.append("")
                    incopdat.append("")
                    comtyp.append("")
                    jurs.append("")
                    ra.append("")
                            

            
                       
def generate_final_file(df):
        # gleif data processing 
        la,oa,lei,comnum,incopdat,comtyp,jurs,ra = [],[],[],[],[],[],[],[]
        
        for i,row in df.iterrows():
                company = row["Companies"]
                if "," in row["Companies"]:
                        company = row["Companies"].strip().split(",")[0]
                print("gleif company name " , company)

                word_length = len(company.split())
                if word_length > 2:
                        company = " ".join(company.strip().split()[:-1])
                
                extract_gleif_data(df,company,row["Country"].strip(),la,oa,lei)

        df["LegalAddress"] = la
        df["OfficeAddress"] = oa
        df["LEI"] = lei
        print ("gleif df ", df)
        #df.to_excel("FinalFile.xlsx",index=False)
        df.to_excel(filename,index=False)
        
        # gleif data processing ends 
                
        # open corporates 
        options = Options()
        options.headless = True
        driver = webdriver.Chrome(options=options)
        #driver = webdriver.Chrome(ChromeDriverManager().install())
        
        #df1=pd.read_excel("FinalFile.xlsx")
        df1=pd.read_excel(filename)
        for i,row in df1.iterrows():
                company = row["Companies"]
                if "," in row["Companies"]:
                        company = row["Companies"].strip().split(",")[0]
                print("company name " , company)
                country = row["Country"].strip()
                word_length = len(company.split())
                if word_length > 2:
                        company = " ".join(company.strip().split()[:-1])
                
                
                extract_opencorporate_data(df1, driver,country, company,comnum,incopdat,comtyp,jurs,ra)
              
        df1["Comapny Number"] = comnum
        df1["Incorporation Date"] = incopdat
        df1["Company Type"] = comtyp
        df1["Jurisdiction"] = jurs
        df1["Registered Address"] = ra
        
        print("opencorporate df1  ", df1)
        #df1.to_excel("FinalFile.xlsx",index=False)
        df1.to_excel(filename,index=False)
    
        driver.quit()
        
        #return df

        

        


if __name__ == "__main__":
        df = pd.read_excel("27-03-2024.xlsx")
        generate_final_file(df)
        
