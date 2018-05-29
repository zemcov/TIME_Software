import plotly.graph_objs as go
#import fakedata
#import fakedataall
#import takedata
#import takedataall


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


def initHeatmap(parameters, heatmapOptions):
    if parameters[2] == 'All':
        print('All Readout Cards')
        tempfile = open('tempfiles/tempzdata.txt', 'r')
        #z = [[ [] for i in range(32)] for j in range(32)]
        z = []
        for line in tempfile:
            x = line.strip().split()
            for i in range(len(x)):
                x[i] = int(float(x[i]))
                pass
            z.append(x)
        tempfile.close()

        new_z = modZData(z, heatmapOptions)

        data = [
                go.Heatmap(z=new_z,
                           x=['CH1', 'CH2', 'CH3', 'CH4', 'CH5','CH6','CH7','CH8'],
                           y=['Row1','Row2','Row3','Row4','Row5','Row6','Row7',\
                              'Row8','Row9','Row10','Row11','Row12','Row13','Row14',\
                              'Row15','Row16','Row17','Row18','Row19','Row20','Row21',\
                              'Row22','Row23','Row24','Row25','Row26','Row27','Row28',\
                              'Row29','Row30','Row31','Row32','Row33', 'Row34', 'Row35',\
                              'Row36', 'Row37', 'Row38', 'Row39', 'Row40', 'Row41'])
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
        tempfile = open('tempfiles/tempzdata.txt', 'r')
        #z = [[ [] for i in range(32)] for j in range(32)]
        z = []
        for line in tempfile:
            x = line.strip().split()
            for i in range(len(x)):
                x[i] = int(float(x[i]))
            z.append(x)
        tempfile.close()

        data = [
                go.Heatmap(z=z,
                           x=['CH1', 'CH2', 'CH3', 'CH4', 'CH5','CH6','CH7','CH8'],
                            y=['Row1','Row2','Row3','Row4','Row5','Row6','Row7',\
                               'Row8','Row9','Row10','Row11','Row12','Row13','Row14',\
                               'Row15','Row16','Row17','Row18','Row19','Row20','Row21',\
                               'Row22','Row23','Row24','Row25','Row26','Row27','Row28',\
                               'Row29','Row30','Row31','Row32','Row33', 'Row34', 'Row35',\
                               'Row36', 'Row37', 'Row38', 'Row39', 'Row40', 'Row41'])
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

if __name__ == '__main__':
    main()
