import pandas as pd
from datetime import datetime


legal_type_mapping = {'Chamber of ': "CCI", 'Female': "CCI",'General ':'GPA','Insurance ':'ISO',
'Joint Stock ':'JSC','Licensed ':'UNK','Limited ':'LPA','Literary, ':'UNK',"Male":'CCI','Unknown':'UNK',' ':'UNK',
'Sole Proprietorship': "LLC",
 'Establishment': "LBS",
'General Partnership':'GPA','Insurance ':'ISO',
'Joint Stock ':'JSC','Licensed ':'UNK','Limited ':'LPA','Literary, ':'UNK',"Male":'CCI','Unknown':'UNK',' ':'UNK'}
#
def preprocessing_df(df):
    
    df = df.replace({"Legal Type": legal_type_mapping})
    df['CloseDate']= pd.to_datetime(df['CloseDate'])
    df['CloseDate'] = df['CloseDate'].dt.strftime("%Y%m%d")
    df['CloseDate'] = df['CloseDate'].fillna(0).astype(int)
    df['SettleDate']= pd.to_datetime(df['SettleDate'])
    df['SettleDate'] = df['SettleDate'].dt.strftime("%Y%m%d")
    df['SettleDate'] = df['SettleDate'].fillna(0).astype(int)
    df['StartDate']= pd.to_datetime(df['StartDate'])
    df['StartDate'] = df['StartDate'].dt.strftime("%Y%m%d")
    df['StartDate'] = df['StartDate'].fillna(0).astype(int)
    df['LastPaymentDate']= pd.to_datetime(df['LastPaymentDate'])
    df['LastPaymentDate'] = df['LastPaymentDate'].dt.strftime("%Y%m%d")
    df['LastPaymentDate'] = df['LastPaymentDate'].fillna(0).astype(int)
    df['SatisfactionDate']= pd.to_datetime(df['SatisfactionDate'])
    df['SatisfactionDate'] = df['SatisfactionDate'].dt.strftime("%Y%m%d")
    df['SatisfactionDate'] = df['SatisfactionDate'].fillna(0).astype(int)
    df['installment_amount'] = df['InstallmentAmount'].fillna(0).astype(int)
    df["Legal Type"]=df["Legal Type"].fillna('UNK')
   
    return df
 