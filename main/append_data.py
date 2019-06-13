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
import read_mce0, read_mce1, read_tel
import init

class Time_Files:

    def __init__(self,flags,offset):
        self.a = 0
        self.p = 0
        self.flags = flags
        self.offset = offset
        self.dir = temp_dir
        self.data1, queue1 = mp.Pipe() #what are each of these pipes, idk
        self.data2, queue2 = mp.Pipe()
        self.data3, queue3 = mp.Pipe()
        self.data4, queue4 = mp.Pipe()
        self.p1 = mp.Process(target=read_mce0.netcdfdata, args=(queue1,self.flags,))
        self.p2 = mp.Process(target=read_mce1.netcdfdata , args=(queue2,self.flags,))
        self.p3 = mp.Process(target=read_tel.loop_files , args=(queue3,))
        # self.p4 = mp.Process(target=read_kms.loop_files , args=(queue4,))

        if ut.which_mce[0] == 1 :
            print('starting read mce0')
            self.p1.start()
        if ut.which_mce[1] == 1 :
            print('starting read mce1')
            self.p2.start()

        self.p3.start()
        # self.p4.start()

    def retrieve(self,queue,dir):
        """
        The purpose of this function is to retrieve data for the telescope and both of the mces 
        Inputs: queue - idk
                dir - the directory where we want to append data
        Outputs: None
        """
        # os.nice(-20)
        while not ut.mce_exit.is_set():
            a = []
            b = []

            if ut.which_mce[0] == 1 :
                data1 = self.data1.recv() #what is actually in data1, idk
                self.h1 = data1[0] #what is h1? idk
                self.head1 = data1[1]
                self.sync1 = data1[2]
                self.mce0_on = data1[3]
                a = self.h1
                # ---------------------------------------------------------

            if ut.which_mce[1] == 1 :
                data2 = self.data2.recv()
                self.h2 = data2[0]
                self.head2 = data2[1]
                self.sync2 = data2[2]
                self.mce1_on = data2[3]
                b = self.h2

            if ut.which_mce[2] == 1 :
                # a = np.random.rand(33,32,100)
                # b = np.random.rand(33,32,100)
                a = np.random.normal(0,2,(33,32,100))
                b = np.random.normal(10,0.1,(33,32,100))

                time.sleep(1.0)

            queue.send([a,b,self.p]) #where is it beign sent to idk

            self.tel_data = self.data3.recv()
            # self.kms_data = self.data4.recv()
            # ------------------------------------------
            # if ut.which_mce[2] == 0 : # if we aren't running in sim mode
            self.parse_arrays(dir)
            self.append_mce_data(dir)
            self.p += 1
            time.sleep(0.01)

    def parse_arrays(self,dir):
        # self.hold_h1 = []
        # self.hold_h2 = []

        # print(colored('MCE1 Sync: %s' %(self.sync2[0]),'green'))
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

        if ut.which_mce[1] == 1 :
            ut.utc_time = ut.sync_to_utc(self.sync2,self.offset.value)
            self.utc = zip(ut.utc_time,self.sync2) # tuples of (utc,sync)
        if ut.which_mce[0] == 1 :
            ut.utc_time = ut.sync_to_utc(self.sync1,self.offset.value)
            self.utc = zip(ut.utc_time,self.sync1) # tuples of (utc,sync)

        # new_utc = self.utc[::5]
        # # print(len(self.utc),len([x[0] for x in new_utc]),len(self.tel_data[:,-1]))
        # print('MCE UTC: ', ["%0.3f" % x[0] for x in new_utc])
        # print('Tel UTC: ', ["%0.3f" % x[-1] for x in self.tel_data])
        # print('Diff: ' , ["%0.3f" % x for x in np.subtract([x[0] for x in new_utc],self.tel_data[:,-1])])
        # sys.stdout.flush()

        return

# ============================================================================
    def append_mce_data(self,dir):

        if self.a == 0: # if it's the first file, make a new netcdf file
            self.filestarttime = dt.datetime.utcnow()
            self.filestarttime = self.filestarttime.isoformat()
            print(colored('------------ New MCE File -------------','green'))
            mce = nc.new_file(self.filestarttime,dir)
            self.ncfile = dir + "/raw_mce_%s.nc" %(self.filestarttime)

            if ut.which_mce[0] == 1 and ut.which_mce[1] == 1 :
                nc.data_append(self.ncfile, self.a, self.flags, self.utc, self.head1, self.head2, self.h1, self.h2, self.mce0_on, self.mce1_on, self.tel_data)
            elif ut.which_mce[0] == 1 :
                dummy = []
                nc.data_append(self.ncfile, self.a, self.flags, self.utc, self.head1, dummy, self.h1, dummy, self.mce0_on, dummy, self.tel_data)
            elif ut.which_mce[1] == 1 :
                dummy = []
                nc.data_append(self.ncfile, self.a, self.flags, self.utc, dummy, self.head2, dummy, self.h2, dummy, self.mce1_on, self.tel_data)
            else:
                dummy = []
        # elif os.stat(netcdfdir + "/raw_mce_%s.nc" % (self.filestarttime)).st_size >= 20 * 10**6:
        elif self.a % 100 == 0 :
            self.a = 0
            # if it's a full file, make a new netcdf file
            print(colored('----------- New MCE File ------------','green'))
            self.filestarttime = dt.datetime.utcnow()
            self.filestarttime = self.filestarttime.isoformat()
            mce = nc.new_file(self.filestarttime,dir)
            self.ncfile = dir + "/raw_mce_%s.nc" %(self.filestarttime)

            if ut.which_mce[0] == 1 and ut.which_mce[1] == 1 :
                nc.data_append(self.ncfile, self.a, self.flags, self.utc, self.head1, self.head2, self.h1, self.h2, self.mce0_on, self.mce1_on, self.tel_data)
            elif ut.which_mce[0] == 1 :
                dummy = []
                nc.data_append(self.ncfile, self.a, self.flags, self.utc, self.head1, dummy, self.h1, dummy, self.mce0_on, dummy, self.tel_data)
            elif ut.which_mce[1] == 1 :
                dummy = []
                nc.data_append(self.ncfile, self.a, self.flags, self.utc, dummy, self.head2, dummy, self.h2, dummy, self.mce1_on, self.tel_data)
            else:
                dummy = []
        else: # if everything is okay, append data to the file

            if ut.which_mce[0] == 1 and ut.which_mce[1] == 1 :
                nc.data_append(self.ncfile, self.a, self.flags, self.utc, self.head1, self.head2, self.h1, self.h2, self.mce0_on, self.mce1_on, self.tel_data) # give first values for heatmap to create image scale
            elif ut.which_mce[0] == 1 :
                dummy = []
                nc.data_append(self.ncfile, self.a, self.flags, self.utc, self.head1, dummy, self.h1, dummy, self.mce0_on, dummy, self.tel_data)
            elif ut.which_mce[1] == 1 :
                dummy = []
                nc.data_append(self.ncfile, self.a, self.flags, self.utc, dummy, self.head2, dummy, self.h2, dummy, self.mce1_on, self.tel_data)
            else:
                dummy = []
        # have the counter incremement for every append
        self.a += 1
        return
