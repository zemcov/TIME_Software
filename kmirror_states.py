
"""
kmirror_states.py
Define all the State classes of the K-Mirror.
"""

"""
Code implemented from
https://dev.to/karn/building-a-simple-state-machine-in-python
"""

from state import *
import RPi.GPIO as GPIO
from safety import *
from encoder import get_pos, home_pos, minimum, maximum, pa_enc
from util import *
from rotate_motor import rotate_motor, twos_comp
import sys, subprocess
import socket, threading, sys, binascii, struct, sys, time, math, pickle
import numpy as np
import PID
import multiprocessing as mp
from multiprocessing import Manager
import matplotlib
matplotlib.use('TkAgg')
import matplotlib.pyplot as plt

TELESCOPE_HOST = '0.0.0.0'
TELESCOPE_PORT = 8888
CONTROL_HOST = '192.168.0.101'
CONTROL_PORT = 8500

NUM_SAMPLES = 800
STEP_OFFSET = 150
DEMO = False

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
#=====================================================================================
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
# =====================================================================================
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
            # -------------------------------------------------------------------------------
            if abs(self.speed) > 1000 :
                print("Slowing Down Motor")
                rotate_motor(steps,1000)
            else :
                rotate_motor(steps, abs(self.speed))

            # --------------------------------------------------------------------------------
        else:
            self.speed = 0.0

    def update(self):
        self.encoder_pos_s = deg_to_step(get_pos())
# ===================================================================
class Stop_Checker():
    """
    Checks for E-stop Signals
    """
    def __init__(self):
        GPIO.setmode(GPIO.BCM)
        GPIO.setwarnings(False)
        GPIO.setup([12,13,16],GPIO.IN)
        print("Stop Checker Initialized")
        self.thread1Stop = mp.Event()

###############################################################################################################
    def limits(self,flag):
        print("Limit Checker Initialized")
        while not self.thread1Stop.is_set():
            if get_pos() > minimum and get_pos() < maximum :
                continue
            else :
                if flag == 'good' :
                    print("software limit hit")
                    safety_checker = Checker()
                    safety_checker.stop_motor()
                    safety_checker.stop()
                    break
                else :
                    pass
##########################################################################################################
    def stop_check(self):
        sample1 = [0.0] * 100
        sample2 = [0.0] * 100
        sample3 = [0.0] * 50
        a = 0.0
        b = 0.0
        c = 0.0
        while True:
            if not self.thread1Stop.is_set():
                if GPIO.input(16) == GPIO.HIGH :
                    a = 0.0
                else :
                    a = 1.0
                sample1.pop(0)
                sample1.append(a)
                if GPIO.input(12) == GPIO.LOW :
                    b = 0.0
                else :
                    b = 1.0
                sample2.pop(0)
                sample2.append(b)
                if GPIO.input(13) == GPIO.LOW :
                    c = 0.0
                else :
                    c = 1.0
                sample3.pop(0)
                sample3.append(c)
                if np.mean(sample1) > 0.5 or np.mean(sample2) > 0.5 or np.mean(sample3) > 0.5:
		    self.thread1Stop.set()
                    EmergencyStop()
            else :
                break
##################################################################################################################################
    def go_to(self,angle):
        while not self.thread1Stop.is_set() :
            if get_pos() < (angle - 0.1) or get_pos() > (angle + 0.1) :
                steps = deg_to_step(angle) - deg_to_step(get_pos())
                rotate_motor(int(steps), 1000)
                time.sleep(abs(steps)/2000.0 + 0.1)
            else :
                break
        self.thread1Stop.set()
        return
########################################################################################################################################
    def home_motor(self,arg):
        while get_pos() < (home_pos - 0.1) or get_pos() > (home_pos + 0.1):
            if not self.thread1Stop.is_set() :
                steps = deg_to_step(home_pos) - deg_to_step(get_pos())
                rotate_motor(int(steps), 1000)
                time.sleep(abs(steps)/2000.0 + 0.1)
            else :
                break
        self.thread1Stop.set()
        return
