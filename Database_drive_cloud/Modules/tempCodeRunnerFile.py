    file_data = base64.urlsafe_b64decode(attachment['body']['data'])
                        
                        if attachment['filename'].endswith('.xlsx'):
                            df = pd.read_excel(BytesIO(file_data))
                        elif attachment['filename'].endswith('.csv'):
                            df = pd.read_csv(BytesIO(file_data))
                        else:
                            df = None 
                        if df is not None:
                            try:
                                dataframes[filename].append(df)
                            except:
                                dataframes[filename]=[df]