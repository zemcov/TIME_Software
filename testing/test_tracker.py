import socket, struct, subprocess, os, sys
import time
import numpy as np
import multiprocessing as mp

def start_tracker():
    PORT = 4444
    l = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    l.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    l.bind(('',PORT))
    print('Server Listening on port %s' % PORT)
    l.listen(5)

    PORT = 1806
    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    s.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    s.bind(('',6666))
    # s.connect(('192.168.1.252',PORT)) # this is tracker's IP
    s.connect(('',PORT)) # this is to connect locally

    print('Socket 1 Connected on port %s' % PORT)
    s.send('TIME_START_TELEMETRY 2'.encode())
    reply = s.recv(1024).decode("ascii")
    print(reply)


    client, info = l.accept()
    reply = client.recv(1024).decode('ascii')
    print('Socket 2 Connected')
    print(reply)
    unpacker = struct.Struct('i i i i d d d d d d d d d d d d d d d d Q Q') # d = float , s = char string , i = integer
    n = 0

    while True :

        try :
            data = client.recv(unpacker.size)
            if len(data) !=0 :
                # unpacking data packet ===============================================
                blanking, direction, observing, pad, utc, lst, deltaT, cur_ra, cur_dec,\
                map_ra, map_dec, ra_off, dec_off, az, el, azvelcmd, elvelcmd, azvelact,\
                elvelact, pa, unix_val, unix_delta = unpacker.unpack(data)
                # ==================================================================
                print('val: %s , delta: %s' %(unix_val,unix_delta))

                # if n == 20 :
                #     break

                n += 1

        except KeyboardInterrupt :
            s.send('TIME_START_TELEMETRY 0'.encode())
            s.shutdown()
            l.shutdown()
            l.close()
            s.close()
            break

    sys.exit()

if __name__ == '__main__' :
    start_tracker()
