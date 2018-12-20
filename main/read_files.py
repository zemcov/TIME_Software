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
n = 0

class Time_Files:
    def netcdfdata(rc):
        self.a = 0
        self.rc = rc
        self.mce = 0
        filestarttime = 0
        self.h1_shape = 0
        self.h2_shape = 0
        dir1 = '/home/time/Desktop/time-data/mce1/'
        dir2 = '/home/time/Desktop/time-data/mce2/'
        dir3 = '/home/time/Desktop/time-data/hk/'
        subprocess.Popen(['ssh -T time@time.pyhk.net python /home/time/time-software-testing/TIME_Software/sftp/hk_sftp.py'], shell=True)
        subprocess.Popen(['ssh -T time@time-mce-1.caltech.edu python /home/time/time-software-testing/TIME_Software/sftp/mce1_sftp.py'] , shell=True)
        subprocess.Popen(['ssh -T time@time-mce-0.caltech.edu python /home/time/time-software-testing/TIME_Software/sftp/mce0_sftp.py'], shell=True)
        begin = dt.datetime.utcnow()
        end = dt.datetime.utcnow()
        while end - begin < dt.timedelta(seconds = 5):
            if self.a > 0 :
                mce_file1 = os.path.exists(dir1 + 'temp.%0.3i' %(self.a+1))
                mce_file2 = os.path.exists(dir2 + 'temp.%0.3i' %(self.a+1))
                hk_file = len(os.listdir(dir3))
                if (mce_file1 and mce_file2 and hk_file != 0):
                    files1 = [dir1 + x for x in os.listdir(dir1) if (x.startswith("temp") and not x.endswith('.run'))]
                    files2 = [dir2 + x for x in os.listdir(dir2) if (x.startswith("temp") and not x.endswith('.run'))]
                    files3 = [dir3 + x for x in os.listdir(dir3) if (x.startswith('omnilog'))]
                    print colored('num of hk files : %s' %(len(files3)),'magenta')
                    if (len(files1) and len(files2)) != 0:
                        mce1 = min(files1, key = os.path.getctime)
                        mce2 = min(files2, key = os.path.getctime)
                        #hk = min(files3, key = os.path.getctime)
                        hk_read(files3)
                        self.rc = rc
                        f1 = mce_data.SmallMCEFile(mce1)
                        f2 = mce_data.SmallMCEFile(mce1)
                        header1 = read_header(f1)
                        header2 = read_header(f2)
                        readdata(self.h1_shape,self.h2_shape, f1, f2, self.mce, header1, header2, self.a, filestarttime, self.rc)
                        #print colored('File Read: mce1:%s , mce2:%s , hk:%s' %(str(mce1).replace(dir1,''),str(mce1).replace(dir2,''),str(hk).replace(dir3,'')),'yellow')
                        self.a = self.a + 1
                        begin = dt.datetime.utcnow()
            else :
                files1 = [dir1 + x for x in os.listdir(dir1) if (x.startswith("temp") and not x.endswith('.run'))]
                files2 = [dir2 + x for x in os.listdir(dir2) if (x.startswith("temp") and not x.endswith('.run'))]
                files3 = [dir3 + x for x in os.listdir(dir3) if (x.startswith('omnilog'))]
                subprocess.Popen(['rm %s' %(files1)], shell=True)
                subprocess.Popen(['rm %s' %(files2)], shell=True)
                subprocess.Popen(['rm %s' %(files3)], shell=True)
                a = a + 1
            end = dt.datetime.utcnow()

        else :
            print colored('No More Files','red')
            subprocess.Popen(['rm /home/time/Desktop/time-data/mce1/temp.run'], shell=True)
            subprocess.Popen(['rm /home/time/Desktop/time-data/mce2/temp.run'], shell=True)
            subprocess.Popen(['ssh -T time@time.pyhk.net pkill -9 -f hk_sftp.py'], shell=True)
            sys.exit()

