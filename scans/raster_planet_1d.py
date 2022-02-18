import socket, struct, subprocess, os, sys
import time
import numpy as np
from scipy import interpolate as interp
from datetime import datetime
import astropy.units as u
from astropy.time import Time as thetime
from astropy.coordinates import EarthLocation, TETE, get_body
import multiprocessing as mp
from coms import tel_tracker
# import termcolor as colored
import config.utils as ut
from main.pos_counter import scan_params
import main.angle_converter as ac
from termcolor import colored
from multiprocessing import Manager

location = EarthLocation.from_geodetic(lon =-111.61485416666*u.deg, lat =31.95333333333*u.deg, height=1914*u.m)

class TIME_TELE :

    def start_sock(self,queue2,queue,sec,map_size,map_len,map_angle,coord1,coord1_unit,coord2,coord2_unit,epoch,\
                    object,step,coord_space,step_unit,map_size_unit,map_len_unit,map_angle_unit,numloop,kms_on_off):

        if coord_space not in ['RA','DEC']:
            raise ValueError('Az/El scans not currently enabled')

        if str(map_size_unit) != 'deg' or str(map_len_unit) != 'deg' or str(map_angle_unit) != 'deg' or str(step_unit) != 'deg':
            raise ValueError("raster_script_2d was expecting units in degrees")
        num_loop = int(numloop)

        # I am accepting telescope sim data for the gui
        self.i = Manager().list()
        self.i.append(0)
        PORT = 1806
        self.s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.s.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        self.s.bind(('',6666))
        self.s.connect(('192.168.1.252',PORT))
        print('Socket Connected')
        commands = '{} {} {} {}'
        print(colored(commands.format(coord1,coord2,epoch,object),'yellow'))

        # Figure out where the planet is
        planet = object
        object = 'TIME_'+object

        print("Calculating ephemeris for {}".format(planet))

        time_est = 2 + num_loop * 2 * int(sec) # Could likely be more accurate, but I don't understand the full set of telescope commands

        time_now = thetime(datetime.now().strftime('%Y-%m-%d %H:%M:%S')) + 7*u.h
        times = [time_now + 30*i*u.s for i in range(2*int(time_est)//30+1)]

        ras = np.zeros(len(times))
        decs = np.zeros(len(times))
        times_num = np.zeros(len(times))
        for i in range(len(times)):
            coords = get_planet_info(times[i],planet)
            ras[i] = coords.ra.degree
            decs[i] = coords.dec.degree
            times_num[i] = times[i].to_value('unix')

        ra_spline = interp.UnivariateSpline(times_num, ras, s=0, ext=3)
        dec_spline = interp.UnivariateSpline(times_num, decs, s=0, ext=3)

        p2 = mp.Process(target = self.loop_track , args=(num_loop,queue2))
        p2.start()

        cmnd_list = ['TIME_START_TELEMETRY ' + str(kms_on_off),'TIME_SEND_CMD CMD','TIME_TELESCOPE_WAIT_TIME 2',\
                        'TIME_START_TRACKING off','TIME_SCAN_TIME ' + str(sec),'TIME_MAP_SIZE ' + str(map_size),\
                                'TIME_MAP_ANGLE ' + str(map_angle),'TIME_MAP_COORD ' + str(coord_space)]
        #
        i = 0
        while i <= (len(cmnd_list) - 1):
            self.s.send(cmnd_list[i].encode())
            reply = self.s.recv(1024).decode("ascii")
            print(cmnd_list[i],reply)
            if i == 0 :
                if 'OK' in reply:
                    p = mp.Process(target=tel_tracker.start_tracker, args=(queue,))
                    p.start()
                    i += 1
                else :
                    print(cmnd_list[i] + ' sent ERROR reply')
                    sys.exit()
            else :
                if 'OK' in reply :
                    i += 1
                else :
                    print(cmnd_list[i] + ' sent ERROR reply')
                    sys.exit()

        ################################################################################################
        while self.i[-1] < int(num_loop) :

            if self.i[-1] == 0 :
                time_now = (thetime(datetime.now().strftime('%Y-%m-%d %H:%M:%S')) + 7*u.h).to_value('unix')
                new_ra = ra_spline(time_now)
                new_dec = dec_spline(time_now)

                commands = '{} {} {} {}'
                msg = 'TIME_SEEK ' + commands.format(new_ra,new_dec,'Apparent',object)
                self.s.send(msg.encode())
                reply = self.s.recv(1024).decode("ascii")
                print(msg,reply)

                self.pos_update()
                time.sleep((int(sec)+int(sec)*0.05)*2)
                self.s.send('TIME_TURNAROUND_NOTIFY'.encode())
                reply = self.s.recv(1024).decode("ascii")
                if 'OK' in reply:
                    pass
                else :
                    print('TIME_TURNAROUND_NOTIFY sent Error Reply')
                    sys.exit()


            else :
                time_now = (thetime(datetime.now().strftime('%Y-%m-%d %H:%M:%S')) + 7*u.h).to_value('unix')
                new_ra = ra_spline(time_now)
                new_dec = dec_spline(time_now)

                print('new_coords:',new_ra,new_dec)
                sys.stdout.flush()

                # feed new values to telescope
                commands = '{} {} {} {}'
                msg = 'TIME_SEEK ' + commands.format(new_ra,new_dec,'Apparent',object)
                self.s.send(msg.encode())
                reply = self.s.recv(1024).decode("ascii")
                print(msg,reply)

                time.sleep((int(sec)*0.9)*2)
                self.s.send('TIME_TURNAROUND_NOTIFY'.encode())
                reply = self.s.recv(1024).decode("ascii")
                if 'OK' in reply:
                    pass
                else :
                    print("TIME_TURNAROUND_NOTIFY sent Error Reply")
                    sys.exit()

            self.i[-1] += 1

        # Closing Commands ============================
        msg = 'TIME_START_OBSERVING off'
        self.s.send(msg.encode())
        reply = self.s.recv(1024).decode("ascii")
        print(msg,reply)
        # -------------------------------------------
        msg = 'TIME_START_TRACKING OFF'
        self.s.send(msg.encode())
        reply = self.s.recv(1024).decode("ascii")
        print(msg,reply)
        # ---------------------------------------------
        msg = 'TIME_START_TELEMETRY 0'
        self.s.send(msg.encode())
        print('Telemetry Off')
        reply = self.s.recv(1024).decode("ascii")
        print(msg,reply)
        if 'OK' in reply :
            ut.tel_exit.set()
        # # ------------------------------------------
        print("Telescope Socket Closed")
        self.s.close()
        sys.exit()
        # ================================================

    def pos_update(self):

        # -----------------------------------------------------------
        msg = 'TIME_START_TRACKING arm'
        self.s.send(msg.encode())
        reply = self.s.recv(1024).decode("ascii")
        print(msg,reply)
        # --------------------------------------------------------------
        msg = 'TIME_START_TRACKING neg'
        self.s.send(msg.encode())
        reply = self.s.recv(1024).decode("ascii")
        print(msg,reply)

        time.sleep(2.0)

        # --------------------------------------------------------------
        msg = 'TIME_START_TRACKING track'
        self.s.send(msg.encode())
        reply = self.s.recv(1024).decode("ascii")
        print(msg,reply)
        # ---------------------------------------------------------------
        msg = 'TIME_START_OBSERVING on'
        self.s.send(msg.encode())
        reply = self.s.recv(1024).decode("ascii")
        print(msg,reply)
        # -----------------------------------------------------------------

    def loop_track(self,num_loop,queue2):
        while not ut.tel_exit.is_set():
            tot = int((float(self.i[-1]) / float(num_loop)) * 100.0)
            sys.stdout.flush()
            queue2.put([tot])
            time.sleep(0.05)

        return


def get_planet_info(time,planet):
    frame = TETE(obstime=time, location=location)
    coords = get_body(planet,time=time,location=location).transform_to(frame)
    return coords
