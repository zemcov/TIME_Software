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

'''
TESTING KMIRROR SIDE
'''

#data structure
'''
[:,0] = utc
[:,1] = pa
[:,2] = ?
[:,3] = ?
[:,4] = ?
[:,5] = azvelcmd
[:,6] = elvelcmd
[:,7] = azvelact
[:,8] = elvelact
self.pa = sim_data[n,1]
self.direction = sim_data[n,-1]
self.utc = sim_data[n,0]
azvelcmd = sim_data[n,5]
elvelcmd = sim_data[n,6]
azvelact = sim_data[n,7]
elvelact = sim_data[n,8]
'''
def kms_ports():
    data_file = '/home/time_user/kmirror_testing/TIME_Software/kms_test_0_perm.npy'
    data = np.load(data_file, allow_pickle=True)
    print(data.shape)
    # PORT = 8500
    # sim_gui_s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    # sim_gui_s.bind(('',PORT))
    # print('GUI Listening for KMS')
    # sim_gui_s.listen(5)
    # client, info = sim_gui_s.accept()
    # print('Socket Connected at 8500 hooray!')
    # unpacker = struct.Struct('d i d d') # d = float , s = char string , i = integer
    kms_connect_flag = False
    while not kms_connect_flag:
        print('trying to connect to KMS on port 8000')
        time.sleep(1)
        try:
            PORT = 8000
            kms_s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            kms_s.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
            # s.bind(('',PORT))
            kms_s.connect(('', PORT))
            print('Connected to KMS on port 8000')
            kms_connect_flag = True
        except ConnectionRefusedError:
            pass

    packer = struct.Struct('i i i i d d d d d d')
    for i in range(data.shape[0]):
        print('sending pack %s' %i)
        blank = 0; direction=1; obs=1; pad=1; azvelcmd=data[i,5]; elvelcmd=data[i,6]
        azvelact=data[i,7];elvelact=data[i,8];utc=data[i,0];pa=data[i,1]
        send_data = packer.pack(blank, direction, obs, pad, azvelcmd, elvelcmd, azvelact, elvelact, utc, pa)
        kms_s.send(send_data)
        time.sleep(1)

    print('awaiting signals')
    time.sleep(10) #sleep for 20
    # kms_s.shutdown()
    kms_s.close()
    # sim_gui_s.shutdown()
    sim_gui_s.close()

def gui_ports():

    print('Starting socket')
    c = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    PORT = 1806
    print('Binding to port %s' % PORT)
    c.bind(('', PORT))
    c.listen()
    print('Listening on port %s' % PORT)
    conn, addr = c.accept()
    print('Connected to port %s' % PORT)
    conn.sendall(b'Hello GUI!')
    reply = conn.recv(1024).decode("ascii")
    print(reply)

    server_connect_flag = False
    while not server_connect_flag:
        print('trying to connect to GUI on port 4444')
        time.sleep(1)
        try:
            PORT = 4444
            s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            s.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
            s.bind(('',PORT))
            s.connect(('', PORT))
            print('Connected to GUI on port 4444')
            server_connect_flag = True
        except ConnectionRefusedError:
            pass
    s.sendall(b'Hello World')
    while True:
        data = conn.recv(1024).decode("ascii")
        if data:
            print(data)
            if data == 'TIME_START_TELEMETRY 0':
                print('ending while loop')
                break
            conn.send('Message Received -simple_socket_test'.encode())
        if not data:
            pass
    print('kmirror_socket_time')
    kms_ports()

if __name__ == '__main__':
    gui_ports()
