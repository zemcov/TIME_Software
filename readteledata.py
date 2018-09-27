import socket, struct, subprocess

PORT = 8888
# I am accepting tel socket packets as server
run = True
tele = []
s = 0
def main():
    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    s.bind(('',PORT))
    print('Server listening on port %i' %(PORT))
    s.listen(5)

    unpacker = struct.Struct('d d d d d d d')
    client, info = s.accept()
    loop()
    return s

def loop():
    while run == True:
        data = client.recv(unpacker.size)
        pa,slew_flag,alt,az,ra,dec,time = unpacker.unpack(data)
        tempfilename = '/home/pilot1/TIME_Software/tempfiles/tempteledata.txt'
        f = open(tempfilename,'a')
        f.write("\n%.06f,%.06f,%.06f,%.06f,%.06f,%.06f" %(pa, slew_flag, alt, az, ra, dec))
        f.close()

# def stop_sock(s):
#     run = False
#     print("Client Socket Shutdown")
#     s.shutdown(socket.SHUT_RDWR)
#     s.close()
#     sys.exit()


    #print('Data Received')
    #print('Tel Server:',pa,slew_flag,alt,az,ra,dec)
if __name__=='__main__':
    main()
