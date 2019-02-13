# raster 2D script

import socket, struct, subprocess, os, sys
import time
import numpy as np

''' how do I get the telescope to connect at the other end? '''
''' Need to send "TIME_START_TELEMETRY ON" before activating socket'''

def start_sock():
    # I am accepting telescope sim data for the gui
    PORT = 1806
    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    s.bind(('',PORT))
    print('Server Listening')
    s.listen(5)
    unpacker = struct.Struct('s i i i i d d d d d d d d d d d d d d d d') # d = float , s = char string , i = integer
    ack = struct.Struct('s') ''' for when we know what telescope acknowlegement looks like'''
    client, info = s.accept()
    # time.sleep(1.0)
    message = tel_init(client,sec,map_size,map_angle,coord,epoch,object)
    return message
    # =================================================================================================================

def tel_init(client,sec,map_size,map_angle,coord):
    cmnd_list = ['TIME_START_TELEMETRY ON','TIME_START_TRACKING off','TIME_SCAN_TIME %s','TIME_MAP_SIZE %s','TIME_MAP_ANGLE %s','TIME_MAP_COORD %s'/
                'SEEK %s %s %s %s' %(sec,map_size,map_angle,coord,coord[0],coord[1],epoch,object)]
    for i in range(len(cmnd_list)):
        client.send(cmnd_list[i].encode('utf-8'))
        reply = client.recv(ack.size)
        # wait for ack from tel
    message = 'TELESCOPE INITIALIZED, STATUS: READY'
    return message


def move_tel(queue,sec,map_size,map_angle,coord,epoch,object):
    n = 0

    while True:

        if ut.tel_exit.is_set(): # if shutdown command from software, send shutdown command to tel
            print("Client Shutting Down")
            stop_msg = 'TIME_START_TRACKING off'
            client.send(stop_msg.encode('utf-8'))
            reply = client.recv(ack.size)
            # wait for ack
            final_msg = 'TIME_START_TELEMETRY off'
            client.send(final_msg.encode('utf-8'))
            reply = client.recv(ack.size)
            # wait for ack
            break

        else :
            ''' starting position depends heavily on whether or not center position of telescope
                is center of time pixel array'''

            # position_update(ra,dec)
            msg = ''
            client.send(msg.encode())

            data = client.recv(unpacker.size)
            # unpacking data packet ===============================================
            name, blanking, direction, observing, pad, /
            ut, lst, deltaT, cur_ra, cur_dec, map_ra, map_dec, /
            ra_off, dec_off, az, el, azvelcmd, elvelcmd, azvelact, elvelact, /
            pa = unpacker.unpack(data)
            # ==================================================================
            n += 1
            tel_data = np.array([float(blanking), float(direction), float(observing), float(pad), /
            ut, lst, deltaT, cur_ra, cur_dec, map_ra, map_dec, /
            ra_off, dec_off, az, el, azvelcmd, elvelcmd, azvelact, elvelact, /
            pa])
            np.save('/home/time/time-software-testing/TIME_Software/main/tempfiles/tele_packet%i.npy' %(n), tel_data)
            # send positional data to gui window
            queue.send([pa,float(direction),el,az,map_ra,map_dec,ut])

    print("Telescope Socket Closed")
    s.shutdown(socket.SHUT_RDWR)
    s.close()
    sys.exit()

def pos_update(queue2,coord):

    ''' have this update every time it gets a flag saying that the telescope is on source
        update from the gui tel thread'''
    # ''' Each beam width is 0.43 ' or 0.0071666 degrees. So I subtracted that from 20 and kept going until I had 16 positions.'''
    # ra = [19.8925,19.8996,19.9068,19.9140,19.9211,19.9283,19.9355,19.9426,19.9498,19.9570,19.9641,19.9713,19.9785,19.9856,19.9928,20]
