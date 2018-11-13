import numpy as np
from os import stat
import os
import sys
import mce_data
import netcdf as nc
import subprocess
import datetime as dt
import gzip
from termcolor import colored

sys.stdout = os.fdopen(sys.stdout.fileno(), 'w', 1) # line buffering

def netcdfdata(rc):
    a = 0
    mce = 0
    n = 0
    filestarttime = 0
    h1_shape = 0
    h2_shape = 0
    dir1 = '/home/time/Desktop/time-data/mce1/'
    dir2 = '/home/time/Desktop/time-data/mce2/'
    dir3 = '/home/time/Desktop/time-data/hk/'
    subprocess.Popen(['ssh -T time@time-mce-1.caltech.edu python /home/time/time-software-testing/TIME_Software/sftp/mce1_sftp.py'] , shell=True)
    subprocess.Popen(['ssh -T time@time-mce-0.caltech.edu python /home/time/time-software-testing/TIME_Software/sftp/mce0_sftp.py'], shell=True)
    subprocess.Popen(['ssh -T time@time.pyhk.net python /home/time/time-software-testing/TIME_Software/sftp/hk_sftp.py'], shell=True)
    begin = dt.datetime.utcnow()
    end = dt.datetime.utcnow()
    while end - begin < dt.timedelta(seconds = 5):
        mce_file1 = os.path.exists(dir1 + 'temp.%0.3i' %(a+1))
        mce_file2 = os.path.exists(dir2 + 'temp.%0.3i' %(a+1))
        hk_file = len(os.listdir(dir3))
        if (mce_file1 and mce_file2 and hk_file != 0):
            files1 = [dir1 + x for x in os.listdir(dir1) if (x.startswith("temp") and not x.endswith('.run'))]
            files2 = [dir2 + x for x in os.listdir(dir2) if (x.startswith("temp") and not x.endswith('.run'))]
            files3 = [dir3 + x for x in os.listdir(dir3) if (x.startswith('omnilog'))]
            print colored('num of hk files : %s' %(len(files3)),'magenta')
            if (len(files1) and len(files2)) != 0:
                mce1 = min(files1, key = os.path.getctime)
                mce2 = min(files2, key = os.path.getctime)
                #hk = min(files3, key = os.path.getctime)
                f1 = mce_data.SmallMCEFile(mce1)
                f2 = mce_data.SmallMCEFile(mce1)
                hk_data, hk_time, hk_sensors, tele_time, hk_size, t_type, hk_files = hk_read(files3)
                header1 = read_header(f1)
                header2 = read_header(f2)
                mce, n, filestarttime = readdata(h1_shape,h2_shape,f1, f2, mce, header1, header2, n, a, filestarttime, rc,
                                                    mce1, mce2, hk_data, hk_time, hk_sensors, tele_time, hk_size, t_type, hk_files)
                #print colored('File Read: mce1:%s , mce2:%s , hk:%s' %(str(mce1).replace(dir1,''),str(mce1).replace(dir2,''),str(hk).replace(dir3,'')),'yellow')
                a = a + 1
                begin = dt.datetime.utcnow()
        end = dt.datetime.utcnow()

    else :
        print colored('No More Files','red')
        subprocess.Popen(['rm /home/time/Desktop/time-data/mce1/temp.run'], shell=True)
        subprocess.Popen(['rm /home/time/Desktop/time-data/mce2/temp.run'], shell=True)
        subprocess.Popen(['ssh -T time@time.pyhk.net pkill -9 -f hk_sftp.py'], shell=True)
        sys.exit()

