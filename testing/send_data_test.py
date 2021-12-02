import sys, os, subprocess, time, datetime, socket, struct, threading, shutil

HOST = '127.0.0.1'  # The server's hostname or IP address
print('Starting socket')
s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
PORT = 10001
HOST = '127.0.0.1' #change this to time.ce.rit.edu's ip
print('Binding to host %s' % HOST)
s.connect((HOST, PORT))
s.sendall(b'Hello World')
