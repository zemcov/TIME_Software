#!/usr/bin/python2.7
# -*- coding: utf-8 -*-
'''
    Basic GUI Layout:

    UTC/Location | Title | Blank?
    ------------------------------
    Input Boxes | MCE Graphs | MCE Graphs
    ------------------------------
    Start/Stop | Heatmap | Heatmap
'''
import dash
from dash.dependencies import Input, Output, State
import dash_core_components as dcc
import dash_html_components as html
import datetime
import plotly.plotly as py
import plotly.graph_objs as go
import astropy
import json
from subprocess import Popen, PIPE
import subprocess
from shutil import copy2
#import mce_data
#import matplotlib.pyplot as plt

print(dcc.__version__)

print('Hello')

app = dash.Dash()

app.css.append_css({"external_url": "https://codepen.io/chriddyp/pen/bWLwgP.css"})

app.config.supress_callback_exceptions=True

app.layout = html.Div([
    dcc.Location(id='url', refresh=False),
    html.Div(id='page-content'),
    html.Div([
        html.Div(id='storedParameters'),
        html.Div(id='validParameters'),
    ], style={'display': 'none'}),
])

index_page = html.Div([ #index page -> input parameters
    html.Div([ #Input Parameters Div
        html.H4(children='Input Parameters'),
        html.Div([
            html.H6(children='Filename'),
            dcc.Input(
                id='filename',
                placeholder='Enter filename...',
                type='text',
                value='',
            ),
            html.H6(children='Datamode'),
            dcc.Dropdown(
                id='datamode',
                options=[
                    {'label': 'Select an Option', 'value': ''},
                    {'label': 'Error', 'value': 0},
                    {'label': 'Raw', 'value': 12},
                    {'label': 'Low Pass Filtered', 'value': 2},
                    {'label': 'Mixed Mode', 'value': 10},
                    {'label': 'SQ1 Feedback', 'value': 1}
                ],
                value=''
            ),
            html.H6(children='Readout Card'),
            dcc.Dropdown(
                id='readoutcard',
                options=[
                    {'label': 'Select an Option', 'value': ''},
                    {'label': 'RC 1', 'value': 1},
                    {'label': 'RC 2', 'value': 2},
                    {'label': 'RC 3', 'value': 3},
                    {'label': 'RC 4', 'value': 4},
                    {'label': 'RC All', 'value': 5}
                ],
                value=''
            ),
            html.H6(children='Frame Number'),
            dcc.Input(
                id='framenumber',
                placeholder='Enter frame number...',
                type='numeric',
                value=0
            ),
            html.H6(children='Submit Parameters to MCE'),
            html.Button('Submit', id='parameterSubmit'),
            html.Div(id='parameterCheck'),
            ], style={}, id='inputParameters'),
        ]),
], style={'textAlign': 'center',
          'margin': 'auto',
          'display': 'grid',
          'gridTemplateColumns': 'auto auto auto',
          'gridTemplateRows': 'auto auto auto'})

data_page = html.Div([ #Main page of gui
    html.Div([ #Title Div
        html.H1('TIME MCE DATA',
                style={'paddingLeft': 100})
        ], style={'gridColumn': '2 / span 1',
              'gridRow': '1 / span 1'
              }
        ),

    html.Div([ #UTC/Location Div
        html.H4('UTC/Location'),
        html.P(children='Our UTC/Location will go here over to the left.',
               style={'border': '3px solid black'}
               )
        ], style={'gridColumn': '1 / span 1',
              'gridRow': '1 / span 1'}
        ),

    html.Div([ #entered parameters
        html.H4('Entered Parameters'),
        html.Button('See Parameters', id='seeParameters'),
        html.Div(children='No parameters entered!', id='enteredParameters'),
        ], style={'gridColumn': '1 / span 1',
              'gridRow': '2 / span 1'}),

    html.Div([ #Start/Stop Buttons Div
        html.H4(children='Pause/Emergency Stop Buttons'),
        html.Button('Pause/Resume', id='pauseData'),
        html.Button('Emergency Stop', id='eStop'),
        html.Div(children='MCE is running', id='stateMCE'),
        html.Div(id='returnLink')
        ], style={'gridColumn': '1 / span 1',
              'gridRow': '3 / span 1'}
        ),

    html.Div([ #MCE Graph Div
        html.H4(children='MCE Graphs'),
        ], style={'gridColumn': '2 / span 2',
              'gridRow': '2 / span 1'}
        ),

    html.Div([ #Heatmap Div
        html.H4(children='Heatmap'),
        html.Div(id='Heatmap'),
        dcc.Interval(
            id='heatInterval',
            interval=1*1000,
            n_intervals=0
        )
        ], style={'gridColumn': '2 / span 2',
              'gridRow': '3 / span 1'}
        ),

    html.Div([ #K-Mirror Div
        html.H4(children='K-Mirror Data'),
        html.P('''
               Data having to do with the K-Mirror (duh).
               '''),
        ], style={'gridColumn': '3 / span 1',
          'gridRow': '1 / span 1'}
        ),

    html.Div([ #holds hidden Divs
            html.Div(children='Off', id='mceState'), #holds state of MCE
            html.Div(children='Yes', id='parametersSubmitted'), #holds state of data submission
            html.Div(id='displayedParameters'),
        ], style={'display': 'none'}
        ),

], style={'textAlign': 'center',
          'margin': 'auto',
          'display': 'grid',
          'gridTemplateColumns': 'auto auto auto',
          'gridTemplateRows': 'auto auto auto'})

