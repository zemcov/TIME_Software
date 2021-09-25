#!/usr/bin/python

import spidev
import sys
import numpy as np

spi = spidev.SpiDev()
spi.open(0,0)
spi.max_speed_hz = 7629

home_pos = 294.5
maximum = home_pos + 42.0
minimum = home_pos - 45.0

def get_pos():
    '''
    Returns the absolute rotational position of the encoder in degrees.  Accurate to about 0.005 degrees
    '''
    data = spi.readbytes(5)
    for i in range(0,5):
        data[i] = bin(data[i])[2:].rjust(8,'0')
    new_data = data[0] + data[1] + data[2] + data[3] + data[4]
    enc_pos = new_data[1:21]
    #print("Encoder position:" , float((360.0/1048575)*int(enc_pos,2))+22.95)
    return float((360.0/1048575)*int(enc_pos,2))

def pa_enc(pa):
    ang = 0.0
    # if np.sign(pa) == -1.0:
    #     ang = abs(pa/2.0) + home_pos
    # else :
    #     ang = -(pa/2.0) + home_pos
    ang = (pa/2.0) + home_pos
    return ang

def enc_pa(enc):
    ang = (enc - home_pos) * 2.0
    return ang


if __name__ == "__main__":
    import time, sys
    while True:
        # print("Encoder Position: ", get_pos(), "degrees")
        sys.stdout.write("Encoder Position: %s degrees\r" % get_pos())
        sys.stdout.flush()
        time.sleep(0.5)
