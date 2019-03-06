import netCDF4 as nc
import os, sys
import time as t
import datetime as now
import numpy as np
from termcolor import colored
import utils as ut

def new_file(filestarttime,dir):
    print(colored(('DIR:',dir),'yellow'))
    hk = nc.Dataset(dir + "/raw_hk_%s.nc" %(filestarttime),"w",format="NETCDF4_CLASSIC")

    # Dimensions for Data Arrays -------------------------------------------------------------------
    # hk.createDimension('mode',2)
    hk.createDimension('t',None)
    hk.createDimension('hk_col',3)
    hk.createDimension('hk_row',1000)
    hk.createDimension('hk_num', int(ut.german_freq))
    hk.createDimension('tuple',2)

    # creating variables --------------------------------------------------------------------------------
    global HK_Data
    HK_Data = hk.createVariable('hk_data','f8',('t','hk_num','hk_col','hk_row'),zlib=True)
    global Time
    Time = hk.createVariable('hk_time', 'f8',('t','tuple'),zlib=True)
    # =========================================================================
    hk.close()

def data_append(nc_file, p, data, time):
    if os.path.exists(nc_file):
        hk = nc.Dataset(nc_file,"r+",format="NETCDF4_CLASSIC")
        HK_Data[p,:,:,:] = data
        Time[p,:] = time
        hk.close()
    else :
        print(colored("Could not find NETCDF File!", 'red'))
