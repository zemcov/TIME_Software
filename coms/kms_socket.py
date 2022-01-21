# I'm accepting positional updates from the KMS for the gui
# sending end will be from KMS socket
# receiving end is the gui

import socket, struct, subprocess, os, sys, time
import time as othertime
import numpy as np
import config.utils as ut
from config import directory

def start_sock(queue):
    """
    Purpose: to open a socket for getting K-mirror data from the K-mirror computer and
    then sending that data to the GUI
    Inputs: KMS Socket (data = client.recv)
    Outputs: None
    Calls : queue.send()
    """
    PORT = 8500
    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    s.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    s.bind(('',PORT))
    print('KMS GUI Socket Listening')
    s.listen(5)
    client, info = s.accept()
    print('KMS GUI Socket Connected')
    unpacker = struct.Struct('d i d d') # d = float , s = char string , i = integer
    kms_data = []
    n = 0
    while not ut.tel_exit.is_set():
        data = client.recv(unpacker.size)
        if len(data) !=0 :
            # print('Data Received')
            # unpacking data packet ===============================================
            pa, flag, time, enc_pos = unpacker.unpack(data)
            # ==================================================================
            if len(kms_data) < 20 :
                kms_data.append(np.array([float(pa),float(flag),float(time),float(enc_pos)]))

            else :
                np.save(directory.temp_dir + 'kms_packet%i.npy' %(n/20), kms_data)
                kms_data = []
                kms_data.append(np.array([float(pa),float(flag),float(time),float(enc_pos)]))
            # send positional data to gui window
            queue.send([pa, flag, time, enc_pos])
            n += 1

        else :
            print('waiting for data')

    s.shutdown(1)
    s.close()
    sys.exit()
