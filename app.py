import dash
import dash_design_kit as ddk
from dash import dcc
import dash_html_components as html
from dash.dependencies import Input, Output
import plotly.express as px
import base64
from datetime import datetime
import io
import theme
import dash
from dash.dependencies import Input, Output, State



import pandas as pd





app = dash.Dash(__name__)
server = app.server 


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
    ]),
    dcc.Upload(
        id='upload-data',
        children=html.Div([
            'Drag and Drop or ',
            html.A('Select File')
        ]),style={
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
   
         html.Button("Download Text", id="btn-download-txt"),
         dcc.Download(id="download-text")
    
])
])
month=datetime.now().date().month  
Fname=str(month)+"th-month SIMAH Report.txt"
@app.callback(
    Output("download-text", "data"),
    Input("btn-download-txt", "n_clicks"),
    prevent_initial_call=True,
)
def func(n_clicks):
    return dict(content="not yet", filename=Fname)



####

if __name__ == '__main__':
    app.run_server(debug=True)

