# raster 2D script, currently set up to do constant DEC scans

import socket, struct, subprocess, os, sys
import time
import numpy as np
import astropy.units as u
from astropy.time import Time as thetime
from astropy.coordinates import SkyCoord, AltAz
import multiprocessing as mp
from coms import tel_tracker
# import termcolor as colored
import config.utils as ut
from main.pos_counter import scan_params
import main.angle_converter as ac
from termcolor import colored
from multiprocessing import Manager

class TIME_TELE :

    def start_sock(self,queue2,queue,sec,map_size,map_len,map_angle,coord1,coord1_unit,coord2,coord2_unit,epoch,\
                    object,step,coord_space,step_unit,map_size_unit,map_len_unit,map_angle_unit,numloop,kms_on_off):
        # I am accepting telescope sim data for the gui
        self.i = Manager().list()
        self.i.append(0)
        PORT = 1806
        self.s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.s.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        self.s.bind(('',6666))
        self.s.connect(('192.168.1.252',PORT))
        print('Socket Connected')
        commands = '{} {} {} {}'
        print(colored(commands.format(coord1,coord2,epoch,object),'yellow'))

        _, calc_coord1, calc_coord2 = scan_params(1,coord_space,map_size,map_size_unit,map_len,map_len_unit,coord1,coord1_unit,coord2,coord2_unit,step,step_unit)
        num_loop = numloop
        p2 = mp.Process(target = self.loop_track , args=(num_loop,queue2))
        p2.start()
    # =================================================================================================================
        ''' Make sure map_size and map_angle are being fed as degrees to tracker '''
        # ===============================================
        if str(map_size_unit) != 'deg' :
            if str(map_size_unit) == 'arcsec' :
                map_size = float(map_size) // 3600
            else :
                map_size = float(map_size) // 60

        if str(map_angle_unit) != 'deg' :
            if str(map_angle_unit) == 'arcsec' :
                map_angle = float(map_angle) // 3600
            else :
                map_angle = float(map_angle) // 60
        # ===============================================

        cmnd_list = ['TIME_START_TELEMETRY ' + str(kms_on_off),'TIME_SEND_CMD CMD','TIME_TELESCOPE_WAIT_TIME 2',\
                        'TIME_START_TRACKING off','TIME_SCAN_TIME ' + str(sec),'TIME_MAP_SIZE ' + str(map_size),\
                                'TIME_MAP_ANGLE ' + str(map_angle),'TIME_MAP_COORD ' + str(coord_space)]
        #
        i = 0
        while i <= (len(cmnd_list) - 1):
            self.s.send(cmnd_list[i].encode())
            reply = self.s.recv(1024).decode("ascii")
            print(cmnd_list[i],reply)
            if i == 0 :
                if 'OK' in reply:
                    p = mp.Process(target=tel_tracker.start_tracker, args=(queue,))
                    p.start()
                    i += 1
                else :
                    print(cmnd_list[i] + ' sent ERROR reply')
                    sys.exit()
            else :
                if 'OK' in reply :
                    i += 1
                else :
                    print(cmnd_list[i] + ' sent ERROR reply')
                    sys.exit()

        ################################################################################################
        while self.i[-1] < int(num_loop) :

            if self.i[-1] == 0 :
                commands = '{} {} {} {}'
                msg = 'TIME_SEEK ' + commands.format(calc_coord1,calc_coord2,epoch,object)
                self.s.send(msg.encode())
                reply = self.s.recv(1024).decode("ascii")
                print(msg,reply)

                self.pos_update()
                time.sleep((int(sec)+int(sec)*0.05)*2)
                self.s.send('TIME_TURNAROUND_NOTIFY'.encode())
                reply = self.s.recv(1024).decode("ascii")
                if 'OK' in reply:
                    pass
                else :
                    print('TIME_TURNAROUND_NOTIFY sent Error Reply')
                    sys.exit()


            else :
                # feed new values to telescope
                commands = '{} {} {} {}'
                msg = 'TIME_SEEK ' + commands.format(calc_coord1,calc_coord2,epoch,object)
                self.s.send(msg.encode())
                reply = self.s.recv(1024).decode("ascii")
                print(msg,reply)

                time.sleep((int(sec)*0.9)*2)
                self.s.send('TIME_TURNAROUND_NOTIFY'.encode())
                reply = self.s.recv(1024).decode("ascii")
                if 'OK' in reply:
                    pass
                else :
                    print("TIME_TURNAROUND_NOTIFY sent Error Reply")
                    sys.exit()

            self.i[-1] += 1

        # Closing Commands ============================
        msg = 'TIME_START_OBSERVING off'
        self.s.send(msg.encode())
        reply = self.s.recv(1024).decode("ascii")
        print(msg,reply)
        # -------------------------------------------
        msg = 'TIME_START_TRACKING OFF'
        self.s.send(msg.encode())
        reply = self.s.recv(1024).decode("ascii")
        print(msg,reply)
        # ---------------------------------------------
        msg = 'TIME_START_TELEMETRY 0'
        self.s.send(msg.encode())
        print('Telemetry Off')
        reply = self.s.recv(1024).decode("ascii")
        print(msg,reply)
        if 'OK' in reply :
            ut.tel_exit.set()
        # # ------------------------------------------
        print("Telescope Socket Closed")
        self.s.close()
        sys.exit()
        # ================================================

    def pos_update(self):

        # -----------------------------------------------------------
        msg = 'TIME_START_TRACKING arm'
        self.s.send(msg.encode())
        reply = self.s.recv(1024).decode("ascii")
        print(msg,reply)
        # --------------------------------------------------------------
        msg = 'TIME_START_TRACKING neg'
        self.s.send(msg.encode())
        reply = self.s.recv(1024).decode("ascii")
        print(msg,reply)

        time.sleep(2.0)

        # --------------------------------------------------------------
        msg = 'TIME_START_TRACKING track'
        self.s.send(msg.encode())
        reply = self.s.recv(1024).decode("ascii")
        print(msg,reply)
        # ---------------------------------------------------------------
        msg = 'TIME_START_OBSERVING on'
        self.s.send(msg.encode())
        reply = self.s.recv(1024).decode("ascii")
        print(msg,reply)
        # -----------------------------------------------------------------

    def loop_track(self,num_loop,queue2):
        while not ut.tel_exit.is_set():
            tot = int((float(self.i[-1]) / float(num_loop)) * 100.0)
            sys.stdout.flush()
            queue2.put([tot])
            time.sleep(0.05)

        return
