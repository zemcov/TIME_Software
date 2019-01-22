import socket, struct, sys, subprocess
import utils as ut

def start_tel_server(queue):
    PORT = 55555
    # I am accepting telescope sim data for the gui
    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    s.bind(('',PORT))
    print('Server Listening')
    s.listen(5)
    unpacker = struct.Struct('d d d d d d d')
    client, info = s.accept()
    # start up fake telescope script
    # in reality, this will be activated before sending a init signal
    # to the real telescope
    subprocess.Popen(['python fake_tel.py'],shell=True)

    while not ut.tel_exit.is_set():
        # retrieve and unpack data from socket
        data = client.recv(unpacker.size)
        pa,flag,alt,az,ra,dec,time = unpacker.unpack(data)
        if ra == (0.0,):
            # this will be replaced by the telescope shutting itself down
            # and sending us an appropriate shutdown signal
            subprocess.Popen(['pkill -9 -f fake_tel.py'],shell=True)
            break

        else:
            # if no e-stop status is sent, send updates to gui thread
            queue.send([pa,flag,alt,az,ra,dec,time])
            print('Data Received')
    # don't use this during normal operations... 
    subprocess.Popen(['pkill -9 -f fake_tel.py'],shell=True)
    print("Telescope Socket Closed")
