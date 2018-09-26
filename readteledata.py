import socket, struct, subprocess

PORT = 8888
# I am accepting tel socket packets as server

s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
s.bind(('',PORT))
print('Server listening on port %i' %(PORT))
s.listen(5)

unpacker = struct.Struct('d d d d d d d')
client, info = s.accept()
run = True
tele = []

def stop_sock():
    s.shutdown(socket.SHUT_RDWR)
    s.close()
    run = False

while run == True:
    data = client.recv(unpacker.size)
    pa,slew_flag,alt,az,ra,dec,time = unpacker.unpack(data)
    tempfilename = '/home/pilot1/TIME_Software/tempfiles/tempteledata.txt'
    f = open(tempfilename,'w')
    f.write("%d , %d , %d , %d , %d , %d" , pa, slew_flag, alt, az, ra, dec)
    f.close()

    #print('Data Received')
    #print('Tel Server:',pa,slew_flag,alt,az,ra,dec)
