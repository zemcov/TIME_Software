import pyqtgraph as pg
from pyqtgraph import QtCore, QtGui
import numpy as np
import sys
import datetime
import os
import subprocess
import time

class mcegui(QtGui.QWidget):
    def __init__(self):
        super(mcegui, self).__init__()
        self.init_mce()
        self.init_ui()
        self.qt_connections()


    def init_mce(self):
        for i in range(2):
            tempfilename = 'tempfiles/tempgraphdata%s.txt' % (i)
            tempfile = os.path.exists(tempfilename)
            if tempfile:
                delete_file = ['rm ' + tempfilename]
                subprocess.Popen(delete_file,shell=True)
        self.observer = ''
        self.datamode = ''
        self.readoutcard = ''
        self.framenumber = ''
        self.frameperfile = 374
        self.totaltimeinterval = 10
        self.timeinterval = 1

    def init_ui(self):
        self.setWindowTitle('MCE TIME Data')
        self.getparameters()
        self.channelselection()
        self.grid = QtGui.QGridLayout()
        self.grid.addLayout(self.parametersquit, 1, 1)
        self.setLayout(self.grid)

        #self.plotwidget = pg.PlotWidget()
        #self.grid.addWidget(self.plotwidget, 1, 3, 1, 2)

        self.grid.addLayout(self.channelbox, 2, 2)

        #self.setGeometry(10, 10, 1000, 600)
        self.show()

    def qt_connections(self):
        self.quitbutton.clicked.connect(self.on_quitbutton_clicked)
        self.submitbutton.clicked.connect(self.on_submitbutton_clicked)
        self.selectchannel.currentIndexChanged.connect(self.changechannel)

    def on_quitbutton_clicked(self):
        print('Quitting Application')
        run = ['mce_cmd -x stop rc%s ret_dat' %(self.readoutcard)]
        a = subprocess.Popen(run, shell=True)
        deletetemp = ['rm /data/cryo/current_data/temp.*']
        b = subprocess.Popen(deletetemp, shell=True)
        self.runmce.terminate()
        sys.exit()

    def on_submitbutton_clicked(self):
        self.observer = self.enterobserver.text()
        self.datamode = self.enterdatamode.currentText()
        if self.datamode == 'Error':
            self.datamode = 0
        elif self.datamode == 'Raw':
            self.datamode = 12
        elif self.datamode == 'Low Pass Filtered':
            self.datamode = 2
        elif self.datamode == 'Mixed Mode':
            self.datamode = 10
        elif self.datamode == 'SQ1 Feedback':
            self.datamode = 1
        self.readoutcard = self.enterreadoutcard.currentIndex() + 1
        self.framenumber = self.enterframenumber.text()
        if self.observer == '' or self.framenumber == '' or self.framenumber == '0':
            self.parameterwarning = QtGui.QMessageBox()
            self.parameterwarning.setIcon(QtGui.QMessageBox.Warning)
            self.parameterwarning.setText('One or more parameters not entered correctly!')
            self.parameterwarning.setStandardButtons(QtGui.QMessageBox.Ok)
            self.parameterwarning.setWindowTitle('Parameter Warning')
            self.parameterwarning.buttonClicked.connect(self.on_warningbutton_clicked)
            self.parameterwarning.exec_()

        else:
            parafile = open('tempfiles/tempparameters.txt', 'w')
            parafile.write(self.observer+' ')
            parafile.write(str(self.datamode)+' ')
            parafile.write(str(self.readoutcard)+' ')
            parafile.write(self.framenumber+' ')
            parafile.close()

            parameteroutput = QtGui.QVBoxLayout()

            self.observertext = QtGui.QLabel()
            self.datamodetext = QtGui.QLabel()
            self.readoutcardtext = QtGui.QLabel()
            self.framenumbertext = QtGui.QLabel()

            self.observertext.setText('Observer: %s' % (self.observer))
            self.datamodetext.setText('Datamode: %s' % (self.datamode))
            self.readoutcardtext.setText('Readout Card: %s' % (self.readoutcard))
            self.framenumbertext.setText('Frame Number: %s' % (self.framenumber))

            parameteroutput.addWidget(self.observertext)
            parameteroutput.addWidget(self.datamodetext)
            parameteroutput.addWidget(self.readoutcardtext)
            parameteroutput.addWidget(self.framenumbertext)

            self.grid.addLayout(parameteroutput, 1, 2)

            print('Observer: %s' % (self.observer))
            print('Datamode: %s' % (self.datamode))
            print('Readout Card: %s' % (self.readoutcard))
            print('Frame Number: %s' % (self.framenumber))

            self.initplot()

    def on_warningbutton_clicked(self):
        self.observer = ''
        self.datamode = ''
        self.readoutcard = ''
        self.framenumber = ''

    def getparameters(self):
        self.parametersquit = QtGui.QVBoxLayout()

        self.enterobserver = QtGui.QLineEdit()
        self.enterdatamode = QtGui.QComboBox()
        self.enterdatamode.addItems(['Error', 'Raw', 'Low Pass Filtered', 'Mixed Mode', 'SQ1 Feedback'])
        self.enterreadoutcard = QtGui.QComboBox()
        for i in range(8):
            if i < 4:
                self.enterreadoutcard.addItem('MCE 1 RC %s' % (i % 4 + 1))
            else:
                self.enterreadoutcard.addItem('MCE 2 RC %s' % (i % 4 + 1))
        self.enterframenumber = QtGui.QLineEdit()
        self.submitbutton = QtGui.QPushButton('Submit')

        self.parameters = QtGui.QFormLayout()
        self.parameters.addRow('Observer', self.enterobserver)
        self.parameters.addRow('Datamode', self.enterdatamode)
        self.parameters.addRow('Readout Card', self.enterreadoutcard)
        self.parameters.addRow('Frame Number', self.enterframenumber)
        self.parameters.addRow(self.submitbutton)

        self.parametersquit.addLayout(self.parameters)

        self.quitbutton = QtGui.QPushButton('Quit')
        self.parametersquit.addWidget(self.quitbutton)

    def channelselection(self):
        tempfile = open('tempfiles/tempchannel.txt', 'w')
        tempfile.write('1')
        tempfile.close()

        self.channelbox = QtGui.QVBoxLayout()

        self.selectchannel = QtGui.QComboBox()
        self.selectchannel.addItems(['1', '2', '3', '4', '5', '6', '7', '8'])

        self.channelbox.addWidget(self.selectchannel)

    def changechannel(self):
        tempfile = open('tempfiles/tempchannel.txt', 'w')
        tempfile.write(self.selectchannel.currentText())
        tempfile.close()
        print(self.selectchannel.currentText())

    def initplot(self):
        changedatamode = ["mce_cmd -x wb rc%s data_mode %s" % (self.readoutcard, self.datamode)]
        b = subprocess.Popen(changedatamode, shell=True)
        run = ["mce_run temp %s %s --sequence=%s" %(self.framenumber, self.readoutcard, self.frameperfile)]
        c = subprocess.Popen(run, shell=True)

        if self.readoutcard == 'All':
            self.runmce = subprocess.Popen(['python', 'takedataall.py', self.observer])
        else:
            self.runmce = subprocess.Popen(['python', 'takedata.py', self.observer])

        self.n_intervals = 1
        self.data = [0, 0, 0]

        self.mcegraphdata = pg.ScatterPlotItem()
        #self.plotwidget.addItem(self.mcegraph)
        self.graphwin = pg.GraphicsWindow()
        self.graphwin.setWindowTitle('MCE TIME Data')

        self.mcegraph = self.graphwin.addPlot()

        self.mcegraph.setLabel('bottom', 'Time', 's')
        self.mcegraph.setLabel('left', 'Counts')
        self.mcegraph.setTitle('MCE TIME Data')

        self.updateplot()

        self.timer = pg.QtCore.QTimer()
        self.timer.timeout.connect(self.moveplot)
        self.timer.start(1000 * self.timeinterval)

    def moveplot(self):
        self.n_intervals+=self.timeinterval
        self.updateplot()

    def updateplot(self):
        while not os.path.isfile('tempfiles/tempgraphdata%s.txt' % (0)):
            time.sleep(0.1)
        tempfile = open('tempfiles/tempgraphdata%s.txt' % (0), 'r')
        ch = tempfile.readline().strip()
        if not ch:
            ch = 1
        else:
            ch = int(ch)
        a = tempfile.readline().strip()
        print('gui', str(self.n_intervals), a)
        a = int(a)
        #if a > self.n_intervals:
        #    self.n_intervals = a
        datagrab = tempfile.readline().strip().split()
        #xy = []
        pointcolor = []
        x = []
        y = []
        for i in range(self.frameperfile):
            #point = []
            masterx = i / (self.frameperfile * 1.0)
            #point.append(self.n_intervals + masterx - 1)
            x.append(self.n_intervals + masterx - 1)
            #point.append(float(datagrab[i]))
            y.append(float(datagrab[i]))
            #xy.append(point)
            if ch == 1:
                pointcolor.append(pg.mkBrush('b'))
            elif ch == 2:
                pointcolor.append(pg.mkBrush('r'))
            elif ch == 3:
                pointcolor.append(pg.mkBrush('g'))
            elif ch == 4:
                pointcolor.append(pg.mkBrush('y'))
            elif ch == 5:
                pointcolor.append(pg.mkBrush('c'))
            elif ch == 6:
                pointcolor.append(pg.mkBrush('m'))
            elif ch == 7:
                pointcolor.append(pg.mkBrush('k'))
            elif ch == 8:
                pointcolor.append(pg.mkBrush('w'))

        tempfile.close()
        #data[0].extend(ch)
        if self.n_intervals == 1:
            self.data[0] = pointcolor
            self.data[1] = x
            self.data[2] = y
        else:
            self.data[0].extend(pointcolor)
            #self.data[1] = x
            #self.data[2] = y
            self.data[1].extend(x)
            self.data[2].extend(y)

        if self.n_intervals > self.totaltimeinterval:
            self.data[0] = self.data[0][self.frameperfile:]
            self.data[1] = self.data[1][self.frameperfile:]
            self.data[2] = self.data[2][self.frameperfile:]
            #if self.n_intervals > self.totaltimeinterval + 1:
            #    self.data[0] = self.data[0][374:]
            #    self.data[1] = self.data[1][374:]
            #    self.data[2] = self.data[2][374:]
        print(len(self.data[0]))
        print(len(self.data[1]))
        print(len(self.data[2]))
            #p1.setPos(n_intervals)
        pointcolor = self.data[0]
        x = self.data[1]
        y = self.data[2]
        x = np.asarray(x)
        y = np.asarray(y)
        #self.plotwidget.setLabel('bottom', 'Time', 's')
        #self.plotwidget.setLabel('left', 'Counts')
        #self.plotwidget.setTitle('MCE TIME Data')
        if self.n_intervals == 1:
            self.mcegraph.addItem(self.mcegraphdata)
            self.mcegraphdata.setData(x, y)
            self.mcegraphdata.setBrush(pointcolor)
        else:
            self.mcegraphdata.setData(x, y)
            self.mcegraphdata.setBrush(pointcolor)
            #if self.n_intervals > self.totaltimeinterval:
                #x_axis = pg.AxisItem('bottom', parent=self.mcegraph)
                #x_axis.setRange(self.n_intervals - self.totaltimeinterval, self.n_intervals)
                #self.data[0] = self.data[0][self.frameperfile:]

def main():
    app = QtGui.QApplication(sys.argv)
    app.setApplicationName('MCE TIME Data')
    ex = mcegui()
    sys.exit(app.exec_())


if __name__ == '__main__':
    main()
