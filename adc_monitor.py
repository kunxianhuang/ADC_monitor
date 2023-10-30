# Run this app with `python3 adc_monitor.py` and
# visit http://127.0.0.1:8050/ in your web browser locally

import os,sys
from datetime import datetime
import numpy as np
import dash
#import dash_core_components as dcc
#import dash_html_components as html
from dash import dcc
from dash import html
from dash.dependencies import Input, Output
import plotly.express as px
import plotly.graph_objects as go
import pandas as pd
import multiprocessing
import signal
#import read_ads79XX
#from read_ads79XX import loop_test

from test_example import test_loop
from test_example.test_loop import loop_test


external_stylesheets = ['https://codepen.io/chriddyp/pen/bWLwgP.css']

app = dash.Dash(__name__, external_stylesheets=external_stylesheets)

prol = []


styles = {
        'pre': {
                    'border': 'thin lightgrey solid',
                    'overflowX': 'scroll',
                }
}

blue_button_style = {'background-color': '#00FFFF',
                      'color': 'black',
                      'width': '340px',
                      'height': '82px',
                      'font-size': '18px',
                      }


yellow_button_style = {'background-color': 'LemonChiffon',
                      'color': 'grey',
                      'width': '340px',
                      'height': '82px',
                      'font-size': '18px',
                      }

white_button_style = {'background-color': 'white',
                      'color': 'black',
                      'width': '340px',
                      'height': '82px',
                      'font-size': '18px',
                      }

red_button_style = {'background-color': 'red',
                    'color': 'grey',
                    'width': '340px',
                      'height': '82px',
                      'font-size': '18px',
                    }


app.layout = html.Div(children=[
    html.H1("Fiber detector monitoring",style={'textAlign': 'center'}),

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
    ],style={'width':"800px", 'margin':'0','left':'50%'}),

    html.Div(id='live-update-adc-text'),
    html.Div(children=[
        dcc.Graph(id='live-update-adc-graph')
        ], style={'display': 'inline-block', 'width': '70%'}),

    dcc.Interval(
        id='interval-component',
        interval=1*500, # in milliseconds
        n_intervals=0)
        
])



@app.callback(
    [Output('start_ADC_button', 'style',allow_duplicate=True),
    Output('start_ADC_button', 'disabled',allow_duplicate=True),
    Output('file_name_output','children')],
    Input('start_ADC_button', 'n_clicks'),
    prevent_initial_call=True)
def PushStartADC(button_clicks):
    #print(button_clicks)
    if button_clicks:
        start_time = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = 'data/ADC_'+ start_time +'.txt'

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
        # disable EndADC button
        return blue_button_style, False
    else: 
        return red_button_style, True

@app.callback(Output('live-update-adc-text', 'children'),
        Input('interval-component', 'n_intervals'))
def update_time(n):
    with open('temp/time.txt', 'r') as ft:
        time_content = ft.readline()
        
    return html.Span('Last reading time {}'.format(time_content))

# Multiple components can update everytime interval gets fired.
@app.callback(Output('live-update-adc-graph', 'figure'),
              Input('interval-component', 'n_intervals'))
def update_graph_live(n_inter):
    x_label = ["CH0","CH1","CH2","CH3","CH4","CH5","CH6","CH7","CH8","CH9","CH10","CH11","CH12","CH13","CH14","CH15"]
    # reading voltage array and drawing a plot 
    with open('temp/voltagetmp.npy', 'rb') as fv:
        voltage_array = np.load(fv)
    
    voltage_chs = np.mean(voltage_array,axis=1)
    fig = go.Figure(data=[go.Bar(x=x_label, y=voltage_chs)])
    # Customize aspect
    fig.update_traces(marker_color='rgb(158,202,225)', marker_line_color='rgb(8,48,107)',
                  marker_line_width=1.5, opacity=0.6)
    fig.update_layout(title_text='ADC value live update',yaxis_range=[0.0,5.1],yaxis_title="Voltage (V)")
    #fig = px.bar(voltage_chs, labels={'index': 'Channel #', 'value':'Voltage (V)'})
    return fig




if __name__ == '__main__':
    #app.run_server(debug=True)
    app.run_server(host='0.0.0.0',debug=True)
