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
# from astroplan import download_IERS_A
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

        return pa,other_y,other_x
    #-----------------------------------------------------------------------------------------------------------------------
    def start_tel(self,queue,map_len,map_len_unit,map_size,map_size_unit,scan_time,coord1,coord1_unit,coord2,coord2_unit,coord_space,step,step_unit):

        self.i = 0
        num_loop, calc_coord1, calc_coord2 = scan_params(map_size,map_size_unit,map_len,map_len_unit,coord1,coord1_unit,coord2,coord2_unit,step,step_unit)

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

        # speeds = [float(map_size)*3600.0/float(scan_time),3600.0] # arcseconds per second, 3600 arcseconds per degree
        speeds = [1800.0,3600.0]
        area = float(map_len) #degrees wide of observing field
        rate = 20.0 #how many updates from telescope per second
        track = (speeds[1]/rate)/3600.0
        move = (speeds[0]/rate)/3600.0
        update = int((3600.0/(speeds[0]-15.0))*(area)*rate)
        n = 0
        slew_flag = 3.0 #starts the simulation tracking up to starting position
        x = float(calc_coord1.degree) # iterative
        y = float(calc_coord2.degree) # iterative
        start_x = float(calc_coord1.degree) # static
        start_y = float(calc_coord2.degree) # static

        if str(step_unit) != 'arcsec':
            if str(step_unit) == 'arcmin' :
                step = float(step) * 60.0
            else :
                step = float(step) * 3600.0
        loops_deg = float(step) / 3600.0 #number of loops per degrees

        # -------------------------------------------------------------------------

        print(colored((x,y),'yellow'))
        while not ut.tel_exit.is_set():
        # ==========================================================================
            if self.i <= num_loop :
            # ----------MOVING RIGHT---------------------------------------------------------------------------
                if slew_flag == 3.0:
                    if coord_space == 'RA' or coord_space == 'AZ':
                        while y <= start_y + map_len :
                            if y <= 360.0:
                                y = y + move
                            else :
                                y = y - 360.0 + move # keep coordinates realistic, can't go more than 360 degrees around a circle
                            pa,other_y,other_x = self.tel_move(coord_space,x,y,n)

                            tot = int((self.i / num_loop) * 100)
                            queue.send([tot,pa,int(slew_flag),other_y,other_x,x,y,othertime.time()])

                            n = n + (1/rate)
                            othertime.sleep(1/rate)

                        else:
                            t.append(slew_flag)
                            slew_flag = 4.0
                            self.i += 1
                    else :
                        while x <= start_x + map_len :
                            if x <= 360.0:
                                x = x + move
                            else :
                                x = x - 360.0 + move # keep coordinates realistic, can't go more than 360 degrees around a circle
                            pa,other_y,other_x = self.tel_move(coord_space,x,y,n)

                            tot = int((self.i / num_loop) * 100)
                            queue.send([tot,pa,int(slew_flag),other_y,other_x,x,y,othertime.time()])

                            n = n + (1/rate)
                            othertime.sleep(1/rate)
                        else:
                            t.append(slew_flag)
                            slew_flag = 4.0
                            self.i += 1

            # ---------MOVING LEFT--------------------------------------------------------------------
                if slew_flag == 2.0:
                    if coord_space == 'RA' or coord_space == 'AZ':
                        while y >= start_y - map_len :
                            if y <= 360.0:
                                y = y + move
                            else :
                                y = y - 360.0 + move # keep coordinates realistic, can't go more than 360 degrees around a circle
                            pa,other_y,other_x = self.tel_move(coord_space,x,y,n)

                            tot = int((self.i / num_loop) * 100)
                            queue.send([tot,pa,int(slew_flag),other_y,other_x,x,y,othertime.time()])

                            n = n + (1/rate)
                            othertime.sleep(1/rate)

                        else:
                            t.append(slew_flag)
                            slew_flag = 4.0
                            self.i += 1
                    else :
                        while x <= start_x + map_len :
                            if x <= 360.0:
                                x = x + move
                            else :
                                x = x - 360.0 + move # keep coordinates realistic, can't go more than 360 degrees around a circle
                            pa,other_y,other_x = self.tel_move(coord_space,x,y,n)

                            tot = int((self.i / num_loop) * 100)
                            queue.send([tot,pa,int(slew_flag),other_y,other_x,x,y,othertime.time()])

                            n = n + (1/rate)
                            othertime.sleep(1/rate)
                        else:
                            t.append(slew_flag)
                            slew_flag = 4.0
                            self.i += 1


            # -------------MOVE UP----------------------------------------------------------
                if slew_flag == 4.0:
                    if coord_space == 'RA' or coord_space == 'AZ':
                        while x <= start_x + step :
                            if x <= 360.0:
                                x = x + track
                            else :
                                x = x - 360.0 + track # keep coordinates realistic, can't go more than 360 degrees around a circle
                            pa,other_y,other_x = self.tel_move(coord_space,x,y,n)

                            tot = int((self.i / num_loop) * 100)
                            queue.send([tot,pa,int(slew_flag),other_y,other_x,x,y,othertime.time()])

                            n = n + (1/rate)
                            othertime.sleep(1/rate)

                        else:
                            if t[len(t)-1] == 2.0: # do the opposite of the last slew
                                slew_flag = 3.0
                            if t[len(t)-1] == 3.0:
                                slew_flag = 2.0
                    else :
                        while y <= start_y + step :
                            if y <= 360.0:
                                y = y + track
                            else :
                                y = y - 360.0 + track # keep coordinates realistic, can't go more than 360 degrees around a circle
                            pa,other_y,other_x = self.tel_move(coord_space,x,y,n)

                            tot = int((self.i / num_loop) * 100)
                            queue.send([tot,pa,int(slew_flag),other_y,other_x,x,y,othertime.time()])

                            n = n + (1/rate)
                            othertime.sleep(1/rate)
                        else:
                            if t[len(t)-1] == 2.0: # do the opposite of the last slew
                                slew_flag = 3.0
                            if t[len(t)-1] == 3.0:
                                slew_flag = 2.0

            else :
                ut.tel_exit.set()
            #---------------------------------------------------------------------------------------------------------------------
        sys.exit()
