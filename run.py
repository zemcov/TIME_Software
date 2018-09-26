import numpy as np
import sys
import datetime
import os
import subprocess
import time

def main(observer='VLB', datamode='0', readoutcard='s', framenumber='13500000', datarate='45'):
    netcdfdir = ('/home/pilot1/Desktop/time-data/netcdffiles')
    if os.path.exists(netcdfdir):
        print('netcdfdir exists')
    else:
        print('Making NETCDF File Directory')
        netcdf_dir = ['mkdir /home/pilot1/Desktop/time-data/netcdffiles']
        subprocess.Popen(netcdf_dir, shell=True).wait()
    mcedir = ('/home/pilot1/Desktop/time-data/mce1')
    if os.path.exists(mcedir):
        print('mcedir exists')
    else:
        print('Making MCE File Directory')
        mce_dir = ['mkdir /home/pilot1/Desktop/time-data/mce1']
        subprocess.Popen(mce_dir, shell=True).wait()

    print('Observer: %s' % (observer))
    print('Datamode: %s' % (datamode))
    print('Readout Card: %s' % (readoutcard))
    print('Frame Number: %s' % (framenumber))
    print('Data Rate: %s' % (datarate))

    parafile = open('tempfiles/tempparameters.txt', 'w')
    parafile.write(observer+' ')
    parafile.write(str(datamode)+' ')
    parafile.write(str(readoutcard)+' ')
    parafile.write(framenumber+' ')
    parafile.write(datarate+' ')
    parafile.close()

    startmce(observer, datamode, readoutcard, framenumber, datarate)

def startmce(observer, datamode, readoutcard, framenumber, datarate):
    frameperfile = int((50 * 10 ** 6) / (33 * 90 * int(datarate)))

    editdatarate = ['./mce1_cdr.sh %s' %(datarate)]
    a = subprocess.call(editdatarate, shell=True)

    if readoutcard == 's':
        changedatamode1 = ["./mce1_cdm.sh a %s" % (datamode)]
        b = subprocess.Popen(changedatamode1, shell=True)
        run1 = ["./mce1_run.sh %s s %s" %(framenumber, frameperfile)]
        print("starting mce1")
        c = subprocess.Popen(run1, shell=True)
        #changedatamode2 = ["./mce1_cdm.sh %s" % (datamode)]
        #d = subprocess.Popen(changedatamode2, shell=True)
        #run2 = ["./mce1_run.sh %s a %s" %(framenumber, frameperfile)]
        #e = subprocess.Popen(run2, shell=True)
    else:
        changedatamode1 = ["./mce1_cdm.sh %s %s" % (readoutcard, datamode)]
        b = subprocess.Popen(changedatamode1, shell=True)
        print("starting mce1")
        run1 = ["./mce1_run.sh %s %s %s" %(framenumber, readoutcard, frameperfile)]
        c = subprocess.Popen(run1, shell=True)
        #changedatamode2 = ["./mce1_cdm.sh %s %s" % (readoutcard, datamode)]
        #d = subprocess.Popen(changedatamode2, shell=True)
        #run2 = ["./mce1_run.sh %s %s %s" %(framenumber, readoutcard, frameperfile)]
        #e = subprocess.Popen(run2, shell=True)
    f = open('tempfiles/tempteledata.txt','w')
    f.close()
    subprocess.Popen(['ssh -T pilot2@timemce.rit.edu /home/pilot2/anaconda3/bin/python /home/pilot2/TIME_Software/tel_sock.py'], shell=True)
    print('Tel Server Started')
    subprocess.Popen(['python readteledata.py'],shell=True)
    subprocess.Popen(['python read_files.py %s' %(readoutcard)], shell=True)

if __name__ == '__main__':
    main(sys.argv[1], sys.argv[2], sys.argv[3], sys.argv[4], sys.argv[5])
