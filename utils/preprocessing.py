import pandas as pd
from datetime import datetime
import numpy as np


legal_type_mapping = {'Chamber of ': "CCI", 'Female': "CCI",'General ':'GPA','Insurance ':'ISO',
'Joint Stock ':'JSC','Licensed ':'UNK','Limited ':'LPA','Literary, ':'UNK',"Male":'CCI','Unknown':'UNK',' ':'UNK',
'Sole Proprietorship': "LLC",
 'Establishment': "LBS",
'General Partnership':'GPA','Insurance ':'ISO',
'Joint Stock ':'JSC','Licensed ':'UNK','Limited ':'LPA','Literary, ':'UNK',"Male":'CCI','Unknown':'UNK',' ':'UNK'}


def check_uploded_columns(df):

    if 'LastAmountPaid' not in df:
        df['LastAmountPaid'] =np.nan
        df['LastPaymentDate'] = np.nan

    if 'PastDueBalance' not in df:
        df['PastDueBalance'] = df['PastDueAmount']

    if 'CurrentBalance' not in df:
        df['CurrentBalance'] = df['OutstandingBalanceAmount']
    if 'StartDate' not in df:
        df['StartDate'] = pd.to_datetime(df['IssueDate'])
    

    return df



def change_format(df,column):
    df[column]= pd.to_datetime(df[column])
    df[column] = df[column].dt.strftime("%Y%m%d")
    if (column != 'SatisfactionDate')& (column != 'SettleDate'):
        df[column] = df[column].fillna(0).astype(int)
    return df[column]


def get_preprocessing(df):
    
    df = df.replace({"Legal Type": legal_type_mapping})
    df['age'] = (df['StartDate'].apply(lambda x : pd.to_datetime("now") - x)).dt.days/365
    df['CloseDate']=change_format(df,'CloseDate')
    df['SettleDate']= change_format(df,'SettleDate')
    df['StartDate']= change_format(df,'StartDate')
    df['LastPaymentDate']= change_format(df,'LastPaymentDate')
    df['SatisfactionDate']= change_format(df,'SatisfactionDate')
    df['installment_amount'] = df['InstallmentAmount'].fillna(0).astype(int)
    df["Legal Type"]=df["Legal Type"].fillna('UNK')

   
    return df
 