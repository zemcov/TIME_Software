#!/usr/bin/python 

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

# takes user input and saves that as filename, and adds mce header to it
filename = str(sys.argv[1])
rc = sys.argv[2]
numframe = sys.argv[3]

# ask user for specific mce_run info, can add more later as desired
datamode = str(input('Enter data mode value as int:'))
changedatamode = ["mce_cmd -x wb rc%s data_mode %s" % (rc,datamode)]
a = subprocess.Popen(changedatamode, shell=True)
a.communicate()
print("I have set the data mode to something...")
print("Data acquisition started")

# make sure that the credentials file has stream id tokens already set

#getting stream id from id list
stream_ids = tls.get_credentials_file()['stream_ids']
stream_id=stream_ids[0]

# making an instance of a stream
stream_1 = dict(token=stream_id, maxpoints=1000)
''' stream_1 = go.Stream(
	token=stream_id # link stream id to 'token' key
	maxpoints = 1000 # max number of points kept on screen
) '''

# initializing the trace & embedding 1 stream id per trace
trace1 = go.Scatter(
	x=[],
	y=[],
	# can optionally set 'mode = "lines+markers",' here
	stream=stream_1
)
data = go.Data([trace1])

# formatting and initializing the figure in plotly
layout = go.Layout(title='MCE Run Acquisition 4')
fig = go.Figure(data=data, layout=layout)
py.iplot(fig,filename='mce run test 4')

# initializing a stream link object which updates the chart in plotly
s = py.Stream(stream_id)
s.open()

import datetime
import time

# delay start to find correct tab
time.sleep(5)

i=0
while True:
	try :
                print(i)
                run  = ["mce_run temp %s %s && cat /data/cryo/current_data/temp >> /data/cryo/current_data/%s" %(numframe,rc,filename)]
                b = subprocess.Popen(run, shell=True)
                b.communicate()

                if i == 0:
                        copy2('/data/cryo/current_data/temp.run','/data/cryo/current_data/%s' %(filename) + '.run')
                        open("/data/cryo/current_data/temp","w").close()
                else :
                        open("/data/cryo/current_data/temp","w").close()
                        open("/data/cryo/current_data/temp.run" , "w").close()
                i = i + 1
		
		# create mce data object
                f = mce_data.SmallMCEFile('/data/cryo/current_data/%s' %(filename))
                d = f.Read(row_col=True, unfilter='DC').data
		
		x = datetime.datetime.now().strftime('%m-%d-%Y %H:%M:%S.%f')
	        y = (d[1,1])
        	s.write(dict(x=x, y=y))
        	time.sleep(1) #plots one point every second

        except KeyboardInterrupt :
                s.close()
		print("Data acquisition stopped after %s runs" %(i))
                exit()

