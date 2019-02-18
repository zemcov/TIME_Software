import socket, struct, subprocess, os, sys, time
import time as othertime
import numpy as np

def start_sock(ra,dec):
    # I am accepting telescope sim data for the gui
    PORT = 8000
    HOST = '192.168.1.252'
    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    s.connect((HOST,PORT))
    print('Socket Connected')
    unpacker = struct.Struct('d d d d') # d = float , s = char string , i = integer
    time.sleep(1.0)
    # =================================================================================================================
    n = 0

    while True:

        if ut.tel_exit.is_set(): # if shutdown command from software, send shutdown command to tel
            print("Client Shutting Down")
            stop_msg = 'end'
            s.send(stop_msg.encode())
            break

        else :
            msg = 'go'
            s.send(msg.encode())
            data = s.recv(unpacker.size)
            # unpacking data packet ===============================================
            pa, flag, time, enc_pos = unpacker.unpack(data)
            # ==================================================================
            n += 1
            kms_data = np.array([])
            np.save('/home/time/time-software-testing/TIME_Software/main/tempfiles/kms_packet%i.npy' %(n), kms_data)
            # send positional data to gui window
            queue.send([pa, flag, time, enc_pos])

    print("KMS Socket Closed")
    s.close()
    sys.exit()
