# just loading dependencies and packages

import numpy as np
from os import stat
import os
import sys
from subprocess import Popen, PIPE
import subprocess
import time
#sys.path.append('/usr/mce/mce_script/python')
sys.path.append('/data/cryo/current_data')
import mce_data
from pathlib2 import Path


def takedata(observer):
    a = 0
    y = []
    while True:

         if a < 10 : # create a check so we know the file is there and has the right name
             mce_file_name = "/data/cryo/current_data/temp.00%i" %(a)
             mce_file = Path("/data/cryo/current_data/temp.00%i" %(a+1)) #wait to read new file until old file is complete
             if mce_file.exists():
                 a = a + 1
                 f = mce_data.SmallMCEFile(mce_file_name)
                 readdata(f, mce_file_name)
                 y = readgraph(y, f, mce_file_name)
             else:
                 continue

         if a >= 10 and a < 100 :
             mce_file_name = "/data/cryo/current_data/temp.0%i"%(a)
             mce_file = Path("/data/cryo/current_data/temp.0%i"%(a+1))
             if mce_file.exists():
                 a = a + 1
                 f = mce_data.SmallMCEFile(mce_file_name)
                 readdata(f, mce_file_name)
                 y = readgraph(y, f, mce_file_name)
             else:
                 continue

         if a >= 100 :
             mce_file_name = "/data/cryo/current_data/temp.%i"%(a)
             mce_file = Path("/data/cryo/current_data/temp.%i"%(a+1))
             if mce_file.exists():
                 a = a + 1
                 f = mce_data.SmallMCEFile(mce_file_name)
                 readdata(f, mce_file_name)
                 y = readgraph(y, f, mce_file_name)
             else:
                 continue


def readdata(f, mce_file_name):
    h = f.Read(row_col=True, unfilter='DC').data
    #delete_file = ["rm %s" %(mce_file_name)] #to keep temp files from piling up in memory
    #subprocess.Popen(delete_file,shell=True)

    #d = np.array([[ [] for i in range(8)] for j in range(41)])
<<<<<<< HEAD
    d = np.empty([h.shape[0],h.shape[1]],dtype=float)
    for b in range(h.shape[0]):
        for c in range(h.shape[1]):
=======
    d = np.empty([41,8],dtype=float)
    for b in range(41):
        for c in range(8):