# ===========================================================================================================================
def readdata(h1_shape,h2_shape,f1, f2, mce, head1, head2, n, a, filestarttime, rc, mce_file1, mce_file2,
             hk_data, hk_time,hk_sensors, tele_time, hk_size, t_type, hk_files):
    h1 = f1.Read(row_col=True, unfilter='DC').data
    h2 = f2.Read(row_col=True, unfilter='DC').data
    # -------CHECK FOR FRAME SIZE CHANGE--------------------------------
    if n != 0 :
        if (h1.shape != h1_shape and h2.shape != h2_shape) :
            print colored('WARNING! Both MCE Frame Size Has Changed','red')
        elif h1.shape != h1_shape :
            print colored('WARNING! MCE0 Frame Size Has Changed','red')
        else :
            print colored('WARNING! MCE1 Frame Size Has Changed','red')
    h1_shape = h1.shape
    h2_shape = h2.shape
    # -----------------------------------------------------------------
    # d1 = np.empty([h.shape[0],h.shape[1]],dtype=float)
    # for b in range(h.shape[0]):
    #     for c in range(h.shape[1]):
    #         d1[b][c] = (np.std(h1[b][c][:],dtype=float))
    # d2 = np.empty([h.shape[0],h.shape[1]],dtype=float)
    # for b in range(h.shape[0]):
    #     for c in range(h.shape[1]):
    #         d2[b][c] = (np.std(h2[b][c][:],dtype=float))
    # -----------------------------------------------------------------
    subprocess.Popen(['rm %s' % (mce_file1)], shell=True)
    subprocess.Popen(['rm %s' % (mce_file2)], shell=True)
    netcdfdir = '/home/time/Desktop/time-data/netcdffiles'
    if n == 0:
        filestarttime = datetime.datetime.utcnow()
        filestarttime = filestarttime.isoformat()
        print colored('------------ New File -------------','green')
        mce = nc.new_file(h1.shape, head1, head2, filestarttime, hk_size, hk_files)
        if rc == 's' :
            nc.data_all(h1, h2, n, head1, head2, filestarttime, hk_data, hk_sensors, hk_time, tele_time, t_type)
        else :
            print colored('Wrong RC Input!','red')

    elif os.stat(netcdfdir + "/raw_%s.nc" % (filestarttime)).st_size >= 20 * 10**6:
        n = 0
        print colored('----------- New File ------------','green')
        filestarttime = datetime.datetime.utcnow()
        filestarttime = filestarttime.isoformat()
        mce = nc.new_file(h1.shape, head1, head2, filestarttime, hk_size, hk_files)
        if rc == 's' :
            nc.data_all(h1, h2, n, head1, head2, filestarttime, hk_data, hk_sensors, hk_time, tele_time, t_type)
        else :
            print colored('Wrong RC Input!','red')

    else:
        if rc == 's' :
            nc.data_all(h1, h2, n, head1, head2, filestarttime, hk_data, hk_sensors, hk_time, tele_time, t_type)
        else :
            print colored('Wrong RC Input!','red')
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
                    value[i] = '1'
                elif value[i] == False:
                    value[i] = '0'
                else:
                    print("I don't know what I am...")
            value = ''.join(map(str,value))
        value = int(value)
        values.append(value)
    values = np.asarray(values)
    return values

# ============================================================================
def hk_read(hk):
    hk_sensor = [[]]
    time = [[]]
    sensor = [[]]
    name = [[]]
    data = [[]]
    t_type = [[]]
    tele_time = [(0.0,0.0)]

    # telling netcdf how many files worth of hk data to expect
    hk_files = len(hk)
    for i in range(len(hk)-1):
        file = gzip.open(hk[i])
        for line in file:
            #fields = line.strip().split(',')
            a,b,c,d,e = line.strip().split(',')
            t_type.append(a)
            time.append(b)
            sensor.append(c)
            name.append(d)
            data.append(e)

            # t_type.append(fields[0])
            # time.append(fields[1])
            # sensor.append(fields[2])
            # name.append(fields[3])
            # data.append(float(fields[4]))

    # telling netcdf how many sensors to account for in the array size
        hk_size = len(sensor)
        for j in range(len(sensor)):
            hk_sensor.append((sensor[j] + "_" + name[j]).replace('"',''))
            if hk_sensor[i] == 'HKMBv1b0_SYNC_number' :
                tele_time = float(time[j]),data[j]
                #print colored(tele_time,'red')

    # delete old hk files
    for i in range(len(hk)) :
        subprocess.Popen(['rm %s' % (hk[i])], shell=True)

    return data, time, hk_sensor, tele_time, hk_size, t_type, hk_files

# ============================================================================
if __name__ == '__main__':
    netcdfdata(sys.argv[1])
