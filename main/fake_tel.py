import socket, struct, subprocess, os, sys
import time as othertime
import numpy as np
import matplotlib.pyplot as plt
import astropy.units as u
from astropy.time import Time as thetime
from astropy.coordinates import SkyCoord, EarthLocation, AltAz, Angle, Latitude, Longitude, ICRS, Galactic, FK4, FK5
from astroplan import Observer
import utils as ut
from datetime import datetime
from pos_counter import scan_params
from termcolor import colored
from astroplan import download_IERS_A
sys.path.append('/home/time_user/TIME_Software/Scans/')
import test_tracker
import time
import multiprocessing as mp

# download_IERS_A()

class TIME_TELE :

    def tel_move(self,coord_space,x,y,n):
        #initialize  and update position coordinates
        location = EarthLocation.from_geodetic(lon =-111.5947*u.deg, lat =31.95844*u.deg, height=2097.024*u.m)
        kittpeak = Observer(location=location, name='kitt peak')
        self.thedate = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        time = thetime(self.thedate)
        times = time + (n*u.second)
        lst = kittpeak.local_sidereal_time(times)

        if coord_space == 'RA' or coord_space == 'DEC' :
            coord = SkyCoord(ra = x*u.deg, dec = y*u.deg, unit = 'deg',frame='icrs')
            frame = AltAz(obstime=times, location=location)
            new_coord = coord.transform_to(frame)
            other_y = new_coord.alt.degree
            other_x  = new_coord.az.degree
            ha = (lst.hour - (x/15.0)) # given in hours, converted to degrees later for PA calc

        else :
            coord = AltAz(x*u.deg,y*u.deg)
            frame = SkyCoord(obstime=times, location=location)
            new_coord = coord.transform_to(frame)
            other_x = new_coord.ra.degree
            other_y = new_coord.dec.degree
            ha = (lst.hour - (other_x/15.0)) # given in hours, converted to degrees later for PA calc

        # parallactic angle calculation -----------------------------------------------------------------------------------
        sina = np.sin(np.radians(ha*15.0))
        cosa = (np.tan(np.radians(31.95844))*np.cos(np.radians(y)))-(np.sin(np.radians(y))*np.cos(np.radians(ha*15.0)))
        pa = np.degrees(np.arctan2(sina,cosa))

        return pa,other_x,other_y
    #-----------------------------------------------------------------------------------------------------------------------
    def start_tel(self, queue2,queue, sec,map_size,map_len,\
                            map_angle,coord1,coord1_unit,coord2,coord2_unit,epoch,object,step,\
                            coord_space,step_unit,map_size_unit,map_len_unit,map_angle_unit,numloop,kms_on_off):
        print(colored("FAKE TEL STARTED",'magenta'))
        PORT = 1806
        self.s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.s.bind(('',6666))
        # self.s.connect(('192.168.1.252',PORT))
        self.s.connect(('', PORT))
        print('Connected on port %s' % PORT)
        reply = self.s.recv(1024).decode("ascii")
        print(reply)
        self.s.send(b'Hello simple_socket_test')
        self.i = 0
        num_loop, calc_coord1, calc_coord2 = scan_params(coord_space,map_size,map_size_unit,map_len,map_len_unit,coord1,coord1_unit,coord2,coord2_unit,step,step_unit)
        commands = '{} {} {} {}'
        print(colored(commands.format(coord1,coord2,epoch,object),'yellow'))

        # cmnd_list = ['TIME_START_TELEMETRY ' + str(kms_on_off),'TIME_START_TRACKING off','TIME_SCAN_TIME ' + str(sec),'TIME_MAP_SIZE_EXTRA 1.1','TIME_MAP_SIZE ' + str(map_size),\
                        # 'TIME_MAP_ANGLE ' + str(map_angle),'TIME_MAP_COORD ' + str(coord_space),'TIME_TELESCOPE_WAIT_TIME 2','TIME_SEEK ' + commands.format(calc_coord1,calc_coord2,epoch,object)]


        i = 0
        # while i <= (len(cmnd_list) - 1):
        #     # self.s.send(cmnd_list[i].encode())
        #     reply = self.s.recv(1024).decode("ascii")
        #     print(reply, i)
        #     if i == 0 :
        #         # if 'OK' in reply:
        #         p = mp.Process(target=test_tracker.start_tracker, args=(queue,))
        #         p.start()
        #         i += 1
        #         # else :
        #         #     print('ERROR reply')
        #     else :
        #         # if 'OK' in reply :
        #         i += 1
        #         # else :
        #         #     print('ERROR reply')

        self.pos_update()
        time.sleep((int(sec)+(int(sec)*0.05))*2)

        msg = 'TIME_START_OBSERVING off'
        self.s.send(msg.encode())
        reply = self.s.recv(1024).decode("ascii")
        if 'OK' in reply  :
            print(reply)

        msg = 'TIME_START_TRACKING off'
        self.s.send(msg.encode())
        reply = self.s.recv(1024).decode("ascii")
        print(reply)
        if 'OK' in reply :
            ut.tel_exit.set()

        self.s.send(b'TIME_START_TELEMETRY 0')
        print('Telemetry Off')
        reply = self.s.recv(1024).decode("ascii")
        print(reply)

        print("Telescope Socket Closed")
        self.s.close()
        sys.exit()

    def pos_update(self):

        # ---------------------------------------------------------------
        msg = 'TIME_START_TRACKING arm'
        self.s.send(msg.encode())
        reply = self.s.recv(1024).decode("ascii")
        if 'OK' in reply  :
            print(reply)
        # --------------------------------------------------------------
        msg = 'TIME_START_TRACKING neg'
        self.s.send(msg.encode())
        reply = self.s.recv(1024).decode("ascii")
        if 'OK' in reply  :
            print(reply)

        time.sleep(2.0)
        # --------------------------------------------------------------
        msg = 'TIME_START_TRACKING track'
        self.s.send(msg.encode())
        reply = self.s.recv(1024).decode("ascii")
        if 'OK' in reply  :
            print(reply)
        # ---------------------------------------------------------------
        msg = 'TIME_START_OBSERVING on'
        self.s.send(msg.encode())
        reply = self.s.recv(1024).decode("ascii")
        if 'OK' in reply  :
            print(reply)
        # # -----------------------------------------------------------------

        return

        t = [] # to keep track of the last scan, either up or down
    # --------SPEEDS AND PARAMETERS---------------------------------------------
        if str(map_size_unit) != 'deg' :
            if str(map_size_unit) == 'arcsec' :
                map_size = float(map_size) / 3600.0
            else :
                map_size = float(map_size) / 60.0
        else :
            map_size = float(map_size)

        if str(map_len_unit) != 'deg' :
            if str(map_len_unit) == 'arcsec' :
                map_len = float(map_len) / 3600.0
            else :
                map_len = float(map_len) / 60.0
        else :
            map_len = float(map_len)


        '''
        # speeds = [float(map_size)*3600.0/float(scan_time),3600.0] # arcseconds per second, 3600 arcseconds per degree
        speeds = [1800.0,3600.0]
        area = float(map_len) #degrees wide of observing field
        rate = 20.0 #how many updates from telescope per second
        track = (speeds[1]/rate)/3600.0
        move = (speeds[0]/rate)/3600.0
        update = int((3600.0/(speeds[0]-15.0))*(area)*rate)
        n = 0
        slew_flag = 3.0 #starts the simulation tracking up to starting position
        x = float(calc_coord1) - map_len/2.# iterative
        y = float(calc_coord2) # iterative
        start_x = float(calc_coord1) - map_len / 2.# static
        start_y = float(calc_coord2) # static

        if str(step_unit) != 'deg':
            if str(step_unit) == 'arcmin' :
                step = float(step) / 60.0
            else :
                step = float(step) / 3600.0
        else :
            step = float(step)
        loops_deg = float(step) / 3600.0 #number of loops per degrees

        # -------------------------------------------------------------------------

        while not ut.tel_exit.is_set():
        # ==========================================================================
            if self.i <= num_loop :
            # ----------MOVING RIGHT---------------------------------------------------------------------------
                if slew_flag == 3.0:
                    if coord_space == 'RA' or coord_space == 'AZ':
                        while y <= start_y + map_len and not ut.tel_exit.is_set():
                            if y <= 360.0:
                                y = y + move
                            else :
                                y = y - 360.0 + move # keep coordinates realistic, can't go more than 360 degrees around a circle
                            pa,other_x,other_y = self.tel_move(coord_space,x,y,n)

                            tot = (float(self.i) / float(num_loop)) * 100.0
                            if coord_space == 'RA' :
                                queue.send([tot,pa,int(slew_flag),other_y,other_x,x,y,othertime.time()])
                            else :
                                queue.send([tot,pa,int(slew_flag),y,x,other_x,other_y,othertime.time()])

                            n = n + (1/rate)
                            othertime.sleep(1/rate)

                        else:
                            t.append(slew_flag)
                            slew_flag = 4.0
                            self.i += 1
                    else :
                        while x <= start_x + map_len and not ut.tel_exit.is_set():
                            if x <= 360.0:
                                x = x + move
                            else :
                                x = x - 360.0 + move # keep coordinates realistic, can't go more than 360 degrees around a circle
                            pa,other_x,other_y = self.tel_move(coord_space,x,y,n)

                            tot = (float(self.i) / float(num_loop)) * 100.0
                            if coord_space == 'DEC' :
                                queue.send([tot,pa,int(slew_flag),other_y,other_x,x,y,othertime.time()])
                            else :
                                queue.send([tot,pa,int(slew_flag),y,x,other_x,other_y,othertime.time()])

                            n = n + (1/rate)
                            othertime.sleep(1/rate)
                        else:
                            t.append(slew_flag)
                            slew_flag = 4.0
                            self.i += 1

            # ---------MOVING LEFT--------------------------------------------------------------------
                if slew_flag == 2.0:
                    if coord_space == 'RA' or coord_space == 'AZ':
                        while y >= start_y and not ut.tel_exit.is_set() :
                            if y <= 360.0:
                                y = y - move
                            else :
                                y = y - 360.0 + move # keep coordinates realistic, can't go more than 360 degrees around a circle
                            pa,other_x,other_y = self.tel_move(coord_space,x,y,n)

                            tot = (float(self.i) / float(num_loop)) * 100.0
                            if coord_space == 'RA' :
                                queue.send([tot,pa,int(slew_flag),other_y,other_x,x,y,othertime.time()])
                            else :
                                queue.send([tot,pa,int(slew_flag),y,x,other_x,other_y,othertime.time()])

                            n = n + (1/rate)
                            othertime.sleep(1/rate)

                        else:
                            t.append(slew_flag)
                            slew_flag = 4.0
                            self.i += 1
                    else :
                        while x >= start_x and not ut.tel_exit.is_set():
                            if x <= 360.0:
                                x = x - move
                            else :
                                x = x - 360.0 - move # keep coordinates realistic, can't go more than 360 degrees around a circle
                            pa,other_x,other_y = self.tel_move(coord_space,x,y,n)

                            tot = (float(self.i) / float(num_loop)) * 100.0
                            if coord_space == 'DEC' :
                                queue.send([tot,pa,int(slew_flag),other_y,other_x,x,y,othertime.time()])
                            else :
                                queue.send([tot,pa,int(slew_flag),y,x,other_x,other_y,othertime.time()])

                            n = n + (1/rate)
                            othertime.sleep(1/rate)
                        else:
                            t.append(slew_flag)
                            slew_flag = 4.0
                            self.i += 1


            # -------------MOVE UP----------------------------------------------------------
                if slew_flag == 4.0:
                    if coord_space == 'RA' or coord_space == 'AZ':
                        while x <= start_x + step and not ut.tel_exit.is_set():
                            if x <= 360.0:
                                x = x + track
                            else :
                                x = x - 360.0 + track # keep coordinates realistic, can't go more than 360 degrees around a circle
                            pa,other_x,other_y = self.tel_move(coord_space,x,y,n)

                            tot = (float(self.i) / float(num_loop)) * 100.0
                            if coord_space == 'RA' :
                                queue.send([tot,pa,int(slew_flag),other_y,other_x,x,y,othertime.time()])
                            else :
                                queue.send([tot,pa,int(slew_flag),y,x,other_x,other_y,othertime.time()])

                            n = n + (1/rate)
                            othertime.sleep(1/rate)

                        else:
                            if t[-1] == 2.0: # do the opposite of the last slew
                                slew_flag = 3.0
                            if t[-1] == 3.0:
                                slew_flag = 2.0
                            start_x = start_x + step
                    else :
                        while y < start_y + step and not ut.tel_exit.is_set():
                            if y <= 360.0:
                                y = y + track
                            else :
                                y = y - 360.0 + track # keep coordinates realistic, can't go more than 360 degrees around a circle
                            pa,other_x,other_y = self.tel_move(coord_space,x,y,n)

                            tot = (float(self.i) / float(num_loop)) * 100.0
                            if coord_space == 'DEC' :
                                queue.send([tot,pa,int(slew_flag),other_y,other_x,x,y,othertime.time()])
                            else :
                                queue.send([tot,pa,int(slew_flag),y,x,other_x,other_y,othertime.time()])

                            n = n + (1/rate)
                            othertime.sleep(1/rate)
                        else:
                            if t[-1] == 2.0: # do the opposite of the last slew
                                slew_flag = 3.0
                            if t[-1] == 3.0:
                                slew_flag = 2.0
                            start_y = start_y + step
            else :
                ut.tel_exit.set()
            #---------------------------------------------------------------------------------------------------------------------
        sys.exit()
        '''
