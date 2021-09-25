#!/usr/bin/env python
import numpy as np
import minimalmodbus
import serial
import time
from encoder import get_pos
# -------------------------------------------------------------------

driver = minimalmodbus.Instrument('/dev/ttyUSB0', 1)
driver.serial.baudrate = 9600
driver.serial.parity = serial.PARITY_EVEN
driver.mode = minimalmodbus.MODE_RTU
driver.serial.timeout = 100
# ----------------------------------------------------------------------

def twos_comp(val, bits=16):
    bitstr = "{0:b}".format(abs(val))
    pad = '0' * (16 - len(bitstr))
    bitstr = pad + bitstr
    bitstr = ''.join(['1' if bit == '0' else '0' for bit in bitstr])
    val = int(bitstr, 2) + 1
    return val
# ===========================================================================

def rotate_motor(steps, speed):

    accel = 10000
    decel = 10000
    speed = int(speed)
    steps = int(steps)
            
    if speed >= 0 and steps >= 0:
        print("option 1", steps , speed)
        driver.write_registers(88, [0,0,0,2,0,steps,0,speed,0,accel,0,decel,0,1000,0,1])
    elif speed <= 0 and steps >= 0:
        print("option 2")
        driver.write_registers(88, [0,0,0,2,0,steps,65535,twos_comp(speed),0,accel,0,decel,0,1000,0,1])
    elif speed >= 0 and steps < 0:
        print("option 3", steps, speed)
        driver.write_registers(88, [0,0,0,2,65535,twos_comp(steps),0,speed,0,accel,0,decel,0,1000,0,1])
    else:
        print("option 4")
        driver.write_registers(88, [0,0,0,2,65535,twos_comp(steps),65535,twos_comp(speed),0,accel,0,decel,0,1000,0,1])
        
    
# ====================================================================================================================
if __name__ == "__main__":
    #twos_comp(-14, 16)
    #rotate_motor(47, -357)
    rotate_motor(10000, 1000)