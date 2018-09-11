#!/usr/bin/python

import spidev

spi = spidev.SpiDev()
spi.open(0,0)
spi.max_speed_hz = 7629


max_pos = -45.0
min_pos = -135.0
home_pos = -50.1

def get_pos():
    '''
    Returns the absolute rotational position of the encoder in degrees.  Accurate to about 0.005 degrees
    '''
    data = spi.readbytes(5)
    for i in range(0,5):
        data[i] = bin(data[i])[2:].rjust(8,'0')
    new_data = data[0] + data[1] + data[2] + data[3] + data[4] 
    enc_pos = new_data[1:21]
    return float((360.0/1048575)*int(enc_pos,2))


if __name__ == "__main__":
    import time, sys
    while True:
        # print("Encoder Position: ", get_pos(), "degrees")
        sys.stdout.write("Encoder Position: %s degrees                       \r" % get_pos())
        sys.stdout.flush()
        time.sleep(0.5)