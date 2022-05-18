import pandas as pd
from datetime import datetime


legal_type_mapping = {'Chamber of ': "CCI", 'Female': "CCI",'General ':'GPA','Insurance ':'ISO',
'Joint Stock ':'JSC','Licensed ':'UNK','Limited ':'LPA','Literary, ':'UNK',"Male":'CCI','Unknown':'UNK',' ':'UNK',
'Sole Proprietorship': "LLC",
 'Establishment': "LBS",
'General Partnership':'GPA','Insurance ':'ISO',
'Joint Stock ':'JSC','Licensed ':'UNK','Limited ':'LPA','Literary, ':'UNK',"Male":'CCI','Unknown':'UNK',' ':'UNK'}



def preprocessing_df(df):

    for i, row in df.iterrows():
        date_number= datetime.strptime(df.loc[i, 'StartDate'], '%Y-%m-%d').strftime('%Y%m%d')
        df.loc[i, 'StartDate'] = date_number
        date_number= datetime.strptime(df.loc[i, 'CloseDate'], '%Y-%m-%d').strftime('%Y%m%d')
        df.loc[i, 'CloseDate'] = date_number
        date_number= datetime.strptime(df.loc[i, 'LastPaymentDate'], '%Y-%m-%d').strftime('%Y%m%d')
        df.loc[i, 'LastPaymentDate'] = date_number
        date_number= datetime.strptime(df.loc[i, 'SatisfactionDate'], '%Y-%m-%d').strftime('%Y%m%d')
        df.loc[i, 'SatisfactionDate'] = date_number
        date_number= datetime.strptime(df.loc[i, 'SettleDate'], '%Y-%m-%d').strftime('%Y%m%d')
        df.loc[i, 'SettleDate'] = date_number


    df = df.replace({"Legal Type": legal_type_mapping})
    df['CloseDate']= pd.to_datetime(df['CloseDate'])
    df['CloseDate'] = df['CloseDate'].dt.strftime("%Y%m%d")
    df['installment_amount'] = df['InstallmentAmount'].fillna(0).astype(int)
    df['CloseDate'] = df['CloseDate'].fillna(0).astype(int)
  #df['LastPaymentDate'] = df['LastPaymentDate'].fillna(0).astype(int)
    df["Legal Type"]=df["Legal Type"].fillna('UNK')

    return df
 