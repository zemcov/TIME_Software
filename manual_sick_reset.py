import RPi.GPIO as GPIO
import time

GPIO.setmode(GPIO.BCM)
GPIO.setwarnings(False)
GPIO.setup([20,21],GPIO.OUT)
GPIO.output(21,GPIO.HIGH)
GPIO.output(20,GPIO.HIGH)
time.sleep(2.0)
GPIO.output(21,GPIO.LOW)
GPIO.output(20,GPIO.LOW)
time.sleep(1.0)
print("Success")

