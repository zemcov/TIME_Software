from pyqtgraph import QtCore, QtGui
import pyqtgraph as Qt
import numpy as np
import sys, os, subprocess, time, datetime, socket, struct, threading
sys.path.append('../TIME_Software/main')
sys.path.append('../main/tempfiles')
sys.path.append('../TIME_Software/')
sys.path.append('../TIME_Software/scans')
import pyqtgraph as pg
import random as rm
from termcolor import colored
import multiprocessing as mp
import utils as ut
import append_data, append_hk
import read_hk, kms_socket, raster_script_1d, raster_script_2d, tel_tracker, bowtie_scan, point_cross

#class of all components of GUI
class mcegui(QtGui.QWidget):
    #initializes mcegui class and calls other init functions
    def __init__(self, parent = None):
        super(mcegui, self).__init__(parent)
        self.init_mce()
        self.init_ui()
        self.qt_connections()
        self.flags = mp.Array('i',ut.flags,lock=True)
        self.offset = mp.Value('d',ut.offset,lock=True)

    #sets all of the variables for mce/graph, deletes old gui_data_test files
    def init_mce(self):
        self.timeinterval = 1
        self.observer = ''
        self.datamode = ''
        self.readoutcard = ''
        self.framenumber = ''
        self.frameperfile = 100
        self.totaltimeinterval = 120
        self.currentchannel = 1
        self.row = 0
        self.oldch = 0
        self.graphdata1 = []
        self.z1 = 0
        self.n_interval = 0
        ut.new_dir = str(datetime.datetime.utcnow().isoformat())
        self.netcdfdir = '/data/netcdffiles/%s' %(ut.new_dir)
        os.makedirs(self.netcdfdir)


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

        # stop all of the mces with their own command
        if self.showmcedata == 'Yes':
            if self.readoutcard == 'All':
                if ut.which_mce[1] == 1 :
                    subprocess.Popen(['./main/mce1_stop.sh s'],shell=True)
                if ut.which_mce[0] == 1 :
                    subprocess.Popen(['./main/mce0_stop.sh s'],shell=True)

            else :
                if ut.which_mce[1] == 1 :
                    subprocess.Popen(['./main/mce1_stop.sh %s' %(self.readoutcard)], shell=True)
                if ut.which_mce[0] == 1 :
                    subprocess.Popen(['./main/mce0_stop.sh %s' %(self.readoutcard)], shell=True)

        # # stop the file transfer process to time-master
        subprocess.Popen(['./main/mce1_stop_sftp.sh'], shell=True)
        subprocess.Popen(['./main/mce0_stop_sftp.sh'], shell=True)
        subprocess.Popen(['./main/hk_stop_sftp.sh'], shell=True)

        # # delete all MCE temp files still in local and mce computer directory
        if os.path.isfile('/home/time/Desktop/time-data/mce1/temp*'):
            os.remove('/home/time/Desktop/time-data/mce1/temp*')
        if os.path.isfile('/home/time/Desktop/time-data/mce2/temp*'):
            os.remove('/home/time/Desktop/time-data/mce2/temp*')
        if os.path.isfile('/home/time/Desktop/time-data/hk/omnilog*'):
            os.remove('/home/time/Desktop/time-data/hk/omnilog*')
        if os.path.isfile('/home/time/TIME_Software/main/tempfiles/tele_*'):
            os.remove('/home/time/TIME_Software/main/tempfiles/tele_*')

        print('Quitting Application')
        sys.exit()

    def on_starttel_clicked(self):

        self.sec = self.tel_sec.text()
        self.map_size = self.tel_map_size.text()
        self.num_loop = self.tel_num_loop.text()
        self.map_angle = self.tel_map_angle.text()
        self.coord1 = self.tel_coord1.text()
        self.coord2 = self.tel_coord2.text()
        self.epoch = self.tel_epoch.currentText()
        self.object = self.tel_object.text()
        self.inittel = self.init_tel.currentText()
        self.scan_time = self.scan_time_input.text()
        self.step = self.tel_step.text()

        if self.inittel == 'Yes':
            self.tel_scan = self.telescan.currentText()
            scans = ['1D Raster','2D Raster','Bowtie (constant el)','Pointing Cross']
            script = [raster_script_1d,raster_script_2d,bowtie_scan,point_cross]
            for scan in scans :
                if self.tel_scan == scan :
                    self.tel_script = script[scans.index(scan)]
            tel_message = 'TELESCOPE INITIALIZED'

            self.off = False
        else :
            self.tel_script = ' '
            self.off = True
            tel_message = 'NO TELESCOPE SELECTED'

        print(tel_message)

    #sets parameter variables to user input and checks if valid - will start MCE
    #and live graphing if they are

    def on_submitbutton_clicked(self):
        # check if telescope has been started first
        if not self.starttel.isEnabled() :
            print("Please Initialize Telescope First")
            self.submitbutton.setEnabled(False)

        ut.new_dir = '%s' %(datetime.datetime.utcnow().isoformat())

        #set variables to user input
        # observer ---------------------------------------
        self.observer = self.enterobserver.text()

        # which mces are active --------------------------
        self.mceson = self.whichmces.currentText()
        if self.mceson == 'MCE0':
            ut.which_mce[0] = 1
            ut.which_mce[1] = 0
        elif self.mceson == 'MCE1':
            ut.which_mce[0] = 0
            ut.which_mce[1] = 1
        else :
            ut.which_mce[0] = 1
            ut.which_mce[1] = 1

        # data mode --------------------------------------
        self.datamode = self.enterdatamode.currentText()
        mce_states = ['Error', 'SQ1 Feedback', 'Raw', 'Filtered SQ1 Feedback', 'Debugging', 'Mixed Mode (25:7)','Mixed Mode (22:10)','Mixed Mode (24:8)','Mixed mode (18:14)']
        mce_states2 = [0,1,12,2,11,10,7,5,4]
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
        # self.datarate = self.enterdatarate.text()

        # how much data to view on screen at once -------------------
        self.timeinterval = self.entertimeinterval.text()

        # keep old channel data on graph ----------------------------
        self.channeldelete = self.enterchanneldelete.currentText()

        # keep mce data on screen -----------------------------------
        self.showmcedata = self.entershowmcedata.currentText()

        # time keepers ----------------------------------------------
        self.timestarted = datetime.datetime.utcnow()
        self.timestarted = self.timestarted.isoformat()

        # -----------------------------------------------------------
        #check if parameters are valid - will create warning box if invalid
        if self.observer == '' or self.framenumber == '' or self.framenumber == '0'\
        or self.timeinterval == ''\
        or self.timeinterval == '0':
            self.warningbox('gui') # throw up a warning box
            # restart the gui window
            ex = mcegui()
        elif self.showmcedata == 'No':
            self.submitbutton.setEnabled(False)
        else:
            dir = '/home/time/TIME_Software/main/'
            if os.path.exists(dir + 'tempfiles/tempparameters.txt') :
                parafile = open(dir + 'tempfiles/tempparameters.txt', 'w')
                parafile.write(self.observer+' ')
                parafile.write(str(self.datamode)+' ')
                parafile.write(str(self.readoutcard)+' ')
                parafile.write(self.framenumber+' ')
                parafile.write(self.timeinterval+' ')
                parafile.write(self.channeldelete+' ')
                parafile.write(self.timestarted+' ')
                parafile.close()

            self.channelselection()
            print(colored('Time Started: %s' % (self.timestarted),'magenta'))
            # self.p = int((50 * 10 ** 6) / (33 * 90 * ut.german_freq)) #calculation taken from UBC MCE Wiki

            # prevents user from re-activating everything
            self.submitbutton.setEnabled(False)

            # check for leftover files from previous run and delete
            dir1 = '/home/time/Desktop/time-data/mce1/'
            dir2 = '/home/time/Desktop/time-data/mce2/'
            mce0 = len(os.listdir(dir1))
            mce1 = len(os.listdir(dir2))
            if mce0 != 0 :
                if os.path.isfile('/home/time/Desktop/time-data/mce1/temp*'):
                    os.remove('/home/time/Desktop/time-data/mce1/temp*')
                # subprocess.Popen(['rm /home/time/Desktop/time-data/mce1/temp*'], shell = True)
            if mce1 != 0 :
                if os.path.isfile('/home/time/Desktop/time-data/mce2/temp*'):
                    os.remove('/home/time/Desktop/time-data/mce2/temp*')
                # subprocess.Popen(['rm /home/time/Desktop/time-data/mce2/temp*'], shell = True)

            if os.path.isfile('/home/time/TIME_Software/main/tempfiles/tele_*'):
                os.remove('/home/time/TIME_Software/main/tempfiles/tele_*')
            # subprocess.Popen(['rm /home/time/TIME_Software/main/tempfiles/tele_*'], shell = True)

            #set the data mode for both mces and start them running
            if self.readoutcard == 'All':
                if ut.which_mce[0] == 1 :
                    subprocess.Popen(['./main/mce0_cdm.sh a %s' %(self.datamode)], shell = True)
                    subprocess.Popen(['./main/mce0_del.sh'], shell=True)
                    subprocess.Popen(['./main/mce0_run.sh %s s %s' %(self.framenumber, self.frameperfile)], shell = True)

                if ut.which_mce[1] == 1 :
                    subprocess.Popen(['./main/mce1_cdm.sh a %s' %(self.datamode)], shell = True)
                    subprocess.Popen(['./main/mce1_del.sh'], shell=True)
                    subprocess.Popen(['./main/mce1_run.sh %s s %s' %(self.framenumber, self.frameperfile)], shell = True)
            else :
                if ut.which_mce[0] == 1 :
                    subprocess.Popen(['./main/mce0_cdm.sh a %s %s' %(self.readoutcard, self.datamode)], shell = True)
                    subprocess.Popen(['./main/mce0_del.sh'], shell=True)
                    subprocess.Popen(['./main/mce0_run.sh %s %s %s' %(self.framenumber, self.readoutcard, self.frameperfile)], shell = True)

                if ut.which_mce[1] == 1 :
                    subprocess.Popen(['./main/mce1_cdm.sh a %s %s' %(self.readoutcard, self.datamode)], shell = True)
                    subprocess.Popen(['./main/mce1_del.sh'], shell=True)
                    subprocess.Popen(['./main/mce1_run.sh %s %s %s' %(self.framenumber, self.readoutcard, self.frameperfile)], shell = True)

            # start file transfer scripts
            subprocess.Popen(['ssh -T time-hk python /home/time/TIME_Software/sftp/hk_sftp.py'], shell=True)
            if ut.which_mce[0] == 1 :
                subprocess.Popen(['ssh -T time-mce-0 python /home/time/TIME_Software/sftp/mce0_sftp.py'], shell=True)
            if ut.which_mce[1] == 1 :
                subprocess.Popen(['ssh -T time-mce-1 python /home/time/TIME_Software/sftp/mce1_sftp.py'], shell=True)
            time.sleep(2.0)

            data = np.zeros((33,32))
            #start other plot making processes
            self.initplot()
            self.initheatmap(data,data) # give first values for heatmap to create image scale
            self.initfftgraph()
            self.inittelescope()
            # self.initkmirrordata()

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
            ['Error', 'SQ1 Feedback', 'Raw', 'Filtered SQ1 Feedback', 'Debugging', 'Mixed Mode (25:7)','Mixed Mode (22:10)','Mixed Mode (24:8)','Mixed mode (18:14)'])
        self.whichmces = QtGui.QComboBox()
        self.whichmces.addItems(['MCE0','MCE1','Both'])
        self.enterreadoutcard = QtGui.QComboBox()
        for i in range(8):
            if i < 4:
                self.enterreadoutcard.addItem('MCE 0 RC %s' % (i % 4 + 1))
            else:
                self.enterreadoutcard.addItem('MCE 1 RC %s' % (i % 4 + 1))
        self.enterreadoutcard.addItem('All')
        self.enterframenumber = QtGui.QLineEdit('1350000')
        self.enterframenumber.setMaxLength(9)
        # self.enterdatarate = QtGui.QLineEdit('45')
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
        self.parameters.addRow("Active MCE's", self.whichmces)
        self.parameters.addRow('Datamode', self.enterdatamode)
        self.parameters.addRow('Readout Card', self.enterreadoutcard)
        self.parameters.addRow('Frame Number', self.enterframenumber)
        # self.parameters.addRow('Data Rate', self.enterdatarate)
        self.parameters.addRow('Delete Old Columns', self.enterchanneldelete)
        self.parameters.addRow('Time Interval (s)', self.entertimeinterval)
        self.parameters.addRow('Show MCE Data', self.entershowmcedata)
        self.parameters.addRow(self.submitbutton)
        self.mceGroupBox.setLayout(self.parameters)

        # telescope options =================================================
        self.telescan = QtGui.QComboBox()
        self.telescan.addItems(['1D Raster','2D Raster','BowTie (constant el)','Pointing Cross'])

        self.tel_delay = QtGui.QLineEdit('0')

        self.init_tel = QtGui.QComboBox()
        self.init_tel.addItems(['No','Yes'])

        self.tel_sec = QtGui.QLineEdit('6')
        self.tel_map_size = QtGui.QLineEdit('1')
        self.tel_num_loop  = QtGui.QLineEdit('20')
        self.tel_step = QtGui.QLineEdit('0.001')
        self.tel_map_angle = QtGui.QLineEdit('0')
        self.scan_time_input = QtGui.QLineEdit('30')
        self.tel_coord1 = QtGui.QLineEdit()
        self.tel_coord2 = QtGui.QLineEdit()
        self.tel_epoch = QtGui.QComboBox()
        self.tel_epoch.addItems(['B1950.0','Apparent','J2000.0'])
        self.tel_object = QtGui.QLineEdit('Mars')

        self.telGroupBox = QtGui.QGroupBox("Telescope Parameters")
        self.telparams = QtGui.QFormLayout()
        self.teltitle = QtGui.QLabel(self)
        self.teltitle.setAlignment(QtCore.Qt.AlignCenter)
        self.teltitle.setText('Telescope Parameters')
        self.telparams.addRow(self.teltitle)
        self.telparams.addRow('Activate Telescope', self.init_tel)
        self.telparams.addRow('Scan Strategy', self.telescan)
        self.telparams.addRow('Total Scan Time (sec)', self.scan_time_input)
        self.telparams.addRow('Delayed Start (sec)', self.tel_delay)
        self.telparams.addRow('Time to Traverse Scan Length (sec)', self.tel_sec)
        self.telparams.addRow('Map Size [deg], (distance for center of array to reach map edge)', self.tel_map_size)
        self.telparams.addRow('Angle of Map Offset [deg]', self.tel_map_angle)
        self.telparams.addRow('Number of 2D Map Vertical Steps [deg]', self.tel_num_loop)
        self.telparams.addRow('Size of 2D Vertical Step [deg]', self.tel_step)
        self.telparams.addRow('RA Coord of Source: [hr:min:sec]', self.tel_coord1)
        self.telparams.addRow('DEC Coord of Source: [deg:arcmin:arcsec]', self.tel_coord2)
        self.telparams.addRow('Epoch of Observation', self.tel_epoch)
        self.telparams.addRow('Object Catalog Name', self.tel_object)
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
        self.mcegraphdata1 = pg.ScatterPlotItem()
        self.mcegraphdata2 = pg.ScatterPlotItem()
        self.mcegraph = pg.PlotWidget()
        self.grid.addWidget(self.mcegraph, 1, 2, 4, 10)

        #add labels to graph
        self.mcegraph.setLabel('bottom', 'Time', 's')
        self.mcegraph.setLabel('left', 'Counts')
        self.mcegraph.setTitle('MCE TIME Data')

        #initalize old data graph GUI item and add labels
        # self.oldmcegraph = pg.PlotWidget()
        # self.oldmcegraphdata1 = pg.PlotCurveItem()
        # self.oldmcegraphdata2 = pg.PlotCurveItem()
        # self.grid.addWidget(self.oldmcegraph, 1, 2, 2, 3)
        # self.oldmcegraph.setLabel('bottom', 'Time', 's')
        # self.oldmcegraph.setLabel('left', 'Counts')
        # self.oldmcegraph.setTitle('Old MCE TIME Data')
        # self.oldmcegraph.addItem(self.oldmcegraphdata1)
        # self.oldmcegraph.addItem(self.oldmcegraphdata2)

        # connecting thread functions
        self.updater = MCEThread(offset = self.offset, flags = self.flags, netcdfdir = self.netcdfdir)
        self.updater.new_data.connect(self.updateplot)
        self.updater.start()

    def initheatmap(self,h1,h2) :

        if ut.which_mce[0] == 1 :
            self.roll_avg_1 = h1

        if ut.which_mce[1] == 1 :
            self.roll_avg_2 = h2

        # heatmap for first MCE ===================================================================================
        self.heatmapplot1 = pg.PlotItem()
        self.heatmapplot1.setLabel('bottom', 'Row')
        self.heatmapplot1.setLabel('left', 'Channel')
        self.heatmapplot1.setTitle('MCE0 RMS Noise')

        self.heatmap1 = pg.ImageView(view= self.heatmapplot1)
        self.heatmap1.setPredefinedGradient('thermal')
        self.heatmap1.autoLevels()

        if ut.which_mce[0] == 1 :
            self.heatmap1.setImage(h1)
        # =========================================================================================================

        # heatmap for second MCE ==================================================================================
        self.heatmapplot2 = pg.PlotItem()
        self.heatmapplot2.setLabel('bottom', 'Row')
        self.heatmapplot2.setLabel('left', 'Channel')
        self.heatmapplot2.setTitle('MCE1 RMS Noise')

        self.heatmap2 = pg.ImageView(view= self.heatmapplot2)
        self.heatmap2.setPredefinedGradient('thermal')
        self.heatmap2.autoLevels()

        if ut.which_mce[1] == 1 :
            self.heatmap2.setImage(h2)
        # ===========================================================================================================

        # first set image is same as heatmap because we need 2 updates of data to take an average

        # heatmap for Raw Data MCE0 ==================================================================================
        self.heatmapplot3 = pg.PlotItem()
        self.heatmapplot3.setLabel('bottom', 'Row')
        self.heatmapplot3.setLabel('left', 'Channel')
        self.heatmapplot3.setTitle('MCE0 Averaged Signal')

        self.heatmap3 = pg.ImageView(view= self.heatmapplot3)
        self.heatmap3.setPredefinedGradient('thermal')
        self.heatmap3.autoLevels()

        if ut.which_mce[0] == 1 :
            self.heatmap3.setImage(h1)
        # ===========================================================================================================

        # heatmap for Raw Data MCE1 ==================================================================================
        self.heatmapplot4 = pg.PlotItem()
        self.heatmapplot4.setLabel('bottom', 'Row')
        self.heatmapplot4.setLabel('left', 'Channel')
        self.heatmapplot4.setTitle('MCE1 Averaged Signal')

        self.heatmap4 = pg.ImageView(view= self.heatmapplot4)
        self.heatmap4.setPredefinedGradient('thermal')
        self.heatmap4.autoLevels()

        if ut.which_mce[1] == 1 :
            self.heatmap4.setImage(h2)
        # ===========================================================================================================

        # create new window for hk and fft data
        self.heatmapwindow = QtGui.QWidget()
        self.heatmapwindow.setWindowTitle('MCE Heatmap')
        self.heatgrid = QtGui.QGridLayout()
        self.heatgrid.addWidget(self.heatmap1, 1, 5, 2, 3)
        self.heatgrid.addWidget(self.heatmap2, 1, 2, 2, 3)
        self.heatgrid.addWidget(self.heatmap3, 3, 5, 2, 3)
        self.heatgrid.addWidget(self.heatmap4, 3, 2, 2, 3)
        self.heatmapwindow.setGeometry(10, 10, 1920, 1080)
        self.heatmapwindow.setLayout(self.heatgrid)
        self.heatmapwindow.show()

    def initfftgraph(self):

        self.fftgraph = pg.PlotWidget()
        self.fftgraphdata1 = pg.ScatterPlotItem()
        self.fftgraphdata2 = pg.ScatterPlotItem()
        self.fftgraph.addItem(self.fftgraphdata1)
        self.fftgraph.addItem(self.fftgraphdata2)

        self.fftgraph.setLabel('bottom', 'Time', 's')
        self.fftgraph.setLabel('left', 'Counts')
        self.fftgraph.setTitle('MCE 0/1 FFT Data')

        self.grid.addWidget(self.fftgraph, 3, 2, 4, 6)

    def initkmirrordata(self):
        # start the kms QThread
        ''' Add back in once KMS is running '''
        # if self.tel_script == 'point_cross.py' :
        #     # do something to set KMS in specific position before starting KMS thread
        #     print('No KMS!')
        # self.kms_updater = KMS_Thread()
        # self.kms_updater.new_kms_data.connect(self.updatekmirrordata)
        # self.kms_updater.start()

        #place holder data
        self.parallacticangle = 0.0
        self.positionalerror = 0.0
        self.kmsstatus = 'Normal'
        self.status = ' '
        self.time = 0.0
        self.enc = 0.0

        self.parallacticangletext = QtGui.QLabel('Parallactic Angle: %s' %(self.parallacticangle))
        self.parallacticangletext.setAlignment(QtCore.Qt.AlignCenter)
        self.positionalerrortext = QtGui.QLabel('Positional Error: %s' %(self.positionalerror))
        self.positionalerrortext.setAlignment(QtCore.Qt.AlignCenter)
        self.kmsstatustext = QtGui.QLabel('KMS Status Flag: %s' %(self.kmsstatus))
        self.kmsstatustext.setAlignment(QtCore.Qt.AlignCenter)
        self.kmstitle = QtGui.QLabel('Kmirror System Position and Status')
        self.kmstitle.setAlignment(QtCore.Qt.AlignCenter)
        self.statustext = QtGui.QLabel('Tel Status: %s' %(self.status))
        self.statustext.setAlignment(QtCore.Qt.AlignCenter)
        self.timetext = QtGui.QLabel('UTC Time: %s' %(self.time))
        self.timetext.setAlignment(QtCore.Qt.AlignCenter)
        self.enctext = QtGui.QLabel('Encoder Position: %s' %(self.enc))
        self.enctext.setAlignment(QtCore.Qt.AlignCenter)

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
        self.kmsparams.addWidget(self.statustext)
        self.kmsparams.addWidget(self.timetext)
        self.kmsparams.addWidget(self.enctext)
        self.kmsgui.setLayout(self.kmsparams)
        self.grid.addWidget(self.kmsgui, 4, 1, 1, 1)

    def inittelescope(self):

        # start the telescope QThread
        self.tel_updater = Tel_Thread(flags = self.flags, scan_time = self.scan_time, tel_script = self.tel_script, off = self.off, sec = self.sec, map_size = self.map_size,\
                                        map_angle = self.map_angle, coord1 = self.coord1, coord2 = self.coord2, epoch = self.epoch,\
                                            object = self.object, num_loop = self.num_loop, step = self.step)
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

        if self.off == False :
            self.telescopewindow.show()
        else :
            pass

        self.repeat = False

        self.alt = [0]
        self.az = [0]
        self.ra = [0]
        self.dec = [0]

    def updatekmirrordata(self,pa,status,time,enc):

        # error checking based on status flags from kmirror
        kms_error = [10,11,12,13]
        if (status in kms_error) and (self.repeat == False) :
            os.system("mpg123 /home/time/time-software-testing/TIME_Software/main/klaxon.mp3")
            self.repeat = True
            ut.tel_exit.set()
            ut.mce_exit.set()
            ut.kms_exit.set()
            ut.hk_exit.set()
            self.warningbox(['kms',status])

        else :
            self.parallacticangle = pa
            self.positionalerror = rm.randint(0, 90)
            self.status = status
            self.time = time
            self.enc = enc

            self.parallacticangletext.setText('Parallactic Angle: %s' % (self.parallacticangle))
            self.positionalerrortext.setText('Positonal Error: %s' % (self.positionalerror))
            self.statustext.setText('Tel Current Status: %s' %(self.status))
            self.timetext.setText('UTC Time: %s' %(self.time))
            self.enctext.setText('Encoder Position %s' %(self.enc))

    def updatefftgraph(self):
        #self.y and self.x are defined in updateplot

        if ut.which_mce[0] == 1 :

            self.fftdata1 = np.fft.fft(self.y1)
            self.fftdata1 = np.asarray(self.fftdata1, dtype=np.float32)
            self.fftdata1[0] = self.fftdata1[-1]
            self.fftgraphdata1.setData(self.x, self.fftdata1)

        if ut.which_mce[1] == 1 :

            self.fftdata2 = np.fft.fft(self.y2)
            self.fftdata2 = np.asarray(self.fftdata2, dtype=np.float32)
            self.fftdata2[0] = self.fftdata2[-1]
            self.fftgraphdata2.setData(self.x, self.fftdata2)

    def updatetelescopedata(self,pa,slew,alt,az,ra,dec,time):
        # error checking based on status flags from telescope
        tel_error = [10,11,12]

        if (slew in tel_error) and (self.repeat == False) :
            # use afplay for mac testing
            os.system("mpg123 /home/time/time-software-testing/TIME_Software/main/klaxon.mp3")
            self.repeat = True
            ut.tel_exit.set()
            ut.mce_exit.set()
            ut.kms_exit.set()
            ut.hk_exit.set()
            self.warningbox(['tel',slew]) #slew will be replaced with tel status flag over socket

        elif slew == 'done' :
            print('telescope data did')
            os.system("mpg123 /home/time/time-software-testing/TIME_Software/main/finished.mp3")
            self.repeat = True
            ut.tel_exit.set()
            ut.mce_exit.set()
            ut.kms_exit.set()
            ut.hk_exit.set()
            self.warningbox(['tel_stop','done'])

        else :
            # update text on window to reflect new data
            tel_flags = [0,1,2,3,4]
            tel_names = ['Idle','Tracking Centroid','-RA','+RA','Turn Around Zone']
            for i in range(len(tel_flags)):
                if slew == tel_flags[i]:
                    self.slewtext.setText('Slew Flag: %s' %(tel_names[i]))
            self.patext.setText('PA: %s' %(round(float(pa),2)))
            self.timetext.setText('UTC Time: %s'%(round(float(time),2)))

            altazcolor = pg.mkBrush('b')
            radeccolor = pg.mkBrush('r')

            if len(self.az) < 800 :
                self.az.append(float(az))
                self.alt.append(float(alt))
                self.ra.append(float(ra))
                self.dec.append(float(dec))
            else :
                self.az.pop(0)
                self.az.append(float(az))
                self.alt.pop(0)
                self.alt.append(float(alt))
                self.ra.pop(0)
                self.ra.append(float(ra))
                self.dec.pop(0)
                self.dec.append(float(dec))

            self.altazgraphdata.setData(x=self.az, y=self.alt, brush=altazcolor)
            self.radecgraphdata.setData(x=self.ra, y=self.dec, brush=radeccolor)

            # self.altazgraphdata.addPoints(x=az, y=alt, brush=altazcolor)
            # self.radecgraphdata.addPoints(x=ra, y=dec, brush=radeccolor)

    def updateplot(self,h1,h2,index):

        # self.currentchannel = 2
        # self.row = 14


        self.index = index
        self.starttime = datetime.datetime.utcnow()

        # parsing mce array for graph data ========================
        if ut.which_mce[0] == 1 :

            y1 = np.asarray(h1)[self.row,self.currentchannel,:]
            self.y1 = y1

        if ut.which_mce[1] == 1 :

            y2 = np.asarray(h2)[self.row,self.currentchannel,:]
            self.y2 = y2

        #creates x values for current time interval and colors points based on current channel ===
        self.endtime = datetime.datetime.utcnow()
        self.timetaken = self.endtime - self.starttime

        x = np.linspace(self.index,self.index + 1,self.frameperfile)
        self.x = x

        self.pointcolor = []
        self.pointsymbol = []
        # =====================================================================================
        #picks color based on current channel =============================================
        symbols = ['b','r','g','y','c','m','k','w']
        i = self.currentchannel // 4
        self.pointcolor.extend([pg.mkBrush(symbols[i]) for j in range(self.frameperfile)])
        # =================================================================================================================
        # changes symbols for viewing different RC cards on same plot =====================
        syms = ['d','o','s','t','d','o','s','t']
        i = self.row // 4
        self.pointsymbol.extend([syms[i] for j in range(self.frameperfile)])
        #============================================================================================================

        #creates graphdata item on first update
        if self.index == 0:

            self.mcegraph.setXRange(self.index, self.index + self.totaltimeinterval - 1, padding=0)

            # self.updatefftgraph()
            self.data[0] = x

            if ut.which_mce[0] == 1 :
                self.data[1] = y1
                self.mcegraph.addItem(self.mcegraphdata1)

            if ut.which_mce[1] == 1 :
                self.mcegraph.addItem(self.mcegraphdata2)
                self.data[2] = y2

            if self.readoutcard == 'All':

                if ut.which_mce[0] == 1 :
                    self.mcegraphdata1.setData(x, y1, brush=self.pointcolor, symbol=self.pointsymbol)
                    # self.mcegraphdata1.setData(x,y1)
                if ut.which_mce[1] == 1 :
                    self.mcegraphdata2.setData(x, y2, brush=self.pointcolor, symbol=self.pointsymbol)
                    # self.mcegraphdata2.setData(x,y2)

            else:

                if ut.which_mce[0] == 1 :
                    self.mcegraphdata1.setData(x, y1, brush=self.pointcolor)
                if ut.which_mce[1] == 1 :
                    self.mcegraphdata2.setData(x, y2, brush=self.pointcolor)

            self.oldch = self.currentchannel
            # updates oldgraph data
            self.data[0] = x

            if ut.which_mce[0] == 1 :
                self.data[1] = y1
            if ut.which_mce[1] == 1 :
                self.data[2] = y2

            self.n_interval += 1 # update to keep graph going
        # ===========================================================================================================
        #clears graphdata and updates old graph after the total time interval has passed
        elif self.n_interval == self.totaltimeinterval :
            # self.oldmcegraph.setXRange(self.index - self.frameperfile, self.index + self.totaltimeinterval - 1 - self.frameperfile, padding=0)
            self.mcegraph.setXRange(self.index, self.index + self.totaltimeinterval - 1, padding=0)
            self.data[0] = x

            if ut.which_mce[0] == 1 :
                self.data[1] = y1
                # self.oldmcegraphdata1.setData(self.data[0], self.data[1])
                self.mcegraphdata1.clear()

            if ut.which_mce[1] == 1 :
                self.data[2] = y2
                # self.oldmcegraphdata2.setData(self.data[0], self.data[2])
                self.mcegraphdata2.clear()

            if self.readoutcard == 'All':
                if ut.which_mce[0] == 1 :
                    self.mcegraphdata1.setData(x, y1, brush=self.pointcolor, symbol=self.pointsymbol)
                    # self.mcegraphdata1.setData(x,y1)
                if ut.which_mce[1] == 1 :
                    self.mcegraphdata2.setData(x, y2, brush=self.pointcolor, symbol=self.pointsymbol)
                    # self.mcegraphdata1.setData(x,y2)

            else:
                if ut.which_mce[0] == 1 :
                    self.mcegraphdata1.setData(x, y1, brush=self.pointcolor)
                if ut.which_mce[1] == 1 :
                    self.mcegraphdata2.setData(x, y2, brush=self.pointcolor)

            self.data = [0, 0, 0]
            # updates oldgraphdata after total time interval is reached
            self.data[0] = x

            if ut.which_mce[0] == 1 :
                self.data[1] = y1
            if ut.which_mce[1] == 1 :
                self.data[2] = y2

            self.n_interval = 0 #reset counter
        # ==============================================================================================================
        #updates graph, if channel delete is set to yes will clear data first
        else:

            if ut.which_mce[0] == 1 and ut.which_mce[1] == 1 :
                self.updateheatmap(h1,h2) # give first values for heatmap to create image scale
            elif ut.which_mce[0] == 1 :
                dummy = []
                self.updateheatmap(h1,dummy)
            else :
                dummy = []
                self.updateheatmap(dummy,h2)

            # self.updatefftgraph()

            if self.channeldelete == 'Yes' and self.oldch != self.currentchannel:

                if ut.which_mce[0] == 1 :
                    self.mcegraphdata1.clear()
                if ut.which_mce[1] == 1 :
                    self.mcegraphdata2.clear()

                if self.readoutcard == 'All':
                    if ut.which_mce[0] == 1 :
                        self.mcegraphdata1.setData(x, y1, brush=self.pointcolor, symbol=self.pointsymbol)
                        # self.mcegraphdata1.setData(x,y1)
                    if ut.which_mce[1] == 1 :
                        self.mcegraphdata2.setData(x, y2, brush=self.pointcolor, symbol=self.pointsymbol)
                        # self.mcegraphdata1.setData(x,y2)

                else:
                    if ut.which_mce[0] == 1 :
                        self.mcegraphdata1.setData(x, y1, brush=self.pointcolor)
                    if ut.which_mce[1] == 1 :
                        self.mcegraphdata2.setData(x, y2, brush=self.pointcolor)

            else:
                if self.readoutcard == 'All':
                    if ut.which_mce[0] == 1 :
                        self.mcegraphdata1.addPoints(x, y1, brush=self.pointcolor, symbol=self.pointsymbol)
                        # self.mcegraphdata1.setData(x,y1)
                    if ut.which_mce[1] == 1 :
                        self.mcegraphdata2.addPoints(x, y2, brush=self.pointcolor, symbol=self.pointsymbol)
                        # self.mcegraphdata1.setData(x,y2)

                else:
                    if ut.which_mce[0] == 1 :
                        self.mcegraphdata1.addPoints(x, y1, brush=self.pointcolor)
                    if ut.which_mce[1] == 1 :
                        self.mcegraphdata2.addPoints(x, y2, brush=self.pointcolor)

            # updates old data for when graph resets
            np.append(self.data[0],x) # doesn't create a new array but adds to existing

            if ut.which_mce[0] == 1 :
                np.append(self.data[1],y1)
            if ut.which_mce[1] == 1 :
                np.append(self.data[2],y2)

            self.n_interval += 1
        # =================================================================================================================
        self.oldch = self.currentchannel
        # =================================================================================================================

    def updateheatmap(self,h1,h2):

        self.alpha = 0.1

        if ut.which_mce[0] == 1 :

            m1 = np.zeros([h1.shape[0],h1.shape[1]],dtype=np.float32)
            for b in range(h1.shape[0]):
                for c in range(h1.shape[1]):
                    z1 = np.std(h1[b,c,:])
                    if z1 != 0.0 :
                        m1[b][c] = np.log(z1)
                    else :
                        m1[b][c] = None
            b = 0
            c = 0

            d1 = np.zeros([h1.shape[0],h1.shape[1]],dtype=np.float32)
            for b in range(h1.shape[0]):
                for c in range(h1.shape[1]):
                    d1[b][c] = (np.mean(h1[b,c,:],dtype=np.float32))

            b = 0
            c = 0

            self.heatmap1.setImage(m1)

            d1_avg = np.empty([33,32])

            for b in range(h1.shape[0]):
                for c in range(h1.shape[1]):
                    self.roll_avg_1[b][c] = ((1-self.alpha)*self.roll_avg_1[b][c]) + (self.alpha * d1[b][c])
                    d1_avg[b][c] = d1[b][c] - self.roll_avg_1[b][c]

            self.heatmap3.setImage(d1_avg)

        if ut.which_mce[1] == 1 :

            # ---------------------------------------------------------
            m2 = np.zeros([h2.shape[0],h2.shape[1]],dtype=np.float32)
            for b in range(h2.shape[0]):
                for c in range(h2.shape[1]):
                    z2 = np.std(h2[b,c,:])
                    if z2 != 0.0 :
                        m2[b][c] = np.log(z2)
                    else :
                        m2[b][c] = None
            print(m2[0])

            b = 0
            c = 0

            d2 = np.zeros([h2.shape[0],h2.shape[1]],dtype=np.float32)
            for b in range(h2.shape[0]):
                for c in range(h2.shape[1]):
                    d2[b][c] = (np.mean(h2[b,c,:],dtype=np.float32))

            b = 0
            c = 0
            # ----------------------------------------------------------

            self.heatmap2.setImage(m2)

            d2_avg = np.zeros([33,32],dtype=np.float32)

            for b in range(h2.shape[0]):
                for c in range(h2.shape[1]):
                    self.roll_avg_2[b][c] = ((1-self.alpha)*self.roll_avg_2[b][c]) + (self.alpha * d2[b][c])
                    d2_avg[b][c] = d2[b][c] - self.roll_avg_2[b][c]

            self.heatmap4.setImage(d2_avg)


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
        elif message[0] == 'tel_stop' :
            telwarning = QtGui.QMessageBox()
            telwarning.setStyleSheet("background-color: rgb(0,128,0); color: rgb(0,0,0)")
            telwarning.setIcon(QtGui.QMessageBox.Information)
            telwarning.setText('Telescope Scan Finished!')
            telwarning.setStandardButtons(QtGui.QMessageBox.Ok)
            telwarning.setWindowTitle('Telescope Stopped')
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

