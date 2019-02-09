import numpy as np
import sys
import datetime
import os
import subprocess
import time
from termcolor import colored

#sys.stdout = os.fdopen(sys.stdout.fileno(), 'w', 1) # line buffering

def main(observer='VLB', datamode='0', readoutcard='s', framenumber='13500000', datarate='45'):
    #run = input('Press enter to run')
    #print('\n')

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
    print(colored("starting MCE0 & MCE1",'magenta'))
    subprocess.Popen(['python read_files_local.py %s' %(readoutcard)], shell=True)

if __name__ == '__main__':
    main('VLB', '0', 's', '13500000', '45')
