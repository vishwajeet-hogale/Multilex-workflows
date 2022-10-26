import pandas as pd
from advertools import word_tokenize
import re
def tokenize_no_words(text_list, val):
    return set(word_tokenize(text_list, val)[0])
def conver_to_lower(li):
    return [str(i).lower() for i in li]

def FilterFunction(final):
        
        try:            
            if (final.empty):
                return final
            final["title"] = final["title"].str.replace(' b ',' ')
            final["text"] = final["text"].str.replace(' b ',' ')
            final["title"] = final["title"].str.replace(' B ',' ')
            final["text"] = final["text"].str.replace(' B ',' ')
            key_1_gram = ['IPO', 'IPO', 'IPO ', 'SPACs', 'ipo', 'pre-IPO',
                          'pre-ipo', 'PRE-IPO', 'pre-IPO', 'spac', 'shares', 'pre ipo']
            key_2_gram = ['offering ipo', "listed on", "go public", "plan to", "going public",
                          "offering shares", "initial public", "public offering", "have listed", "files for"]
            key_3_gram = ["an initial public", "offer its shares", "to the public", "going to list",
                          "files for ipo", "filed for ipo", "initial public offering", "public offering ipo"]
            key_4_gram = ["an initial public offering", "the initial public offering", "its initial public offering","initial public offering ipo", 
                          "The Initial Public Offering", "Its Initial Public Offering ", "Has Set Its Ipo", "Targeting A 2023 Ipo"]
            key_5_gram = ["Planning An Initial Public Offering", "Files A Prospectus For Ipo", "Considering An Initial Public Offering",'for an initial public offering']

            key_6_gram = [ 'sebagai ungkapan terimakasih atas perhatian anda', 'ungkapan terimakasih atas perhatian anda tersedia', 'terimakasih atas perhatian anda tersedia voucer', 'atas perhatian anda tersedia voucer gratis', 'perhatian anda tersedia voucer gratis senilai', 'anda tersedia voucer gratis senilai donasi',
                          'tersedia voucer gratis senilai donasi yang', 'voucer gratis senilai donasi yang bisa', 'gratis senilai donasi yang bisa digunakan', 'senilai donasi yang bisa digunakan berbelanja', 'donasi yang bisa digunakan berbelanja di', 'b initial public offering b b', 'b initial public offering b of', 'initial public offering b b ipo', 'public offering b b ipo b', 'the b initial public offering b', "Will Hold An Initial Public Offering", "On Its Potential Initial Public Offering"]
            key_7_gram = ["Has Filed For An Initial Public Offering",'sebagai ungkapan terimakasih atas perhatian anda tersedia', 'ungkapan terimakasih atas perhatian anda tersedia voucer', 'terimakasih atas perhatian anda tersedia voucer gratis', 'atas perhatian anda tersedia voucer gratis senilai', 'perhatian anda tersedia voucer gratis senilai donasi', 'anda tersedia voucer gratis senilai donasi yang', 'tersedia voucer gratis senilai donasi yang bisa', 'voucer gratis senilai donasi yang bisa digunakan', 'gratis senilai donasi yang bisa digunakan berbelanja', 'senilai donasi yang bisa digunakan berbelanja di'
                          , 'dapat voucer gratis sebagai ungkapan terimakasih atas', 'voucer gratis sebagai ungkapan terimakasih atas perhatian', 'gratis sebagai ungkapan terimakasih atas perhatian anda', 'donasi yang bisa digunakan berbelanja di dukungan', 'yang bisa digunakan berbelanja di dukungan anda', 'bisa digunakan berbelanja di dukungan anda akan', "Raise Funds Through An Initial Public Offering"]
            key_8_gram = []
            title, link, published_date, scraped_date, text = [], [], [], [], []
            for i, row in final.iterrows():
                cases = [0]*8
                article = str(str(row["title"]) + " " +
                              str(row["text"])).lower()
                # print(article + "\n\n\n\n")
                text_list = [article]
                key_1_gram = conver_to_lower(key_1_gram)
                key_2_gram = conver_to_lower(key_2_gram)
                key_3_gram = conver_to_lower(key_3_gram)
                key_4_gram = conver_to_lower(key_3_gram)
                key_5_gram = conver_to_lower(key_3_gram)
                key_6_gram = conver_to_lower(key_3_gram)
                key_7_gram = conver_to_lower(key_3_gram)
                # key_8_gram = conver_to_lower(key_3_gram)

                res_1_gram = tokenize_no_words(text_list, 1)
                res_2_gram = tokenize_no_words(text_list, 2)
                res_3_gram = tokenize_no_words(text_list, 3)
                res_4_gram = tokenize_no_words(text_list, 4)
                res_5_gram = tokenize_no_words(text_list, 5)
                res_6_gram = tokenize_no_words(text_list, 6)
                res_7_gram = tokenize_no_words(text_list, 7)
                # res_8_gram = tokenize_no_words(text_list, 8)
                if (len(res_1_gram.intersection(key_1_gram)) > 0):
                    cases[0] = 1
                if (len(res_2_gram.intersection(key_2_gram)) > 0):
                    cases[1] = 1
                if (len(res_3_gram.intersection(key_3_gram))):
                    cases[2] = 1
                if (len(res_4_gram.intersection(key_4_gram))):
                    cases[3] = 1
                if (len(res_5_gram.intersection(key_5_gram))):
                    cases[4] = 1
                if (len(res_6_gram.intersection(key_6_gram))):
                    cases[5] = 1
                if (len(res_7_gram.intersection(key_7_gram))):
                    cases[6] = 1
                # if (len(res_8_gram.intersection(key_8_gram))):
                #     cases[7] = 1
                if (cases[0] and (cases[1] or cases[2] or cases[3] or cases[4] or cases[5] or cases[6] )):
                    title.append(final['title'][i])
                    link.append(final['link'][i])
                    published_date.append(final['publish_date'][i])
                    scraped_date.append(final['scraped_date'][i])
                    text.append(final['text'][i])
                cases = [0]*8
            final = pd.DataFrame(list(zip(title, link, published_date, scraped_date, text)),
                                 columns=['title', 'link', 'publish_date', 'scraped_date', 'text'])
            final = final[~final['title'].isin(
                ["private placement", "reverse merger", "blank check merger"])]
            final = final[~final['text'].isin(
                ["private placement", "reverse merger", "blank check merger"])]
            final.to_csv("Newshab.csv")
            return final
        except:
            print("Issue in Filter Function")

if __name__ == "__main__":
    final = pd.read_csv("todays_report.csv")
    final = FilterFunction(final)
    final.to_csv("New_report.csv")
