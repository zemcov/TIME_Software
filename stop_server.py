import sys
sys.path.append('/home/pilot1/TIME_Software')
import readteledata

print("Client Socket Shutdown")
s.shutdown(socket.SHUT_RDWR)
s.close()
sys.exit()
