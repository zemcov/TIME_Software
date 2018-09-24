import pyqtgraph as pg
from pyqtgraph.Qt import QtCore, QtGui
import numpy as np
import sys
import datetime
import os
import subprocess
import time

global n_intervals
n_intervals = 1

class mcegui(QtGui.QWidget):

    def __int__(self):
        super(Parameters, self).__init__()

        self.initUI()

    def initUI(self):
        qbtn = QtGui.QPushButton('Quit', self)
        qbtn.clicked.connect(quitgui)
        qbth.resize(qbth.sizeHint())
        qbtn.move(50, 50)

        self.setGeometry(300, 300, 250, 150)
        self.setWindowTitle('MCE TIME Data!')
        self.show()

def quitgui():
    readoutcard = sys.argv[3]
    run = ['mce_cmd -x stop rc%s ret_dat' %(readoutcard)]
    a = subprocess.Popen(run, shell=True)
    deletetemp = ['rm /data/cryo/current_data/temp.*']
    b = subprocess.Popen(deletetemp, shell=True)

for i in range(2):
    tempfilename = 'tempfiles/tempgraphdata%s.txt' % (i)
    tempfile = os.path.exists(tempfilename)
    if tempfile:
        delete_file = ['rm ' + tempfilename]
        subprocess.Popen(delete_file,shell=True)

observer = sys.argv[1]
datamode = sys.argv[2]
readoutcard = sys.argv[3]
framenumber = sys.argv[4]
changedatamode = ["mce_cmd -x wb rc%s data_mode %s" % (readoutcard, datamode)]
b = subprocess.Popen(changedatamode, shell=True)
#a.communicate()
#subprocess.call(["mkfifo", "/data/cryo/current_data/temp"])
run = ["mce_run temp %s %s --sequence=374" %(framenumber, readoutcard)]
c = subprocess.Popen(run, shell=True)

tempfile = open('tempfiles/tempchannel.txt', 'w')
tempfile.write(str(1))
tempfile.close()

if sys.argv[3] == 'All':
    heatmap = subprocess.Popen(['python', 'takedataall.py', sys.argv[1]])
else:
    heatmap = subprocess.Popen(['python', 'takedata.py', sys.argv[2]])
#parafile = open('tempfiles/tempparameters.txt', 'w')
#for parameter in parameters:
#    parafile.write(str(parameter)+' ')

win = pg.GraphicsWindow()
win.setWindowTitle('MCE TIME Data')
qbtn = QtGui.QPushButton('Quit')
qbtn.clicked.connect(quitgui)

totaltimeinterval = 30
timeinterval = 1
if n_intervals == 1:
    data = [0, 0]

while not os.path.isfile('tempfiles/tempgraphdata%s.txt' % (0)):
    time.sleep(0.1)
tempfile = open('tempfiles/tempgraphdata%s.txt' % (0), 'r')
#z = [[ [] for i in range(32)] for j in range(32)]
ch = int(tempfile.readline().strip())
datagrab = tempfile.readline().strip().split()
smallx = []
smally = []
xy = []
for i in range(374):
    point = []
    masterx = i / 374.0
    point.append(n_intervals + masterx - 1)
    smallx.append(n_intervals + masterx - 1)
    point.append(float(datagrab[i]))
    smally.append(float(datagrab[i]))
    xy.append(point)
tempfile.close()
#allx.append(smallx)
#ally.append(smally)
#print(len(x_axis), len(y_data))

if n_intervals == 1:
    data[0] = [ch]
    data[1] = xy

p1 = win.addPlot(colspan=2)
p1.setLabel('bottom', 'Time', 's')
p1.setLabel('left', 'Counts')
curve1 = p1.plot(smallx, smally)
ptr1 = 1
def update1():
    global data, curve1, ptr1
    ptr1 += 1
    n_intervals = ptr1
    totaltimeinterval = 30
    timeinterval = 1
    print('gui', n_intervals)
    while not os.path.isfile('tempfiles/tempgraphdata%s.txt' % (0)):
        time.sleep(0.1)
    tempfile = open('tempfiles/tempgraphdata%s.txt' % (0), 'r')
    ch = int(tempfile.readline().strip())
    datagrab = tempfile.readline().strip().split()
    xy = []
    for i in range(374):
        point = []
        masterx = i / 374.0
        point.append(n_intervals + masterx - 1)
        point.append(float(datagrab[i]))
        xy.append(point)
    tempfile.close()
    #print(len(x_axis), len(y_data))
    #data[0].extend(ch)
    data[1].extend(xy)
    if n_intervals > totaltimeinterval:
        data[1] = data[1][374:]
        print(len(data[1]))
        #p1.setPos(n_intervals)
    xy = data[1]
    xy = np.asarray(xy)
    curve1.setData(xy)

def update():
    update1()
timer = pg.QtCore.QTimer()
timer.timeout.connect(update)
timer.start(1000)

if __name__ == '__main__':
    import sys
    if (sys.flags.interactive != 1) or not hasattr(QtCore, 'PYQT_VERSION'):
        QtGui.QApplication.instance().exec_()
