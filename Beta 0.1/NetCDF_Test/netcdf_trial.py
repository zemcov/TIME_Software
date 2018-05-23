from netCDF4 import Dataset
from netCDF4 import MFDataset
import os
import sys
import takedata_test as td
import settings as st
import datetime as now
from netCDF4 import num2date, date2num

#from multipagegui import parameters

def new_file(n):
    mce = Dataset("gui_data_test{n}.nc".format(n=st.n),"w",format="NETCDF4")

    # create the gui parameters group
    guiparams = mce.createGroup('guiparams')
    stream = mce.createGroup('stream')
    heatmap = mce.createGroup('heatmap')
    mce_header = mce.createGroup('mce_header')

    # GUI PARAMETERS ---------------------------------------------------------------------------------
    guiparams.createDimension('det',1)
    guiparams.createDimension('obs',1)
    guiparams.createDimension('date',1)
    guiparams.createDimension('f',1)
    guiparams.createDimension('mode',1)
    guiparams.createDimension('r',1)
    guiparams.createDimension('t',None)
    # Dimensions for Data Arrays -------------------------------------------------------------------
    stream.createDimension('raw_rows',41)
    stream.createDimension('raw_cols',8)
    stream.createDimension('raw_cols_all',32)
    stream.createDimension('raw_num',st.h_size)
    stream.createDimension('t',None)

    heatmap.createDimension('rms_rows',41)
    heatmap.createDimension('rms_cols',8)
    heatmap.createDimension('rms_cols_all',32)
    heatmap.createDimension('t',None)

    mce_header.createDimension('k',2)
    mce_header.createDimension('v',16)
    mce_header.createDimension('t',None)

    # creating variables --------------------------------------------------------------------------------
    Observer = guiparams.createVariable("observer","S3","obs")
    Datetime = guiparams.createVariable('datetime', 'S8','date')
    Frames = guiparams.createVariable('frames', 'S3','f')
    Datamode = guiparams.createVariable('datamode','S2','mode')
    Detector = guiparams.createVariable('detector','f8','det')
    Rc = guiparams.createVariable('rc','S1','r') # can either use rc name or integer used by gui
    global Time
    Time = guiparams.createVariable('time','S26','t')

    global Rms_Noise_All
    global Rms_Noise
    Rms_Noise_All = heatmap.createVariable('rms_noise_all','f8',('t','rms_rows','rms_cols_all'))
    Rms_Noise = heatmap.createVariable('rms_noise','f8',('t','rms_rows','rms_cols'))

    global Raw_Data_All
    global Raw_Data
    Raw_Data = stream.createVariable('raw_data','f8',('t','raw_rows','raw_cols','raw_num'))
    Raw_Data_All = stream.createVariable('raw_data_all','f8',('t','raw_rows','raw_cols_all','raw_num'))

    global Header
    Header = mce_header.createVariable('header','S3',('t','v','k'))

    # appending to variables w/ gui params ------------------------------------------------------------
    Observer[0] = 'VLB' #str(parameters[0])
    Frames[0] = '100' #str(parameters[3])
    Datetime[0] = '00:00:00' #str(parameters[4]
    Datamode[0] = str(10) #str(parameters[1])
    Rc[0] = str(2) #str(parameters[2])

def data_all(h,d,n,a):
    Time[0] = str(now.datetime.utcnow())
    Rms_Noise_All[0,:,:] = d # can use datetime from gui...
    Raw_Data_All[0,:,:,:] = h
    Header[0,:,:] = st.head

def data(h,d,n,a):
    Time[0] = str(now.datetime.utcnow())
    Rms_Noise[0,:,:] = d
    Raw_Data[0,:,:,:] = h
    Header[0,:,:] = st.head
