
import socket, struct, subprocess, os, sys
import time
import numpy as np
import multiprocessing as mp

class TIME_TELE :

    def start_sock_tcomm(self): # this is what we use to talk to telescope
        PORT = 1806
        HOST = '192.168.1.252'
        self.s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.s.connect((HOST,PORT))
        print('TCOMM Socket Connected')
        ack = struct.Struct('s')
        # ======================================================================
        cmnd_list = 'TIME_START_TELEMETRY on'
        self.s.send(cmnd_list.encode('utf-8'))
        reply = self.s.recv(ack.size)
        if 'done' in reply : # wait for ack from tel
            print('TELESCOPE INITIALIZED, STATUS: READY')
            self.start_sock_tracker()
        # ======================================================================

    def start_sock_tracker(self): # this is just receiving firehose of data packets
        PORT2 = 1825
        HOST2 = '192.168.1.252'
        self.s2 = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.s2.connect((HOST2,PORT2))
        print('Tracker Socket Connected')
        unpacker = struct.Struct('s i i i i d d d d d d d d d d d d d d d d') # d = float , s = char string , i = integer

        # ===========================================================================================
        while True:

            if tel_exit.is_set(): # if shutdown command from software, send shutdown command to tel
                print("Client Shutting Down")
                final_msg = 'TIME_START_TELEMETRY off'
                self.s.send(final_msg.encode('utf-8'))
                reply = self.s.recv(ack.size)
                if 'done' in reply:
                    break

            else :
                data = self.s2.recv(unpacker.size)
                # unpacking data packet ===============================================
                name, blanking, direction, observing, pad, \
                ut, lst, deltaT, cur_ra, cur_dec, map_ra, map_dec, \
                ra_off, dec_off, az, el, azvelcmd, elvelcmd, azvelact, elvelact, \
                pa = unpacker.unpack(data)
                # ==================================================================

        print("Telescope Socket Closed")
        self.s.close()
        self.s2.close()
        sys.exit()

if __name__ == '__main__':
    tel_exit = mp.Event()
    TIME_TELE().start_sock_tcomm()
    time.sleep(10.0)
    tel_exit.set()
