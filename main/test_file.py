import time as t
import gzip, os, sys, subprocess
import datetime as dt
from termcolor import colored
import numpy as np
import utils as ut
import hk_netcdf_files as hnc

times = np.linspace(0,0,1000)
names = np.linspace(1,1,1000)
data = np.linspace(2,2,1000)
hk_data = np.array((times,names,data))
mega_hk = []
time_tuple = [0.0,0.0]

for i in range(20) :
    mega_hk.append(hk_data)

hk = np.zeros((100,3,1000))
mega_hk = np.array(mega_hk)

j = 0
for i in range(len(mega_hk)):
    if i % 2 == 0 :
        hk[i,:,:] = mega_hk[j,:,:]
    j += 1

filestarttime = dt.datetime.utcnow()
filestarttime = filestarttime.isoformat()
netcdfdir = '/Users/vlb9398/Desktop'
ncfile = netcdfdir + "/raw_hk_%s.nc" %(filestarttime)
hk = hnc.new_file(filestarttime)
hnc.data_append(ncfile, 0, hk_data, time_tuple)
