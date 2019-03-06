# this parses telescope data files
import numpy as np
import utils as ut
import os, subprocess, sys
from termcolor import colored

dir = '/home/time/time-software-testing/TIME_Software/main/tempfiles/'
mega_tel = []

def loop_files(queue3):

    while True :

        files = [dir + x for x in os.listdir(dir) if x.startswith("tele_packet")]
        if os.path.isfile(dir + 'tele_packet_off1.npy') :
            tel_data = np.zeros((20,20))
            queue3.send(tel_data)
            continue

        if len(files) != 0 : # check for at least 2 files to exist
            tel_file = min(files, key = os.path.getctime) # grab the oldest of the unparsed files
            a = int(tel_file.replace(dir,'').replace('tele_packet','').replace('.npy',''))
            print(colored('TEL starting file = %i' %(a),'green'))
            break

        else :
            continue

        while not ut.tel_exit.is_set():
            if os.path.exists(dir + 'tele_packet%i.npy' %(a+1)) : #wait to read new file until old file is complete
                a += 1
                tele_file = dir + 'tele_packet%i.npy' %(a)
                print(colored('TEL file' %(tele_file),'green'))
                data = np.load(tele_file)
                mega_tel.append(data)
                subprocess.Popen(['rm %s' %(tele_file)], shell=True)

            if a % 20 == 0 :
                queue3.send(mega_tel)
                mega_tel = []
