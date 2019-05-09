# raster 2D script, currently set up to do constant DEC scans

import socket, struct, subprocess, os, sys
import time
import numpy as np
import astropy.units as u
from astropy.time import Time as thetime
from astropy.coordinates import SkyCoord, AltAz
import multiprocessing as mp
import tel_tracker
import termcolor as colored
import utils as ut
from pos_counter import scan_params
import angle_converter as ac

class TIME_TELE :

    def start_sock(self,queue2,queue,scan_time,sec,map_size,map_len,map_angle,coord1,coord1_unit,coord2,coord2_unit,epoch,object,num_loop,step,coord_space,step_unit,map_size_unit,map_len_unit,map_angle_unit):
        # I am accepting telescope sim data for the gui
        self.i = 0
        PORT = 1806
        self.s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.s.bind(('',6666))
        self.s.connect(('192.168.1.252',PORT))
        print('Socket Connected')

        num_loop, calc_coord1, calc_coord2 = scan_params(map_len,map_len_unit,map_size_unit,scan_time,coord1,coord1_unit,coord2,coord2_unit,step,step_unit)
        p2 = mp.Process(target = self.loop_track , args=(num_loop,))
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
            if str(map_size_unit) == 'arcsec' :
                map_size = float(map_size) // 3600
            else :
                map_size = float(map_size) // 60
        # ===============================================

        cmnd_list = ['TIME_START_TELEMETRY on','TIME_START_TRACKING off','TIME_SCAN_TIME ' + str(sec),'TIME_MAP_SIZE ' + str(map_size),\
                        'TIME_MAP_ANGLE ' + str(map_angle),'TIME_MAP_COORD ' + str(coord_space)]

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

        c1 = str(calc_coord1.to_string()).split(':')
        c2 = str(calc_coord2.to_string()).split(':')
        if str(coord1_unit) == 'RA' and str(coord2_unit) == 'DEC' :
            old_coord = SkyCoord(c1[0]+'h'+c1[1]+'m'+c1[2]+'s', c2[0]+'d'+c2[1]+'m'+c2[2]+'s')
        else :
            old_coord = AltAz(c1[0]+'d'+c1[1]+'m'+c1[2]+'s', c2[0]+'d'+c2[1]+'m'+c2[2]+'s')

        while self.i < int(num_loop) :

            if self.i == 0 :
                commands = '{} {} {} {}'
                msg = 'TIME_SEEK ' + commands.format(calc_coord1,calc_coord2,epoch,object)
                self.s.send(msg)
                reply = self.s.recv(1024).decode("ascii")
                print(reply)

                self.pos_update()
                time.sleep(int(scan_time) + (int(sec) * 6)) # because the dome needed 6-8 wraps for the first scan to warm up

            else :
                new_coord = '{}{}{}{}{}'
                # convert all coordinates to same format, then add values to ra and dec
                if str(coord_space) == 'RA' or str(coord_space) == 'DEC' :
                    c = SkyCoord(ra = (self.i*float(step))* u.degree, dec = (self.i*float(step)) * u.degree)

                    if str(coord_space) == 'RA' :
                        new_ra = (c.ra + old_coord.ra).to_string()
                        new_coord = new_coord.format(new_ra[:new_ra.find('h')],':',new_ra[new_ra.find('h')+1:new_ra.find('m')],':',new_ra[new_ra.find('m')+1:new_ra.find('s')])
                    else :
                        new_dec = (c.dec + old_coord.dec).to_string()
                        new_coord = new_coord.format(new_dec[:new_dec.find('d')],':',new_dec[new_dec.find('d')+1:new_dec.find('m')],':',new_dec[new_dec.find('m')+1:new_dec.find('s')])

                else :
                    c = AltAz(az = (self.i*float(step))*u.degree, alt = (self.i*float(steps))*u.degree)
                    if str(coord_space) == 'AZ' :
                        new_az = (c.az + old_coord.az).to_string()
                        new_coord = new_coord.format(new_az[:new_az.find('d')],':',new_az[new_az.find('d')+1:new_az.find('m')],':',new_az[new_az.find('m')+1:new_az.find('s')])
                    else :
                        new_alt = (c.alt + old_coord.alt).to_string()
                        new_coord = new_coord.format(new_alt[:new_alt.find('d')],':',new_alt[new_alt.find('d')+1:new_alt.find('m')],':',new_alt[new_alt.find('m')+1:new_alt.find('s')])

                # feed new values to telescope
                commands = '{} {} {} {}'
                msg = 'TIME_SEEK ' + commands.format(coord1,new_coord,epoch,object)
                self.s.send(msg)
                reply = self.s.recv(1024).decode("ascii")
                print(reply)

                self.pos_update()
                time.sleep(int(scan_time))

            self.i += 1
            # -------------------------------------------
            msg = 'TIME_START_TRACKING neg'
            self.s.send(msg)
            reply = self.s.recv(1024).decode("ascii")
            print(reply)

        # Closing Commands ============================
        # -------------------------------------------
        msg = 'TIME_START_TRACKING OFF'
        self.s.send(msg)
        reply = self.s.recv(1024).decode("ascii")
        print(reply)
        # ---------------------------------------------
        msg = 'TIME_START_TELEMETRY OFF'
        self.s.send(msg)
        print('Telemetry Off')
        reply = self.s.recv(1024).decode("ascii")
        print(reply)
        if 'OK' in reply :
            ut.tel_exit.set()
        # ------------------------------------------
        print("Telescope Socket Closed")
        self.s.close()
        sys.exit()
        # ================================================

    def pos_update(self):

        # -----------------------------------------------------------
        msg = 'TIME_START_TRACKING arm'
        self.s.send(msg)
        reply = self.s.recv(1024).decode("ascii")
        print(reply)
        # --------------------------------------------------------------
        msg = 'TIME_START_TRACKING neg'
        self.s.send(msg)
        reply = self.s.recv(1024).decode("ascii")
        print(reply)
        # --------------------------------------------------------------
        msg = 'TIME_START_TRACKING track'
        self.s.send(msg)
        reply = self.s.recv(1024).decode("ascii")
        print(reply)
        # ---------------------------------------------------------------
        msg = 'TIME_START_OBSERVING on'
        self.s.send(msg)
        reply = self.s.recv(1024).decode("ascii")
        print(reply)
        # -----------------------------------------------------------------

    def loop_track(self,num_loop):
        while not ut.tel_exit.is_set():
            tot = int((self.i / num_loop) * 100)
            queue2.send([tot])
            time.sleep(0.05)

        return
