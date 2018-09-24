#!/usr/bin/python
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
#import mce_data
#import matplotlib.pyplot as plt


app = dash.Dash(__name__)

app.css.append_css({"external_url": "https://codepen.io/chriddyp/pen/bWLwgP.css"})

app.config.supress_callback_exceptions=True

app.layout = html.Div([ #Main layout of gui
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
        ], style={}, id='inputParameters'),
        ], style={'gridColumn': '1 / span 1',
              'gridRow': '2 / span 1'}
        ),

    html.Div([ #Start/Stop Buttons Div
        html.H4(children='Pause/Emergency Stop Buttons'),
        html.Button('Pause/Resume', id='pauseData'),
        html.Button('Emergency Stop', id='eStop'),
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
        dcc.Graph(
            id='Heatmap',
            figure={
                'data':[
                    go.Heatmap(z=[[1, 0, 0, 0, 0, 0, 0, 0],
                                  [2, 0, 0, 0, 0, 0, 0, 0],
                                  [3, 0, 0, 0, 0, 0, 0, 0],
                                  [4, 0, 0, 0, 0, 0, 0, 0],
                                  [5, 0, 0, 0, 0, 0, 0, 0],
                                  [6, 0, 0, 0, 0, 0, 0, 0],
                                  [7, 0, 0, 0, 0, 0, 0, 0],
                                  [8, 0, 0, 0, 0, 0, 0, 0],
                                  [9, 0, 0, 0, 0, 0, 0, 0],
                                  [10, 0, 0, 0, 0, 0, 0, 0],
                                  [11, 0, 0, 0, 0, 0, 0, 0],
                                  [12, 0, 0, 0, 0, 0, 0, 0],
                                  [13, 0, 0, 0, 0, 0, 0, 0],
                                  [14, 0, 0, 0, 0, 0, 0, 0],
                                  [15, 0, 0, 0, 0, 0, 0, 0],
                                  [16, 0, 0, 0, 0, 0, 0, 0],
                                  [17, 0, 0, 0, 0, 0, 0, 0],
                                  [18, 0, 0, 0, 0, 0, 0, 0],
                                  [19, 0, 0, 0, 0, 0, 0, 0],
                                  [20, 0, 0, 0, 0, 0, 0, 0],
                                  [21, 0, 0, 0, 0, 0, 0, 0],
                                  [22, 0, 0, 0, 0, 0, 0, 0],
                                  [23, 0, 0, 0, 0, 0, 0, 0],
                                  [24, 0, 0, 0, 0, 0, 0, 0],
                                  [25, 0, 0, 0, 0, 0, 0, 0],
                                  [26, 0, 0, 0, 0, 0, 0, 0],
                                  [27, 0, 0, 0, 0, 0, 0, 0],
                                  [28, 0, 0, 0, 0, 0, 0, 0],
                                  [29, 0, 0, 0, 0, 0, 0, 0],
                                  [30, 0, 0, 0, 0, 0, 0, 0],
                                  [31, 0, 0, 0, 0, 0, 0, 0],
                                  [32, 0, 0, 0, 0, 0, 0, 0],
                                  [33, 0, 0, 0, 0, 0, 0, 0]],
                               x=['CH1', 'CH2', 'CH3', 'CH4', 'CH5','CH6','CH7','CH8'],
                               y=['Row1','Row2','Row3','Row4','Row5','Row6','Row7','Row8','Row9','Row10','Row11','Row12','Row13','Row14','Row15','Row16','Row17','Row18','Row19','Row20','Row21','Row22','Row23','Row24',
                                  'Row25','Row26','Row27','Row28','Row29','Row30','Row31','Row32','Row33'])
                    ],
                'layout':go.Layout(title= 'MCE Heatmap',
                                   xaxis= {'title':'Channel'},
                                   yaxis= {'title':'Data'}
                                   )
                }),
        #dcc.Interval(
        #    id='heatInterval',
        #    interval=5*1000,
        #    n_intervals=0
        #)
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
            html.Div(children='Yes', id='parametersSubmitted') #holds state of data submission
        ], style={'display': 'none'}
        ),
], style={'textAlign': 'center',
          'margin': 'auto',
          'display': 'grid',
          'gridTemplateColumns': 'auto auto auto',
          'gridTemplateRows': 'auto auto auto'})



@app.callback(
    Output('inputParameters', 'children'),
    [Input('parameterSubmit', 'n_clicks'),
     Input('eStop', 'n_clicks')],
    [State('filename', 'value'),
     State('datamode', 'value'),
     State('readoutcard', 'value'),
     State('framenumber', 'value')])
def startDataCollection(submit, eStop, filename, datamode, readoutcard, framenumber):
    if filename == '' or datamode == '' or readoutcard == '' or framenumber == 0:
        return '''**One or more parameters not entered!**'''
    if readoutcard == 5:
        str(readoutcard)
        readoutcard = 'All'
    if submit > eStop and mceState == 'On':
        return u'''
            Filename: {}
            Datamode: {}
            Readout Card: {}
            Number of Frames: {}
        '''.format(filename, datamode, readoutcard, framenumber)
    else:
        return html.Div([
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
        ], style={}),

