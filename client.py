import socket, struct, threading

PILOT1 = '129.21.172.16' #client
PILOT1_PORT = 8888
MY_MAC = '129.21.61.159' #server
MAC_PORT = 8888
PILOT2 = '129.21.172.211'

# I am the telescope sending data to the gui

s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
s.connect((PILOT1, MAC_PORT))
s.send('Hello Scientist :)')
