import socket, struct, subprocess

PORT = 8888
# I am accepting tel socket packets as server
tele = []
s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
def main():
    s.bind(('',PORT))
    print('Server listening on port %i' %(PORT))
    s.listen(5)

    unpacker = struct.Struct('d d d d d d d')
    client, info = s.accept()
    client.setblocking(0)
    loop(client,unpacker)
    return s

def loop(client,unpacker):
    while True:
        try:
            data = client.recv(unpacker.size)
            pa,slew_flag,alt,az,ra,dec,time = unpacker.unpack(data)
            tempfilename = '/home/pilot1/TIME_Software/tempfiles/tempteledata.txt'
            f = open(tempfilename,'a')
            f.write("\n%.06f,%.06f,%.06f,%.06f,%.06f,%.06f" %(pa, slew_flag, alt, az, ra, dec))
            f.close()
        except socket.error,(value,msg):
            if value != 11:
                raise

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
