#!/usr/bin/python

import spidev
import time

spi = spidev.SpiDev()
spi.open(0,0)
spi.max_speed_hz = 7629


while True:
    data = spi.readbytes(5)
    for i in range(0,5):
        data[i] = bin(data[i])[2:].rjust(8,'0')
    new_data = data[0] + data[1] + data[2] + data[3] + data[4] 
    enc_pos = new_data[1:21]
    #status = new_data[20:22]
    #detailed_status = new_data[22:31]
    #crc = new_data[33:]
    #print"Raw Data: ", data
    print("Encoder Position: ", float((360.0/1048575)*int(enc_pos,2)), "degrees")
    #print"General Status: ", status
    #print"Detailed Status: ", detailed_status
    #print"CRC: ", crc
    time.sleep(0.5)