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

def stop_sock():
    s.shutdown(socket.SHUT_RDWR)
    s.close()
    run = False

while run == True:
    data = client.recv(unpacker.size)
    pa,slew_flag,alt,az,ra,dec,time = unpacker.unpack(data)
    tempfilename = '/home/pilot1/TIME_Software/tempfiles/tempteledata.txt'
    tempfile = open(tempfilename, 'w')
    tempfile.write(str(pa)+',')
    tempfile.write(str(slew_flag)+',')
    tempfile.write(str(alt)+',')
    tempfile.write(str(az)+',')
    tempfile.write(str(ra)+',')
    tempfile.write(str(dec)+'')
    #tempfile.write(str(time))
    tempfile.close()
    #print('Data Received')
    print('Tel Server:',pa)
