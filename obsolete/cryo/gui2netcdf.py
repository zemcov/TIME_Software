import subprocess
import os

def writetopipe(parameters):
    #pipename of gui2temp
    pipename = 'gui2temp'
    #changes list of parameters into string to pass over named pipe
    data = parameters[0] + ' ' + str(parameters[1]) + ' ' + parameters[2] + ' ' + parameters[3]
    #creates pipe with name of pipename
    os.mkfifo(pipename)
    #opens named pipe to write parameters to it
    fifo = open(pipename, 'w')
    #writes data to named pipe
    fifo.write(data)
    #prints message to verfiy that write/read was successful
    print "Data is written"


def main():
    #deletes old pipe called gui2temp so os.mkfifo can work
    deleteoldpipe = subprocess.call(['rm', 'gui2temp'])
    #fake gui parameters - represents gui passing parameters
    parameters = ['Jake', 12, 'All', '9000']

    writetopipe(parameters)

if __name__ == '__main__':
    main()
