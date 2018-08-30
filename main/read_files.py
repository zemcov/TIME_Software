import numpy as np
from os import stat
import os
import sys
import mce_data
import netcdf as nc
import subprocess
import datetime

def filetransfer(rc):
    a = 0
    mce = 1
    n = 0
    filestarttime = 0
    while True:
        subprocess.call(['ssh -T time@time-mce-0.caltech.edu python /home/time/time-software/sftp/mce1_sftp.py'], shell=True)
        mce_file = os.path.exists("/home/time/Desktop/time-data/mce1/temp.%0.3i" %(a+1))
        if mce_file:
            print("items in directory:",len(os.listdir("/home/time/Desktop/time-data/mce1")))# - 2)
            for i in range(len(os.listdir("/home/time/Desktop/time-data/mce1"))):# - 2):
                mce_file_name = "/home/time/Desktop/time-data/mce1/temp.%0.3i" %(a)
                f = mce_data.SmallMCEFile(mce_file_name)
                header = read_header(f)
                mce, n, filestarttime = readdata(f, mce_file_name, mce, header, n, a, filestarttime)
                a = a + 1
    # -----------------------------------------------------------------------------------------------------

def readdata(f, mce_file_name, mce, head, n, a, filestarttime):
    print('readdata started')
    tempfiledir = os.path.expanduser('/home/time/Desktop/time-data/netcdffiles')
    h = f.Read(row_col=True, unfilter='DC').data
    d = np.empty([h.shape[0],h.shape[1]],dtype=float)
    for b in range(h.shape[0]):
        for c in range(h.shape[1]):
            d[b][c] = (np.std(h[b][c][:],dtype=float))

    if a == 0:
        print('------- New File 0 -------')
        filestarttime = datetime.datetime.utcnow()
        filestarttime = filestarttime.isoformat()
        mce = nc.new_file(n, h.shape, head, filestarttime)
        if rc == 's' :
            print('data append')
            nc.data_all(h,d,n,a,head)
        else :
            print('data append')
            nc.data(h,d,n,a,head)

    else :
        old_mce_file_name = "/home/time/Desktop/time-data/mce1/temp.%0.3i" %(a - 1)
        subprocess.Popen(['rm %s' % (old_mce_file_name)], shell=True)
        filestarttime = datetime.datetime.utcnow()
        filestarttime = filestarttime.isoformat()
        if os.stat(tempfiledir + "/mce_netcdf-%s.nc" %(filestarttime)).st_size < 20 * 10**6: # of bytes here
            if rc == 's' :
                print('data append 1')
                nc.data_all(h,d,n,a,head)
            else :
                print('data append 2')
                nc.data(h,d,n,a,head)

        else :
            print('-------- New File --------')
            mce = nc.new_file(n, h.shape, head, filestarttime)
            if rc == 's' :
                print('data append 3')
                nc.data_all(h,d,n,a,head)
            else :
                print('data append 4')
                nc.data(h,d,n,a,head)

    # if a == 1:
    #     filestarttime = datetime.datetime.utcnow()
    #     filestarttime = filestarttime.isoformat()
    #     mce = nc.new_file(n, h.shape, head, filestarttime)
    # elif os.stat(tempfiledir + "/mce_netcdf-%s.nc" % (filestarttime)).st_size < 20 * 10**6: # of bytes here
    #     nc.data(h,d,n,a,head)
    #     #subprocess.Popen(['rm %s' % (mce_file_name)], shell=True)
    # else:
    #     n = n + 1
    #     mce.close()

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
    filetransfer(sys.argv[1])
