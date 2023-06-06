def FilterFunction(final):
        
        try:         
            if (final.empty):
                return final
            
            key_1_gram = ['ipo', 'ipo', 'ipo ', 'spacs', 'ipo', 'pre-ipo', 'pre-ipo', 'pre-ipo', 'pre-ipo', 'spac', 'shares', 'pre ipo']
            key_2_gram = ['ipo calendar', 'shelves ipo', 'halts ipo', 'ipo pipeline', 'withdraws ipo', 'eyes ipo', 'ipo-bound', 'ipo registration', 'red herring', 'pre-initial public', 'pre-ipo announcement', 'ipos scheduled', 'ipo scheduled', 'offering ipo', 'listed on', 'go public', 'plan to', 'going public', 'offering shares', 'initial public', 'public offering', 'have listed', 'files for']
            
            key_3_gram = ['begins ipo process', 'set to ipo', 'ipo open for', 'open for subscription', 'prices ipo', 'expected ipo filings', 'files for ipo', 'upcoming ipo', 'an initial public', 'offer its shares', 'to the public', 'going to list', 'files for ipo', 'filed for ipo', 'initial public offering', 'public offering ipo']
            
            key_4_gram = ['gets nod for ipo', 'fixed a price band', 'sets ipo price band', 'planning to go public', 'preparing to go public', 'ipo to be launched', 'an initial public offering', 'the initial public offering', 'its initial public offering', 'initial public offering ipo', 'the initial public offering', 'its initial public offering ', 'has set its ipo', 'targeting a 2023 ipo']
            
            key_5_gram = ['planning an initial public offering', 'files a prospectus for ipo', 'considering an initial public offering', 'for an initial public offering']
            
            key_6_gram = [ 'sebagai ungkapan terimakasih atas perhatian anda', 'ungkapan terimakasih atas perhatian anda tersedia', 'terimakasih atas perhatian anda tersedia voucer', 'atas perhatian anda tersedia voucer gratis', 'perhatian anda tersedia voucer gratis senilai', 'anda tersedia voucer gratis senilai donasi',
                          'tersedia voucer gratis senilai donasi yang', 'voucer gratis senilai donasi yang bisa', 'gratis senilai donasi yang bisa digunakan', 'senilai donasi yang bisa digunakan berbelanja', 'donasi yang bisa digunakan berbelanja di', 'b initial public offering b b', 'b initial public offering b of', 'initial public offering b b ipo', 'public offering b b ipo b', 'the b initial public offering b', "Will Hold An Initial Public Offering", "On Its Potential Initial Public Offering"]
            key_7_gram = ["has filed for an initial public offering",'sebagai ungkapan terimakasih atas perhatian anda tersedia', 'ungkapan terimakasih atas perhatian anda tersedia voucer', 'terimakasih atas perhatian anda tersedia voucer gratis', 'atas perhatian anda tersedia voucer gratis senilai', 'perhatian anda tersedia voucer gratis senilai donasi', 'anda tersedia voucer gratis senilai donasi yang', 'tersedia voucer gratis senilai donasi yang bisa', 'voucer gratis senilai donasi yang bisa digunakan', 'gratis senilai donasi yang bisa digunakan berbelanja', 'senilai donasi yang bisa digunakan berbelanja di'
                          , 'dapat voucer gratis sebagai ungkapan terimakasih atas', 'voucer gratis sebagai ungkapan terimakasih atas perhatian', 'gratis sebagai ungkapan terimakasih atas perhatian anda', 'donasi yang bisa digunakan berbelanja di dukungan', 'yang bisa digunakan berbelanja di dukungan anda', 'bisa digunakan berbelanja di dukungan anda akan', "Raise Funds Through An Initial Public Offering"]
            key_8_gram = ["listing",'initial public offering','initial public offfering','to go public','goes Public','goes public','restricted shares','traded','list','listed','listing','lifted','allotment','Nyse','will be listed','stock exchange','delisting','moved to','hit','funding','raise','raises','valuation','going public','subscription','spac','sells','stake','debut','fundraising','board','enrollment','trade','hits','revenues','expansion','rebrand','subscribe','purchase','target price','shares','investing','allotmnet','approved','approves','fpo','registration','funds','sebi','investment','offering','nasdaq','files','launch','fund', 'stock', 'stocks', 'aims to', 'explores options', 'spinoff', 'digest', 'securities', "offer price"]
            title, link, published_date, scraped_date, text = [], [], [], [], []
            final["accepted"]=""
            for i, row in final.iterrows():
                
                article = str(row["title"]).lower()
                # print(article + "\n\n\n\n")
                c=0
                for j in key_1_gram:
                    if j in article:
                        c+=1
                        break
                for j in key_2_gram:
                    if j in article:
                        c+=1
                        break
                
                for j in key_3_gram:
                    if j in article:
                        c+=1
                        break
                
                for j in key_4_gram:
                    if j in article:
                        c+=1
                        break
                
                for j in key_5_gram:
                    if j in article:
                        c+=1
                        break
                
                for j in key_8_gram:
                    if j in article:
                        c+=1
                        break
                        
                if(c>0):
                    final.at[i, "accepted"]="Yes"
                else:
                    final.at[i, "accepted"]="No"
                c=0
            final=final[final["accepted"]=="Yes"]
            del final["accepted"]
            final = final.reset_index(drop=True)
            return final
        except:
            print("Issue in Filter Function")