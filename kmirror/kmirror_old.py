import socket, threading, sys, binascii, struct, sys, time, math
import numpy as np
import matplotlib.pyplot as plt
import PID
from util import *
from rotate_motor import rotate_motor

'''
Include other 2 use cases in telescope sim
Begin sending out status stuff
Integrate into full program

packet format:
Paralactic Angle (float) | Time packet is sent (double) | Bool Slewing | Bool Observing/Tracking | Bool Staring (sidereal rate)
'''


TELESCOPE_HOST = '129.21.75.185'
TELESCOPE_PORT = 50007
CONTROL_HOST = ''
CONTROL_PORT = 8888

PACKET_FORMAT = 'fd???'
DEG_TO_STEP = 0.36  # 21.6', 1296"
GEAR_RATIO = 160.0
# NUM_SAMPLES = float('inf')
NUM_SAMPLES = 1000
STEP_OFFSET = 30

deg_to_step = lambda degs: float(degs) * GEAR_RATIO / DEG_TO_STEP
step_to_deg = lambda steps: float(steps) / GEAR_RATIO * DEG_TO_STEP


# A class to encapsulate each "update" from the telescope
# for now includes the rotational position, time received, and time sent
class TelescopeUpdate():
    def __init__(self, abs_degree_pos, when_received, when_sent):
        self.abs_degree_pos = abs_degree_pos
        self.when_received = when_received
        self.when_sent = when_sent

    def delta_degs(self, other_update):
        return self.abs_degree_pos - other_update.abs_degree_pos

    def delta_steps(self, other_update):
        return deg_to_step(self.delta_degs(other_update))

    def __str__(self):
        return str(self.abs_degree_pos)
    def __repr__(self):
        return str(self.abs_degree_pos)

'''
def rotate_motor(steps, speed)
'''


class KMirror():
    def __init__(self):
        self.encoder_pos_s = 0.0
        self.calibrated_origin = -135.0
        self.speed = 0
        self.dest_pos = 0
        self.last_time = time.time()
        self.pid = PID.PID(P=17.0, I=11.0, D=0.01)
        self.pid.SetPoint = 0.0
        self.pid.setSampleTime(0.01)
        self.pid.setWindup(150.0)

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
        delta_time = time.time() - self.last_time
        self.last_time += delta_time
        if (self.speed > 0.0 and self.encoder_pos_s < self.dest_pos) \
            or (self.speed < 0.0 and self.encoder_pos_s > self.dest_pos):
            new_pos = self.encoder_pos_s + self.speed * delta_time
            if self.speed > 0.0:
                self.encoder_pos_s = min(new_pos, self.dest_pos)
            else:
                self.encoder_pos_s = max(new_pos, self.dest_pos)

            if self.encoder_pos_s == self.dest_pos:
                print "Motor reached destination and stopped unecessarily!"
        else:
            print "No move command, bad!"


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
            while len(updateList) <= old_len:
                continue
            old_len = len(updateList)

            # NEW UPDATE
            if len(updateList) == 1:
                #first update
                kmirror.encoder_pos_s = deg_to_step(updateList[-1].abs_degree_pos)
            elif len(updateList) >= 2:
                # Kalman stuff
                tele_vel = updateList[-1].abs_degree_pos - updateList[-2].abs_degree_pos
                time_delta = updateList[-1].when_sent - updateList[-2].when_sent
                tele_vel /= time_delta
                # if tele_vel > 100 or tele_vel < -100:
                #     continue
                if (tele_vel > 0 and measured_speed[-1] < 0) or (tele_vel < 0 and measured_speed[-1] > 0):
                    kalman_filter.reset(tele_vel)
                kalman_filter.input_latest_noisy_measurement(tele_vel)
                kalman_speed.append(kalman_filter.get_latest_estimated_measurement())
                measured_speed.append(tele_vel)

                #every subsequent update
                if len(updateList) >= 3:
                    kmirror.update()    # the simulation element
                    update_debugs(debug_vars, kmirror, updateList[-1])
                set_point = deg_to_step(updateList[-1].abs_degree_pos) - kmirror.encoder_pos_s
                if kmirror.speed > 0.0:
                    # steps_to_move = max(1.0, set_point)
                    steps_to_move = math.ceil(set_point) + STEP_OFFSET
                else:
                    # steps_to_move = min(-1.0, set_point)
                    steps_to_move = math.floor(set_point) - STEP_OFFSET
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

        # graph debug stuff
        x_axis = range(len(debug_vars['speed_list']))
        f, axarr = plt.subplots(4, sharex=True)
        axarr[0].plot(x_axis, debug_vars['abs_encoder_degs_list'])
        axarr[0].plot(x_axis, debug_vars['abs_update_degs_list'])
        # axarr[0].plot(x_axis, debug_vars['motor_set_point'])
        axarr[0].set(ylabel='degrees')
        axarr[0].set_title('Absolute Rotational Position')

        axarr[1].plot(x_axis, debug_vars['abs_err_arcsec_list'])
        axarr[1].plot(np.zeros(len(x_axis)))
        axarr[1].set(ylabel='arcsec')
        axarr[1].set_title('Error')
        # axarr[1].grid(True, which='both', axis='y')

        axarr[2].plot(x_axis, debug_vars['speed_list'])
        axarr[2].plot(np.zeros(len(x_axis)))
        # axarr[2].set(ylabel='arcsec/sec')
        axarr[2].set(ylabel='steps/sec')
        axarr[2].set_title('Motor Speed')

        altaxs = axarr[2].twinx()
        # s2 = np.sin(2 * np.pi * t)
        # altaxs.plot(t, s2, 'r.')
        altaxs.plot(x_axis, [deg_to_arcsec(step_to_deg(num)) for num in debug_vars['speed_list']])
        altaxs.set_ylabel('arcsec/sec')#, color='r')
        # altaxs.tick_params('y', colors='r')
        # axarr[2].grid(True, which='both', axis='y')

        del measured_speed[:len(measured_speed)-len(x_axis)]
        del kalman_speed[0]
        axarr[3].plot(x_axis, measured_speed)
        axarr[3].plot(x_axis, kalman_speed)
        axarr[3].set(ylabel='degrees/sec')
        axarr[3].set_title('Kalman Response to Velocity')

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
        s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        s.connect((TELESCOPE_HOST, TELESCOPE_PORT))

        unpacker = struct.Struct(PACKET_FORMAT)

        try:
            while not self.stopped():
               data = s.recv(unpacker.size)
               pa,sent,_,_,_, = unpacker.unpack(data)
               update = TelescopeUpdate(pa/2.0, time.time(), sent)
               self.masterList.append(update)
        except Exception as e:
            print e
            s.close()
            self.stop()


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
    main()