>>>>>>> 7854dda37939273a4bdfb87515a1f6780c3a7dbb
            d[b][c] = (np.std(h[b][c],dtype=float))

    z = ([[d[0][0], d[0][1], d[0][2], d[0][3], d[0][4], d[0][5], d[0][6], d[0][7]],
    	[d[1][0], d[1][1], d[1][2], d[1][3], d[1][4], d[1][5], d[1][6], d[1][7]],
    	[d[2][0], d[2][1], d[2][2], d[2][3], d[2][4], d[2][5], d[2][6], d[2][7]],
    	[d[3][0], d[3][1], d[3][2], d[3][3], d[3][4], d[3][5], d[3][6], d[3][7]],
    	[d[4][0], d[4][1], d[4][2], d[4][3], d[4][4], d[4][5], d[4][6], d[4][7]],
    	[d[5][0], d[5][1], d[5][2], d[5][3], d[5][4], d[5][5], d[5][6], d[5][7]],
    	[d[6][0], d[6][1], d[6][2], d[6][3], d[6][4], d[6][5], d[6][6], d[6][7]],
    	[d[7][0], d[7][1], d[7][2], d[7][3], d[7][4], d[7][5], d[7][6], d[7][7]],
    	[d[8][0], d[8][1], d[8][2], d[8][3], d[8][4], d[8][5], d[8][6], d[8][7]],
    	[d[9][0], d[9][1], d[9][2], d[9][3], d[9][4], d[9][5], d[9][6], d[9][7]],
    	[d[10][0], d[10][1], d[10][2], d[10][3], d[10][4], d[10][5], d[10][6], d[10][7]],
    	[d[11][0], d[11][1], d[11][2], d[11][3], d[11][4], d[11][5], d[11][6], d[11][7]],
   	[d[12][0], d[12][1], d[12][2], d[12][3], d[12][4], d[12][5], d[12][6], d[12][7]],
    	[d[13][0], d[13][1], d[13][2], d[13][3], d[13][4], d[13][5], d[13][6], d[13][7]],
    	[d[14][0], d[14][1], d[14][2], d[14][3], d[14][4], d[14][5], d[14][6], d[14][7]],
    	[d[15][0], d[15][1], d[15][2], d[15][3], d[15][4], d[15][5], d[15][6], d[15][7]],
    	[d[16][0], d[16][1], d[16][2], d[16][3], d[16][4], d[16][5], d[16][6], d[16][7]],
    	[d[17][0], d[17][1], d[17][2], d[17][3], d[17][4], d[17][5], d[17][6], d[17][7]],
    	[d[18][0], d[18][1], d[18][2], d[18][3], d[18][4], d[18][5], d[18][6], d[18][7]],
    	[d[19][0], d[19][1], d[19][2], d[19][3], d[19][4], d[19][5], d[19][6], d[19][7]],
   	[d[23][0], d[23][1], d[23][2], d[23][3], d[23][4], d[23][5], d[23][6], d[23][7]],
   	[d[21][0], d[21][1], d[21][2], d[21][3], d[21][4], d[21][5], d[21][6], d[21][7]],
    	[d[22][0], d[22][1], d[22][2], d[22][3], d[22][4], d[22][5], d[22][6], d[22][7]],
    	[d[23][0], d[23][1], d[23][2], d[23][3], d[23][4], d[23][5], d[23][6], d[23][7]],
    	[d[24][0], d[24][1], d[24][2], d[24][3], d[24][4], d[24][5], d[24][6], d[24][7]],
    	[d[25][0], d[25][1], d[25][2], d[25][3], d[25][4], d[25][5], d[25][6], d[25][7]],
    	[d[26][0], d[26][1], d[26][2], d[26][3], d[26][4], d[26][5], d[26][6], d[26][7]],
   	[d[27][0], d[27][1], d[27][2], d[27][3], d[27][4], d[27][5], d[27][6], d[27][7]],
    	[d[28][0], d[28][1], d[28][2], d[28][3], d[28][4], d[28][5], d[28][6], d[28][7]],
    	[d[29][0], d[29][1], d[29][2], d[29][3], d[29][4], d[29][5], d[29][6], d[29][7]],
    	[d[33][0], d[33][1], d[33][2], d[33][3], d[33][4], d[33][5], d[33][6], d[33][7]],
    	[d[31][0], d[31][1], d[31][2], d[31][3], d[31][4], d[31][5], d[31][6], d[31][7]],
        [d[32][0], d[32][1], d[32][2], d[32][3], d[32][4], d[32][5], d[32][6], d[32][7]],
        [d[33][0], d[33][1], d[33][2], d[33][3], d[33][4], d[33][5], d[33][6], d[33][7]],
        [d[34][0], d[34][1], d[34][2], d[34][3], d[34][4], d[34][5], d[34][6], d[34][7]],
        [d[35][0], d[35][1], d[35][2], d[35][3], d[35][4], d[35][5], d[35][6], d[35][7]],
        [d[36][0], d[36][1], d[36][2], d[36][3], d[36][4], d[36][5], d[36][6], d[36][7]],
        [d[37][0], d[37][1], d[37][2], d[37][3], d[37][4], d[37][5], d[37][6], d[37][7]],
        [d[38][0], d[38][1], d[38][2], d[38][3], d[38][4], d[38][5], d[38][6], d[38][7]],
        [d[39][0], d[39][1], d[39][2], d[39][3], d[39][4], d[39][5], d[39][6], d[39][7]],
        [d[40][0], d[40][1], d[40][2], d[40][3], d[40][4], d[40][5], d[40][6], d[40][7]]])

    filename = 'tempfiles/tempzdata.txt'
    tempfile = open(filename, 'w')

    #print('Z:',z)

<<<<<<< HEAD
    for x in range(h.shape[0]):
        for y in range(h.shape[1]):
=======
    for x in range(41):
        for y in range(8):
>>>>>>> 7854dda37939273a4bdfb87515a1f6780c3a7dbb
            tempfile.write(str(z[x][y])+' ')
        tempfile.write('\n')

    tempfile.close()
    #time.sleep(1.0)

def readgraph(y, f, mce_file_name):
    h = f.Read(row_col=True, unfilter='DC').data
    delete_file = ["rm %s" %(mce_file_name)] #to keep temp files from piling up in memory
    subprocess.Popen(delete_file,shell=True)
<<<<<<< HEAD

    chfile = open('tempfiles/tempchannel.txt', 'r')
    ch = int(chfile.read().strip())
    #T = range(h.shape[0])
    if len(y) < 5000:
        y.append(h[:,ch]) #should output every row, and only 1 channel or column for all frame data
    else:
        y = y[1000:] #each 500 frame file will add 33 data points to y

    print(y)

=======

    chfile = open('tempfiles/tempchannel.txt', 'r')
    ch = int(chfile.read().strip())
    #T = range(h.shape[0])
    if len(y) < 5000:
        y.append(h[:][ch])
    else:
        y = y[1000:]

    print(y)

>>>>>>> 7854dda37939273a4bdfb87515a1f6780c3a7dbb
    filename = 'tempfiles/tempgraphdata.txt'
    tempfile = open(filename, 'a')

    for i in range(len(y)):
        tempfile.write(str(y[i])+' ')
<<<<<<< HEAD
=======



>>>>>>> 7854dda37939273a4bdfb87515a1f6780c3a7dbb
    tempfile.close()
    return y

if __name__ == "__main__":
    takedata(sys.argv[1])
