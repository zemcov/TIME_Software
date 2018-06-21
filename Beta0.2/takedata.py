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


def takedata(a, ch, n_files, frameperfile, mce):
    #print('Hello!')

    #nc.initglobal()
    a -= 1
    st.a = a
    #nc.new_file(st.n, frameperfile)
    y = []
    allgraphdata = []
    while True:

        if a < 10 : # create a check so we know the file is there and has the right name
            mce_file_name = "/data/cryo/current_data/temp.00%i" %(a)
            if a == 9:
                mce_file = os.path.exists("/data/cryo/current_data/temp.0%i"%(a+1))
            else:
                mce_file = os.path.exists("/data/cryo/current_data/temp.00%i" %(a+1)) #wait to read new file until old file is complete
            if mce_file:
                print(len(os.listdir("/data/cryo/current_data")) - 2 - n_files)
                for i in range(len(os.listdir("/data/cryo/current_data")) - 2 - n_files):
                    print('Checking for directory files...')
                    if a < 10:
                        mce_file_name = "/data/cryo/current_data/temp.00%i" %(a)
                    else:
                        mce_file_name = "/data/cryo/current_data/temp.0%i" %(a)
                    a = a + 1
                    st.a = a
                    f = mce_data.SmallMCEFile(mce_file_name)
                    header = read_header(f)
                    z, mce = readdata(f, mce_file_name, frameperfile, mce, header)
                    graphdata = readgraph(y, f, mce_file_name, a, ch)
                    allgraphdata.append(graphdata)
                break
            else:
                #continue
                pass

        elif a >= 10 and a < 100 :
            mce_file_name = "/data/cryo/current_data/temp.0%i"%(a)
            if a == 99:
                mce_file = os.path.exists("/data/cryo/current_data/temp.%i"%(a+1))
            else:
                mce_file = os.path.exists("/data/cryo/current_data/temp.0%i"%(a+1))
            if mce_file:
                print(len(os.listdir("/data/cryo/current_data")) - 2 - n_files)
                for i in range(len(os.listdir("/data/cryo/current_data")) - 2 - n_files):
                    if a < 100:
                        mce_file_name = "/data/cryo/current_data/temp.0%i" %(a)
                    else:
                        mce_file_name = "/data/cryo/current_data/temp.%i" %(a)
                    a = a + 1
                    st.a = a
                    f = mce_data.SmallMCEFile(mce_file_name)
                    header = read_header(f)
                    z, mce = readdata(f, mce_file_name, frameperfile, mce, header)
                    graphdata = readgraph(y, f, mce_file_name, a, ch)
                    allgraphdata.append(graphdata)
                break
            else:
                #continue
                pass

        elif a >= 100 :
            mce_file_name = "/data/cryo/current_data/temp.%i"%(a)
            mce_file = os.path.exists("/data/cryo/current_data/temp.%i"%(a+1))
            if mce_file:
                print(len(os.listdir("/data/cryo/current_data")) - 2 - n_files)
                for i in range(len(os.listdir("/data/cryo/current_data")) - 2 - n_files):
                    mce_file_name = "/data/cryo/current_data/temp.%i" %(a)
                    a = a + 1
                    st.a = a
                    f = mce_data.SmallMCEFile(mce_file_name)
                    header = read_header(f)
                    z, mce = readdata(f, mce_file_name, frameperfile, mce, header)
                    graphdata = readgraph(y, f, mce_file_name, a, ch)
                    allgraphdata.append(graphdata)
                break
            else:
                #continue
                pass

    #nc.new_file(st.n, frameperfile)
    return z, allgraphdata, mce

