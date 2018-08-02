def readfile():
    tempfile = open('tempfiles/testnewline.txt')
    y = []
    for i in range(374):
        y.append(tempfile.readline().strip().split())
        print(len(y))

if __name__ == '__main__':
    readfile()
