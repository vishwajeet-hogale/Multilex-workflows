import pandas as pd 

def FilterFunction(final):
        # import matplotlib.pyplot as plt
        try:
            keyword = [ 'IPO','IPO','IPO ','SPACs','ipo','pre-IPO','pre-ipo','PRE-IPO','pre-IPO','going public','spac','shares','public']
            
            # keyword = [ "Follow-on Offering", 'FPO', 'Seasoned Equity Offering', 'SEO',' Bookrunner', 'Underwriter', 'Rumour', 'Primary Exchange', 'Currency','raised','IPO','IPO','IPO ','SPACs','ipo','pre-IPO','pre-ipo','PRE-IPO','pre-IPO','going public','public','closes','listing','planning','closing','excellent','Public','Initial','Offering','initial','Announces','Pricing','pricing','announces','launches','Launches','SPAC','spac']
            keywords1=['IPO,','IPO,','IPO, ','SPACs,','ipo,','pre-IPO,','pre-ipo,','PRE-IPO,','pre-IPO,','going public,','public,','closes,','listing,','planning,','closing,','excellent,','Public,','Initial,','Offering,','initial,','Announces,','Pricing,','pricing,','announces,','launches,','Launches,','SPAC,','spac,']
            keywords=keyword
            title=[]
            link=[]
            published_date=[]
            scraped_date=[]
            text=[]
            flag=False
              #Here is the dataframe to be passed
                
            for i in range(0,final.shape[0]):
                article=final["title"][i] + " " + final['text'][i]
                article=article.split(" ")
                for let in article:
                    if let in keywords :
                        flag=True
                        break
                if flag==True:
                    title.append(final['title'][i])
                    link.append(final['link'][i])
                    published_date.append(final['publish_date'][i])
                    scraped_date.append(final['scraped_date'][i])
                    text.append(final['text'][i])
                    flag=False
        except:
            print('DataFrame is blank')
        final = pd.DataFrame(list(zip(title,link,published_date,scraped_date,text)), 
                   columns =['title','link','publish_date','scraped_date','text'])
        final = final[~final['title'].isin(["private placement", "reverse merger", "blank check merger"])]
        final = final[~final['text'].isin(["private placement", "reverse merger", "blank check merger"])]
        
        return final 
    