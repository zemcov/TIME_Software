
import socket, struct, subprocess, os, sys
# from socket import htonl
import time
import numpy as np
import multiprocessing as mp

class TIME_TELE :

    def __init__(self):
        self.tel_exit = mp.Event()

        PORT = 1806
        s1 = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        s1.bind(('',6666))
        s1.connect('192.168.1.252',PORT)
        # client1, info = s1.accept()
        print('Socket Connected')
        s1.send('hiya')
        print('message sent')
        data = s1.recv(1024).decode("ascii")
        print(data)
        if data != 0 :
            s1.send('hello world')
            # self.start_sock_tcomm()
        else :
            print('Junk reply')

    # def start_sock_tcomm(self):
    #
    #     PORT2 = 1806
    #     HOST2 = '192.168.1.252'
    #     s2 = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    #     s2.connect((HOST2,PORT2))
    #     print('Tracker Socket Connected')
    #     s2.send('hello world')
        # ===============================================================

if __name__ == '__main__':
    TIME_TELE()
