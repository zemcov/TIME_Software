#!/usr/bin/python
# -*- coding: utf-8 -*-
'''
    Basic GUI Layout:

    UTC/Location | Title | K-Mirror | K-Mirror
    -------------------------------------------
    Show Inputs | G Options | Graphs | Graphs
    -------------------------------------------
    Start/Stop | H Options | Heatmap | Heatmap
'''
import dash
from dash.dependencies import Input, Output, State
import dash_core_components as dcc
import dash_html_components as html
import datetime
import plotly.plotly as py
import plotly.graph_objs as go
#import astropy
import json
from subprocess import Popen, PIPE
import subprocess
from shutil import copy2
#import mce_data
#import matplotlib.pyplot as plt
#import takedata
#import takedataall
import guiheatmap
import os
import time
import sys
sys.path.append('/data/cryo/current_data')

print(dcc.__version__)

print('Hello')

global runtakedata

app = dash.Dash()

app.css.append_css({"external_url": "https://codepen.io/chriddyp/pen/bWLwgP.css"})

app.config.supress_callback_exceptions=True

app.layout = html.Div([
    dcc.Location(id='url', refresh=False),
    html.Div(id='page-content'),
    html.Div([
        html.Div(id='storedParameters'),
        html.Div(id='validParameters'),
        html.Div(id='eStopData'),
        html.Div(id='graphy'),
        html.Div(id='graphx'),
        html.Div(id='graphchannel')
    ], style={'display': 'none'}),
])

