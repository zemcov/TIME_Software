import RPi.GPIO as GPIO
import time

GPIO.setmode(GPIO.BCM)
GPIO.setwarnings(False)
GPIO.setup([16,20,21],GPIO.OUT)
print('initial 16',GPIO.input(16))

GPIO.output(21,GPIO.HIGH)
GPIO.output(20,GPIO.HIGH)
GPIO.output(16,GPIO.LOW)
time.sleep(2.0)
GPIO.output(21,GPIO.LOW)
GPIO.output(20,GPIO.LOW)
GPIO.output(16,GPIO.HIGH)
print('16',GPIO.input(16))
time.sleep(1.0)
print('final 16',GPIO.input(16))
print('20',GPIO.input(20))
print('21',GPIO.input(21))
print("Success")

# while True :
#
#     try :
#         GPIO.output(21,GPIO.HIGH)
#         print('16',GPIO.input(16))
#         time.sleep(1.0)
#
#     except KeyboardInterrupt :
#         break
