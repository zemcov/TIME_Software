# raster 1D script

import socket, struct, subprocess, os, sys
import time
import numpy as np
import multiprocessing as mp
import tel_tracker
import utils as ut
from termcolor import colored
from pos_counter import scan_params

class TIME_TELE :

    def start_sock(self,queue2,queue,scan_time,sec,map_size,map_angle,coord1,coord2,epoch,object,num_loop,step,coord_space,step_unit,map_size_unit,map_angle_unit):
        # I am accepting telescope sim data for the gui
        PORT = 1806
        self.s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.s.bind(('',6666))
        self.s.connect(('192.168.1.252',PORT))
        print('Socket Connected')
        commands = '{} {} {} {}'
        print(colored(commands.format(coord1,coord2,epoch,object),'yellow'))

        num_loop = scan_params(map_size,scan_time,coord1,coord2,step)
        p2 = mp.Process(target = self.loop_track , args=(num_loop,))
        p2.start()
    # =================================================================================================================
        # cmnd_list = ['TIME_START_TELEMETRY on','TIME_START_TRACKING off','TIME_SCAN_TIME ' + str(sec),'TIME_MAP_SIZE ' + str(map_size),\
        #                 'TIME_MAP_ANGLE ' + str(map_angle),'TIME_MAP_COORD RA','TIME_SEEK ' + commands.format(coord1,coord2,epoch,object)]
        cmnd_list = ['TIME_START_TELEMETRY on','TIME_START_TRACKING off','TIME_SCAN_TIME ' + str(sec),'TIME_MAP_SIZE_EXTRA 1.1','TIME_MAP_SIZE ' + str(map_size),\
                        'TIME_MAP_ANGLE ' + str(map_angle),'TIME_MAP_COORD RA','TIME_SEEK ' + commands.format(coord1,coord2,epoch,object)]
        i = 0
        while i <= (len(cmnd_list) - 1):
            self.s.send(cmnd_list[i])
            reply = self.s.recv(1024).decode("ascii")
            print(reply)
            if i == 0 :
                if 'OK' in reply:
                    p = mp.Process(target=tel_tracker.start_tracker, args=(queue,))
                    p.start()
                    i += 1
                else :
                    print('ERROR reply')
            else :
                if 'OK' in reply :
                    i += 1
                else :
                    print('ERROR reply')

        self.pos_update()

        # time.sleep(int(scan_time) + (int(sec) * 6)) # sec * 6 gives dome time to catch up before taking real scans
        time.sleep(int(scan_time))

        msg = 'TIME_START_TRACKING off'
        self.s.send(msg)
        reply = self.s.recv(1024).decode("ascii")
        print(reply)
        if 'OK' in reply :
            ut.tel_exit.set()

        self.s.send('TIME_START_TELEMETRY OFF')
        print('Telemetry Off')
        reply = self.s.recv(1024).decode("ascii")
        print(reply)

        print("Telescope Socket Closed")
        self.s.close()
        sys.exit()

    def pos_update(self):

        # ---------------------------------------------------------------
        msg = 'TIME_START_TRACKING arm'
        self.s.send(msg)
        reply = self.s.recv(1024).decode("ascii")
        if 'OK' in reply  :
            print(reply)
        # --------------------------------------------------------------
        msg = 'TIME_START_TRACKING neg'
        self.s.send(msg)
        reply = self.s.recv(1024).decode("ascii")
        if 'OK' in reply  :
            print(reply)
        # --------------------------------------------------------------
        msg = 'TIME_START_TRACKING track'
        self.s.send(msg)
        reply = self.s.recv(1024).decode("ascii")
        if 'OK' in reply  :
            print(reply)
        # ---------------------------------------------------------------
        msg = 'TIME_START_OBSERVING on'
        self.s.send(msg)
        reply = self.s.recv(1024).decode("ascii")
        if 'OK' in reply  :
            print(reply)
        # # -----------------------------------------------------------------

        return
