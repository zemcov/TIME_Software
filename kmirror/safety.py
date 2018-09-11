"""
safety.py:
Integration of the safety subsystem into the K-Mirror.

Using information from
https://sourceforge.net/p/raspberry-gpio-python/wiki/Examples/
https://www.tutorialspoint.com/python/python_multithreading.htm
"""

from __future__ import print_function
import time
import threading
import RPi.GPIO as GPIO
from settings import *
from kmirror_states import EmergencyStop

"""
***Inputs:***
12: Reverse limit switch
13: Forward limit switch
16: E-stop
19: SICK Reset Success (Always on except when stopped)

***Outputs:***
20: Pi reset success
21: Activates contactor
"""

booted = False

class Checker(threading.Thread):
    """
    The class that defines safety checking
    """
    def __init__(self, reset_mode=0):
        threading.Thread.__init__(self)
        print("Starting safety boot sequence")
        GPIO.setmode(GPIO.BCM)
        GPIO.setwarnings(False)
        self.in_chan_list = [12,13,16,19]
        GPIO.setup(self.in_chan_list, GPIO.IN)
        self.out_chan_list = [20,21]
        GPIO.setup(self.out_chan_list,GPIO.OUT)
        self.operating = True
        self.reset_mode = reset_mode
        #reset_mode: 0=all fine, 1=emergency stop, 2=reverse limit, 3=forward limit
        self.enable_motor()
        print("SICK coming online")
        dots=1
        while GPIO.input(19) == GPIO.LOW:
            print("."*dots, end="\r")
            dots +=1
            if dots == 11:
                dots = 1
            time.sleep(1)
        print("Safety system initialized!")
        booted=True
    
    def run(self):
        while self.operating:
            for ch in self.in_chan_list:
                if GPIO.input(ch) == GPIO.LOW:
                    if ch==19:
                        print("19 bad")
                        self.reset_mode = 1
                        break
                    elif ch == 16:
                        print("16 bad")
                        self.reset_mode = 1
                        break
                elif GPIO.input(ch) == GPIO.HIGH:
                    operating = False
                    if ch == 12:
                        print("12 bad")
                        self.reset_mode = 2
                        break
                    elif ch == 13:
                        print("13 bad")
                        self.reset_mode = 3
                        break
                    elif ch == 19:
                        print("19 good")
                        self.enable_motor()
                        self.reset_mode = 0
                else:
                    print("Hmmmm..")
            if self.reset_mode != 0:
                print("Entering an emergency state. Please do not attempt to reset yet.")
                if self.reset_mode == 1:
                    self.stop_motor()
                    res = Reset()
                    res.start()
                    reset_mode=0
                elif self.reset_mode == 2 or self.reset_mode == 3:
                    home = self.home_motor()
                    reset_mode=0
                    if not home:
                        self.stop_motor()
                        res = Reset()
                        res.start()
                        reset_mode=0
                d = set_device(self,EmergencyStop())
            
            time.sleep(0.01)           #Operates 5 times as fast as the 20Hz at which signals are sent to the motor controller
        
    
    def stop_motor(self):
        """
        Opens contactor and brakes motor
        """
        GPIO.output(21,GPIO.LOW)
        print("Motor stopping")
        
    def enable_motor(self):
        """
        Undoes the effects of stop_motor
        """
        GPIO.output(21,GPIO.HIGH)
        print("Motor enabled")
    
    def home_motor(self):
        from rotate_motor import rotate_motor
        from encoder import get_pos, home_pos
        from util import deg_to_step
        import time
        
        while get_pos() < home_pos - 0.1 or get_pos() > home_pos + 0.1:
            steps = deg_to_step(home_pos) - deg_to_step(get_pos())
            rotate_motor(int(steps), 2000)
            if GPIO.input(12) == GPIO.HIGH or GPIO.input(13) == GPIO.HIGH or GPIO.input(16) == GPIO.HIGH:
                return False
            time.sleep(abs(steps)/2000.0 + 0.1)
        print(get_pos())
        return True
    
    def stop(self):
        self.operating=False



class Reset(threading.Thread):
    """
    Does reset stuff
    """
    
    def __init__(self):
        threading.Thread.__init__(self)
        GPIO.setup(20,GPIO.OUT)
    
    def run(self):
        self.confirm_reset()
    
    def confirm_reset(self):
        """
        Tells the SICK that the positional reset was successful
        """
        GPIO.output(20,GPIO.HIGH)
        time.sleep(.2)
        GPIO.output(20,GPIO.LOW)
        print("Ready for system reset.")
    
