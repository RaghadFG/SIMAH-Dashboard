import dash
import dash_design_kit as ddk
from dash import dcc
import dash_html_components as html
from dash.dependencies import Input, Output
import plotly.express as px
import base64
from datetime import datetime
import numpy as np
import math
import io
import theme
import dash
from dash.dependencies import Input, Output, State
import plotly.graph_objs as go
import pandas as pd
import dash_table
from utils.text_format import *
from utils.preprocessing import get_preprocessing,check_uploded_columns 
app = dash.Dash(__name__)
server = app.server 


month=datetime.now().date().month  
Fname=str(month)+"th-month SIMAH Report.txt"
columnheaders =pd.read_excel('column header names.xlsx', engine='openpyxl')


app.layout = ddk.App(theme=theme.theme,children=[

    ddk.Header([
        ddk.Logo(src=app.get_asset_url('logo.png')),
        ddk.Title('SIMAH Dashbord'),
    ])

    ,html.Div([html.Div([
    ddk.Card([
    ddk.Row(children=
    [html.Div([

          dcc.Markdown('''
    **Please consider the following simple steps:**
''')
      ,
        dcc.Markdown('''

    * Download the required column headers.
    * Upload the Excel file.
    * Download SIMAH report.
    
''')
,
  
        

    ])]
    )
    ])]),
#
        html.P(),
        html.Button("Download required column", id="btn_xlsx", style={'margin-left':'10px'}),
        dcc.Download(id="download-dataframe-xlsx"),html.P(),

    html.Div([
    ddk.Card([
    ddk.Row(children= [html.Div([

         dcc.Markdown('''
    **Policies & Legal requirements:**
''')
      ,
        dcc.Markdown('''
    * Send notifications for clients to inform them with sharing data to SIMAH Systems
    * Default account definition: reporting account as default when the overdue exceeds 180 Days of due date
    * Send Notification for the client before reporting as Default (30-Days before)
    * Data quality reports will be sent in monthly basis by SIMAH for live data through MFT
    
''')
,
    ])]

    )])])
    
    ,html.Div([
    dcc.Upload(
        id='upload-data',
        children=html.Div([
            'Drag and Drop or ',
            html.A('Select Files')
        ]),
        style={
            'width': '100%',
            'height': '60px',
            'lineHeight': '60px',
            'borderWidth': '1px',
            'borderStyle': 'dashed',
            'borderRadius': '5px',
            'textAlign': 'center',
            'margin': '10px'
        },
        # Allow multiple files to be uploaded
        multiple=True
    ),
    html.Div(id='output-data-upload'),

   
         html.Button("Download SIMAH report", id="btn-download-txt", style={'margin-left':'9px'}),
         dcc.Download(id="download-text")
    
])
])])

def parse_contents(contents, filename, date):
    global erorr_df,Flag

    error_data = {
    "AccountNumber": [None],
    "Error": [None]
    }

    erorr_df = pd.DataFrame(error_data)
    Flag = False

    content_type, content_string = contents.split(',')
    decoded = base64.b64decode(content_string)
    
    global df
    try:
        if 'csv' in filename:
            # Assume that the user uploaded a CSV file
           
            df = pd.read_csv(
                io.StringIO(decoded.decode('utf-8')))
        elif 'xls' in filename:
            # Assume that the user uploaded an excel file
            df= pd.read_excel(io.BytesIO(decoded),engine='openpyxl')
        

    except Exception as e:
        print(e)
        return html.Div([
            'There was an error processing this file.'
        ])
       
    df = check_uploded_columns(df)
    #Check validation rules
    for i,row in df.iterrows():
        
        #check 1st rule
        if (row['LastAmountPaid'] == 0) and (row['LastPaymentDate']!=''):
            Flag=True
            erorr_df.at[i,'AccountNumber'] = row['AccountNumber']
            #1st error in AccountNumber
            if erorr_df.at[i,'Error'] == None or (str(erorr_df.at[i,'Error'])=='nan'):
                erorr_df.at[i,'Error'] = 'Error: LastAmountPaid = 0 while valid LastPaymentDate is provided'
            #more than one error in the same AccountNumber
            else:
                erorr_df.at[i,'Error'] = 'Error: LastAmountPaid = 0 while valid LastPaymentDate is provided'+' | '+str(erorr_df.at[i,'Error'])

        #check 2st rule
        if (row['LastAmountPaid'] != 0) and (row['LastPaymentDate']==''):
            Flag=True
            erorr_df.at[i,'AccountNumber'] = row['AccountNumber']
            #1st error in AccountNumber
            if erorr_df.at[i,'Error'] == None or (str(erorr_df.at[i,'Error'])=='nan'):
                erorr_df.at[i,'Error'] = 'Error: LastPaymentDate is not provided while there is amount paid'
            #more than one error in the same AccountNumber
            else:
                erorr_df.at[i,'Error'] = 'Error: LastPaymentDate is not provided while there is amount paid'+' | '+str(erorr_df.at[i,'Error'])
        
        #check 3st rule
        if row['PastDueBalance']>row['CurrentBalance']:
            Flag=True
            erorr_df.at[i,'AccountNumber'] = row['AccountNumber']
            #1st error in AccountNumber
            if erorr_df.at[i,'Error'] == None or (str(erorr_df.at[i,'Error'])=='nan'):
                erorr_df.at[i,'Error'] = 'Error: PastDueBalance > OutStanding'
            #more than one error in the same AccountNumber
            else:
                erorr_df.at[i,'Error'] = 'Error: PastDueBalance > OutStanding'+' | '+str(erorr_df.at[i,'Error'])

        #check 4st rule
        if  (row['PaymentStatus'] == 1) and (row['PastDueBalance']<= 0):
            Flag=True
            erorr_df.at[i,'AccountNumber'] = row['AccountNumber']
            #1st error in AccountNumber
            if erorr_df.at[i,'Error'] == None or (str(erorr_df.at[i,'Error'])=='nan'):
                erorr_df.at[i,'Error'] = 'Error: PaymentStatus is 1 while PastDueBalance is not > 0'
            #more than one error in the same AccountNumber
            else:
                erorr_df.at[i,'Error'] = 'Error: PaymentStatus is 1 while PastDueBalance is not > 0'+" | "+str(erorr_df.at[i,'Error'])       


    #the uploaded file has errors
    if Flag:
        #show the errors
        return html.Div([
        
        html.H5('Ops fix the errors then try uploading the file again'),
        html.H6('Error Table'),
    

        dash_table.DataTable(
            data=erorr_df.to_dict('records'),
            columns=[{'name': i, 'id': i} for i in erorr_df.columns]
        ),

        html.Hr(), 
            ])

    #show the uploaded file
    else:
        return html.Div([
            dash_table.DataTable(
                data=df.to_dict('records'),
                columns=[{'name': i, 'id': i} for i in df.columns]
            ),

            html.Hr(),  
        ])

