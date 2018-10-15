import numpy as np
import sys
import datetime
import os
import subprocess
import time
from termcolor import colored

sys.stdout = os.fdopen(sys.stdout.fileno(), 'w', 1) # line buffering

def main(observer='VLB', datamode='0', readoutcard='s', framenumber='13500000', datarate='45'):
    run = raw_input('Press enter to run')
    print('\n')
    netcdfdir = ('/home/time/Desktop/time-data/netcdffiles')
    if os.path.exists(netcdfdir):
        print colored('netcdfdir exists','blue')
    else:
        print colored('Making NETCDF File Directory','green')
        netcdf_dir = ['mkdir /home/time/Desktop/time-data/netcdffiles']
        subprocess.Popen(netcdf_dir, shell=True).wait()

    mcedir1 = ('/home/time/Desktop/time-data/mce1')
    if os.path.exists(mcedir1):
        print colored('mcedir1 exists','blue')
    else:
        print colored('Making MCE0 File Directory','green')
        mce_dir1 = ['mkdir /home/time/Desktop/time-data/mce1']
        subprocess.Popen(mce_dir1, shell=True).wait()

    mcedir2 = ('/home/time/Desktop/time-data/mce2')
    if os.path.exists(mcedir2):
        print colored('mcedir2 exists','blue')
    else :
        print colored('Making MCE1 File Directory','green')
        mce_dir2 = ['mkdir /home/time/Desktop/time-data/mce2']
        subprocess.Popen(mce_dir2, shell=True).wait()

    if os.path.exists('tempfiles/stop.txt'):
        subprocess.Popen('rm tempfiles/stop.txt', shell=True)

    # print('Observer: %s' % (observer))
    # print('Datamode: %s' % (datamode))
    # print('Readout Card: %s' % (readoutcard))
    # print('Frame Number: %s' % (framenumber))
    # print('Data Rate: %s' % (datarate))

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

    editdatarate1 = ['./mce0_cdr.sh %s' %(datarate)]
    subprocess.call(editdatarate1, shell=True)
    editdatarate2 = ['./mce1_cdr.sh %s' %(datarate)]
    subprocess.call(editdatarate2, shell=True)

    if readoutcard == 's':
        changedatamode1 = ["./mce0_cdm.sh a %s" % (datamode)]
        subprocess.Popen(changedatamode1, shell=True)
        changedatamode2 = ["./mce1_cdm.sh a %s" % (datamode)]
        subprocess.Popen(changedatamode2, shell=True)
        run1 = ["./mce0_run.sh %s s %s" %(framenumber, frameperfile)]
        run2 = ["./mce1_run.sh %s s %s" %(framenumber, frameperfile)]
        print colored("starting MCE0 & MCE1",'magenta')
        subprocess.Popen(run1, shell=True)
        subprocess.Popen(run2, shell=True)
        #changedatamode2 = ["./mce1_cdm.sh %s" % (datamode)]
        #d = subprocess.Popen(changedatamode2, shell=True)
        #run2 = ["./mce1_run.sh %s a %s" %(framenumber, frameperfile)]
        #e = subprocess.Popen(run2, shell=True)
    else:
        changedatamode1 = ["./mce0_cdm.sh %s %s" % (readoutcard, datamode)]
        subprocess.Popen(changedatamode1, shell=True)
        changedatamode2 = ["./mce1_cdm.sh %s %s" % (readoutcard, datamode)]
        subprocess.Popen(changedatamode2, shell=True)
        run1 = ["./mce0_run.sh %s %s %s" %(framenumber, readoutcard, frameperfile)]
        run2 = ["./mce1_run.sh %s %s %s" %(framenumber, readoutcard, frameperfile)]
        print colored("starting MCE0 & MCE1",'magenta')
        subprocess.Popen(run1, shell=True)
        subprocess.Popen(run2, shell=True)
        #changedatamode2 = ["./mce1_cdm.sh %s %s" % (readoutcard, datamode)]
        #d = subprocess.Popen(changedatamode2, shell=True)
        #run2 = ["./mce1_run.sh %s %s %s" %(framenumber, readoutcard, frameperfile)]
        #e = subprocess.Popen(run2, shell=True)
    subprocess.Popen(['python read_files.py %s' %(readoutcard)], shell=True)


if __name__ == '__main__':
    main(sys.argv[1], sys.argv[2], sys.argv[3], sys.argv[4], sys.argv[5])
