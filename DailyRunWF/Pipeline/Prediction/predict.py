import os
import pandas as pd
import spacy
from datetime import date
# from simpletransformers.question_answering import QuestionAnsweringModel, QuestionAnsweringArgs
def NERModel_lg(input_dir, output_dir):
        spacy_model='en_core_web_sm'
        nlp1 = spacy.load(spacy_model)
        input_file_fullpath = os.path.join(input_dir,'todays_report.csv')
        data = pd.read_csv(input_file_fullpath)
        data = data[['text','publish_date','scraped_date','title','link']]
        text = data['text']
        title = data['title']
        lst1 =[]
        for i in text:
                lst_1 =[]
                i = str(i)
                print(i)
                doc = nlp1(i)
                for element in doc.ents:
        #             print(element.label_)
                        if element.label_ == 'ORG':
                                lst_1.append(element)
                lst1.append(lst_1)     

        lst2=[]
        for i in title:
                lst_2 =[]
                i = str(i)
                doc = nlp1(i)
                for element in doc.ents:
        #             print(element.label_)
                    if element.label_ == 'ORG':
                        lst_2.append(element)
                lst2.append(lst_2)        
        dic = {'companies_1':lst1,'companies_2':lst2}
        df = pd.DataFrame(dic)
        dff = [data,df]
        df_final = pd.concat(dff,axis=1)
        df_final.to_csv('EDI_PREIPO_report.csv',index=False)
        df = pd.read_csv('EDI_PREIPO_report.csv')
        df["Companies"] = df['companies_1'].str.cat(df['companies_2'],sep=",")
#         df_final["Companies"] = df_final.companies_1.str.cat(df_final.companies_2)
        df = df[['text','publish_date','scraped_date','title','Companies','link']]
        edi_preipo_report_fname = os.path.join( output_dir, 'EDI_PREIPO_report.csv' )
        # logging.info("writing output artifact " + edi_preipo_report_fname + " to " + output_dir)
        df.to_csv(edi_preipo_report_fname,index=False)

# def company(myModel,text):
#     predict_questions = [
#                     {
#                         "context": text,
#                         "qas": [
#                                 {
#                                     "id": "1",
#                                  "question": "which company is going ipo?"
#                                  }
#                         ]
#                     }
#     ]
#     answers, probabilities = myModel.predict(predict_questions)
#     company=[]
#     for i in answers[0]['answer']:
#         if i !='':
#             company.append(i)
#     # print(company)
#     return company
# def NERModel_lg(input_dir, output_dir):
#         import os
#         print(os.getcwd())
#         # %%
#         import pandas as pd
#         # import spacy
#         from datetime import datetime ,date
#         import pyshorteners
#         cur_date = str(date.today())

#         # download the spacy model.  TODO: switch to en_core_web_lg
#         # spacy_model='en_core_web_sm'
#         # spacy_model='en_core_web_lg'
#         # download_spacy_model(spacy_model)
#         # load the module.  
#         # nlp1 = spacy.load(spacy_model)
#         with open(input_dir + "NewQuestionAnsweringModel_v2.pkl", "rb") as newFile:
#             myModel = pickle.load(newFile)
#         input_file_fullpath = os.path.join(input_dir,'todays_report.csv')
#         logging.info("reading input artifact " + input_file_fullpath)
#         data = pd.read_csv(input_file_fullpath)
#         logging.info("completed reading input artifact " + input_file_fullpath)
#         # data.drop('companies', inplace=True, axis=1)
#         data = data[['text','publish_date','scraped_date','title','link']]
#         text = data['text']
#         title = data['title']   
#         company_names = []
#         for val,i in data.iterrows():
#             t = str(i["title"]) + " " + str(i["text"])
#             print(t)
#             company_names.append(company(myModel, t))
#         # data["Companies"] = company_names
#         dic = {'Companies':company_names}
#         #["abc","def"]
#         df = pd.DataFrame(dic)
#         #data=["text","title"]
#         dff = [data,df]
        
#         df_final = pd.concat(dff,axis=1)
#         # df_final.to_csv('EDI_PREIPO_report.csv',index=False)


#         # %%

#         # import ipynb
#         # df = pd.read_csv('EDI_PREIPO_report.csv')
#         # df["Companies"] = df['companies_1'].str.cat(df['companies_2'],sep=",")
#         # df = df[['text','pub*lish_date','scraped_date','title','Companies','link']]
#         edi_preipo_report_fname = os.path.join( output_dir, 'EDI_PREIPO_report.csv' )
#         logging.info("writing output artifact " + edi_preipo_report_fname + " to " + output_dir)
#         df_final.to_csv(edi_preipo_report_fname,index=False)
#         logging.info("completed writing output artifact " + edi_preipo_report_fname + " to " + output_dir)
if __name__ == "__main__":
    NERModel_lg("", "")    



