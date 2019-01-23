import netCDF4 as nc
import os
import sys
#import takedata_test as td
import datetime as now
import numpy as np
from termcolor import colored

tempfiledir = '/Users/vlb9398/Desktop/netcdffiles'
def new_file(h_size, filestarttime):
    mce = nc.Dataset(tempfiledir + "/raw_%s.nc" %(filestarttime),"w",format="NETCDF4_CLASSIC")

     # GUI PARAMETERS ---------------------------------------------------------------------------------
    mce.createDimension('det',1)
    mce.createDimension('obs',3)
    mce.createDimension('date',26)
    mce.createDimension('f',8)
    mce.createDimension('mode',2)
    mce.createDimension('r',1)
    mce.createDimension('t',None)
    # Dimensions for Data Arrays -------------------------------------------------------------------
    mce.createDimension('raw_rows',h_size[0])
    mce.createDimension('raw_cols',h_size[1])
    mce.createDimension('raw_num', h_size[2])
    mce.createDimension('k',1)
    mce.createDimension('v',16)
    mce.createDimension('hk',1)
    mce.createDimension('hks',2)
    mce.createDimension('sf',4)


    # creating variables --------------------------------------------------------------------------------
    Observer = mce.createVariable("observer","S1",("obs",),zlib=True)
    Datetime = mce.createVariable('datetime', 'S1',('date',),zlib=True)
    Frames = mce.createVariable('frames', 'S1',('f',),zlib=True)
    Datamode = mce.createVariable('datamode','S1',('mode',),zlib=True)
    Detector = mce.createVariable('detector','f8',('det',),zlib=True)
    Rc = mce.createVariable('rc','S1',('r',),zlib=True) # can either use rc name or integer used by gui
    global Time
    Time = mce.createVariable('time','S1',('t','k'),zlib=True)
    global Tele_time
    Tele_time = mce.createVariable('tele_time','f8',('t','hk','hk','hk'),zlib=True)

    # MCE DATA =============================================================================================
    global MCE0_Raw_Data_All
    global MCE1_Raw_Data_All
    MCE0_Raw_Data_All = mce.createVariable('mce0_raw_data_all','f8',('t','raw_rows','raw_cols','raw_num'),zlib=True)
    MCE1_Raw_Data_All = mce.createVariable('mce1_raw_data_all','f8',('t','raw_rows','raw_cols','raw_num'),zlib=True)

    # =========================================================================================================

    # MCE HEADER INFO =========================================================
    global MCE0_Header
    global MCE1_Header
    MCE0_Header = mce.createVariable('mce0_header','i4',('t','v','k'),zlib=True)
    MCE1_Header = mce.createVariable('mce1_header','i4',('t','v','k'),zlib=True)
    # =========================================================================

    global Status_Flags
    Status_Flags = mce.createVariable('status','i4',('t','k','sf'))

    # parafilename = ('tempfiles/tempparameters.txt')
    # parafile = open(parafilename, 'r')
    # parameters = parafile.readline().strip().split()
    #
    # Observer._Encoding = 'ascii'
    # Frames._Encoding = 'ascii'
    # Datamode._Encoding = 'ascii'
    # Rc._Encoding = 'ascii'
    # Time._Encoding = 'ascii'
    #
    # Observer[:] = np.array([parameters[0]],dtype='S3')
    # Frames[:] = np.array([parameters[3]],dtype='S8')
    # Datamode[:] = np.array([parameters[1]],dtype='S2')
    # Rc[:] = np.array([parameters[2]],dtype='S1')
    # parafile.close()
    mce.close()
    return mce

def mce_append(nc_file, p, h1, h2, head1, head2, flags):
    mce = nc.Dataset(nc_file,"r+",format="NETCDF4_CLASSIC")
    Time[p,:] = np.array([str(now.datetime.utcnow())],dtype='S26') # will eventually come from telescope
    Status_Flags[p,:,:] = flags
    MCE0_Raw_Data_All[p,:,:,:] = h1
    MCE1_Raw_Data_All[p,:,:,:] = h2
    MCE0_Header[p,:,:] = head1
    MCE1_Header[p,:,:] = head2
    mce.close()

def hk_append(nc_file, n, time, data, name, tele_time):
    hk = nc.Dataset(nc_file,"r+",format="NETCDF4_CLASSIC")
    if (name + '_NC') in hk.variables.keys():
        hk.variables[name + '_NC'][n,:,:] = [float(time),float(data)]
    else :
        #trying to make the netcdf name the same as the sensor name
        name = hk.createVariable(name + '_NC','f8',('t','hk','hks'),zlib=True)
        name[n,:,:] = [float(time),float(data)]
    if tele_time[0] != 0 : # make sure we are only appending real data
        Tele_time[n,:,:,:] = tele_time
    # print(hk.variables.keys())
