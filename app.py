import dash
import dash_design_kit as ddk
from dash import dcc
import dash_html_components as html
from dash.dependencies import Input, Output
import plotly.express as px
import base64
from datetime import datetime
import math
import io
import theme
import dash
from dash.dependencies import Input, Output, State
import plotly.graph_objs as go
import pandas as pd
import dash_table
app = dash.Dash(__name__)
server = app.server 


month=datetime.now().date().month  
Fname=str(month)+"th-month SIMAH Report.txt"

#

app.layout = ddk.App([
    ddk.Header([
        ddk.Logo(src=app.get_asset_url('logo.png')),
        ddk.Title('SIMAH Dashbord'),
    ]),
    html.Div([
    ddk.Card([
    ddk.Row(children=
    [html.Div([
        html.P('How to use:'),
        html.P('-'),
        html.P("Policies & Legal requirements:"),
        html.P('-'),

    ])]
    )
    ]),html.Div([
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

   
         html.Button("Download File", id="btn-download-txt"),
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
    


    try:
        if 'csv' in filename:
            # Assume that the user uploaded a CSV file
            df = pd.read_csv(
                io.StringIO(decoded.decode('utf-8')))

        elif 'xls' in filename:
            # Assume that the user uploaded an excel file
            df = pd.read_excel(io.BytesIO(decoded))
        

    except Exception as e:
        print(e)
        return html.Div([
            'There was an error processing this file.'
        ])

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


@app.callback(Output('output-data-upload', 'children'),
              Input('upload-data', 'contents'),
              State('upload-data', 'filename'),
              State('upload-data', 'last_modified'))
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

    #download txt file ... not yet
    return dict(content='not yet', filename=Fname)


if __name__ == '__main__':
    app.run_server(debug=True)



##