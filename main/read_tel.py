# this parses telescope data files
import numpy as np
import config.utils as ut
import os, subprocess, sys
from termcolor import colored
import time
from config import directory

def loop_files(queue):
    """
    Purpose: Sends telescope data to append_data.py for storage into file
    Inputs : queue
    Outputs: None
    Calls: queue.put()
    """
    # os.nice(-20)
    dir = directory.temp_dir
    mega_tel = []
    last_time = 0

    while not ut.tel_exit.is_set():
        
        time.sleep(0.01) # Rate limit
        
        if time.time() - last_time > 5:
            print("read_tel.loop_files inital loop is still alive")
            last_time = time.time()
        
        # If this file exists, the telescope is off and we should send
        # fake empty data
        if os.path.isfile(dir + 'tele_packet_off1.npy'):
            if queue.qsize() < 1: # Don't overload the queue
                print('Sending fake/empty telescope data')
                tel_data = np.zeros((20,21))
                queue.put(tel_data)
            continue

        files = [dir + x for x in os.listdir(dir) if x.startswith("tele_packet")]

        if len(files) != 0 : # check for at least 2 files to exist
            tel_file = max(files, key = os.path.getctime) # grab the oldest of the unparsed files
            a = int(tel_file.replace(dir,'').replace('tele_packet','').replace('.npy',''))
            print(colored('TEL starting file = %i' %(a),'green'))
            sys.stdout.flush()
            break 

    while not ut.tel_exit.is_set():
        
        time.sleep(0.01) # Rate limit
        
        if time.time() - last_time > 5:
            print("read_tel.loop_files main loop is still alive")
            last_time = time.time()
            
        if os.path.exists(dir + 'tele_packet%i.npy' %(a+1)) : #wait to read new file until old file is complete
            tele_file = (dir + 'tele_packet%i.npy' %(a))
            data = np.load(tele_file)
            queue.put(data)
            os.remove(tele_file)
            a += 1
            sys.stdout.flush()
            sys.stderr.flush()            
       
            
    print("read_tel.loop_files is exiting")
    sys.stdout.flush()
