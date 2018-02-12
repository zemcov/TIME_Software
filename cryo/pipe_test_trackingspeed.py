
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

''' The behavior will look like tracking accross RA positions as constant DEC, then moving up slightly by DEC and tracking again backwards through RA.
This will not create a zigzag pattern, but it will make a "box" on the sky going from 20-90 deg and back again, which is good enough for our testing purposes.'''
newra = [0,20]
newdec = 20

for i in range(1000000):
    if newra[1] > newra[0] and newra[1] <= 60.0:
        newra[0] = newra[1]
        newra[1] = newra[1] + (0.04979)

    elif newra[1] < newra[0] and newra[1] >= 20.0:
        newra[0] = newra[1]
        newra[1] = newra[1] - (0.04979)

    elif newra[1] > newra[0] and newra[1] >= 60.0:#the case where we want to go from 90-0
        newdec = newdec + (0.04979)
        newra[0],newra[1] = newra[1],newra[0] # switch so greater number is first in array

    else:# the case where we need to flip back to going from 0-90 again
        newdec = newdec + (0.04979)
        newra[0],newra[1] = newra[1],newra[0] # switch so greater number is second in array

    #initialize  and update position coordinates
    location = EarthLocation.from_geodetic(lon =-111.5947*u.deg, lat =31.95844*u.deg, height=2097.024*u.m)
    kittpeak = Observer(location=location, name='kitt peak')
    coord = SkyCoord(ra = newra[1]*u.deg, dec = newdec*u.deg, unit = 'deg',frame='icrs')
    time = thetime('2018-1-16 00:00:00')
    times = time + (n*u.second)
    lst = kittpeak.local_sidereal_time(times)
    ha = (lst.hour - (newra[1]/15.0)) # given in hours, converted to degrees later for PA calc
    frame = AltAz(obstime=times, location=location)
    new_coord = coord.transform_to(frame)
    alt = new_coord.alt.degree
    az  = new_coord.az.degree

    # parallactic angle calculation -----------------------------------------------------------------------------------
    sina = np.sin(np.radians(ha*15.0))
    cosa = (np.tan(np.radians(31.95844))*np.cos(np.radians(newdec)))-(np.sin(np.radians(newdec))*np.cos(np.radians(ha*15.0)))
    pa = np.degrees(np.arctan2(sina,cosa))

    #---------------------------------------------------------------------------------------------------------------------
    #plt.scatter(new_coord.az.degree,new_coord.alt.degree)
    print(pa) # show new parallactic angle in degrees
    #print(new_coord.alt.degree) # show new position in degrees
    #print(new_coord.az.degree)
    plt.ion
    plt.scatter(newra[1],newdec)
    #plt.scatter(az,alt)
    plt.pause(0.05)
    n = n + 0.05 #for updating the time that the coordinate transfomation will use

    othertime.sleep(0.05) #to wait 1/20 th of a second
'''One issue that came up is that if you feed the coordinates a limit close to 90, SkyCoord complains it's not within the limits to evaluate.
So just keep the limit between -85 and 85 for RA for testing purposes. '''
