import pandas as pd
import datetime as dt

MEMBER_ID = 'ALLM'
VERSION = '0102'  #Version (always set to “0101” or “0102”)
FLAG = 'N' #Financial Storage Flag (Set to “Y” if financial details on corporates are captured. Otherwise set to “N”)
ISSUER = 'MC' # Issuer (Ministry of Commerce and Investment)

prod_type = 'OBC'#'ODF' for version 2 insted of OBC 3PRODUCT_TYPE
def get_text_header():
    
    record_id = '000'
    date = dt.datetime.now().strftime("%Y%m%d") #Date snapshot of data taken  & Date snapshot of data applies  
    time = dt.datetime.now().strftime("%H%M") #Time snapshot of data applies to (HHMM)
    
    
    
    return record_id+MEMBER_ID+date+time+date+time+VERSION+FLAG

def get_detailed_record(Record_id,cr,city,com_name,zip_code):
    
    Record_id = Record_id # Record identifier 
    cr = "{:<15.0f}".format(cr)# Customer ID Number (CR Number)
    city = "{:<3}".format(city)
    com_name = "{:<40}".format(com_name)
    zip_code = "{:<30}".format('') if pd.isna(zip_code) else "{:<30.0f}".format((zip_code))

    return Record_id + cr + ISSUER + city + com_name + zip_code
    
def get_table_105(cr,long_com_name,legal_form):
    
    cr = "{:<26.0f}".format(cr)# Customer ID Number (CR Number)
    name = "{:<150}".format(long_com_name)#Name (ethier english or arabic name should be supplied)
    nationality  = 'SAU'
    #legal form GPA General Partnership  - LLC Limited Liability Company - JSC Closed Joint Stock Company - other LBS
    legal_form = "{:<78}".format(legal_form)
    #f.seek(353)
    corp_flag = 'N' #Corporate flag
    
    return ISSUER + cr + name + nationality + legal_form + corp_flag

def get_table_120(po,city):
        po = "" if pd.isna(po) else "{:.0f}".format(po)
        city= city
        return city + 'P.O.BOX' + str(po)

def get_table_125(phone):
    return ''.join('O'+'966'+'001')+str(phone)
    
def get_table_600(row):
    '''
    This record contains details of payments and defaults.
    Within the Commercial Bureau, defaults will be provided on the same record as credit instruments.  
    The method of sharing account information is also known as CAIS (Customer Account Information Sharing).
    Maximum of 5000 records provided for a customer –warning message returned when there are more than 50 records.
    '''
    
    account_number = str(row['AccountNumber']).ljust(25)
    guarantor_indicator = row['GuarantorIndicator']
    product_type = row['ProductType']
    start_date = str(row['StartDate'])
    close_date = "{:<8}".format(row['CloseDate'])
    installment_amount = "{:<16.0f}".format('') if pd.isnull(row['InstallmentAmount']) else"{:<16.0f}".format(row['InstallmentAmount'])
    repayment_period ='{:.0f}'.format(row['RepaymentPeriod']).zfill(3) 
    current_balance = "{:<17.0f}".format(row['CurrentBalance'])
    payment_status = "{:<2}".format(row['PaymentStatus'])
    last_amount_paid = "{:<20}".format("") if pd.isna(row['LastAmountPaid']) else "{:<20.0f}".format(row['LastAmountPaid'])
    prev_statement_balance = "{:<14}".format('00000000')
    credit_limit = "{:<18.0f}".format(row['CreditLimit'])
    satisfaction_date = "{:<8}".format('') if pd.isna(row['SatisfactionDate']) else "{:<8}".format(row['SatisfactionDate'])
    original_default_balance = "{:<16}".format("") if pd.isna(row['OriginalDefaultBalance']) else "{:<16.0f}".format(row['OriginalDefaultBalance'])
    payment_frequency = row['PaymentFrequency']
    security_type ='NO' #this need to be updated based on SECTYPE table
    past_due_balance= "{:<16.0f}".format(row['PastDueBalance'])
    last_payment_date = "{:<16}".format("") if pd.isna(row['LastPaymentDate']) else "{:<16}".format(row['LastPaymentDate'])
    expiry_date = "{:<8}".format('0')
    product_status = str(row['ProductStatus']) #PRODSTATUS A for active , C closed , D for Default
    government_gurantted = 'N'
    default_status = "{:<2}".format('') if pd.isna(row['DefaultStatus']) else str(row['DefaultStatus'])
    settle_date = "{:<8}".format('') if pd.isna(row['SettleDate']) else "{:<8}".format(row['SettleDate'])
    limit_category = "{:<39}".format('FUNDED')
    new_loan_from_restructured = 'N'
    revolving_limit = "{:<441}".format('N')
    as_of_date= dt.datetime.now().strftime("%d/%m/%Y")
    
    return account_number+guarantor_indicator+product_type+start_date+close_date+installment_amount\
+repayment_period+current_balance+payment_status+last_amount_paid+prev_statement_balance+credit_limit+satisfaction_date\
+original_default_balance+payment_frequency+security_type+past_due_balance+last_payment_date+expiry_date+product_status+government_gurantted+default_status\
+settle_date+limit_category+new_loan_from_restructured+revolving_limit+as_of_date

    