import numpy as np
from os import stat
import os
import sys
import mce_data
import netcdf as nc
import subprocess
import datetime
import time
import logging
import datetime as dt

def netcdfdata(rc):
    a = 0
    mce = 0
    n = 0
    filestarttime = 0
    old_mce_file = 0
    tel_size = 0
    dir = '/home/pilot1/Desktop/time-data/mce1/'
    subprocess.Popen(['ssh -T pilot2@timemce.rit.edu python /home/pilot2/TIME_Software/mce1_sftp.py'], shell=True)

    while True:
        mce_file = os.path.exists('/home/pilot1/Desktop/time-data/mce1/temp.%0.3i' %(a+1))
        if mce_file:
            files = [dir + x for x in os.listdir(dir) if (x.startswith("temp") and not x.endswith('.run'))]
            if (len(files) != 0 and mce_file != old_mce_file):
                mce_file = min(files, key = os.path.getctime)
                f = mce_data.SmallMCEFile(mce_file)
                header = read_header(f)
                mce, n, filestarttime, tel_size = readdata(f, mce_file, mce, header, n, a, filestarttime, rc, tel_size)
                print('File Read: %s' %(mce_file.replace(dir,'')))
                a = a + 1
                old_mce_file = mce_file
            else :
                subprocess.Popen(["python -c 'import /home/pilot1/TIME_Software/readteledata; readteledata.stop_sock()'"],shell=True)
                time.sleep(2.0)
                subprocess.Popen(['pkill -f /home/pilot1/TIME_Software/readteledata.py'],shell=True)
                print('Tel Server Stopped')
                sys.exit()

# ===========================================================================================================================
def readdata(f, mce_file, mce, head, n, a, filestarttime, rc, tel_size):
    h = f.Read(row_col=True, unfilter='DC').data
    d = np.empty([h.shape[0],h.shape[1]],dtype=float)
    for b in range(h.shape[0]):
        for c in range(h.shape[1]):
            d[b][c] = (np.std(h[b][c][:],dtype=float))

    subprocess.Popen(['rm %s' % (mce_file)], shell=True)
    netcdfdir = '/home/pilot1/Desktop/time-data/netcdffiles'

    pa,slew_flag,alt,az,ra,dec = np.loadtxt('tempfiles/tempteledata.txt',delimiter = ',',unpack=True)
    tel_size = len(pa)

    if n == 0:
        filestarttime = datetime.datetime.utcnow()
        filestarttime = filestarttime.isoformat()
        print('------------ New File -------------')
        mce = nc.new_file(h.shape, head, filestarttime, tel_size)
        if rc == 's' :
            nc.data_all(h,d,n,head,filestarttime)
        else :
            nc.data(h,d,n,head,filestarttime)

    elif os.stat(netcdfdir + "/mce1_%s.nc" % (filestarttime)).st_size >= 20 * 10**6:
        n = 0
        print('----------- New File ------------')
        filestarttime = datetime.datetime.utcnow()
        filestarttime = filestarttime.isoformat()
        mce = nc.new_file(h.shape, head, filestarttime, tel_size)
        if rc == 's' :
            nc.data_all(h,d,n,head,filestarttime)
        else :
            nc.data(h,d,n,head,filestarttime)

    else:
        if rc == 's' :
            nc.data_all(h,d,n,head,filestarttime)
        else :
            nc.data(h,d,n,head,filestarttime)
    n = n + 1
    return mce, n, filestarttime, tel_size

# =========================================================================================================
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