index_page = html.Div([ #index page -> input parameters
    html.Div([ #Input Parameters Div
        html.H4(children='Input Parameters'),
        html.Div([
            html.H6(children='Observer'),
            dcc.Input(
                id='observer',
                placeholder='Enter your name...',
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
                    {'label': 'MCE 1 RC 1', 'value': 1},
                    {'label': 'MCE 1 RC 2', 'value': 2},
                    {'label': 'MCE 1 RC 3', 'value': 3},
                    {'label': 'MCE 1 RC 4', 'value': 4},
                    {'label': 'MCE 2 RC 1', 'value': 5},
                    {'label': 'MCE 2 RC 2', 'value': 6},
                    {'label': 'MCE 2 RC 3', 'value': 7},
                    {'label': 'MCE 2 RC 4', 'value': 8},
                    {'label': 'RC All', 'value': 9}
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
        html.H1('TIME MCE DATA')
                #style={'paddingLeft': 100})
        ], style={'gridColumn': '2 / span 2',
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

    html.Div([ #Graph Options Div
        html.H4(children='Change Graph'),
        html.Div([
            dcc.RadioItems(
                    id='mcegraph',
                    options=[
                        {'label': 'MCE 1', 'value': 1},
                        {'label': 'MCE 2', 'value': 2},
                    ],
                    value=1
                ),
            dcc.Dropdown(
                    id='rcgraph',
                    options=[
                        {'label': 'RC 1', 'value': 1},
                        {'label': 'RC 2', 'value': 2},
                        {'label': 'RC 3', 'value': 3},
                        {'label': 'RC 4', 'value': 4},
                    ],
                    value = 2
                ),
            dcc.Dropdown(
                    id='chgraph',
                    options=[
                        {'label': 'CH 1', 'value': 1},
                        {'label': 'CH 2', 'value': 2},
                        {'label': 'CH 3', 'value': 3},
                        {'label': 'CH 4', 'value': 4},
                        {'label': 'CH 5', 'value': 5},
                        {'label': 'CH 6', 'value': 6},
                        {'label': 'CH 7', 'value': 7},
                        {'label': 'CH 8', 'value': 8},
                    ],
                    value = 1
                ),
            ]),
        ], style={'gridColumn': '2 / span 1',
          'gridRow': '2 / span 1'}),

    html.Div([ #Heatmap Options Div
        html.H4('Change Heatmap'),
        html.Div([
            dcc.RadioItems(
                    id='mceheatmap',
                    options=[
                        {'label': 'MCE 1', 'value': 1},
                        {'label': 'MCE 2', 'value': 2},
                    ],
                    value=1
                ),
            dcc.Dropdown(
                    id='rcheatmap',
                    options=[
                        {'label': 'RC 1', 'value': 1},
                        {'label': 'RC 2', 'value': 2},
                        {'label': 'RC 3', 'value': 3},
                        {'label': 'RC 4', 'value': 4},
                    ],
                    value = 2
                ),
            dcc.Dropdown(
                    id='chheatmap',
                    options=[
                        {'label': 'CH 1', 'value': 1},
                        {'label': 'CH 2', 'value': 2},
                        {'label': 'CH 3', 'value': 3},
                        {'label': 'CH 4', 'value': 4},
                        {'label': 'CH 5', 'value': 5},
                        {'label': 'CH 6', 'value': 6},
                        {'label': 'CH 7', 'value': 7},
                        {'label': 'CH 8', 'value': 8},
                    ],
                    value = 1
                ),
            ]),
        #html.Div(id='heatmapCheck')
        ], style={'gridColumn': '2 / span 1',
          'gridRow': '3 / span 1'}),

    html.Div([ #MCE Graph Div
        html.H4(children='MCE Graphs'),
        dcc.Graph(id='mceGraph'),
        dcc.Interval(
            id='graphInterval',
            interval=2*1000,
            n_intervals=0
        )
        ], style={'gridColumn': '3 / span 2',
              'gridRow': '2 / span 1'}
        ),

    html.Div([ #Heatmap Div
        html.H4(children='MCE Heatmaps'),
        dcc.Graph(id='mceHeatmap'),
        dcc.Interval(
            id='heatInterval',
            interval=2*1000,
            n_intervals=0
        )
        ], style={'gridColumn': '3 / span 2',
              'gridRow': '3 / span 1'}
        ),

    html.Div([ #K-Mirror Div
        html.H4(children='K-Mirror Data'),
        html.P('''
               Data having to do with the K-Mirror (duh).
               '''),
        ], style={'gridColumn': '3 / span 2',
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
          'gridTemplateColumns': 'auto auto auto auto',
          'gridTemplateRows': 'auto auto auto'})

'''
@app.callback(
    Output('parametersSubmitted', 'children'),
    [Input('parameterSubmit', 'n_clicks')],
    [State('observer', 'value'),
     State('datamode', 'value'),
     State('readoutcard', 'value'),
     State('framenumber', 'value')])
def checkParameters(submit, observer, datamode, readoutcard, framenumber):
    if observer == '' or datamode == '' or readoutcard == '' or framenumber == 0:
        parameters = 'No'
    else:
        parameters = 'Yes'
    return json.dumps(parameters)
'''

def init():
    heatmapArray = []


def startDataCollection(parameters):
    #deletetempgraph = ['rm /TIME_Software/cryo/tempfiles/tempgraphdata.txt']
    #a = subprocess.Popen(deletetempgraph, shell=True)
    for i in range(2):
        tempfilename = 'tempfiles/tempgraphdata%s.txt' % (i)
        tempfile = os.path.exists(tempfilename)
        if tempfile:
            delete_file = ['rm ' + tempfilename]
            subprocess.Popen(delete_file,shell=True)

    observer = parameters[0]
    datamode = parameters[1]
    readoutcard = str(parameters[2])
    framenumber = parameters[3]
    changedatamode = ["mce_cmd -x wb rc%s data_mode %s" % (readoutcard, datamode)]
    b = subprocess.Popen(changedatamode, shell=True)
    #a.communicate()
    #subprocess.call(["mkfifo", "/data/cryo/current_data/temp"])
    run = ["mce_run temp %s %s --sequence=374" %(framenumber, readoutcard)]
    c = subprocess.Popen(run, shell=True)

    tempfile = open('tempfiles/tempchannel.txt', 'w')
    tempfile.write(str(1))
    tempfile.close()
    #b.communicate()
    #a.terminate()


    init()


def stopDataCollection(parameters):
    readoutcard = str(parameters[2])
    run = ['mce_cmd -x stop rc%s ret_dat' %(readoutcard)]
    a = subprocess.Popen(run, shell=True)
    deletetemp = ['rm /data/cryo/current_data/temp.*']
    b = subprocess.Popen(deletetemp, shell=True)
    #runtakedata.terminate()



def modZData(z, rc):
    new_z = []

    #1 -> 0-7, 2 -> 8-15, 3 -> 16-23, 4 -> 24-31
    if rc % 4 == 1:
        for i in range(32):
            new_z.append(z[i][:8])
    elif rc % 4 == 2:
        for i in range(32):
            new_z.append(z[i][8:16])
    elif rc % 4 == 3:
        for i in range(32):
            new_z.append(z[i][16:24])
    elif rc % 4 == 0:
        for i in range(32):
            new_z.append(z[i][24:])

    return new_z


@app.callback(
    Output('storedParameters', 'children'),
    [Input('parameterSubmit', 'n_clicks')],
    [State('observer', 'value'),
     State('datamode', 'value'),
     State('readoutcard', 'value'),
     State('framenumber', 'value')])
def storeParameters(n_clicks, observer, datamode, readoutcard, framenumber):
    if readoutcard == 9:
        new_readoutcard = 'All'
    else:
        new_readoutcard = readoutcard
    time = datetime.datetime.utcnow()
    time = time.isoformat()
    parameters=[observer, datamode, new_readoutcard, framenumber, time]
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

'''
@app.callback(
    Output('parameterCheck', 'children'),
    [Input('validParameters', 'children')])
def parameterError(json_validparameters):
    validparameters = json.loads(json_validparameters)
    if validparameters == 'Invalid':
        return '**One or more parameters not entered!!**'
'''

@app.callback(
    Output('url', 'pathname'),
    [Input('validParameters', 'children')],
    [State('storedParameters', 'children')])
def toggleDataCollection(json_validparameters, json_parameters):
    validparameters = json.loads(json_validparameters)
    parameters = json.loads(json_parameters)

    if validparameters == 'Valid':
        startDataCollection(parameters)
        time.sleep(1.0)
        if parameters[2] == 'All':
            runtakedata = subprocess.Popen(['python', 'takedataall.py', parameters[0]])
        else:
            runtakedata = subprocess.Popen(['python', 'takedata.py', parameters[0]])
        parafile = open('tempfiles/tempparameters.txt', 'w')
        for parameter in parameters:
            parafile.write(str(parameter)+' ')
        return '/data'
    else:
        return ''


@app.callback(
    Output('enteredParameters', 'children'),
    [Input('seeParameters', 'n_clicks')],
    [State('storedParameters', 'children')])
def showParameters(n_clicks, json_parameters):
    parameters = json.loads(json_parameters)
    parameterStr = '*Observer: ' + parameters[0] + '\n'
    parameterStr += '*Datamode: ' + str(parameters[1]) + '\n'
    parameterStr += '*Readout Card: ' + str(parameters[2]) + '\n'
    parameterStr += '*Number of Frames: ' + parameters[3]
    parameterStr += '*Time Started: ' + parameters[4]
    return parameterStr

'''
@app.callback(
    Output('stateMCE', 'children'),
    [Input('pauseData', 'n_clicks')])
def pauseDataCollection(pauseData):
    if pauseData/2 == 0:
        return 'MCE is running'
    else:
        return 'MCE is not running'
'''

@app.callback(
    Output('eStopData', 'children'),
    [Input('eStop', 'n_clicks')])
def eStopDataCollection(clicks):
    print('Hello!')
    if clicks > 0:
        eStop = 'Yes'
    else:
        eStop = 'No'
    print(eStop)
    return json.dumps(eStop)



@app.callback(
    Output('returnLink', 'children'),
    [Input('eStopData', 'children')],
    [State('storedParameters', 'children')])
def resetPage(eStop, json_parameters):
    parameters = json.loads(json_parameters)
    eStop = json.loads(eStop)
    print('Goodbye!')
    if eStop == 'Yes':
        print(eStop)
        stopDataCollection(parameters)
        return dcc.Link('Enter new parameters', href='/index')
    else:
        print(eStop)
        return 'Press Emergency Stop to stop MCE'


@app.callback(
    Output('rcgraph', 'options'),
    [Input('mcegraph', 'value')])
def changeGraphRC(mcegraph):
    if mcegraph == 1:
        return [{'label': 'RC 1', 'value': 1},
        {'label': 'RC 2', 'value': 2},
        {'label': 'RC 3', 'value': 3},
        {'label': 'RC 4', 'value': 4}]
    else:
        return [{'label': 'RC 1', 'value': 5},
        {'label': 'RC 2', 'value': 6},
        {'label': 'RC 3', 'value': 7},
        {'label': 'RC 4', 'value': 8}]


@app.callback(
    Output('rcheatmap', 'options'),
    [Input('mceheatmap', 'value')])
def changeheatmapRC(mceheatmap):
    if mceheatmap == 1:
        return [{'label': 'RC 1', 'value': 1},
        {'label': 'RC 2', 'value': 2},
        {'label': 'RC 3', 'value': 3},
        {'label': 'RC 4', 'value': 4}]
    else:
        return [{'label': 'RC 1', 'value': 5},
        {'label': 'RC 2', 'value': 6},
        {'label': 'RC 3', 'value': 7},
        {'label': 'RC 4', 'value': 8}]


@app.callback(
    Output('graphchannel', 'children'),
    [Input('chgraph', 'value')])
def changeChannel(chgraph):
    tempfile = open('tempfiles/tempchannel.txt', 'w')
    tempfile.write(str(chgraph))
    tempfile.close()
    return json.dumps(chgraph)

'''
@app.callback(
    Output('chgraph', 'options'),
    [Input('rcgraph', 'value')])
def changegraphCH(rcgraph):
    return [{'label': 'CH 1', 'value': 1 * rcgraph},
    {'label': 'CH 2', 'value': 2 * rcgraph},
    {'label': 'CH 3', 'value': 3 * rcgraph},
    {'label': 'CH 4', 'value': 4 * rcgraph},
    {'label': 'CH 5', 'value': 5 * rcgraph},
    {'label': 'CH 6', 'value': 6 * rcgraph},
    {'label': 'CH 7', 'value': 7 * rcgraph},
    {'label': 'CH 8', 'value': 8 * rcgraph}]
'''
'''
@app.callback(
    Output('enteredParameters', 'children'),
    [Input('parametersSubmit', 'n_clicks')],
    [State('observer', 'value'),
     State('datamode', 'value'),
     State('readoutcard', 'value'),
     State('framenumber', 'value'),
     State('parametersSubmitted', 'children')])
def showParameters(submit, observer, datamode, readoutcard, framenumber, parametersSubmitted):
    if observer == '' or datamode == '' or readoutcard == '' or framenumber == 0:
        return ''
    return u
    *observer: {} n
    *datamode: {} n
    *readoutcard: {} n
    *framenumber: {}
    .format(observer, datamode, readoutcard, framenumber)
'''
'''
@app.callback(
    Output('graphy', 'children'),
    [Input('heatInterval', 'n_intervals')])
def updateGraphY(n_intervals):
    allxy = [0, 0, 0]
    allch = []
    allx = []
    ally = []
    timeinterval = 10
    rows = 1

    n_intervals = n_intervals * 2 + 1

    print('gui', n_intervals)
    for p in range(timeinterval - 1, -1, -1):
        current = (n_intervals - p) % timeinterval
        if os.path.isfile('tempfiles/tempgraphdata%s.txt' % (current)):
            tempfile = open('tempfiles/tempgraphdata%s.txt' % (current), 'r')
            #z = [[ [] for i in range(32)] for j in range(32)]
            ch = tempfile.readline().strip()
            allch.append(int(ch))
            data = tempfile.readline().strip().split()
            smallx = []
            smally = []

            for i in range(rows):
                #sumy = 0
                smally = []
                for j in range(374):
                    #sumy += float(data[j])
                    smally.append(float(data[(j * rows) + 1 + i]))
                #y.append(sumy / 32)
                y.append(smally)

            for i in range(374):
                #smally = []
                #sumy = 0
                #for j in range(i * rows, i * rows + rows):
                #    sumy += float(data[j])
                    #smally.append(float(data[j]))
                #y.append(sumy / 32)
                #y.append(smally)
                if n_intervals > timeinterval:
                    masterx = i / 374.0
                    smallx.append((n_intervals - timeinterval + p) + masterx)
                        #totaltime.append((n_intervals - timeinterval + n) + masterx[i])
                else:
                    masterx = i / 374.0
                    smallx.append(p + masterx)
                    #totaltime.append(n + masterx)

                smally.append(float(data[i]))

            tempfile.close()
            allx.append(smallx)
            ally.append(smally)
            #print(n_intervals, p, current, ch)
            #print('isfile')
        else:
            #print('isntfile')
            pass
    allxy[0] = allch
    allxy[1]= allx
    allxy[2] = ally
    print(len(allxy) - 1)
    print(len(allxy[1]))
    return json.dumps(allxy)
'''
'''
@app.callback(
    Output('graphx', 'children'),
    [Input('heatInterval', 'n_intervals')])
def updateGraphX(n_intervals):
    x = []
    if n_intervals > 10:
        for i in range(10 * 374):
            x.append(i + n_intervals)
    else:
        for i in range(n_intervals * 374):
            x.append(i + (n_intervals * 374))
    return json.dumps(x)
'''

@app.callback(
    Output('mceGraph', 'figure'),
    [Input('rcgraph', 'value'),
     Input('graphInterval', 'n_intervals')],
    [State('storedParameters', 'children'),
    State('mceGraph', 'figure')])
    #State('heatInterval', 'n_intervals')])
    #State('graphx', 'children')])
def updateGraph(rcgraph, n_intervals, json_parameters, figure):
    totaltimeinterval = 30
    timeinterval = 2
    n_intervals = n_intervals * 2 + 1
    if n_intervals == 0:
        data = []
    elif figure is None:
        print(figure)
        #data = figure['data']
        data = []
    else:
        data = figure['data']



    #allxy = json.loads(xy)
    #masterx = []
    #for i in range(374):
        #masterx.append(i / 374.0)

    #for n in range(len(allxy[1])):
    print('gui', (n_intervals - 1) / 2, n_intervals)
    for p in range(1, -1, -1):
        current = (n_intervals - p) % timeinterval
        if os.path.isfile('tempfiles/tempgraphdata%s.txt' % (current)):
            tempfile = open('tempfiles/tempgraphdata%s.txt' % (current), 'r')
            #z = [[ [] for i in range(32)] for j in range(32)]
            ch = int(tempfile.readline().strip())
            datagrab = tempfile.readline().strip().split()
            smallx = []
            smally = []
            for i in range(374):
                masterx = i / 374.0
                smallx.append(n_intervals + masterx - p - 1)
                smally.append(float(datagrab[i]))
            tempfile.close()
            #allx.append(smallx)
            #ally.append(smally)
            x_axis = smallx
            y_data = smally
            '''
            if n_intervals > timeinterval:
                for i in range(374):
                    masterx = i / 374.0
                    x.append((n_intervals - timeinterval + n) + masterx)
                    #totaltime.append((n_intervals - timeinterval + n) + masterx[i])
            else:
                for i in range(374):
                    masterx = i / 374.0
                    x.append(n + masterx)
                    #totaltime.append(n + masterx)
            '''

            #print(len(y_data))
            #print(len(y_data[0]))
            #print(len(x_axis))
            #print(x_axis[0])
            #print(n, ch)

            if ch == 1:
                #for i in range(rows):
                trace0 = go.Pointcloud(
                        x = x_axis,
                        y = y_data,
                        #mode = 'markers',
                        #name = 'MCE Data',
                        marker = dict(
                            color = 'blue',
                            )
                        )
                data.append(trace0);

            elif ch == 2:
                #for i in range(rows):
                trace0 = go.Pointcloud(
                    x = x_axis,
                    y = y_data,
                    #mode = 'markers',
                    #name = 'MCE Data',
                    marker = dict(
                        color = 'red',
                        )
                    )
                data.append(trace0);

            elif ch == 3:
                #for i in range(rows):
                trace0 = go.Pointcloud(
                        x = x_axis,
                        y = y_data,
                        #mode = 'markers',
                        #name = 'MCE Data',
                        marker = dict(
                            color = 'green',
                            )
                        )
                data.append(trace0);

            elif ch == 4:
                #for i in range(rows):
                trace0 = go.Pointcloud(
                        x = x_axis,
                        y = y_data,
                        #mode = 'markers',
                        #name = 'MCE Data',
                        marker = dict(
                            color = 'yellow',
                            )
                        )
                data.append(trace0);

            elif ch == 5:
                #for i in range(rows):
                trace0 = go.Pointcloud(
                        x = x_axis,
                        y = y_data,
                        #mode = 'markers',
                        #name = 'MCE Data',
                        marker = dict(
                            color = 'orange',
                            )
                        )
                data.append(trace0);

            elif ch == 6:
                #for i in range(rows):
                trace0 = go.Pointcloud(
                        x = x_axis,
                        y = y_data,
                        #mode = 'markers',
                        #name = 'MCE Data',
                        marker = dict(
                            color = 'purple',
                            )
                        )
                data.append(trace0);

            elif ch == 7:
                #for i in range(rows):
                trace0 = go.Pointcloud(
                        x = x_axis,
                        y = y_data,
                        #mode = 'markers',
                        #name = 'MCE Data',
                        marker = dict(
                            color = 'brown',
                            )
                        )
                data.append(trace0);

            elif ch == 8:
                #for i in range(rows):
                trace0 = go.Pointcloud(
                        x = x_axis,
                        y = y_data,
                        #mode = 'markers',
                        #name = 'MCE Data',
                        marker = dict(
                            color = 'black',
                            )
                        )
                data.append(trace0);
            #data.append(trace0);
        else:
            pass

        #y = allxy[n + 1]
            #for i in range(rows):
            #    small_y_data = []
            #    for j in range(len(y)):
            #        small_y_data.append(y[j][i])
            #    y_data.append(small_y_data)

    parameters = json.loads(json_parameters)
    if n_intervals == totaltimeinterval + 1:
        data = data[1:]
        print(len(data))
    elif n_intervals > totaltimeinterval:
        data = data[2:]
        print(len(data))

    if n_intervals > totaltimeinterval:

        if rcgraph == 1:
            layout = dict(title= 'MCE 1 RC 1',
                          xaxis = dict(
                            title = 'Time from Start of Collection (seconds)',
                            ticklen= 10,
                            nticks= totaltimeinterval,
                            range=[n_intervals - totaltimeinterval, n_intervals]),
                          yaxis = dict(title = 'Counts'),
                          showlegend = False)

            fig = dict(data=data, layout=layout)

        elif rcgraph == 2:
            layout = dict(title= 'MCE 1 RC 2',
                           xaxis = dict(
                             title = 'Time from Start of Collection (seconds)',
                             ticklen= 10,
                             nticks= totaltimeinterval,
                             range=[n_intervals - totaltimeinterval, n_intervals]),
                           yaxis = dict(title = 'Counts'),
                          showlegend = False)

            fig = dict(data=data, layout=layout)

        elif rcgraph == 3:
            layout = dict(title= 'MCE 1 RC 3',
                           xaxis = dict(
                             title = 'Time from Start of Collection (seconds)',
                             ticklen= 10,
                             nticks= totaltimeinterval,
                             range=[n_intervals - totaltimeinterval, n_intervals]),
                           yaxis = dict(title = 'Counts'),
                          showlegend = False)

            fig = dict(data=data, layout=layout)

        elif rcgraph == 4:
            layout = dict(title= 'MCE 1 RC 4',
                           xaxis = dict(
                             title = 'Time from Start of Collection (seconds)',
                             ticklen= 10,
                             nticks= totaltimeinterval,
                             range=[n_intervals - totaltimeinterval, n_intervals]),
                           yaxis = dict(title = 'Counts'),
                          showlegend = False)

            fig = dict(data=data, layout=layout)

        elif rcgraph == 5:
            layout = dict(title= 'MCE 2 RC 1',
                           xaxis = dict(
                             title = 'Time from Start of Collection (seconds)',
                             ticklen= 10,
                             nticks= totaltimeinterval,
                             range=[n_intervals - totaltimeinterval, n_intervals]),
                           yaxis = dict(title = 'Counts'),
                          showlegend = False)

            fig = dict(data=data, layout=layout)

        elif rcgraph == 6:
            layout = dict(title= 'MCE 2 RC 2',
                           xaxis = dict(
                             title = 'Time from Start of Collection (seconds)',
                             ticklen= 10,
                             nticks= totaltimeinterval,
                             range=[n_intervals - totaltimeinterval, n_intervals]),
                           yaxis = dict(title = 'Counts'),
                          showlegend = False)

            fig = dict(data=data, layout=layout)

        elif rcgraph == 7:
            layout = dict(title= 'MCE 2 RC 3',
                           xaxis = dict(
                             title = 'Time from Start of Collection (seconds)',
                             ticklen= 10,
                             nticks= totaltimeinterval,
                             range=[n_intervals - totaltimeinterval, n_intervals]),
                           yaxis = dict(title = 'Counts'),
                          showlegend = False)

            fig = dict(data=data, layout=layout)

        elif rcgraph == 8:
            layout = dict(title= 'MCE 2 RC 4',
                           xaxis = dict(
                             title = 'Time from Start of Collection (seconds)',
                             ticklen= 10,
                             nticks= totaltimeinterval,
                             range=[n_intervals - totaltimeinterval, n_intervals]),
                           yaxis = dict(title = 'Counts'),
                          showlegend = False)

            fig = dict(data=data, layout=layout)

    else:
        if rcgraph == 1:
            layout = dict(title= 'MCE 1 RC 1',
                          xaxis = dict(
                            title = 'Time from Start of Collection (seconds)',
                            ticklen= 10,
                            nticks= n_intervals),
                          yaxis = dict(title = 'Counts'),
                          showlegend = False)

            fig = dict(data=data, layout=layout)

        elif rcgraph == 2:
            layout = dict(title= 'MCE 1 RC 2',
                           xaxis = dict(
                             title = 'Time from Start of Collection (seconds)',
                             ticklen= 10,
                             nticks= n_intervals),
                           yaxis = dict(title = 'Counts'),
                          showlegend = False)

            fig = dict(data=data, layout=layout)

        elif rcgraph == 3:
            layout = dict(title= 'MCE 1 RC 3',
                           xaxis = dict(
                             title = 'Time from Start of Collection (seconds)',
                             ticklen= 10,
                             nticks= n_intervals),
                           yaxis = dict(title = 'Counts'),
                          showlegend = False)

            fig = dict(data=data, layout=layout)

        elif rcgraph == 4:
            layout = dict(title= 'MCE 1 RC 4',
                           xaxis = dict(
                             title = 'Time from Start of Collection (seconds)',
                             ticklen= 10,
                             nticks= n_intervals),
                           yaxis = dict(title = 'Counts'),
                          showlegend = False)

            fig = dict(data=data, layout=layout)

        elif rcgraph == 5:
            layout = dict(title= 'MCE 2 RC 1',
                           xaxis = dict(
                             title = 'Time from Start of Collection (seconds)',
                             ticklen= 10,
                             nticks= n_intervals),
                           yaxis = dict(title = 'Counts'),
                          showlegend = False)

            fig = dict(data=data, layout=layout)

        elif rcgraph == 6:
            layout = dict(title= 'MCE 2 RC 2',
                           xaxis = dict(
                             title = 'Time from Start of Collection (seconds)',
                             ticklen= 10,
                             nticks= n_intervals),
                           yaxis = dict(title = 'Counts'),
                          showlegend = False)

            fig = dict(data=data, layout=layout)

        elif rcgraph == 7:
            layout = dict(title= 'MCE 2 RC 3',
                           xaxis = dict(
                             title = 'Time from Start of Collection (seconds)',
                             ticklen= 10,
                             nticks= n_intervals),
                           yaxis = dict(title = 'Counts'),
                          showlegend = False)

            fig = dict(data=data, layout=layout)

        elif rcgraph == 8:
            layout = dict(title= 'MCE 2 RC 4',
                           xaxis = dict(
                             title = 'Time from Start of Collection (seconds)',
                             ticklen= 10,
                             nticks= n_intervals),
                           yaxis = dict(title = 'Counts'),
                          showlegend = False)

            fig = dict(data=data, layout=layout)

    return fig

'''
@app.callback(
    Output('mceHeatmap', 'figure'),
    [Input('rcheatmap', 'value'),
     Input('heatInterval', 'n_intervals')],
    [State('storedParameters', 'children')])
def runHeatmap(heatmapOptions, n_intervals, json_parameters):
    parameters = json.loads(json_parameters)
    return guiheatmap.initHeatmap(parameters, heatmapOptions)
'''

'''
@app.callback(
    Output('mceHeatmap', 'figure'),
    [Input('heatInterval', 'n_intervals'),
    Input('heatmapOptions', 'value'),
    Input('showHeatmap', 'n_clicks')],
    [State('storeParameters', 'children')])
def updateHeatmap(n_intervals, heatmapOptions, n_clicks, json_parameters):
    parameters = json.loads(json_parameters)
    return guiheatmap.initHeatmap(parameters, heatmapOptions)


    if parameters[2] == 'All':
        print('All Readout Cards')
        z = fakedataall.getMCEData()
        new_z = modZData(z, heatmapOptions)

        data = [
                go.Heatmap(z=new_z,
                           x=['CH1', 'CH2', 'CH3', 'CH4', 'CH5','CH6','CH7','CH8'],
                           y=['Row1','Row2','Row3','Row4','Row5','Row6','Row7',\
                              'Row8','Row9','Row13','Row11','Row12','Row13','Row14',\
                              'Row15','Row16','Row17','Row18','Row19','Row23','Row21',\
                              'Row22','Row23','Row24','Row25','Row26','Row27','Row28',\
                              'Row29','Row33','Row31','Row32','Row33'])
        ]

        if heatmapOptions == 1:
            layout = go.Layout(title = 'MCE 1 RC 1',
                          xaxis = dict(title = 'Channel'),
                          yaxis = dict(title = 'Row'))

        elif heatmapOptions == 2:
            layout = go.Layout(title = 'MCE 1 RC 2',
                          xaxis = dict(title = 'Channel'),
                          yaxis = dict(title = 'Row'))

        elif heatmapOptions == 3:
            layout = go.Layout(title = 'MCE 1 RC 3',
                          xaxis = dict(title = 'Channel'),
                          yaxis = dict(title = 'Row'))

        elif heatmapOptions == 4:
            layout = go.Layout(title = 'MCE 1 RC 4',
                          xaxis = dict(title = 'Channel'),
                          yaxis = dict(title = 'Row'))

        elif heatmapOptions == 5:
            layout = go.Layout(title = 'MCE 2 RC 1',
                          xaxis = dict(title = 'Channel'),
                          yaxis = dict(title = 'Row'))

        elif heatmapOptions == 6:
            layout = go.Layout(title = 'MCE 2 RC 2',
                          xaxis = dict(title = 'Channel'),
                          yaxis = dict(title = 'Row'))

        elif heatmapOptions == 7:
            layout = go.Layout(title = 'MCE 2 RC 3',
                          xaxis = dict(title = 'Channel'),
                          yaxis = dict(title = 'Row'))

        elif heatmapOptions == 8:
            layout = go.Layout(title = 'MCE 2 RC 4',
                          xaxis = dict(title = 'Channel'),
                          yaxis = dict(title = 'Row'))

    else:
        print('Readout Card', parameters[2])
        z = fakedata.getMCEData()

        data = [
                go.Heatmap(z=z,
                           x=['CH1', 'CH2', 'CH3', 'CH4', 'CH5','CH6','CH7','CH8'],
                           y=['Row1','Row2','Row3','Row4','Row5','Row6','Row7',\
                              'Row8','Row9','Row13','Row11','Row12','Row13','Row14',\
                              'Row15','Row16','Row17','Row18','Row19','Row23','Row21',\
                              'Row22','Row23','Row24','Row25','Row26','Row27','Row28',\
                              'Row29','Row33','Row31','Row32','Row33'])
        ]

        if parameters[2] == 1:
            layout = go.Layout(title = 'MCE 1 RC 1',
                          xaxis = dict(title = 'Channel'),
                          yaxis = dict(title = 'Row'))

        elif parameters[2] == 2:
            layout = go.Layout(title = 'MCE 1 RC 2',
                          xaxis = dict(title = 'Channel'),
                          yaxis = dict(title = 'Row'))

        elif parameters[2] == 3:
            layout = go.Layout(title = 'MCE 1 RC 3',
                          xaxis = dict(title = 'Channel'),
                          yaxis = dict(title = 'Row'))

        elif parameters[2] == 4:
            layout = go.Layout(title = 'MCE 1 RC 4',
                          xaxis = dict(title = 'Channel'),
                          yaxis = dict(title = 'Row'))

        elif parameters[2] == 5:
            layout = go.Layout(title = 'MCE 2 RC 1',
                          xaxis = dict(title = 'Channel'),
                          yaxis = dict(title = 'Row'))

        elif parameters[2] == 6:
            layout = go.Layout(title = 'MCE 2 RC 2',
                          xaxis = dict(title = 'Channel'),
                          yaxis = dict(title = 'Row'))

        elif parameters[2] == 7:
            layout = go.Layout(title = 'MCE 2 RC 3',
                          xaxis = dict(title = 'Channel'),
                          yaxis = dict(title = 'Row'))

        elif parameters[2] == 8:
            layout = go.Layout(title = 'MCE 2 RC 4',
                          xaxis = dict(title = 'Channel'),
                          yaxis = dict(title = 'Row'))

    fig = go.Figure(data=data, layout=layout)

    return fig
'''

'''
@app.callback(
        Output('heatmapCheck', 'children'),
        [Input('heatmapOptions', 'value')])
def sanityCheck(rc):
    return 'Hello!' + str(rc)
'''

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
