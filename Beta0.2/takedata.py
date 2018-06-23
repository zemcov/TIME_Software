# just loading dependencies and packages
#!/usr/bin/python2.7
import numpy as np
from os import stat
import os
import sys
from subprocess import Popen, PIPE
import subprocess
import time
sys.path.append('/usr/lib/python2.7')
sys.path.append('/data/cryo/current_data')
import mce_data
#from pathlib2 import Path
import datetime
import fnmatch
import settings as st
import netcdf_trial as nc
#import pyqtgui as qg


def takedata(a, ch, n_files, frameperfile, mce, row):
    a -= 1
    st.a = a
    y = []
    allgraphdata = []
    while True:
        mce_file_name = "/data/cryo/current_data/temp.%0.3i" %(a)
        mce_file = os.path.exists("/data/cryo/current_data/temp.%0.3i" %(a+1)) #wait to read new file until old file is complete
        if mce_file:
            print(len(os.listdir("/data/cryo/current_data")) - 2 - n_files)
            for i in range(len(os.listdir("/data/cryo/current_data")) - 2 - n_files):
                a = a + 1
                st.a = a
                f = mce_data.SmallMCEFile(mce_file_name)
                header = read_header(f)
                z, mce = readdata(f, mce_file_name, frameperfile, mce, header)
                graphdata = readgraph(y, f, mce_file_name, a, ch, row)
                allgraphdata.append(graphdata)
            break
        else:
            pass
    return z, allgraphdata, mce

def readdata(f, mce_file_name, frameperfile, mce, head):
    h = f.Read(row_col=True, unfilter='DC').data
    d = np.empty([h.shape[0],h.shape[1]],dtype=float)
    for b in range(h.shape[0]):
        for c in range(h.shape[1]):
            d[b][c] = (np.std(h[b][c][:],dtype=float))

    if st.a == 1:
    	mce = nc.new_file(st.n, h.shape, head)
    if os.stat("tempfiles/gui_data_test{n}.nc".format(n=st.n)).st_size < 20 * 10**6: # of bytes here
        nc.data(h,d,st.n,st.a,head)
    else:
        st.n = st.n + 1
        #mce = 'tempfiles/gui_data_test%s.nc' % (n - 1)
        mce.close()
        print('----------New File----------')
        mce = nc.new_file(st.n, h.shape, head)
        nc.data(h,d,st.n,st.a,head)
    return d, mce

def readgraph(y, f, mce_file_name, a, ch, row):
    h = f.Read(row_col=True, unfilter='DC').data
    delete_file = ["rm %s" %(mce_file_name)] #to keep temp files from piling up in memory
    subprocess.Popen(delete_file,shell=True)
    d = h[:,ch - 1]
    y.append(np.reshape(d,d.shape[0]*d.shape[1])) #should output every row, and only 1 channel or column for all frame data
    '''
    for ch = 0, h.shape = (33,8,374), d.shape = (33,374), y.shape = (33*374,)

    can't we just do this to index the correct row of data...?
    new_array = []
    for j in range(d.shape[1]):
        new_array.append(d[row][j])
    '''
    newy = []
    for j in range(row - 1, d.shape[0]*d.shape[1], 33):
        newy.append(y[len(y)-1][j])

    print('newy: %s' % (len(newy)))
    graphdata = [a, ch, newy]
    return graphdata

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

if __name__ == "__main__":
    takedata(1, 1)
