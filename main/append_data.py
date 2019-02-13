import numpy as np
from os import stat
import os, sys, mce_data, subprocess
import netcdf_files as nc
import hk_netcdf_files as hnc
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
        self.data3, queue3 = mp.Pipe()
        self.data4, queue4 = mp.Pipe()
        self.p1 = mp.Process(target=read_mce0.netcdfdata , args=(queue1,))
        self.p2 = mp.Process(target=read_mce1.netcdfdata , args=(queue2,))
        self.p3 = mp.Process(target=read_tel.loop_files , args=(queue3,))
        self.p4 = mp.Process(target=read_kms.loop_files , args=(queue4,))
        self.p1.start()
        self.p2.start()
        self.p3.start()
        self.p4.start()

    def retrieve(self,queue):
        while not ut.mce_exit.is_set():

            time1 = time.time()
            data1 = self.data1.recv()
            data2 = self.data2.recv()
            self.h1 = data1[0]
            self.h2 = data2[0]
            queue.send([self.h1,self.h2,self.p])
            self.tel = self.data3.recv()
            self.kms = self.data4.recv()
            time2 = time.time()
            print('Total Time:',time2 - time1)

            self.head1 = data1[1]
            self.head2 = data2[1]
            self.sync1 = data1[2]
            self.sync2 = data2[2]


            self.parse_arrays()
            self.parse_tel()
            self.parse_kms()
            self.append_mce_data()
            self.p += 1

        self.p1.join()
        self.p2.join()
        self.p1.close()
        self.p2.close()
        sys.exit()

    def parse_tel(self):
        if self.tel[0][0] == 0.0 : # check for zeroes from self. off == True
            self.tel_data = self.tel
        else : # otherwise, parse the real data into larger array
            self.tel_data = [0] * 10
            if len(self.tel) <= 10:
                for i in range(len(self.tel)) :
                    self.tel_data[i] = self.tel[i]
            else :
                print(colored('TEL ARRAY TOO LARGE!','red'))

    def parse_kms(self):
        if self.tel[0][0] == 0.0 :
            self.kms_data = self.kms
        else :
            self.kms_data = [0] * 10
            if len(self.kms) <= 10 :
                for i in range(len(self.kms)) :
                    self.kms_data[i] = self.kms[i]
            else :
                print(colored('KMS ARRAY TOO LARGE!','red'))

    def parse_arrays(self):
        # self.hold_h1 = []
        # self.hold_h2 = []

        print(colored('MCE0 Sync: %s' %(self.sync1[0]),'green'))
        print(colored('MCE1 Sync: %s' %(self.sync2[0]),'green'))
        # check to make sure that the frame sync numbers are lining up
        # if self.sync1[0] == self.sync2[0]:
        #     print(colored('normal sync nums','green'))
            # self.hold_h1 = self.h1
            # self.hold_h2 = self.h2
            # print(self.hold_h1.shape,self.hold_h2.shape)

        # else :
        #     print(colored('mismatched sync nums!!!','red'))
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

        utc_time = ut.sync_to_utc(self.sync2)
        self.utc = zip(utc_time,self.sync2) # tuples of (utc,sync)
        return

# ============================================================================
    def append_mce_data(self):
        netcdfdir = '/home/time/Desktop/time-data/netcdffiles'
        if self.a == 0: # if it's the first file, make a new netcdf file
            self.filestarttime = dt.datetime.utcnow()
            self.filestarttime = self.filestarttime.isoformat()
            print(colored('------------ New MCE File -------------','green'))
            mce = nc.new_file(self.h1.shape, self.filestarttime)
            self.ncfile = netcdfdir + "/raw_mce_%s.nc" %(self.filestarttime)

            nc.data_append(self.ncfile, self.a, ut.flags, self.utc, self.head1, self.head2, self.h1, self.h2, self.tel_data, self.kms_data)
            self.a = 1

        # elif os.stat(netcdfdir + "/raw_mce_%s.nc" % (self.filestarttime)).st_size >= 20 * 10**6:
        elif self.a % 100 == 0 :
            # if it's a full file, make a new netcdf file
            print(colored('----------- New MCE File ------------','green'))
            self.filestarttime = dt.datetime.utcnow()
            self.filestarttime = self.filestarttime.isoformat()
            mce = nc.new_file(self.h1.shape, self.filestarttime)
            self.ncfile = netcdfdir + "/raw_mce_%s.nc" %(self.filestarttime)

            nc.data_append(self.ncfile, self.a, ut.flags, self.utc, self.head1, self.head2, self.h1, self.h2, self.tel_data, self.kms_data)

        else: # if everything is okay, append data to the file
            nc.data_append(self.ncfile, self.a, ut.flags, self.utc, self.head2, self.head2, self.h1, self.h2, self.tel_data, self.kms_data)

        # have the counter incremement for every append
        self.a += 1
        return