class MCEThread(QtCore.QThread):

    new_data = QtCore.pyqtSignal(object,object,object)

    def __init__(self,offset,flags,netcdfdir,parent = None):
        QtCore.QThread.__init__(self, parent)
        self.netcdfdir = netcdfdir
        self.flags = flags
        self.offset = offset

    def __del__(self):
        ut.mce_exit.set()

    def run(self):
        data, queue = mp.Pipe()
        p = mp.Process(target=append_data.Time_Files(flags = self.flags, offset = self.offset).retrieve, args=(queue,self.netcdfdir,))
        p2 = mp.Process(target=append_hk.Time_Files(offset = self.offset).retrieve, args=(self.netcdfdir,))
        p.start()
        p2.start()

        while not ut.mce_exit.is_set():
            stuff = data.recv()
            if ut.which_mce[0] == 1 and ut.which_mce[1] == 1 :
                self.new_data.emit(stuff[0],stuff[1],stuff[2])
            elif ut.which_mce[0] == 1 :
                dummy = []
                self.new_data.emit(stuff[0],dummy,stuff[2])
            else :
                dummy = []
                self.new_data.emit(dummy,stuff[1],stuff[2])
            time.sleep(0.01)

class Tel_Thread(QtCore.QThread):

    new_tel_data = QtCore.pyqtSignal(object,object,object,object,object,object,object)

    def __init__(self, flags, scan_time, tel_script, off, sec, map_size, map_angle, coord1, coord2, epoch, object, num_loop, step, parent = None):
        QtCore.QThread.__init__(self, parent)
        self.off = off
        self.tel_script = tel_script
        self.sec = sec
        self.map_size = map_size
        self.map_angle = map_angle
        self.coord1 = coord1
        self.coord2 = coord2
        self.epoch = epoch
        self.object = object
        self.num_loop = num_loop
        self.scan_time = scan_time
        self.flags = flags
        self.step = step

    def __del__(self):
        ut.tel_exit.set()

    def run(self):
        if self.off == False :
            data, queue = mp.Pipe()
            p = mp.Process(target=self.tel_script.TIME_TELE().start_sock, args=(queue,self.scan_time,self.sec,self.map_size,\
                                    self.map_angle,self.coord1,self.coord2,self.epoch,self.object,self.num_loop,self.step))
            p.start()

            while True :
                # grab data from tel_tracker.py
                if not ut.tel_exit.is_set() :
                    tel_stuff = data.recv()
                    with self.flags.get_lock() :
                        self.flags[0] = int(tel_stuff[1]) #update flags passed to netcdf data
                    # pa,float(direction),el,az,map_ra,map_dec,ut
                    self.new_tel_data.emit(tel_stuff[0],tel_stuff[1],tel_stuff[2],tel_stuff[3],tel_stuff[4],tel_stuff[5],tel_stuff[6])
                    time.sleep(0.01)

                else :
                    self.new_tel_data.emit(0,'done',0,0,0,0,0)
                    print(colored('Telescope Scan Completed!','green'))
                    break

        else :
            # makes fake data for when we don't want to run the telescope
            tele_array = np.zeros((20,20),dtype=float)
            np.save('/home/time/TIME_Software/main/tempfiles/tele_packet_off1.npy',tele_array)
            time.sleep(0.05)
            np.save('/home/time/TIME_Software/main/tempfiles/tele_packet_off2.npy',tele_array)


class KMS_Thread(QtCore.QThread):

    new_kms_data = QtCore.pyqtSignal(object,object,object,object) # object is status flag

    def __init__(self, parent = None):
        QtCore.QThread.__init__(self, parent)

    def __del__(self):
        ut.kms_exit.set()

    def run(self):
        data, queue = mp.Pipe()
        p = mp.Process(target=kms_socket.start_sock , args=(queue,))
        p.start()
        while not ut.kms_exit.is_set() :
            kms_stuff = data.recv() # pa , flags, time, encoder pos
            # send updated data to the gui
            with self.flags.get_lock():
                self.flags[2] = int(kms_stuff[2])

            self.new_kms_data.emit(kms_stuff[0],kms_stuff[1],kms_stuff[2],kms_stuff[3]) #stuff 2 is status flag

#activating the gui main window

if __name__ == '__main__':
    app = QtGui.QApplication(sys.argv)
    app.setApplicationName('TIME Data Visualization Suite')
    ex = mcegui()
    sys.exit(app.exec_())
    print("Done")
