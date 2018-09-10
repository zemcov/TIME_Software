import socket, threading, sys, binascii, struct, sys, time, math, pickle
import numpy as np
# import matplotlib
# matplotlib.use('TkAgg')
import matplotlib.pyplot as plt
import matplotlib.animation as animation
# import astropy.units as u
# from astropy.time import Time as thetime
# from astropy.coordinates import SkyCoord, EarthLocation, AltAz, Angle, Latitude, Longitude, ICRS, Galactic, FK4, FK5
# from astroplan import Observer

import PID
from util import *
from rotate_motor import rotate_motor
from encoder import get_pos

'''
Look into MSD lightning talk schedule

packet format:
Paralactic Angle (float) | Time packet is sent (double) | Bool Slewing | Bool Observing/Tracking | Bool Staring (sidereal rate)
'''


TELESCOPE_HOST = '129.21.74.200'#falsf;
TELESCOPE_PORT = 50008
CONTROL_HOST = ''
CONTROL_PORT = 8888

# PACKET_FORMAT = 'fd???'
DEG_TO_STEP = 0.36  # 21.6', 1296"
GEAR_RATIO = 160.0
# NUM_SAMPLES = float('inf')
NUM_SAMPLES = 800
STEP_OFFSET = 150
DEMO = True

deg_to_step = lambda degs: float(degs) * GEAR_RATIO / DEG_TO_STEP
step_to_deg = lambda steps: float(steps) / GEAR_RATIO * DEG_TO_STEP


class KMirror():
    def __init__(self):
        self.encoder_pos_s = 0.0
        self.calibrated_origin = -135.0
        self.speed = 0
        self.dest_pos = 0
        self.last_time = time.time()
        # self.pid = PID.PID(P=17.0, I=11.0, D=0.01)
        self.pid = PID.PID(P=6.0, I=3.0, D=0.01)
        self.pid.SetPoint = 0.0
        self.pid.setSampleTime(0.01)
        self.pid.setWindup(250.0)

    def move_cmd(self, steps, set_point, vel_est):#, speed):
        self.dest_pos = self.encoder_pos_s + steps
        # self.pid.SetPoint = self.dest_pos
        self.pid.SetPoint = self.encoder_pos_s + set_point
        self.pid.update(self.encoder_pos_s)
        self.speed = self.pid.output
        if sign(self.speed) == sign(vel_est):
            if abs(self.speed) == self.speed:
                self.speed = max(self.speed, 1.0)
            else:
                self.speed = min(self.speed, -1.0)
            if abs(self.speed) > abs(self.pid.output):
                print "PID wanted to go slower than minimum speed"
            rotate_motor(steps, abs(self.speed))
        else:
            self.speed = 0.0

    def update(self):
        self.encoder_pos_s = deg_to_step(get_pos())        


