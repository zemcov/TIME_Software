import time as t
import gzip, os, sys, subprocess, datetime
from termcolor import colored
import numpy as np
import utils as ut


zero = np.zeros((1,3,1000))
hk_data = np.zeros((100,3,1000))

times = [0.0]*1000
names = [1.0]*1000
data = [2.0]*1000
hk = np.array((times,names,data))

time_tuple = [0.0,0.0]
mega_hk = []
for i in range(20) :
    mega_hk.append(hk)

hk1 = [None] * 1000
hk2 = np.array((hk1,hk1,hk1))

j = 0
for i in range(len(mega_hk)-1):
    if i % 2 == 0 :
        hk_data[i] = mega_hk[j][:][:]
    j += 1

print(np.asarray(hk_data).shape)
# print(np.asarray(hk_data).reshape(100,3,1000))

import hk_netcdf_files as hnc
filestarttime = '100'
netcdfdir = '/home/time/Desktop'
ncfile = netcdfdir + "/raw_hk_%s.nc" %(filestarttime)
hk = hnc.new_file(filestarttime)
hnc.data_append(ncfile, 0, hk_data, time_tuple)
