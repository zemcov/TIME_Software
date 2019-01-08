import numpy as np
import sys
import datetime
import os
import subprocess
import time
from termcolor import colored

#sys.stdout = os.fdopen(sys.stdout.fileno(), 'w', 1) # line buffering

def main(observer='VLB', datamode='0', readoutcard='s', framenumber='13500000', datarate='45'):
    run = raw_input('Press enter to run')
    print('\n')
    netcdfdir = ('/Users/vlb9398/Desktop/netcdffiles')
    mcedir1 = ('/Users/vlb9398/Desktop/test_mce_files')
    mcedir2 = ('/Users/vlb9398/Desktop/test_mce_files_copy')
    hkdir = ('/Users/vlb9398/Desktop/test_hk_files')

    # if os.path.exists('tempfiles/stop.txt'):
    #     subprocess.Popen('rm tempfiles/stop.txt', shell=True)

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
    print colored("starting MCE0 & MCE1",'magenta')
    subprocess.Popen(['python read_files_local.py %s' %(readoutcard)], shell=True)

if __name__ == '__main__':
    main(sys.argv[1], sys.argv[2], sys.argv[3], sys.argv[4], sys.argv[5])
