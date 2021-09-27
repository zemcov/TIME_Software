"""
safety.py:
Integration of the safety subsystem into the K-Mirror.

Using information from
https://sourceforge.net/p/raspberry-gpio-python/wiki/Examples/
https://www.tutorialspoint.com/python/python_multithreading.htm
"""

from __future__ import print_function
import time
from datetime import datetime      #REMOVE
import threading
import RPi.GPIO as GPIO
import numpy as np

"""
***Inputs:***
12: Reverse limit switch
13: Forward limit switch
16: E-stop (inverted)

***Outputs:***
20: Pi reset success
21: Activates Contactor for Limit Switch
"""

booted = False

class Checker(threading.Thread):
    """
    The class that defines safety checking
    """
    def __init__(self, reset_mode = 0):
        threading.Thread.__init__(self)
        self.operating = True
        self.in_chan_list = [12,13,16]
        self.out_chan_list = [20,21]
        self.reset_mode = reset_mode

    def boot(self, reset_mode = 0):
        print("Starting safety boot sequence")
        GPIO.setmode(GPIO.BCM)
        GPIO.setwarnings(False)
        GPIO.setup(self.in_chan_list, GPIO.IN)
        GPIO.setup(self.out_chan_list,GPIO.OUT)
        self.reset_mode = reset_mode
        ''' reset_mode: 0=all fine, 1=emergency stop, 2=reverse limit, 3=forward limit '''
        self.enable_motor()
        print("SICK coming online")
        time.sleep(1.0)
        dots=1
        while GPIO.input(16) == GPIO.LOW:
            print("."*dots, end="\r")
            dots +=1
            if dots == 11:
                dots = 1
            time.sleep(.4)
        print("Safety system initialized!")
        booted=True

    def run(self):
        bad_counter = [0,0,0] #corresponds to 12, 13, and 16, respectively
        while self.operating:
            for ch in self.in_chan_list:
                if GPIO.input(ch) == GPIO.LOW:
                    if ch == 12:
                        bad_counter[0]=0
                    if ch == 13:
                        bad_counter[1]=0
                    if ch==16:
                        bad_counter[2] += bad_counter[2]
                        if(bad_counter[2]>4):
                            print("16 has been triggered")
                            self.reset_mode = 1
                            break
                elif GPIO.input(ch) == GPIO.HIGH:
                    if ch == 12:
                        bad_counter[0] += bad_counter[0]
                        if(bad_counter[0]>4):
                            self.reset_mode = 2
                            break
                    elif ch == 13:
                        bad_counter[1] += bad_counter[1]
                        if(bad_counter[1]>4):
                            self.reset_mode = 3
                            break
                    elif ch == 16:
                        bad_counter[2]=0

                else:
                    print("Hmmmm..")
            if self.reset_mode != 0:
                print("Entering an emergency state. Please do not attempt to reset yet.")
                if self.reset_mode == 1:
                    print("ATTEMPTING TO RESET... STANDBY")
                    reset_mode=0
                elif self.reset_mode == 2 or self.reset_mode == 3:
                    time.sleep(1.0)
                    reset_mode=0
            time.sleep(0.01)           #Operates 2 times as fast as the 20Hz at which signals are sent to the motor controller

    def stop(self):
        self.operating = False

##    def is_high(self, pin):
##        if GPIO.input(pin) == GPIO.LOW:
##            return False
##        count=0
##        for i in range(4):
##            if GPIO.input(pin) == GPIO.HIGH :
##                count += 1
##            time.sleep(0.01)
##        if count == 4:
##            return True
##        else:
##            return False
##
##    def is_low(self, pin):
##        if GPIO.input(pin) == GPIO.HIGH:
##            return False
##        count=0
##        for i in range(4):
##            if GPIO.input(pin) == GPIO.LOW :
##                count += 1
##                time.sleep(0.01)
##        if count == 4:
##            return True
##        else:
##            return False

    def stop_motor(self):
        """
        Triggers Deactivate Signal
        """
        GPIO.output(21,GPIO.HIGH)
        print("Motor Deactivated")

    def enable_motor(self):
        """
        Undoes the effects of stop_motor
        """
        GPIO.output(21,GPIO.LOW)
        #print("Motor enabled")


    def stop(self):
        self.operating=False



class Reset(threading.Thread):
    """
    Does reset stuff
    """

    def __init__(self):
        threading.Thread.__init__(self)
        GPIO.setup(20,GPIO.OUT)
        GPIO.setup(21,GPIO.OUT)

    def e_reset(self):
        """
        Tells the SICK that the positional reset was successful
        """
        GPIO.output(20,GPIO.HIGH)
        time.sleep(1.0)
        GPIO.output(20,GPIO.LOW)
        GPIO.output(21,GPIO.LOW)
        time.sleep(1.0)
        print("PLEASE PUSH FLASHING RESET BUTTON TO PROCEED...")

    def limit_reset(self):
        GPIO.output(21,GPIO.LOW)
        time.sleep(1.0)
        print("Motor enabled")