@app.callback(
    Output("download-dataframe-xlsx", "data"),
    Input("btn_xlsx", "n_clicks"),
    prevent_initial_call=True,
)

def funcc(n_clicks):
    return dcc.send_data_frame(columnheaders.to_excel, "columnheaders.xlsx")


@app.callback(Output('output-data-upload', 'children'),
              Input('upload-data', 'contents'),
              State('upload-data', 'filename'),
              State('upload-data', 'last_modified')
              )


def update_output(list_of_contents, list_of_names, list_of_dates):
    if list_of_contents is not None:
        children = [
            parse_contents(c, n, d) for c, n, d in
            zip(list_of_contents, list_of_names, list_of_dates)]
        return children


@app.callback(
    Output("download-text", "data"),
    Input("btn-download-txt", "n_clicks"),
    prevent_initial_call=True,
)

def func(n_clicks):
    #download the errors in the uploaded file 
    if Flag:
        return dcc.send_data_frame(erorr_df.to_csv, "Error-table.csv")

   

    clients_df=pd.read_excel('data/ClientDetails.xlsx', engine='openpyxl')

    ClientCode=pd.read_excel('data/ClientCodeLookUp.xlsx',  engine='openpyxl')

    first_merge=pd.merge(clients_df,ClientCode,on='Client Code')

   
    #Merge with uploaded file
    #first_merge['AccountNumber']=first_merge['AccountNumber'].astype(str)
    full_df=pd.merge(first_merge, df, on='AccountNumber')
    
    full_df =full_df[full_df['AccountNumber'].isin(df['AccountNumber'])]
    full_df=get_preprocessing(full_df)
  
    #Unique clients 
    clients =full_df.drop_duplicates(subset=['Client Code'])

    #Start fill the text file
    with open('ALLM_COMM_20220440.txt','w') as f:
        i= 1    
        #Header Block 000
        f.write(get_text_header())
        for index, row in clients.iterrows():
            #Block 105
            f.write('\n')
            i=i+1
            f.write(get_detailed_record('105',row['ID Number'],row['City of issue'],row['Latin Name'],row['ZIP Code']))
            f.write(get_table_105(row['ID Number'],row['Latin Name'],row['Legal Type']))

            #Block 120
            f.write('\n')
            i=i+1
            f.write(get_detailed_record('120',row['ID Number'],row['City of issue'],row['Latin Name'],row['ZIP Code']))
            f.write(get_table_120(row['P.O. Box'],row['Address']))

            
            #Block 125
            i=i+1
            f.write('\n')
            f.write(get_detailed_record('125',row['ID Number'],row['City of issue'],row['Latin Name'],row['ZIP Code']))# Record identifier
            f.write(get_table_125(row['Office Phone']))



            #Block 600
            temp = full_df[full_df['Client Code']==row['Client Code']]
            for index, row in temp.iterrows(): 
                f.write('\n')
                i=i+1
                f.write(get_detailed_record('600',row['ID Number'],row['City of issue'],row['Latin Name'],row['ZIP Code']))# Record identifier
                f.write(get_table_600(row))

            #Block 615
            if index == temp.index[-1]:
                f.write('\n')
                i=i+1
                
                f.write(get_detailed_record('615',row['ID Number'],row['City of issue'],row['Latin Name'],row['ZIP Code']))
                f.write(get_table_615((np.floor(temp['CreditLimit'])).sum(),(np.floor(temp['CurrentBalance'])).sum(),temp['PastDueBalance'].sum(),temp['age'].max()))
    
    


            
        i=i+1
        f.write(''.join('\n999'+str(i).zfill(10)))
        
    m = open("ALLM_COMM_20220440.txt", "r")
    txtcontent = m.read()
    return dict(content=txtcontent, filename=Fname)


if __name__ == '__main__':
    app.run_server(debug=True)
