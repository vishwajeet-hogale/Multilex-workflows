import requests
import json

def company_info(companyname):
        #api_url = "https://api.gleif.org/api/v1/fuzzycompletions?field=entity.legalName&q=ABB E-mobility"
        api_url="https://api.gleif.org/api/v1/fuzzycompletions?field=entity.legalName&q="+companyname
        response = requests.get(api_url)
        #print(response.json())
        #print(response.status_code)
        json_format = json.loads(response.text)
        #print(json_format['assets'][0]['network_ports'][0]['version'])
        #print(json_format['data'])

        for i in json_format['data']:
                #print (i['attributes']['value'])
                key='relationships'
                x = list(i.keys())
                if(x.count(key) == 1):
                        #print (i['relationships']['lei-records']['links']['related'])
                        api_url1=i['relationships']['lei-records']['links']['related']
                        response1=requests.get(api_url1)
                        #print(response1.status_code)
                        json_format1 = json.loads(response1.text)
                        print("Company name : ",json_format1['data']['attributes']['entity']['legalName']['name'])
                        legalAddress_details=""
                        for j in json_format1['data']['attributes']['entity']['legalAddress']['addressLines']:
                                legalAddress_details=str(legalAddress_details) + str(j)
                        #print("aaaaaa", legalAddress_details)
                        legalAddress=str(legalAddress_details)+" "+str(json_format1['data']['attributes']['entity']['legalAddress']['city'])+ " "+str(json_format1['data']['attributes']['entity']['legalAddress']['region'])+ " "+str(json_format1['data']['attributes']['entity']['legalAddress']['country'])
                        #legalAddress=str(json_format1['data']['attributes']['entity']['legalAddress']['addressLines'])+" "+str(json_format1['data']['attributes']['entity']['legalAddress']['city'])+ " "+str(json_format1['data']['attributes']['entity']['legalAddress']['region'])+ " "+str(json_format1['data']['attributes']['entity']['legalAddress']['country'])
                        #print("legalAddress",json_format1['data']['attributes']['entity']['legalAddress']['addressLines'])
                        print("legalAddress : ",legalAddress)
                        print("legaladdress Country name :",json_format1['data']['attributes']['entity']['legalAddress']['country'])

                        HQAddress_details=""
                        for j in json_format1['data']['attributes']['entity']['headquartersAddress']['addressLines']:
                                HQAddress_details=str(HQAddress_details) + str(j)
                        
                        headquarterAddress=str(HQAddress_details)+" "+str(json_format1['data']['attributes']['entity']['headquartersAddress']['city'])+ " "+str(json_format1['data']['attributes']['entity']['headquartersAddress']['region'])+ " "+str(json_format1['data']['attributes']['entity']['headquartersAddress']['country'])
                        #headquarterAddress=str(json_format1['data']['attributes']['entity']['headquartersAddress']['addressLines'])+" "+str(json_format1['data']['attributes']['entity']['headquartersAddress']['city'])+ " "+str(json_format1['data']['attributes']['entity']['headquartersAddress']['region'])+ " "+str(json_format1['data']['attributes']['entity']['headquartersAddress']['country'])
                        print("headquarterAddress : ",headquarterAddress)


#company_info("ABB E-mobility")
company_info("paytm")