def main():
    # main data structure between threads for telescope updates
    updateList = []

    tele_thread = TelescopeThread(updateList)#threading.Thread(target=telescope_socket)
    tele_thread.start()
    # un-comment when we start communcating with Victoria's control computer
    # ctrl_thread = threading.Thread(target=victoria_socket)
    # ctrl_thread.start()

    # Motor control
    debug_vars = {
        'abs_update_degs_list': [],
        'abs_encoder_degs_list': [],
        'abs_err_arcsec_list': [],
        'speed_list': [],
        'motor_set_point': [],
    }

    measured_speed = [0.0]
    kalman_speed = []
    process_variance = 5e-3
    estimated_measurement_variance = 1
    kalman_filter = KalmanFilter(process_variance, estimated_measurement_variance)

    # telescope_socket()
    kmirror = KMirror()
    try:
        old_len = len(updateList)
        cumul_index = 0
        while 1:
            # Wait for a new update to come in
            # print "Waiting", len(updateList)
            while len(updateList) <= old_len:
                continue
            old_len = len(updateList)

            # NEW UPDATE
            if len(updateList) == 1:
                #first update
                # kmirror.encoder_pos_s = deg_to_step(updateList[-1].abs_degree_pos)
                kmirror.update()
            elif len(updateList) >= 2:
                # Kalman stuff
                # print "Kalman Stuff"
                tele_vel = updateList[-1].abs_degree_pos - updateList[-2].abs_degree_pos
                time_delta = updateList[-1].when_sent - updateList[-2].when_sent
                tele_vel /= time_delta
                # if tele_vel > 100 or tele_vel < -100:
                #     continue
                if (tele_vel > 0 and measured_speed[-1] < 0) or (tele_vel < 0 and measured_speed[-1] > 0) or \
                    updateList[-1].flag != updateList[-2].flag:
                    kalman_filter.reset(tele_vel)
                kalman_filter.input_latest_noisy_measurement(tele_vel)
                kalman_speed.append(kalman_filter.get_latest_estimated_measurement())
                measured_speed.append(tele_vel)

                #every subsequent update
                if len(updateList) >= 3:
                    # print "Getting encoder"
                    kmirror.update()
                    update_debugs(debug_vars, kmirror, updateList[-1])
                set_point = deg_to_step(updateList[-1].abs_degree_pos) - kmirror.encoder_pos_s
                if kmirror.speed > 0.0:
                    # steps_to_move = max(1.0, set_point)
                    steps_to_move = math.ceil(set_point) + STEP_OFFSET
                else:
                    # steps_to_move = min(-1.0, set_point)
                    steps_to_move = math.floor(set_point) - STEP_OFFSET
                # print "Move_cmd"
                print "%s - %s = %s" % (updateList[-1].abs_degree_pos, step_to_deg(kmirror.encoder_pos_s), set_point)
                kmirror.move_cmd(steps_to_move, set_point, kalman_speed[-1])

            if len(debug_vars['speed_list']) >= NUM_SAMPLES:
                break
    except KeyboardInterrupt:
        pass
    finally:
        tele_thread.stop()
        errors = np.array(debug_vars['abs_err_arcsec_list'])
        errors = np.absolute(errors)
        print "Average error (arcsec): {:3.3f}".format(np.mean(errors))

        x_axis = range(len(debug_vars['speed_list']))
        packet_lag = [(update.when_received - update.when_sent)*1000.0 for update in updateList[:len(x_axis)]]
        print "Average Packet Lag (ms): {:3.3f}".format(np.mean(np.absolute(np.array(packet_lag))))
        print "Std Packet Lag (ms): {:3.3f}".format(np.std(np.absolute(np.array(packet_lag))))

        # graph debug stuff
        f, axarr = plt.subplots(3, sharex=True)
        # plt.subplots_adjust(left=.04, right=.95, bottom=.04, top=.95, wspace=.20, hspace=.20)
        # clean encoder signal
        avg_encoder = np.mean(np.absolute(np.array(debug_vars['abs_encoder_degs_list'])))
        encoder_signal = [val if abs(val) < avg_encoder * 10 else avg_encoder for val in debug_vars['abs_encoder_degs_list']]
        print "Deleted %s outlier values" % np.sum(np.array([0 if abs(val) < avg_encoder * 10 else 1 for val in debug_vars['abs_encoder_degs_list']]))

        # lines = []

        line, = axarr[0].plot(x_axis, encoder_signal)
        # lines.append(line)
        line, = axarr[0].plot(x_axis, debug_vars['abs_update_degs_list'])
        # lines.append(line)
        # axarr[0].plot(x_axis, debug_vars['motor_set_point'])
        axarr[0].set(ylabel='degrees')
        axarr[0].set_title('Absolute Rotational Position')
        # print axarr[0].get_ylim()
        # print axarr[0].get_xlim()

        line, = axarr[1].plot(x_axis, debug_vars['abs_err_arcsec_list'])
        # lines.append(line)
        line, = axarr[1].plot(np.zeros(len(x_axis)))
        # lines.append(line)
        axarr[1].set(ylabel='arcsec')
        axarr[1].set_title('Error')
        # axarr[1].grid(True, which='both', axis='y')
        # print axarr[1].get_ylim()

        line, = axarr[2].plot(x_axis, debug_vars['speed_list'])
        # lines.append(line)
        line, = axarr[2].plot(np.zeros(len(x_axis)))
        # lines.append(line)
        # axarr[2].set(ylabel='arcsec/sec')
        axarr[2].set(ylabel='steps/sec')
        axarr[2].set_title('Motor Speed')
        # print axarr[2].get_ylim()

        # altaxs = axarr[2].twinx()
        # # s2 = np.sin(2 * np.pi * t)
        # # altaxs.plot(t, s2, 'r.')
        # line, = altaxs.plot(x_axis, [deg_to_arcsec(step_to_deg(num)) for num in debug_vars['speed_list']])
        # lines.append(line)
        # altaxs.set_ylabel('arcsec/sec')#, color='r')
        # altaxs.tick_params('y', colors='r')
        # axarr[2].grid(True, which='both', axis='y')

        f2, axarr2 = plt.subplots(2, sharex=True)
        plt.subplots_adjust(left=.04, right=.95, bottom=.04, top=.95, wspace=.20, hspace=.20)
        try:
            del measured_speed[:2]
            # if len(measured_speed) - len(x_axis) > 0:
            #     for _ in range(len(measured_speed) - len(x_axis)):
            #         del measured_speed[-1]
            del kalman_speed[0]
            if len(measured_speed) > len(x_axis):
                axarr2[0].plot(x_axis, measured_speed[:len(x_axis)])
            else:
                axarr2[0].plot(x_axis[:len(measured_speed)], measured_speed)
            axarr2[0].plot(x_axis, kalman_speed[:len(x_axis)])
            axarr2[0].set(ylabel='degrees/sec')
            axarr2[0].set_title('Kalman Response to Velocity')
            # print axarr2[0].get_ylim()
        except Exception as e:
            print e

        axarr2[1].plot(x_axis, packet_lag)
        axarr2[1].plot(np.zeros(len(x_axis)))
        axarr2[1].set(ylabel='ms')
        axarr2[1].set_title('Packet lag')

        # with open('objs.pkl', 'w') as p:  # Python 3: open(..., 'wb')
        #     pickle.dump([x_axis, encoder_signal, debug_vars], p)
        #     print "saved"

        # def update(num, lines):
        #     print num
        #     lines[0].set_data(x_axis[:int(num)], encoder_signal[:int(num)])
        #     lines[0].axes.axis([-40, 840, 30.5, 37.8])
        #     lines[1].set_data(x_axis[:int(num)], debug_vars['abs_update_degs_list'][:int(num)])
        #     lines[1].axes.axis([-40, 840, 30.5, 37.8])

        #     lines[2].set_data(x_axis[:int(num)], debug_vars['abs_err_arcsec_list'][:int(num)])
        #     lines[2].axes.axis([-40, 840, -1500, 2500])
        #     lines[3].set_data(x_axis[:int(num)], np.zeros(len(x_axis))[:int(num)])
        #     lines[3].axes.axis([-40, 840, -1500, 2500])

        #     lines[4].set_data(x_axis[:int(num)], debug_vars['speed_list'][:int(num)])
        #     lines[4].axes.axis([-40, 840, -500, 2000])
        #     lines[5].set_data(x_axis[:int(num)], np.zeros(len(x_axis))[:int(num)])
        #     lines[5].axes.axis([-40, 840, -500, 2000])

        #     lines[6].set_data(x_axis[:int(num)], [deg_to_arcsec(step_to_deg(num)) for num in debug_vars['speed_list']][:int(num)])
        #     # lines[6].axes.axis([-40, 840, -500, 2000])
        #     return lines

        # ani = animation.FuncAnimation(f, update, len(x_axis), fargs=[lines],
        #                       interval=25, blit=False)
        # # ani.save('test.gif', writer='imagemagick', fps=10))
        plt.show()