def readdata(f, mce_file_name, frameperfile, mce, head):
    h = f.Read(row_col=True, unfilter='DC').data
    #delete_file = ["rm %s" %(mce_file_name)] #to keep temp files from piling up in memory
    #subprocess.Popen(delete_file,shell=True)
    #print(h.shape)
    #print(np.std(h[7][7][:]))
    #d = np.array([[ [] for i in range(8)] for j in range(41)])
    d = np.empty([h.shape[0],h.shape[1]],dtype=float)
    for b in range(h.shape[0]):
        for c in range(h.shape[1]):
            d[b][c] = (np.std(h[b][c][:],dtype=float))

    mce = nc.new_file(st.n, h.shape, head)
    if os.stat("tempfiles/gui_data_test{n}.nc".format(n=st.n)).st_size < 20 * 10**6: # of bytes here
        nc.data(h,d,st.n,st.a,head)
    else:
        st.n = st.n + 1
        #mce = 'tempfiles/gui_data_test%s.nc' % (n - 1)
        mce.close()
        print('----------New File----------')
        mce = nc.new_file(st.n, frameperfile, head)
        nc.data(h,d,st.n,st.a,head)

    z = ([[d[0][0], d[0][1], d[0][2], d[0][3], d[0][4], d[0][5], d[0][6], d[0][7]],
        [d[1][0], d[1][1], d[1][2], d[1][3], d[1][4], d[1][5], d[1][6], d[1][7]],
        [d[2][0], d[2][1], d[2][2], d[2][3], d[2][4], d[2][5], d[2][6], d[2][7]],
        [d[3][0], d[3][1], d[3][2], d[3][3], d[3][4], d[3][5], d[3][6], d[3][7]],
        [d[4][0], d[4][1], d[4][2], d[4][3], d[4][4], d[4][5], d[4][6], d[4][7]],
        [d[5][0], d[5][1], d[5][2], d[5][3], d[5][4], d[5][5], d[5][6], d[5][7]],
        [d[6][0], d[6][1], d[6][2], d[6][3], d[6][4], d[6][5], d[6][6], d[6][7]],
        [d[7][0], d[7][1], d[7][2], d[7][3], d[7][4], d[7][5], d[7][6], d[7][7]],
        [d[8][0], d[8][1], d[8][2], d[8][3], d[8][4], d[8][5], d[8][6], d[8][7]],
        [d[9][0], d[9][1], d[9][2], d[9][3], d[9][4], d[9][5], d[9][6], d[9][7]],
        [d[10][0], d[10][1], d[10][2], d[10][3], d[10][4], d[10][5], d[10][6], d[10][7]],
        [d[11][0], d[11][1], d[11][2], d[11][3], d[11][4], d[11][5], d[11][6], d[11][7]],
   	    [d[12][0], d[12][1], d[12][2], d[12][3], d[12][4], d[12][5], d[12][6], d[12][7]],
        [d[13][0], d[13][1], d[13][2], d[13][3], d[13][4], d[13][5], d[13][6], d[13][7]],
        [d[14][0], d[14][1], d[14][2], d[14][3], d[14][4], d[14][5], d[14][6], d[14][7]],
        [d[15][0], d[15][1], d[15][2], d[15][3], d[15][4], d[15][5], d[15][6], d[15][7]],
        [d[16][0], d[16][1], d[16][2], d[16][3], d[16][4], d[16][5], d[16][6], d[16][7]],
        [d[17][0], d[17][1], d[17][2], d[17][3], d[17][4], d[17][5], d[17][6], d[17][7]],
        [d[18][0], d[18][1], d[18][2], d[18][3], d[18][4], d[18][5], d[18][6], d[18][7]],
        [d[19][0], d[19][1], d[19][2], d[19][3], d[19][4], d[19][5], d[19][6], d[19][7]],
   	    [d[23][0], d[23][1], d[23][2], d[23][3], d[23][4], d[23][5], d[23][6], d[23][7]],
   	    [d[21][0], d[21][1], d[21][2], d[21][3], d[21][4], d[21][5], d[21][6], d[21][7]],
        [d[22][0], d[22][1], d[22][2], d[22][3], d[22][4], d[22][5], d[22][6], d[22][7]],
        [d[23][0], d[23][1], d[23][2], d[23][3], d[23][4], d[23][5], d[23][6], d[23][7]],
        [d[24][0], d[24][1], d[24][2], d[24][3], d[24][4], d[24][5], d[24][6], d[24][7]],
        [d[25][0], d[25][1], d[25][2], d[25][3], d[25][4], d[25][5], d[25][6], d[25][7]],
        [d[26][0], d[26][1], d[26][2], d[26][3], d[26][4], d[26][5], d[26][6], d[26][7]],
   	    [d[27][0], d[27][1], d[27][2], d[27][3], d[27][4], d[27][5], d[27][6], d[27][7]],
        [d[28][0], d[28][1], d[28][2], d[28][3], d[28][4], d[28][5], d[28][6], d[28][7]],
        [d[29][0], d[29][1], d[29][2], d[29][3], d[29][4], d[29][5], d[29][6], d[29][7]],
        [d[30][0], d[30][1], d[30][2], d[30][3], d[30][4], d[30][5], d[30][6], d[30][7]],
        [d[31][0], d[31][1], d[31][2], d[31][3], d[31][4], d[31][5], d[31][6], d[31][7]]])

    #filename = 'tempfiles/tempzdata.txt'
    #tempfile = open(filename, 'w')

    #print('Z:',z)

    #for x in range(h.shape[0]-1):
    #    for y in range(h.shape[1]-1):
    #        tempfile.write(str(z[x][y])+' ')
    #    tempfile.write('\n')

    #tempfile.close()
    #time.sleep(1.0)
    return z, mce

def readgraph(y, f, mce_file_name, a, ch):
    h = f.Read(row_col=True, unfilter='DC').data
    delete_file = ["rm %s" %(mce_file_name)] #to keep temp files from piling up in memory
    subprocess.Popen(delete_file,shell=True)

    #chfile = open('tempfiles/tempchannel.txt', 'r')
    #ch = int(chfile.read().strip())
    #print(ch)

    d = h[:,ch - 1]
    #print(d[0:10])
    y.append(np.reshape(h[:,ch - 1],d.shape[0]*d.shape[1])) #should output every row, and only 1 channel or column for all frame data
    #print(y[len(y) - 1])
    #print(len(y))
    #print(len(y[len(y) - 1]))

    #print('takedata', a)
    #filename = 'tempfiles/tempgraphdata%s.txt'%(a % 1)
    #tempfile = open(filename, 'w')

    #tempfile.write(str(ch) + '\n')

    #tempfile.write(str(a) + '\n')

    newy = []

    for j in range(0, d.shape[0]*d.shape[1]-1, 32):
        #tempfile.write(str(y[len(y)-1][j])+' ')
        newy.append(y[len(y)-1][j])
    #tempfile.close()


    #oldtempfile = 'tempfiles/tempgraphdata%s.txt'%(a - 10)
    #deletetemp = ["rm %s" %(oldtempfile)] #to keep temp files from piling up in memory
    #subprocess.Popen(deletetemp,shell=True)

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
    # keys,values = zip(*f.header.items())
    keys = np.asarray(keys,dtype=object)
    values = np.asarray(values,dtype=object)
    head = np.array((keys,values)).T
    return head

if __name__ == "__main__":
    #takedata(int(sys.argv[1]))
    takedata(1, 1)
