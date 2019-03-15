import socket, struct, subprocess, os, sys
import time

def test_sock():
    PORT = 5656
    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    s.connect(('192.168.1.84',PORT))
    print('Socket Connected')

    while True :
        try :
            s.send('hiya kmirror!')
            time.sleep(1.0)

        except KeyboardInterrupt :
            break

    s.close()
    sys.exit()

if __name__ == '__main__':
    test_sock()
