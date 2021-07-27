import os, sys
import time as othertime
import numpy as np
import matplotlib.pyplot as plt
import matplotlib.dates as mdates
import astropy.units as u
from astropy.time import Time as thetime
from astropy.coordinates import SkyCoord, EarthLocation, AltAz, Angle, Latitude, Longitude, ICRS, Galactic, FK4, FK5
from astroplan import Observer
from datetime import datetime
from astroplan import download_IERS_A
# download_IERS_A()

def pa_calc(ctime,RA,DEC):
    #initialize  and update position coordinates
    location = EarthLocation.from_geodetic(lon =-111.5947*u.deg, lat =31.95844*u.deg, height=2097.024*u.m)
    kittpeak = Observer(location=location, name='kitt peak')
    lst = kittpeak.local_sidereal_time(ctime)

    coord = SkyCoord(ra = RA*u.deg, dec = DEC*u.deg, unit = 'deg',frame='icrs')
    frame = AltAz(obstime=ctime, location=location)
    new_coord = coord.transform_to(frame)
    ha = (lst.hour - (RA/15.0)) # given in hours, converted to degrees later for PA calc

    # parallactic angle calculation -----------------------------------------------------------------------------------
    sina = np.sin(np.radians(ha*15.0))
    cosa = (np.tan(np.radians(31.95844))*np.cos(np.radians(DEC)))-(np.sin(np.radians(DEC))*np.cos(np.radians(ha*15.0)))
    pa = np.degrees(np.arctan2(sina,cosa))

    return pa

if __name__ == '__main__':

    RA = float(input('enter RA : [deg] '))
    DEC = float(input('enter DEC : [deg] '))
    first = input('enter first datetime : [mm/dd/yy hh:mm:ss] ')
    second = input('enter second datetime : [mm/dd/yy hh:mm:ss] ')
    # RA = 206.8783
    # DEC = -11.7525
    # first = '03/20/19 04:00:00'
    # second = '03/20/19 05:00:00'
    first = datetime.strptime(first,'%m/%d/%y %H:%M:%S')
    second = datetime.strptime(second,'%m/%d/%y %H:%M:%S')
    start = thetime(first,format='datetime')
    stop = thetime(second,format='datetime')

    pas = []
    times = []
    while start < stop :
        start = start + (30*u.second)
        # print(start)
        pa = pa_calc(start,RA,DEC)
        pas.append(pa)
        times.append(start.value)

    fig, ax = plt.subplots()
    ax.scatter(times,pas)
    ax.xaxis.set_major_formatter(mdates.DateFormatter('%m/%d/%y %H:%M:%S'))
    ax.set_xlabel('TIME')
    ax.set_ylabel('Parallactic Angle (PA) [deg]')
    ax.grid(True)
    fig.autofmt_xdate()
    plt.show()
