import numpy as np
from os import stat
import os
import sys
import mce_data
import netcdf as nc
import subprocess
import datetime as dt
import gzip
from termcolor import colored

sys.stdout = os.fdopen(sys.stdout.fileno(), 'w', 1) # line buffering

class Time_Files:

    def __init__(self):
        self.name = ''
        self.data = 0.0
        self.time = 0
        self.new_time = 0
        self.tele_time = (0.0,0.0)
        self.n = 0
        self.filestarttime = 0
        self.a = 0
        self.rc = 0
        self.h1_shape = 0
        self.h2_shape = 0
        self.mce = 0
        self.h1 = 0
        self.h2 = 0
        self.head1 = 0
        self.head2 = 0

    def netcdfdata(queue,rc):
        self.rc = rc
        dir3 = ('/Users/vlb9398/Desktop/netcdffiles')
        dir1 = ('/Users/vlb9398/Desktop/test_mce_files')
        dir2 = ('/Users/vlb9398/Desktop/test_mce_files_copy')
        begin = dt.datetime.utcnow()
        end = dt.datetime.utcnow()
        while end - begin < dt.timedelta(seconds = 5):
            # if self.a > 0 :
                mce_file1 = len(os.listdir(dir1))
                mce_file2 = len(os.listdir(dir2))
                hk_file = len(os.listdir(dir3))
                if (mce_file1 and mce_file2 and hk_file != 0):
                    files1 = [dir1 + x for x in os.listdir(dir1) if (x.startswith("temp") and not x.endswith('.run'))]
                    files2 = [dir2 + x for x in os.listdir(dir2) if (x.startswith("temp") and not x.endswith('.run'))]
                    files3 = [dir3 + x for x in os.listdir(dir3) if (x.startswith('omnilog'))]
                    print colored('num of hk files : %s' %(len(files3)),'magenta')
                    # we want more than just temp.run in the directory
                    if mce_file1 > 1 and mce_file2 > 1:
                        #mce1 = min(files1, key = os.path.getctime)
                        self.hk_read(files3,hk_file)
                        self.rc = rc
                        self.readdata(queue, files1, files2, mce_file1, mce_file2, rc)
                        #print colored('File Read: mce1:%s , mce2:%s , hk:%s' %(str(mce1).replace(dir1,''),str(mce1).replace(dir2,''),str(hk).replace(dir3,'')),'yellow')
                        self.a = self.a + 1
                        begin = dt.datetime.utcnow()
                end = dt.datetime.utcnow()
            # else :
            #     files1 = [dir1 + x for x in os.listdir(dir1) if (x.startswith("temp") and not x.endswith('.run'))]
            #     files2 = [dir2 + x for x in os.listdir(dir2) if (x.startswith("temp") and not x.endswith('.run'))]
            #     files3 = [dir3 + x for x in os.listdir(dir3) if (x.startswith('omnilog'))]
            #     subprocess.Popen(['rm %s' %(files1)], shell=True)
            #     subprocess.Popen(['rm %s' %(files2)], shell=True)
            #     subprocess.Popen(['rm %s' %(files3)], shell=True)
            #     self.a = self.a + 1

        else :
            print colored('No More Files','red')
            queue.put(a,'done','done')
            subprocess.Popen(['rm /home/time/Desktop/time-data/mce1/temp.run'], shell=True)
            subprocess.Popen(['rm /home/time/Desktop/time-data/mce2/temp.run'], shell=True)
            subprocess.Popen(['ssh -T time@time.pyhk.net pkill -9 -f hk_sftp.py'], shell=True)
            sys.exit()

# ===========================================================================================================================
    def readdata(queue, files1, files2, mce_file1, mce_file2, rc):
        ''' This only works under the assumption that both mces are
            spitting out the same number of files at any given time'''
        for i in range(mce_file1 - 1):
            f1 = mce_data.SmallMCEFile(files1[i])
            self.h1 = f1.Read(row_col=True, unfilter='DC').data
            f2 = mce_data.SmallMCEFile(files2[i])
            self.h2 = f2.Read(row_col=True, unfilter='DC').data
            # send data to the gui
            queue.put(self.a,self.h1,self.h2)
        # -------CHECK FOR FRAME SIZE CHANGE--------------------------------
            if n != 0 :
                if (h1.shape != self.h1_shape and h2.shape != self.h2_shape) :
                    print colored('WARNING! Both MCE Frame Size Has Changed','red')
                elif h1.shape != self.h1_shape :
                    print colored('WARNING! MCE0 Frame Size Has Changed','red')
                else :
                    print colored('WARNING! MCE1 Frame Size Has Changed','red')
            self.h1_shape = self.h1.shape
            self.h2_shape = self.h2.shape
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

            subprocess.Popen(['rm %s' % (files1[i])], shell=True)
            subprocess.Popen(['rm %s' % (files2[i])], shell=True)
        return self.rc

# ===========================================================================
    def read_header(f):
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
    def hk_read(hk,num_hk):
        self.rc = 'hk'
        for i in range(num_hk - 1):
            file = gzip.open(hk[i])
            for line in file:
                self.t_type,self.time,name1,name2,self.data = line.strip().split(",")
                name = (name1 + "_" + name2).replace('"','')
                self.name = name.replace(' ','_')
                print(colored(name,'magenta'))
                if self.name == 'HKMBv1b0_SYNC_number' :
                    self.tele_time = [float(self.time),float(self.data)]
                self.append_data()
                #===============================================================
                if self.n == 0 :
                    self.new_time = self.time
                #===============================================================
                if self.new_time == self.time:
                    continue
                else :
                    self.n += 1
                    self.new_time = self.time
                #===============================================================
                print(colored(self.n,self.time,'red'))
                #===============================================================
        # delete old hk files
        for i in range(num_hk - 1):
            subprocess.Popen(['rm %s' % (hk[i])], shell=True)
        return self.rc

# ============================================================================
    def append_data():
        ''' going to have to change this directory '''
        netcdfdir = '/Users/vlb9398/Desktop'
        if self.a == 0: # if it's the first file, make a new netcdf file
            self.filestarttime = dt.datetime.utcnow()
            self.filestarttime = self.filestarttime.isoformat()
            print(colored('------------ New File -------------','green'))
            mce = nc.new_file(h1, self.filestarttime)
            self.ncfile = netcdfdir + "/raw_%s.nc" %(self.filestarttime)

            if self.rc == 's' :
                nc.mce_append(self.ncfile, self.n, self.h1, self.h2, self.head1, self.head2)
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
            mce = nc.new_file(h1, self.filestarttime)
            self.ncfile = netcdfdir + "/raw_%s.nc" %(self.filestarttime)

            if self.rc == 's' :
                nc.mce_append(self.ncfile, self.n, self.h1, self.h2, self.head1, self.head2)
            elif self.rc == 'hk':
                nc.hk_append(self.ncfile, self.n, self.time, self.data, self.name, self.tele_time)
            else :
                print(colored('Wrong RC Input!','red'))

        else: # if everything is okay, append data to the file
            if self.rc == 's' :
                nc.mce_append(self.ncfile, self.n, self.h1, self.h2, self.head1, self.head2)
            elif self.rc == 'hk':
                nc.hk_append(self.ncfile, self.n, self.time, self.data, self.name, self.tele_time)
            else :
                print(colored('Wrong RC Input!','red'))
        return self.rc
