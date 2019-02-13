# bowtie scan

import socket, struct, subprocess, os, sys
import time as othertime
import numpy as np
import matplotlib.pyplot as plt
import astropy.units as u
from astropy.time import Time as thetime
from astropy.coordinates import SkyCoord, EarthLocation, AltAz, Angle, Latitude, Longitude, ICRS, Galactic, FK4, FK5
from astroplan import Observer

''' how do I get the telescope to connect at the other end? '''
''' Need to send "TIME_START_TELEMETRY ON" before activating socket'''

def start_sock(ra,dec):
    # I am accepting telescope sim data for the gui
    PORT = 1806
    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    s.bind(('',PORT))
    print('Server Listening')
    s.listen(5)
    unpacker = struct.Struct('s i i i i d d d d d d d d d d d d d d d d') # d = float , s = char string , i = integer
    client, info = s.accept()
    othertime.sleep(1.0)
    # =================================================================================================================
    n = 0

    while True:

        if ut.tel_exit.is_set(): # if shutdown command from software, send shutdown command to tel
            print("Client Shutting Down")
            stop_msg = 'TIME_START_TELEMETRY off , '
            client.send(stop_msg.encode())
            break

        else :
            # option to send response after receiving packet
             = position_update(ra,dec)
            msg = ''
            client.send(msg.encode())

            data = client.recv(unpacker.size)
            # unpacking data packet ===============================================
            name, blanking, direction, observing, pad, /
            ut, lst, deltaT, cur_ra, cur_dec, map_ra, map_dec, /
            ra_off, dec_off, az, el, azvelcmd, elvelcmd, azvelact, elvelact, /
            pa = unpacker.unpack(data)
            # ==================================================================
            n += 1
            tel_data = np.array([float(blanking), float(direction), float(observing), float(pad), /
            ut, lst, deltaT, cur_ra, cur_dec, map_ra, map_dec, /
            ra_off, dec_off, az, el, azvelcmd, elvelcmd, azvelact, elvelact, /
            pa])
            np.save('/home/time/time-software-testing/TIME_Software/main/tempfiles/tele_packet%i.npy' %(n), tel_data)
            # send positional data to gui window
            queue.send([pa,float(direction),el,az,map_ra,map_dec,ut])

    print("Telescope Socket Closed")
    s.shutdown(socket.SHUT_RDWR)
    s.close()
    sys.exit()

def position_update(ra,dec):

    count_ra = [0,20] # set '20' to whatever starting coordinate you want on sky, maybe bottom left of your map?
    ''' Each beam width is 0.43 ' or 0.0071666 degrees. So I subtracted that from 20 and kept going until I had 16 positions.'''
    ra = [19.8925,19.8996,19.9068,19.9140,19.9211,19.9283,19.9355,19.9426,19.9498,19.9570,19.9641,19.9713,19.9785,19.9856,19.9928,20]
    dec = np.full((1,16), 20, dtype=int) # this won't be incremented
