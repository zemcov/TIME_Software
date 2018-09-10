#!/usr/bin/python
import os
import mce_data
import matplotlib.pyplot as plt
#import mcelib
import numpy
import sys
#import basic.py
from subprocess import Popen, PIPE
#import pykst as kst
from datetime import datetime
import subprocess

# takes user input and saves that as filename, and adds mce header to it
filename = str(sys.argv[1])

''' 
filename = open("/data/cryo/current_data/"+str(sys.argv[1])+".run", "w") 
output_stream=Popen(["mce_status"], stdin=PIPE, stdout=filename)
output_stream.stdin.close()
''' 

rc = sys.argv[2]
numframe = sys.argv[3]

#print("I have a file with a header now...")

# ask user for specific mce_run info, can add more later as desired
datamode = str(input('Enter data mode value as int:'))
changedatamode = ["mce_cmd -x wb %s data_mode %s" % (rc,datamode)]
subprocess.Popen(changedatamode, shell=True)

# data_rate
# num_rows
# row_len

print("I have set the data mode to something...")
 
# start a kst session with the same name as the file plus the date and time
#client = kst.Client("filename-(str(datetime.now()))

# start a bash command that will write the location for the temp file
''' 
subprocess.Popen(["mce_cmd -x acq_path /data/cryo/current_data"],shell=True)
print("acq_path did a thing")
'''

#start a bash command to create and configure the temp file
open("/data/cryo/current_data/temp.run","w").close()

''' 
tempfile = ["mce_cmd -x acq_config /data/cryo/current_data/temp.dat %s" % (rc)]
subprocess.Popen(tempfile, shell=True)
print("acq_config did a thing")
'''

#keep acquiring that number of frame data until someone issues the stop command
''' 
lock = ["mce_cmd -e -X lock_down -X lock_query"]
subprocess.Popen(lock, shell=True)
acqgo = ["mce_cmd -x acq_go %s" % (numframe)]
subprocess.Popen(acqgo, shell=True)
'''
run = ["mce_run temp.run %s %s && cat /data/cryo/current_data/temp.run >> /data/cryo/current_data/%s" % (numframe,rc,filename)]
subprocess.Popen(run, shell=True)
print("Data acquisition started")

print("Enter 'touch /data/cryo/stop' at command line to end data acquisition")
while True :
	if not /data/cryo/stop :
		run = ["mce_run temp.run %s %s && cat /data/cryo/current_data/temp.run >> /data/cryo/current_data/%s" % (numframe,rc,filename)]
		subprocess.Popen(run, shell=True)

		# running go and copying output from acq_go in temp.run to filename
		#subprocess.Popen(['mce_cmd','-x','acq_go', numframe, '&&', 'cat', '/data/cryo/current_data/temp.run', '>>', '/data/cryo/current_data/filename'],shell=True)
	else :
		# putting in a way for user to stop data acquisition, breaks while loop
		#subprocess.Popen(['mce_cmd','-x','stop',rc,'ret_dat'],shell=True)
		break

##################################################################################################


""" 
Other stuff that we may use later for kst...
"""

#f = mce_data.MCEFile('/data/cryo/current_data/testfile5')
#d = f.Read(row_col=True, unfilter='DC').data
#print d.shape
#print d[1,1]
#plt.plot(d[1,1])
#plt.show()

""" 
Idea for passing data into kst using its syntax, used in histogram test script


alldata = array([], dtype=int16)
n=zeros(16384, dtype=int32)
for f in files[0:10000]:
  data=MCEFile(f).Read(data_mode=12).data[0,:]
  alldata = concatenate((alldata,data))
  for d in data:
    n[d + 8192] += 1

stdev[ch] = std(alldata)
print "stdev =", stdev[ch]

"""
