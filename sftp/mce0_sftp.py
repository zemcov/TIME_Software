import os
import subprocess
import time
import shutil
import sys
import datetime as dt

def main():
    a = 0
    print '----- Starting MCE0 Data Transfer -----'
    begin = dt.datetime.utcnow()
    end = dt.datetime.utcnow()
    while end - begin < dt.timedelta(seconds = 3):
        if os.path.exists("/data/cryo/current_data/temp.%0.3i" %(a+1)) #wait to read new file until old file is complete
            mce_file_name = '/data/cryo/current_data/temp.%0.3i' % (a)
            if a == 0:
                subprocess.Popen(['scp', '/data/cryo/current_data/temp.run',  'time-master:/home/time/Desktop/time-data/mce1/temp.run']).wait()
                subprocess.Popen(['rm %s' % ('/data/cryo/current_data/temp.run')],shell=True)
            if os.path.exists(mce_file_name)
            subprocess.Popen(['scp', mce_file_name,  'time-master:/home/time/Desktop/time-data/mce1/temp.%0.3i' % (a)]).wait()
            delete_file = ['rm %s' % (mce_file_name)]
            a += 1
            begin = dt.datetime.utcnow()
            else:
                print "File Doesn't Exist!"
        end = dt.datetime.utcnow()

    else :
        print 'SFTP0 Stopped'
        subprocess.Popen(['rm /data/cryo/current_data/temp*'],shell=True)
        subprocess.Popen(["ssh -t time@time-master.caltech.edu 'pkill -f /home/time/time-software/main/read_files.py'"],shell=True)
        print 'File Read Stopped'
        sys.exit()


if __name__ == '__main__':
    main()
