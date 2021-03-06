import socket, struct
import time
import random
import datetime
import utils as ut

HOST = "129.21.172.16"
PORT = 8500

s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
print('attempting to connect')
s.connect((HOST,PORT))
print('connected')

format = "didd" #d = float, i = integer
length = struct.calcsize(format)
while True:
	pa = random.random()
	flag = random.randint(0,4)
	kms_time = random.random()
	enc_pos = random.random()
	resp = struct.pack(format, pa, flag, kms_time, enc_pos)
	s.send(resp)
	time.sleep(0.05)
