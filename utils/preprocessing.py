import pandas as pd
from datetime import datetime


legal_type_mapping = {'Chamber of ': "CCI", 'Female': "CCI",'General ':'GPA','Insurance ':'ISO',
'Joint Stock ':'JSC','Licensed ':'UNK','Limited ':'LPA','Literary, ':'UNK',"Male":'CCI','Unknown':'UNK',' ':'UNK',
'Sole Proprietorship': "LLC",
 'Establishment': "LBS",
'General Partnership':'GPA','Insurance ':'ISO',
'Joint Stock ':'JSC','Licensed ':'UNK','Limited ':'LPA','Literary, ':'UNK',"Male":'CCI','Unknown':'UNK',' ':'UNK'}

def date_format(df,column):
    df[column]= pd.to_datetime(df[column])
    df[column] = df[column].dt.strftime("%Y%m%d")
    df[column] = df[column].fillna(0).astype(int)
    return df[column]


def preprocessing_df(df):
    
    df = df.replace({"Legal Type": legal_type_mapping})
    df['CloseDate']=date_format(df,'CloseDate')
   
    df['SettleDate']= date_format(df,'SettleDate')
    
    df['StartDate']= date_format(df,'StartDate')
    
    df['LastPaymentDate']= date_format(df,'LastPaymentDate')
    
    df['SatisfactionDate']= date_format(df,'SatisfactionDate')
    
    df['installment_amount'] = df['InstallmentAmount'].fillna(0).astype(int)
    
    df["Legal Type"]=df["Legal Type"].fillna('UNK')
   
    return df
 