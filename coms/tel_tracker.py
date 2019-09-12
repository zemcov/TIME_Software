from __future__ import division
import socket, struct, subprocess, os, sys
import time
import numpy as np
import utils as ut
from termcolor import colored
from config import *
sys.path.append('../TIME_Software/main/tempfiles')

def start_tracker(queue):
    # os.nice(-20)
    PORT = 4444
    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    s.bind(('',PORT))
    print('Tracker Server Listening')
    s.listen(5)
    client, info = s.accept()
    print(colored('Socket Connected','red'))
    unpacker = struct.Struct('i i i i d d d d d d d d d d d d d d d d Q Q')
    n = 0
    mega_tel = []

    while not ut.tel_exit.is_set() :
        data = client.recv(unpacker.size)
        if len(data) !=0 :
            # unpacking data packet ===============================================
            blanking, direction, observing, pad, utc, lst, deltaT, cur_ra, cur_dec,\
            map_ra, map_dec, ra_off, dec_off, az, el, azvelcmd, elvelcmd, azvelact,\
            elvelact, pa, unix_val, unix_delta = unpacker.unpack(data)
            # =======================================================================

            unix = float(unix_val) + float(unix_delta) / 10**(6) - (7*3600) # because unix time is mountain timezone
            # ------------------------------------------------------------------------
            tel_data = np.array([int(blanking), int(direction), float(observing), float(pad), \
            utc, lst, deltaT, cur_ra, cur_dec, map_ra, map_dec, \
            ra_off, dec_off, az, el, azvelcmd, elvelcmd, azvelact, elvelact, \
            pa, unix])

            if len(mega_tel) < 20:
                mega_tel.append(tel_data)
            else :
                print('Tel Time:', unix_val , unix_delta)
                np.save(config.temp_dir + '/tele_packet%i.npy' %(n), mega_tel)
                mega_tel = []
                mega_tel.append(tel_data)
                n += 1

            # send positional data to gui window
            queue.send([pa,int(direction),el,az,map_ra,map_dec,utc])
        else :
            print('waiting for data')

    s.close()
    sys.exit()
