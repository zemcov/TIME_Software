import netCDF4 as nc
import os, sys
import time as t
import datetime as now
import numpy as np
from termcolor import colored
import utils as ut

tempfiledir = '/data/netcdffiles'

def new_file(h_size, filestarttime):
    mce = nc.Dataset(tempfiledir + "/raw_mce_%s.nc" %(filestarttime),"w",format="NETCDF4_CLASSIC")

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
    mce.createDimension('raw_num', int(ut.german_freq))
    mce.createDimension('k',1)
    mce.createDimension('v',1700)
    mce.createDimension('hk_col',3)
    mce.createDimension('hk_row',1000)
    mce.createDimension('hk_num', int(ut.german_freq))
    mce.createDimension('hk',1)
    mce.createDimension('sf',6)
    mce.createDimension('tel_pos',20)
    mce.createDimension('kms_pos',4)
    mce.createDimension('sock_rate',10)

    # creating variables --------------------------------------------------------------------------------
    Observer = mce.createVariable("observer","S1",("obs",),zlib=True)
    Datetime = mce.createVariable('datetime', 'S1',('date',),zlib=True)
    Frames = mce.createVariable('frames', 'S1',('f',),zlib=True)
    Datamode = mce.createVariable('datamode','S1',('mode',),zlib=True)
    Detector = mce.createVariable('detector','f8',('det',),zlib=True)
    Rc = mce.createVariable('rc','S1',('r',),zlib=True) # can either use rc name or integer used by gui
    # global Time
    # Time = mce.createVariable('time','S1',('t','k'),zlib=True)
    global Time
    Time = mce.createVariable('time','f8',('t','mode'),zlib=True)
    global HK_Data
    HK_Data = mce.createVariable('hk_data','f8',('t','hk_col','hk_row','hk_num'),zlib=True)

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

    # TELESCOPE Data ==============================================================
    global Tel
    Tel = mce.createVariable('tel','f8',('sock_rate','tel_pos'),zlib=True)
    # ================================================================================

    # KMS Data ======================================================================
    global KMS
    KMS = mce.createVariable('kms','f8',('sock_rate','kms_pos'),zlib=True)
    # ================================================================================

    global Status_Flags
    Status_Flags = mce.createVariable('status','i4',('t','k','sf'))

    parafilename = ('tempfiles/tempparameters.txt')
    parafile = open(parafilename, 'r')
    parameters = parafile.readline().strip().split()

    Observer._Encoding = 'ascii'
    Frames._Encoding = 'ascii'
    Datamode._Encoding = 'ascii'
    Rc._Encoding = 'ascii'

    Observer[:] = np.array([parameters[0]],dtype='S3')
    Frames[:] = np.array([parameters[3]],dtype='S8')
    Datamode[:] = np.array([parameters[1]],dtype='S2')
    Rc[:] = np.array([parameters[2]],dtype='S1')
    parafile.close()
    mce.close()

def data_append(nc_file, p, flags, times, head1, head2, mce0_data, mce1_data, tele, kms):
    if os.path.exists(nc_file):
        mce = nc.Dataset(nc_file,"r+",format="NETCDF4_CLASSIC")
        Time[p,:] = times
        Status_Flags[p,:,:] = flags
        MCE0_Raw_Data_All[p,:,:,:] = mce0_data
        MCE1_Raw_Data_All[p,:,:,:] = mce1_data
        MCE0_Header[p,:,:] = head1
        MCE1_Header[p,:,:] = head2
        Tel[p,:,:] = tele
        KMS[p,:,:] = kms
        mce.close()
    else :
        print(colored("Could find NETCDF File!", 'red'))
