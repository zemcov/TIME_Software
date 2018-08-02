#!/usr/bin/python2.7
import numpy as np
import math
import mce_data
import time
import plotly.plotly as py
import plotly.graph_objs as go
import plotly.tools as tls
import plotly
import time
#plotly.tools.set_credentials_file(username='vlb9398', api_key='i0QfJqD211xkkR22MuqW')

def readdata():
    n = 0
    f = mce_data.SmallMCEFile('/data/TIME_Software/cryo/20171009/data_test4_2.858Arms_3hz')
    h = f.Read(row_col=True, unfilter='DC').data

    d = [[ [] for i in range(32)] for j in range(31)]

    stream_ids = tls.get_credentials_file()['stream_ids']
    stream_id=stream_ids[0]
    heatmap = go.Heatmap(stream=dict(token=stream_id))
    plot_data = go.Data([heatmap])
    py.plot(plot_data)

    s = py.Stream(stream_id)
    s.open()
    time.sleep(5)
    while n < 5000:
        t = time.time()
        for i in range(32):
            for j in range(31):
                d[j][i] = (np.std(h[j,i,n:n+1000]))
        n = n + 1000
        print(d[27][4])

        z=([[d[23][0],d[23][1],d[23][2],d[23][3],d[23][4]],
            [d[24][0],d[24][1],d[24][2],d[24][3],d[24][4]],
            [d[25][0],d[25][1],d[25][2],d[25][3],d[25][4]],
            [d[26][0],d[26][1],d[26][2],d[26][3],d[26][4]],
            [d[27][0],d[27][1],d[27][2],d[27][3],d[27][4]]])
        s.write(dict(z=z, type='heatmap'))
        print("time elapsed for loop: %s" %(time.time()-t))
        t = 0
        time.sleep(2)
    s.close()

readdata()
