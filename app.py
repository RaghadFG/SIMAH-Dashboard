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

    result = df.dtypes

    #print(result)
    error_data = {
    "AccountNumber": [None],
    "Error": [None]
    }

    #load data into a DataFrame object:
    global erorr_df
    erorr_df = pd.DataFrame(error_data)
    global Flag 
    Flag = False
    for i,row in df.iterrows():
        if (row['LastAmountPaid'] == 0) and (row['LastPaymentDate']!=''):
            Flag=True
            erorr_df.at[i,'AccountNumber'] = row['AccountNumber']
            if erorr_df.at[i,'Error'] == None or (str(erorr_df.at[i,'Error'])=='nan'):
                erorr_df.at[i,'Error'] = 'Error:  LastAmountPaid = 0 while valid LastPaymentDate is provided'
                print(type(erorr_df.at[i,'Error']))
            else:
                erorr_df.at[i,'Error'] = 'Error:  LastAmountPaid = 0 while valid LastPaymentDate is provided'+' | '+str(erorr_df.at[i,'Error'])

        if (row['LastAmountPaid'] != 0) and (row['LastPaymentDate']==''):
            Flag=True
            erorr_df.at[i,'AccountNumber'] = row['AccountNumber']
            if erorr_df.at[i,'Error'] == None or (str(erorr_df.at[i,'Error'])=='nan'):
                erorr_df.at[i,'Error'] = 'Error: LastPaymentDate is not provided while there is amount paid'
                print(type(erorr_df.at[i,'Error']))
            else:
                erorr_df.at[i,'Error'] = 'Error: LastPaymentDate is not provided while there is amount paid'+' | '+str(erorr_df.at[i,'Error'])


        
        if row['PastDueBalance']>row['CurrentBalance']:
            Flag=True
            erorr_df.at[i,'AccountNumber'] = row['AccountNumber']
            if erorr_df.at[i,'Error'] == None or (str(erorr_df.at[i,'Error'])=='nan'):
                erorr_df.at[i,'Error'] = 'Error:  PastDueBalance > OutStanding'
                print(type(erorr_df.at[i,'Error']))
            else:
                erorr_df.at[i,'Error'] = 'Error:  PastDueBalance > OutStanding'+' | '+str(erorr_df.at[i,'Error'])

        if  (row['PaymentStatus'] == 1) and (row['PastDueBalance']<= 0):
            Flag=True
            erorr_df.at[i,'AccountNumber'] = row['AccountNumber']
            if erorr_df.at[i,'Error'] == None or (str(erorr_df.at[i,'Error'])=='nan'):
                erorr_df.at[i,'Error'] = 'Error:  PaymentStatus is 1 while PastDueBalance is not > 0'
                print(type(erorr_df.at[i,'Error']))
            else:
                erorr_df.at[i,'Error'] = 'Error:  PaymentStatus is 1 while PastDueBalance is not > 0'+" | "+str(erorr_df.at[i,'Error'])        
    if Flag:
        return html.Div([
        
        html.H5('Ops fix the errors then try uploading the file again'),
        html.H6('Error Table'),
    

        dash_table.DataTable(
            data=erorr_df.to_dict('records'),
            columns=[{'name': i, 'id': i} for i in erorr_df.columns]
        ),

        html.Hr(),  # horizontal line

        # # For debugging, display the raw contents provided by the web browser
        # html.Div('Raw Content'),
        # html.Pre(contents[0:200] + '...', style={
        #     'whiteSpace': 'pre-wrap',
        #     'wordBreak': 'break-all'
        # })
            ])



        # if ( df['LastAmountPaid'] == 0).any() & (df['LastPaymentDate'] !='').any():
        #             return html.Div([
        #             'Error: LastAmountPaid = 0 while valid LastPaymentDate is provided! Please try uploading the file again'
        #                 ])

    
    # if ( df['LastAmountPaid'] != 0).any() & (df['LastPaymentDate'].isna()).any():
    #             return html.Div([
    #             'Error: LastPaymentDate is not provided while there is an amount paid! Please try uploading the file again'
    #                 ])
    
    # if (df['PastDueBalance']>df['CurrentBalance']).any():
    #             return html.Div([
    #             'Error: PastDueBalance > OutStanding, Please try uploading the file again'
    #                 ])
    
    # if ( df['PaymentStatus'] == 1).any() & (df['PastDueBalance']<= 0).any():
    #             return html.Div([
    #             'Error: PaymentStatus is 1 while PastDueBalance is not > 0, Please try uploading the file again'
    #                 ])


    return html.Div([
       #html.H5(filename),
       #html.H6(datetime.datetime.fromtimestamp(date)),

        dash_table.DataTable(
            data=df.to_dict('records'),
            columns=[{'name': i, 'id': i} for i in df.columns]
        ),

        html.Hr(),  # horizontal line

        # # For debugging, display the raw contents provided by the web browser
        # html.Div('Raw Content'),
        # html.Pre(contents[0:200] + '...', style={
        #     'whiteSpace': 'pre-wrap',
        #     'wordBreak': 'break-all'
        # })
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
    if Flag:
        return dcc.send_data_frame(erorr_df.to_csv, "Error-table.csv")

    return dict(content='not yet', filename=Fname)


if __name__ == '__main__':
    app.run_server(debug=True)