# ===========================================================================================================================
    def readdata(h1_shape,h2_shape,f1, f2, mce, head1, head2, a, filestarttime, rc, mce_file1, mce_file2,
                 hk_data, hk_time,hk_sensors, tele_time, hk_size, t_type):
        h1 = f1.Read(row_col=True, unfilter='DC').data
        h2 = f2.Read(row_col=True, unfilter='DC').data
        # -------CHECK FOR FRAME SIZE CHANGE--------------------------------
        if n != 0 :
            if (h1.shape != h1_shape and h2.shape != h2_shape) :
                print colored('WARNING! Both MCE Frame Size Has Changed','red')
            elif h1.shape != h1_shape :
                print colored('WARNING! MCE0 Frame Size Has Changed','red')
            else :
                print colored('WARNING! MCE1 Frame Size Has Changed','red')
        h1_shape = h1.shape
        h2_shape = h2.shape
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
        subprocess.Popen(['rm %s' % (mce_file1)], shell=True)
        subprocess.Popen(['rm %s' % (mce_file2)], shell=True)
        return mce, filestarttime

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
    def hk_read(hk,mce):
        self.rc = 'hk'
        print colored(len(hk),'red')
        # telling netcdf how many files worth of hk data to expect
        for i in range(len(hk)):
            file = gzip.open(hk[i])
            print colored(hk[i],'red')
            for line in file:
                self.t_type,self.time,name1,name2,self.data = line.strip().split(",")
                self.name = (name1 + "_" + name2).replace('"','')
                if name = 'HKMBv1b0_SYNC_number' :
                    self.tele_time = float(self.time,self.data)
                append_data()

        print hk_size
        # delete old hk files
        for i in range(len(hk)) :
            subprocess.Popen(['rm %s' % (hk[i])], shell=True)

# ============================================================================
    def append_data():
            netcdfdir = '/home/time/Desktop/time-data/netcdffiles'
            if n == 0: # if it's the first file, make a new netcdf file
                self.filestarttime = dt.datetime.utcnow()
                self.filestarttime = filestarttime.isoformat()
                print colored('------------ New File -------------','green')
                mce = nc.new_file(h1.shape, self.filestarttime)
                self.ncfile = netcdfdir + "/raw_%s.nc" %(self.filestarttime)

                if self.rc == 's' :
                    nc.mce_append(self.ncfile, n, h1, h2, head1, head2, self.filestarttime)
                elif self.rc == 'hk':
                    nc.hk_append(self.ncfile, n, self.t_type, self.time, self.data, self.name, self.tele_time)
                else :
                    print colored('Wrong RC Input!','red')

            elif os.stat(netcdfdir + "/raw_%s.nc" % (self.filestarttime)).st_size >= 20 * 10**6:
                # if it's a full file, make a new netcdf file
                n = 0
                print colored('----------- New File ------------','green')
                self.filestarttime = dt.datetime.utcnow()
                self.filestarttime = filestarttime.isoformat()
                mce = nc.new_file(h1.shape, self.filestarttime)
                self.ncfile = netcdfdir + "/raw_%s.nc" %(self.filestarttime)

                if self.rc == 's' :
                    nc.mce_append(self.ncfile, n, h1, h2, head1, head2, self.filestarttime)
                elif self.rc == 'hk':
                    nc.hk_append(self.ncfile, n, self.t_type, self.time, self.data, self.name, self.tele_time)
                else :
                    print colored('Wrong RC Input!','red')

            else: # if everything is okay, append data to the file
                if self.rc == 's' :
                    nc.mce_append(self.ncfile, n, h1, h2, head1, head2, self.filestarttime)
                elif self.rc == 'hk':
                    nc.hk_append(self.ncfile, n, self.t_type, self.time, self.data, self.name, self.tele_time)
                else :
                    print colored('Wrong RC Input!','red')
            # something to increment how many times we have appended data
            Time_Keeper().plus_one()

class Time_Keeper:
    def plus_one(self):
        global n
        n = n + 1

if __name__ == '__main__':
    netcdfdata(sys.argv[1])
