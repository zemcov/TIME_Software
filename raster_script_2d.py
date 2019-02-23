# raster 2D script, currently set up to do constant DEC scans

import socket, struct, subprocess, os, sys
import time
import numpy as np
import astropy.units as u
from astropy.time import Time as thetime
from astropy.coordinates import SkyCoord

class TIME_TELE :

    def start_sock(self,queue,queue2,sec,map_size,map_angle,coord1,coord2,epoch,object,map_len,num_scans):
        # I am accepting telescope sim data for the gui
        PORT = 1806
        self.s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.s.bind(('',6666))
        self.s.connect(('192.168.1.252',PORT))
        print('Socket Connected')
    # =================================================================================================================
        cmnd_list = ['TIME_START_TELEMETRY on','TIME_START_TRACKING off','TIME_SCAN_TIME ' + str(sec),'TIME_MAP_SIZE ' + str(map_size),\
                        'TIME_MAP_ANGLE ' + str(map_angle),'TIME_MAP_COORD RA','TIME_SEEK ' + str(coord1) + ' ' + str(coord2)\
                        + ' ' + str(epoch) + ' ' + str(object)]
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

        self.pos_update(queue2,sec,map_size,map_angle,coord1,coord2,epoch,object,map_len,num_scans)

        self.s.send('TIME_START_TELEMETRY OFF')
        print('Telemetry Off')
        reply = self.s.recv(1024).decode("ascii")
        print(reply)
        print("Telescope Socket Closed")
        self.s.close()
        sys.exit()

    def pos_update(self,queue2,sec,map_size,map_angle,coord1,coord2,epoch,object,map_len,num_scans):
        ''' starting position depends heavily on whether or not center position of telescope
            is center of time pixel array. Current code moves center of beam array to each end
            of the map length, so only half of array so stick out on each end.'''

        num_loop = int(float(map_len) // (0.43/60.0) + (float(map_len) % (0.43/60.0) > 0)) # degrees
        c1 = str(coord1).split(':')
        c2 = str(coord2).split(':')
        old_coord = SkyCoord(c1[0]+'h'+c1[1]+'m'+c1[2]+'s', c2[0]+'d'+c2[1]+'m'+c2[2]+'s')

        i = 0
        if i <= num_loop:
            # --------------------------------------------------------------------------
            if i > 0 :
                # convert all coordinates to same format, then add values to ra and dec
                c = SkyCoord(ra = (i*0.43/60.0) * u.degree, dec = (i*0.43/60.0) * u.degree)
                new_ra1 = c.ra.hms.h + old_coord.ra.hms.h
                new_ra2 = c.ra.hms.m + old_coord.ra.hms.m
                new_ra3 = c.ra.hms.s + old_coord.ra.hms.s
                # new_dec1 = c.dec.hms.d + old_coord.dec.hms.d
                # new_dec2 = c.dec.hms.m + old_coord.dec.hms.m
                # new_dec3 = c.dec.hms.s + old_coord.dec.hms.s
                new_coord_ra = str(new_ra1+':'+new_ra2+':'+new_ra3)
                # new_coord_dec = str(new_dec1+':'+new_dec2+':'+new_dec3)

                # feed new values to telescope
                msg = 'TIME_SEEK ' + new_coord_ra + ' ' + str(coord2) + ' ' + str(epoch) + ' ' + str(object)
                self.s.send(msg)
                reply = self.s.recv(1024).decode("ascii")
                if 'OK' in reply  :
                    continue
            # -----------------------------------------------------------
            msg = 'TIME_START_TRACKING arm'
            self.s.send(msg)
            reply = self.s.recv(1024).decode("ascii")
            if 'OK' in reply  :
                continue
            # --------------------------------------------------------------
            msg = 'TIME_START_TRACKING neg'
            self.s.send(msg)
            reply = self.s.recv(1024).decode("ascii")
            if 'OK' in reply :
                continue
            # --------------------------------------------------------------
            msg = 'TIME_START_TRACKING track'
            self.s.send(msg)
            reply = self.s.recv(1024).decode("ascii")
            if 'OK' in reply  :
                continue
            # ---------------------------------------------------------------
            msg = 'TIME_START_OBSERVING on'
            self.s.send(msg)
            reply = self.s.recv(1024).decode("ascii")
            if 'OK' in reply  :
                continue
            # -----------------------------------------------------------------
            while not ut.tel_exit.set(): # check if gui recieved the move flag from tel
                done = queue2.recv()
                if done == 'increment' :
                    i += 1
                    # ---------------------------------------------------------------
                    msg = 'TIME_START_TRACKING off'
                    self.s.send(msg)
                    reply = self.s.recv(1024).decode("ascii")
                    if 'OK' in reply  :
                        break
                else :
                    pass

        else :
            return
