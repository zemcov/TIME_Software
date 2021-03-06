import numpy as np
from os import stat
import os
import sys
import mce_data
import netcdf_files as nc
import subprocess
import datetime as dt
from termcolor import colored
import time

class Read_Files :
    def __init__(self):
        self.name = ''
        self.data = 0.0
        self.time = 0
        self.new_time = 0
        self.tele_time = (0.0,0.0)
        self.n = 0
        self.filestarttime = 0
        self.a = 0

    def hk_read(self):
        rc = 'hk'
        dir3 = '/Users/vlb9398/Desktop/test_hk_files/'
        hk_file = len(os.listdir(dir3))
        files3 = [dir3 + x for x in os.listdir(dir3) if (x.startswith('omnilog'))]
        for i in range(hk_file - 1):
            file = open(files3[i])
            for line in file:
                self.t_type,self.time,name1,name2,self.data = line.strip().split(",")
                name = (name1 + "_" + name2).replace('"','')
                self.name = name.replace(' ','_')
                print(colored(name,'magenta'))
                if self.name == 'HKMBv1b0_SYNC_number' :
                    self.tele_time = [float(self.time),float(self.data)]
                self.append_data(rc)
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

    def append_data(self,rc):
        netcdfdir = '/Users/vlb9398/Desktop'
        h1 = (1,1,1)
        if self.a == 0: # if it's the first file, make a new netcdf file
            self.filestarttime = dt.datetime.utcnow()
            self.filestarttime = self.filestarttime.isoformat()
            print(colored('------------ New File -------------','green'))
            mce = nc.new_file(h1, self.filestarttime)
            self.ncfile = netcdfdir + "/raw_%s.nc" %(self.filestarttime)

            if rc == 's' :
                nc.mce_append(self.ncfile, self.n, h1, h2, head1, head2, self.filestarttime)
            elif rc == 'hk':
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

            if rc == 's' :
                nc.mce_append(self.ncfile, self.n, h1, h2, head1, head2, self.filestarttime)
            elif rc == 'hk':
                nc.hk_append(self.ncfile, self.n, self.time, self.data, self.name, self.tele_time)
            else :
                print(colored('Wrong RC Input!','red'))

        else: # if everything is okay, append data to the file
            if rc == 's' :
                nc.mce_append(self.ncfile, self.n, h1, h2, head1, head2, self.filestarttime)
            elif rc == 'hk':
                nc.hk_append(self.ncfile, self.n, self.time, self.data, self.name, self.tele_time)
            else :
                print(colored('Wrong RC Input!','red'))

Read_Files().hk_read()
