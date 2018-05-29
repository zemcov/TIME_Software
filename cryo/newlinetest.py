import random as r

def writefile():
    y = [[[[] for k in range(374)] for j in range(8)] for i in range(32)]
    for i in range(32):
        for j in range(8):
            for k in range(374):
                y[i][j][k] = i * j * k % 100
    tempfile = open('tempfiles/testnewline.txt', 'w')
    for k in range(374):
        for i in range(32):
            for j in range(8):
                tempfile.write(str(y[i][j][k]) + ' ')
        tempfile.write('\n')
if __name__ == '__main__':
    writefile()
