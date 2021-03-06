from pyqtgraph import QtCore, QtGui
import pyqtgraph as Qt
import numpy as np
import sys, os, subprocess, time, datetime, socket, struct, threading
import pyqtgraph as pg
import random as rm
from termcolor import colored
import multiprocessing as mp
import read_files_local as rf
import utils as ut
import fake_tel_server as ft

#class of all components of GUI
class mcegui(QtGui.QWidget):
    #initializes mcegui class and calls other init functions
    def __init__(self, parent = None):
        super(mcegui, self).__init__(parent)
        self.init_mce()
        self.init_ui()
        self.qt_connections()

    #sets all of the variables for mce/graph, deletes old gui_data_test files
    def init_mce(self):
        self.timeinterval = 1
        self.observer = ''
        self.datamode = ''
        self.readoutcard = ''
        self.framenumber = ''
        self.frameperfile = 374
        self.totaltimeinterval = 120
        self.currentchannel = 1
        self.row = 1
        self.oldch = 1
        self.graphdata1 = []
        self.z1 = 0
        self.n_interval = 0

    #creates GUI window and calls functions to populate GUI
    def init_ui(self):
        self.setWindowTitle('TIME Live Data Visualization Suite')
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
        self.starttel.clicked.connect(self.on_starttel_clicked)
        self.selectchannel.currentIndexChanged.connect(self.changechannel)
        self.readoutcardselect.currentIndexChanged.connect(self.changereadoutcard)
        self.selectrow.currentIndexChanged.connect(self.changerow)

    def on_quitbutton_clicked(self):
        ut.mce_exit.set()
        ut.tel_exit.set()
        ut.kms_exit.set()
        ut.hk_exit.set()
        print('Quitting Application')
        sys.exit()

    def on_starttel_clicked(self):
        print('Setting Telescope Observing Parameters')
    #sets parameter variables to user input and checks if valid - will start MCE
    #and live graphing if they are
    def on_submitbutton_clicked(self):
        # check if telescope has been started first
        if not self.starttel.isEnabled() :
            print("Please Initialize Telescope First")
            self.submitbutton.setEnabled(False)

        #set variables to user input
        # observer ---------------------------------------
        self.observer = self.enterobserver.text()

        # data mode --------------------------------------
        self.datamode = self.enterdatamode.currentText()
        mce_states = ['Error', 'Raw', 'Filtered SQ1 Feedback', 'Debugging', 'Mixed Mode (25:7)','Mixed Mode (22:10)','Mixed Mode (24:8)','Mixed mode (18:14)']
        mce_states2 = [0,12,2,11,10,7,5,4]
        for state in mce_states :
            if self.datamode == state :
                self.datamode = mce_states2[mce_states.index(state)]

        # readout card ---------------------------------------------
        self.readoutcard = self.enterreadoutcard.currentIndex() + 1
        if self.readoutcard == 9:
            self.readoutcard = 'All'
            self.currentreadoutcard = 2
            self.currentreadoutcarddisplay = 'MCE 1 RC 2'

        # frame number ----------------------------------------------
        self.framenumber = self.enterframenumber.text()

        # data rate -------------------------------------------------
        self.datarate = self.enterdatarate.text()

        # how much data to view on screen at once -------------------
        self.timeinterval = self.entertimeinterval.text()

        # keep old channel data on graph ----------------------------
        self.channeldelete = self.enterchanneldelete.currentText()

        # keep mce data on screen -----------------------------------
        self.showmcedata = self.entershowmcedata.currentText()

        # time keepers ----------------------------------------------
        self.timestarted = datetime.datetime.utcnow()
        self.timestarted = self.timestarted.isoformat()

        self.inittel = self.init_tel.currentText()

        if self.inittel == 'Yes':
            self.inittelescope()
        else :
            pass

        #check if parameters are valid - will create warning box if invalid
        if self.observer == '' or self.framenumber == '' or self.framenumber == '0'\
        or self.datarate == '0' or self.datarate == '' or self.timeinterval == ''\
        or self.timeinterval == '0':
            self.warningbox('gui') # throw up a warning box
            ''' should probably also add something in to restart the gui main form screen '''
        elif self.showmcedata == 'No':
            self.submitbutton.setEnabled(False)
        else:
            dir = 'Desktop/Gui_Code/TIME_Software/main'
            if os.path.exists(dir + 'tempfiles/tempparameters.txt') :
                parafile = open(dir + 'tempfiles/tempparameters.txt', 'w')
                parafile.write(self.observer+' ')
                parafile.write(str(self.datamode)+' ')
                parafile.write(str(self.readoutcard)+' ')
                parafile.write(self.framenumber+' ')
                parafile.write(self.datarate+' ')
                parafile.write(self.timeinterval+' ')
                parafile.write(self.channeldelete+' ')
                parafile.write(self.timestarted+' ')
                parafile.close()

            self.channelselection()
            print(colored('Time Started: %s' % (self.timestarted),'magenta'))
            self.p = int((50 * 10 ** 6) / (33 * 90 * int(self.datarate))) #calculation taken from UBC MCE Wiki

            # prevents user from re-activating everything
            self.submitbutton.setEnabled(False)

            #start other plot making processes
            self.initplot()
            self.initfftgraph()
            self.initkmirrordata()

    #resets parameter variables after warning box is read
    def on_warningbutton_clicked(self):
        self.on_quitbutton_clicked()
    #creates inputs for user to enter parameters and creates 'Quit' button

    def getparameters(self):
        #creating user input boxes
        self.enterobserver = QtGui.QLineEdit('VLB')
        self.enterobserver.setMaxLength(3)
        self.enterdatamode = QtGui.QComboBox()
        self.enterdatamode.addItems(
            ['Error', 'Raw', 'Filtered SQ1 Feedback', 'Debugging', 'Mixed Mode (25:7)','Mixed Mode (22:10)','Mixed Mode (24:8)','Mixed mode (18:14)'])
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

        self.mceGroupBox = QtGui.QGroupBox("MCE Parameters")
        self.parameters = QtGui.QFormLayout()
        self.mcetitle = QtGui.QLabel(self)
        self.mcetitle.setAlignment(QtCore.Qt.AlignCenter)
        self.mcetitle.setText('MCE Parameters')
        self.parameters.addRow(self.mcetitle)
        self.parameters.addRow('Observer', self.enterobserver)
        self.parameters.addRow('Datamode', self.enterdatamode)
        self.parameters.addRow('Readout Card', self.enterreadoutcard)
        self.parameters.addRow('Frame Number', self.enterframenumber)
        self.parameters.addRow('Data Rate', self.enterdatarate)
        self.parameters.addRow('Delete Old Columns', self.enterchanneldelete)
        self.parameters.addRow('Time Interval (s)', self.entertimeinterval)
        self.parameters.addRow('Show MCE Data', self.entershowmcedata)
        self.parameters.addRow(self.submitbutton)
        self.mceGroupBox.setLayout(self.parameters)

        # telescope options =================================================
        self.telescan = QtGui.QComboBox()
        self.telescan.addItems(['1D','2D','BowTie (constant el)'])

        self.tel_delay = QtGui.QLineEdit('0')

        self.init_tel = QtGui.QComboBox()
        self.init_tel.addItems(['No','Yes'])



        self.telGroupBox = QtGui.QGroupBox("Telescope Parameters")
        self.telparams = QtGui.QFormLayout()
        self.teltitle = QtGui.QLabel(self)
        self.teltitle.setAlignment(QtCore.Qt.AlignCenter)
        self.teltitle.setText('Telescope Parameters')
        self.telparams.addRow(self.teltitle)
        self.telparams.addRow('Activate Telescope', self.init_tel)
        self.telparams.addRow('Scan Strategy', self.telescan)
        self.telparams.addRow('Delayed Start (sec)', self.tel_delay)
        self.starttel = QtGui.QPushButton('Initialize Telescope')
        self.telparams.addRow(self.starttel)
        self.telGroupBox.setLayout(self.telparams)
        # =====================================================================
        self.parametersquit = QtGui.QVBoxLayout()
        self.parametersquit.setAlignment(QtCore.Qt.AlignCenter)
        self.parametersquit.addWidget(self.telGroupBox)
        self.parametersquit.addWidget(self.mceGroupBox)
        self.quitbutton = QtGui.QPushButton('Quit')
        self.parametersquit.addWidget(self.quitbutton)

        self.readoutcardselect = QtGui.QComboBox()
        self.selectchannel = QtGui.QComboBox()
        self.selectrow = QtGui.QComboBox()

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
    	# self.currentreadoutcard.setText('Current Readout Card: %s' % (self.currentreadoutcarddisplay))
        # self.currentreadoutcarddisplay = self.readoutcardselect.currentText()

    def initplot(self):
        #initialize graph objects & graph time scales
        self.starttime = datetime.datetime.utcnow()
        # passes the variable set by the user to the graph (user sets timeinterval)
        self.totaltimeinterval = int(self.timeinterval)
        self.n_intervals = 1 # resets after graph reaches edge

        self.mce = 1

        #initalize data list
        ''' This is meant to store old data '''
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

        # connecting thread functions
        self.updater = MyThread()
        self.updater.new_data.connect(self.updateplot)
        self.updater.start()

    def initheatmap(self,z1):
        #casts z as array for creating heatmap
        # z1 = np.asarray(z1)
        #z2 = np.asarray(self.z2)
        #recasting data in z as integers
        # z1.astype(int)
        #z2.astype(int)

        self.heatmapplot = pg.PlotItem()
        self.heatmapplot.setLabel('bottom', 'Row')
        self.heatmapplot.setLabel('left', 'Channel')
        self.heatmapplot.setTitle('MCE RMS Channel Noise')

        self.heatmap = pg.ImageView(view= self.heatmapplot)
        self.heatmap.setPredefinedGradient('thermal')
        self.heatmap.autoLevels()
        self.heatmap.setImage(z1)

        #changes levels for heatmap to create gradient at depending on the data rate
        self.avggrad = int(np.average(z1))
        self.stddevgrad = int(np.std(z1))
        # self.heatmap.setLevels(self.avggrad - (3 * self.stddevgrad), self.avggrad + (3 * self.stddevgrad))
        # self.grid.addWidget(self.heatmap, 3, 2, 2, 3)

        # create new window for hk and fft data
        self.heatmapwindow = QtGui.QWidget()
        self.heatmapwindow.setWindowTitle('MCE RMS Noise Map')
        self.heatgrid = QtGui.QGridLayout()
        self.heatgrid.addWidget(self.heatmap, 3, 2, 2, 3)
        self.heatmapwindow.setGeometry(10, 10, 1920, 1080)
        self.heatmapwindow.setLayout(self.heatgrid)
        self.heatmapwindow.show()

    def initfftgraph(self):
        self.fftgraph = pg.PlotWidget()
        self.fftgraphdata = pg.ScatterPlotItem()
        self.fftgraph.addItem(self.fftgraphdata)

        self.fftgraph.setLabel('bottom', 'Time', 's')
        self.fftgraph.setLabel('left', 'Counts')
        self.fftgraph.setTitle('FFT Data')

        self.grid.addWidget(self.fftgraph, 3, 2, 4, 6)

    def initkmirrordata(self):
        # start the kms QThread
        ''' Add back in once KMS is running '''
        # self.kms_updater = KMS_Thread()
        # self.kms_updater.new_kms_data.connect(self.updatekmirrordata)
        # self.kms_updater.start()

        #place holder data
        self.parallacticangle = rm.randint(10, 170)
        self.positionalerror = rm.randint(0, 90)
        self.kmsstatus = 'Normal'

        self.parallacticangletext = QtGui.QLabel('Parallactic Angle: %s' %(self.parallacticangle))
        self.parallacticangletext.setAlignment(QtCore.Qt.AlignCenter)
        self.positionalerrortext = QtGui.QLabel('Positional Error: %s' %(self.positionalerror))
        self.positionalerrortext.setAlignment(QtCore.Qt.AlignCenter)
        self.kmsstatustext = QtGui.QLabel('KMS Status Flag: %s' %(self.kmsstatus))
        self.kmsstatustext.setAlignment(QtCore.Qt.AlignCenter)
        self.kmstitle = QtGui.QLabel('Kmirror System Position and Status')
        self.kmstitle.setAlignment(QtCore.Qt.AlignCenter)

        self.kmsgui = QtGui.QWidget()
        self.kmsFrame = QtGui.QFrame()
        self.kmsFrame.setStyleSheet("background-color: blue;")
        self.kmsFrame.setFrameShape(QtGui.QFrame.StyledPanel)
        self.kmsFrame.setFrameShadow(QtGui.QFrame.Raised)
        self.kmsparams = QtGui.QVBoxLayout()
        self.kmsparams.addWidget(self.kmsFrame)
        self.kmsparams.addWidget(self.kmstitle)
        self.kmsparams.addWidget(self.kmsstatustext)
        self.kmsparams.addWidget(self.parallacticangletext)
        self.kmsparams.addWidget(self.positionalerrortext)
        self.kmsgui.setLayout(self.kmsparams)
        self.grid.addWidget(self.kmsgui, 4, 1, 1, 1)

    def inittelescope(self):
        # start the telescope QThread
        self.tel_updater = Tel_Thread()
        self.tel_updater.new_tel_data.connect(self.updatetelescopedata)
        self.tel_updater.start()

        # initialize printouts of current tele values not plotted
        self.patext = QtGui.QLabel('PA: %s' %('-'))
        self.slewtext = QtGui.QLabel('Slew Flag: %s' %('-'))
        self.timetext = QtGui.QLabel('UTC Time: %s' %('-'))

        # create space for tele printout values
        self.telescopedata = QtGui.QVBoxLayout()
        self.telescopedata.addWidget(self.patext)
        self.telescopedata.addWidget(self.slewtext)
        self.telescopedata.addWidget(self.timetext)

        # create plot object for alt-az graph
        self.altazgraph = pg.PlotWidget()
        self.altazgraphdata = pg.ScatterPlotItem()
        self.altazgraph.addItem(self.altazgraphdata)
        self.altazgraph.showGrid(x=True, y=True)
        self.altazgraph.setTitle('Alt-Az Graph')
        self.altazgraph.setLabel('left', 'alt')
        self.altazgraph.setLabel('bottom', 'az')

        # create plot object for ra-dec graph
        self.radecgraph = pg.PlotWidget()
        self.radecgraphdata = pg.ScatterPlotItem()
        self.radecgraph.addItem(self.radecgraphdata)
        self.radecgraph.showGrid(x=True, y=True)
        self.radecgraph.setTitle('Ra-Dec Graph')
        self.radecgraph.setLabel('left', 'DEC (deg)')
        self.radecgraph.setLabel('bottom', 'RA (deg)')

        # create new window for telescope graphs
        self.telescopewindow = QtGui.QWidget()
        self.telescopewindow.setWindowTitle('Telescope Data')
        self.telegrid = QtGui.QGridLayout()
        self.telegrid.addLayout(self.telescopedata, 1, 1, 1, 1)
        self.telegrid.addWidget(self.altazgraph, 1, 2, 2, 2)
        self.telegrid.addWidget(self.radecgraph, 1, 4, 2, 2)
        self.telescopewindow.setGeometry(10, 10, 1920, 1080)
        self.telescopewindow.setLayout(self.telegrid)
        self.telescopewindow.show()

        self.repeat = False

    def updatekmirrordata(self,status):

        # error checking based on status flags from kmirror
        kms_error = [10,11,12,13]
        if (status in kms_error) and (self.repeat == False) :
            os.system("afplay /Users/vlb9398/Desktop/Gui_code/TIME_Software/main/klaxon.mp3")
            self.repeat = True
            ut.tel_exit.set()
            ut.mce_exit.set()
            ut.kms_exit.set()
            ut.hk_exit.set()
            self.warningbox(['kms',status])

        else :
            self.parallacticangle = rm.randint(10, 170)
            self.positionalerror = rm.randint(0, 90)

            self.parallacticangletext.setText('Parallactic Angle: %s' % (self.parallacticangle))
            self.positionalerrortext.setText('Positonal Error: %s' % (self.positionalerror))

    def updatefftgraph(self):
        # self.y and self.x are defined in updateplot
        self.fftdata = np.fft.fft(self.y)
        self.fftdata = np.asarray(self.fftdata, dtype=np.float32)
        self.fftdata[0] = self.fftdata[-1]
        self.fftgraphdata.setData(self.x, self.fftdata)

    def updatetelescopedata(self,pa,slew,alt,az,ra,dec,time):
        # error checking based on status flags from telescope
        tel_error = [10,11,12]
        if (slew in tel_error) and (self.repeat == False) :
            os.system("afplay /Users/vlb9398/Desktop/Gui_code/TIME_Software/main/klaxon.mp3")
            self.repeat = True
            ut.tel_exit.set()
            ut.mce_exit.set()
            ut.kms_exit.set()
            ut.hk_exit.set()
            self.warningbox(['tel',slew]) #slew will be replaced with tel status flag over socket

        else :
            # update text on window to reflect new data
            self.patext.setText('PA: %s' %(round(float(pa),2)))
            self.slewtext.setText('Slew Flag: %s' %(slew))
            self.timetext.setText('UTC Time: %s'%(round(float(time),2)))

            altazcolor = pg.mkBrush('b')
            radeccolor = pg.mkBrush('r')

            az = [float(az)]
            alt = [float(alt)]
            ra = [float(ra)]
            dec = [float(dec)]

            # if (self.index - 1) == 0 : # if it's the first data set, set data
            #     self.altazgraphdata.setData(x=[float(i) for i in az], y=[float(i) for i in alt], brush=altazcolor)
            #     self.radecgraphdata.setData(x=[float(i) for i in ra], y=[float(i) for i in dec], brush=radeccolor)
            # else : # if it's not the first update, don't remove existing points, but add more to graph
            self.altazgraphdata.addPoints(x=az, y=alt, brush=altazcolor)
            self.radecgraphdata.addPoints(x=ra, y=dec, brush=radeccolor)

    def updateplot(self,h1,index):
        self.index = index - 1 #because self.p gets updated before data is sent
        print(colored(index,'magenta'))

        # parsing mce array to make heatmap data ==================
        # d1 = np.empty([h1.shape[0],h1.shape[1]],dtype=float)
        # for b in range(h1.shape[0]):
        #     for c in range(h1.shape[1]):
        #         d1[b][c] = (np.std(h1[b][c][:],dtype=float))
        d1 = np.random.rand(41,32)
        # =========================================================

        # parsing mce array for graph data ========================
        g1 = h1[:,self.currentchannel - 1]
        array1 = []
        for j in range(g1.shape[1]):
            array1.append(g1[self.row - 1][j])
        self.graphdata1 = [self.currentchannel,array1]
        # =========================================================

        self.starttime = datetime.datetime.utcnow()

        # ============================================================================================
        ch = self.graphdata1[0]
        y = self.graphdata1[1][:self.frameperfile]
        self.y = y

        #creates x values for current time interval and colors points based on current channel ===
        x = []
        ''' Need a way to make end of time array be the actual amount of time it
            took to create that file '''
        self.endtime = datetime.datetime.utcnow()
        self.timetaken = self.endtime - self.starttime
        print(colored('Time taken: %s' % (self.timetaken.total_seconds()),'green'))
        x = np.linspace(self.index,self.index + self.timetaken.total_seconds(),self.frameperfile)
        self.x = x
        # =====================================================================================
        pointcolor = []
        pointsymbol = []
        #picks color based on current channel =============================================
        symbols = ['b','r','g','y','c','m','k','w']
        for i in range(7):
            if self.currentchannel == i :
                pointcolor.extend([pg.mkBrush(symbols[i]) for j in range(self.frameperfile)])
        # =================================================================================================================
        # changes symbols for viewing different RC cards on same plot =====================
        syms = ['d','o','s','t']
        for i in range(3):
            if self.currentreadoutcard == i :
                pointsymbol.extend([syms[i] for j in range(self.frameperfile)])
        #============================================================================================================
        #====================================================================================================

        #creates graphdata item on first update
        if self.index == 0:
            self.initheatmap(d1) # give first values for heatmap to create image scale
            self.updatefftgraph()
            self.data[0] = x
            self.data[1] = y
            self.mcegraph.addItem(self.mcegraphdata)
            self.mcegraph.setXRange(self.index, self.index + self.totaltimeinterval - 1, padding=0)
            if self.readoutcard == 'All':
                self.mcegraphdata.setData(x, y, brush=pointcolor, symbol=pointsymbol)
            else:
                self.mcegraphdata.setData(x, y, brush=pointcolor)
            self.oldch = self.currentchannel
            # updates oldgraph data
            self.data[0] = x
            self.data[1] = y
            self.n_interval += 1 # update to keep graph going
        # ===========================================================================================================
        #clears graphdata and updates old graph after the total time interval has passed
        elif self.n_interval == self.totaltimeinterval :
            self.data[0] = x
            self.data[1] = y
            self.oldmcegraph.setXRange(self.data[0][0], self.data[0][-1], padding=0)
            self.oldmcegraphdata.setData(self.data[0], self.data[1])
            self.mcegraphdata.clear()
            self.mcegraph.setXRange(self.index, self.index + self.totaltimeinterval - 1, padding=0)
            if self.readoutcard == 'All':
                self.mcegraphdata.setData(x, y, brush=pointcolor, symbol=pointsymbol)
            else:
                self.mcegraphdata.setData(x, y, brush=pointcolor)
            self.data = [0, 0, 0]
            # updates oldgraphdata after total time interval is reached
            self.data[0] = x
            self.data[1] = y
            self.n_interval = 0 #reset counter
        # ==============================================================================================================
        #updates graph, if channel delete is set to yes will clear data first
        else:
            self.updateheatmap(d1)
            self.updatefftgraph()
            if self.channeldelete == 'Yes' and self.oldch != self.currentchannel:
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
            # updates old data for when graph resets
            np.append(self.data[0],x) # doesn't create a new array but adds to existing
            np.append(self.data[1],y)
            self.n_interval += 1
        # =================================================================================================================
        self.oldch = self.currentchannel
        # =================================================================================================================

    def updateheatmap(self,z1):
        #casts z as array for creating heatmap
        # z1 = np.asarray(z1)
        #z2 = np.asarray(self.z2)
        #recasting data in z as integers
        # z1.astype(int)
        #z2.astype(int)
        self.heatmap.setImage(z1)
        #changes levels for heatmap to create gradient at depending on the data rate
        #self.heatmap.setLevels(self.avggrad - (3 * self.stddevgrad), self.avggrad + (3 * self.stddevgrad))
        # if self.frameperfile == 11:
        #     self.heatmap.setLevels(60, 260)
        # else:
        #     self.heatmap.setLevels(100, 190)


    def warningbox(self,message): # message is a tuple
        if message[0] == 'gui' :
            parameterwarning = QtGui.QMessageBox()
            parameterwarning.setIcon(QtGui.QMessageBox.Warning)
            parameterwarning.setText('Error %s: One or more parameters not entered correctly!' %(message[1]))
            parameterwarning.setStandardButtons(QtGui.QMessageBox.Ok)
            parameterwarning.setWindowTitle('Parameter Warning')
            parameterwarning.buttonClicked.connect(self.on_warningbutton_clicked)
            parameterwarning.exec_()
        if message[0] == 'kms' :
            kmswarning = QtGui.QMessageBox()
            kmswatning.setStyleSheet("background-color: rgb(255,0,0); color: rgb(0,0,0)")
            kmswarning.setIcon(QtGui.QMessageBox.Critical)
            kmswarning.setText('Error %s: System has halted due to Kmirror E-Stop. Please standby for user reset...' %(message[1]))
            kmswarning.setStandardButtons(QtGui.QMessageBox.Abort)
            kmswarning.setWindowTitle('KMirror System Emergency Stop!')
            kmswarning.buttonClicked.connect(self.on_warningbutton_clicked)
            kmswarning.exec_()
        elif message[0] == 'tel' :
            telwarning = QtGui.QMessageBox()
            telwarning.setStyleSheet("background-color: rgb(255,0,0); color: rgb(0,0,0)")
            telwarning.setIcon(QtGui.QMessageBox.Critical)
            telwarning.setText('Error %s : The telescope has unexpectedly halted normal operations. Software must be reset by user.' %(message[1]))
            telwarning.setStandardButtons(QtGui.QMessageBox.Abort)
            telwarning.setWindowTitle('Telescope Emergency Stop')
            telwarning.buttonClicked.connect(self.on_warningbutton_clicked)
            telwarning.exec_()
        elif message[0] == 'hk' :
            hkwarning = QtGui.QMessageBox()
            hkwarning.setStyleSheet("background-color: rgb(255,0,0); color: rgb(0,0,0)")
            hkwarning.setIcon(QtGui.QMessageBox.Critical)
            hkwarning.setText('Error %s: Housekeeping as reported an error. No files are being created.' %(message[1]))
            hkwarning.setStandardButtons(QtGui.QMessageBox.Abort)
            hkwarning.setWindowTitle('Housekeeping Error')
            hkwarning.buttonClicked.connect(self.on_warningbutton_clicked)
            hkwarning.exec_()

