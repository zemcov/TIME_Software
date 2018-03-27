def readfrompipe(pipename):
    #opens named pipe and reads parameters
    with open(pipename, 'r') as fifo:
        #changes format of parameters from
        #'filename datamode readoutcard frames' (string) >>
        #['filename', int(datamode), 'readoutcard', 'frames'] (list)
        parameters = fifo.read().strip().split()
        #converts parameters[1] (datamode) to integer (only to keep with rest of
        #code, can be kept as string instead if needed)        
        parameters[1] = int(parameters[1])
    return parameters


def main():
    #pipename - whatever we decide to call pipe
    pipename = 'gui2temp'
    parameters = readfrompipe(pipename)
    print(parameters)

if __name__ == '__main__':
    main()
