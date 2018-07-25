from pyqtgraph import QtCore, QtGui
import numpy as np
import sys
import datetime
import os
import subprocess
import time
import pyqtgraph as pg
import takedata as td
import takedataall as tda
import random as rm
import netcdf_trial as nc
import settings as st
import socket, struct, threading
sys.path.append('/data/cryo/current_data')

#class of all components of GUI
class mcegui(QtGui.QWidget):
    #initializes mcegui class and calls other init functions
    def __init__(self):
        super(mcegui, self).__init__()
        self.init_mce()
        self.init_ui()
        self.qt_connections()

    #sets all of the variables for mce/graph, deletes old gui_data_test files
    def init_mce(self):
        tempfiledir = os.path.expanduser('~/Desktop/mce_files')
        if os.path.exists(tempfiledir):
            print('Hello!')
        else:
            mce_dir = ["mkdir ~/Desktop/mce_files"] #% (self.datamode)]
            subprocess.Popen(mce_dir, shell=True)

        self.timeinterval = 1
        #deleting old gui_data_test files
        #for i in range(len(os.listdir('tempfiles'))):
        #    tempfilename = 'tempfiles/gui_data_test%s.nc' % (i)
        #    tempfile = os.path.exists(tempfilename)
        #    if tempfile:
        #        delete_file = ['rm ' + tempfilename]
        #        subprocess.Popen(delete_file,shell=True)
        #setting all variables
        self.observer = ''
        self.datamode = ''
        self.readoutcard = ''
        self.framenumber = ''
        self.frameperfile = 374
        self.totaltimeinterval = 120
        self.currentchannel = 1
        self.row = 1
        self.oldch = 1
        #self.row
        st.init()

    #creates GUI window and calls functions to populate GUI
    def init_ui(self):
        self.setWindowTitle('MCE TIME Data')
        self.getparameters()
        self.grid = QtGui.QGridLayout()
        self.grid.addLayout(self.parametersquit, 1, 1, 1, 1)
        self.setLayout(self.grid)
        self.setGeometry(10, 10, 1920, 1080)
        self.show()

    #reacts to button presses and other GUI user input
    def qt_connections(self):
        self.quitbutton.clicked.connect(self.on_quitbutton_clicked)
        self.submitbutton.clicked.connect(self.on_submitbutton_clicked)
        self.selectchannel.currentIndexChanged.connect(self.changechannel)
        self.readoutcardselect.currentIndexChanged.connect(self.changereadoutcard)
        self.selectrow.currentIndexChanged.connect(self.changerow)

    #quits out of GUI and stops the MCE
    def on_quitbutton_clicked(self):
        print('Quitting Application')
        #stop mce with subprocess
        if self.readoutcard == 'All':
            run = ['mce_cmd -x stop rcs ret_dat']
        else:
            run = ['mce_cmd -x stop rc%s ret_dat' %(self.readoutcard)]
        a = subprocess.Popen(run, shell=True)
        #delete all MCE temp files still in directory
        deletetemp = ['rm /data/cryo/current_data/temp.*']
        b = subprocess.Popen(deletetemp, shell=True)

        self.runtele.terminate()

        runteleserver = './runteleserver.sh stop'
        run = subprocess.Popen(runteleserver, shell=True)


        #tempfilename = 'tempfiles/quittele.txt'
        #tempfile = open(tempfilename, 'w')
        #tempfile.write('Close')
        #tempfile.close()


        sys.exit()

    #sets parameter variables to user input and checks if valid - will start MCE
    #and live graphing if they are
    def on_submitbutton_clicked(self):
        #set variables to user input
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
        if self.readoutcard == 9:
            self.readoutcard = 'All'
            self.currentreadoutcard = 2
            self.currentreadoutcarddisplay = 'MCE 1 RC 2'
        self.framenumber = self.enterframenumber.text()
        self.datarate = self.enterdatarate.text()
        self.timeinterval = self.entertimeinterval.text()
        self.channeldelete = self.enterchanneldelete.currentText()
        self.showmcedata = self.entershowmcedata.currentText()
        self.timestarted = datetime.datetime.utcnow()
        self.timestarted = self.timestarted.isoformat()
        #check if parameters are valid - will create warning box if invalid
        if self.observer == '' or self.framenumber == '' or self.framenumber == '0'\
        or self.datarate == '0' or self.datarate == '' or self.timeinterval == ''\
        or self.timeinterval == '0':
            self.parameterwarning = QtGui.QMessageBox()
            self.parameterwarning.setIcon(QtGui.QMessageBox.Warning)
            self.parameterwarning.setText('One or more parameters not entered correctly!')
            self.parameterwarning.setStandardButtons(QtGui.QMessageBox.Ok)
            self.parameterwarning.setWindowTitle('Parameter Warning')
            self.parameterwarning.buttonClicked.connect(self.on_warningbutton_clicked)
            self.parameterwarning.exec_()
        elif self.showmcedata == 'No':
            self.submitbutton.setEnabled(False)
            self.inittelescope()
        else:
            parafile = open('tempfiles/tempparameters.txt', 'w')
            parafile.write(self.observer+' ')
            parafile.write(str(self.datamode)+' ')
            parafile.write(str(self.readoutcard)+' ')
            parafile.write(self.framenumber+' ')
            parafile.write(self.datarate+' ')
            parafile.write(self.timeinterval+' ')
            parafile.write(self.channeldelete+' ')
            parafile.write(self.timestarted+' ')
            parafile.close()

            #editdatarate = ['mce_cmd -x wb cc data_rate %s' % (self.datarate)]
            editdatarate = ['./mce1_cdr.sh %s' %(self.datarate)], shell=True)
            a = subprocess.call(editdatarate, shell=True)

            parameteroutput = QtGui.QVBoxLayout()

            self.observertext = QtGui.QLabel()
            self.datamodetext = QtGui.QLabel()
            self.readoutcardtext = QtGui.QLabel()
            self.framenumbertext = QtGui.QLabel()
            self.dataratetext = QtGui.QLabel()
            self.timeintervaltext = QtGui.QLabel()
            self.channeldeletetext = QtGui.QLabel()
            self.timestartedtext = QtGui.QLabel()

            self.observertext.setText('Observer: %s' % (self.observer))
            self.datamodetext.setText('Datamode: %s' % (self.datamode))
            self.readoutcardtext.setText('Readout Card: %s' % (self.readoutcard))
            self.framenumbertext.setText('Frame Number: %s' % (self.framenumber))
            self.dataratetext.setText('Data Rate: %s' % (self.datarate))
            self.timeintervaltext.setText('Time Interval: %s' % (self.timeinterval))
            self.channeldeletetext.setText('Delete Old Columns: %s' % (self.channeldelete))
            self.timestartedtext.setText('Time Started: %s' % (self.timestarted))


            parameteroutput.addWidget(self.observertext)
            parameteroutput.addWidget(self.datamodetext)
            parameteroutput.addWidget(self.readoutcardtext)
            if self.readoutcard == 'All':
                self.currentreadoutcardtext = QtGui.QLabel()
                self.currentreadoutcardtext.setText('Current Readout Card: %s' % (self.currentreadoutcarddisplay))
                parameteroutput.addWidget(self.currentreadoutcardtext)
            parameteroutput.addWidget(self.framenumbertext)
            parameteroutput.addWidget(self.dataratetext)
            parameteroutput.addWidget(self.timeintervaltext)
            parameteroutput.addWidget(self.channeldeletetext)
            parameteroutput.addWidget(self.timestartedtext)

            self.grid.addLayout(parameteroutput, 2, 1, 1, 1)

            self.channelselection()

            # print('Observer: %s' % (self.observer))
            # print('Datamode: %s' % (self.datamode))
            # print('Readout Card: %s' % (self.readoutcard))
            # print('Frame Number: %s' % (self.framenumber))
            # print('Data Rate: %s' % (self.datarate))
            # print('Time Interval: %s' % (self.timeinterval))
            # print('Delete Old Columns: %s' % (self.channeldelete))
            print('Time Started: %s' % (self.timestarted))

            self.frameperfile = (50 * 10 ** 6) / (33 * 90 * int(self.datarate))
            print('Frame per file: %s' % (self.frameperfile))

            self.submitbutton.setEnabled(False)

            self.initplot()

            #self.inittelescope()

    #resets parameter variables after warning box is read
    def on_warningbutton_clicked(self):
        self.observer = ''
        self.datamode = ''
        self.readoutcard = ''
        self.framenumber = ''

    #creates inputs for user to enter parameters and creates 'Quit' button
    def getparameters(self):
        self.parametersquit = QtGui.QVBoxLayout()

        #creating user input boxes
        self.enterobserver = QtGui.QLineEdit('JMB')
        self.enterobserver.setMaxLength(3)
        self.enterdatamode = QtGui.QComboBox()
        self.enterdatamode.addItems(['Error', 'Raw', 'Low Pass Filtered', 'Mixed Mode', 'SQ1 Feedback'])
        self.enterreadoutcard = QtGui.QComboBox()
        for i in range(8):
            if i < 4:
                self.enterreadoutcard.addItem('MCE 1 RC %s' % (i % 4 + 1))
            else:
                self.enterreadoutcard.addItem('MCE 2 RC %s' % (i % 4 + 1))
        self.enterreadoutcard.addItem('All')
        self.enterframenumber = QtGui.QLineEdit('1350000')
        self.enterframenumber.setMaxLength(9)
        self.enterdatarate = QtGui.QLineEdit('45')
        self.entertimeinterval = QtGui.QLineEdit('120')
        self.enterchanneldelete = QtGui.QComboBox()
        self.enterchanneldelete.addItems(['No', 'Yes'])
        self.entershowmcedata = QtGui.QComboBox()
        self.entershowmcedata.addItems(['Yes', 'No'])
        self.submitbutton = QtGui.QPushButton('Submit')

        self.parameters = QtGui.QFormLayout()
        self.parameters.addRow('Observer', self.enterobserver)
        self.parameters.addRow('Datamode', self.enterdatamode)
        self.parameters.addRow('Readout Card', self.enterreadoutcard)
        self.parameters.addRow('Frame Number', self.enterframenumber)
        self.parameters.addRow('Data Rate', self.enterdatarate)
        self.parameters.addRow('Delete Old Columns', self.enterchanneldelete)
        self.parameters.addRow('Time Interval (s)', self.entertimeinterval)
        self.parameters.addRow('Show MCE Data', self.entershowmcedata)
        self.parameters.addRow(self.submitbutton)

        self.parametersquit.addLayout(self.parameters)

        #creating quit button
        self.quitbutton = QtGui.QPushButton('Quit')
        self.parametersquit.addWidget(self.quitbutton)

        self.readoutcardselect = QtGui.QComboBox()
        self.selectchannel = QtGui.QComboBox()
        self.selectrow = QtGui.QComboBox()


    def inittelescope(self):
        #return
        tempfilename = 'tempfiles/quittele.txt'
        tempfile = open(tempfilename, 'w')
        tempfile.write('Open')
        tempfile.close()
        self.telescopewindow = QtGui.QWidget()
        self.telescopewindow.setWindowTitle('Telescope Data')
        self.inittelescopedata()
        self.telegrid = QtGui.QGridLayout()
        self.telegrid.addLayout(self.telescopedata, 1, 1, 1, 1)
        self.telegrid.addWidget(self.altazgraph, 1, 2, 2, 2)
        self.telegrid.addWidget(self.radecgraph, 1, 4, 2, 2)
        self.telescopewindow.setGeometry(50, 50, 100, 100)
        self.telescopewindow.setLayout(self.telegrid)
        self.telescopewindow.show()

        self.teletimer = pg.QtCore.QTimer()
        self.teletimer.timeout.connect(self.updatetelescopedata)
        self.teletimer.start(1000)


    def inittelescopedata(self):
        #self.teleintervals = 1
        altazcolor = pg.mkBrush('b')
        radeccolor = pg.mkBrush('r')
        #return
        runtelecollect = 'python readteledata.py'
        self.runtele = subprocess.Popen(runtelecollect, shell=True)

        runteleserver = './runteleserver.sh start'
        run = subprocess.Popen(runteleserver, shell=True)

        tempfile = open('tempfiles/tempteledata.txt', 'r')
        while not os.path.exists('tempfiles/tempteledata.txt'):
            time.sleep(0.1)
        teledata = tempfile.read().strip().split()

        print(teledata)

        self.telescopedata = QtGui.QVBoxLayout()
        self.telescopetest = QtGui.QLabel('Hello!')
        self.telescopedata.addWidget(self.telescopetest)

        self.altazgraph = pg.PlotWidget()
        self.altazgraphdata = pg.ScatterPlotItem()
        self.altazgraph.addItem(self.altazgraphdata)
        self.altazgraph.showGrid(x=True, y=True)
        self.altazgraph.setTitle('Alt-Az Graph')
        self.altazgraph.setLabel('left', 'alt')
        self.altazgraph.setLabel('bottom', 'az')

        self.radecgraph = pg.PlotWidget()
        self.radecgraphdata = pg.ScatterPlotItem()
        self.radecgraph.addItem(self.radecgraphdata)
        self.radecgraph.showGrid(x=True, y=True)
        self.radecgraph.setTitle('Ra-Dec Graph')
        self.radecgraph.setLabel('left', 'DEC (deg)')
        self.radecgraph.setLabel('bottom', 'RA (deg)')

        alt = [float(teledata[2])]
        az = [float(teledata[3])]

        dec = [float(teledata[5])]
        ra = [float(teledata[4])]

        #print(az, alt)

        self.altazgraphdata.setData(x=az, y=alt, brush=altazcolor)
        self.radecgraphdata.setData(x=ra, y=dec, brush=radeccolor)

        self.patext = QtGui.QLabel('PA: %s' % teledata[0])
        self.slewtext = QtGui.QLabel('Slew Flag: %s' % teledata[1])
        self.alttext = QtGui.QLabel('Alt: %s'%teledata[2])
        self.aztext = QtGui.QLabel('Az: %s'%teledata[3])
        self.ratext = QtGui.QLabel('RA: %s'%teledata[4])
        self.dectext = QtGui.QLabel('Dec: %s'%teledata[5])
        self.timetext = QtGui.QLabel('UTC Time: %s'%teledata[6])

        self.telescopedata.addWidget(self.patext)
        self.telescopedata.addWidget(self.slewtext)
        self.telescopedata.addWidget(self.alttext)
        self.telescopedata.addWidget(self.aztext)
        self.telescopedata.addWidget(self.ratext)
        self.telescopedata.addWidget(self.dectext)
        self.telescopedata.addWidget(self.timetext)


    def updatetelescopedata(self):
        tempfile = open('tempfiles/tempteledata.txt', 'r')
        if os.path.exists('tempfiles/tempteledata.txt'):
            teledata = tempfile.read().strip().split()

        #self.teleintervals += 1
        '''
        if self.teleintervals % 8 == 1:
            telecolor = pg.mkBrush('b')
        elif self.teleintervals % 8 == 2:
            telecolor = pg.mkBrush('r')
        elif self.teleintervals % 8 == 3:
            telecolor = pg.mkBrush('g')
        elif self.teleintervals % 8 == 4:
            telecolor = pg.mkBrush('y')
        elif self.teleintervals % 8 == 5:
            telecolor = pg.mkBrush('c')
        elif self.teleintervals % 8 == 6:
            telecolor = pg.mkBrush('m')
        elif self.teleintervals % 8 == 7:
            telecolor = pg.mkBrush('k')
        elif self.teleintervals % 8 == 0:
            telecolor = pg.mkBrush('w')
        '''
        telecolor = pg.mkBrush('b')
        radeccolor = pg.mkBrush('r')

        self.patext.setText('PA: %s' % teledata[0])
        self.slewtext.setText('Slew Flag: %s' % teledata[1])
        self.alttext.setText('Alt: %s'%teledata[2])
        self.aztext.setText('Az: %s'%teledata[3])
        self.ratext.setText('RA: %s'%teledata[4])
        self.dectext.setText('Dec: %s'%teledata[5])
        self.timetext.setText('UTC Time: %s'%teledata[6])

        alt = [float(teledata[2])]
        az = [float(teledata[3])]
        dec = [float(teledata[5])]
        ra = [float(teledata[4])]

        #print(az, alt)

        self.altazgraphdata.addPoints(x=az, y=alt, brush=telecolor)
        self.radecgraphdata.addPoints(x=ra, y=dec, brush=radeccolor)




        #print(teledata)

    #creates input to change channel of live graph during operation, also adds
    #input for readout card if reading All readout cards
    def channelselection(self):
        self.channelreadoutbox = QtGui.QFormLayout()

        #adds readout card dropbox if All
        if self.readoutcard == 'All':
            for i in range(32):
                self.selectchannel.addItem(str(i))
        else:
            self.selectchannel.addItems(['0', '1', '2', '3', '4', '5', '6', '7'])
        #creates channel dropbox

        for i in range(33):
            self.selectrow.addItem(str(i))

        self.channellabel = QtGui.QLabel('Column')

        self.rowlabel = QtGui.QLabel('Row')

        self.channelreadoutbox.addRow(self.channellabel, self.selectchannel)

        self.channelreadoutbox.addRow(self.rowlabel, self.selectrow)

        self.grid.addLayout(self.channelreadoutbox, 3, 1, 1, 1)

    #changes channel of live graph when user changes channel
    def changechannel(self):
        self.currentchannel = int(self.selectchannel.currentText()) + 1
        if self.readoutcard == 'All':
	           self.changereadoutcard()
        #print(self.currentchannel)


    def changerow(self):
        self.row = int(self.selectrow.currentText()) + 1
        print(self.row)

    #changes readout card of live graph when user changes readout card
    def changereadoutcard(self):
    	if self.currentchannel < 9:
    	   self.currentreadoutcard = 1
    	   self.currentreadoutcarddisplay = 'MCE 1 RC 1'
    	elif self.currentchannel >= 9 and self.currentchannel < 17:
    	   self.currentreadoutcard = 2
    	   self.currentreadoutcarddisplay = 'MCE 1 RC 2'
    	elif self.currentchannel >= 17 and self.currentchannel < 25:
    	   self.currentreadoutcard = 3
    	   self.currentreadoutcarddisplay = 'MCE 1 RC 3'
    	elif self.currentchannel >= 25:
    	   self.currentreadoutcard = 4
    	   self.currentreadoutcarddisplay = 'MCE 1 RC 4'
    	self.currentreadoutcardtext.setText('Current Readout Card: %s' % (self.currentreadoutcarddisplay))
            #self.currentreadoutcarddisplay = self.readoutcardselect.currentText()

    #adds location for K-mirror data, currently has place holder data
    def initkmirrordata(self):
        #place holder data
        self.parallacticangle = rm.randint(10, 170)
        self.positionalerror = rm.randint(0, 90)

        self.parallacticangletext = QtGui.QLabel()
        self.positionalerrortext = QtGui.QLabel()

        self.parallacticangletext.setText('Parallactic Angle: %s' % (self.parallacticangle))
        self.positionalerrortext.setText('Positonal Error: %s' % (self.positionalerror))

        self.kmirrordatatext = QtGui.QVBoxLayout()

        self.kmirrordatatext.addWidget(self.parallacticangletext)
        self.kmirrordatatext.addWidget(self.positionalerrortext)

        self.grid.addLayout(self.kmirrordatatext, 4, 1, 1, 1)

    #update K-mirror data with new place holder data
    def updatekmirrordata(self):
        self.parallacticangle = rm.randint(10, 170)
        self.positionalerror = rm.randint(0, 90)

        self.parallacticangletext.setText('Parallactic Angle: %s' % (self.parallacticangle))
        self.positionalerrortext.setText('Positonal Error: %s' % (self.positionalerror))

    #initializes graph for live viewing of data
    def initplot(self):
        #counts number of files in current_data for later checks of number of
        #temp files
        self.n_files = len(os.listdir("/data/cryo/current_data"))
        print(self.n_files)
        #changes commands to start mce if All readout cards are to be read
        if self.readoutcard == 'All':
            changedatamode1 = ["./mce1_cdm.sh a %s" % (self.datamode)]
            b = subprocess.Popen(changedatamode1, shell=True)
            run1 = ["./mce1_run.sh %s a %s" %(self.framenumber, self.frameperfile)]
            c = subprocess.Popen(run1, shell=True)
            #changedatamode2 = ["./mce1_cdm.sh %s" % (self.datamode)]
            #d = subprocess.Popen(changedatamode2, shell=True)
            #run2 = ["./mce1_run.sh %s a %s" %(self.framenumber, self.frameperfile)]
            #e = subprocess.Popen(run2, shell=True)
        else:
            changedatamode1 = ["./mce1_cdm.sh %s %s" % (self.readoutcard, self.datamode)]
            b = subprocess.Popen(changedatamode1, shell=True)
            run1 = ["./mce1_run.sh %s %s %s" %(self.framenumber, self.readoutcard, self.frameperfile)]
            c = subprocess.Popen(run1, shell=True)
            #changedatamode2 = ["./mce1_cdm.sh %s %s" % (self.readoutcard, self.datamode)]
            #d = subprocess.Popen(changedatamode2, shell=True)
            #run2 = ["./mce1_run.sh %s %s %s" %(self.framenumber, self.readoutcard, self.frameperfile)]
            #e = subprocess.Popen(run2, shell=True)

        #initialize time
        self.n_intervals = 1
        self.starttime = datetime.datetime.utcnow()
        self.totaltimeinterval = int(self.timeinterval)

        #create new netCDF4 file
        #self.mce = nc.new_file(st.n, self.frameperfile)

        self.mce = 1
        #calls takedata or takedata depending on 1 or all readout cards respectfully,
        #passes variables to let takedata/takedataall correctly parse data and
        #gets data for graohing back
        if self.readoutcard == 'All':
            self.z, self.allgraphdata, self.mce = tda.takedataall(self.n_intervals, self.currentchannel, self.currentreadoutcard, self.n_files, self.frameperfile, self.mce, \
            self.row)
        else:
            self.z, self.allgraphdata, self.mce = td.takedata(self.n_intervals, self.currentchannel, self.n_files, self.frameperfile, self.mce, self.row)

        #initalize data list
        self.data = [0, 0, 0]

        #initialize graph GUI item
        self.mcegraphdata = pg.ScatterPlotItem()
    	self.mcegraph = pg.PlotWidget()
    	self.grid.addWidget(self.mcegraph, 1, 5, 2, 3)

        #add labels to graph
        self.mcegraph.setLabel('bottom', 'Time', 's')
        self.mcegraph.setLabel('left', 'Counts')
        self.mcegraph.setTitle('MCE TIME Data')

        #initalize old data graph GUI item and add labels
        self.oldmcegraph = pg.PlotWidget()
        self.oldmcegraphdata = pg.PlotCurveItem()
        self.grid.addWidget(self.oldmcegraph, 1, 2, 2, 3)
        self.oldmcegraph.setLabel('bottom', 'Time', 's')
        self.oldmcegraph.setLabel('left', 'Counts')
        self.oldmcegraph.setTitle('Old MCE TIME Data')
        self.oldmcegraph.addItem(self.oldmcegraphdata)

        #call other init functions and begin updating graph
        self.initheatmap()
        self.initkmirrordata()
        self.initfftgraph()
        self.updateplot()

        #timer for updating graph
        self.timer = pg.QtCore.QTimer()
        self.timer.timeout.connect(self.moveplot)
        self.timer.start(1000)

    #updates 'clock' (n_intervals) and recalls takedata/takedataall, also calls
    #update functions
    def moveplot(self):
        self.n_intervals+=int(1)

        self.starttime = datetime.datetime.utcnow()

        if self.readoutcard == 'All':
            self.z, self.allgraphdata, self.mce = tda.takedataall(self.n_intervals, self.currentchannel, self.currentreadoutcard, self.n_files, self.frameperfile, self.mce,\
            self.row)
        else:
            self.z, self.allgraphdata, self.mce = td.takedata(self.n_intervals, self.currentchannel, self.n_files, self.frameperfile, self.mce, self.row)

        self.updateheatmap()
        self.updatekmirrordata()
        self.updatefftgraph()
        self.updateplot()

    #writes and updates data to both live graph and old graph
    def updateplot(self):
        #determines number of updates needed based on how many tempfiles were read
        #allgraphdata's length is based on the number of tempfiles takedata read
    	for g in range(len(self.allgraphdata)):
            #take out data from allgraphdata
    	    self.graphdata = self.allgraphdata[g]
            a = self.graphdata[0]
            ch = self.graphdata[1]
            y = self.graphdata[2][:self.frameperfile]
            self.y = y
            #visual watchdog to make sure everything is in-sync with everything else
            print('gui %s %s' % (self.n_intervals, a))
            #creates x values for current time interval and colors points based
            #on current channel
            pointcolor = []
            pointsymbol = []
            x = []
            for i in range(self.frameperfile):
                #create x value
                masterx = i / (self.frameperfile * 1.0)
                x.append(self.n_intervals + masterx - 1)
                #picks color based on current channel
                if ch % 8 == 1:
                    pointcolor.append(pg.mkBrush('b'))
                elif ch % 8 == 2:
                    pointcolor.append(pg.mkBrush('r'))
                elif ch % 8 == 3:
                    pointcolor.append(pg.mkBrush('g'))
                elif ch % 8 == 4:
                    pointcolor.append(pg.mkBrush('y'))
                elif ch % 8 == 5:
                    pointcolor.append(pg.mkBrush('c'))
                elif ch % 8 == 6:
                    pointcolor.append(pg.mkBrush('m'))
                elif ch % 8 == 7:
                    pointcolor.append(pg.mkBrush('k'))
                elif ch % 8 == 0:
                    pointcolor.append(pg.mkBrush('w'))
                if self.readoutcard == 'All':
                    if self.currentreadoutcard % 4 == 1:
                        pointsymbol.append('o')
                    elif self.currentreadoutcard % 4 == 2:
                        pointsymbol.append('s')
                    elif self.currentreadoutcard % 4 == 3:
                        pointsymbol.append('t')
                    elif self.currentreadoutcard % 4 == 0:
                        pointsymbol.append('d')
            self.x = x
            #initializes old data list on either the first update or the first one after
            #the current total time interval, otherwise adds to current list
            if self.n_intervals == 1 or self.n_intervals % self.totaltimeinterval == 2:
                self.data[0] = x
                self.data[1] = y
            else:
                self.data[0].extend(x)
                self.data[1].extend(y)
            #recasts x, y as arrays for updating the graph data
            x = np.asarray(x)
            y = np.asarray(y)
            #creates graphdata item on first update
            if self.n_intervals == 1:
                self.mcegraph.addItem(self.mcegraphdata)
                self.mcegraph.setXRange(self.n_intervals - 1, self.n_intervals + self.totaltimeinterval - 1, padding=0)
                if self.readoutcard == 'All':
                    self.mcegraphdata.setData(x, y, brush=pointcolor, symbol=pointsymbol)
                else:
                    self.mcegraphdata.setData(x, y, brush=pointcolor)
                self.oldch = ch
            #clears graphdata and updates old graph after the total time interval
            #has passed
            elif self.n_intervals % self.totaltimeinterval == 1:
                self.oldmcegraph.setXRange(self.data[0][0], self.data[0][-1], padding=0)
                self.oldmcegraphdata.setData(self.data[0], self.data[1])
                self.mcegraphdata.clear()
                self.mcegraph.setXRange(self.n_intervals - 1, self.n_intervals + self.totaltimeinterval - 1, padding=0)
                if self.readoutcard == 'All':
                    self.mcegraphdata.setData(x, y, brush=pointcolor, symbol=pointsymbol)
                else:
                    self.mcegraphdata.setData(x, y, brush=pointcolor)
                self.data = [0, 0, 0]
            #updates graph, if channel delete is set to yes will clear data first
            else:
                if self.channeldelete == 'Yes' and self.oldch != ch:
                    self.mcegraphdata.clear()
                    if self.readoutcard == 'All':
                        self.mcegraphdata.setData(x, y, brush=pointcolor, symbol=pointsymbol)
                    else:
                        self.mcegraphdata.setData(x, y, brush=pointcolor)
                else:
                    if self.readoutcard == 'All':
                        self.mcegraphdata.addPoints(x, y, brush=pointcolor, symbol=pointsymbol)
                    else:
                        self.mcegraphdata.addPoints(x, y, brush=pointcolor)
            self.oldch = ch
            #watchdog for time to update graph/heatmap/K-mirror data
            self.endtime = datetime.datetime.utcnow()
            self.timetaken = self.endtime - self.starttime
            #if updating multiple intervals, add to n_intervals to keep time in-sync
    	    if len(self.allgraphdata) > 1 and g != len(self.allgraphdata) - 1:
                self.n_intervals += 1
            print('Time taken: %s' % (self.timetaken))

    #initialize heatmap
    def initheatmap(self):
        #casts z as array for creating heatmap
        z = np.asarray(self.z)
        #recasting data in z as integers
        z.astype(int)
        #creating heatmap, labeling
        self.heatmapplot = pg.PlotItem()
        self.heatmapplot.setLabel('bottom', 'Row')
        self.heatmapplot.setLabel('left', 'Channel')
        #self.heatmapplot.setXRange(0, 8, padding=0)
        #self.heatmapplot.setYRange(0, 32, padding=0)
        self.heatmap = pg.ImageView(view= self.heatmapplot)
        self.heatmap.setPredefinedGradient('thermal')
        self.heatmap.setImage(z)
        #changes levels for heatmap to create gradient at depending on the data rate
        print(z)
        self.avggrad = int(np.average(z))
        self.stddevgrad = int(np.std(z))
        print('heatmap average: %s' % (self.avggrad))
        print('std dev grad %s' % (self.stddevgrad))
        self.heatmap.setLevels(self.avggrad - (3 * self.stddevgrad), self.avggrad + (3 * self.stddevgrad))
        # if self.frameperfile == 11:
        #     self.heatmap.setLevels(60, 260)
        # else:
        #     self.heatmap.setLevels(100, 190)
        self.grid.addWidget(self.heatmap, 3, 2, 2, 3)

    #updates heatmap
    def updateheatmap(self):
        #casts z as array for creating heatmap
        z = np.asarray(self.z)
        #recasting data in z as integers
        z.astype(int)
        self.heatmap.setImage(z)
        #changes levels for heatmap to create gradient at depending on the data rate
        self.heatmap.setLevels(self.avggrad - (3 * self.stddevgrad), self.avggrad + (3 * self.stddevgrad))
        # if self.frameperfile == 11:
        #     self.heatmap.setLevels(60, 260)
        # else:
        #     self.heatmap.setLevels(100, 190)


    def initfftgraph(self):
        self.fftgraph = pg.PlotWidget()
        self.fftgraphdata = pg.ScatterPlotItem()
        self.fftgraph.addItem(self.fftgraphdata)

        self.fftgraph.setLabel('bottom', 'Time', 's')
        self.fftgraph.setLabel('left', 'Counts')
        self.fftgraph.setTitle('FFT Data')

        self.grid.addWidget(self.fftgraph, 3, 5, 2, 3)


    def updatefftgraph(self):
        self.fftdata = np.fft.fft(self.y)

        self.fftdata = np.asarray(self.fftdata, dtype=np.float32)

        #print(self.fftdata)

        self.fftdata[0] = self.fftdata[1]

        self.fftgraphdata.setData(self.x, self.fftdata)


#calls mcegui class to start GUI
def main():
    app = QtGui.QApplication(sys.argv)
    app.setApplicationName('MCE TIME Data')
    ex = mcegui()
    sys.exit(app.exec_())


if __name__ == '__main__':
    main()
