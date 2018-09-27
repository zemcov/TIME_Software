import sys
sys.path.append('/home/pilot1/TIME_Software')
from readteledata import stop_sock,s
stop_sock(s)
sys.stdout.write('I also did a thing')

def stop_sock(s):
    run = False
    print("Client Socket Shutdown")
    s.shutdown(socket.SHUT_RDWR)
    s.close()
    sys.exit()
