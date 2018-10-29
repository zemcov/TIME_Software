# this is for transferring housekeeping data files to the command computer
import os
import subprocess
import time
import shutil
import sys
import datetime as dt
from termcolor import colored

sys.stdout = os.fdopen(sys.stdout.fileno(), 'w', 1) # line buffering

def main():
    a = 0
    dir = '/'
    print colored('Starting HK File Transfer','green')
    begin = dt.datetime.utcnow()
    end = dt.datetime.utcnow()
    while end - begin < dt.timedelta(seconds = 5):
        if os.path.exists(dir + "hk_temp%i" %(a+1)) : #wait to read new file until old file is complete
            file_name = dir + 'hk_temp%i' % (a)
            if os.path.exists(file_name) :
                subprocess.Popen(['scp', file_name,  'time-master:/home/time/Desktop/time-data/hk/hk_temp%i' % (a)]).wait()
                subprocess.Popen(['rm %s' % (file_name)],shell=True)
                a += 1
                begin = dt.datetime.utcnow()
            else:
                print "HK File Doesn't Exist!"
        end = dt.datetime.utcnow()

    else :
        print colored('HK SFTP Stopped','red')
        sys.exit()

if __name__ == '__main__':
    main()
