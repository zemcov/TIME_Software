import netCDF4 as nc
import os
import sys
#import takedata_test as td
import datetime as now
import numpy as np
from termcolor import colored

mce = nc.Dataset('/Users/vlb9398/Desktop/netcdf_overhead_file.nc',"w",format="NETCDF4_CLASSIC")
mce.createDimension('time',None)
mce.createDimension('hk',1)


for i in range(210):
    name = str(i)
    name = mce.createVariable(name + '_NC','f8',('time','hk','hk'))
mce.close()
print(colored(os.stat('/Users/vlb9398/Desktop/netcdf_overhead_file.nc').st_size,'red'))
