import numpy as np
from os import stat
import os, sys, mce_data, subprocess
import netcdf_files as nc
import datetime as dt
from termcolor import colored
import time as TIME
from multiprocessing import Pipe
import multiprocessing as mp
import utils as ut

class Time_Files:

    def __init__(self):
        self.a = 0

    def parse_arrays(self,q_in,q_out):
        self.rc = 'a'
        self.hold_h1 = []
        self.hold_h2 = []

        ''' for once we get the sync box working again '''
        # sync1 = [h1['sync_box_num'] for h1 in self.h1.headers]
        # sync2 = [h2['sync_box_num'] for h2 in self.h2.headers]
        ''' using frame counter '''

        #( mce0_data, mce0_head, mce0_frame_num, mce1_data, mce1_head, mce1_frame_num )
        h1,head1,sync1,h2,head2,sync2 = q_in.get()
        i = 0
        while i <= len(self.h1):
            if sync1[i] > sync2[i]:
                start_frame = sync1[i]
                i += 1
                while i <= len(self.h1):
                    if sync2[i] < start_frame:
                        i += 1
                    else :
                        self.h1 = self.h1[i]
                        self.h2 = self.h2[i]
                        if len(self.h1) < ut.frameperfile:
                            empty = [[0 for col in range(self.h1.shape[0])] for row in range(self.h1.shape[1])]
                            self.hold_h1.append(self.h1[i] + (empty*(ut.frameperfile - len(self.h1)))) # keeps the last two dimensions as all, same as self.h1[i,:,:]
                            self.hold_h2.append(self.h2[i] + (empty*(ut.frameperfile - len(self.h1))))
                        self.append_data
                        # don't need else statement, because otherise the last else statement would have been triggered if the array was the right size
                        break
                break

            elif sync2[i] > sync1[i]:
                start_frame = sync2[i]
                i += 1
                while i <= len(self.h1):
                    if sync1[i] < start_frame:
                        i += 1
                    else :
                        self.h1 = self.h1[i]
                        self.h2 = self.h2[i]
                        if len(self.h1) < ut.frameperfile:
                            empty = [[0 for col in range(self.h1.shape[0])] for row in range(self.h1.shape[1])]
                            self.hold_h1.append(self.h1[i] + (empty*(ut.frameperfile - len(self.h1))))
                            self.hold_h2.append(self.h2[i] + (empty*(ut.frameperfile - len(self.h1))))
                        self.append_data
                        break
                break

            else :
                #append both frames to netcdf file and send update to gui every n frames
                self.append_data
                break

        self.head1 = head1[i]
        self.head2 = head2[i]
        self.sync1 = sync1[i]
        self.sync2 = sync2[i]

        q_out.put([self.hold_h1,head1,sync1,self.hold_h2,head2,sync2])
        self.hold_h1 = []
        self.hold_h2 = []
        # incremement so we know how many files we have tried to append

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
                nc.mce_append(self.ncfile, ut.p, self.hold_h1, self.hold_h2, self.head1, self.head2, ut.flags)
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
                nc.mce_append(self.ncfile, ut.p, self.hold_h1, self.hold_h2, self.head1, self.head2, ut.flags)
            elif self.rc == 'hk':
                nc.hk_append(self.ncfile, self.n, self.time, self.data, self.name, self.tele_time)
            else :
                print(colored('Wrong RC Input!','red'))

        else: # if everything is okay, append data to the file
            if self.rc == 'a' :
                nc.mce_append(self.ncfile, ut.p, self.hold_h1, self.hold_h2, self.head1, self.head2, ut.flags)
            elif self.rc == 'hk':
                nc.hk_append(self.ncfile, self.n, self.time, self.data, self.name, self.tele_time)
            else :
                print(colored('Wrong RC Input!','red'))

        # have the counter incremement for every append, not just hk
        self.a += 1
        return
