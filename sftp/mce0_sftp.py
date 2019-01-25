import os
import subprocess
import time
import shutil
import sys
import datetime as dt
from termcolor import colored

# sys.stdout = os.fdopen(sys.stdout.fileno(), 'w', 1) # line buffering

a = 0
dir = '/data/cryo/current_data/'
# print colored('----- Starting MCE0 Data Transfer -----','green')
begin = dt.datetime.utcnow()
end = dt.datetime.utcnow()
while end - begin < dt.timedelta(seconds = 3):
    if os.path.exists(dir + "temp.%0.3i" %(a+1)) : #wait to read new file until old file is complete
        mce_file_name = dir + 'temp.%0.3i' % (a)
        # print 'File Transfered (MCE0):',(mce_file_name.replace(dir,''))
        if a == 0:
            subprocess.Popen(['scp', dir + 'temp.run',  'time-master:/home/time/Desktop/time-data/mce1/temp.run']).wait()
        if os.path.exists(mce_file_name) :
            subprocess.Popen(['scp', mce_file_name,  'time-master:/home/time/Desktop/time-data/mce1/temp.%0.3i' % (a)]).wait()
            subprocess.Popen(['rm %s' % (mce_file_name)],shell=True)
            a += 1
            begin = dt.datetime.utcnow()
        else:
            print "File Doesn't Exist!"
    end = dt.datetime.utcnow()

subprocess.Popen(['rm /data/cryo/current_data/temp.*'], shell = True)
sys.exit()
