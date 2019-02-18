import socket, struct, subprocess, os, sys
# from socket import htonl
import time
import numpy as np
import multiprocessing as mp

def start_sock_tcomm():
    PORT = 8888
    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    s.bind(('',PORT))
    print('Server Listening')
    s.listen(5)
    client, info = s.accept()
    print('Socket Connected')
    unpacker = struct.Struct('s i i i i d d d d d d d d d d d d d d d d') # d = float , s = char string , i = integer

    while True :
        data = client.recv(unpacker.size)
        print('package size',unpacker.size)
        print('Data Received')
        # unpacking data packet ===============================================
        name, blanking, direction, observing, pad, ut, lst, deltaT, cur_ra, cur_dec, map_ra, map_dec, ra_off, dec_off, az, el, azvelcmd, elvelcmd, azvelact, elvelact, pa = unpacker.unpack(data)
        print('PA:',pa)
        # ==================================================================

if __name__ == '__main__':
    start_sock_tcomm()
