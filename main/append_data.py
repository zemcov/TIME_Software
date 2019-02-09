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
import read_mce0, read_mce1, read_hk

class Time_Files:

    def __init__(self):
        self.a = 0
        self.p = 0
        self.data1, queue1 = mp.Pipe()
        self.data2, queue2 = mp.Pipe()
        self.data3, queue3 = mp.Pipe()
        self.p1 = mp.Process(target=read_mce0.netcdfdata , args=(queue1,))
        self.p2 = mp.Process(target=read_mce1.netcdfdata , args=(queue2,))
        self.p3 = mp.Process(target=read_hk.loop_files , args=(queue3,))
        self.p1.start()
        self.p2.start()
        self.p3.start()

    def retrieve(self,queue):
        while not ut.mce_exit.is_set():
            data1 = self.data1.recv()
            data2 = self.data2.recv()
            data3 = self.data3.recv()
            self.h1 = data1[0]
            self.h2 = data2[0]
            self.head1 = data1[1]
            self.head2 = data2[1]
            self.sync1 = data1[2]
            self.sync2 = data2[2]
            # self.hk = data3 # n * (3,215)
            queue.send([self.h1,self.h2,self.p])
            print(colored('Offset: %s' %(ut.offset),'green'))
            if ut.offset != 0 :
                self.parse_arrays()
                self.append_data()
            else :
                print(colored('data append skipped!','red'))
            self.p += 1

        # self.p1.join()
        # self.p2.join()
        # self.p1.close()
        # self.p2.close()


    def parse_arrays(self):
        # self.hold_h1 = []
        # self.hold_h2 = []
        print()
        print(colored('MCE0 Sync: %s' %(self.sync1[0]),'green'))
        print(colored('MCE1 Sync: %s' %(self.sync1[0]),'green'))
        # print(self.h1.shape[2],self.h2.shape[2])
        # check to make sure that the frame sync numbers are lining up
        if self.sync1[0] == self.sync2[0]:
            print(colored('normal sync nums','green'))
            # self.hold_h1 = self.h1
            # self.hold_h2 = self.h2
            # print(self.hold_h1.shape,self.hold_h2.shape)

        else :
            print(colored('mismatched sync nums!!!','red'))
            # self.hold_h1 = self.h1
            # self.hold_h2 = self.h2
            # for i in range(self.h1.shape[2]):
            #     if int(self.sync1[i]) > int(self.sync2[i]):
            #         start_frame = self.sync1[i]
            #         for i in range(self.h1.shape[2]):
            #             if self.sync2[i] < start_frame:
            #                 continue
            #             else :
            #                 self.h2 = self.h2[i:]
            #                 if self.h2.shape[2] < ut.frameperfile:
            #                     empty = [[0 for col in range(self.h1.shape[0])] for row in range(self.h1.shape[1])]
            #                     self.hold_h1.append(self.h1[i] + (empty*(ut.frameperfile - len(self.h1)))) # keeps the last two dimensions as all, same as self.h1[i,:,:]
            #                     self.hold_h2.append(self.h2[i] + (empty*(ut.frameperfile - len(self.h1))))
            #                     break
            #
            #
            #     elif int(self.sync2[i]) > (self.sync1[i]):
            #         start_frame = self.sync2[i]
            #         for i in range(self.h1.shape[2]):
            #             if self.sync1[i] < start_frame:
            #                 continue
            #             else :
            #                 self.h1 = self.h1[i:]
            #                 if self.h1.shape[2] < ut.frameperfile:
            #                     empty = [[0 for col in range(self.h1.shape[0])] for row in range(self.h1.shape[1])]
            #                     self.hold_h1.append(self.h1[i] + (empty*(ut.frameperfile - len(self.h1))))
            #                     self.hold_h2.append(self.h2[i] + (empty*(ut.frameperfile - len(self.h1))))
            #                     break


        timer1_start = time.time()
        # Append HK data to correct frame matching MCE timestream ---------------------------------
        utc_time = ut.sync_to_utc(self.sync1)
        self.utc = zip(utc_time,self.sync1) # tuples of (utc,sync)
        self.hk_data = [0]*ut.german_freq # give it the same number of frames as mce data file
        for i in range(len(utc_time)) :
            for j in range(len(self.hk)):
                if self.hk[j][0][0] == utc_time[i] : # check if timestamps match
                    self.hk_data[i] = self.hk[j]
        # ------------------------------------------------------------------------------------------
        timer1_stop = time.time()
        print(colored('Total Time: %s' %(timer1_stop - timer1_start),'red'))
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

            nc.data_append(self.ncfile, self.a, ut.flags, self.utc, self.head1, self.head2, self.h1, self.h2, self.hk_data)
            self.a = 1

        elif os.stat(netcdfdir + "/raw_%s.nc" % (self.filestarttime)).st_size >= 20 * 10**6:
            # if it's a full file, make a new netcdf file
            print(colored('----------- New File ------------','green'))
            self.filestarttime = dt.datetime.utcnow()
            self.filestarttime = self.filestarttime.isoformat()
            mce = nc.new_file(self.h1.shape, self.filestarttime)
            self.ncfile = netcdfdir + "/raw_%s.nc" %(self.filestarttime)

            nc.data_append(self.ncfile, self.a, ut.flags, self.utc, self.head1, self.head2, self.h1, self.h2, self.hk_data)

        else: # if everything is okay, append data to the file
            nc.data_append(self.ncfile, self.a, ut.flags, self.utc, self.head2, self.head2, self.h1, self.h2, self.hk_data)

        # have the counter incremement for every append, not just hk
        self.a += 1
        return
