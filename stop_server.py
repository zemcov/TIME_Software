import sys
sys.path.append('/home/pilot1/TIME_Software')
import readteledata
import socket

print("Server Socket Shutdown")
#readteledata.on = False
#s.shutdown(socket.SHUT_RDWR)
readteledata.s.close()
sys.exit()
