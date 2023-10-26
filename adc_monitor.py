# Run this app with `python3 adc_monitor.py` and
# visit http://127.0.0.1:8050/ in your web browser locally

import dash
#import dash_core_components as dcc
#import dash_html_components as html
from dash import dcc
from dash import html
from dash.dependencies import Input, Output
import plotly.express as px
import pandas as pd
import read_ads79XX

external_stylesheets = ['https://codepen.io/chriddyp/pen/bWLwgP.css']

app = dash.Dash(__name__, external_stylesheets=external_stylesheets)


styles = {
        'pre': {
                    'border': 'thin lightgrey solid',
                    'overflowX': 'scroll'
                }
}


app.layout = html.Div([
    html.H1("Fiber detector monitoring", style={'textAlign': 'center'}),

    html.Div(className='row', children=[
        # Button for start ADS79XX reading
        html.Button(
            id='start_ADC_button', # id for corresponding call back
            disabled=False, # initially functionable
            children='Start ADC Reading'
        ),
        # Button for end ADS79XX reading
        html.Button(
            id='end_ADC_button', # id for corresponding call back
            disabled=True, # initially function disabled
            children='End ADC Reading'
        ),
        html.Output(
            id='file_name_output', # id for corresponding call back
            children='File to save' # Saving file name
        )
    ])




])






if __name__ == '__main__':
    app.run_server(debug=True)
