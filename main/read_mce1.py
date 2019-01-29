import numpy as np
from os import stat
import os, sys, mce_data, subprocess
import netcdf_files as nc
import datetime as dt
from termcolor import colored
import time as TIME
from multiprocessing import Pipe
import multiprocessing as mp
import utils as ut

h_shape = 0
p = 0

def netcdfdata(queue2):
    dir = '/home/time/Desktop/time-data/mce2/'
    a = 0
    while not ut.mce_exit.is_set():
        mce_file_len = len(os.listdir(dir))
        # files = [dir + x for x in os.listdir(dir) if (x.startswith("temp") and not x.endswith('.run'))]
        mce_file_name = dir + 'temp.%0.3i' %(a)
        mce_file = os.path.exists(dir + 'temp.%0.3i' %(a+1))
        if mce_file:
            print('MCE1:',mce_file_name, mce_file_len)
            head,h,frame_num = readdata(mce_file_name)
            queue2.send([h,head])
            a += 1
            subprocess.Popen(['rm %s' %(mce_file_name)], shell = True)
        else :
            pass

    print(colored('No More Files','red'))
    sys.exit()

# ===========================================================================================================================
def readdata(file):
    global h_shape
    global p
    print(colored(file,'green'))
    f = mce_data.MCEFile(file)
    h = f.Read(row_col=True, unfilter='DC').data

    # -------CHECK FOR FRAME SIZE CHANGE----------------------------------------
    # if frame size is wrong, just append zeros instead of partial array to prevent netcdf error
    # also gives a frame size error flag
    if p == 0 :
        h_shape = h.shape
        ut.flags[4] = 0

    else :
        if (h.shape != h_shape):
            print(colored('WARNING! MCE1 Frame Size Has Changed','red'))
            ut.flags[4] = 11
            h = np.zeros((h_shape[0],h_shape[1],h_shape[2]))

        else :
            ut.flags[4] = 0
            print(ut.flags)
    # -------------------------------------------------------------------------
    # send data to header to be parsed and append data
    head, frame_num = read_header(f)
    p += 1
    # remove the parsed file from the directory

    return head, h, frame_num

# ===========================================================================
def read_header(f):
    keys = []
    values = []
    frame_num = []
    for key,value in f.header.items():
        if key == '_rc_present':
            for i in range(len(value)):
                if value[i] == True:
                    value[i] = '1'
                elif value[i] == False:
                    value[i] = '0'
                else:
                    print("I don't know what I am...")
            value = ''.join(map(str,value))
        if key == 'frame_counter' :
            frame_num.append(value)

        value = int(value)
        values.append(value)
    values = np.asarray(values)
    print(colored('MCE0 Frame: %s' %(frame_num),'magenta'))
    return values, frame_num
