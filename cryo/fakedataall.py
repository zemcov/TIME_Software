import time

def getMCEData():
    a = 0
    print('Hello!')

    while True:
        a = a+1
        time.sleep(0.1)

        #Heatmap Data
        z = [[ [] for i in range(32)] for j in range(32)]

        for i in range(32):
            for j in range(32):
                z[j][i] = j * i * a % 100

        filename = 'tempzdata.txt'

        tempfile = open(filename, 'w')

        for i in range(32):
            for j in range(32):
                tempfile.write(str(z[j][i])+' ')
            tempfile.write('\n')

        tempfile.close()

        #Graph Data
        y = [[] for i in range(10)]
        filename = 'tempgraphdata.txt'
        for i in range(10):
            y[i] = (i * a + a + i) % 100
        tempfile = open(filename, 'w')
        for i in range(10):
            tempfile.write(str(y[i])+' ')
        tempfile = open(filename, 'r')
        #print(tempfile.read().strip())
        tempfile.close()


def main():
    getMCEData()


if __name__ == '__main__':
    main()
