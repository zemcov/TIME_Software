#!/usr/bin/env python
import minimalmodbus
import serial
import time

driver = minimalmodbus.Instrument('/dev/ttyUSB0', 1)
driver.serial.baudrate = 9600
driver.serial.parity = serial.PARITY_EVEN
driver.mode = minimalmodbus.MODE_RTU
driver.serial.timeout = 100

steps = 50000
speed = 500
accel = 10000
decel = 10000

driver.write_registers(88, [0,0,0,2,0,steps,0,speed,0,accel,0,decel,0,1000,0,1])

time.sleep(1)
speed = 2000
print(speed)
driver.write_registers(88, [0,0,0,2,0,steps,0,speed,0,accel,0,decel,0,1000,0,1])


time.sleep(1)
speed = 3000
print(speed)
driver.write_registers(88, [0,0,0,2,0,steps,0,speed,0,accel,0,decel,0,1000,0,1])


time.sleep(1)
speed = 6000
print(speed)
driver.write_registers(88, [0,0,0,2,0,steps,0,speed,0,accel,0,decel,0,1000,0,1])#driver.write_register(125,0, 0, 6 )

#driver.write_register(1153,1000, 0, 6 )
#driver.write_register(6147,1000, 0, 6 )

#driver.write_register(125,16384, 0, 6 )
#driver.write_register(125,0, 0, 6 )

#driver.write_register(6149,5000, 0, 6 )
#driver.write_register(6147,1000, 0, 6 )

#driver.write_register(125,8, 0, 6 )
#driver.write_register(125,0, 0, 6 )

"""value = driver.read_register(125, 0 , 3)
value1 = driver.read_register(6149, 0, 3)
value2 = driver.read_register(6147, 0, 3)

print value1
print value
print value2"""
