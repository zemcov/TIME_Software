
import socket, struct, subprocess, os, sys
# from socket import htonl
import time
import numpy as np
import multiprocessing as mp
import tom_tel

class TIME_TELE :

    def __init__(self):
        self.tel_exit = mp.Event()

        PORT = 1806
        s1 = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        s1.bind(('',6666))
        s1.connect(('192.168.1.252',PORT))
        # client1, info = s1.accept()
        print('Socket Connected')
        s1.send('time_start_telemetry on')
        print('message sent')
        data = s1.recv(1024).decode("ascii")
        print(data)
        if 'OK' in data:
            p = mp.Process(target=tom_tel.start_sock_tracker)
            p.start()
        else :
            print('ERROR reply')
        time.sleep(10.0)
        s1.send('time_start_telemetry off')
        print('telemetry off')
        data2 = s1.recv(1024).decode("ascii")
        print(data2)


if __name__ == '__main__':
    TIME_TELE()