'''
@app.callback(
    Output('parametersSubmitted', 'children'),
    [Input('parameterSubmit', 'n_clicks')],
    [State('filename', 'value'),
     State('datamode', 'value'),
     State('readoutcard', 'value'),
     State('framenumber', 'value')])
def checkParameters(submit, filename, datamode, readoutcard, framenumber):
    if filename == '' or datamode == '' or readoutcard == '' or framenumber == 0:
        parameters = 'No'
    else:
        parameters = 'Yes'
    return json.dumps(parameters)
'''

def init():
    heatmapArray = []


def startDataCollection(parameters):
    filename = parameters[0]
    datamode = parameters[1]
    readoutcard = str(parameters[2])
    framenumber = parameters[3]
    changedatamode = ["mce_cmd -x wb rc%s data_mode %s" % (readoutcard,datamode)]
    a = subprocess.Popen(changedatamode, shell=True)
    a.communicate()

    subprocess.call(["mkfifo", "/data/cryo/current_data/temp"])

    run  = ["mce_run temp %s %s && cat /data/cryo/current_data/temp >> /data/cryo/current_data/%s" %(framenumber,readoutcard,filename)]
    b = subprocess.Popen(run, shell=True)
    b.communicate()

    init()


@app.callback(
    Output('storedParameters', 'children'),
    [Input('parameterSubmit', 'n_clicks')],
    [State('filename', 'value'),
     State('datamode', 'value'),
     State('readoutcard', 'value'),
     State('framenumber', 'value')])
def storeParameters(n_clicks, filename, datamode, readoutcard, framenumber):
    if readoutcard == 5:
        new_readoutcard = 'All'
    else:
        new_readoutcard = readoutcard
    parameters=[filename, datamode, new_readoutcard, framenumber]
    return json.dumps(parameters)


@app.callback(
    Output('validParameters', 'children'),
    [Input('storedParameters', 'children')])
def validateParameters(json_parameters):
    parameters = json.loads(json_parameters)
    print(parameters)
    for parameter in parameters:
        if parameter == '' or parameter == '0':
            validation = 'Invalid'
            return json.dumps(validation)
    validation = 'Valid'
    return json.dumps(validation)


@app.callback(
    Output('parameterCheck', 'children'),
    [Input('validParameters', 'children'),
     Input('parameterSubmit', 'n_clicks')])
def parameterError(json_validparameters, clicks):
    validparameters = json.loads(json_validparameters)
    if validparameters == 'Invalid':
        return '**One or more parameters not entered!!**'


@app.callback(
    Output('url', 'pathname'),
    [Input('validParameters', 'children')])
def toggleDataCollection(json_validparameters):
    validparameters = json.loads(json_validparameters)
    if validparameters == 'Valid':
        startDataCollection()
        return '/data'
    else:
        return ''


@app.callback(
    Output('enteredParameters', 'children'),
    [Input('seeParameters', 'n_clicks')],
    [State('storedParameters', 'children')])
def showParameters(n_clicks, json_parameters):
    parameters = json.loads(json_parameters)
    return '''
    *Filename: {}
    *Datamode: {}
    *Readout Card: {}
    *Number of Frames: {}
    '''.format(parameters[0], parameters[1], parameters[2], parameters[3])


@app.callback(
    Output('stateMCE', 'children'),
    [Input('pauseData', 'n_clicks')])
def pauseDataCollection(pauseData):
    if pauseData % 2 == 0:
        return 'MCE is running'
    else:
        return 'MCE is not running'


@app.callback(
    Output('returnLink', 'children'),
    [Input('eStop', 'n_clicks')])
def eStopDataCollection(clicks):
    #eStopDataCollection()
    return dcc.Link('Enter new parameters', href='/index')


'''
@app.callback(
    Output('enteredParameters', 'children'),
    [Input('parametersSubmit', 'n_clicks')],
    [State('filename', 'value'),
     State('datamode', 'value'),
     State('readoutcard', 'value'),
     State('framenumber', 'value'),
     State('parametersSubmitted', 'children')])
def showParameters(submit, filename, datamode, readoutcard, framenumber, parametersSubmitted):
    if filename == '' or datamode == '' or readoutcard == '' or framenumber == 0:
        return ''
    return u
    *filename: {} n
    *datamode: {} n
    *readoutcard: {} n
    *framenumber: {}
    .format(filename, datamode, readoutcard, framenumber)
'''


@app.callback(
    Output('Heatmap', 'children'),
    [Input('heatInterval', 'n_intervals')],
    [State('storeParameters', 'children')])
def updateHeatmap(n_intervals, json_parameters):
    parameters = json.loads(json_parameters)
    if parameters[2] == 'All':
        print('All Readout Cards')
        #return takedataAll.py
    else:
        print('Readout Card {}'.format(parameters[2]))
        #return takedata.py



@app.callback(
    Output('page-content', 'children'),
    [Input('url', 'pathname')])
def display_page(pathname):
    if pathname == '/data':
        return data_page
    else:
        return index_page


if __name__ == '__main__':
	app.run_server(debug=True)
