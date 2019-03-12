# raster 2D script, currently set up to do constant DEC scans

import socket, struct, subprocess, os, sys
import time
import numpy as np
import astropy.units as u
from astropy.time import Time as thetime
from astropy.coordinates import SkyCoord
import multiprocessing as mp
import tel_tracker
import termcolor as colored
import utils as ut

class TIME_TELE :

    def start_sock(self,queue,scan_time,sec,map_size,map_angle,coord1,coord2,epoch,object,map_len,num_scans):
        # I am accepting telescope sim data for the gui
        self.i = 0
        PORT = 1806
        self.s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.s.bind(('',6666))
        self.s.connect(('192.168.1.252',PORT))
        print('Socket Connected')
        commands = '{} {} {} {}'
        # print(colored(commands.format(coord1,coord2,epoch,object),'yellow'))
    # =================================================================================================================
        cmnd_list = ['TIME_START_TELEMETRY on','TIME_START_TRACKING off','TIME_SCAN_TIME ' + str(sec),'TIME_MAP_SIZE ' + str(map_size),\
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


        # num_loop = int(float(map_len) // (0.43/60.0) + (float(map_len) % (0.43/60.0) > 0)) # degrees
        num_loop = int(10)
        c1 = str(coord1).split(':')
        c2 = str(coord2).split(':')
        old_coord = SkyCoord(c1[0]+'h'+c1[1]+'m'+c1[2]+'s', c2[0]+'d'+c2[1]+'m'+c2[2]+'s')
        print(old_coord)

        while self.i < num_loop :
            print(self.i,num_loop)
            if self.i > 0 :
                cmnd_list = ['TIME_SCAN_TIME ' + str(sec),'TIME_MAP_SIZE ' + str(map_size),\
                                'TIME_MAP_ANGLE ' + str(map_angle),'TIME_MAP_COORD RA']
                i = 0
                while i <= (len(cmnd_list) - 1):
                    self.s.send(cmnd_list[i])
                    reply = self.s.recv(1024).decode("ascii")
                    print(reply)
                    if 'OK' in reply :
                        i += 1
                    else :
                        print('ERROR reply')

                # convert all coordinates to same format, then add values to ra and dec
                # c = SkyCoord(ra = (self.i*0.43/60.0) * u.degree, dec = (self.i*0.43/60.0) * u.degree)
                c = SkyCoord(ra = (self.i*0.001)* u.degree, dec = (self.i*0.001) * u.degree)
                # new_ra = (c.ra + old_coord.ra).to_string()
                new_dec = (c.dec + old_coord.dec).to_string()
                print('New Dec',new_dec,'C',c)
                # new_coord_ra = '{}{}{}{}{}'
                # new_coord_ra = new_coord_ra.format(new_ra[0][0:2],':',new_ra[0][3:5],':',new_ra[0][6:8])
                new_coord_dec = '{}{}{}{}{}'
                new_coord_dec = new_coord_dec.format(new_dec[:new_dec.find('d')],':',new_dec[new_dec.find('d')+1:new_dec.find('m')],':',new_dec[new_dec.find('m')+1:new_dec.find('s')])
                print('New Coord Dec',new_coord_dec, new_dec[:new_dec.find('d')],new_dec[new_dec.find('d')+1:new_dec.find('m')],new_dec[new_dec.find('m')+1:new_dec.find('s')])
                # feed new values to telescope
                commands = '{} {} {} {}'
                msg = 'TIME_SEEK ' + commands.format(coord1,new_coord_dec,epoch,object)
                self.s.send(msg)
                reply = self.s.recv(1024).decode("ascii")
                print(reply)

            self.pos_update()
            time.sleep(int(scan_time))
            self.i += 1
            # -------------------------------------------
            msg = 'TIME_START_TRACKING off'
            self.s.send(msg)
            reply = self.s.recv(1024).decode("ascii")
            print(reply)

        # -------------------------------------------\
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

        return
