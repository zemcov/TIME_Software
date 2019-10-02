import os, sys
import time as othertime
import numpy as np
import matplotlib.pyplot as plt
import astropy.units as u
from astropy.time import Time as thetime
from astropy.coordinates import SkyCoord, EarthLocation, AltAz, Angle, Latitude, Longitude, ICRS, Galactic, FK4, FK5
from astroplan import Observer
import utils as ut
from datetime import datetime
from termcolor import colored
# from astroplan import download_IERS_A
# download_IERS_A()

def start_kms(queue,coord_space,x,y,n):
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

    queue.send(pa)
#-----------------------------------------------------------------------------------------------------------------------
