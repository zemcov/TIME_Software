import os

def readfrompipe(pipename):
    z = []
    #opens named pipe and reads parameters
    with open(pipename, 'r') as fifo:
        data = fifo.read()
        print(data)
        data = data.strip().split('\n')
        print(data)
        for j in range(32):
            print(z)
            z[j] = data[j].strip().split()

    return z


def main():
    while True:
    #pipename - whatever we decide to call pipe
        pipename = 'data2temp'
        z = readfrompipe(pipename)
        print(z)

if __name__ == '__main__':
    main()
