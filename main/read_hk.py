import time as t
import gzip, os, sys, subprocess
import datetime as dt
from termcolor import colored
import numpy as np
import config.utils as ut
from config import directory

class HK_Reader:

    def __init__(self,offset):
        self.dir = directory.hk_dir
        self.n = 0
        self.offset = offset
        self.sync_num_base = 0

    def loop_files(self,queue3):

        while True : #force it to wait until files exist before continuing
            files = [self.dir + x for x in os.listdir(self.dir) if x.startswith("syncframes")]
            if len(files) != 0 :
                hk_file = min(files, key = os.path.getctime) # grab the oldest of the unparsed files
                a = int(hk_file.replace(self.dir,'').replace('syncframes.','').replace('.npy',''))
                self.sync_num_base = a
                print(colored('HK starting file = %i' %(a),'green'))
                sys.stdout.flush()
                break
            else :
                t.sleep(0.05)

        while not ut.mce_exit.is_set():
            if os.path.exists(self.dir + "syncframes.%i.npy" %(a+100)): #wait to read new file until old file is complete
                hk_file = self.dir + 'syncframes.%i.npy' % (a)
                a += 100
                self.sync_num_base = a
                mega_hk, time_tuple = self.hk_read(hk_file)
                queue3.send([mega_hk,time_tuple])
                subprocess.Popen(['rm %s' %(hk_file)], shell=True)
                self.n += 1
            else :
                t.sleep(0.05)

        sys.exit()

    def hk_read(self,hk):
        ntp_times = []
        sync_times = []

        # Load in the array indexed (sync_num_offset, sensor_index), usually with shape (100, 256)
        data = np.load(hk)

        new_sync_offset = ut.timing(data[0][0],self.sync_num_base)
        if self.offset.value == 0.0 or self.offset.value != new_sync_offset:
            with self.offset.get_lock():
                self.offset.value = new_sync_offset
                print(colored('Offset: %s , %s' %(self.offset.value),'red'))
                sys.stdout.flush()

        # grab network time array and sync time array
        for sync_num_offset in range(data.shape[0]):
                ntp_times.append(data[sync_num_offset][0])
                print(colored(('len of ntp times : ', len(ntp_times)),'magenta'))
                sync_times.append(self.sync_num_base + sync_num_offset)

        return data,[ntp_times,sync_nums]
