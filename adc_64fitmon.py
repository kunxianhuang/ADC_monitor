# Run this app with `python3 adc_fitmon.py` and
# visit http://127.0.0.1:8050/ in your web browser locally

import os,sys
from datetime import datetime
import numpy as np
import dash

from dash import dcc
from dash import html
from dash.dependencies import Input, Output
import plotly.express as px
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import pandas as pd
import multiprocessing
import signal
#import read_ads79XX
from read_ads79XX import loop_infinite_64measurements
from gau_fit import gau_fit,gauss_fn



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
    html.H1("Fiber detector monitoring with 64 channels",style={'textAlign': 'center'}),

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
    
    html.Div(className='row', children=[
        html.Div(children=[
            dcc.Graph(id='live-update-fitting-graph')
            ], style={'display': 'inline-block','width':'48%'}),
        html.Div(className='column', children=[
            html.Div(children=[
                dcc.Graph(id='live-update-xaxis-fitting-graph')
                ], style={'display': 'inline-block'}),
            html.Div(children=[
                dcc.Graph(id='live-update-yaxis-fitting-graph')
                ], style={'display': 'inline-block'}),
        ], style={'width':'45%'})
    ]),
    html.Div(id='live-update-gaussian-fit-text'),
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

        p = multiprocessing.Process(target=loop_infinite_64measurements,args=(filename,))
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
@app.callback([Output('live-update-fitting-graph','figure'),
               Output('live-update-xaxis-fitting-graph','figure'),
               Output('live-update-yaxis-fitting-graph','figure'),
               Output('live-update-gaussian-fit-text','children')],
              Input('interval-component', 'n_intervals'))
