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

def netcdfdata(q_in,q_out):
    dir = '/home/time/Desktop/time-data/mce1/'
    while not ut.mce_exit.is_set():
        mce_file = len(os.listdir(dir))
        files = [dir + x for x in os.listdir(dir) if (x.startswith("temp") and not x.endswith('.run'))]

        if mce_file > 1 : # we never remove temp.run
            print(mce_file,len(files))
            for i in range(mce_file - 1):
                head_new, data_new, frame_new = self.readdata(files[i])
            data_old,head_old = q_in.get()
            data_new.append(data_old)
            head_new.append(head_new)
            print(len(data_new,head_new,frame_new)
            q_out.put(data_new, head_new, frame_new)

        else :
            pass
            print("Waiting for files....")

    print(colored('No More Files','red'))
    sys.exit()

# ===========================================================================================================================
def readdata(file):
    global h_shape
    f = mce_data.SmallMCEFile(file)
    h = f.Read(row_col=True, unfilter='DC').data

    # -------CHECK FOR FRAME SIZE CHANGE----------------------------------------
    # if frame size is wrong, just append zeros instead of partial array to prevent netcdf error
    # also gives a frame size error flag
    if ut.p == 0 :
        h_shape = h.shape
        ut.flags.append(0)

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
    head, frame_num = self.read_header(f)
    ut.p += 1
    # remove the parsed file from the directory
    subprocess.Popen(['rm %s' %(file)], shell=True)

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
    return values, frame_num
