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
import read_hk

class Time_Files:

    def __init__(self):
        self.b = 0
        self.data3, queue3 = mp.Pipe()
        self.p3 = mp.Process(target=read_hk.HK_Reader().loop_files , args=(queue3,))
        self.p3.start()

    def retrieve(self):
        while not ut.mce_exit.is_set():
            data3 = self.data3.recv()
            self.hk = data3[0] # n * (3,215)
            self.offset = data3[1]
            # if self.offset != 0 :
            #     self.parse_arrays()
            #     self.append_hk_data()
            # else :
            #     print(colored('data append skipped!','red'))

        self.p3.join()
        self.p3.close()
        sys.exit()

    def parse_arrays(self):

        # # Append HK data to correct frame matching MCE timestream ---------------------------------
        self.hk_data = [0]*int(ut.german_freq) # give it the same number of frames as mce data files

        # if len(self.hk) < 100 :
        #     filler = np.zeros((3,100))
        #     for i in range(len(self.hk)):
        #         self.hk_data.append(self.hk[i])
        #     for i in range(int(ut.german_freq) - len(self.hk)):
        #         self.hk_data.append(filler)
        #
        # print(len(self.hk_data[0]),len(self.hk_data[0][0]))

        # ------------------------------------------------------------------------------------------
        return

# ============================================================================================================================
    def append_hk_data(self):
        netcdfdir = '/home/time/Desktop/time-data/netcdffiles'
        if self.b == 0: # if it's the first file, make a new netcdf file
            self.filestarttime = dt.datetime.utcnow()
            self.filestarttime = self.filestarttime.isoformat()
            print(colored('------------ New HK File -------------','green'))
            hk = hnc.new_file(self.h1.shape, self.filestarttime)
            self.ncfile = netcdfdir + "/raw_hk_%s.nc" %(self.filestarttime)

            hnc.data_append(self.ncfile, self.b, self.hk)
            self.b = 1

        # elif os.stat(netcdfdir + "/raw_%s.nc" % (self.filestarttime)).st_size >= 20 * 10**6:
        elif self.b % 100 == 0 :
            # if it's a full file, make a new netcdf file
            print(colored('----------- New HK File ------------','green'))
            self.filestarttime = dt.datetime.utcnow()
            self.filestarttime = self.filestarttime.isoformat()
            hk = hnc.new_file(self.h1.shape, self.filestarttime)
            self.ncfile = netcdfdir + "/raw_hk_%s.nc" %(self.filestarttime)

            hnc.data_append(self.ncfile, self.b, self.hk)

        else: # if everything is okay, append data to the file
            hnc.data_append(self.ncfile, self.b, self.hk)

        # have the counter incremement for every append
        self.b += 1
        return
