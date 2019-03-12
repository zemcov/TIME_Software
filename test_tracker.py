import socket, struct, subprocess, os, sys
import time
import numpy as np
import multiprocessing as mp

def start_sock():
    PORT = 1806
    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    s.bind(('',6666))
    s.connect(('192.168.1.252',PORT))
    print('Socket Connected')
    s.send('TIME_START_TELEMETRY on')
    reply = s.recv(1024).decode("ascii")
    print(reply)
    s.close()
    start_tracker()

def start_tracker():
    PORT = 4444
    l = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    l.bind(('',PORT))
    print('Server Listening')
    l.listen(5)
    client, info = l.accept()
    print('Socket Connected')
    unpacker = struct.Struct('i i i i d d d d d d d d d d d d d d d d') # d = float , s = char string , i = integer
    n = 0

    while True :

        try :
            data = client.recv(unpacker.size)
            if len(data) !=0 :
                # unpacking data packet ===============================================
                blanking, direction, observing, pad, utc, lst, deltaT, cur_ra, cur_dec,\
                map_ra, map_dec, ra_off, dec_off, az, el, azvelcmd, elvelcmd, azvelact,\
                elvelact, pa = unpacker.unpack(data)
                # ==================================================================
                if n % 5 == 0:
                    min = utc % 1 * 60
                    sec = min % 1 * 60
                    print('utc: %s : %s : %0.10f' %(int(utc),int(min),sec))

                n += 1

        except KeyboardInterrupt :
            break

    l.close()
    sys.exit()

if __name__ == '__main__' :
    start_sock()
