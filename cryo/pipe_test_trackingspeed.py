
'''The maximum slew speed of the telescope is rated at 60 deg/min or 1 deg/sec or 3600 "/s. Since the sidereal rate is at 15 "/s, we must
be incrementing our position vectors by 3585 "/s. Since we are updating the position 20 times/sec , this means that each update should move
the position by 179.25 arcseconds ("), or, since our position vectors are in degrees... 0.04979 deg. The following code produces this result.'''

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
m = 0
dec = 20.0 # degrees
ra = 20.0 # degrees

''' The behavior will look like tracking accross RA positions as constant DEC, then moving up slightly by DEC and tracking again backwards through RA.
This will not create a zigzag pattern, but it will make a "box" on the sky going from 20-90 deg and back again, which is good enough for our testing purposes.'''
newra = [0,20]
newdec = 20

for i in range(100):
    #initialize  and update position coordinates
    location = EarthLocation.from_geodetic(lon =-111.5947*u.deg, lat =31.95844*u.deg, height=2097.024*u.m)
    kittpeak = Observer(location=location, name='kitt peak')
    coord = SkyCoord(ra = newra[1]*u.deg, dec = newdec*u.deg, unit = 'deg',frame='icrs')
    time = thetime('2018-1-16 00:00:00')
    times = time + (m*u.second)
    frame = AltAz(obstime=times, location=location)
    new_coord = coord.transform_to(frame)
    alt = new_coord.alt.radian
    az  = new_coord.az.radian

    # parallactic angle calculation -----------------------------------------------------------------------------------
    sindec = (np.sin(alt) * np.sin(np.radians(31.95844))) + (np.cos(alt) * np.cos(az) * np.cos(np.radians(31.95844)))
    cosdec = np.sqrt(1.0 - sindec * sindec)
    if cosdec != 0:
        cosdec = 1/(cosdec)
    sin_h = -cosdec * np.cos(alt) *np.sin(az)
    pa = (np.degrees(np.arcsin(np.cos(np.radians(31.95844))*sin_h/cosdec)))
    #---------------------------------------------------------------------------------------------------------------------
    #print(pa) # show new parallactic angle in degrees
    #print(new_coord.alt.degree) # show new position in degrees
    #print(new_coord.az.degree)

    if newra[1] > newra[0] and newra[1] <= 90.0:
        newra[0] = newra[1]
        newra[1] = ra + (0.04979*n)

    elif newra[1] < newra[0] and newra[1] >= 20.0:
        newra[0] = newra[1]
        newra[1] = newra[1] - (0.04929*n)

    elif newra[1] > newra[0] and newra[1] >= 90.0:#the case where we want to go from 90-0
        n = 0
        newdec = newdec + (0.04929)
        newra[0],newra[1] = newra[1],newra[0] # switch so greater number is first in array

    else:# the case where we need to flip back to going from 0-90 again
        n = 0
        newdec = newdec + (0.04929)
        newra[0],newra[1] = newra[1],newra[0] # switch so greater number is second in array

    plt.scatter(new_coord.az.degree,new_coord.alt.degree)
    n = n + 1
    m = m + 1 #for updating the time that the coordinate transfomation will use

    othertime.sleep(3.0) #to wait 3 seconds


''' The difference here is that the new coordinates have to be fed to SkyCoord each iteration to get updated alt and az, and requires them
to be in the for loop with everything else.'''