def update_graph_live(n_inter):
    x_label = ["CH0","CH1","CH2","CH3","CH4","CH5","CH6","CH7","CH8","CH9","CH10","CH11","CH12","CH13","CH14","CH15",
               "CH16","CH17","CH18","CH19","CH20","CH21","CH22","CH23","CH24","CH25","CH26","CH27","CH28","CH29","CH30","CH31"]
    y_label = ["CH32","CH33","CH34","CH35","CH36","CH37","CH38","CH39","CH40","CH41","CH42","CH43","CH44","CH45","CH46","CH47",
               "CH48","CH49","CH50","CH51","CH52","CH53","CH54","CH55","CH56","CH57","CH58","CH59","CH60","CH61","CH62","CH63"]
    # reading voltage array and drawing a plot 
    with open('temp/voltage64tmp.npy', 'rb') as fv:
        voltage_array = np.load(fv)
    
    with open('temp/voltage64pedestal.npy', 'rb') as fp:
        pedestal_array = np.load(fp)
    
    voltage_chs = np.mean(voltage_array,axis=1)
    axis_adc_num = 32
    # x-axis ADC (ch0-31)
    voltage_xaxis_chs = voltage_chs[:axis_adc_num]
    pedestal_xaxis = pedestal_array[:axis_adc_num]
    
    # y-axis ADC (ch32-63)
    voltage_yaxis_chs = voltage_chs[axis_adc_num:]
    pedestal_yaxis = pedestal_array[axis_adc_num:]
    
    
    # Initialize the 2x2 grid layout with custom dimension for profile plots and heatmap
    fig_heatprofile = make_subplots(
        rows=2,
        cols=2,
        row_heights=[0.3, 0.7],  # Top row gets 30% height, bottom row gets 70%                                                                            
        column_widths=[0.7, 0.3],  # Left col gets 70% width, right col gets 30%                                                                           
        shared_xaxes=True,  # Binds top column chart and central heatmap X-axis                                                                            
        shared_yaxes=True,  # Binds right bar chart and central heatmap Y-axis                                                                             
        horizontal_spacing=0.03,
        vertical_spacing=0.03,)   

    

    fiber_interval = 2.4 # scintillator fiber diameter 
    lower_ = -1.0*axis_adc_num/2
    higher_ = 1.0*axis_adc_num/2
    x_array = np.linspace(lower_,higher_,axis_adc_num)
    x_array = fiber_interval*x_array

    mu_x,sigma_x,A_x,fit_xarray = gau_fit(x_array,voltage_xaxis_chs,pedestal_xaxis)
    vol_xaxis_substract = np.subtract(voltage_xaxis_chs,pedestal_xaxis)

    
    x_line_array = np.linspace(lower_*fiber_interval,higher_*fiber_interval,1000)
    fitx_line_array = gauss_fn(x_line_array,mu_x,sigma_x,A_x)

    fig_xaxis_adcposition = go.Bar(x=x_array,y=vol_xaxis_substract,marker_color="#2b5c8f",name="X-axis Voltage")
    
    fig_xaxis_fitposition = go.Scatter(x=x_line_array,y=fitx_line_array,mode='lines',marker_size=20,name="X-axis fitted Gaussian")
    fig_fit_x = go.Figure(data=[fig_xaxis_adcposition,fig_xaxis_fitposition])


    fig_fit_x.update_layout(title_text='X-axis gaussian fitting',yaxis_range=[0.0,5.1],yaxis_title="Voltage (V)")
    fig_heatprofile.add_trace(fig_xaxis_adcposition,row=1,col=1)
    
    y_array = x_array
    mu_y,sigma_y,A_y,fit_yarray = gau_fit(y_array,voltage_yaxis_chs,pedestal_yaxis)
    vol_yaxis_substract = np.subtract(voltage_yaxis_chs,pedestal_yaxis)
    
    y_line_array = np.linspace(lower_*fiber_interval,higher_*fiber_interval,1000)
    fity_line_array = gauss_fn(y_line_array,mu_y,sigma_y,A_y)

    fig_yaxis_adcposition = go.Bar(x=vol_yaxis_substract,y=y_array,orientation="h",marker_color="#d41dda",name="Y-axis Voltage") # this bar chart is for heatmap
    fig_yaxis_adcpositionforcomp = go.Bar(x=y_array,y=vol_yaxis_substract,marker_color="#d41dda",name="Y-axis Voltage 2") # this bar chart is for the comparison with gaussian fitting
    
    
    fig_yaxis_fitposition = go.Scatter(x=y_line_array,y=fity_line_array,orientation="h",mode='lines',marker_size=20,name="Y-axis fitted Gaussian")
    fig_fit_y = go.Figure(data=[fig_yaxis_adcpositionforcomp,fig_yaxis_fitposition])
    fig_fit_y.update_layout(title_text='Y-axis gaussian fitting',yaxis_range=[0.0,5.1],yaxis_title="Voltage (V)")


    fig_heatprofile.add_trace(fig_yaxis_adcposition,row=2,col=2)

    
    # heatmap of x-y cross voltage (we use outer product here)
    hmvoltage = np.outer(voltage_yaxis_chs,voltage_xaxis_chs)
    hmpedestal = np.outer(pedestal_yaxis,pedestal_xaxis)

    hmvalue = np.subtract(hmvoltage,hmpedestal)
    
    fig_heatmap = go.Heatmap(x=x_label,y=y_label,z=hmvalue,colorscale="Viridis",
                             colorbar=dict(
                                title="Value",
                                thickness=15,
                                x=1.2,  # Pushes the heatmap colorbar out past the right bar chart
                                ),
                                showlegend=False)   
    fig_heatprofile.add_trace(fig_heatmap,row=2,col=1)
    
    # 7. Finalize layout modifications
    fig_heatprofile.update_layout(
        title=dict(text="Proton beam live-monitoring", x=0.5),
        height=600,
        width=900,
        barmode="group",
        template="plotly_white",
    )

    # Ensure the shared axis formatting remains aligned properly  
    fig_heatprofile.update_xaxes(row=1, col=1, showticklabels=False)  # Hide top X labels to avoid duplication
    fig_heatprofile.update_yaxes(row=2, col=2, side="right")  # Put right-most Y-axis text on the outside edge
    

    fit_span = html.Span('Beam property: Mean ({:.2f},{:.2f}) mm, Sigma ({:.2f},{:.2f}) mm'.format(mu_x,mu_y,sigma_x,sigma_y))
    
    
    return fig_heatprofile,fig_fit_x,fig_fit_y,fit_span





if __name__ == '__main__':
    #app.run_server(debug=True)
    app.run_server(host='0.0.0.0',debug=True)
