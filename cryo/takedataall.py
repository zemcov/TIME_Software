# just loading dependencies and packages
import plotly.plotly as py
import numpy as np
import plotly.tools as tls
import plotly.graph_objs as go
import mce_data
import os
import matplotlib.pyplot as plt
import sys
from subprocess import Popen, PIPE
from datetime import datetime
import subprocess
from shutil import copy2
import time

def takedataall(observer):
    a = 0
    while True:
        if a < 10 : # create a check so we know the file is there and has the right name
            mce_file_name = "/data/cryo/current_data/temp.00%i" %(a)
            mce_file = Path("/data/cryo/current_data/temp.00%i" %(a+1)) #wait to read new file until old file is complete
            if mce_file.exists():
                a = a + 1
                f = mce_data.SmallMCEFile(mce_file_name)
                readdata(f, mce_file_name)
                y = readgraphall(y, f, mce_file_name)
            else:
                continue

        if a >= 10 and a < 100 :
            mce_file_name = "/data/cryo/current_data/temp.0%i"%(a)
            mce_file = Path("/data/cryo/current_data/temp.0%i"%(a+1))
            if mce_file.exists():
                a = a + 1
                f = mce_data.SmallMCEFile(mce_file_name)
                readdata(f, mce_file_name)
                y = readgraphall(y, f, mce_file_name)
            else:
                continue

        if a >= 100 :
            mce_file_name = "/data/cryo/current_data/temp.%i"%(a)
            mce_file = Path("/data/cryo/current_data/temp.%i"%(a+1))
            if mce_file.exists():
                a = a + 1
                f = mce_data.SmallMCEFile(mce_file_name)
                readdata(f, mce_file_name)
                y = readgraphall(y, f, mce_file_name)
            else:
                continue

