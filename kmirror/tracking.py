import socket, threading, sys, binascii, struct, sys, time, math, pickle
import numpy as np
import matplotlib
matplotlib.use('TkAgg')
import matplotlib.pyplot as plt

import PID
from util import *
from rotate_motor import rotate_motor
from encoder import get_pos


TELESCOPE_HOST = '129.21.74.200'
TELESCOPE_PORT = 50008
CONTROL_HOST = ''
CONTROL_PORT = 8888

NUM_SAMPLES = 800
STEP_OFFSET = 150
DEMO = True


class KMirror():
    def __init__(self):
        self.encoder_pos_s = 0.0
        self.speed = 0
        self.dest_pos = 0
        self.last_time = time.time()
        self.pid = PID.PID(P=7.5, I=2.5, D=0.1)
        self.pid.SetPoint = 0.0
        self.pid.setSampleTime(0.01)
        self.pid.setWindup(250.0)

    def move_cmd(self, steps, set_point, vel_est):#, speed):
        self.dest_pos = self.encoder_pos_s + steps
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


class TrackingAlgorithm():
    def __init__(self):
        pass

    def track(self):
        # main data structure between threads for telescope updates
        updateList = []

        tele_thread = TelescopeThread(updateList)
        tele_thread.start()
        # un-comment when we start communcating with Victoria's control computer
        # ctrl_thread = threading.Thread(target=victoria_socket)
        # ctrl_thread.start()

        # This data structure is just for debugging.  It basically holds all the data that eventually
        # gets displayed as plots
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
        kmirror = KMirror()

        try:
            # ===================================== TRACKING ALGORITHM MAIN LOOP =====================================
            old_len = len(updateList)
            while 1:
                # Wait for a new update to come in
                while len(updateList) <= old_len:
                    time.sleep(0.02)
                old_len = len(updateList)

                # NEW UPDATE
                if len(updateList) == 1:
                    #first update
                    kmirror.update()
                elif len(updateList) >= 2:
                    tele_vel = updateList[-1].abs_degree_pos - updateList[-2].abs_degree_pos
                    time_delta = updateList[-1].when_sent - updateList[-2].when_sent
                    tele_vel /= time_delta
                    if (tele_vel > 0 and measured_speed[-1] < 0) or (tele_vel < 0 and measured_speed[-1] > 0) or \
                        updateList[-1].flag != updateList[-2].flag:
                        kalman_filter.reset(tele_vel)
                    kalman_filter.input_latest_noisy_measurement(tele_vel)
                    kalman_speed.append(kalman_filter.get_latest_estimated_measurement())
                    measured_speed.append(tele_vel)

                    if len(updateList) >= 3:
                        kmirror.update()
                        update_debugs(debug_vars, kmirror, updateList[-1])
                    encoder_pos_d = step_to_deg(kmirror.encoder_pos_s)
                    set_point = deg_to_step(ang_subtract(updateList[-1].abs_degree_pos, encoder_pos_d))
                    set_point *= ang_subtract_sign(updateList[-1].abs_degree_pos, encoder_pos_d)
                    steps_to_move = int(set_point) + STEP_OFFSET * sign(kmirror.speed)
                    kmirror.move_cmd(steps_to_move, set_point, kalman_speed[-1])

                if len(debug_vars['speed_list']) >= NUM_SAMPLES:
                    break
            # ========================================================================================================
        except KeyboardInterrupt:
            pass
        finally:
            tele_thread.stop()

            # ====================================== OPTIONAL CODE FOR DEBUGGING ======================================
            errors = np.array(debug_vars['abs_err_arcsec_list'])
            errors = np.absolute(errors)
            print "Average error (arcsec): {:3.3f}".format(np.mean(errors))

            x_axis = range(len(debug_vars['speed_list']))
            packet_lag = [(update.when_received - update.when_sent)*1000.0 for update in updateList[:len(x_axis)]]
            print "Average Packet Lag (ms): {:3.3f}".format(np.mean(np.absolute(np.array(packet_lag))))
            print "Std Packet Lag (ms): {:3.3f}".format(np.std(np.absolute(np.array(packet_lag))))

            # attempt to clean encoder signal
            avg_encoder = np.mean(np.absolute(np.array(debug_vars['abs_encoder_degs_list'])))
            encoder_signal = [val if abs(val) < avg_encoder * 10 else avg_encoder for val in debug_vars['abs_encoder_degs_list']]
            print "Deleted %s outlier values" % np.sum(np.array([0 if abs(val) < avg_encoder * 10 else 1 for val in debug_vars['abs_encoder_degs_list']]))

            # graph debug stuff
            f, axarr = plt.subplots(3, sharex=True)

            line, = axarr[0].plot(x_axis, encoder_signal)
            line, = axarr[0].plot(x_axis, debug_vars['abs_update_degs_list'])
            axarr[0].set(ylabel='degrees')
            axarr[0].set_title('Absolute Rotational Position')

            line, = axarr[1].plot(x_axis, debug_vars['abs_err_arcsec_list'])
            line, = axarr[1].plot(np.zeros(len(x_axis)))
            axarr[1].set(ylabel='arcsec')
            axarr[1].set_title('Error')

            line, = axarr[2].plot(x_axis, debug_vars['speed_list'])
            line, = axarr[2].plot(np.zeros(len(x_axis)))
            axarr[2].set(ylabel='steps/sec')
            axarr[2].set_title('Motor Speed')

            f2, axarr2 = plt.subplots(2, sharex=True)
            plt.subplots_adjust(left=.04, right=.95, bottom=.04, top=.95, wspace=.20, hspace=.20)
            try:
                del measured_speed[:2]
                del kalman_speed[0]
                if len(measured_speed) > len(x_axis):
                    axarr2[0].plot(x_axis, measured_speed[:len(x_axis)])
                else:
                    axarr2[0].plot(x_axis[:len(measured_speed)], measured_speed)
                axarr2[0].plot(x_axis, kalman_speed[:len(x_axis)])
                axarr2[0].set(ylabel='degrees/sec')
                axarr2[0].set_title('Kalman Response to Velocity')
            except Exception as e:
                print e

            axarr2[1].plot(x_axis, packet_lag)
            axarr2[1].plot(np.zeros(len(x_axis)))
            axarr2[1].set(ylabel='ms')
            axarr2[1].set_title('Packet lag')
            plt.show()
            # ========================================================================================================


def update_debugs(debug_vars, kmirror, last_update):
    error_s = deg_to_step(last_update.abs_degree_pos) - kmirror.encoder_pos_s
    error_arcsec = deg_to_arcsec(step_to_deg(error_s))
    print "Error (steps, arcsec): {:3.3f}, {:3.3f}".format(error_s, error_arcsec)
    debug_vars['abs_update_degs_list'].append(last_update.abs_degree_pos)
    debug_vars['abs_encoder_degs_list'].append(step_to_deg(kmirror.encoder_pos_s))
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


def victoria_socket():
    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    s.connect((CONTROL_HOST, CONTROL_PORT))
    # s.send('Hello, world')
    data = s.recv(1024)
    s.close()
    print 'Received', repr(data)


if __name__ == "__main__":
    tracker = TrackingAlgorithm()
    tracker.track()