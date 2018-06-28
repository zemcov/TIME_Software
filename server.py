import socket, struct, threading

PILOT1 = '129.21.172.16' #client
PILOT1_PORT = 8888
PILOT2 = '129.21.172.211' #server
PILOT2_PORT = 500008

# I am accepting telescope sim data for the gui

s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
s.bind('127.0.0.1',PILOT1_PORT)
print('Server listening on localhost port 8888')
s.listen(5)
unpacker = struct.Struct('f?ffffs')
# f is float
# ? is boolean
while True:
    data = s.recv(unpacker.size)
    pa,slew_flag,alt,az,ra,dec,time = unpacker.unpack(data)

    # (client,address) = s.accept()
    # ctrl_thread = threading.Thread(target=client)
    # ctrl_thread.start()
