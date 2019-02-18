
import socket, struct, subprocess, os, sys
import time
import numpy as np
import multiprocessing as mp
tel_exit = mp.Event()

class TIME_TELE :

    def start_sock_tcomm(self): # this is what we use to talk to telescope
        PORT = 1806
        HOST = '192.168.1.252'
        self.s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.s.connect((HOST,PORT))
        print('TCOMM Socket Connected')
        ack = struct.Struct('s')
        message = tel_init(sec,map_size,map_angle,coord,epoch,object)
        return message

    def start_sock_tracker(self): # this is just receiving firehose of packets
        PORT2 = 1825
        HOST = '192.168.1.252'
        self.s2 = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.s2.connect((HOST,PORT))
        print('Tracker Socket Connected')
        unpacker = struct.Struct('s i i i i d d d d d d d d d d d d d d d d') # d = float , s = char string , i = integer

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

    def tel_init(self,sec,map_size,map_angle,coord):
        i = 0
        cmnd_list = ['TIME_START_TELEMETRY on','TIME_START_TRACKING off','TIME_SCAN_TIME %s','TIME_MAP_SIZE %s','TIME_MAP_ANGLE %s',\
                        'TIME_MAP_COORD RA','SEEK %s %s %s %s' %(sec,map_size,map_angle,coord[0],coord[1],epoch,object)]
        while i <= len(cmnd_list) :
            self.s.send(cmnd_list[i].encode('utf-8'))
            reply = self.s.recv(ack.size)
            if 'done' in reply : # wait for ack from tel
                if i == 0 :
                    self.start_sock_tracker()
                i += 1

        message = 'TELESCOPE INITIALIZED, STATUS: READY'
        return message


if __name__ == '__main__':
    Time_Tele().start_sock()
    time.sleep(10.0)
    tel_exit.set()
