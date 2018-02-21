# just loading dependencies and packages
import plotly.plotly as py
import numpy as np
import plotly.tools as tls
import plotly.graph_objs as go
import mce_data
import os
import matplotlib.pyplot as plt
import sys
from subprocess import Popen, PIPE
from datetime import datetime
import subprocess
from shutil import copy2
import time

i = 0
t = []
tcurrent = time.time()
while time.time() <= tcurrent + 1:
    f = mce_data.SmallMCEFile('/data/cryo/current_data/temp')
    h = f.Read(row_col=True, unfilter='DC').data
    t.append(h)

    if i == 0:
        copy2('/data/cryo/current_data/temp.run','/data/cryo/current_data/%s' %(filename) + '.run')
        open("/data/cryo/current_data/temp","w").close()

    i=i+1
    time.sleep(0.1)  # wait for 100 milliseconds before running next loop

open("/data/cryo/current_data/temp","w").close()
open("/data/cryo/current_data/temp.run", "w").close()

l = []
d = numpy.zeroes((33,8))
for i in range(len(t)):
    for j in range(len(t)):
        for k in range(len(t)):
            l.append(t[i][j][k])
        d[i][j].append(np.stdev(l))
        l = []

return dcc.Graph(
        id='Heatmap',
        figure={
            'data':[
                go.Heatmap(z=[[d[0,0], d[0,1], d[0,2], d[0,3], d[0,4], d[0,5], d[0,6], d[0,7]],
                                      [d[1,0], d[1,1], d[1,2], d[1,3], d[1,4], d[1,5], d[1,6], d[1,7]],
                                      [d[2,0], d[2,1], d[2,2], d[2,3], d[2,4], d[2,5], d[2,6], d[2,7]],
                                      [d[3,0], d[3,1], d[3,2], d[3,3], d[3,4], d[3,5], d[3,6], d[3,7]],
                                      [d[4,0], d[4,1], d[4,2], d[4,3], d[4,4], d[4,5], d[4,6], d[4,7]],
                                      [d[5,0], d[5,1], d[5,2], d[5,3], d[5,4], d[5,5], d[5,6], d[5,7]],
                                      [d[6,0], d[6,1], d[6,2], d[6,3], d[6,4], d[6,5], d[6,6], d[6,7]],
                                      [d[7,0], d[7,1], d[7,2], d[7,3], d[7,4], d[7,5], d[7,6], d[7,7]],
                                      [d[8,0], d[8,1], d[8,2], d[8,3], d[8,4], d[8,5], d[8,6], d[8,7]],
                                      [d[9,0], d[9,1], d[9,2], d[9,3], d[9,4], d[9,5], d[9,6], d[9,7]],
                                      [d[10,0], d[10,1], d[10,2], d[10,3], d[10,4], d[10,5], d[10,6], d[10,7]],
                                      [d[11,0], d[11,1], d[11,2], d[11,3], d[11,4], d[11,5], d[11,6], d[11,7]],
                                      [d[12,0], d[12,1], d[12,2], d[12,3], d[12,4], d[12,5], d[12,6], d[12,7]],
                                      [d[13,0], d[13,1], d[13,2], d[13,3], d[13,4], d[13,5], d[13,6], d[13,7]],
                                      [d[14,0], d[14,1], d[14,2], d[14,3], d[14,4], d[14,5], d[14,6], d[14,7]],
                                      [d[15,0], d[15,1], d[15,2], d[15,3], d[15,4], d[15,5], d[15,6], d[15,7]],
                                      [d[16,0], d[16,1], d[16,2], d[16,3], d[16,4], d[16,5], d[16,6], d[16,7]],
                                      [d[17,0], d[17,1], d[17,2], d[17,3], d[17,4], d[17,5], d[17,6], d[17,7]],
                                      [d[18,0], d[18,1], d[18,2], d[18,3], d[18,4], d[18,5], d[18,6], d[18,7]],
                                      [d[19,0], d[19,1], d[19,2], d[19,3], d[19,4], d[19,5], d[19,6], d[19,7]],
                                      [d[20,0], d[20,1], d[20,2], d[20,3], d[20,4], d[20,5], d[20,6], d[20,7]],
                                      [d[21,0], d[21,1], d[21,2], d[21,3], d[21,4], d[21,5], d[21,6], d[21,7]],
                                      [d[22,0], d[22,1], d[22,2], d[22,3], d[22,4], d[22,5], d[22,6], d[22,7]],
                                      [d[23,0], d[23,1], d[23,2], d[23,3], d[23,4], d[23,5], d[23,6], d[23,7]],
                                      [d[24,0], d[24,1], d[24,2], d[24,3], d[24,4], d[24,5], d[24,6], d[24,7]],
                                      [d[25,0], d[25,1], d[25,2], d[25,3], d[25,4], d[25,5], d[25,6], d[25,7]],
                                      [d[26,0], d[26,1], d[26,2], d[26,3], d[26,4], d[26,5], d[26,6], d[26,7]],
                                      [d[27,0], d[27,1], d[27,2], d[27,3], d[27,4], d[27,5], d[27,6], d[27,7]],
                                      [d[28,0], d[28,1], d[28,2], d[28,3], d[28,4], d[28,5], d[28,6], d[28,7]],
                                      [d[29,0], d[29,1], d[29,2], d[29,3], d[29,4], d[29,5], d[29,6], d[29,7]],
                                      [d[30,0], d[30,1], d[30,2], d[30,3], d[30,4], d[30,5], d[30,6], d[30,7]],
                                      [d[31,0], d[31,1], d[31,2], d[31,3], d[31,4], d[31,5], d[31,6], d[31,7]],

                           x=['CH1', 'CH2', 'CH3', 'CH4', 'CH5','CH6','CH7','CH8'],
                           y=['Row1','Row2','Row3','Row4','Row5','Row6','Row7','Row8','Row9','Row10','Row11','Row12','Row13','Row14','Row15','Row16','Row17','Row18','Row19','Row20','Row21','Row22','Row23','Row24',
                              'Row25','Row26','Row27','Row28','Row29','Row30','Row31','Row32','Row33'])
                ],
            'layout':go.Layout(title= 'MCE Heatmap',
                               xaxis= {'title':'Channel'},
                               yaxis= {'title':'Data'}
                               )
            }),
