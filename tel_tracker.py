import socket, struct, subprocess, os, sys
import time
import numpy as np
import utils as ut

def start_tracker(queue):
    PORT = 4444
    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    s.bind(('',PORT))
    print('Server Listening')
    s.listen(5)
    client, info = s.accept()
    print('Socket Connected')
    unpacker = struct.Struct('i i i i d d d d d d d d d d d d d d d d') # d = float , s = char string , i = integer
    n = 0
    mega_tel = []

    while not ut.tel_exit.is_set() :
        data = client.recv(unpacker.size)
        if len(data) !=0 :
            # unpacking data packet ===============================================
            blanking, direction, observing, pad, utc, lst, deltaT, cur_ra, cur_dec,\
            map_ra, map_dec, ra_off, dec_off, az, el, azvelcmd, elvelcmd, azvelact,\
            elvelact, pa = unpacker.unpack(data)
            # print('ut:',ut)
            # ==================================================================
            tel_data = np.array([int(blanking), int(direction), float(observing), float(pad), \
            utc, lst, deltaT, cur_ra, cur_dec, map_ra, map_dec, \
            ra_off, dec_off, az, el, azvelcmd, elvelcmd, azvelact, elvelact, \
            pa])

            if len(mega_tel) < 20:
                mega_tel.append(tel_data)
            else :
                print('Tel UTC:',utc)
                np.save('/home/time/time-software-testing/TIME_Software/main/tempfiles/tele_packet%i.npy' %(n), mega_tel)
                mega_tel = []
                mega_tel.append(tel_data)
                n += 1

            # send positional data to gui window
            queue.send([pa,int(direction),el,az,map_ra,map_dec,utc])
        else :
            print('waiting for data')

    s.close()
    sys.exit()
