import numpy as np
from os import stat
import os, sys, subprocess
sys.path.append('/home/butler/time_analysis/py')
import timefpu.mce_data as mce_data
from . import netcdf_files as nc
import datetime as dt
from termcolor import colored
import time
import multiprocessing as mp
import config.utils as ut
from config import directory

h_shape = 0
p = 0

def netcdfdata(mce_index, queue, flags):
    """
    Purpose: read the mce0 or mce1 data
    inputs: queue - idk
            flags - idk
    outputs: None
    Calls : readdata()
    """
    # os.nice(-20)
    dir = directory.mce_dir_template % mce_index
    a = 0
    print('starting mce%i read' % mce_index)
    last_time = 0

    while not ut.mce_exit.is_set():
        mce_file_len = len(os.listdir(dir))
        mce_file_name = dir + 'temp.%0.3i' %(a)
        mce_file = os.path.exists(dir + 'temp.%0.3i' %(a+1))
        mce_run = os.path.exists(dir + 'temp.run')
        if mce_file and mce_run:
            head,h,frame_num,mce_on = readdata(mce_index, mce_file_name, flags)
            queue.put([h,head,frame_num,mce_on])
            a += 1
            subprocess.Popen(['rm %s' %(mce_file_name)], shell = True)

        time.sleep(0.01) # Rate limit

        if time.time() - last_time > 5:
            print("read_mce.netcdfdata for mce %i is still alive" % mce_index)
            # ~ print("read_mce.netcdfdata for mce %i is still alive, waiting on event %i" % (mce_index,id(ut.mce_exit)))
            last_time = time.time()

    print("read_mce.netcdfdata for mce %i is exiting" % mce_index)
    sys.stdout.flush()

    # print(colored('No More Files','red'))
    # ~ sys.exit()

# ===========================================================================================================================
def readdata(mce_index, file, flags):
    """
    Purpose: reads data from a raw mce file
    Inputs: file - mce_file
            flags - idk
    Outputs: head - header data
             h - mce data? idk
             frame_num - an array of frame numbers
             mce_on - mce on/off data
             l - idk
    Calls: mce_data.MCEFILE()
           read_header()
    """
    global h_shape
    global p

    print("Processing mce%i file %s" % (mce_index, file))
    f = mce_data.MCEFile(file)
    l = f.Read(row_col=True, unfilter='DC', all_headers=True)
    h = l.data

    # -------CHECK FOR FRAME SIZE CHANGE----------------------------------------
    # if frame size is wrong, just append zeros instead of partial array to prevent netcdf error
    # also gives a frame size error flag
    if p == 0 :
        h_shape = h.shape
        with flags.get_lock() :
            flags[3] = 0

    else :
        if (h.shape != h_shape):
            print(colored('WARNING! MCE%i Frame Size Has Changed' % (mce_index),'red'))
            sys.stdout.flush()
            with flags.get_lock():
                flags[3 + mce_index] = 11
            h = np.zeros((h_shape[0],h_shape[1],h_shape[2]))

        else :
            with flags.get_lock():
                flags[3 + mce_index] = 0
    # -------------------------------------------------------------------------
    # check for row/col that are off or reporting zeros
    mce_on = np.empty((h_shape[0],h_shape[1]),dtype=int)
    for i in range(h_shape[0]):
        for j in range(h_shape[1]):
            if np.sum(h[i][j][:]) == 0.0 :
                mce_on[i][j] = 0
            else :
                mce_on[i][j] = 1

    # send data to header to be parsed and append data
    head, frame_num = read_header(l)
    p += 1

    return head, h, frame_num, mce_on

# ===========================================================================
def read_header(l):
    """
    Purpose: reads header data from a mce file
    Inputs: l - idk
    Outputs: frame_num - an array of frame numbers
             values - an array of values from the header dictionary
    Calls: None
    """
    keys = []
    values = []
    frame_num = []
    for i in range(len(l.headers)):
        for key in sorted(l.headers[i].keys()):
            value = l.headers[i][key]
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
                # ~ print('sync num', value)
            # ~ if key == 'frame_counter':
                # ~ print('frame num',value)
            value = int(value)
            values.append(value)
    values = np.asarray(values)
    sys.stdout.flush()
    return values, frame_num
