import numpy as np
from os import stat
import os, sys, subprocess, errno
from . import netcdf_files as nc
from . import hk_netcdf_files as hnc
import datetime as dt
from termcolor import colored
import time
import multiprocessing as mp
import config.utils as ut
from . import read_mce, read_tel, read_kms
from config import init

class Time_Files:

    def __init__(self,flags,offset):
        self.a = 0
        self.p = 0
        self.flags = flags
        self.offset = offset

        self.queues = [mp.Queue() for i in range(4)]
        self.procs = []
        self.procs.append(mp.Process(name='Data Process MCE0', target=read_mce.netcdfdata, args=(0,self.queues[0],self.flags,)))
        self.procs.append(mp.Process(name='Data Process MCE1',target=read_mce.netcdfdata , args=(1,self.queues[1],self.flags,)))
        self.procs.append(mp.Process(name='Data Process Tel',target=read_tel.loop_files , args=(self.queues[2],)))
        # self.procs.append(mp.Process(name='Data Process KMS',target=read_kms.loop_files , args=(self.queues[3],)))

        for mce_index in range(2):
            if ut.which_mce[mce_index] == 1 :
                print('starting read mce%i' % mce_index)
                self.procs[mce_index].start()
        self.procs[2].start()
        # self.procs[3].start()

        sys.stdout.flush()
        sys.stderr.flush()

    # ~ def close(self):
        # ~ for i in range(len(self.procs)):
            # ~ print("Joining process %i (%s)" % (i, self.procs[i]))
            # ~ self.procs[i].join()

    def retrieve(self,queue,dir):
        """
        The purpose of this function is to retrieve data for the telescope and both of the mces
        Inputs: queue - idk
                dir - the directory where we want to append data
        Outputs: None
        """
        # os.nice(-20)
        last_time = 0
        while not ut.mce_exit.is_set():

            time.sleep(0.01) # Rate limit

            if time.time() - last_time > 1:
                # print("append_data.retrieve is still alive"
                # ~ print("append_data.retrieve is still alive, waiting on event %i" % id(ut.mce_exit))
                last_time = time.time()

            # Wait until everything is ready
            data_ready = True
            for mce_index in range(2):
                if (ut.which_mce[mce_index] == 1) and self.queues[mce_index].empty():
                    data_ready = False
            for qi in [2]: # [2,3]:
                if self.queues[qi].empty():
                    data_ready = False
            if not data_ready:
                continue

            a = []
            b = []

            if ut.which_mce[0] == 1 :
                data1 = self.queues[0].get() #what is actually in data1, idk
                self.h1 = data1[0] #what is h1? idk
                self.head1 = data1[1]
                self.sync1 = data1[2]
                self.mce0_on = data1[3]
                a = self.h1
                # ---------------------------------------------------------

            if ut.which_mce[1] == 1 :
                data2 = self.queues[1].get()
                self.h2 = data2[0]
                self.head2 = data2[1]
                self.sync2 = data2[2]
                self.mce1_on = data2[3]
                b = self.h2

            if ut.which_mce[2] == 1 :
                a = np.random.normal(0,2,(33,32,100))
                b = np.random.normal(10,0.1,(33,32,100))

                time.sleep(0.99)

            queue.put([a,b,self.p])

            self.tel_data = self.queues[2].get()
            # self.kms_data = self.queues[3].get()
            # ------------------------------------------
            # if ut.which_mce[2] == 0 : # if we aren't running in sim mode
            self.parse_arrays(dir)
            self.append_mce_data(dir)
            self.p += 1

        # ~ print("append_data.retrieve is closing processes")
        # ~ self.close()

        print("append_data.retrieve is closing connections")
        for q in self.queues:
            q.close()

        print("append_data.retrieve is exiting")
        sys.stdout.flush()

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
            self.utc = list(zip(ut.utc_time,self.sync2)) # tuples of (utc,sync)
        if ut.which_mce[0] == 1 :
            ut.utc_time = ut.sync_to_utc(self.sync1,self.offset.value)
            self.utc = list(zip(ut.utc_time,self.sync1)) # tuples of (utc,sync)

        # new_utc = self.utc[::5]
        # # print(len(self.utc),len([x[0] for x in new_utc]),len(self.tel_data[:,-1]))
        # print('MCE UTC: ', ["%0.3f" % x[0] for x in new_utc])
        # print('Tel UTC: ', ["%0.3f" % x[-1] for x in self.tel_data])
        # print('Diff: ' , ["%0.3f" % x for x in np.subtract([x[0] for x in new_utc],self.tel_data[:,-1])])
        # sys.stdout.flush()

        return

# ============================================================================
    def append_mce_data(self,dir):
        """
        Purpose: to append mce data into the netcdf files
        Inputs: dir - the directory for the netcdf files
        Outputs: None - but it creates files
        """
        if self.a == 0: # if it's the first file, make a new netcdf file
            self.filestarttime = dt.datetime.utcnow()
            self.filestarttime = self.filestarttime.isoformat()
            print(colored('------------ New MCE File -------------','green'))
            mce = nc.new_file(self.filestarttime,dir)
            self.ncfile = dir + "/raw_mce_%s.nc" %(self.filestarttime)

            if ut.which_mce[0] == 1 and ut.which_mce[1] == 1 : #if it is using mce1 and mce0
                nc.data_append(self.ncfile, self.a, self.flags, self.utc, self.head1, self.head2, self.h1, self.h2, self.mce0_on, self.mce1_on, self.tel_data)
            elif ut.which_mce[0] == 1 : #if it is just mce0
                dummy = []
                nc.data_append(self.ncfile, self.a, self.flags, self.utc, self.head1, dummy, self.h1, dummy, self.mce0_on, dummy, self.tel_data)
            elif ut.which_mce[1] == 1 : #if it is just mce1
                dummy = []
                nc.data_append(self.ncfile, self.a, self.flags, self.utc, dummy, self.head2, dummy, self.h2, dummy, self.mce1_on, self.tel_data)
            else: #if it's sim data
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