'''
@app.callback(
    Output('mceState', 'children'),
    [Input('startData', 'n_clicks'),
     Input('eStop', 'n_clicks')],
    [State('mceState', 'children'),
     State('parametersSubmitted', 'children')])
def toggleMCE(start_clicks, estop_clicks, mceState, parametersSubmitted):
    if start_clicks >= estop_clicks:
        if mceState == 'Off' and parametersSubmitted == 'Yes':
            return 'On'
        elif mceState == 'Off' and parametersSubmitted == 'No':
            return 'Off'
        else:
            return 'Off'
    else:
        return 'Off'
'''
'''
@app.callback(
    Output('parametersSubmitted', 'children'),
    [Input('parameterSubmit', 'n_clicks')],
    [State('mceState', 'children'),
     State('parametersSubmitted', 'children')])
def toggleParameters(n_clicks, mceState, parametersSubmitted):
    if parametersSubmitted == 'No' and mceState == 'Off':
        return 'Yes'
    else:
        return 'No'

'''
'''
@app.callback(
    Output('submitButton', 'children'),
    [Input('startData', 'n_clicks'),
     Input('eStop', 'n_clicks')],
    [State('mceState', 'children'),
     State('parametersSubmitted', 'children')])
def disableSubmit(start_clicks, estop_clicks, mceState, parametersSubmitted):
    if start_clicks >= estop_clicks:
        if mceState == 'Off' and parametersSubmitted == 'Yes':
            return ''
        elif mceState == 'On' and parametersSubmitted == 'Yes':
            return ''
        else:
            return html.Button('Submit', id='parameterSubmit')
    elif estop_clicks >= start_clicks:
        if mceState == 'On' and parametersSubmitted == 'Yes':
            return html.Button('Submit', id='parameterSubmit')
    return html.Button('Submit', id='parameterSubmit')
'''
'''@app.callback(
    Output('parameterSubmit', 'children'),
    [Input('eStop', 'n_clicks')])
def eStopDataCollection(n_clicks, filename, datamode, readoutcard, framenumber):
    return ''
'''

'''@app.callback(
    Output('liveHeatmap', 'figure'),
    [Input('heatInterval', 'n_intervals')])
def makeHeatmap(n):
    #init plotly heatmap object
    trace = go.Heatmap(z=[[1, 0, 0, 0, 0, 0, 0, 0],
                          [2, 0, 0, 0, 0, 0, 0, 0],
                          [3, 0, 0, 0, 0, 0, 0, 0],
                          [4, 0, 0, 0, 0, 0, 0, 0],
                          [5, 0, 0, 0, 0, 0, 0, 0],
                          [6, 0, 0, 0, 0, 0, 0, 0],
                          [7, 0, 0, 0, 0, 0, 0, 0],
                          [8, 0, 0, 0, 0, 0, 0, 0],
                          [9, 0, 0, 0, 0, 0, 0, 0],
                          [10, 0, 0, 0, 0, 0, 0, 0],
                          [11, 0, 0, 0, 0, 0, 0, 0],
                          [12, 0, 0, 0, 0, 0, 0, 0],
                          [13, 0, 0, 0, 0, 0, 0, 0],
                          [14, 0, 0, 0, 0, 0, 0, 0],
                          [15, 0, 0, 0, 0, 0, 0, 0],
                          [16, 0, 0, 0, 0, 0, 0, 0],
                          [17, 0, 0, 0, 0, 0, 0, 0],
                          [18, 0, 0, 0, 0, 0, 0, 0],
                          [19, 0, 0, 0, 0, 0, 0, 0],
                          [20, 0, 0, 0, 0, 0, 0, 0],
                          [21, 0, 0, 0, 0, 0, 0, 0],
                          [22, 0, 0, 0, 0, 0, 0, 0],
                          [23, 0, 0, 0, 0, 0, 0, 0],
                          [24, 0, 0, 0, 0, 0, 0, 0],
                          [25, 0, 0, 0, 0, 0, 0, 0],
                          [26, 0, 0, 0, 0, 0, 0, 0],
                          [27, 0, 0, 0, 0, 0, 0, 0],
                          [28, 0, 0, 0, 0, 0, 0, 0],
                          [29, 0, 0, 0, 0, 0, 0, 0],
                          [30, 0, 0, 0, 0, 0, 0, 0],
                          [31, 0, 0, 0, 0, 0, 0, 0],
                          [32, 0, 0, 0, 0, 0, 0, 0],
                          [33, 0, 0, 0, 0, 0, 0, 0]],
                       x=['CH1', 'CH2', 'CH3', 'CH4', 'CH5','CH6','CH7','CH8'],
                       y=['Row1','Row2','Row3','Row4','Row5','Row6','Row7','Row8','Row9','Row10','Row11','Row12','Row13','Row14','Row15','Row16','Row17','Row18','Row19','Row20','Row21','Row22','Row23','Row24',
                          'Row25','Row26','Row27','Row28','Row29','Row30','Row31','Row32','Row33'])
    data=[trace]
    return py.iplot(data, filename='channel_rms_heatmap')
'''


'''def getTestData():
    f = mce_data.SmallMCEFile('data_test4_2.858Arms_3hz')
    d = f.Read(row_col=True, unfilter='DC').data
    print d.shape

    i = 0
    T = range(d.shape[0])
    for i in range(d.shape[1]):
    	plt.plot(T,d[:,i])

    plt.show()
'''
if __name__ == '__main__':
	app.run_server(debug=True)
