from __future__ import print_function
import time as othertime
import os
import numpy as np
import matplotlib.pyplot as plt
import astropy.units as u
from astropy.time import Time as thetime
from astropy.coordinates import SkyCoord, EarthLocation, AltAz, Angle, Latitude, Longitude, ICRS, Galactic, FK4, FK5
from astroplan import Observer
import socket, struct, threading

# --------SPEEDS AND PARAMETERS---------------------------------------------
speeds = [315.0,3615.0] # arcseconds per second, 3600 arcseconds per degree
area = 2.0 #degrees wide of observing field
rate = 20.0 #how many updates from telescope per second
track = ((speeds[1]-15.0)/rate)/3600
move = ((speeds[0]-15.0)/rate)/3600
update = int((3600.0/(speeds[0]-15.0))*(area)*rate)
n = 0
i = 0
z = 0
slew_flag = 0.0 #starts the simulation tracking up to starting position
dec_start = 20.0 # static, for loop limits
ra = 20 # static
dec = 20 # static
loops_deg = 2 #number of loops per degrees = loops_deg
COLOR = 'black'
# -------------------------------------------------------------------------
s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
PILOT1_PORT = 8888
PILOT1 = '129.21.172.16' #I'm sending the socket packets to server
s.connect((PILOT1, PILOT1_PORT))
#message = 'Hello!'



def tel_move(RA,DEC,n,COLOR,s):
    #initialize  and update position coordinates
    location = EarthLocation.from_geodetic(lon =-111.5947*u.deg, lat =31.95844*u.deg, height=2097.024*u.m)
    kittpeak = Observer(location=location, name='kitt peak')
    coord = SkyCoord(ra = RA*u.deg, dec = DEC*u.deg, unit = 'deg',frame='icrs')
    time = thetime('2018-4-6 00:00:00')
    times = time + (n*u.second)
    lst = kittpeak.local_sidereal_time(times)
    ha = (lst.hour - (RA/15.0)) # given in hours, converted to degrees later for PA calc
    frame = AltAz(obstime=times, location=location)
    new_coord = coord.transform_to(frame)
    alt = new_coord.alt.degree
    az  = new_coord.az.degree

    # parallactic angle calculation -----------------------------------------------------------------------------------
    sina = np.sin(np.radians(ha*15.0))
    cosa = (np.tan(np.radians(31.95844))*np.cos(np.radians(DEC)))-(np.sin(np.radians(DEC))*np.cos(np.radians(ha*15.0)))
    pa = np.degrees(np.arctan2(sina,cosa))

    #s.send(message.encode('utf-8'))
    packer = struct.Struct('d d d d d d d')
    data = packer.pack(pa,slew_flag,alt,az,ra,dec,othertime.time())
    s.send(data)
    return s

#-----------------------------------------------------------------------------------------------------------------------
t = [] # to keep track of the last scan, either up or down
# ----------MOVING UP TO SCANNING POSITION---------------------------------------------------------------------------

while True:
    if slew_flag == 0.0:
        while dec <= (dec_start + 2) :
            dec = dec + track
            if ra <= 360.0:
                ra = ra + track
            else :
                ra = ra - 360.0 + track # keep coordinates realistic, can't go more than 360 degrees around a circle
            tel_move(ra,dec,n,COLOR,s)

            n = n + (1/rate)
            # plt.ion
            # plt.scatter(ra,dec,color='black')
            # plt.xlabel('DEC [deg]')
            # plt.ylabel('RA [deg]')
            plt.pause(1/rate)
            othertime.sleep(1/rate)
            z = z + 1
        else:
            t.append(slew_flag)
            slew_flag = 2.0
            COLOR = 'red'

# ---------MOVING DOWN TO SCANNING POSITION--------------------------------------------------------------------
    if slew_flag == 1.0:
        while dec >= dec_start :
            dec = dec - track
            if ra <= 360.0 :
                ra = ra + track
            else :
                ra = ra - 360.0 + track
            tel_move(ra,dec,n,COLOR,s)

            n = n + (1/rate)
            #plt.ion
            #plt.scatter(ra,dec,color='black')
            plt.pause(1/rate)
            othertime.sleep(1/rate)

        else:
            t.append(slew_flag)
            slew_flag = 2.0
            COLOR = 'red'

# -------------MOVE BACK AND FORTH IN SCAN----------------------------------------------------------
    if slew_flag == 2.0:
        ra_init = ra
        dec_init = dec
        loops = loops_deg*2*np.pi
        while ra <= ra_init + area:
            dec = dec_init + np.sin(loops*(ra-ra_init))
            ra = ra + (speeds[0]/3600.0/rate)
            tel_move(ra,dec,n,COLOR,s)
            n = n + (1/rate)
            #plt.ion
            #plt.scatter(ra,dec,color='red')
            plt.pause(1/rate)
            othertime.sleep(1/rate)

        else:
            COLOR = 'black'
            if t[len(t)-1] == 0: # do the opposite of the last slew
                slew_flag = 1.0
            if t[len(t)-1] == 1:
                slew_flag = 0.0
#---------------------------------------------------------------------------------------------------------------------