###################################################################################################################################
    def track(self):
        print("tracking is starting")
        # main data structure between threads for telescope updates

        measured_speed = [0.0]
        kalman_speed = []
        process_variance = 5e-3
        estimated_measurement_variance = 1
        kalman_filter = KalmanFilter(process_variance, estimated_measurement_variance)
        kmirror = KMirror()

        debug_vars = {
        'abs_update_degs_list': [],
        'abs_encoder_degs_list': [],
        'abs_err_arcsec_list': [],
        'speed_list': [],
        'motor_set_point': [],
        }

        try:
            old_len = len(self.masterlist)
            while not self.thread1Stop.is_set():
            # ===================================== TRACKING ALGORITHM MAIN LOOP =====================================
                # Wait for a new update to come in
                while len(self.masterlist) <= old_len:
                    time.sleep(0.02)
		        #print("updating...")
                old_len = len(self.masterlist)

                # NEW UPDATE
                if len(self.masterlist) == 1:
                    #first update
                    kmirror.update()
                elif len(self.masterlist) >= 2:
                    tele_vel = self.masterlist[-1].abs_degree_pos - self.masterlist[-2].abs_degree_pos
                    time_delta = self.masterlist[-1].when_sent - self.masterlist[-2].when_sent
                    if time_delta == 0.0 :
		    	        tele_vel /= 0.1

                    if (tele_vel > 0 and measured_speed[-1] < 0) or (tele_vel < 0 and measured_speed[-1] > 0) or \
                        self.masterlist[-1].flag != self.masterlist[-2].flag:
                        kalman_filter.reset(tele_vel)
                    kalman_filter.input_latest_noisy_measurement(tele_vel)
                    kalman_speed.append(kalman_filter.get_latest_estimated_measurement())
                    measured_speed.append(tele_vel)

                    if len(self.masterlist) >= 3:
                        kmirror.update()
                        ''' debug stuff '''
                        self.update_debugs(debug_vars, kmirror, self.masterlist[-1])
                    encoder_pos_d = step_to_deg(kmirror.encoder_pos_s)
                    set_point = deg_to_step(ang_subtract(self.masterlist[-1].abs_degree_pos, encoder_pos_d))
                    set_point *= ang_subtract_sign(self.masterlist[-1].abs_degree_pos, encoder_pos_d)
                    steps_to_move = int(set_point) + STEP_OFFSET * sign(kmirror.speed)
                    kmirror.move_cmd(steps_to_move, set_point, kalman_speed[-1])
                ''' debug stuff '''
                if len(debug_vars['speed_list']) >= NUM_SAMPLES:
                    self.thread1Stop.set()
        except KeyboardInterrupt():
            self.thread1Stop.set()
            print("Tracking has stopped")
        finally:
            # ====================================== OPTIONAL CODE FOR DEBUGGING ======================================
            errors = np.array(debug_vars['abs_err_arcsec_list'])
            errors = np.absolute(errors)
            print "Average error (arcsec): {:3.3f}".format(np.mean(errors))

            x_axis = range(len(debug_vars['speed_list']))
            packet_lag = [(update.when_received - update.when_sent)*1000.0 for update in self.masterlist[:len(x_axis)]]
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

            del measured_speed[:2]
            del kalman_speed[0]
            if len(measured_speed) > len(x_axis):
                axarr2[0].plot(x_axis, measured_speed[:len(x_axis)])
            else:
                axarr2[0].plot(x_axis[:len(measured_speed)], measured_speed)
            axarr2[0].plot(x_axis, kalman_speed[:len(x_axis)])
            axarr2[0].set(ylabel='degrees/sec')
            axarr2[0].set_title('Kalman Response to Velocity')

            axarr2[1].plot(x_axis, packet_lag)
            axarr2[1].plot(np.zeros(len(x_axis)))
            axarr2[1].set(ylabel='ms')
            axarr2[1].set_title('Packet lag')
            plt.show()

            # ========================================================================================================
    def update_debugs(self,debug_vars, kmirror, last_update):
        error_s = deg_to_step(last_update.abs_degree_pos) - kmirror.encoder_pos_s
        error_arcsec = deg_to_arcsec(step_to_deg(error_s))
        #print "Error (steps, arcsec): {:3.3f}, {:3.3f}".format(error_s, error_arcsec)
        debug_vars['abs_update_degs_list'].append(last_update.abs_degree_pos)
        debug_vars['abs_encoder_degs_list'].append(step_to_deg(kmirror.encoder_pos_s))
        debug_vars['speed_list'].append(kmirror.speed)
        debug_vars['abs_err_arcsec_list'].append(error_arcsec)
        debug_vars['motor_set_point'].append(step_to_deg(kmirror.dest_pos))
