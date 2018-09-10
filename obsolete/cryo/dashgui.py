
import plotly.graph_objs as go
import dash
import dash_core_components as dcc
import dash_html_components as html
import plotly
from dash.dependencies import Input, Output, Event
import plotly.plotly as py
import numpy as np
import plotly.tools as tls
import plotly.graph_objs as go
import mce_data
import os
import matplotlib.pyplot as plt
import sys
from subprocess import Popen, PIPE
import datetime
import subprocess
from shutil import copy2
import time

app = dash.Dash()

#specifying the color scheme for the whole page
colors = {
        'background':'#111111',
        'text':'#7FDBFF'
        }

# make sure that the credentials file has stream id tokens already set

#getting stream id from id list
stream_ids = tls.get_credentials_file()['stream_ids']
stream_id=stream_ids[0]

# making an instance of a stream
stream_1 = dict(token=stream_id, maxpoints=1000)

#initializing the trace and embedding 1 stream id per trace
trace1 = go.Scatter(
	x=[],
	y=[],
	# can optionally set 'mode = "lines+markers",' here
	stream=stream_1
                       )
#initializing the data cube for plotting
data = go.Data([trace1])

  # importing a datafile from the MCE /data/cryo file
f = mce_data.MCEFile('/data/cryo/testfile2')
d = f.Read(row_col=True, unfilter='DC').data
T = range(0,d.shape[2])
data2 = (d[0,0])
print(d.shape)

#adding in a title and aligning it to center
app.layout = html.Div(style={'backgroundColor': colors['background']},children=[

    html.H1(
            children='MCE Control Window',
            style={
                    'textAlign':'center',
                    'color':colors['text']
                    }
    ),

    # adding a subtitle    
    html.Div(children='A web interface for the control of the TIME instrument and other instrumentation', style={
             'textAlign': 'center',
             'color': colors['text']
             }
    ),

    #label to input the number of frames    
    html.Label('Number of Frames',style={
             'textAlign': 'center',
             'color': colors['text']
             }),
    dcc.Input(id ='frames',value='1000',type='text'),
        html.Div(id='output-frames'),

@app.callback(
        dash.dependencies.Output('output-frames','children'),
        [dash.dependencies.Input('frames','value')])
def callback(value):
        return numframe = .format(value)

    #label for different readout cards you want to collect data for    
    html.Label('Readout Cards', style={
        'textAlign': 'center',
        'color': colors['text']
    }),
    
    dcc.Checklist(
        options=[
            {'label': 'RC1','value':'1'},
            {'label': 'RC2','value':'2'},
            {'label': 'RC3','value':'3'},
            {'label': 'RC4','value':'4'},
            {'label': 'RCA','value':'a'}
            ],
        values = ['1','2','3','4','a']
        ),

    dcc.Graph(
            id = 'MCE Live Raw Data',
            figure={
                    'data':[data
                    ],
                    'layout':go.Layout(title='MCE Run Acquisiton #',
                                       xaxis={'title':'UTC Time'},
                                       yaxis={'title':'Raw Counts'}
                                       )
            }),
        
  
   dcc.Graph(
         id = 'MCE Static Raw Data',
         figure={
             'data':[
                 go.Scatter(
                     x = [T],
                     y = [data2]
                     )
             ],
             'layout':go.Layout(title = 'MCE Run Testfile2',
                                xaxis={'title':'Time'},
                                yaxis={'title':'Random Data'}
                               )
                })
        
# initializing a stream link object which updates the chart in plotly

])

        
if __name__=='__main__':
        app.run_server(debug=True)

     
