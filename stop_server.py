import sys
sys.path.append('/home/pilot1/TIME_Software')
from readteledata import s
import socket

print("Server Socket Shutdown")
s.shutdown(socket.SHUT_RDWR)
s.close()
sys.exit()
