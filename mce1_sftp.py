import os
import subprocess
import time
import shutil
import sys
import datetime as dt

c = 0
sys.path.append('/home/pilot2/TIME_Software')
dir = '/data/cryo/current_data/'
print('------- Starting Data Transfer -------')
a = 0
begin = dt.datetime.utcnow()
end = dt.datetime.utcnow()
while end - begin < dt.timedelta(seconds=3):
    if os.path.exists("/data/cryo/current_data/temp.%0.3i" %(a+1)) :
        mce_file_name = '/data/cryo/current_data/temp.%0.3i' %(a)
        if a == 0:
            subprocess.Popen(['scp', '/data/cryo/current_data/temp.run', 'pilot1@time.rit.edu:/home/pilot1/Desktop/time-data/mce1/temp.run']).wait()
            #subprocess.Popen(['rm %s' % ('/data/cryo/current_data/temp.run')],shell=True)
        if os.path.exists(mce_file_name):
            subprocess.Popen(['scp', mce_file_name, 'pilot1@time.rit.edu:/home/pilot1/Desktop/time-data/mce1/temp.%0.3i' % (a)]).wait()
            subprocess.Popen(['rm %s' % (mce_file_name)],shell=True)
            #print 'File Transfered :' , mce_file_name.replace(dir,'')
            a += 1
            begin = dt.datetime.utcnow()

        else :
            print("File Doesn't Exist")
    end = dt.datetime.utcnow()
else :
    print('File Transfer Stopped')
    #subprocess.Popen(['/home/pilot2/anaconda3/bin/python /home/pilot2/TIME_Software/stop_client.py'],shell=True)
    #print('Tel Client Stopped')
    #time.sleep(2.0)
    #subprocess.Popen(['pkill -9 -f tel_sock.py'],shell=True)
    sys.exit()
