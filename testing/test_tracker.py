import socket, struct, subprocess, os, sys
import time
import numpy as np
import multiprocessing as mp

def start_tracker():
    PORT = 4444
    l = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    l.bind(('',PORT))
    print('Server Listening')
    l.listen(5)

    PORT = 1806
    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    s.bind(('',6666))
    s.connect(('192.168.1.252',PORT))
    print('Socket 1 Connected')
    s.send('TIME_START_TELEMETRY 2') # 0 = off , 1 = on , 2 = both kms & tel
    reply = s.recv(1024).decode("ascii")
    print(reply)

    # PORT = 8500
    # k = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    # k.bind(('',PORT))
    # print('KMS Server Listening')
    # k.listen(5)

    client, info = l.accept()
    print('Socket 2 Connected')
    unpacker = struct.Struct('i i i i d d d d d d d d d d d d d d d d q q') # d = float , s = char string , i = integer
    n = 0

    # kms_client, kms_info = k.accept()
    # print('KMS Socket Connected')
    # unpacker_kms = struct.Struct('d i d d') # pa, direction, utc, enc_pos

    # save_data = []
    while True :

        try :

            data = client.recv(unpacker.size)
            # kms_data = kms_client.recv(unpacker_kms.size)

            if len(data) !=0 :

                try :
                    # unpacking data packet ===============================================
                    blanking, direction, observing, pad, utc, lst, deltaT, cur_ra, cur_dec,\
                    map_ra, map_dec, ra_off, dec_off, az, el, azvelcmd, elvelcmd, azvelact,\
                    elvelact, pa, unix_val, unix_delta = unpacker.unpack(data)
                    # ==================================================================
                    print('pa: %s , UTC: %s , delta: %s' %(pa,unix_val,unix_delta))

                    # kms_pa, kms_dir, kms_utc, kms_pos = unpacker_kms.unpack(kms_data)
                    # save_data.append([kms_pa, kms_dir, kms_utc, kms_pos])

                except struct.error :
                    print('wrong size! :',len(data))

        except KeyboardInterrupt :
            print('Interrupted')
            # np.save('kms_longevity_test_083121.npy',save_data)
            s.send('TIME_START_TELEMETRY 0')
            reply = s.recv(1024).decode("ascii")
            print(reply)
            s.close()
            l.close()
            try :
                sys.exit(0)
            except SystemExit:
                os._exit(0)

if __name__ == '__main__' :
    start_tracker()
