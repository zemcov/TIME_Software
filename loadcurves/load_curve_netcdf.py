import netCDF4 as nc
import os, sys
import time as t
import datetime as now
import numpy as np
from termcolor import colored
import utils as ut


class LcDataFile():
    def __init__(self, identifier, dir):
        self.new_lc_file(identifier, dir)

    def new_lc_file(self, filestarttime,dir):
        """
        Purpose: to create a new netcdf file for the mce/K-mirror/telescope data
        Inputs: filestarttime - the time of the first set of data that is appended to the file
                dir - the directory in which you want to create the netcdf files
        Outputs : None
        Calls : None
        """
        lc = nc.Dataset(dir + "/loadcurve_%s.nc" %(filestarttime),"w",format="NETCDF4_CLASSIC")

        lc.createDimension('t',None)
        lc.createDimension('det', 1)
        lc.createDimension('rows',33)
        lc.createDimension('cols',32)
        lc.createDimension('num',100)
        lc.createDimension('raw_num', int(ut.german_freq))
        lc.createDimension('v',1700)
        lc.createDimension('k',1)

        # global Time
        self.time = lc.createVariable('time','f8',('t','time_num','mode'))

        self.mce0_data = lc.createVariable('mce0_data', 'f8', ('t', 'rows', 'cols', 'num'))
        self.mce1_data = lc.createVariable('mce1_data', 'f8', ('t', 'rows', 'cols', 'num'))
        # =========================================================================================================

        self.mce0_header = lc.createVariable('mce0_header','f8',('t','v','k'))
        self.mce1_header = lc.createVariable('mce1_header','f8',('t','v','k'))
        # =========================================================================
        lc.close()
        return

    def data_append(self, nc_file, p, times, mce0_head, mce1_head, mce0_data, mce1_data):
        """
        Purpose: to append data to the netcdf file created in the above function
        inputs: nc_file - the file in which you want to append data to
                p - the index we are appending to

        Outputs: None
        Calls : None
        """
        if os.path.exists(nc_file): #check that the new file exists:
            lc = nc.Dataset(nc_file,"r+",format="NETCDF4_CLASSIC")
            self.time[p,:,:] = times

            if ut.which_mce[0] == 1 :
                self.mce0_data[p,:,:,:] = mce0_data
                self.mce0_header[p,:,:] = head1

            if ut.which_mce[1] == 1 :
                self.mce1_data[p,:,:,:] = mce1_data
                self.mce1_header[p,:,:] = head2

            lc.close()
        else :
            print(colored("Could find NETCDF File!", 'red'))
