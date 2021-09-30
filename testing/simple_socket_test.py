import sys, os, subprocess, time, datetime, socket, struct, threading, shutil
import numpy as np
import multiprocessing as mp

'''
PORTS
1806 - Telescope listens for gui
4444 - gui listens for telescope
8000 - Telescope listens for kms
8500 - kms listens for telescope
'''
def gui_ports():
    # try:
    #     conn_flag = False
    #     PORT = 1806
    #     while not conn_flag:
    #         print('trying to connecto the socket manager from the GUI')
    #         time.sleep(2)
    #         try:
    #             s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    #             s.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    #             s.bind(('',6666))
    #             # s.connect(('192.168.1.252',PORT)) # this is tracker's IP
    #             s.connect(('192.168.1.252',PORT)) # this is to connect locally
    #             print('connected to the socketmanager from the GUI')
    #             conn_flag = True
    #         except Exception:
    #             pass
    #
    #     s.send('TIME_START_TELEMETRY 2'.encode())
    #     reply = s.recv(1024).decode("ascii")
    #     print(reply)
    # except KeyboardInterrupt:
    #     s.send('TIME_START_TELEMETRY 0'.encode())
    #     reply = s.recv(1024).decode("ascii")
    #     print(reply)
    #     s.shutdown()
    #     # l.shutdown()
    #     # l.close()
    #     s.close()
    # '''
    # This is the telescope listening for the GUI
    # '''
    # print('Starting socket')
    # c = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    # PORT = 1806
    # print('Binding to port %s' % PORT)
    # c.bind(('', PORT))
    # c.listen()
    # print('Listening on port %s' % PORT)
    # conn, addr = c.accept()
    # print('Connected to port %s' % PORT)
    # conn.sendall(b'Hello GUI!')
    # reply = conn.recv(1024).decode("ascii")
    # print(reply)

    '''
    This is the telescope trying to connect to the GUI
    '''
    # server_connect_flag = False
    # while not server_connect_flag:
    #     print('trying to connect to GUI on port 4444')
    #     time.sleep(1)
    #     try:
    #         PORT = 4444
    #         s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    #         s.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    #         s.bind(('',PORT))
    #         s.connect(('', PORT))
    #         print('Connected to GUI on port 4444')
    #         server_connect_flag = True
    #     except ConnectionRefusedError:
    #         pass
    # s.sendall(b'Hello World')
    # while True:
    #     data = conn.recv(1024).decode("ascii")
    #     if data:
    #         print(data)
    #         if data == 'TIME_START_TELEMETRY 0':
    #             print('ending while loop')
    #             break
    #         conn.send('Message Received -simple_socket_test'.encode())
    #     if not data:
    #         pass
    # print('kmirror_socket_time')
    '''
    This is the GUI listening for the telescope connection
    '''
    PORT = 4444
    # PORT = 10002 #for testing
    l = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    l.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    l.bind(('',PORT))
    print('.')
    print('Server Listening ------------------------------', time.localtime())
    l.listen(5)
    client, info = l.accept()
    reply = client.recv(1024).decode('ascii')
    print('Socket 2 Connected')
    print(reply)
    unpacker = struct.Struct('i i i i d d d d d d d d d d d d d d d d Q Q') # d = float , s = char string , i = integer
    n = 0

    while True:
        try:
            data = client.recv(unpacker.size)
            if len(data) !=0 :
                # unpacking data packet ===============================================
                decode_data = unpacker.unpack(data)
                print('data being sent to GUI from telescope', decode_data)
        except:
            pass


def kms_ports():
    # '''
    # This is simulating the GUI receiving data from the kmirror
    # '''
    # data_file = '/home/time_user/kmirror_testing/TIME_Software/kms_test_0_perm.npy'
    # data = np.load(data_file, allow_pickle=True)
    # print(data.shape)
    PORT = 8500
    sim_gui_s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    sim_gui_s.bind(('192.168.1.255',PORT))
    print('GUI Listening for KMS')
    sim_gui_s.listen(5)
    client, info = sim_gui_s.accept()
    print('Socket Connected at 8500 hooray!')
    unpacker = struct.Struct('d i d d') # d = float , s = char string , i = integer
    while True:
        data = client.recv(unpacker.size)
        decode_data = unpacker.unpack(data)
        print('data being sent to GUI from KMS', decode_data)
    # '''
    # Below this is to simulate the telescope sending data to the kmirror
    # '''
    # kms_connect_flag = False
    # while not kms_connect_flag:
    #     print('trying to connect to KMS on port 8000')
    #     time.sleep(1)
    #     try:
    #         PORT = 8000
    #         kms_s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    #         kms_s.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    #         # s.bind(('',PORT))
    #         kms_s.connect(('', PORT))
    #         print('Connected to KMS on port 8000')
    #         kms_connect_flag = True
    #     except ConnectionRefusedError:
    #         pass
    #
    # packer = struct.Struct('i i i i d d d d d d')
    # for i in range(data.shape[0]):
    #     print('sending pack %s' %i)
    #     blank = 0; direction=1; obs=1; pad=1; azvelcmd=data[i,5]; elvelcmd=data[i,6]
    #     azvelact=data[i,7];elvelact=data[i,8];utc=data[i,0];pa=data[i,1]
    #     send_data = packer.pack(blank, direction, obs, pad, azvelcmd, elvelcmd, azvelact, elvelact, utc, pa)
    #     kms_s.send(send_data)
    #     time.sleep(1)
    #
    # print('awaiting signals')
    # time.sleep(10) #sleep for 20
    # # kms_s.shutdown()
    # kms_s.close()
    # # sim_gui_s.shutdown()
    # sim_gui_s.close()



if __name__ == "__main__":

    # gui_ports()
    # kms_ports()
    t1 = mp.Process(target=gui_ports,args = ())
    t2 = mp.Process(target=kms_ports,args=())
    t1.start()
    t2.start()
