import datetime
from sqlalchemy import text
from utils.db_config import getconn,get_db_data
import pandas as pd
#from dateutil import relativedelta


def get_jira_data():
    query_text = text('''
 select distinct company_key as "Client Code",
 --pip.key as facility_key,
         com.cr_number::BIGINT as "ID Number",
         split_part(com.city, '-',1)as "Address",
         --com.cr_entity_number,
        --'MC' as "city code",
        left(com.english_company_name,20) as "Latin Name",
        --left(com.summary,20) as "english arabic name",
        NULLIF(regexp_replace(com.company_zip_code, '\D','','g'), '')::float as "ZIP Code",
        --left(com.company_business_mobile_number,25) as "company business mobile number",
        --concat('MC',cr_entity_number) as "CR entity number",
        --to_char(com.gregorian_cr_expiry_date::date, 'DD/MM/YYYY') as "cr expiry date",
        left(com.english_company_name,75) as "long_company_name",
        com.company_type as "Legal Type",
        com.company_business_mobile_number as "Office Phone",
        --left(com.summary,75) as "summary",
        --'SAU' as "nationaly",
         company_po_box as "P.O. Box",
        to_char(com.gregorian_cr_issue_date::date, 'DD/MM/YYYY') as "cr issue date",
        split_part(com.cr_place_of_issue, '-',1)as "City of issue"
        --com.company_zip_code as "company zip code"
from pipeline_facility pip join company_issues as com on com.key=pip.company_key
        where com.jira_issue_status='exists' and pip.jira_issue_status='exists'
        --and disbursed_date >= '2022-06-23'
 ''')
    df = get_db_data(query_text)
    cities= pd.read_csv('data/CityofIssue.csv')
    df = pd.merge(df,cities, how='left',on='City of issue')
    print(df)
    df['City of issue']= df['cr_place_of_issue']
    df['City of issue'] = df['City of issue'].fillna('UNK')

    return df