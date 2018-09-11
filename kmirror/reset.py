"""
reset.py:
Resets Pi GPIO to initial states.
Run this script if the system crashes.
"""

import RPi.GPIO as GPIO

GPIO.setmode(GPIO.BCM)
GPIO.setwarnings(False)
in_chan_list = [12,13,16,19]
GPIO.setup(in_chan_list, GPIO.IN)
out_chan_list = [20,21]
GPIO.setup(out_chan_list,GPIO.OUT)

GPIO.output(20,GPIO.LOW)
GPIO.output(21,GPIO.HIGH)