class MyThread(QtCore.QThread):

    new_data = QtCore.pyqtSignal(object,object)

    def __init__(self, parent = None):
        QtCore.QThread.__init__(self, parent)

    def __del__(self):
        ut.mce_exit.set()

    def run(self):
        data, queue = mp.Pipe()
        p = mp.Process(target=rf.Time_Files().netcdfdata , args=(queue,))
        p.start()
        while not ut.mce_exit.is_set():
            # grab data from read_files.py
            stuff = data.recv()
            # send updated data to the gui
            self.new_data.emit(stuff[0],stuff[1])

class Tel_Thread(QtCore.QThread):
    new_tel_data = QtCore.pyqtSignal(object,object,object,object,object,object,object)

    def __init__(self, parent = None):
        QtCore.QThread.__init__(self, parent)

    def __del__(self):
        ut.tel_exit.set()

    def run(self):
        data, queue = mp.Pipe()
        p = mp.Process(target=ft.start_tel_server, args=(queue,))
        p.start()
        while not ut.tel_exit.is_set() :
            # grab data from fake_tel_server.py
            tel_stuff = data.recv()
            ut.flags[0] = tel_stuff[1] #update flags passed to netcdf data
            self.new_tel_data.emit(tel_stuff[0],tel_stuff[1],tel_stuff[2],tel_stuff[3],tel_stuff[4],tel_stuff[5],tel_stuff[6])


