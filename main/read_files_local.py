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

sys.stdout = os.fdopen(sys.stdout.fileno(), 'w', 1) # line buffering

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
        self.done = True

    def netcdfdata(self,rc):
        self.rc = rc
        dir3 = ('/Users/vlb9398/Desktop/test_hk_files/')
        dir1 = ('/Users/vlb9398/Desktop/test_mce_files/')
        dir2 = ('/Users/vlb9398/Desktop/test_mce_files_copy/')
        begin = dt.datetime.utcnow()
        end = dt.datetime.utcnow()
        while end - begin < dt.timedelta(seconds = 3):
            # if self.a > 0 :
                mce_file1 = len(os.listdir(dir1))
                mce_file2 = len(os.listdir(dir2))
                hk_file = len(os.listdir(dir3))
                if (mce_file1 and mce_file2 and hk_file != 0):
                    files1 = [dir1 + x for x in os.listdir(dir1) if (x.startswith("test") and not x.endswith('.run'))]
                    files2 = [dir2 + x for x in os.listdir(dir2) if (x.startswith("test") and not x.endswith('.run'))]
                    # we want more than just temp.run in the directory
                    if self.a < mce_file1 - 1: # won't work when directory is having files being deleted after each read
                        self.rc = rc
                        self.readdata(files1[self.a], files2[self.a], 1, 1, rc)
                        self.done = True
                        self.rc = 'hk'
                        self.hk_read(hk_file)
                        self.done = True
                        self.a = self.a + 1
                        print(colored("This is a: %s" %(self.a),'red'))
                        begin = dt.datetime.utcnow()
                        # print(colored(files1[self.a],'yellow'))
                    else :
                        end = dt.datetime.utcnow() + 3.5
                    end = dt.datetime.utcnow()

        else :
            print(colored('No More Files','red'))
            sys.exit()

# ===========================================================================================================================
    def readdata(self, files1, files2, mce_file1, mce_file2, rc):
        if self.done :
            self.done = False
            ''' This only works under the assumption that both mces are
                spitting out the same number of files at any given time'''
            # for i in range(1):
            f1 = mce_data.SmallMCEFile(files1)
            self.h1 = f1.Read(row_col=True, unfilter='DC').data
            f2 = mce_data.SmallMCEFile(files2)
            self.h2 = f2.Read(row_col=True, unfilter='DC').data

            # -------CHECK FOR FRAME SIZE CHANGE--------------------------------
            if self.a != 0 :
                if (self.h1.shape != self.h1_shape and self.h2.shape != self.h2_shape) :
                    print(colored('WARNING! Both MCE Frame Size Has Changed','red'))
                elif self.h1.shape != self.h1_shape :
                    print(colored('WARNING! MCE0 Frame Size Has Changed','red'))
                else :
                    print(colored('WARNING! MCE1 Frame Size Has Changed','red'))
            else :
                self.h1_shape = self.h1.shape
                self.h2_shape = self.h2.shape

            # self.h1_shape = self.h1.shape
            # self.h2_shape = self.h2.shape
            self.head1 = self.read_header(f1)
            self.head2 = self.read_header(f2)
            # -----------------------------------------------------------------
            # d1 = np.empty([h.shape[0],h.shape[1]],dtype=float)
            # for b in range(h.shape[0]):
            #     for c in range(h.shape[1]):
            #         d1[b][c] = (np.std(h1[b][c][:],dtype=float))
            # d2 = np.empty([h.shape[0],h.shape[1]],dtype=float)
            # for b in range(h.shape[0]):
            #     for c in range(h.shape[1]):
            #         d2[b][c] = (np.std(h2[b][c][:],dtype=float))
            # -----------------------------------------------------------------
            self.rc = rc
            self.append_data()
            self.p += 1
            print(colored("MCE Append",'red'))
            return self.rc
        else :
            print(colored("I'm broken",'red'))
            sys.exit()

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
    def hk_read(self,num_hk):
        if self.done :
            self.done = False
            self.k = 0
            dir3 = ('/Users/vlb9398/Desktop/test_hk_files/')
            files3 = [dir3 + x for x in os.listdir(dir3) if (x.startswith('omnilog'))]
            # print(colored(files3[0],'green'))
            file = open(files3[0])
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
                print(colored("HK Append",'red'))
            self.k = 0
                    #===============================================================
            return self.rc
        else :
            print(colored("I'm broken",'red'))
            sys.exit()

# ============================================================================
    def append_data(self):
        netcdfdir = '/Users/vlb9398/Desktop/netcdffiles'
        if self.a == 0: # if it's the first file, make a new netcdf file
            self.filestarttime = dt.datetime.utcnow()
            self.filestarttime = self.filestarttime.isoformat()
            print(colored('------------ New File -------------','green'))
            mce = nc.new_file(self.h1.shape, self.filestarttime)
            self.ncfile = netcdfdir + "/raw_%s.nc" %(self.filestarttime)

            if self.rc == 's' :
                nc.mce_append(self.ncfile, self.p, self.h1, self.h2, self.head1, self.head2)
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

            if self.rc == 's' :
                nc.mce_append(self.ncfile, self.p, self.h1, self.h2, self.head1, self.head2)
            elif self.rc == 'hk':
                nc.hk_append(self.ncfile, self.n, self.time, self.data, self.name, self.tele_time)
            else :
                print(colored('Wrong RC Input!','red'))

        else: # if everything is okay, append data to the file
            if self.rc == 's' :
                nc.mce_append(self.ncfile, self.p, self.h1, self.h2, self.head1, self.head2)
            elif self.rc == 'hk':
                nc.hk_append(self.ncfile, self.n, self.time, self.data, self.name, self.tele_time)
            else :
                print(colored('Wrong RC Input!','red'))

        # print(colored(os.stat(netcdfdir + "/raw_%s.nc" %(self.filestarttime)).st_size,'magenta'))
        return self.rc

if __name__ == "__main__" :
    tf = Time_Files()
    tf.netcdfdata('s')