##################################################################################################################################
    def run(self):
        print("run is starting")
##        if DEMO:
##            with open('pa.txt', 'r') as f:
##                for line in f.readlines():
##                    if not self.thread1Stop.is_set():
##                        pa, flag = line.strip().split(',')
##                        update = TelescopeUpdate(pa_enc(float(pa)), time.time(), time.time(), bool(flag))
##                        self.masterlist.append(update)
##                        # print float(pa)/2.0
##                        time.sleep(1.0/20.0)
##                    else:
##                        break
##                self.thread1Stop.set()
##        else:
        s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        s.bind((TELESCOPE_HOST,TELESCOPE_PORT))
        s.listen(1)
        print('listening for connection')
        unpacker = struct.Struct('d i')
        while not self.thread1Stop.is_set():
            pa_file = open('pa.txt','w')
            pa_file.close()
            pa_file = open('pa.txt', 'a')
            connection = None
            connection,client= s.accept()
            print('Socket connected')
            try:
                while not self.thread1Stop.is_set():
                    data = connection.recv(unpacker.size)
                    pa,flag = unpacker.unpack(data)
                    update = TelescopeUpdate(pa_enc(float(pa)), time.time(), time.time(), flag)
                    self.masterlist.append(update)
                    pa_file.writelines([str(pa) + ' , ',str((get_pos() - home_pos)/2.0) + '\n'])
                    # self.pa = pa
                    # self.slew_flag = flag
            except KeyboardInterrupt:
                if connection :
                    connection.close()
                pa_file.close()
                self.thread1Stop.set()

        s.close()
