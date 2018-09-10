#!/usr/bin/python
import os
import mce_data
import matplotlib.pyplot as plt
import numpy
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

i = 0
while True :
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

	except KeyboardInterrupt :
		print("Data acquisition stopped after %s runs" %(i))
		exit()

