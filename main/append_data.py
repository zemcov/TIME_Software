import numpy as np
from os import stat
import os, sys, mce_data, subprocess
import netcdf_files as nc
import datetime as dt
from termcolor import colored
import time
from multiprocessing import Pipe
import multiprocessing as mp
import utils as ut
import read_mce0, read_mce1

class Time_Files:

    def __init__(self):
        self.a = 0
        self.p = 0
        self.data1, queue1 = mp.Pipe()
        self.data2, queue2 = mp.Pipe()
        self.p1 = mp.Process(target=read_mce0.netcdfdata , args=(queue1,))
        self.p2 = mp.Process(target=read_mce1.netcdfdata , args=(queue2,))
        self.p1.start()
        self.p2.start()

    def retrieve(self,queue):
        while not ut.mce_exit.is_set():
            data1 = self.data1.recv()
            data2 = self.data2.recv()
            self.h1 = data1[0]
            self.h2 = data2[0]
            self.head1 = data1[1]
            self.head2 = data2[1]
            queue.send([self.h1,self.h2,self.p])
            self.parse_arrays()
            self.p += 1

        # self.p1.join()
        # self.p2.join()
        # self.p1.close()
        # self.p2.close()

    def parse_arrays(self):
        self.rc = 'a'
        self.hold_h1 = []
        self.hold_h2 = []

        ''' for once we get the sync box working again '''
        # sync1 = [item['sync_box_num'] for item in self.h1.headers]
        # sync2 = [item['sync_box_num'] for item in self.h2.headers]
        ''' using frame counter '''

        # i = 0
        # while i <= len(self.h1):
        #     if sync1[i] > sync2[i]:
        #         start_frame = sync1[i]
        #         i += 1
        #         while i <= len(self.h1):
        #             if sync2[i] < start_frame:
        #                 i += 1
        #             else :
        #                 self.h1 = self.h1[i]
        #                 self.h2 = self.h2[i]
        #                 if len(self.h1) < ut.frameperfile:
        #                     empty = [[0 for col in range(self.h1.shape[0])] for row in range(self.h1.shape[1])]
        #                     self.hold_h1.append(self.h1[i] + (empty*(ut.frameperfile - len(self.h1)))) # keeps the last two dimensions as all, same as self.h1[i,:,:]
        #                     self.hold_h2.append(self.h2[i] + (empty*(ut.frameperfile - len(self.h1))))
        #                 # don't need else statement, because otherise the last else statement would have been triggered if the array was the right size
        #                 break
        #         break
        #
        #     elif sync2[i] > sync1[i]:
        #         start_frame = sync2[i]
        #         i += 1
        #         while i <= len(self.h1):
        #             if sync1[i] < start_frame:
        #                 i += 1
        #             else :
        #                 self.h1 = self.h1[i]
        #                 self.h2 = self.h2[i]
        #                 if len(self.h1) < ut.frameperfile:
        #                     empty = [[0 for col in range(self.h1.shape[0])] for row in range(self.h1.shape[1])]
        #                     self.hold_h1.append(self.h1[i] + (empty*(ut.frameperfile - len(self.h1))))
        #                     self.hold_h2.append(self.h2[i] + (empty*(ut.frameperfile - len(self.h1))))
        #
        #                 break
        #         break

        self.append_data()

        # self.head1 = head1[i]
        # self.head2 = head2[i]
        # self.sync1 = sync1[i]
        # self.sync2 = sync2[i]

        return

# ============================================================================
    def append_data(self):
        netcdfdir = '/home/time/Desktop/time-data/netcdffiles'
        if self.a == 0: # if it's the first file, make a new netcdf file
            self.filestarttime = dt.datetime.utcnow()
            self.filestarttime = self.filestarttime.isoformat()
            print(colored('------------ New File -------------','green'))
            mce = nc.new_file(self.h1.shape, self.filestarttime)
            self.ncfile = netcdfdir + "/raw_%s.nc" %(self.filestarttime)

            if self.rc == 'a' :
                nc.mce_append(self.ncfile, self.p, self.h1, self.h2, self.head1, self.head2, ut.flags)
            elif self.rc == 'hk':
                nc.hk_append(self.ncfile, self.n, self.time, self.data, self.name, self.tele_time)
            else :
                print(colored('Wrong RC Input!','red'))
            self.a = 1

        elif os.stat(netcdfdir + "/raw_%s.nc" % (self.filestarttime)).st_size >= 20 * 10**6:
            # if it's a full file, make a new netcdf file
            print(colored('----------- New File ------------','green'))
            self.filestarttime = dt.datetime.utcnow()
            self.filestarttime = self.filestarttime.isoformat()
            mce = nc.new_file(self.h1.shape, self.filestarttime)
            self.ncfile = netcdfdir + "/raw_%s.nc" %(self.filestarttime)

            if self.rc == 'a' :
                nc.mce_append(self.ncfile, self.p, self.h1, self.h2, self.head1, self.head2, ut.flags)
            elif self.rc == 'hk':
                nc.hk_append(self.ncfile, self.n, self.time, self.data, self.name, self.tele_time)
            else :
                print(colored('Wrong RC Input!','red'))

        else: # if everything is okay, append data to the file
            if self.rc == 'a' :
                nc.mce_append(self.ncfile, self.p, self.h1, self.h2, self.head1, self.head2, ut.flags)
            elif self.rc == 'hk':
                nc.hk_append(self.ncfile, self.n, self.time, self.data, self.name, self.tele_time)
            else :
                print(colored('Wrong RC Input!','red'))

        # have the counter incremement for every append, not just hk
        self.a += 1
        return
