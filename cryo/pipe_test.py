from __future__ import print_function
import time as othertime
import os
import numpy as np
import matplotlib.pyplot as plt
import astropy.units as u
from astropy.time import Time as thetime
from astropy.coordinates import SkyCoord, EarthLocation, AltAz, Angle, Latitude, Longitude, ICRS, Galactic, FK4, FK5
from astroplan import Observer

# initialize coordinates of source on sky and time stepper ----------------------------------------------------------------------------------
n = 0
dec = 45 # degrees
ra = 45 # degrees

# this sections simulates tracking at the sidereal rate with data transmitted at 20 reports/sec -----------------------------------------------------------
for x in range(10000):
    location = EarthLocation.from_geodetic(lon =-111.5947*u.deg, lat =31.95844*u.deg, height=2097.024*u.m)
    kittpeak = Observer(location=location, name='kitt peak')
    coord = SkyCoord(ra = ra*u.deg, dec = dec*u.deg, unit = 'deg',frame='icrs')
    time = thetime('2018-1-16 00:00:00')
    times = time + (n*u.second)
    frame = AltAz(obstime=times, location=location)
    new_coord = coord.transform_to(frame)
    alt = new_coord.alt.radian
    az  = new_coord.az.radian

# parallactic angle calculation -----------------------------------------------------------------------------------
    sindec = (np.sin(alt) * np.sin(31.95844)) + (np.cos(alt) * np.cos(az) * np.cos(31.95844))
    cosdec = np.sqrt(1.0 - sindec * sindec)
    if cosdec != 0:
        cosdec = 1/(cosdec)
    sin_h = -cosdec * np.cos(alt) *np.sin(az)
    pa = (np.degrees(np.arcsin(np.cos(31.95844)*sin_h/cosdec)))
#---------------------------------------------------------------------------------------------------------------------
    print(pa) # show new parallactic angle in degrees
    print(new_coord.alt.degree) # show new position in degrees
    print(new_coord.az.degree)

    othertime.sleep(0.05) #to wait a 1/20 th of a second
    os.system('clear') #to clear previous number

    n = n + 0.05

# this section simulates tracking at 15"/sec at 20 reports/sec
    #still figuring out how to do this one...
