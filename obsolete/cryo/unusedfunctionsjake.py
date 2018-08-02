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
