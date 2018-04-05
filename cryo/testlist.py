import subprocess
from subprocess import Popen, PIPE
import time

def modZData(z, rc):
    new_z = []

    #1 -> 0-7, 2 -> 8-15, 3 -> 16-23, 4 -> 24-31
    if rc % 4 == 1:
        for i in range(4):
            new_z.append(z[i][:1])
            print(new_z)
    elif rc % 4 == 2:
        for i in range(4):
            new_z.append(z[i][1:2])
            print(new_z)
    elif rc % 4 == 3:
        for i in range(4):
            new_z.append(z[i][2:3])
            print(new_z)
    elif rc % 4 == 0:
        for i in range(4):
            new_z.append(z[i][3:4])
            print(new_z)
    return new_z

def main():

    while True:
        tempfile = open('tempzdata.txt', 'r')
        z = [[ [] for i in range(32)] for j in range(32)]
        for line in tempfile:
            x = line.strip().split()
            for i in range(len(x)):
                x[i] = int(x[i])
            z.append(x)
        print(z)
        time.sleep(1)


if __name__ == '__main__':
    main()
