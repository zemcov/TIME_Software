import numpy as np
from os import stat
import os
import sys
import mce_data
import netcdf_files_local as nc
import subprocess
import datetime as dt
import gzip
from termcolor import colored
import time as TIME
from multiprocessing import Pipe
import utils as ut

# sys.stdout = os.fdopen(sys.stdout.fileno(), 'w', 1) # line buffering

class Time_Files:

    def __init__(self):
        self.name = ''
        self.data = 0.0
        self.time = 0
        self.new_time = 0
        self.tele_time = (0.0,'',0.0)
        self.n = 0  # hk file indexer
        self.p = 0  # mce file indexer
        self.filestarttime = 0
        self.a = 0 # time keeper from gui
        self.rc = 0
        self.mce = 0
        self.h1 = 0
        self.h2 = 0
        self.head1 = 0
        self.head2 = 0

    def netcdfdata(self,queue):
        dir1 = '/home/time/Desktop/time-data/mce1/'
        dir2 = '/home/time/Desktop/time-data/mce2/'
        dir3 = '/home/time/Desktop/time-data/hk/'
        while not ut.mce_exit.is_set():
            mce_file1 = len(os.listdir(dir1))
            mce_file2 = len(os.listdir(dir2))
            hk_file = len(os.listdir(dir3))
            if (mce_file1 and mce_file2 and hk_file != 0):
                files1 = [dir1 + x for x in os.listdir(dir1) if (x.startswith("test") and not x.endswith('.run'))]
                files2 = [dir2 + x for x in os.listdir(dir2) if (x.startswith("test") and not x.endswith('.run'))]
                files3 = [dir3 + x for x in os.listdir(dir3) if (x.startswith("ominlog"))]
                # we want more than just temp.run in the directory
                if mce_file1 > 0 and mce_file2 > 0: # won't work when directory is having files being deleted after each read
                    self.rc = 'a'
                    self.readdata(files1[self.a], files2[self.a], mce_file1, mce_file2)
                    queue.send([self.h1,self.h2,self.p])
                    #self.rc = 'hk'
                    # self.hk_read(hk_file,files3)
                    self.a = self.a + 1
                else :
                    pass
                    print("No Files!")

        print(colored('No More Files','red'))
        sys.exit()

# ===========================================================================================================================
    def readdata(self, files1, files2, mce_file1, mce_file2):
        ''' This only works under the assumption that both mces are
            spitting out the same number of files at any given time'''
        for i in range(mce_file1 - 1):
            f1 = mce_data.SmallMCEFile(files1[i])
            self.h1 = f1.Read(row_col=True, unfilter='DC').data
            f2 = mce_data.SmallMCEFile(files2[i])
            self.h2 = f2.Read(row_col=True, unfilter='DC').data

            # -------CHECK FOR FRAME SIZE CHANGE--------------------------------
            # if frame size is wrong, just append zeros instead of partial array to prevent netcdf error
            # also gives a frame size error flag
            if self.p == 0 :
                self.h1_shape = self.h1.shape
                self.h2_shape = self.h2.shape
                ut.flags.append(0)

            else :
                if (self.h1.shape != self.h1_shape) and (self.h2.shape != self.h2_shape) :
                    print(colored('WARNING! Both MCE Frame Size Has Changed','red'))
                    ut.flags[3] = 11
                    self.h1 = np.zeros((self.h1_shape[0],self.h1_shape[1],self.h1_shape[2]))
                    self.h2 = np.zeros((self.h2_shape[0],self.h2_shape[1],self.h2_shape[2]))

                elif self.h1.shape != self.h1_shape :
                    print(colored('WARNING! MCE0 Frame Size Has Changed','red'))
                    ut.flags[3] = 11
                    self.h1 = np.zeros((self.h1_shape[0],self.h1_shape[1],self.h1_shape[2]))

                elif self.h2.shape != self.h2_shape :
                    print(colored('WARNING! MCE1 Frame Size Has Changed','red'))
                    ut.flags[3] = 11
                    self.h2 = np.zeros((self.h2_shape[0],self.h2_shape[1],self.h2_shape[2]))

                else :
                    ut.flags[3] = 0
                    print(ut.flags)

            self.head1 = self.read_header(f1)
            self.head2 = self.read_header(f2)
            self.rc = 'a'
            self.append_data()
            self.p += 1

        return

# ===========================================================================
    def read_header(self, f):
        keys = []
        values = []
        for key,value in f.header.items():
            if key == '_rc_present':
                for i in range(len(value)):
                    if value[i] == True:
                        value[i] = '1'
                    elif value[i] == False:
                        value[i] = '0'
                    else:
                        print("I don't know what I am...")
                value = ''.join(map(str,value))
            value = int(value)
            values.append(value)
        values = np.asarray(values)
        return values

# ============================================================================
    def hk_read(self,num_hk,hk):
        self.k = 0
        for i in range(num_hk -1):
            file = gzip.open(hk[i])
            name = []
            data = []
            time = []
            # print(colored("name %s" %(name),'red'))
            for line in file:
                fields = line.strip().split(",")
                t_type = str(fields[0])
                name1 = str(fields[2])
                name2 = str(fields[3])
                names = (name1 + "_" + name2).replace('"','')
                if t_type == 't': # want to keep exact sync box value
                    sync = float(fields[1])
                    self.tele_time = [float(fields[1]),names.replace(' ','_'),float(fields[4])]
                else :
                    time.append(int(fields[1]))
                    name.append(names.replace(' ','_'))
                    data.append(float(fields[4]))
                    self.tele_time = [0,'',0]

            #==============================================
            ''' Routine for Sorting Data by Time Index '''
            #==============================================
            sort_name = [x for _,x in sorted(zip(time,name))]
            sort_data = [x for _,x in sorted(zip(time,data))]
            sort_time = sorted(time)
            #==============================================
            print(len(time))
            # only want to append one line at a time to check for new variables
            for i in range(len(time)-1):
                self.time = sort_time[i]
                self.name = sort_name[i]
                self.data = sort_data[i]

                # only incremment index for a new timestamp,not for file num or for t =======
                if self.k == 0 :
                    self.new_time = self.time
                if self.new_time == self.time:
                    pass
                elif self.new_time != self.time :
                    self.n += 1
                    self.new_time = self.time
                self.k += 1

                self.append_data()
            self.k = 0
            print(colored("End of HK Files List",'yellow'))

            # remove the hk file that was just read
            subprocess.Popen(['rm %s' %(hk[i])], shell=True)
                #===============================================================
        return

# ============================================================================
    def append_data(self):
        netcdfdir = '/home/time/Desktop/time-date/netcdffiles'
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

        return
