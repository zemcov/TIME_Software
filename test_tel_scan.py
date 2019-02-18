
import socket, struct, subprocess, os, sys
# from socket import htonl
import time
import numpy as np
import multiprocessing as mp

class TIME_TELE :

    def __init__(self):
        self.tel_exit = mp.Event()

        PORT = 6666
        s1 = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        s1.bind(('',PORT))
        print('Server Listening')
        s1.listen(5)
        client1, info = s1.accept()
        print('Socket Connected')
        data = client1.recv(1024).decode("ascii")
        print(data)
        if data != 0 :
            self.start_sock_tcomm()
        else :
            print('Junk reply')

    def start_sock_tcomm(self):

        PORT2 = 1806
        HOST2 = '192.168.1.252'
        ack = struct.Struct('s')
        s2 = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        s2.connect((HOST2,PORT2))
        print('Tracker Socket Connected')
        hiya = 'hello world'
        s2.send('hello world')
        # ===============================================================
        # ==============================================================
        # PORT = 6666
        # s3 = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        # s3.bind(('',PORT))
        # s3.listen(5)
        # client3, info = s.accept()
        # print('Socket Connected')
        # reply = client3.recv(1024).decode("ascii")
        # print('tracker reply',reply)
        # # ===============================================================

if __name__ == '__main__':
    TIME_TELE()
