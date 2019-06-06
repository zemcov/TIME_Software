import numpy as np
from os import stat
import os, sys, mce_data, subprocess, errno
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

    def __init__(self,offset):
        # os.nice(-10)
        self.b = 0
        self.start_time_stamp = 0
        self.new_time_stamp = 0
        self.k = 0
        self.i = 0
        self.j = 0
        self.time_tuple = []
        self.hk_data = np.zeros((int(ut.german_freq),3,500))
        self.offset = offset
        self.saved_array = []
        self.saved_time = 0

        self.data3, queue3 = mp.Pipe()
        self.p3 = mp.Process(target=read_hk.HK_Reader(offset = self.offset).loop_files , args=(queue3,))
        self.p3.start()
        print(colored('HK Has Started'),'red')

    def retrieve(self,dir):
        # os.nice(-20)
        while not ut.mce_exit.is_set():
            data3 = self.data3.recv() # n * (3,1000)
            self.hk = np.array(data3[0])
            self.time_tuple = data3[1]

            if self.offset != 0 :
                self.parse_arrays(dir)

            else :
                print(colored('data append skipped!','red'))
            time.sleep(0.01)

        sys.exit()

    def parse_arrays(self,dir):
        i = 0
        j = 0

        if self.saved_time != 0 :
            data = self.saved_array
            self.start_time_stamp = self.saved_time
            self.k += 1
            self.saved_array = []
            self.saved_time = 0

        while i <= (self.hk.shape[0] - 1) : # ~10
            while j <= (self.hk.shape[2] - 1) : # 1000

                data = self.hk[i][0][j]

                if data != 0.0 : # only finds first instance of non-zero value
                    if self.b == 0 and i == 0 and self.k == 0 :
                        self.new_time_stamp = data
                        self.start_time_stamp = data
                        self.hk_data[0,:,:] = self.hk[0][:][:] # take first file and put them in first position
                        self.k += 1
                        i += 1
                        j = 0
                        break

                    else :
                        self.new_time_stamp = data
                        index = int(self.new_time_stamp - self.start_time_stamp)

                        if index >= 100 :
                            print(colored(('index > 200',index),'red'))
                            self.append_hk_data(dir) # stick the current data array in netcdf
                            new_index = ((index+100//2)//100) - 1 # how many empty filler files do we need?
                            print(colored(('num of files :',new_index),'red'))

                            """#################################################################################"""
                            """ IF OUR NEXT INDEX IS OVER 200 , ADD A FILLER FILE OF JUST ZEROES """
                            """################################################################################"""

                            if new_index > 0 :
                                # create a bunch of empty arrays
                                for i in range(new_index) :
                                    self.hk_data = np.zeros((int(ut.german_freq),self.hk.shape[1],self.hk.shape[2]))
                                    self.append_hk_data(dir) # stick empty data into netcdf
                                # find the remainder
                                new_index = (index % 100) - 1
                                # append to last empty array + whatever the index of the remainder was
                                self.hk_data[new_index,:,:] = self.hk[i][:][:]
                                j = 0
                                i += 1
                                self.start_time_stamp = data # reset the time for the current placeholder
                                break
                                """#################################################################################"""

                            else :
                                self.hk_data = np.zeros((int(ut.german_freq),self.hk.shape[1],self.hk.shape[2])) # make a new array
                                new_index = index % 100
                                self.hk_data[new_index,:,:] = self.hk[i][:][:]
                                j = 0
                                i += 1
                                self.start_time_stamp = int(data) + 1 # reset the time for the current placeholder
                                break

                        else : # if not, put it in correct place in array
                            self.hk_data[index,:,:] = self.hk[i][:][:]
                            j = 0
                            i += 1
                            break

                else :
                    j += 1

            if i == self.hk.shape[0]:
                print('LAST ARRAY, SAVING HK ARRAY AND TIMESTAMP')
                self.saved_array = self.hk_data
                self.saved_time = self.start_time_stamp
                print(colored(('final array',self.start_time_stamp,self.new_time_stamp,i-1,j),'red'))
                break
        # # ------------------------------------------------------------------------------------------
        return

# ============================================================================================================================
    def append_hk_data(self,dir):

        if self.b == 0: # if it's the first file, make a new netcdf file
            self.filestarttime = dt.datetime.utcnow()
            self.filestarttime = self.filestarttime.isoformat()
            print(colored('------------ New HK File -------------','green'))
            hk = hnc.new_file(self.filestarttime,dir)
            self.ncfile = dir + "/raw_hk_%s.nc" %(self.filestarttime)

            hnc.data_append(self.ncfile, self.b, self.hk_data, self.time_tuple)

        # elif os.stat(netcdfdir + "/raw_%s.nc" % (self.filestarttime)).st_size >= 20 * 10**6:
        elif self.b % 200 == 0 :
            self.b = 0
            # if it's a full file, make a new netcdf file
            print(colored('----------- New HK File ------------','green'))
            self.filestarttime = dt.datetime.utcnow()
            self.filestarttime = self.filestarttime.isoformat()
            hk = hnc.new_file(self.filestarttime,dir)
            self.ncfile = dir + "/raw_hk_%s.nc" %(self.filestarttime)

            hnc.data_append(self.ncfile, self.b, self.hk_data, self.time_tuple)

        else: # if everything is okay, append data to the file
            hnc.data_append(self.ncfile, self.b, self.hk_data, self.time_tuple)

        # have the counter incremement for every append
        self.b += 1
        return
