import numpy as np
from os import stat
import os
import sys
import mce_data
import netcdf as nc
import subprocess
import datetime
from termcolor import colored

#sys.stdout = os.fdopen(sys.stdout.fileno(), 'w', 1) # line buffering
def netcdfdata(rc):
    a = 0
    mce = 0
    n = 0
    filestarttime = 0
    dir1 = '/home/time/Desktop/time-data/mce1/'
    dir2 = '/home/time/Desktop/time-data/mce2/'
    subprocess.Popen(['ssh -T time@time-mce-1.caltech.edu python /home/time/time-software-testing/TIME_Software/sftp/mce1_sftp.py'] , shell=True)
    subprocess.Popen(['ssh -T time@time-mce-0.caltech.edu python /home/time/time-software-testing/TIME_Software/sftp/mce0_sftp.py'], shell=True)
    while True:
        mce_file1 = os.path.exists('/home/time/Desktop/time-data/mce1/temp.%0.3i' %(a+1))
        mce_file2 = os.path.exists('/home/time/Desktop/time-data/mce2/temp.%0.3i' %(a+1))
        if (mce_file1 and mce_file2):
            files1 = [dir1 + x for x in os.listdir(dir1) if (x.startswith("temp") and not x.endswith('.run'))]
            files2 = [dir2 + x for x in os.listdir(dir2) if (x.startswith("temp") and not x.endswith('.run'))]
            if (len(files1) and len(files2)) != 0:
                mce_file1 = min(files1, key = os.path.getctime)
                mce_file2 = min(files2, key = os.path.getctime)
                f1 = mce_data.SmallMCEFile(mce_file1)
                f2 = mce_data.SmallMCEFile(mce_file2)
                header1 = read_header(f1)
                header2 = read_header(f2)
                mce, n, filestarttime = readdata(f1, f2, mce, header1, header2, n, a, filestarttime, rc, mce_file1, mce_file2)
                print colored('File Read: %s , %s' %(mce_file1.replace(dir1,''),mce_file2.replace(dir2,'')),'yellow')
                a = a + 1

    else :
        print colored('No More Files','red')
        subprocess.Popen(['rm /home/time/Desktop/time-data/mce1/temp.run'], shell=True)
        subprocess.Popen(['rm /home/time/Desktop/time-data/mce2/temp.run'], shell=True)
        sys.exit()

# ===========================================================================================================================
def readdata(f1, f2, mce, head1, head2, n, a, filestarttime, rc, mce_file1, mce_file2):
    h1 = f1.Read(row_col=True, unfilter='DC').data
    h2 = f2.Read(row_col=True, unfilter='DC').data
    # d1 = np.empty([h.shape[0],h.shape[1]],dtype=float)
    # for b in range(h.shape[0]):
    #     for c in range(h.shape[1]):
    #         d1[b][c] = (np.std(h1[b][c][:],dtype=float))
    # d2 = np.empty([h.shape[0],h.shape[1]],dtype=float)
    # for b in range(h.shape[0]):
    #     for c in range(h.shape[1]):
    #         d2[b][c] = (np.std(h2[b][c][:],dtype=float))

    subprocess.Popen(['rm %s' % (mce_file1)], shell=True)
    subprocess.Popen(['rm %s' % (mce_file2)], shell=True)
    netcdfdir = '/home/time/Desktop/time-data/netcdffiles'
    if n == 0:
        filestarttime = datetime.datetime.utcnow()
        filestarttime = filestarttime.isoformat()
        print colored('------------ New File -------------','green')
        mce = nc.new_file(h1.shape, head1, head2, filestarttime)
        if rc == 's' :
            nc.data_all(h1, h2, n, head1, head2, filestarttime)
        else :
            nc.data(h1, h2, n, head1, head2, filestarttime)

    elif os.stat(netcdfdir + "/raw_%s.nc" % (filestarttime)).st_size >= 20 * 10**6:
        n = 0
        print colored('----------- New File ------------','green')
        filestarttime = datetime.datetime.utcnow()
        filestarttime = filestarttime.isoformat()
        mce = nc.new_file(h1.shape, head1, head2, filestarttime)
        if rc == 's' :
            nc.data_all(h1, h2, n, head1, head2, filestarttime)
        else :
            nc.data(h1, h2, n, head1, head2, filestarttime)

    else:
        if rc == 's' :
            nc.data_all(h1, h2, n, head1, head2, filestarttime)
        else :
            nc.data(h1, h2, n, head1, head2, filestarttime)
    n = n + 1
    return mce, n, filestarttime

# ===========================================================================
def read_header(f):
    keys = []
    values = []
    for key,value in f.header.items():
        if key == '_rc_present':
            for i in range(len(value)):
                if value[i] == True:
                    value[i] = "1"
                elif value[i] == False:
                    value[i] = "0"
                else:
                    print("I don't know what I am...")
            value = ''.join(map(str,value))
        value = str(value)
        keys.append(key)
        values.append(value)
    keys = np.asarray(keys,dtype=object)
    values = np.asarray(values,dtype=object)
    head = np.array((keys,values)).T
    return head

if __name__ == '__main__':
    netcdfdata(sys.argv[1])
