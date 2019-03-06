import numpy as np
from os import stat
import os, sys, mce_data_jon, subprocess
import netcdf_files as nc
import datetime as dt
from termcolor import colored
import time as TIME
from multiprocessing import Pipe
import multiprocessing as mp
import utils as ut

h_shape = 0
p = 0

def netcdfdata(queue1):
    dir = '/home/time/Desktop/time-data/mce1/'
    a = 1
    while not ut.mce_exit.is_set():
        mce_file_len = len(os.listdir(dir))
        mce_file_name = dir + 'temp.%0.3i' %(a)
        mce_file = os.path.exists(dir + 'temp.%0.3i' %(a+1))

        if mce_file:
            print('MCE0:',mce_file_name, mce_file_len)
            head,h,frame_num = readdata(mce_file_name)
            queue1.send([h,head,frame_num])
            a += 1
            # subprocess.Popen(['rm %s' %(mce_file_name)], shell = True)

        else :
            pass

    print(colored('No More Files','red'))
    sys.exit()

# ===========================================================================================================================
def readdata(file):
    global h_shape
    global p
    f = mce_data_jon.MCEFile(file)
    l = f.Read(row_col=True, unfilter='DC', all_headers=True)
    h = l.data

    # -------CHECK FOR FRAME SIZE CHANGE----------------------------------------
    # if frame size is wrong, just append zeros instead of partial array to prevent netcdf error
    # also gives a frame size error flag
    if p == 0 :
        h_shape = h.shape
        ut.flags[3] = 0

    else :
        if (h.shape != h_shape):
            print(colored('WARNING! MCE0 Frame Size Has Changed','red'))
            ut.flags[3] = 11
            h = np.zeros((h_shape[0],h_shape[1],h_shape[2]))

        else :
            ut.flags[3] = 0
            print(ut.flags)
    # -------------------------------------------------------------------------
    # send data to header to be parsed and append data
    head, frame_num = read_header(l)
    p += 1

    return head, h, frame_num

# ===========================================================================
def read_header(l):
    keys = []
    values = []
    frame_num = []

    for i in range(len(l.headers)):
        for key,value in l.headers[i].items():
            if key == '_rc_present':
                for i in range(len(value)):
                    if value[i] == True:
                        value[i] = '1'
                    elif value[i] == False:
                        value[i] = '0'
                    else:
                        print("I don't know what I am...")
                value = ''.join(map(str,value))
            if key == 'sync_box_num' :
                frame_num.append(value)
            value = int(value)
            values.append(value)
    values = np.asarray(values)
    return values, frame_num
