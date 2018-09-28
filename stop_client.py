import sys
sys.path.append('/home/pilot2/TIME_Software')
from tel_sock import s
import socket

print("Client Socket Shutdown")
s.shutdown(socket.SHUT_RDWR)
s.close()
sys.exit()
