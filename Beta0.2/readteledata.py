import socket, struct

PORT = 8888

# I am accepting telescope sim data for the gui

s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
s.bind(('',PORT))
print('Server listening on port %i' %(PORT))
s.listen(5)
unpacker = struct.Struct('d i d d d d d')
client, info = s.accept()
while quit != 'Close':
    data = client.recv(unpacker.size)
    pa,slew_flag,alt,az,ra,dec,time = unpacker.unpack(data)
    tempfilename = 'tempfiles/tempteledata.txt'
    tempfile = open(tempfilename, 'w')
    tempfile.write(str(pa)+' ')
    tempfile.write(str(slew_flag)+' ')
    tempfile.write(str(alt)+' ')
    tempfile.write(str(az)+' ')
    tempfile.write(str(ra)+' ')
    tempfile.write(str(dec)+' ')
    tempfile.write(str(time))
    tempfile.close()
    quittempfilename = 'tempfiles/quitele.txt'
    quittempfile = open(quittempfilename, 'r')
    quit = quittempfile.read().strip()
    quittempfile.close()
    print('Data Received')
    print(pa,time)
s.close()
print('Successfully Closed')
