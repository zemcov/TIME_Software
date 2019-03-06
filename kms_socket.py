# I'm accepting positional updates from the KMS for the gui
# sending end will be from KMS socket
# receiving end is the gui

import socket, struct, subprocess, os, sys, time
import time as othertime
import numpy as np

def start_tracker(queue):
    PORT = 8500
    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    s.bind(('',PORT))
    print('Server Listening')
    s.listen(5)
    client, info = s.accept()
    print('Socket Connected')
    unpacker = struct.Struct('d d d d') # d = float , s = char string , i = integer

    n = 0
    while not ut.tel_exit.is_set() :
        data = client.recv(unpacker.size)
        if len(data) !=0 :
            # print('Data Received')
            # unpacking data packet ===============================================
            pa, flag, time, enc_pos = unpacker.unpack(data)
            # print('pa:',pa)
            # ==================================================================
            kms_data = np.array([float(pa),float(flag),float(time),float(enc_pos)])
            np.save('/home/time/time-software-testing/TIME_Software/main/tempfiles/kms_packet%i.npy' %(n), kms_data)
            # send positional data to gui window
            queue.send([pa, flag, time, enc_pos])
            n += 1

        else :
            print('waiting for data')

    s.close()
    sys.exit()
