# this parses telescope data files
import numpy as np
import utils as ut
import os, subprocess, sys
from termcolor import colored
import time
import directory

def loop_files(queue3):
    """
    Purpose: Sends telescope data to append_data.py for storage into file
    Inputs : queue3
    Outputs: None
    Calls: queue3.send()
    """
    # os.nice(-20)
    dir = directory.temp_dir
    mega_tel = []

    while True :

        files = [dir + x for x in os.listdir(dir) if x.startswith("tele_packet")]
        if os.path.isfile(dir + 'tele_packet_off1.npy') :
            # print('tele_packet_off1.npy')
            tel_data = np.zeros((20,21))
            queue3.send(tel_data)
            continue

        if len(files) != 0 : # check for at least 2 files to exist
            tel_file = max(files, key = os.path.getctime) # grab the oldest of the unparsed files
            a = int(tel_file.replace(dir,'').replace('tele_packet','').replace('.npy',''))
            print(colored('TEL starting file = %i' %(a),'green'))
            sys.stdout.flush()
            break

        else :
            time.sleep(0.01)

    while not ut.tel_exit.is_set():
        if os.path.exists(dir + 'tele_packet%i.npy' %(a+1)) : #wait to read new file until old file is complete
            tele_file = (dir + 'tele_packet%i.npy' %(a))
            data = np.load(tele_file)
            queue3.send(data)
            os.remove(tele_file)
            a += 1
        else :
            time.sleep(0.01)