''' Add this one once we know that KMS is on and ready to be integrated'''
# class KMS_Thread(QtCore.QThread):

#     new_kms_data = QtCore.pyqtSignal(object) # object is status flag
#
#     def __init__(self, parent = None):
#         QtCore.QThread.__init__(self, parent)
#
#     def __del__(self):
#         ut.kms_exit.set()
#
#     def run(self):
#         data, queue = mp.Pipe()
#         p = mp.Process(target='''tbd''' , args=(queue,))
#         p.start()
#         while not ut.kms_exit.is_set() :
#             kms_stuff = data.recv()
#             # send updated data to the gui
#             self.parallacticangle = kms_stuff[0]
#             self.positionalerror = kms_stuff[1]
            # ut.flags[1] = kms_stuff[2] #update kms flags sent to netcdf data
#             self.new_kms_data.emit(kms_stuff[2]) #stuff 2 is status flag

''' Add back in once HK socket script has been made '''
# class HK_Thread(QtCore.QThread):
#
#     def __init__(self, parent = None):
#         QtCore.QThread.__init__(self, parent)
#
#     def __del__(self):
#         hk_exit.set()
#
#     def run(self):
#         data, queue = mp.Pipe()
#         p = mp.Process(target=hk.update_sock , args=(queue,))
#         p.start()
#         while not ut.hk_exit.is_set() :
#             hk_stuff = data.recv()
#             # send hk status flag to gui
#             ut.flags[2] = hk_stuff


#activating the gui main window

if __name__ == '__main__':
    app = QtGui.QApplication(sys.argv)
    app.setApplicationName('TIME Data Visualization Suite')
    ex = mcegui()
    sys.exit(app.exec_())
    print("Done")
