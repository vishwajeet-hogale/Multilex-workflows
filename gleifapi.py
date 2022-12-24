import requests
import json
import pandas as pd
def company_info(companyname):
        #api_url = "https://api.gleif.org/api/v1/fuzzycompletions?field=entity.legalName&q=ABB E-mobility"
        api_url="https://api.gleif.org/api/v1/fuzzycompletions?field=entity.legalName&q="+companyname
        response = requests.get(api_url)
        #print(response.json())
        #print(response.status_code)
        json_format = json.loads(response.text)
        #print(json_format['assets'][0]['network_ports'][0]['version'])
        print(json_format['data'][0]["relationships"]["lei-records"]["data"]["id"])
        # print(json_format)

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


def company_info1(companyname):
        api_url="https://api.gleif.org/api/v1/fuzzycompletions?field=entity.legalName&q="+str(companyname)
        response = requests.get(api_url)
        json_format = json.loads(response.text)
        print(json_format["data"])
        res_obj = {"company_name":None,"legalAddress":None,"officeAddress":None,"country":None,"LEI":None}
        try:
                i = json_format['data'][0]
        except:
                return res_obj
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
                HQAddress_details=""
                for j in json_format1['data']['attributes']['entity']['headquartersAddress']['addressLines']:
                        HQAddress_details=str(HQAddress_details) + str(j)
                
                headquarterAddress=str(HQAddress_details)+" "+str(json_format1['data']['attributes']['entity']['headquartersAddress']['city'])+ " "+str(json_format1['data']['attributes']['entity']['headquartersAddress']['region'])+ " "+str(json_format1['data']['attributes']['entity']['headquartersAddress']['country'])
                res_obj["officeAddress"] = headquarterAddress
                res_obj["LEI"] = json_format['data'][0]["relationships"]["lei-records"]["data"]["id"]
        return res_obj

def generate_final_file(df):
        la,oa,lei = [],[],[]
        for i,row in df.iterrows():
                data = company_info1(row["Companies"])
                print(data)
                la.append(data["legalAddress"])
                oa.append(data["officeAddress"])
                lei.append(data["LEI"])
        df["LegalAddress"] = la
        df["OfficeAddress"] = oa
        df["LEI"] = lei
        df.to_csv("FinalFile.csv")
        return df


#company_info("ABB E-mobility")
if __name__ == "__main__":
        df = pd.read_excel("FinalFile.xlsx")
        print(generate_final_file(df))