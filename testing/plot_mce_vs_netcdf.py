# let's the user choose which data to pull out of which files
import netCDF4 as nc
from netCDF4 import MFDataset
import sys, time
import numpy as np
import subprocess
import argparse
import os
import matplotlib.pyplot as plt
import timefpu.mce_data as mce_data

def extract_data(file,type):
    """
    Purpose: To extract all of the data in a file(s) even the errors
    Inputs: File - the name of the file(s) to be read
    Outputs:
    data - an array of mce data including raw data, header data, and on_off data.
    0 - A list of all times without errors [100 * number of files, 2]
    1 - mce0_raw_data without errors [100 * number of files, 33, 32, 100]
    2 - mce1_raw_data without errors [100 * number of files, 33, 32, 100]
    3 - mce0 on off data without errors [100 * number of files, 33, 32]
    4 - mce1 on off data without errors [100 * number of files, 33, 32]
    5 - head0 - mce0_header data without errors [100 * number of files, 1700, 1]
    6 - head1 - mce1 header data without errors [100 * number of files, 1700, 1]
    7 - status flags data without errors [100 * number of files, 1, 5]
    tel_data - an array of telescope data [100 * number of files, 20, 21]
    """
    f = nc.Dataset(file)
    if type != 'mce' and type != 'hk' :
        data = []
        counter = 0
        for var in f.variables: # assumption that all files have the same variables
            if 'mce0_raw_data' in var: # or var == 'status' or var == 'time':
                print('collecting %s data' % (var))
                mce0_raw_data =  f.variables[var]
                counter += 1
        return mce0_raw_data, None


    else :
        f = nc.MFDataset(file)
        unix = f.variables['time'][:, 0]
        data = []
        counter = 0
        for var in f.variables:
            if 'mce' in var or var == 'status' or var == 'time':
                print('collecting %s data' % (var))
                data.append([])
                data[counter].append(f.variables[var][:])
                counter += 1

        print('collecting tel_data')
        tel_data = f.variables['tel'][:]
        return data, tel_data


def load_and_plot_data(filename, col, row):
    col = int(col); row=int(row) #force thse to be integers

    mce_data, tel_data = extract_data(filename, type='unknown')
    mce_data = mce_data[0,:,:,:]
    print(mce_data.shape)
    y = mce_data[row, col, :]


    f = mce_data.MCEFile(tempfile)
    l = f.Read(row_col=True, unfilter='DC', all_headers=True)
    h = l.data

    print(h.shape)

    x = np.arange(0,len(y)*0.001,0.001)
    plt.scatter(x, h[row, col], label='tempfile')
    plt.scatter(x, y+ 0.5,label='netcdffile') # label = 'Row: %s Col: %s' %(row,col),
    plt.xlabel('Time')
    plt.ylabel('ADU')
    plt.legend()
    plt.grid()
    plt.title(str(filename))
    plt.legend()
    plt.show()


if __name__ == '__main__':
    print('start')
    ### Example files to load in
    tempfile = '/data/netcdffiles/staging/mce0/temp.001'
    filename = '/data/netcdffiles/1628124297/raw_mce_2021-08-05T00:45:06.061249.nc'
    parser = argparse.ArgumentParser()
    parser.add_argument('-plot', nargs=3, metavar=('filename', 'col', 'row'), default='-d')
    args = parser.parse_args()
    load_and_plot_data(filename, 3, 4)
