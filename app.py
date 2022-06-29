import dash
import dash_design_kit as ddk
from dash import dcc
import dash_html_components as html
from dash.dependencies import Input, Output
import plotly.express as px
import base64
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
from utils.preprocessing import get_preprocessing,check_uploded_columns,legal_type_mapping
from data.data import *
import dash_user_analytics
from dateutil import tz
#from datetime import *
from datetime import timezone
from dash.exceptions import PreventUpdate

app = dash.Dash(__name__)
server = app.server 

from_zone = tz.gettz('UTC')
to_zone = tz.gettz('Asia/Riyadh')

# month=datetime.now().date().month  
# Fname=str(month)+"th-month SIMAH Report.txt"

columnheaders =pd.read_excel('column header names.xlsx', engine='openpyxl')


def serve_layout():
    return ddk.App(theme=theme.theme,children=[

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
            'margin': '10px'},
        # Allow multiple files to be uploaded
        multiple=False
    ),
    html.Div(id='output-data-upload'),
    dcc.Store(id='Flag'),
    dcc.Store(id='error_df'),
    dcc.Store(id='df'),

   
    html.Button("Download SIMAH report", id="btn-download-txt", style={'margin-left':'9px'}),
    dcc.Download(id="download-text")
    
]),
   

])])

app.layout = serve_layout

#dash_user_analytics.DashUserAnalytics(app)


 
# @app.callback(
#     Output("table", "children"),
#     Output("Flag", "value"),
#     Output("error_df", "data"),
#     Output("df", "data"),
#     Input("run", "n_intervals"),
#     prevent_initial_call=True,    
# )



def parse_contents(contents, filename, date):

    content_type, content_string = contents.split(',')
    decoded = base64.b64decode(content_string)
    
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

    
    return df.to_dict('records')
  

@app.callback(Output('output-data-upload', 'children'),
              Output("Flag", "data"),
              Output("error_df", "data"),
              Output("df", "data"),
              Input('upload-data', 'contents'),
              State('upload-data', 'filename'),
              State('upload-data', 'last_modified'),
               prevent_initial_call=True,)

def update_output(contents, name, date):
    error_data = {
    "AccountNumber": [None],
    "Error": [None]
    }
    erorr_df = pd.DataFrame(error_data)
    Flag = False


    if contents is not None:
        children = parse_contents(contents,name, date)
        df = pd.DataFrame.from_dict(children)

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

             #check 5th rule
            if  (row['PaymentStatus'] == 'D') and (str(row['CloseDate'])== 'nan'):
                Flag=True
                erorr_df.at[i,'AccountNumber'] = row['AccountNumber']
                #1st error in AccountNumber
                if erorr_df.at[i,'Error'] == None or (str(erorr_df.at[i,'Error'])=='nan'):
                    erorr_df.at[i,'Error'] = 'Error: payment status = D, close date should not be empty'
                #more than one error in the same AccountNumber
                else:
                    erorr_df.at[i,'Error'] = 'Error: payment status = D, close date should not be empty'+" | "+str(erorr_df.at[i,'Error'])       
 

    # erorr_df=erorr_df.to_dict('rows')
        #the uploaded file has errors
        if Flag:
           # show the errors
            return html.Div([
            
            html.H5('Ops fix the errors then try uploading the file again'),
            html.H6('Error Table'),
        

            dash_table.DataTable(
                data=erorr_df.to_dict('records'),
                columns=[{'name': i, 'id': i} for i in erorr_df.columns]
            ),

            html.Hr(), 
                ]),Flag,erorr_df.to_dict('records'),df.to_dict('records')

        #show the uploaded file
        else:
    
            return html.Div([
                dash_table.DataTable(
                    data=df.to_dict('records'),
                    columns=[{'name': i, 'id': i} for i in df.columns]
                ),

                html.Hr(),  
            ]),Flag,erorr_df.to_dict('records'),df.to_dict('records')

@app.callback(
    Output("download-text", "data"),
    Input("btn-download-txt", "n_clicks"),
    State("Flag", "data"),
    State("error_df", "data"),
    State("df", "data"),
    prevent_initial_call=True,
)
def func(n_clicks,Flag,error_dff,dff):
    df=pd.DataFrame.from_dict(dff)
    error_df=pd.DataFrame.from_dict(error_dff)

    if df is None:
        print('df is none')
        raise PreventUpdate

    if n_clicks:
        if Flag:
            return dcc.send_data_frame(pd.DataFrame.from_dict(error_dff).to_csv, "Error-table.csv")


        clients_df=pd.read_excel('data/ClientDetails.xlsx', engine='openpyxl')

        ClientCode=pd.read_excel('data/ClientCodeLookUp.xlsx',  engine='openpyxl')

        first_merge=pd.merge(clients_df,ClientCode,on='Client Code')


        #Merge with uploaded file
        full_df=pd.merge(first_merge, df, on='AccountNumber')
        if(full_df.empty):
            clients = get_jira_data()
            #clients['ID Number'] =int(clients['ID Number'])
            full_df = pd.merge(clients, df, on='Client Code')
            clients = clients[clients['Client Code'].isin(df['Client Code'])]
            clients = clients.replace({"Legal Type": legal_type_mapping})
        else:
            full_df =full_df[full_df['AccountNumber'].isin(df['AccountNumber'])]
            #Unique clients 
            clients =full_df.drop_duplicates(subset=['Client Code'])
        full_df=get_preprocessing(full_df)

        
        name=datetime.datetime.now().strftime("%d%m%Y_%H%M%S")

        n=name+'.txt'
        #Start fill the text file
        with open(n,'w') as f:
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
            
        m = open(n, "r")
        txtcontent = m.read()
        return dict(content=txtcontent, filename=f"SIMAH {datetime.datetime.now(timezone.utc).astimezone(to_zone):%Y-%m-%d %H:%M:%S}")


@app.callback(
    Output("download-dataframe-xlsx", "data"),
    Input("btn_xlsx", "n_clicks"),
    prevent_initial_call=True,
)

def funcc(n_clicks):
    return dcc.send_data_frame(columnheaders.to_excel, "columnheaders.xlsx")


if __name__ == '__main__':
    app.run_server(host="0.0.0.0",port=8000,debug=True)
    #app.run_server(debug=True)
