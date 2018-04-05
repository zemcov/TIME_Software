import os
import subprocess
import time


def getGraphData():
    a = 1
    y = [[] for i in range(10)]

    while True:
        time.sleep(0.1)

        filename = 'tempgraphdata.txt'

        for i in range(10):
            y[i] = (i * a + a + i) % 100

        tempfile = open(filename, 'w')

        for i in range(10):
            tempfile.write(str(y[i])+' ')

        a += 1


def main():
    getGraphData()


if __name__ == '__main__':
    main()
