# this is for transferring housekeeping data files to the command computer
import os
import subprocess
import time
import shutil
import sys
import datetime as dt
import fnmatch
from termcolor import colored

# sys.stdout = os.fdopen(sys.stdout.fileno(), 'w', 1) # line buffering
a = 0
dir = '/data/hk/omnilog/'
print(colored('Starting HK File Transfer','green'))

while True:
    if a == 0 :
        files = [dir + x for x in os.listdir(dir) if (x.startswith("omnilog") and x.endswith('.gz'))]
        hk_file = max(files, key = os.path.getctime)
        a = int(hk_file.replace(dir,'').replace('omnilog.','').replace('.txt.gz',''))
        print(colored('HK starting file = %i' %(a),'green'))
        a = a + 1
    else :
        if os.path.exists(dir + "omnilog.%i.txt.gz" %(a+1)) : #wait to read new file until old file is complete
            file_name = dir + 'omnilog.%i.txt.gz' % (a)
            if os.path.exists(file_name) :
                subprocess.Popen(['scp', file_name,  'time_user@time-rit:/home/time_user/Desktop/time-data/hk/omnilog.%i.txt.gz' % (a)]).wait()
                print(colored('HK File Transfered : %s' %(file_name),'magenta'))
                a = a + 1
            else:
                print("HK File Doesn't Exist!")