################################################################################################################################
    def step_overload(self,num_steps) :
        steps = num_steps
        for i in range(int(num_steps)//100) :
            if not self.thread1Stop.is_set():
                if steps >= 100 :
                    rotate_motor(100, 2000)
                    time.sleep(0.1)
                    #time.sleep(abs(100)/2000.0 + 0.1)
                    steps = steps - 100
                else :
                    rotate_motor(steps, 2000)
                    time.sleep(0.1)
                    #time.sleep(abs(100)/2000.0 + 0.1)
                    steps = 0
            else :
                break
        self.thread1Stop.set()
#########################################################################
    # def vic_socket(self):
    #     s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    #     s.connect((CONTROL_HOST, CONTROL_PORT))
    #     packer = packer = struct.Struct('d d d i')
    #     while not self.thread1Stop.is_set():
    #         try:
    #             data = packer.pack(float(self.pa.value),float(pa_enc(get_pos())),float(time.time()),int(self.slew_flag.value))
    #             s.send(data)
    #             time.sleep(0.05)
    #             print 'PA Sent to Gui',time.time()
    #         except KeyboardInterrupt:
    #             self.thread1stop.set()
    #     s.close()
    #     print 'vic_socket closed'

###############################################################################################################################
    def main(self,arg1,arg2,arg3):
        self.masterlist = Manager().list()
        self.pa = Manager().Value('d',0.0)
        self.slew_flag = Manager().Value('i',0)
        if arg1 == 'go_to':
            t1 = mp.Process(target=self.go_to,args = (arg2,))
            t2 = mp.Process(target=self.limits,args = (arg3,))
            t1.start()
            t2.start()
        elif arg1 == 'home_motor' :
            t1 = mp.Process(target=self.home_motor,args = (arg2,))
            t2 = mp.Process(target=self.limits,args=(arg3,))
            t1.start()
            t2.start()
        else :
            t1 = mp.Process(target=self.limits,args=(arg3,))
            t2 = mp.Process(target=self.run)
            t3 = mp.Process(target=self.track)
            # t4 = mp.Process(target=self.vic_socket)
            t1.start()
            t2.start()
            t3.start()
            # t4.start()
        self.stop_check()

# ====================================================================================================
# Start of our states.
class Home(State):
    """
    The state which indicates that the K-Mirror is home.
    """

    def __init__(self,verified=0):
        """
        Initialize Home state.
        """
        super(Home, self).__init__(verified)
        # Other Home tasks should be listed in this function.

    def on_event(self, event):
        """
        Process event action.
        """
        if event == 'turn_on':
            return Ready(self.verified)
        if event == 'error':
            return EmergencyStop()
        return self

    def events(self):
        """
        Give string list of applicable events for current state.
        """
        return ['turn_on', 'error']

class Ready(State):
    """
    The state which indicates that the K-Mirror is ready.
    """

    def __init__(self, verified):
        """
        Initialize Ready state.
        """
        super(Ready, self).__init__(verified)
        # Other Ready tasks should be listed in this function.


    def on_event(self, event):
        """
        Process event action.
        """
        if event == 'go_home':
            return Verification()
        if event == 'start_tracking':
            if self.verified == 1:
                return Tracking(self.verified)
            print 'Error: K-Mirror must be verified to start tracking'
        if event == 'verify':
            return Home()
        if event == 'error':
            return EmergencyStop()
        if event == 'go_to_pos':
            if get_pos() > minimum and get_pos() < maximum :
                flag = 'good'
            else :
                flag = 'bad'
            angle = raw_input("Enter position to move to (KMS Coord): \n")
            problem = False
            print("Moving to Position")
            sc = Stop_Checker()
            sc.main("go_to",float(angle) + 293.65,flag)
        return self

    def events(self):
        """
        Give string list of applicable events for current state.
        """
        return ['verify', 'start_tracking', 'go_home', 'error','go_to_pos']


class EmergencyStop(State):
    """
    The state which indicates that the K-Mirror has initiated an Emergency
    Stop.
    """

    def __init__(self, verified=0,):
        """
        Initialize EmergencyStop state.
        """
        super(EmergencyStop, self).__init__(verified)
	# Other EmergencyStop tasks should be listed in this function.
        rotate_motor(1,100)
        safety_checker = Checker()
        safety_checker.stop_motor()
        safety_checker.stop()

    def on_event(self, event):
        """
        Process event action.
        """
##        if event == 'turn_on':
##            #reactivates the contactor
##            res = Reset()
##            res.start()
##            return Ready(self.verified)
        if event == 'e_reset':
            res = Reset()
            res.e_reset()
            return Home()
        if event == 'limit_reset':
            res = Reset()
            res.limit_reset()
            return Home()
        return self

    def events(self):
        """
        Give string list of applicable events for current state.
        """
        return ['e_reset','limit_reset']

class Verification(State):
    """
    The state which indicates that the K-Mirror is verifying its functionality
    and going to a set position.
    """

    def __init__(self, verified=1):
        """
        Initialize Verification state.
        """
        super(Verification, self).__init__(verified)
        if get_pos() > minimum and get_pos() < maximum :
            flag = 'good'
        else :
            flag = 'bad'
        print("Homing Motor")
        sc = Stop_Checker()
        sc.main('home_motor','crap',flag)

        self.auto_next_event = 'finished_verifying'

    def on_event(self, event):
        """
        Process event action.
        """
        if event == 'finished_verifying':
            return Ready(self.verified)
        if event == 'error':
            return EmergencyStop()
        return self

    def events(self):
        """
        Give string list of applicable events for current state.
        """
        return ['finished_verifying', 'error']

class Tracking(State):
    """
    The state which indicates that the K-Mirror is in Tracking mode.
    """

    def __init__(self, verified):
        """
        Initialize Tracking state.
        """
        super(Tracking, self).__init__(verified)
        # Other Tracking tasks should be listed in this function.
        sc = Stop_Checker()
        sc.main("tracking",'crap','good')
        self.auto_next_event = 'end_tracking'

    def on_event(self, event):
        """
        Process event action.
        """
        if event == 'end_tracking':
            return Ready(self.verified)
        if event == 'error':
            return EmergencyStop()
##        if safety.get_state[2]:
##            return EmergencyStop()
        return self

    def events(self):
        """
        Give string list of applicable events for current state.
        """
        return ['end_tracking', 'error']
# End of states.
