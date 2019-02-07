import socket, struct, sys, subprocess, time
import utils as ut

def start_tel_server(queue):
    PORT = 55562
    # I am accepting telescope sim data for the gui
    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    s.bind(('',PORT))
    print('Server Listening')
    s.listen(5)
    unpacker = struct.Struct('d d d d d d d')
    client, info = s.accept()

    while True:

        if ut.tel_exit.is_set():
            print("Client Shutting Down")
            stop_msg = 'end'
            client.send(stop_msg.encode())
            break

        else :
            msg = 'go'
            client.send(msg.encode())
            data = client.recv(unpacker.size)
            pa,flag,alt,az,ra,dec,othertime = unpacker.unpack(data)
            queue.send([pa,flag,alt,az,ra,dec,time])


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
    s.shutdown(socket.SHUT_RDWR)
    s.close()
    sys.exit()
