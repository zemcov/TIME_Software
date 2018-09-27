import socket, struct, subprocess
import settings as st

PORT = 8888
# I am accepting tel socket packets as server
run = True
tele = []

def main():
    st.s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    st.s.bind(('',PORT))
    print('Server listening on port %i' %(PORT))
    st.s.listen(5)

    unpacker = struct.Struct('d d d d d d d')
    client, info = st.s.accept()

    while run == True:
        data = client.recv(unpacker.size)
        pa,slew_flag,alt,az,ra,dec,time = unpacker.unpack(data)
        tempfilename = '/home/pilot1/TIME_Software/tempfiles/tempteledata.txt'
        f = open(tempfilename,'a')
        f.write("\n%.06f,%.06f,%.06f,%.06f,%.06f,%.06f" %(pa, slew_flag, alt, az, ra, dec))
        f.close()

def stop_sock(s):
    run = False
    print("Client Socket Shutdown")
    s.shutdown(socket.SHUT_RDWR)
    s.close()
    sys.exit()


    #print('Data Received')
    #print('Tel Server:',pa,slew_flag,alt,az,ra,dec)
if __name__=='__main__':
    main()