def readdataall(f,mce_file_name):
    h = f.Read(row_col=True, unfilter='DC').data
    delete_file = ["rm %s" %(mce_file_name)] #to keep temp files from piling up in memory
    subprocess.Popen(delete_file,shell=True)

    #d = np.array([[ [] for i in range(8)] for j in range(41)])
    d = np.empty([h.shape[0],h.shape[1]],dtype=float)
    for b in range(h.shape[0]):
        for c in range(h.shape[1]):
            d[b][c] = (np.std(h[b][c],dtype=float))

    z = ([[d[0][0], d[0][1], d[0][2], d[0][3], d[0][4], d[0][5], d[0][6],\
               d[0][7], d[0][8], d[0][9], d[0][10], d[0][11], d[0][12], d[0][13],\
               d[0][14], d[0][15], d[0][16], d[0][17], d[0][18], d[0][19],\
               d[0][20], d[0][21], d[0][22], d[0][22], d[0][24], d[0][25],\
               d[0][26], d[0][27], d[0][28], d[0][29], d[0][30], d[0][31]],\
              [d[1][0], d[1][1], d[1][2], d[1][3], d[1][4], d[1][5], d[1][6],\
               d[1][7], d[1][8], d[1][9], d[1][10], d[1][11], d[1][12], d[1][13],\
               d[1][14], d[1][15], d[1][16], d[1][17], d[1][18], d[1][19],\
               d[1][20], d[1][21], d[1][22], d[1][23], d[1][24], d[1][25],\
               d[1][26], d[1][27], d[1][28], d[1][29], d[1][33], d[1][31]],\
              [d[2][0], d[2][1], d[2][2], d[2][3], d[2][4], d[2][5], d[2][6],\
               d[2][7], d[2][8], d[2][9], d[2][10], d[2][11], d[2][12], d[2][13],\
               d[2][14], d[2][15], d[2][16], d[2][17], d[2][18], d[2][19],\
               d[2][20], d[2][21], d[2][22], d[2][23], d[2][24], d[2][25],\
               d[2][26], d[2][27], d[2][28], d[2][29], d[2][33], d[2][31]],\
              [d[3][0], d[3][1], d[3][2], d[3][3], d[3][4], d[3][5], d[3][6],\
               d[3][7], d[3][8], d[3][9], d[3][10], d[3][11], d[3][12], d[3][13],\
               d[3][14], d[3][15], d[3][16], d[3][17], d[3][18], d[3][19],\
               d[3][20], d[3][21], d[3][22], d[3][23], d[3][24], d[3][25],\
               d[3][26], d[3][27], d[3][28], d[3][29], d[3][33], d[3][31]],\
              [d[4][0], d[4][1], d[4][2], d[4][3], d[4][4], d[4][5], d[4][6],\
               d[4][7], d[4][8], d[4][9], d[4][10], d[4,11], d[4][12], d[4][13],\
               d[4][14], d[4][15], d[4][16], d[4][17], d[4][18], d[4][19],\
               d[4][20], d[4][21], d[4][22], d[4][23], d[4][24], d[4][25],\
               d[4][26], d[4][27], d[4][28], d[4][29], d[4][34], d[4][31]],\
              [d[5][0], d[5][1], d[5][2], d[5][3], d[5][4], d[5][5], d[5][6],\
               d[5][7], d[5][8], d[5][9], d[5][10], d[5,11], d[5][12], d[5][13],\
               d[5][14], d[5][15], d[5][16], d[5][17], d[5][18], d[5][19], d[5][20],\
               d[5][21], d[5][22], d[5][23], d[5][24], d[5][25], d[5][26],\
               d[5][27], d[5][28], d[5][29], d[5][35], d[5][31]],\
              [d[6][0], d[6][1], d[6][2], d[6][3], d[6][4], d[6][5], d[6][6],\
               d[6][7], d[6][8], d[6][9], d[6][10], d[6,11], d[6][12], d[6][13],\
               d[6][14], d[6][15], d[6][16], d[6][17], d[6][18], d[6][19],\
               d[6][20], d[6][21], d[6][22], d[6][23], d[6][24], d[6][25],\
               d[6][26], d[6][27], d[6][28], d[6][29], d[6][36], d[6][31]],\
              [d[7][0], d[7][1], d[7][2], d[7][3], d[7][4], d[7][5], d[7][6],\
               d[7][7], d[7][8], d[7][9], d[7][10], d[7,11], d[7][12], d[7][13],\
               d[7][14], d[7][15], d[7][16], d[7][17], d[7][18], d[7][19],\
               d[7][20], d[7][21], d[7][22], d[7][23], d[7][24], d[7][25],\
               d[7][26], d[7][27], d[7][28], d[7][29], d[7][37], d[7][31]],\
              [d[8][0], d[8][1], d[8][2], d[8][3], d[8][4], d[8][5], d[8][6],\
               d[8][7], d[8][8], d[8][9], d[8][10], d[8,11], d[8][12], d[8][13],\
               d[8][14], d[8][15], d[8][16], d[8][17], d[8][18], d[8][19],\
               d[8][20], d[8][21], d[8][22], d[8][23], d[8][24], d[8][25],\
               d[8][26], d[8][27], d[8][28], d[8][29], d[8][38], d[8][31]],\
              [d[9][0], d[9][1], d[9][2], d[9][3], d[9][4], d[9][5], d[9][6],\
               d[9][7], d[9][8], d[9][9], d[9][10], d[9,11], d[9][12], d[9][13],\
               d[9][14], d[9][15], d[9][16], d[9][17], d[9][18], d[9][19],\
               d[9][20], d[9][21], d[9][22], d[9][23], d[9][24], d[9][25],\
               d[9][26], d[9][27], d[9][28], d[9][29], d[9][39], d[9][31]],\
              [d[10][0], d[10][1], d[10][2], d[10][3], d[10][4], d[10][5],\
               d[10][6], d[10][7], d[10][8], d[10][9], d[10,10], d[10][11],\
               d[10][12], d[10][13], d[10][14], d[10][15], d[10][16], d[10][17],\
               d[10][18], d[10][19], d[10][20], d[10][21], d[10][22], d[10][23],\
               d[10][24], d[10][25], d[10][26], d[10][27], d[10][28], d[10][29],\
               d[10][30], d[10][31]],\
              [d[11][0], d[11][1], d[11][2], d[11][3], d[11][4], d[11][5],\
               d[11][6], d[11][7], d[11][8], d[11][9], d[11,10], d[11][11],\
               d[11][12], d[11][13], d[11][14], d[11][15], d[11][16], d[11][17],\
               d[11][18], d[11][19], d[11][20], d[11][21], d[11][22], d[11][23],\
               d[11][24], d[11][25], d[11][26], d[11][27], d[11][28], d[11][29],\
               d[11][30], d[11][31]],\
              [d[12][0], d[12][1], d[12][2], d[12][3], d[12][4], d[12][5],\
               d[12][6], d[12][7], d[12][8], d[12][9], d[12,10], d[12][11],\
               d[12][12], d[12][13], d[12][14], d[12][15], d[12][16], d[12][17],\
               d[12][18], d[12][19], d[12][20], d[12][21], d[12][22], d[12][23],\
               d[12][24], d[12][25], d[12][26], d[12][27], d[12][28], d[12][29],\
               d[12][30], d[12][31]],\
              [d[13][0], d[13][1], d[13][2], d[13][3], d[13][4], d[13][5],\
               d[13][6], d[13][7], d[13][8], d[13][9], d[13,10], d[13][11],\
               d[13][12], d[13][13], d[13][14], d[13][15], d[13][16], d[13][17],\
               d[13][18], d[13][19], d[13][20], d[13][21], d[13][22], d[13][23],\
               d[13][24], d[13][25], d[13][26], d[13][27], d[13][28], d[13][29],\
               d[13][30], d[13][31]],\
              [d[14][0], d[14][1], d[14][2], d[14][3], d[14][4], d[14][5],\
               d[14][6], d[14][7], d[14][8], d[14][9], d[14][10], d[14][11],\
               d[14][12], d[14][13], d[14][14], d[14][15], d[14][16], d[14][17],\
               d[14][18], d[14][19], d[14][20], d[14][21], d[14][22], d[14][23],\
               d[14][24], d[14][25], d[14][26], d[14][27], d[14][28], d[14][29],\
               d[14][30], d[14][31]],\
              [d[15][0], d[15][1], d[15][2], d[15][3], d[15][4], d[15][5],\
               d[15][6], d[15][7], d[15][8], d[15][9], d[15][10], d[15][11],\
               d[15][12], d[15][13], d[15][14], d[15][15], d[15][16], d[15][17],\
               d[15][18], d[15][19], d[15][20], d[15][21], d[15][22], d[15][23],\
               d[15][24], d[15][25], d[15][26], d[15][27], d[15][28], d[15][29],\
               d[15][30], d[15][31]],\
              [d[16][0], d[16][1], d[16][2], d[16][3], d[16][4], d[16][5],\
               d[16][6], d[16][7], d[16][8], d[16][9], d[16][10], d[16][11],\
               d[16][12], d[16][13], d[16][14], d[16][15], d[16][16], d[16][17],\
               d[16][18], d[16][19], d[16][20], d[16][21], d[16][22], d[16][23],\
               d[16][24], d[16][25], d[16][26], d[16][27], d[16][28], d[16][29],\
               d[16][30], d[16][31]],\
              [d[17][0], d[17][1], d[17][2], d[17][3], d[17][4], d[17][5],\
               d[17][6], d[17][7], d[17][8], d[17][9], d[17][10], d[17][11],\
               d[17][12], d[17][13], d[17][14], d[17][15], d[17][16], d[17][17],\
               d[17][18], d[17][19], d[17][20], d[17][21], d[17][22], d[17][23],\
               d[17][24], d[17][25], d[17][26], d[17][27], d[17][28], d[17][29],\
               d[17][30], d[17][31]],\
              [d[18][0], d[18][1], d[18][2], d[18][3], d[18][4], d[18][5],\
               d[18][6], d[18][7], d[18][8], d[18][9], d[18][10], d[18][11],\
               d[18][12], d[18][13], d[18][14], d[18][15], d[18][16], d[18][17],\
               d[18][18], d[18][19], d[18][20], d[18][21], d[18][22], d[18][23],\
               d[18][24], d[18][25], d[18][26], d[18][27], d[18][28], d[18][29],\
               d[18][30], d[18][31]],\
              [d[19][0], d[19][1], d[19][2], d[19][3], d[19][4], d[19][5],\
               d[19][6], d[19][7], d[19][8], d[19][9], d[19][10], d[19][11],\
               d[19][12], d[19][13], d[19][14], d[19][15], d[19][16], d[19][17],\
               d[19][18], d[19][19], d[19][20], d[19][21], d[19][22], d[19][23],\
               d[19][24], d[19][25], d[19][26], d[19][27], d[19][28], d[19][29],\
               d[19][30], d[19][31]],\
              [d[23][0], d[23][1], d[23][2], d[23][3], d[23][4], d[23][5],\
               d[23][6], d[23][7], d[20][8], d[20][9], d[20][10], d[20][11],\
               d[20][12], d[20][13], d[20][14], d[20][15], d[20][16], d[20][17],\
               d[20][18], d[20][20], d[20][20], d[20][21], d[20][22], d[20][23],\
               d[20][24], d[20][25], d[20][26], d[20][27], d[20][28], d[20][29],\
               d[20][30], d[20][31]],\
              [d[21][0], d[21][1], d[21][2], d[21][3], d[21][4], d[21][5],\
               d[21][6], d[21][7], d[21][8], d[21][9], d[21][10], d[21][11],\
               d[21][12], d[21][13], d[21][14], d[21][15], d[21][16], d[21][17],\
               d[21][18], d[21][19], d[21][20], d[21][21], d[21][22], d[21][23],\
               d[21][24], d[21][25], d[21][26], d[21][27], d[21][28], d[21][29],\
               d[21][30], d[21][31]],\
              [d[22][0], d[22][1], d[22][2], d[22][3], d[22][4], d[22][5],\
               d[22][6], d[22][7], d[22][8], d[22][9], d[22][10], d[22][11],\
               d[22][12], d[22][13], d[22][14], d[22][15], d[22][16], d[22][17],\
               d[22][18], d[22][19], d[22][20], d[22][21], d[22][22], d[22][23],\
               d[22][24], d[22][25], d[22][26], d[22][27], d[22][28], d[22][29],\
               d[22][30], d[22][31]],\
              [d[23][0], d[23][1], d[23][2], d[23][3], d[23][4], d[23][5],\
               d[23][6], d[23][7], d[23][8], d[23][9], d[23][10], d[23][11],\
               d[23][12], d[23][13], d[23][14], d[23][15], d[23][16], d[23][17],\
               d[23][18], d[23][19], d[23][20], d[23][21], d[23][22], d[23][23],\
               d[23][24], d[23][25], d[23][26], d[23][27], d[23][28], d[23][29],\
               d[23][30], d[23][31]],\
              [d[24][0], d[24][1], d[24][2], d[24][3], d[24][4], d[24][5],\
               d[24][6], d[24][7], d[24][8], d[24][9], d[24][10], d[24][11],\
               d[24][12], d[24][13], d[24][14], d[24][15], d[24][16], d[24][17],\
               d[24][18], d[24][19], d[24][20], d[24][21], d[24][22], d[24][23],\
               d[24][24], d[24][25], d[24][26], d[24][27], d[24][28], d[24][29],\
               d[24][30], d[24][31]],\
              [d[25][0], d[25][1], d[25][2], d[25][3], d[25][4], d[25][5],\
               d[25][6], d[25][7], d[25][8], d[25][9], d[25][10], d[25][11],\
               d[25][12], d[25][13], d[25][14], d[25][15], d[25][16], d[25][17],\
               d[25][18], d[25][19], d[25][20], d[25][21], d[25][22], d[25][23],\
               d[25][24], d[25][25], d[25][26], d[25][27], d[25][28], d[25][29],\
               d[25][30], d[25][31]],\
              [d[26][0], d[26][1], d[26][2], d[26][3], d[26][4], d[26][5],\
               d[26][6], d[26][7], d[26][8], d[26][9], d[26][10], d[26][11],\
               d[26][12], d[26][13], d[26][14], d[26][15], d[26][16], d[26][17],\
               d[26][18], d[26][19], d[26][20], d[26][21], d[26][22], d[26][23],\
               d[26][24], d[26][25], d[26][26], d[26][27], d[26][28], d[26][29],\
               d[26][30], d[26][31]],\
              [d[27][0], d[27][1], d[27][2], d[27][3], d[27][4], d[27][5],\
               d[27][6], d[27][7], d[27][8], d[27][9], d[27][10], d[27][11],\
               d[27][12], d[27][13], d[27][14], d[27][15], d[27][16], d[27][17],\
               d[27][18], d[27][19], d[27][20], d[27][21], d[27][22], d[27][23],\
               d[27][24], d[27][25], d[27][26], d[27][27], d[27][28], d[27][29],\
               d[27][30], d[27][31]],\
              [d[28][0], d[28][1], d[28][2], d[28][3], d[28][4], d[28][5],\
               d[28][6], d[28][7], d[28][8], d[28][9], d[28][10], d[28][11],\
               d[28][12], d[28][13], d[28][14], d[28][15], d[28][16], d[28][17],\
               d[28][18], d[28][19], d[28][20], d[28][21], d[28][22], d[28][23],\
               d[28][24], d[28][25], d[28][26], d[28][27], d[28][28], d[28][29],\
               d[28][30], d[28][31]],\
              [d[29][0], d[29][1], d[29][2], d[29][3], d[29][4], d[29][5],\
               d[29][6], d[29][7], d[29][8], d[29][9], d[29][10], d[29][11],\
               d[29][12], d[29][13], d[29][14], d[29][15], d[29][16], d[29][17],\
               d[29][18], d[29][19], d[29][20], d[29][21], d[29][22], d[29][23],\
               d[29][24], d[29][25], d[29][26], d[29][27], d[29][28], d[29][29],\
               d[29][30], d[29][31]],\
              [d[30][0], d[30][1], d[30][2], d[30][3], d[30][4], d[30][5],\
               d[30][6], d[30][7], d[30][8], d[30][9], d[30][10], d[30][11],\
               d[30][12], d[30][13], d[30][14], d[30][15], d[30][16], d[30][17],\
               d[30][18], d[30][19], d[30][20], d[30][21], d[30][22], d[30][23],\
               d[30][24], d[30][25], d[30][26], d[30][27], d[30][28], d[30][29],\
               d[30][30], d[30][31]],\
              [d[31][0], d[31][1], d[31][2], d[31][3], d[31][4], d[31][5],\
               d[31][6], d[31][7], d[31][8], d[31][9], d[31][10], d[31][11],\
               d[31][12], d[31][13], d[31][14], d[31][15], d[31][16], d[31][17],\
               d[31][18], d[31][19], d[31][20], d[31][21], d[31][22], d[31][23],\
               d[31][24], d[31][25], d[31][26], d[31][27], d[31][28], d[31][29],\
               d[31][30], d[31][31]],\
              [d[32][0], d[32][1], d[32][2], d[32][3], d[32][4], d[32][5],\
               d[32][6], d[32][7], d[32][8], d[32][9], d[32][10], d[32][11],\
               d[32][12], d[32][13], d[32][14], d[32][15], d[32][16], d[32][17],\
               d[32][18], d[32][19], d[32][20], d[32][21], d[32][22], d[32][23],\
               d[32][24], d[32][25], d[32][26], d[32][27], d[32][28], d[32][29],\
               d[32][30], d[32][31]],\
              [d[33][0], d[33][1], d[33][2], d[33][3], d[33][4], d[33][5],\
               d[33][6], d[33][7], d[33][8], d[33][9], d[33][10], d[33][11],\
               d[33][12], d[33][13], d[33][14], d[33][15], d[33][16], d[33][17],\
               d[33][18], d[33][19], d[33][20], d[33][21], d[33][22], d[33][23],\
               d[33][24], d[33][25], d[33][26], d[33][27], d[33][28], d[33][29],\
               d[33][30], d[33][31]],\
              [d[34][0], d[34][1], d[34][2], d[34][3], d[34][4], d[34][5],\
               d[34][6], d[34][7], d[34][8], d[34][9], d[34][10], d[34][11],\
               d[34][12], d[34][13], d[34][14], d[34][15], d[34][16], d[34][17],\
               d[34][18], d[34][19], d[34][20], d[34][21], d[34][22], d[34][23],\
               d[34][24], d[34][25], d[34][26], d[34][27], d[34][28], d[34][29],\
               d[34][30], d[34][31]],\
              [d[35][0], d[35][1], d[35][2], d[35][3], d[35][4], d[35][5],\
               d[35][6], d[35][7], d[35][8], d[35][9], d[35][10], d[35][11],\
               d[35][12], d[35][13], d[35][14], d[35][15], d[35][16], d[35][17],\
               d[35][18], d[35][19], d[35][20], d[35][21], d[35][22], d[35][23],\
               d[35][24], d[35][25], d[35][26], d[35][27], d[35][28], d[35][29],\
               d[35][30], d[35][31]],\
              [d[36][0], d[36][1], d[36][2], d[36][3], d[36][4], d[36][5],\
               d[36][6], d[36][7], d[36][8], d[36][9], d[36][10], d[36][11],\
               d[36][12], d[36][13], d[36][14], d[36][15], d[36][16], d[36][17],\
               d[36][18], d[36][19], d[36][20], d[36][21], d[36][22], d[36][23],\
               d[36][24], d[36][25], d[36][26], d[36][27], d[36][28], d[36][29],\
               d[36][30], d[36][31]],\
              [d[37][0], d[37][1], d[37][2], d[37][3], d[37][4], d[37][5],\
               d[37][6], d[37][7], d[37][8], d[37][9], d[37][10], d[37][11],\
               d[37][12], d[37][13], d[37][14], d[37][15], d[37][16], d[37][17],\
               d[37][18], d[37][19], d[37][20], d[37][21], d[37][22], d[37][23],\
               d[37][24], d[37][25], d[37][26], d[37][27], d[37][28], d[37][29],\
               d[37][30], d[37][31]],\
              [d[38][0], d[38][1], d[38][2], d[38][3], d[38][4], d[38][5],\
               d[38][6], d[38][7], d[38][8], d[38][9], d[38][10], d[38][11],\
               d[38][12], d[38][13], d[38][14], d[38][15], d[38][16], d[38][17],\
               d[38][18], d[38][19], d[38][20], d[38][21], d[38][22], d[38][23],\
               d[38][24], d[38][25], d[38][26], d[38][27], d[38][28], d[38][29],\
               d[38][30], d[38][31]],\
              [d[39][0], d[39][1], d[39][2], d[39][3], d[39][4], d[39][5],\
               d[39][6], d[39][7], d[39][8], d[39][9], d[39][10], d[39][11],\
               d[39][12], d[39][13], d[39][14], d[39][15], d[39][16], d[39][17],\
               d[39][18], d[39][19], d[39][20], d[39][21], d[39][22], d[39][23],\
               d[39][24], d[39][25], d[39][26], d[39][27], d[39][28], d[39][29],\
               d[39][30], d[39][31]],\
              [d[40][0], d[40][1], d[40][2], d[40][3], d[40][4], d[40][5],\
               d[40][6], d[40][7], d[40][8], d[40][9], d[40][10], d[40][11],\
               d[40][12], d[40][13], d[40][14], d[40][15], d[40][16], d[40][17],\
               d[40][18], d[40][19], d[40][20], d[40][21], d[40][22], d[40][23],\
               d[40][24], d[40][25], d[40][26], d[40][27], d[40][28], d[40][29],\
               d[40][30], d[40][31]],\
              [d[41][0], d[41][1], d[41][2], d[41][3], d[41][4], d[41][5],\
               d[41][6], d[41][7], d[41][8], d[41][9], d[41][10], d[41][11],\
               d[41][12], d[41][13], d[41][14], d[41][15], d[41][16], d[41][17],\
               d[41][18], d[41][19], d[41][20], d[41][21], d[41][22], d[41][23],\
               d[41][24], d[41][25], d[41][26], d[41][27], d[41][28], d[41][29],\
               d[41][30], d[41][31]]])

        filename = 'temp/tempzdata.txt'
        tempfile = open(filename, 'w')

        for x in range(h.shape[0]):
            for y in range(h.shape[1]):
                tempfile.write(str(z[x][y])+' ')
            tempfile.write('\n')

        tempfile.close()

def readgraph(y, f, mce_file_name):
    h = f.Read(row_col=True, unfilter='DC').data
    delete_file = ["rm %s" %(mce_file_name)] #to keep temp files from piling up in memory
    subprocess.Popen(delete_file,shell=True)

    chfile = open('tempfiles/tempchannel.txt', 'r')
    ch = int(chfile.read().strip())
    #T = range(h.shape[0])
    if len(y) < 5000:
        y.append(h[:,ch]) #should output every row, and only 1 channel or column for all frame data
    else:
        y = y[1000:]

    filename = 'tempfiles/tempgraphdata.txt'
    tempfile = open(filename, 'a')

    for i in range(len(y)):
        tempfile.write(str(y[i])+' ')
    tempfile.close()
    return y

if __name__ =="__main__":
    takedataall(sys.argv[1])
