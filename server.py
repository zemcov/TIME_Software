import socket, struct, threading

PILOT1 = '129.21.172.16' #client
PILOT1_PORT = 8888
PILOT2 = '129.21.172.211' #server
PILOT2_PORT = 500008
MY_MAC = '129.21.61.159' #server
MAC_PORT = 50008

# I am accepting telescope sim data for the gui

s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
s.bind(('127.0.0.1',MAC_PORT))
print('Server listening on port %i' %(MAC_PORT))
s.listen(5)
#unpacker = struct.Struct('f?ffffs')
client, info = s.accept()
unpacker = struct.Struct('5s')
# f is float
# ? is boolean
while True:
    data = client.recv(unpacker.size)
    #pa,slew_flag,alt,az,ra,dec,time = unpacker.unpack(data)
    print('Data Received')
    hello = unpacker.unpack(data)

    # (client,address) = s.accept()
    # ctrl_thread = threading.Thread(target=client)
    # ctrl_thread.start()
