import netCDF4 as nc
import os, sys
import time as t
import datetime as now
import numpy as np
from termcolor import colored
import config.utils as ut

def new_file(filestarttime,dir):
    """
    Purpose: to create an hk .nc file
    inputs: filestarttime - the time for the first set of data appended to the file
            dir - the directory in which to create this netcdf file
    outputs: None - but a file is created
    Calls: None
    """
    hk = nc.Dataset(dir + "/raw_hk_%s.nc" %(filestarttime),"w",format="NETCDF4_CLASSIC")

    # Dimensions for Data Arrays -------------------------------------------------------------------
    hk.createDimension('t',None)
    hk.createDimension('hk_det',256)
    hk.createDimension('hk_num', int(ut.german_freq))
    hk.createDimension('tuple',2)

    # creating variables --------------------------------------------------------------------------------
    global HK_Data
    HK_Data = hk.createVariable('hk_data','f8',('t','hk_num','hk_det'))
    global Time
    Time = hk.createVariable('hk_time', 'f8',('t','tuple'))
    # =========================================================================
    hk.close()

def data_append(nc_file, p, data, time):
    """
    Purpose: to append data to the hk netcdf files
    input: nc_file - the name of the nc file that data is being appended to
           p - dimensionless rolling time array
           data - hk data of shape [100, 256 detectors]
           time - time tuple of [network time, sync number]
    outputs: None
    calls: None
    """
    if os.path.exists(nc_file):
        hk = nc.Dataset(nc_file,"r+",format="NETCDF4_CLASSIC")
        HK_Data[p,:,:] = data
        Time[p,:] = time
        hk.close()
    else :
        print(colored("Could not find NETCDF File!", 'red'))