def update_debugs(debug_vars, kmirror, last_update):
    error_s = deg_to_step(last_update.abs_degree_pos) - kmirror.encoder_pos_s
    error_arcsec = deg_to_arcsec(step_to_deg(error_s))
    print "Error (steps, arcsec): {:3.3f}, {:3.3f}".format(error_s, error_arcsec)
    debug_vars['abs_update_degs_list'].append(last_update.abs_degree_pos)
    debug_vars['abs_encoder_degs_list'].append(step_to_deg(kmirror.encoder_pos_s))
    # debug_vars['speed_list'].append(deg_to_arcsec(step_to_deg(kmirror.speed)))
    # debug_vars['speed_list'].append(step_to_deg(kmirror.speed))
    debug_vars['speed_list'].append(kmirror.speed)
    debug_vars['abs_err_arcsec_list'].append(error_arcsec)
    debug_vars['motor_set_point'].append(step_to_deg(kmirror.dest_pos))


# Thread for communicating with the telescope
# needs to be passed the updateList object so it can write to it
class TelescopeThread(threading.Thread):
    def __init__(self, masterList, *args, **kwargs):
        super(TelescopeThread, self).__init__(*args, **kwargs)
        self._stop = threading.Event()
        self.masterList = masterList

    def stop(self):
        self._stop.set()

    def stopped(self):
        return self._stop.isSet()

    def run(self):
        if DEMO:
            with open('pa.txt', 'r') as f:
                for line in f.readlines():
                    if not self.stopped():
                        pa, flag = line.strip().split(',')
                        update = TelescopeUpdate(float(pa)/2.0, time.time(), time.time(), bool(flag))
                        self.masterList.append(update)
                        # print float(pa)/2.0
                        time.sleep(1.0/20.0)
                    else:
                        break
                self.stop()
        else:
            s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            s.connect((TELESCOPE_HOST, TELESCOPE_PORT))

            unpacker = struct.Struct(PACKET_FORMAT)

            try:
                while not self.stopped():
                   data = s.recv(unpacker.size)
                   # pa,sent,flag,_,_, = unpacker.unpack(data)
                   pa,sent,flag,_,_, = unpacker.unpack(data)
                   # pa_ang = tel_move(ra,dec,n)
                   update = TelescopeUpdate(pa/2.0, time.time(), sent, flag)
                   self.masterList.append(update)
            except Exception as e:
                print e
                s.close()
                self.stop()


