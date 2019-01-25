import socket, struct, sys, subprocess, time
import utils as ut

def start_tel_server(queue):
    PORT = 55556
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
    subprocess.Popen(['python %s/fake_tel.py' %(dir)],shell=True)

    while True:
        data = client.recv(unpacker.size)
        pa,flag,alt,az,ra,dec,othertime = unpacker.unpack(data)
        print(pa)

        if flag == 2.0 or ut.tel_exit.is_set():
            pause_msg = '1'
            pause_msg = str.encode(pause_msg, 'utf-8')
            client.send(pause_msg)
            print("RA > 21, Client Shutting Down")
            stop_msg = '0'
            stop_msg = str.encode(stop_msg, 'utf-8')
            client.send(stop_msg)
            time.sleep(2.0)
            break

        else :
            msg = '3'
            msg = str.encode(msg, 'utf-8')
            client.send(msg)
            print('Data Received: RA %s' %(ra))

    # while not ut.tel_exit.is_set():
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
