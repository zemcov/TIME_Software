import netCDF4 as nc
import os
import sys
#import takedata_test as td
import datetime as now
import numpy as np
from termcolor import colored

#sys.stdout = os.fdopen(sys.stdout.fileno(), 'w', 1) # line buffering

tempfiledir = '/home/time/Desktop/time-data/netcdffiles'
def new_file(h_size, head1, head2, filestarttime):
    mce = nc.Dataset(tempfiledir + "/raw_%s.nc" %(filestarttime),"w",format="NETCDF4_CLASSIC")

    # create the gui parameters group
    # guiparams = mce.createGroup('guiparams')
    # stream = mce.createGroup('stream')
    # heatmap = mce.createGroup('heatmap')
    # mce_header = mce.createGroup('mce_header')

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
    mce.createDimension('raw_cols',8)
    mce.createDimension('raw_cols_all',32)
    mce.createDimension('raw_num', h_size[2])
    mce.createDimension('rms_rows',h_size[0])
    mce.createDimension('rms_cols',8)
    mce.createDimension('rms_cols_all',32)
    mce.createDimension('k',1)
    mce.createDimension('v',32)


    # creating variables --------------------------------------------------------------------------------
    Observer = mce.createVariable("observer","S1",("obs",))
    Datetime = mce.createVariable('datetime', 'S1',('date',))
    Frames = mce.createVariable('frames', 'S1',('f',))
    Datamode = mce.createVariable('datamode','S1',('mode',))
    Detector = mce.createVariable('detector','f8',('det',))
    Rc = mce.createVariable('rc','S1',('r',)) # can either use rc name or integer used by gui
    global Time
    Time = mce.createVariable('time','S1',('t','date'))

    global MCE0_Raw_Data_All
    # global MCE0_Raw_Data
    global MCE1_Raw_Data_All
    # global MCE1_Raw_Data
    # MCE0_Raw_Data = mce.createVariable('mce0_raw_data','f8',('t','raw_rows','raw_cols','raw_num'))
    MCE0_Raw_Data_All = mce.createVariable('mce0_raw_data_all','f8',('t','raw_rows','raw_cols_all','raw_num'))

    # MCE1_Raw_Data = mce.createVariable('mce1_raw_data','f8',('t','raw_rows','raw_cols','raw_num'))
    MCE1_Raw_Data_All = mce.createVariable('mce1_raw_data_all','f8',('t','raw_rows','raw_cols_all','raw_num'))

    # global Rms_Noise_All
    # global Rms_Noise
    # Rms_Noise_All = mce.createVariable('rms_noise_all','f8',('t','rms_rows','rms_cols_all'))
    # Rms_Noise = mce.createVariable('rms_noise','f8',('t','rms_rows','rms_cols'))

    global MCE0_Header
    global MCE1_Header
    MCE0_Header = mce.createVariable('mce0_header','S1',('t','k','v'))
    MCE1_Header = mce.createVariable('mce1_header','S1',('t','k','v'))

    parafilename = ('tempfiles/tempparameters.txt')
    parafile = open(parafilename, 'r')
    parameters = parafile.readline().strip().split()

    MCE0_Header._Encoding = 'ascii'
    MCE1_Header._Encoding = 'ascii'
    Observer._Encoding = 'ascii'
    Frames._Encoding = 'ascii'
    Datamode._Encoding = 'ascii'
    Rc._Encoding = 'ascii'
    Time._Encoding = 'ascii'

    Observer[:] = np.array([parameters[0]],dtype='S3')
    Frames[:] = np.array([parameters[3]],dtype='S8')
    Datamode[:] = np.array([parameters[1]],dtype='S2')
    Rc[:] = np.array([parameters[2]],dtype='S1')
    parafile.close()

    mce.close()
    return mce

def data_all(h1, h2, n, head1, head2, filestarttime):
    mce = nc.Dataset(tempfiledir + "/raw_%s.nc" %(filestarttime),"a")
    Time[n,:] = np.array([str(now.datetime.utcnow())],dtype='S26')
    MCE0_Raw_Data_All[n,:,:,:] = h1
    MCE1_Raw_Data_All[n,:,:,:] = h2
    new_head1 = np.array([head1],dtype='S15').reshape((1,32))
    new_head2 = np.array([head2],dtype='S15').reshape((1,32))
    print head1
    print '-----------------------------'
    print new_head1
    MCE0_Header[n,:,:] = new_head1
    MCE1_Header[n,:,:] = new_head2
    mce.close()

# def data(h1, h2, n, head1, head2, filestarttime):
#     mce = nc.Dataset(tempfiledir + "/raw_%s.nc" %(filestarttime),"a")
#     Time[n,:] = np.array([str(now.datetime.utcnow())],dtype='S26')
#     MCE0_Raw_Data[n,:,:,:] = h1
#     MCE1_Raw_Data[n,:,:,:] = h2
#     #new_head1 = np.array([head1],dtype='S15').reshape((2,16))
#     #new_head2 = np.array([head2],dtype='S15').reshape((2,16))
#     #MCE0_Header[a,:,:] = new_head1
#     #MCE1_Header[a,:,:] = new_head2
#     mce.close()
