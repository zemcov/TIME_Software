import sys
sys.path.append('/home/pilot2/TIME_Software')
import tel_sock
import socket

print("Client Socket Shutdown")
tel_sock.s.shutdown(socket.SHUT_RDWR)
tel_sock.s.close()
sys.exit()
