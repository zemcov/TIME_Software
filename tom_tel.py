import socket, struct, subprocess, os, sys
# from socket import htonl
import time
import numpy as np

def start_sock_tracker():
    PORT = 8888
    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    s.bind(('',PORT))
    print('Server Listening')
    s.listen(5)
    client, info = s.accept()
    print('Socket Connected')
    unpacker = struct.Struct('i i i i d d d d d d d d d d d d d d d d') # d = float , s = char string , i = integer
    i = 0
    while True :
        data = client.recv(unpacker.size)
        if i < 3 :
            if len(data) !=0 :
                # print('package size',unpacker.size)
                # print('Data Received')
                # unpacking data packet ===============================================
                blanking, direction, observing, pad, ut, lst, deltaT, cur_ra, cur_dec,\
                map_ra, map_dec, ra_off, dec_off, az, el, azvelcmd, elvelcmd, azvelact,\
                elvelact, pa = unpacker.unpack(data)
                # print('ut:',ut)
                # ==================================================================
            else :
                print('waiting for data')
                i += 1
        else :
            break

    s.close()
    sys.exit()

if __name__ == '__main__' :
    start_sock_tracker()
