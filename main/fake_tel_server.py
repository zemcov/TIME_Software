import socket, struct, sys, subprocess, time
import utils as ut
dir = '/Users/vlb9398/Desktop/Gui_Code/TIME_Software/main'

# def start_tel_server(queue):
PORT = 55556
# I am accepting telescope sim data for the gui
s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
s.bind(('',PORT))
print('Server Listening')
s.listen(5)
# unpacker = struct.Struct('d d d d d d d')
unpacker = struct.Struct('d')
client, info = s.accept()
# start up fake telescope script
# in reality, this will be activated before sending a init signal
# to the real telescope
# subprocess.Popen(['python %s/fake_tel.py' %(dir)],shell=True)
while True :
    if not ut.tel_exit.is_set() :
        s.send('server online')
        tel_stuff = client.recv(unpacker.size)
        # pa,flag,alt,az,ra,dec,othertime = unpacker.unpack(tel_stuff)
        ra = unpacker.unpack(tel_stuff)
        print(ra)
        if ra > 21.0 :
            ut.tel_exit.set()
    else :
        s.send('server going offline')
        # time.sleep(2.0)
        break

# while True:
#     # retrieve and unpack data from socket
#     data = client.recv(unpacker.size)
#     pa,flag,alt,az,ra,dec,othertime = unpacker.unpack(data)
#     print(flag)
#     if flag == 2.0:
#         time.sleep(2.0)
#         break
#
#     else:
#         print("DATA Received: %s" %(pa))
        # if no e-stop status is sent, send updates to gui thread
        # queue.send([pa,flag,alt,az,ra,dec,time])

print("Telescope Socket Closed")
sys.exit()
