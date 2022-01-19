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
dir = '/data/hk/syncframes/'
print(colored('Starting HK File Transfer','green'))

while True:
    if a == 0 :
        files = [dir + x for x in os.listdir(dir) if (x.startswith("syncframes") and x.endswith('.npy'))]
        hk_file = max(files, key = os.path.getctime)
        a = int(hk_file.replace(dir,'').replace('syncframes.','').replace('.npy',''))
        print(colored('HK starting file = %i' %(a),'green'))
        a = a + 100
    else :
        if os.path.exists(dir + "syncframes.%i.npy" %(a+100)) : #wait to read new file until old file is complete
            file_name = dir + 'syncframes.%i.npy' % (a)
            if os.path.exists(file_name) :
                subprocess.Popen(['scp', file_name,  'time@time-master:/data/hk/syncframes/syncframes.%i.npy' % (a)]).wait()
                # print(colored('HK File Transfered : %s' %(file_name),'magenta'))
                a = a + 100
            else:
                print("HK File Doesn't Exist!")
