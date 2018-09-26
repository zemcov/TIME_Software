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
    tempfile.write(pa + ' ')
    tempfile.write(slew_flag + ' ')
    tempfile.write(alt + ' ')
    tempfile.write(az + ' ')
    tempfile.write(ra + ' ')
    tempfile.write(dec + ' ')
    #tempfile.write(str(time))
    tempfile.close()
    #print('Data Received')
    #print('Tel Server:',pa,slew_flag,alt,az,ra,dec)
