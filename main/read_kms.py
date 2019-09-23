# this parses kms data
import numpy as np
import subprocess, os, sys, time
import directory
import utils as ut
from termcolor import colored

dir = directory.temp_dir

def loop_files(queue4):
    """
    Purpose: Sends data to append_data.py for storage in file
    Inputs: queue4
    Outputs: None
    Calls: queue4.send()
    """
    dir = directory.temp_dir
    mega_kms = []

    while True :

        files = [dir + x for x in os.listdir(dir) if x.startswith("kms_packet")]

        if len(files) != 0 : # check for at least 2 files to exist
            tel_file = max(files, key = os.path.getctime) # grab the oldest of the unparsed files
            a = int(tel_file.replace(dir,'').replace('kms_packet','').replace('.npy',''))
            print(colored('KMS starting file = %i' %(a),'green'))
            sys.stdout.flush()
            break

        else :
            time.sleep(0.01)

    while not ut.tel_exit.is_set():
        if os.path.exists(dir + 'kms_packet%i.npy' %(a+1)) : #wait to read new file until old file is complete
            kms_file = (dir + 'kms_packet%i.npy' %(a))
            data = np.load(kms_file)
            queue4.send(data)
            os.remove(kms_file)
            a += 1
            time.sleep(0.01)
        else :
            time.sleep(0.01)

    sys.exit()
