from netCDF4 import Dataset
from netCDF4 import MFDataset
import time as time
import os

i = 0
n = 0

def file():
    mce_data = Dataset("gui_data_test%s.nc","w",format="NETCDF4") %(n)

    if os.stat("~/gui_data_test%s.nc").st_size %(n) < :# of bytes here
        if i == 0:
            # create the gui parameters group
            guiparams = mce_data.createGroup('guiparams')
            stream_data = mce_data.createGroup('stream data')
            heatmap_data = mce_data.createGroup('heatmap data')
            mce_header_run = mce_data.createGroup('mce header info')

            # set dimensions before creating a variable
            mce_data.createDimension('observer',None) # none means unlimited dimension
            mce_data.createDimension('datetime',None)
            mce_data.createDimension('frames',None)
            mce_data.createDimension('datamode',None)
            mce_data.createDimension('rc',None)

            mce_data.createDimension('rms noise all rc cards',None)
            mce_data.createDimension('rms noise 1 rc card',None)

            mce_data.createDimension('detector',None)
            mce_data.createDimension('header',None)

            # creating variables
            Observer = mce_data.createVariable("/guiparams/observer","S3",("observer",)) #observer initials, only 3 characters
            Datetime = mce_data.createVariable('/guiparams/datetime', 'f8',('datetime',)) #not sure what the
            Frames = mce_data.createVariable('/guiparams/frames', 'f8',('frames',))
            Datamode = mce_data.createVariable('/guiparams/datamode','i8',('datamode',))
            Rc = mce_data.createVariable('/guiparams/rc','i8',('rc',)) # can either use rc name or integer used by gui

            rms_noise_all = mce_data.createVariable('/heatmap_data/rms_noise_all','f8',('rms noise all rc cards',))
            rms_noise_onerc = mce_data.createVariable('/heatmap_data/rms_noise_onerc','f8',('rms noise 1 rc card',))

            detector = mce_data.createVariable('/stream_data/detector','f8',('detector',))
            raw_data = mce_data.createVariable('/stream_data/raw_data','f8',('data',))

            mce_header = mce_data.createVariable('/mce_header_run/mce_header','f8',('mce header'))

            Observer[0] = parameters[0]
            Frames[0] = parameters[3]
            Datetime[0] = parameters[4]
            Datamode[0] = parameters[1]
            Rc[0] = parameters[3]
            rms_noise_all[0] = hm_data '''need some way of distinguishing between all and one rc for data storage...
                probably an if statement'''
            rms_noise_onerc[0] = hm_data
            mce_header[0] = header
            raw_data[0] = data

                '''want to add in something for mce header here, but only do it once per file.
                    we don't need multiple copies'''
            mce_header[0] = #whatever pipe we use to transfer this

            i = i + 1
            #time.sleep(1.0)
            '''time.sleep() might not be necessary if this python file is only called once the
                    pipes have been populated with data that we know is correct'''


        else:
            Observer[i] = parameters[0]
            Frames[i] = parameters[3]
            Datamode[i] = parameters[1]
            Rc[i] = parameters[3]
            rms_noise_all[i] = hm_data
            rms_noise_onerc[i] = hm_data
            mce_header[i] = header
            raw_data[i] = data

            i = i + 1
            #time.sleep(1.0)

    else:
        n = n + 1
        i = 0
        mce_data.close() #close the old file
        mce_data = Dataset("gui_data_test%s.nc","w",format="NETCDF4") %(n)


def params(pipename):
    #opens named pipe and reads parameters
    with open(pipename, 'r') as fifo:
        parameters = fifo.read().strip().split()
        parameters[1] = int(parameters[1])
    return parameters

def hm_data_stream(pipename2):
    with open(pipename2, 'r') as fifo:
        hm_data = fifo.read()
    return hm_data

def header_data(pipename3):
    with open(pipename3, 'r') as fifo:
        header = fifo.read()
    return header

def live_data(pipename4):
    with open(pipename4, 'r') as fifo:
        data = fifo.read()
    return data

def main():
    pipename = 'params'
    pipename2 = 'heatmap'
    pipename3 = 'header'
    pipenmae4 = 'livedata'

    parameters = params(pipename)
    hm_data_stream(pipename2)
    header_data_stream(pipename3)
    live_data(pipename4)
    file()


    #print(mce_data["/guiparams/observer"])
    #print(mce_data["/guiparams/observer"])

if __name__ == '__main__':
    main()
