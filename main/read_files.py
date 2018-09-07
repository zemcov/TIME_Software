import numpy as np
from os import stat
import os
import sys
import mce_data
import netcdf as nc
import subprocess
import datetime

def netcdfdata(rc):
    print('HELLO!')
    #n_files = len(os.listdir("/data/cryo/current_data"))
    a = 0
    mcea = 0
    mce = 1
    n = 0
    n_files = 8
    filestarttime = 0
    mcea = subprocess.Popen(['ssh -T time@time-mce-0.caltech.edu python /home/time/time-software/sftp/mce1_sftp.py %s %s' % (a, n_files)], shell=True)
    while True:
        #mce_file_name = "/data/cryo/current_data/temp.%0.3i" %(a)
        #mce_file = os.path.exists("/data/cryo/current_data/temp.%0.3i" %(a+1)) #wait to read new file until old file is complete
        #if mce_file:
            #print('NETCDF IS WORKING')
            #print(len(os.listdir("/data/cryo/current_data")) - 2 - n_files)
        
        mce_file = os.path.exists('/home/time/Desktop/time-data/mce1/temp.%0.3i' %(a+1))
        #print('/home/time/Desktop/time-data/mce1/temp.%0.3i' %(a+1))
        if mce_file:
            #print(len(os.listdir("/home/time/Desktop/time-data/mce1")) - 2)
            for i in range(len(os.listdir("/home/time/Desktop/time-data/mce1")) - 3):
                print('netcdf: %s' % (a))
                mce_file_name = '/home/time/Desktop/time-data/mce1/temp.%0.3i' %(a)
                a = a + 1
                f = mce_data.SmallMCEFile(mce_file_name)
                header = read_header(f)
                mce, n, filestarttime = readdata(f, mce_file_name, mce, header, n, a, filestarttime, rc)
                mce_file = os.path.exists('/home/time/Desktop/time-data/mce1/temp.%0.3i' %(a+1))
            #else:
            #    pass
        if os.path.exists('tempfiles/stop.txt'):
            subprocess.call(["ssh -T time@time-mce-0.caltech.edu /usr/mce/bin/mce_cmd '-x stop rcs ret_dat'"], shell=True)
            subprocess.call(['ssh -T time@time-mce-0.caltech.edu "rm /data/cryo/current_data/temp.*"'], shell=True)
            subprocess.call(['rm /home/time/Desktop/time-data/mce1/temp.*'], shell=True)
            sys.exit()


def readdata(f, mce_file_name, mce, head, n, a, filestarttime, rc):
    h = f.Read(row_col=True, unfilter='DC').data
    d = np.empty([h.shape[0],h.shape[1]],dtype=float)
    for b in range(h.shape[0]):
        for c in range(h.shape[1]):
            d[b][c] = (np.std(h[b][c][:],dtype=float))
    if a > 1:
        old_mce_file_name = '/home/time/Desktop/time-data/mce1/temp.%0.3i' %(a - 2)
        subprocess.Popen(['rm %s' % (old_mce_file_name)], shell=True)

    tempfiledir = os.path.expanduser('/home/time/Desktop/time-data/netcdffiles')
    if a == 1:
        filestarttime = datetime.datetime.utcnow()
        filestarttime = filestarttime.isoformat()
        mce = nc.new_file(n, h.shape, head, filestarttime)
    elif os.stat(tempfiledir + "/mce_netcdf-%s.nc" % (filestarttime)).st_size < 20 * 10**6: # of bytes here
        if rc == 's' :
            nc.data_all(h,d,n,a,head)
        else :
            nc.data(h,d,n,a,head)
    else:
        n = n + 1
        mce.close()
        print('----------New File----------')
        filestarttime = datetime.datetime.utcnow()
        filestarttime = filestarttime.isoformat()
        mce = nc.new_file(n, h.shape, head, filestarttime)
        if rc == 's' :
            nc.data_all(h,d,n,a,head)
        else :
            nc.data(h,d,n,a,head)
    return mce, n, filestarttime


def read_header(f):
    keys = []
    values = []
    for key,value in f.header.items():
        if key == '_rc_present':
            for i in range(len(value)):
                if value[i] == True:
                    value[i] = "1"
                elif value[i] == False:
                    value[i] = "0"
                else:
                    print("I don't know what I am...")
            value = ''.join(map(str,value))
        value = str(value)
        keys.append(key)
        values.append(value)
    keys = np.asarray(keys,dtype=object)
    values = np.asarray(values,dtype=object)
    head = np.array((keys,values)).T
    return head

if __name__ == '__main__':
    netcdfdata(sys.argv[1])
