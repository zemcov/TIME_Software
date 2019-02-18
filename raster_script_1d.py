# raster 2D script

import socket, struct, subprocess, os, sys
import time
import numpy as np

class TIME_TELE :

    def start_sock(self):
        # I am accepting telescope sim data for the gui
        PORT = 1806
        HOST = '192.168.1.252'
        self.s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.s.connect((HOST,PORT))
        print('Socket Connected')
        unpacker = struct.Struct('s i i i i d d d d d d d d d d d d d d d d') # d = float , s = char string , i = integer
        ack = struct.Struct('s')
        message = tel_init(sec,map_size,map_angle,coord,epoch,object)
        return message
    # =================================================================================================================

    def tel_init(self,sec,map_size,map_angle,coord):
        cmnd_list = ['TIME_START_TELEMETRY on','TIME_START_TRACKING off','TIME_SCAN_TIME %s','TIME_MAP_SIZE %s','TIME_MAP_ANGLE %s',\
                        'TIME_MAP_COORD DEC','SEEK %s %s %s %s' %(sec,map_size,map_angle,coord[0],coord[1],epoch,object)]
        for i in range(len(cmnd_list)):
            self.s.send(cmnd_list[i].encode('utf-8'))
            reply = self.s.recv(ack.size)
            while True :
                if 'done' in reply : # wait for ack from tel
                    message = 'TELESCOPE INITIALIZED, STATUS: READY'
        return message

    def move_tel(self,queue,sec,map_size,map_angle,coord,epoch,object):
        n = 0

        while True:

            if ut.tel_exit.is_set(): # if shutdown command from software, send shutdown command to tel
                print("s Shutting Down")
                stop_msg = 'TIME_START_TRACKING off'
                self.s.send(stop_msg.encode('utf-8'))
                reply = self.s.recv(ack.size)
                if reply == 'confirmed':
                    final_msg = 'TIME_START_TELEMETRY off'
                    self.s.send(final_msg.encode('utf-8'))
                reply = self.s.recv(ack.size)
                if reply == 'confirmed':
                    break

            else :

                data = self.s.recv(unpacker.size)
                # unpacking data packet ===============================================
                name, blanking, direction, observing, pad, \
                ut, lst, deltaT, cur_ra, cur_dec, map_ra, map_dec, \
                ra_off, dec_off, az, el, azvelcmd, elvelcmd, azvelact, elvelact, \
                pa = unpacker.unpack(data)
                # ==================================================================
                # msg = 'proceed'
                # self.s.send(msg.encode())

                n += 1
                tel_data = np.array([int(blanking), int(direction), float(observing), float(pad), \
                ut, lst, deltaT, cur_ra, cur_dec, map_ra, map_dec, \
                ra_off, dec_off, az, el, azvelcmd, elvelcmd, azvelact, elvelact, \
                pa])
                np.save('/home/time/time-software-testing/TIME_Software/main/tempfiles/tele_packet%i.npy' %(n), tel_data)
                # send positional data to gui window
                queue.send([pa,int(blanking),int(direction),el,az,map_ra,map_dec,ut])

        print("Telescope Socket Closed")
        self.s.close()
        sys.exit()

    def pos_update(self,queue2,sec,map_size,map_angle,coord,epoch,object,map_len,num_scans):
        ''' starting position depends heavily on whether or not center position of telescope
            is center of time pixel array. Current code moves center of beam array to each end
            of the map length, so only half of array so stick out on each end.'''

        while not ut.tel_exit.is_set() :

                # --------------------------------------------------------------------------
                msg = 'SEEK %s %s %s %s' %(coord[0],coord[1],epoch,object)
                self.s.send(msg.encode('utf-8'))
                reply = self.s.recv(ack.size)
                if reply == 'proceed':
                    continue
                # -----------------------------------------------------------
                msg = 'TIME_START_TRACKING arm'
                self.s.send(msg.encode('utf-8'))
                reply = self.s.recv(ack.size)
                if reply == 'proceed' :
                    continue
                # --------------------------------------------------------------
                msg = 'TIME_START_TRACKING neg'
                self.s.send(msg.encode('utf-8'))
                reply = self.s.recv(ack.size)
                if reply == 'proceed' :
                    continue
                # --------------------------------------------------------------
                msg = 'TIME_START_TRACKING track'
                self.s.send(msg.encode('utf-8'))
                reply = self.s.recv(ack.size)
                if reply == 'proceed' :
                    continue
                # ---------------------------------------------------------------
                msg = 'TIME_START_OBSERVING on'
                self.s.send(msg.encode('utf-8'))
                reply = self.s.recv(ack.size)
                if reply == 'proceed' :
                    continue
                # -----------------------------------------------------------------
                while not ut.tel_exit.set(): # check if gui recieved the move flag from tel
                    done = queue2.recv()
                    if done == 'increment' :
                        i += 1
                        if i == num_scans : # wait to stop scanning until number of scans is done
                            ut.tel_exit.set()
                    else :
                        pass
