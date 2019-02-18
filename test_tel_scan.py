
import socket, struct, subprocess, os, sys
# from socket import htonl
import time
import numpy as np
import multiprocessing as mp

class TIME_TELE :

    def __init__(self):
        self.tel_exit = mp.Event()

    def start_sock_tcomm(self): # this is what we use to talk to telescope
        PORT = 8888
        # I am accepting telescope sim data for the gui
        self.s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.s.bind(('',PORT))
        print('Server Listening')
        print('Tots Socket Connected')
        self.s.listen(5)
        self.client, info = self.s.accept()
        # data1 = self.client.recv(1024).decode("ascii")
        # print(data1)
        data = self.client.recv(1024).decode("ascii")
        print(data)
        time.sleep(2.0)
        self.start_sock_tracker(self.client)
        # ======================================================================

    def start_sock_tracker(self,client): # this is just receiving firehose of data packets
        PORT2 = 1806
        HOST2 = '192.168.1.252'
        ack = struct.Struct('s')
        self.s2 = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.s2.connect((HOST2,PORT2))
        print('Tracker Socket Connected')

        cmnd_list = 'time_start_telemetry on '
        # packer = struct.Struct('i')
        # packed_data = packer.pack(24)
        # data = socket.htonl(24)
        # packer = struct.pack('I',data)
        # self.s2.send(packer)
        # ----------------------------------------
        self.s2.send(cmnd_list)
        # ----------------------------------------
        reply = self.s2.recv(1024).decode("ascii")
        print('tracker reply',reply)
        # if 'ok' in reply : # wait for ack from tel
        #     print('TELESCOPE INITIALIZED, STATUS: READY')

        # ===========================================================================================
        while True:

            # if self.tel_exit.is_set(): # if shutdown command from software, send shutdown command to tel
            #     print("Client Shutting Down")
            #     final_msg = 'TIME_START_TELEMETRY off'
            #     self.s2.send(final_msg.encode('utf-8'))
            #     reply = self.s2.recv(ack.size)
            #     if 'ok' in reply:
            #         break
            #
            # else :
            unpacker = struct.Struct('s i i i i d d d d d d d d d d d d d d d d') # d = float , s = char string , i = integer
            data = client.recv(unpacker.size)
            print('Data Received')
            # unpacking data packet ===============================================
            name, blanking, direction, observing, pad, ut, lst, deltaT, cur_ra, cur_dec, map_ra, map_dec, ra_off, dec_off, az, el, azvelcmd, elvelcmd, azvelact, elvelact, pa = unpacker.unpack(data)
            print('PA:',pa)
            # ==================================================================
        # else :
        #     print('Bad Reply')

        # print("Telescope Socket Closed")
        # self.s.close()
        # self.s2.close()
        # sys.exit()

if __name__ == '__main__':
    TIME_TELE().start_sock_tcomm()
    # time.sleep(10.0)
    # tel_exit.set()