# A class to encapsulate each "update" from the telescope
# for now includes the rotational position, time received, and time sent
class TelescopeUpdate():
    def __init__(self, abs_degree_pos, when_received, when_sent, flag):
        self.abs_degree_pos = abs_degree_pos
        self.when_received = when_received
        self.when_sent = when_sent
        self.flag = flag

    def delta_degs(self, other_update):
        return self.abs_degree_pos - other_update.abs_degree_pos

    def delta_steps(self, other_update):
        return deg_to_step(self.delta_degs(other_update))

    def __str__(self):
        return str(self.abs_degree_pos)
    def __repr__(self):
        return str(self.abs_degree_pos)


class KalmanFilter(object):
    def __init__(self, process_variance, estimated_measurement_variance):
        self.process_variance = process_variance
        self.estimated_measurement_variance = estimated_measurement_variance
        self.posteri_estimate = 0.0
        self.posteri_error_estimate = 1.0

    def reset(self, correction):
        # self.posteri_estimate = 0.0
        self.posteri_estimate = correction/2.0
        self.posteri_error_estimate = 1.0

    def input_latest_noisy_measurement(self, measurement):
        priori_estimate = self.posteri_estimate
        priori_error_estimate = self.posteri_error_estimate + self.process_variance

        blending_factor = priori_error_estimate / (priori_error_estimate + self.estimated_measurement_variance)
        self.posteri_estimate = priori_estimate + blending_factor * (measurement - priori_estimate)
        self.posteri_error_estimate = (1 - blending_factor) * priori_error_estimate

    def get_latest_estimated_measurement(self):
        return self.posteri_estimate


# def tel_move(RA,DEC,n):
#     #initialize  and update position coordinates
#     location = EarthLocation.from_geodetic(lon =-111.5947*u.deg, lat =31.95844*u.deg, height=2097.024*u.m)
#     kittpeak = Observer(location=location, name='kitt peak')
#     coord = SkyCoord(ra = RA*u.deg, dec = DEC*u.deg, unit = 'deg',frame='icrs')
#     time = thetime('2018-4-6 00:00:00')
#     times = time + (n*u.second)
#     lst = kittpeak.local_sidereal_time(times)
#     ha = (lst.hour - (RA/15.0)) # given in hours, converted to degrees later for PA calc
#     frame = AltAz(obstime=times, location=location)
#     new_coord = coord.transform_to(frame)
#     alt = new_coord.alt.degree
#     az  = new_coord.az.degree

#     # parallactic angle calculation -----------------------------------------------------------------------------------
#     sina = np.sin(np.radians(ha*15.0))
#     cosa = (np.tan(np.radians(31.95844))*np.cos(np.radians(DEC)))-(np.sin(np.radians(DEC))*np.cos(np.radians(ha*15.0)))
#     return np.degrees(np.arctan2(sina,cosa)) / 2.0


def victoria_socket():
    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    s.connect((CONTROL_HOST, CONTROL_PORT))
    # s.send('Hello, world')
    data = s.recv(1024)
    s.close()
    print 'Received', repr(data)


if __name__ == "__main__":
    main()