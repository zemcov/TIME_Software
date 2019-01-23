import socket, struct, subprocess, os, sys
import time as othertime
import numpy as np
import matplotlib.pyplot as plt
import astropy.units as u
from astropy.time import Time as thetime
from astropy.coordinates import SkyCoord, EarthLocation, AltAz, Angle, Latitude, Longitude, ICRS, Galactic, FK4, FK5
from astroplan import Observer

s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
PILOT1_PORT = 55555
PILOT1 = '127.0.0.1'
s.connect((PILOT1, PILOT1_PORT))

# initialize coordinates of source on sky and time stepper ----------------------------------------------------------------------------------
n = 0
count_ra = [0,20] # set '20' to whatever starting coordinate you want on sky, maybe bottom left of your map?
''' Each beam width is 0.43 ' or 0.0071666 degrees. So I subtracted that from 20 and kept going until I had 16 positions.'''
ra = [19.8925,19.8996,19.9068,19.9140,19.9211,19.9283,19.9355,19.9426,19.9498,19.9570,19.9641,19.9713,19.9785,19.9856,19.9928,20]
dec = np.full((1,16), 20, dtype=int) # this won't be incremented
mce_ra = []
mce_dec = []
mce_array = []
time = [] # telescope will be sending utctime, but we can't increment that more quickly than normal time
n = 0
while n <= 0.25 : #while our time incrementer is less than an hour long in sec

    print(ra[0])
    packer = struct.Struct('d')
    data = packer.pack(float(ra[0]))
    s.send(data)

    if count_ra[1] > count_ra[0] and count_ra[1] <= 22.0:
        count_ra[0] = count_ra[1]
        count_ra[1] = count_ra[1] + (0.0125)
        mce_ra.append(ra)
        mce_dec.append(dec)
        ra = [(x + 0.0125) for x in ra]

    elif count_ra[1] < count_ra[0] and count_ra[1] >= 20.0:
        count_ra[0] = count_ra[1]
        count_ra[1] = count_ra[1] - (0.0125)
        mce_ra.append(ra)
        mce_dec.append(dec)
        ra = [(x - 0.0125) for x in ra]

    elif count_ra[1] > count_ra[0] and count_ra[1] >= 22.0:#the case where we want to go from 90-0
        count_ra[0],count_ra[1] = count_ra[1],count_ra[0] # switch so greater number is first in arcount_ray

    else:# the case where we need to flip back to going from 0-90 again
        count_ra[0],count_ra[1] = count_ra[1],count_ra[0] # switch so greater number is second in array

    #update time coordinates
    time.append(n) # 20 Hz telescope update rate
    n = n + 0.05
#     print(n)

packer = struct.Struct('d')
data = packer.pack(float('0000'))
s.send(data)

# mce_array = list(zip(mce_ra,mce_dec))
# print(mce_array[0])
