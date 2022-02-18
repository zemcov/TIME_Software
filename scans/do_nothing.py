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

        cmnd_list = ['TIME_START_TELEMETRY ' + str(kms_on_off)]
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
        queue2.put([0])
        t = time.time()
        while time.time()-t < int(sec):
            queue2.put([0])
            time.sleep(.5)

        # Closing Commands ============================
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


        return
