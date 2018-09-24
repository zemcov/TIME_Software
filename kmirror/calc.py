import time
import serial
import threading

import RPi.GPIO as GPIO

def enable_out():
    
    if GPIO.input(13) == 0:
        GPIO.output(36, GPIO.HIGH)
        time.sleep(0.001)
        GPIO.output(36, GPIO.LOW)
        

def crc16_calc(lst_bytes):
    """

    :param lst_bytes: list of bytes in the message sent
    :return: the Modbus CRC16 checksum
    """

    crc = 0xFFFF

    for byte in lst_bytes:
        crc = crc ^ byte

        for i in range(0, 8):
            if crc & 0x0001 != 0:
                crc >>= 1
                crc = crc ^ 0xA001
            else:
                crc = crc >> 1
    return crc

def reverse_bits(num):
    value = int(num, 16)
    #value = int('{:08b}'.format(value)[::-1], 2)
    
    return value
    

ser = serial.Serial(
    port='/dev/ttyUSB3',
    baudrate=9600,
    parity=serial.PARITY_EVEN,
    stopbits=serial.STOPBITS_ONE,
    bytesize=serial.EIGHTBITS,
    timeout=1
)

GPIO.setmode(GPIO.BOARD)
GPIO.setup(13, GPIO.IN)
GPIO.setup(36, GPIO.OUT, initial=GPIO.LOW)

crc = crc16_calc([0x00, 0x06, 0x02, 0x55, 0x00, 0x50])
#print(crc)
#ser.write(bytearray([0xFF, 0x10, 0x18, 0x02, 0x00, 0x04, 0x08, 0x00, 0x00, 0x03, 0xE8, 0x00, 0x00, 0x13, 0x88, 0x03, 0x17]))

    #ser.write(bytearray([reverse_bits('00'),reverse_bits('10'), reverse_bits('18'), reverse_bits('02'), reverse_bits('01'), reverse_bits('04'), reverse_bits('08'), reverse_bits('01'), reverse_bits('01'), reverse_bits('03'), reverse_bits('E8'), reverse_bits('01'), reverse_bits('01'), reverse_bits('13'), reverse_bits('88'), reverse_bits('C2'), reverse_bits('17')]))
#while(1):
ser.write(bytearray([reverse_bits('00'), reverse_bits('06'), reverse_bits('02'), reverse_bits('55'), reverse_bits('00'), reverse_bits('50'), reverse_bits('06'), reverse_bits('99'), reverse_bits('8F')]))
    #time.sleep(0.05)
while(1):
    if GPIO.input(13) == 0:
        GPIO.output(36, GPIO.HIGH)
        time.sleep(0.010296)
        GPIO.output(36, GPIO.LOW)
        

#ctrl_thread = threading.Thread(target=enable_out)
#ctrl_thread.start()

"""ser.write(bytearray([0x01, 0x10, 0x18, 0x02, 0x00, 0x02, 0x04, 0x00, 0x00, 0x21,0x34, 0xC1, 0xF1]))
time.sleep(0.01)
ser.write(bytearray([0x01, 0x10, 0x18, 0x04, 0x00, 0x02, 0x04, 0x00, 0x00, 0x07, 0xD0, 0x5B, 0xF0]))
time.sleep(0.01)
ser.write(bytearray([0x01, 0x10, 0x18, 0x06, 0x00, 0x02, 0x04, 0x00, 0x00, 0x05, 0xDC, 0xDB, 0x4C]))
time.sleep(0.01)
ser.write(bytearray([0x01, 0x10, 0x18, 0x08, 0x00, 0x02, 0x04, 0x00, 0x00, 0x05, 0xDC, 0x5A, 0xC0]))
time.sleep(0.01)
ser.write(bytearray([0x01, 0x10, 0x00, 0x7C, 0x00, 0x02, 0x04, 0x00, 0x00, 0x00, 0x08, 0xF5, 0x18]))
time.sleep(0.01)
ser.write(bytearray([0x01, 0x10, 0x00, 0x7C, 0x00, 0x02, 0x04, 0x00, 0x00, 0x00, 0x00, 0xF4, 0xDE]))
time.sleep(0.01)"""

