# Run this app with `python3 adc_monitor.py` and
# visit http://127.0.0.1:8050/ in your web browser locally

import os,sys
from datetime import datetime
import dash
#import dash_core_components as dcc
#import dash_html_components as html
from dash import dcc
from dash import html
from dash.dependencies import Input, Output
import plotly.express as px
import pandas as pd
import multiprocessing
import signal
#import read_ads79XX
#from read_ads79XX import loop_test
import test_loop
from test_loop import loop_test


external_stylesheets = ['https://codepen.io/chriddyp/pen/bWLwgP.css']

app = dash.Dash(__name__, external_stylesheets=external_stylesheets)

prol = []


styles = {
        'pre': {
                    'border': 'thin lightgrey solid',
                    'overflowX': 'scroll'
                }
}

blue_button_style = {'background-color': '#00FFFF',
                      'color': 'black',
                      'width': '340px',
                      'height': '82px',
                      'font-size': '15px'
                      }


yellow_button_style = {'background-color': 'LemonChiffon',
                      'color': 'grey',
                      'width': '340px',
                      'height': '82px',
                      'font-size': '15px'
                      }

white_button_style = {'background-color': 'white',
                      'color': 'black',
                      'width': '340px',
                      'height': '82px',
                      'font-size': '15px'
                      }

red_button_style = {'background-color': 'red',
                    'color': 'grey',
                    'width': '340px',
                      'height': '82px',
                      'font-size': '15px'
                    }


app.layout = html.Div([
    html.H1("Fiber detector monitoring", style={'textAlign': 'center'}),

    html.Div(className='row', children=[
        # Button for start ADS79XX reading
        html.Button(
            id='start_ADC_button', # id for corresponding call back
            n_clicks=0,
            style = blue_button_style,
            children='Start ADC Reading'
        ),
        # Button for end ADS79XX reading
        html.Button(
            id='end_ADC_button', # id for corresponding call back
            disabled=True, # initially function disabled
            n_clicks=0,
            style = white_button_style,
            children='End ADC Reading'
        ),
        html.Div(children= 'Save file to:'),
        html.Output(
            id='file_name_output', # id for corresponding call back
            children='File to save' # Saving file name
        )
    ],style={'width':"800px", 'margin':'0','left':'50%'})



])



@app.callback(
    [Output('start_ADC_button', 'style',allow_duplicate=True),
    Output('start_ADC_button', 'disabled',allow_duplicate=True),
    Output('file_name_output','children')],
    Input('start_ADC_button', 'n_clicks'),
    prevent_initial_call=True)
def PushStartADC(button_clicks):
    print(button_clicks)
    if button_clicks:
        start_time = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = 'ADC_'+ start_time +'.txt'

        p = multiprocessing.Process(target=loop_test,args=(filename,))
        p.start()
        prol.append(p)
        # disable StartADC button
        return red_button_style, True, filename

    else :
        return yellow_button_style, False


@app.callback(
    [Output('end_ADC_button', 'style',allow_duplicate=True),
    Output('end_ADC_button', 'disabled',allow_duplicate=True)],
    Input('start_ADC_button', 'n_clicks'),
    prevent_initial_call=True)
def EnableEndADC(button_clicks):
    if button_clicks:
        # enable EndADC button
        return blue_button_style,False 
    else :  
        return yellow_button_style, True


@app.callback(
    [Output('end_ADC_button', 'style',allow_duplicate=True),
    Output('end_ADC_button', 'disabled',allow_duplicate=True)],
    Input('end_ADC_button', 'n_clicks'),
    prevent_initial_call=True)
def PushEndADC(button_clicks):
    if button_clicks:
        for p in prol:
            os.kill(p.pid,signal.SIGINT)
            p.join()
            print(p.exitcode)
            prol.remove(p)
        
        # disable EndADC button
        return yellow_button_style, True
    else: 
        return blue_button_style, False


@app.callback(
    [Output('start_ADC_button', 'style',allow_duplicate=True),
    Output('start_ADC_button', 'disabled',allow_duplicate=True)],
    Input('end_ADC_button', 'n_clicks'),
    prevent_initial_call=True)
def EnableStartADC(button_clicks):
    if button_clicks:
        # disable EndADc button
        return blue_button_style, False
    else: 
        return red_button_style, True






if __name__ == '__main__':
    app.run_server(debug=True)
