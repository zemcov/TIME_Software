import RPi.GPIO as GPIO

GPIO.setmode(GPIO.BCM)
GPIO.setwarnings(False)
GPIO.setup([20,21],GPIO.OUT)
GPIO.output(21,GPIO.HIGH)
GPIO.output(20,GPIO.HIGH)
print("KMIRROR STOPPED")
