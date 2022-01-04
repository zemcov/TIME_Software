#!/usr/bin/env python3

import sys

if sys.version_info.major != 3:
    sys.exit("This software is expecting Python 3.x")
from matplotlib import cm
import os, subprocess, time, datetime, socket, struct, threading, shutil
from pyqtgraph import QtCore, QtGui, GraphicsLayoutWidget, GraphicsLayout
from PyQt5.QtWebEngineWidgets import QWebEngineView
from PyQt5.QtWidgets import QSizePolicy
import pyqtgraph as Qt
import numpy as np
import pyqtgraph as pg
import random as rm
from termcolor import colored
import multiprocessing as mp
from hanging_threads import start_monitoring
from matplotlib import cm
from coms import kms_socket, tel_tracker
from main import append_data, append_hk, read_hk, fake_tel
from main.tel_box import draw_box
from scans import raster_script_1d, raster_script_2d, bowtie_scan, point_cross
# from make_iv_curve_nc import *
from config import init, directory
import time
import config.utils as ut
sys.path.append('loadcurves')
from gui_loadcurve import *

#class of all components of GUI
class MainWindow(QtGui.QMainWindow):

    #initializes mcegui class and calls other init functions
    def __init__(self, parent = None):

        self.telescope_initialized = False
        self.showmcedata = None
        self.startwindow = None
        self.browser = None
        self.newwindow = None
        self.heatmapwindow = None
        self.telescopewindow = None
        self.updater = None
        self.tel_updater = None
        self.kms_updater = None

        super(MainWindow, self).__init__(parent)
        self.setWindowTitle('TIME Live Data Visualization Suite')
        # self.setAutoFillBackground(true)
        self.getparameters()

        p = QtGui.QPalette()
        # p.setBrush(QtGui.QPalette.Window, QtGui.QBrush(QtGui.QColor(114,160,240)))
        p.setBrush(QtGui.QPalette.Window, QtGui.QBrush(QtGui.QColor(255,255,255)))


        self.logo = QtGui.QImage(directory.master_dir + "/timelogo.png")
        self.logopal = QtGui.QPalette()
        self.logopal.setBrush(QtGui.QPalette.Window,QtGui.QBrush(self.logo))

        # start the main input window to specify observing parameters
        self.startwindow = QtGui.QWidget()
        self.startgrid = QtGui.QGridLayout()
        self.startgrid.addLayout(self.parametersquit,1,1,QtCore.Qt.AlignBottom)
        self.startwindow.setGeometry(10, 10, 1920, 1080)
        self.startwindow.setLayout(self.startgrid)
        # self.startwindow.setPalette(self.logopal)
        self.startwindow.setPalette(p)
        self.startwindow.closeEvent = self.on_quitbutton_clicked
        self.startwindow.show()

        ''' ######################################################################## '''
        # subprocess.Popen(['ssh -T -X -n obs@corona "cd /home/corona/cactus/status; ./status -n"'],shell=True)
        # subprocess.Popen(['ssh -T -X -n obs@modelo "cd /home/corona/cactus/catalog; ./catalog"'],shell=True)
        # subprocess.Popen(['ssh -T -Y -n obs@corona "cd /home/corona/cactus/APA/display; ./tsd_client --geometry 864x487"'],shell=True)
        # subprocess.Popen(['ssh -T -Y -n oper12m@corona "cd /home/corona/cactus/xhchat; ./xhchat :1.0"'],shell=True)
        # subprocess.Popen(['ssh -T -X -n obs@modelo "cd /home/corona/cactus/weather; ./weather"'],shell=True)
        ''' ######################################################################## '''

        self.init_mce()
        self.qt_connections()

    #sets all of the variables for mce/graph, deletes old gui_data_test files
    def init_mce(self):
        self.timeinterval = 1
        self.observer = ''
        self.datamode = ''
        self.readoutcard = ''
        self.framenumber = ''
        self.frameperfile = 100
        self.totaltimeinterval = 120
        self.channel1 = 0
        self.channel2 = 0
        self.row1 = 0
        self.row2 = 0
        self.oldch1 = 0
        self.oldch2 = 0
        self.graphdata1 = []
        self.z1 = 0
        self.n_interval = 0
        self.flags = mp.Array('i',ut.flags,lock=True)
        self.offset = mp.Value('d',ut.offset,lock=True)
        # self.netcdfdir = directory.netcdf_dir
        self.netcdfdir = directory.netcdf_dir + str(int(time.time()))
        if not os.path.isdir(self.netcdfdir) :
            # oldmask = os.umask(000)
            os.makedirs(self.netcdfdir,0o755)
            # os.umask(oldmask)

    #reacts to button presses and other GUI user input
    def qt_connections(self):
        self.quitbutton.clicked.connect(self.on_quitbutton_clicked)
        self.submitbutton.clicked.connect(self.on_submitbutton_clicked)
        self.starttel.clicked.connect(self.on_starttel_clicked)
        self.changechan.clicked.connect(self.on_set_chan_clicked)
        self.helpbutton.clicked.connect(self.on_help_clicked)
        self.useinit.clicked.connect(self.on_useinit_clicked)
        self.kms_stop.clicked.connect(self.onkmsstop_clicked)
        self.kms_restart.clicked.connect(self.onkmsrestart_clicked)
        self.set_bias.clicked.connect(self.bias_bool)

    def bias_bool(self):
        self.bias_ready = True

    def onkmsrestart_clicked(self):
        subprocess.Popen(['ssh -T pi@kms python /home/pi/kms-dev/manual_sick_reset.py'],shell=True)

    def onkmsstop_clicked(self):
        subprocess.Popen(['ssh -T pi@kms python /home/pi/kms-dev/stop.py'],shell=True)

    def on_help_clicked(self):

        self.browser = QWebEngineView()
        local_url = QtCore.QUrl.fromLocalFile(directory.master_dir + "help_doc.html")
        self.browser.load(local_url)
        self.browser.show()

    def on_quitbutton_clicked(self, event=None):

        print("Running quit function")

        print('=== Setting Exit Flags ===')
        ut.mce_exit.set()
        ut.tel_exit.set()
        ut.kms_exit.set()
        ut.hk_exit.set()

        print('=== Stopping MCEs ===')

        # stop all of the mces with their own command
        if self.showmcedata == 'Yes' and self.mceson != 'MCE SIM':
            rc = self.readoutcard
            if self.readoutcard == 'All':
                rc = 's'
            for mce_index in range(2):
                if ut.which_mce[mce_index] == 1 :
                    subprocess.call('./coms/mce_stop.sh %i %s' % (mce_index, rc), shell=True)
                    subprocess.call('./coms/mce_stop_rsync.sh %i' % (mce_index), shell=True)

        # # stop the file transfer process to time-master
        # ~ if self.mceson != 'MCE SIM':
            # ~ subprocess.Popen(['./coms/hk_stop_sftp.sh'], shell=True)

        # self.clear_temp_files()

        # ~ monitor_thread = start_monitoring(seconds_frozen=2)
        # ~ print(monitor_thread)
        # ~ monitor_thread.stop()


        print('=== Closing Windows ===')
        for window in [self.startwindow, self.browser, self.newwindow, self.heatmapwindow, self.telescopewindow]:
            if window is not None:
                window.close()

        print('=== Closing Processes ===')
        for proc, name in zip([self.updater, self.tel_updater,self.kms_updater],['MCE','Telescope','KMS']):
            if proc is not None:
                while proc.isRunning():
                    print("Still waiting on " + name + " updater process...")
                    proc.wait(2000)
                print(name + " updater process ended")
            else:
                print(name + " updater process was not used")

        print('=== Application Exit ===')
        app.exit()

        print("=== System Exit ===")
        sys.exit()

    def clear_temp_files(self):

        print("Clearing out local temp files...")
        tmp_dirs = [
            directory.mce0_dir + 'temp.*',
            directory.mce1_dir + 'temp.*',
            directory.temp_dir + 'tele*',
            directory.hk_dir + 'omnilog*',
            ]
        for td in tmp_dirs:
            # os.remove doesn't support wildcards
            subprocess.call('rm ' + td, shell=True)

    def on_starttel_clicked(self):

        self.num_loop = self.numloop.text()
        self.sec = self.tel_sec.text()
        self.map_size = self.tel_map_size.text()
        self.map_len = self.tel_map_len.text()
        self.map_angle = self.tel_map_angle.text()
        self.coord1 = self.tel_coord1.text()
        self.coord2 = self.tel_coord2.text()
        self.epoch = self.tel_epoch.currentText()
        self.object = self.tel_object.text()
        self.inittel = self.init_tel.currentText()
        self.kmsonoff = self.kmsonofftext.currentText()
        self.step = self.tel_step.text()
        self.coord_space = self.map_space.currentText()
        self.map_size_unit = self.unit1.currentText()
        self.map_len_unit = self.unit6.currentText()
        self.map_angle_unit = self.unit2.currentText()
        self.step_unit = self.unit3.currentText()
        self.coord1_unit = self.unit4.currentText()
        self.coord2_unit = self.unit5.currentText()
        self.telescope_initialized = True

        if self.inittel == 'Yes':
            self.tel_scan = self.telescan.currentText()
            scans = ['1D Raster','2D Raster','Bowtie (constant el)','Pointing Cross']
            script = [raster_script_1d,raster_script_2d,bowtie_scan,point_cross]
            for scan in scans :
                if self.tel_scan == scan :
                    self.tel_script = script[scans.index(scan)]
            tel_message = 'TELESCOPE INITIALIZED'
            self.off = False

        elif self.inittel == 'No' :
            if self.kmsonoff == 'No':
                self.tel_script = ' '
                self.off = True
                tel_message = 'NO TELESCOPE SELECTED'
            if self.kmsonoff == 'Yes':
                self.tel_script = 'Tracker'
                self.off = True
                tel_message = 'KMS ONLY'

        elif self.inittel == 'Sim' :
            tel_message = 'TEL SIM SELECTED'
            self.tel_script = 'Sim'
            self.off = False

        else :
            tel_message = 'TRACKER DATA ONLY'
            self.tel_script = 'Tracker'
            self.off = False

        self.useinit.setEnabled(False)
        print(tel_message)

    def on_useinit_clicked(self):

        # mce params ========================
        self.observer = init.mce_dict["observer"]
        self.mceson = init.mce_dict["mceson"]
        self.datamode = init.mce_dict["datamode"]
        self.readoutcard = init.mce_dict["readoutcard"]
        self.framenumber = init.mce_dict["framenumber"]
        self.alpha = float(init.mce_dict["alpha"])
        self.timeinterval = init.mce_dict["timeinterval"]
        self.channeldelete = init.mce_dict["channeldelete"]
        self.showmcedata = init.mce_dict["showmcedata"]
        # =====================================

        # telescope params ====================
        self.num_loop = init.tel_dict["num_loop"]
        self.sec = init.tel_dict["sec"]
        self.map_size = init.tel_dict["map_size"]
        self.map_len = init.tel_dict["map_len"]
        self.map_angle = init.tel_dict["map_angle"]
        self.coord1 = init.tel_dict["coord1"]
        self.coord2 = init.tel_dict["coord2"]
        self.epoch = init.tel_dict["epoch"]
        self.object = init.tel_dict["object"]
        self.inittel = init.tel_dict["inittel"]
        self.kmsonoff = init.tel_dict["kmsonoff"]
        self.tel_scan = init.tel_dict["tel_scan"]
        self.step = init.tel_dict["step"]
        self.coord_space = init.tel_dict["coord_space"]
        self.map_size_unit = init.tel_dict["map_size_unit"]
        self.map_len_unit = init.tel_dict["map_len_unit"]
        self.map_angle_unit = init.tel_dict["map_angle_unit"]
        self.step_unit = init.tel_dict["step_unit"]
        self.coord1_unit = init.tel_dict["coord1_unit"]
        self.coord2_unit = init.tel_dict["coord2_unit"]
        # ==============================================================================
        self.starttel.setEnabled(True)
        self.useinit.setEnabled(True)


    #sets parameter variables to user input and checks if valid - will start MCE
    #and live graphing if they are

    def on_submitbutton_clicked(self):

        self.timestarted = datetime.datetime.utcnow().isoformat()

        # check if telescope has been started first
        if not self.telescope_initialized:
            print("Please Initialize Telescope First")
            self.warningbox('gui')
            return

        print(self.useinit.isEnabled())
        # sys.exit()
        if not self.useinit.isEnabled():
            print('I know useinit is false')
            #set variables to user input
            # observer ---------------------------------------
            self.observer = self.enterobserver.text()

            # which mces are active --------------------------
            self.mceson = self.whichmces.currentText()
            print(self.mceson)

            # data mode --------------------------------------
            self.datamode = self.enterdatamode.currentText()
            if self.datamode == 'Load Curves':
                self.loadcurve_flag = True
            else:
                self.loadcurve_flag = False
            mce_states = ['Error', 'SQ1 Feedback', 'Raw', 'Filtered SQ1 Feedback', 'Debugging', 'Mixed Mode (25:7)','Mixed Mode (22:10)','Mixed Mode (24:8)','Mixed mode (18:14)', 'Load Curves']
            #want loadcurve to be the same as ??
            #for now I'm going to say that the load curve is the same as RAw or SQ1 Feedback
            mce_states2 = [0,1,12,2,11,10,7,5,4, 12]

            for state in mce_states :
                if self.datamode == state :
                    self.datamode = mce_states2[mce_states.index(state)]
            # readout card ---------------------------------------------
            self.readoutcard = self.enterreadoutcard.currentIndex() - 1
            if self.readoutcard < 0:
                self.readoutcard = 'All'
                self.currentreadoutcard = 2
                self.currentreadoutcarddisplay = 'MCE 1 RC 2'

            # frame number ----------------------------------------------
            self.framenumber = self.enterframenumber.text()

            # heatmap error function ------------------------------------
            self.alpha = float(self.heatalpha.text())

            # how much data to view on screen at once -------------------
            self.timeinterval = self.entertimeinterval.text()

            # keep old channel data on graph ----------------------------
            self.channeldelete = self.enterchanneldelete.currentText()

            # keep mce data on screen -----------------------------------
            self.showmcedata = self.entershowmcedata.currentText()

        if self.inittel == 'Yes':
            if self.kmsonoff == 'Yes':
                self.kms_on_off = 3
            else :
                self.kms_on_off = 1

            if not self.useinit.isEnabled(): # only use self.telescan.currentText() if not using auto_fill
                self.tel_scan = self.telescan.currentText()
            scans = ['1D Raster','2D Raster','Bowtie (constant el)','Pointing Cross']
            script = [raster_script_1d,raster_script_2d,bowtie_scan,point_cross]
            for scan in scans :
                if self.tel_scan == scan :
                    self.tel_script = script[scans.index(scan)]
                    print(self.tel_script)
            tel_message = 'TELESCOPE INITIALIZED'
            self.off = False

        elif self.inittel == 'No' :
            if self.kmsonoff == 'Yes':
                self.kms_on_off = 2
                print(colored('I have set the kmsonoff to 2','red'))
            else :
                self.kms_on_off = 0
                print(colored('I have set the kmsonoff to 0','red'))
            self.tel_script = ' '
            self.off = True
            tel_message = 'NO TELESCOPE SELECTED'

        elif self.inittel == 'Sim' :
            tel_message = 'TEL SIM SELECTED'
            self.tel_script = 'Sim'
            self.off = False
            if self.kmsonoff == 'Yes':
                self.kms_on_off = 2
            else :
                self.kms_on_off = 0

        else :
            if self.kmsonoff == 'Yes':
                self.kms_on_off = 3
            else :
                self.kms_on_off = 1
            tel_message = 'TRACKER DATA ONLY'
            self.tel_script = 'Tracker'
            self.off = False

        print(tel_message)

        # -----------------------------------------------------------
        if self.mceson == 'MCE0':
            ut.which_mce[0] = 1
            ut.which_mce[1] = 0
            ut.which_mce[2] = 0
        elif self.mceson == 'MCE1':
            ut.which_mce[0] = 0
            ut.which_mce[1] = 1
            ut.which_mce[2] = 0
        elif self.mceson == 'MCE SIM':
            ut.which_mce[0] = 0
            ut.which_mce[1] = 0
            ut.which_mce[2] = 1
        else :
            ut.which_mce[0] = 1
            ut.which_mce[1] = 1
            ut.which_mce[2] = 0

        #check if parameters are valid - will create warning box if invalid
        if self.observer == '' or self.framenumber == '' or self.framenumber == '0'\
        or self.timeinterval == ''\
        or self.timeinterval == '0':
            self.warningbox('gui') # throw up a warning box
            # restart the gui window
            ex = MainWindow()
        elif self.showmcedata == 'No':
            self.submitbutton.setEnabled(False)
        else:
            dir = directory.master_dir
            if os.path.exists(dir + 'tempfiles/tempparameters.txt') :
                parafile = open(dir + 'tempfiles/tempparameters.txt', 'w')
                parafile.write(self.observer+'\n')
                parafile.write(str(self.datamode)+'\n')
                parafile.write(str(self.readoutcard)+' ')
                parafile.write(self.framenumber+'\n')
                parafile.write(self.timeinterval+'\n')
                parafile.write(self.channeldelete+'\n')
                parafile.write(self.timestarted+'\n')
                parafile.write(self.logtext.toPlainText())
                parafile.close()

            new_tempfile = shutil.copy(dir + 'tempfiles/tempparameters.txt',self.netcdfdir + '/log.txt')

            print(colored('Time Started: %s' % (self.timestarted),'magenta'))
            # self.p = int((50 * 10 ** 6) / (33 * 90 * ut.german_freq)) #calculation taken from UBC MCE Wiki

            # prevents user from re-activating everything
            self.submitbutton.setEnabled(False)


            if self.mceson != "MCE SIM" :

                # self.clear_temp_files()

                #set the data mode for both mces and start them running
                rc = self.readoutcard
                if self.readoutcard == 'All':
                    rc = 's'

                # Remote location to copy the mce sync script to
                SYNC_SCRIPT_DEST = '/data/cryo/mce_rsync.py'

                for mce_index in range(2):
                    if ut.which_mce[mce_index] == 1 :
                        print("Copying mce_rsync.py to mce%i..." % mce_index)
                        subprocess.call('scp ./coms/mce_rsync.py time@time-mce-%i:%s' % (mce_index, SYNC_SCRIPT_DEST), shell = True)
                        print("Changing data_mode on mce%i..." % mce_index)
                        subprocess.call('./coms/mce_cdm.sh %i a %s' % (mce_index, self.datamode), shell = True)
                        print("Clearing remote temp files on mce%i..." % mce_index)
                        subprocess.call('./coms/mce_del.sh %i' % (mce_index), shell=True)

                for mce_index in range(2):
                    if ut.which_mce[mce_index] == 1 :
                        print("Starting acquision on mce%i..." % mce_index)
                        cmd = './coms/mce_run.sh %i %s %s %s' % (mce_index, self.framenumber, rc, self.frameperfile)
                        print(cmd)
                        subprocess.Popen([cmd], shell = True)

                # start file transfer scripts
                for mce_index in range(2):
                    if ut.which_mce[mce_index] == 1 :
                        dirname = directory.mce_dir_template % mce_index
                        subprocess.Popen(['ssh -T time@time-mce-%i python3 %s time@time-master:%s' % (mce_index, SYNC_SCRIPT_DEST, dirname)], shell=True)

                time.sleep(2.0)

            # subprocess.Popen(['ssh -T time@time-hk python /home/time/TIME_Software/sftp/hk_sftp.py'], shell=True)
            if self.loadcurve_flag == True:
                data = np.zeros((33,32))

                self.startwindow.hide()

                self.newwindow = QtGui.QWidget()
                self.newwindow.setWindowTitle('TIME Live Data Viewer')
                self.newgrid = QtGui.QGridLayout()
                self.newgraphs = QtGui.QVBoxLayout()
                self.newwindow.setGeometry(10, 10, 1920, 1080)
                self.newwindow.setLayout(self.newgrid)
                self.newgrid.addLayout(self.newgraphs, 0,3,8,8)

                p = QtGui.QPalette()
                p.setBrush(QtGui.QPalette.Window, QtGui.QBrush(QtGui.QColor(255,255,255)))
                self.newwindow.setPalette(p)

                self.newquitbutton = QtGui.QVBoxLayout()
                self.newquitbutton.addWidget(self.quitbutton)
                # self.newgrid.addLayout(self.newquitbutton, 9,0,1,2)

                self.setnewrc = QtGui.QVBoxLayout()
                self.setnewrc.addWidget(self.changechan)
                self.newgrid.addLayout(self.setnewrc, 8,0,1,2)

                self.kmsstop = QtGui.QVBoxLayout()
                self.kmsstop.addWidget(self.kms_stop)
                self.newgrid.addLayout(self.kmsstop,6,0,1,2)

                self.kmsrestart = QtGui.QVBoxLayout()
                self.kmsrestart.addWidget(self.kms_restart)
                self.newgrid.addLayout(self.kmsrestart,7,0,1,2)

                self.bias_button = QtGui.QVBoxLayout()
                self.bias_button.addWidget(self.set_bias)
                self.newgrid.addLayout(self.bias_button, 9,0,1,2)
                # self.bias_ready = True
                self.init_lc_plots()
                self.channelselection()
                self.set_bias_levels()
                # self.initheatmap(data,data) # give first values for heatmap to create image scale
                # self.initfftgraph()
                # self.inittelescope()
                # self.initkmirrordata()

                sys.stdout.flush()
                sys.stderr.flush()
                self.newwindow.closeEvent = self.on_quitbutton_clicked
                self.newwindow.show()

            else:
                print('init normal plot!!!- ----------')
                data = np.zeros((33,32))

                self.startwindow.hide()

                self.newwindow = QtGui.QWidget()
                self.newwindow.setWindowTitle('TIME Live Data Viewer')
                self.newgrid = QtGui.QGridLayout()
                self.newgraphs = QtGui.QVBoxLayout()
                self.newwindow.setGeometry(10, 10, 1920, 1080)
                self.newwindow.setLayout(self.newgrid)
                self.newgrid.addLayout(self.newgraphs, 0,2,8,8)

                p = QtGui.QPalette()
                p.setBrush(QtGui.QPalette.Window, QtGui.QBrush(QtGui.QColor(255,255,255)))
                self.newwindow.setPalette(p)

                self.newquitbutton = QtGui.QVBoxLayout()
                self.newquitbutton.addWidget(self.quitbutton)
                self.newgrid.addLayout(self.newquitbutton, 9,0,1,2)

                self.setnewrc = QtGui.QVBoxLayout()
                self.setnewrc.addWidget(self.changechan)
                self.newgrid.addLayout(self.setnewrc, 8,0,1,2)

                self.kmsstop = QtGui.QVBoxLayout()
                self.kmsstop.addWidget(self.kms_stop)
                self.newgrid.addLayout(self.kmsstop,6,0,1,2)

                self.kmsrestart = QtGui.QVBoxLayout()
                self.kmsrestart.addWidget(self.kms_restart)
                self.newgrid.addLayout(self.kmsrestart,7,0,1,2)

                #start other plot making processes
                self.initplot()
                self.channelselection()
                self.initheatmap(data,data) # give first values for heatmap to create image scale
                self.initfftgraph()
                self.inittelescope()
                self.initkmirrordata()

                sys.stdout.flush()
                sys.stderr.flush()
                self.newwindow.closeEvent = self.on_quitbutton_clicked
                self.newwindow.show()

    #resets parameter variables after warning box is read
    def on_warningbutton_clicked(self):
        self.on_quitbutton_clicked()
    #creates inputs for user to enter parameters and creates 'Quit' button

    def on_set_chan_clicked(self):
        self.changechannel()
        self.changerow()

    def getparameters(self):
        #creating user input boxes
        self.enterobserver = QtGui.QLineEdit('VLB')
        self.enterobserver.setMaxLength(3)
        self.enterdatamode = QtGui.QComboBox()
        self.enterdatamode.addItems(
            ['Mixed Mode (25:7)', 'Error', 'SQ1 Feedback', 'Raw', 'Filtered SQ1 Feedback', 'Debugging', 'Mixed Mode (22:10)','Mixed Mode (24:8)','Mixed mode (18:14)', 'Load Curves'])
        self.whichmces = QtGui.QComboBox()
        self.whichmces.addItems(['MCE0','MCE1','Both','MCE SIM'])
        self.enterreadoutcard = QtGui.QComboBox()
        self.enterreadoutcard.addItem('All')
        for i in range(8):
            if i < 4:
                self.enterreadoutcard.addItem('MCE 0 RC %s' % (i % 4 + 1))
            else:
                self.enterreadoutcard.addItem('MCE 1 RC %s' % (i % 4 + 1))
        self.enterframenumber = QtGui.QLineEdit('1350000')
        self.enterframenumber.setMaxLength(9)
        self.heatalpha = QtGui.QLineEdit('0.1')
        # self.enterdatarate = QtGui.QLineEdit('45')
        self.entertimeinterval = QtGui.QLineEdit('120')
        self.enterchanneldelete = QtGui.QComboBox()
        self.enterchanneldelete.addItems(['No', 'Yes'])
        self.entershowmcedata = QtGui.QComboBox()
        self.entershowmcedata.addItems(['Yes', 'No'])

        self.mceGroupBox = QtGui.QGroupBox()
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
        self.parameters.addRow('Heatmap Alpha', self.heatalpha)
        # self.parameters.addRow('Data Rate', self.enterdatarate)
        self.parameters.addRow('Delete Old Columns', self.enterchanneldelete)
        self.parameters.addRow('Time Interval (s)', self.entertimeinterval)
        self.parameters.addRow('Show MCE Data', self.entershowmcedata)
        self.mceGroupBox.setLayout(self.parameters)

        # telescope options =================================================
        self.telescan = QtGui.QComboBox()
        self.telescan.addItems(['1D Raster','2D Raster','BowTie (constant el)','Pointing Cross'])

        self.numloop = QtGui.QLineEdit('2')

        self.tel_delay = QtGui.QLineEdit('0')

        self.init_tel = QtGui.QComboBox()
        self.init_tel.addItems(['No','Yes','Sim','Tracker'])

        self.kmsonofftext = QtGui.QComboBox()
        self.kmsonofftext.addItems(['No','Yes'])

        self.tel_sec = QtGui.QLineEdit('6')
        self.tel_map_len = QtGui.QLineEdit('1')
        self.tel_map_size = QtGui.QLineEdit('1')
        self.tel_step = QtGui.QLineEdit('0.001')
        self.tel_map_angle = QtGui.QLineEdit('0')
        self.tel_coord1 = QtGui.QLineEdit()
        self.tel_coord2 = QtGui.QLineEdit()
        self.tel_epoch = QtGui.QComboBox()
        self.tel_epoch.addItems(['B1950.0','Apparent','J2000.0'])
        self.tel_object = QtGui.QLineEdit('Mars')
        self.unit1 = QtGui.QComboBox()
        self.unit2 = QtGui.QComboBox()
        self.unit3 = QtGui.QComboBox()
        self.unit6 = QtGui.QComboBox()
        self.unit1.addItems(['arcsec','arcmin','deg'])
        self.unit2.addItems(['arcsec','arcmin','deg'])
        self.unit3.addItems(['arcsec','arcmin','deg'])
        self.unit6.addItems(['arcsec','arcmin','deg'])
        self.unit4 = QtGui.QComboBox()
        self.unit4.addItems(['RA','AZ'])
        self.unit5 = QtGui.QComboBox()
        self.unit5.addItems(['DEC','ALT'])
        self.map_space = QtGui.QComboBox()
        self.map_space.addItems(['RA','DEC','AZ','ALT'])

        self.telGroupBox = QtGui.QGroupBox()
        self.telparams = QtGui.QFormLayout()
        self.teltitle = QtGui.QLabel(self)
        self.teltitle.setAlignment(QtCore.Qt.AlignCenter)
        self.teltitle.setText('Telescope Parameters')
        self.telparams.addRow(self.teltitle)
        self.telparams.addRow('Activate Telescope', self.init_tel)
        self.telparams.addRow('Activate KMS', self.kmsonofftext)
        self.telparams.addRow('Scan Strategy', self.telescan)
        self.telparams.addRow('Constant Coordinate System', self.map_space)
        self.telparams.addRow('Delayed Start (sec)', self.tel_delay)
        self.telparams.addRow('Time to Traverse Scan Length (sec)', self.tel_sec)
        self.maplen_widget = QtGui.QHBoxLayout ()
        self.maplen_widget.addWidget(self.tel_map_len)
        self.maplen_widget.addWidget(self.unit6)
        self.numloop_widget = QtGui.QHBoxLayout()
        self.numloop_widget.addWidget(self.numloop)
        self.telparams.addRow('Number of Scans (1D Only)',self.numloop_widget)
        self.mapsize_widget = QtGui.QHBoxLayout()
        self.telparams.addRow('Map Len (2D only)',self.maplen_widget)
        self.mapsize_widget.addWidget(self.tel_map_size)
        self.mapsize_widget.addWidget(self.unit1)
        self.telparams.addRow('Map Size',self.mapsize_widget)
        self.mapangle_widget = QtGui.QHBoxLayout()
        self.mapangle_widget.addWidget(self.tel_map_angle)
        self.mapangle_widget.addWidget(self.unit2)
        self.telparams.addRow('Angle of Map Offset', self.mapangle_widget)
        self.telparams.addRow(self.mapangle_widget)
        self.vstep_widget = QtGui.QHBoxLayout()
        self.vstep_widget.addWidget(self.tel_step)
        self.vstep_widget.addWidget(self.unit3)
        self.telparams.addRow('Size of 2D Vertical Step', self.vstep_widget)
        self.coord1_widget = QtGui.QHBoxLayout()
        self.coord1_widget.addWidget(self.tel_coord1)
        self.coord1_widget.addWidget(self.unit4)
        self.coord2_widget = QtGui.QHBoxLayout()
        self.coord2_widget.addWidget(self.tel_coord2)
        self.coord2_widget.addWidget(self.unit5)
        self.telparams.addRow('Source Coord 1:', self.coord1_widget)
        self.telparams.addRow('Source Coord 2:', self.coord2_widget)
        self.telparams.addRow('Epoch of Observation', self.tel_epoch)
        self.telparams.addRow('Object Catalog Name', self.tel_object)
        self.starttel = QtGui.QPushButton('Initialize Telescope')
        self.starttel.setStyleSheet("background-color: blue")
        self.telparams.addRow(self.starttel)
        self.telGroupBox.setLayout(self.telparams)
        # =====================================================================

        self.useinit = QtGui.QPushButton('Auto-Fill from File')
        self.useinit.setStyleSheet("background-color: orange")
        self.initGroupBox = QtGui.QGroupBox()
        self.initparams = QtGui.QFormLayout()
        self.initparams.addRow(self.useinit)
        self.quitbutton = QtGui.QPushButton('Quit')
        self.quitbutton.setStyleSheet("background-color: red")
        self.helpbutton = QtGui.QPushButton('Help')
        self.helpbutton.setStyleSheet("background-color: yellow")
        self.submitbutton = QtGui.QPushButton('Submit')
        self.submitbutton.setStyleSheet("background-color: green")
        self.kms_stop = QtGui.QPushButton('KMS STOP')
        self.kms_stop.setStyleSheet("background-color: orange")
        self.set_bias = QtGui.QPushButton('Set Bias')
        self.set_bias.setStyleSheet("background-color: green")
        self.kms_restart = QtGui.QPushButton('KMS RESTART')
        self.kms_restart.setStyleSheet("background-color: yellow")
        self.initparams.addRow(self.helpbutton)
        self.initparams.addRow(self.quitbutton)
        self.initparams.addRow(self.submitbutton)
        self.initGroupBox.setLayout(self.initparams)

        # =====================================================================
        self.parameters = QtGui.QHBoxLayout()
        self.allbuttons = QtGui.QVBoxLayout()
        self.parametersquit = QtGui.QHBoxLayout()

        self.telbutton = QtGui.QHBoxLayout()
        self.telbutton.addWidget(self.telGroupBox)

        self.logbox = QtGui.QVBoxLayout()
        self.logform = QtGui.QFormLayout()
        self.logbox.addLayout(self.logform)
        self.logtitle = QtGui.QLabel(self)
        self.logtitle.setAlignment(QtCore.Qt.AlignCenter)
        self.logtitle.setText('Observer Log')
        self.logform.addRow(self.logtitle)
        self.logtext = QtGui.QTextEdit('Please make a note about the current run...')
        self.logtext.setFontPointSize(20)
        self.logbox.addWidget(self.logtext)
        # self.logtext.resize(640,640)

        # self.parameters.addWidget(self.telGroupBox)
        self.parameters.addLayout(self.telbutton)
        self.parameters.addWidget(self.mceGroupBox)
        self.parameters.addLayout(self.logbox)

        self.allbuttons.addLayout(self.parameters)
        self.allbuttons.addWidget(self.initGroupBox)
        self.parametersquit.setAlignment(QtCore.Qt.AlignCenter)
        self.parametersquit.addLayout(self.allbuttons)

        self.changechan = QtGui.QPushButton('Set New')
        self.changechan.setStyleSheet("background-color: blue")

        self.readoutcardselect = QtGui.QComboBox()
        self.selectchannel = QtGui.QComboBox()
        self.selectrow = QtGui.QComboBox()

        sys.stdout.flush()
        sys.stderr.flush()

    #creates input to change channel of live graph during operation, also adds
    #input for readout card if reading All readout cards

    def read_new_bias(self):
        ncols = 3
        self.is_checked_0 = np.zeros((32), dtype='bool')
        self.is_checked_1 = np.zeros((32), dtype='bool')
        for n in range(32):
            ind = n % ncols
            self.is_checked_0[n] = not self.bias_box_1[n].isChecked()
            self.is_checked_1[n] = not self.bias_box_2[n].isChecked()
        self.master_bias0 = int(self.master_b1.text())
        self.master_bias1 = int(self.master_b1.text())

        self.bias_0_vals[self.is_checked_0] = self.master_bias0
        self.bias_1_vals[self.is_checked_1] = self.master_bias1

        # self.bias_ready = True

    def set_bias_levels(self):
        ncols = 3

        self.b1_checkboxes = [QtGui.QGridLayout() for i in range(ncols)]
        self.master_bias_1 = QtGui.QFormLayout()
        self.master_b1 = QtGui.QLineEdit('2000')
        self.master_bias_1.addRow('mce0 Bias Level', self.master_b1)

        self.newgrid.addLayout(self.master_bias_1, 1, 0, 1, 2)
        self.bias_box_1 = [QtGui.QCheckBox() for i in range(32)]
        self.bias_levels = {}
        for n in range(32):
            self.bias_box_1[n].setText('col %s' % n)

            ind = n % ncols
            row = n // ncols
            self.b1_checkboxes[ind].addWidget(self.bias_box_1[n], row, 0, 1, 1)
        [self.newgrid.addLayout(self.b1_checkboxes[i], 2, i,1,1) for i in range(ncols)]

        self.b2_checkboxes = [QtGui.QGridLayout() for i in range(ncols)]
        self.master_bias_2 = QtGui.QFormLayout()
        self.master_b2 = QtGui.QLineEdit('2000')
        self.master_bias_2.addRow('mce1 Bias Level', self.master_b2)
        self.newgrid.addLayout(self.master_bias_2, 4, 0, 1, 2)
        self.bias_box_2 = [QtGui.QCheckBox() for i in range(32)]
        self.bias_levels = {}
        for n in range(32):
            self.bias_box_2[n].setText('col %s' % n)

            ind = n % ncols
            row = n // ncols
            self.b2_checkboxes[ind].addWidget(self.bias_box_2[n], row, 0, 1, 1)
        [self.newgrid.addLayout(self.b2_checkboxes[i], 5, i,1,1) for i in range(ncols)]

    def channelselection(self):

        self.channelreadoutbox1 = QtGui.QFormLayout()
        self.selectchannel1 = QtGui.QLineEdit('0')
        self.selectrow1 = QtGui.QLineEdit('0')
        self.row1 = int(self.selectrow1.text())
        self.channel1 = int(self.selectchannel1.text())
        self.channelreadoutbox1.addRow('Row1 [0-32]',self.selectrow1)
        self.channelreadoutbox1.addRow('Col1 [0-31]',self.selectchannel1)
        self.newgrid.addLayout(self.channelreadoutbox1, 0,0,1,2)

        self.channelreadoutbox2 = QtGui.QFormLayout()
        self.selectchannel2 = QtGui.QLineEdit('0')
        self.selectrow2 = QtGui.QLineEdit('0')
        self.row2 = int(self.selectrow2.text())
        self.channel2 = int(self.selectchannel2.text())
        self.channelreadoutbox2.addRow('Row2 [0-32]',self.selectrow2)
        self.channelreadoutbox2.addRow('Col2 [0-31]',self.selectchannel2)
        self.newgrid.addLayout(self.channelreadoutbox2, 3,0,1,2)

    #changes channel of live graph when user changes channel
    def changechannel(self):
        if int(self.selectchannel1.text()) <= 31 :
            if int(self.selectchannel1.text()) != self.channel1 :
                self.channel1 = int(self.selectchannel1.text())
                if self.i3 < 6 :
                    self.i3 += 1
                else :
                    self.i3 == 0
        else :
            os.system("mpg123 " + directory.master_dir + "warning3.mp3")
            self.warningbox(['rc_wrong','CHANNEL 1'])

        if int(self.selectchannel2.text()) <= 31 :
            if int(self.selectchannel2.text()) != self.channel2 :
                self.channel2 = int(self.selectchannel2.text())
                if self.i4 < 6 :
                    self.i4 += 1
                else :
                    self.i4 == 0
        else :
            os.system("mpg123 " + directory.master_dir + "warning3.mp3")
            self.warningbox(['rc_wrong','CHANNEL 2'])

    def changerow(self):
        if int(self.selectrow1.text()) <= 32 :
            if int(self.selectrow1.text()) != self.row1 :
                self.row1 = int(self.selectrow1.text())
                if self.i1 < 7 :
                    self.i1 += 1
                else :
                    self.i1 == 0
        else :
            os.system("mpg123 " + directory.master_dir + "warning3.mp3")
            self.warningbox(['rc_wrong','ROW 1'])

        if int(self.selectrow2.text()) <= 32 :
            if int(self.selectrow2.text()) != self.row2 :
                self.row2 = int(self.selectrow2.text())
                if self.i2 < 7 :
                    self.i2 += 1
                else :
                    self.i2 == 0
        else :
            os.system("mpg123 " + directory.master_dir + "warning3.mp3")
            self.warningbox(['rc_wrong','ROW 2'])

    def init_lc_plots(self):
        self.starttime = datetime.datetime.utcnow()
        # passes the variable set by the user to the graph (user sets timeinterval)
        self.totaltimeinterval = int(self.timeinterval)
        self.n_intervals = 1 #

        self.mce = 1 #want to check what this means ? need to review some of the code
        #want to store old data before we update to new data to keep the flow moving !
        self.data = [0, 0, 0]

        self.mcegraphdata1 = pg.ScatterPlotItem()
        self.mcegraphdata2 = pg.ScatterPlotItem()
        self.mcegraph1 = pg.PlotWidget()
        self.mcegraph2 = pg.PlotWidget()
        self.mcegraph1.addItem(self.mcegraphdata1)
        self.mcegraph2.addItem(self.mcegraphdata2)
        self.newgraphs.addWidget(self.mcegraph1, stretch=2)
        self.newgraphs.addWidget(self.mcegraph2, stretch=2)
        self.mcegraph1.setLabel('bottom', 'Bias Current [DAC]')
        self.mcegraph1.setLabel('left', 'OFfset SQ1 Feedback [DAC]')
        self.mcegraph1.setTitle('MCE0 Load Curve')
        self.graph1legend = self.mcegraph1.addLegend()

        self.mcegraph2.setLabel('bottom', 'Bias Current [$\\mu A$]')
        self.mcegraph2.setLabel('left', 'SQ1 Feedback [$\\mu A$]')
        self.mcegraph2.setTitle('MCE1 Load Curve')
        self.graph2legend = self.mcegraph2.addLegend()

        self.data_line_dict_1 = {}
        self.data_line_dict_2 = {}

        self.updater = MCEThread(offset = self.offset, flags = self.flags, netcdfdir = self.netcdfdir)
        self.updater.new_data.connect(self.update_lc_plot)
        self.updater.start()

        self.lc_indexer = 0
        self.old_lc = -1

        self.lc_queue = mp.Queue()
        rser_cr = {}
        self.bias_0_vals = np.zeros((32),dtype='int')
        self.bias_0_vals[:] = 3000
        self.bias_1_vals = np.zeros((32),dtype='int')
        self.bias_1_vals[:] = 2000
        self.bias_ready = False
        self.master_bias0 = 3000
        self.is_checked_0 = np.zeros((32), dtype='bool')
        self.is_checked_0[:] = True
        lc_p = mp.Process(name='append_data',target=self.loadcurve_thread, args=(self.lc_queue, self.lc_indexer, rser_cr, self.bias_0_vals, self.is_checked_0))
        # p2 = mp.Process(name='append_hk',target=append_hk.Time_Files(offset = self.offset).retrieve, args=(self.netcdfdir,))
        lc_p.start()


    def loadcurve_thread(self, lc_queue, lc_indexer, rser_cr, bias, columns, T=293):
        T = 293
        cols=32; rows=33
        init_bias = np.load(directory.time_analysis + 'bias_list_%s.npy'%(T),allow_pickle=True) #This file relies on read load curves being run at least once
        sys.path.append('/home/time/time_analysis/py/timefpu/')
        import calib.time202001 as calib
        bias_min = init_bias[:, 1]
        col_vals = tuple(np.where(columns == True)[0])

        col_str = '-c'
        for val in col_vals:
            col_str += ' %s' % val
        # opt_num_fin = init_bias[:, 3]
        data_name = 'iteration_%s' % lc_indexer
        count = 5000 - bias + 1
        str_list = tuple([data_name] + [bias[i] for i in range(bias.size)])
        # print('sending signal to bias detectors')
        print('ssh -T -X -n time@m192.168.1.81 python partial_iv_curve.py -r %s %s %s %s %s %s %s %s %s %s %s %s %s %s %s %s %s %s %s %s %s %s %s %s %s %s %s %s %s %s %s %s %s' % str_list)
        # script_path = 'ssh -X -n time@192.168.1.81 python /home/time/b3_analysis/load_curve/ivcurve_copy.py '
        # default_commands = ' --bias_start 5000 --zap_bias 8000 --zap_time 1 --settle_bias 5000 --settle_time 1 --bias_step -1 --bias_count %s --bias_pause 0.03 --bias_final %s --data_mode 10 -d %s' % (count, bias, data_name)
        # command = script_path + col_str + default_commands
        # print(command)
        dname = '/home/time/TIME_Software/main/tempfiles/temp_lc/' + data_name
        fname = os.path.join(dname, data_name)
        if lc_indexer is not 0:
            # subprocess.Popen([command], shell=True)
            subprocess.Popen(['ssh -T -X -n time@192.168.1.81 python /home/time/time_analysis/py/timefpu/partial_iv_curve.py -r %s %s %s %s %s %s %s %s %s %s %s %s %s %s %s %s %s %s %s %s %s %s %s %s %s %s %s %s %s %s %s %s %s' % str_list] ,shell=True)
            while not os.path.exists(fname):
                print('waiting for %s' %fname)
                time.sleep(2)

        folder = dname
        fname_full = '/home/time/TIME_Software/main/tempfiles/iv_pid375mK_opteff_300K/iv_pid375mK_opteff_300K'
        lower_lim = upper_lim = np.zeros((32))
        if lc_indexer == 0:
            rser = {}
            lc_queue.put([rser_cr, lower_lim, upper_lim])
            lc_data_arr = np.zeros((4, cols, rows, 5))
            np.save(directory.temp_lc + 'temp_cur_x_%s' % lc_indexer, lc_data_arr, allow_pickle=True)

            print('done making files')
        else:
            bias_x, bias_y = showivecg(fname)
            bias_y = bias_y.swapaxes(0,1)
            bias_max = np.argmax(bias)

            lc_data_arr = np.zeros((4, cols, rows, bias_x.shape[1]))

            lower_limits = np.zeros((32)); upper_limits = np.zeros((32))
            for mux_c in range(cols): #detector position
                for mux_r in range(rows): #detector frequency

                    lc_data_arr[2,mux_c,mux_r,:] = bias_x[mux_c]
                    lc_data_arr[3,mux_c,mux_r,:] = bias_y[mux_c, mux_r] * 1e-3 #kDAC

            rser_cr = {}
            print('putting loadcurve data into queue')
            lc_queue.put([rser_cr, lower_lim, upper_lim])
            print('making files')
            np.save(directory.temp_lc + 'temp_cur_x_%s' % lc_indexer, lc_data_arr, allow_pickle=True)
            print('done making files')
        return


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
        self.mcegraph1 = pg.PlotWidget()
        self.mcegraph2 = pg.PlotWidget()
        self.mcegraph1.addItem(self.mcegraphdata1)
        self.mcegraph2.addItem(self.mcegraphdata2)
        self.newgraphs.addWidget(self.mcegraph1, stretch=2)
        self.newgraphs.addWidget(self.mcegraph2, stretch=2)

        #add labels to graph
        self.mcegraph1.setLabel('bottom', 'Time [sec]')
        self.mcegraph1.setLabel('left', 'Counts [ADU]')
        self.mcegraph1.setTitle('MCE0 Raw Data')

        self.mcegraph2.setLabel('bottom', 'Time [sec]')
        self.mcegraph2.setLabel('left', 'Counts [ADU]')
        self.mcegraph2.setTitle('MCE1 Raw Data')

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

        if ut.which_mce[2] == 1 :
            self.roll_avg_1 = h1
            self.roll_avg_2 = h2

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
        # self.heatmap1.autoLevels()

        if ut.which_mce[0] == 1 or ut.which_mce[2] == 1:
            self.heatmap1.setImage(h1)
        # =========================================================================================================

        # heatmap for second MCE ==================================================================================
        self.heatmapplot2 = pg.PlotItem()
        self.heatmapplot2.setLabel('bottom', 'Row')
        self.heatmapplot2.setLabel('left', 'Channel')
        self.heatmapplot2.setTitle('MCE1 RMS Noise')

        self.heatmap2 = pg.ImageView(view= self.heatmapplot2)
        self.heatmap2.setPredefinedGradient('thermal')
        # self.heatmap2.autoLevels()

        if ut.which_mce[1] == 1 or ut.which_mce[2] == 1:
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
        # self.heatmap3.autoLevels()


        if ut.which_mce[0] == 1 or ut.which_mce[2] == 1:
            self.heatmap3.setImage(h1)
            self.heatmap3.setLevels(np.mean(h1)-np.var(h1),np.mean(h1)+np.var(h1))
            self.h1_var = np.var(h1)
            self.h1_avg = np.mean(h1)
        # ===========================================================================================================

        # heatmap for Raw Data MCE1 ==================================================================================
        self.heatmapplot4 = pg.PlotItem()
        self.heatmapplot4.setLabel('bottom', 'Row')
        self.heatmapplot4.setLabel('left', 'Channel')
        self.heatmapplot4.setTitle('MCE1 Averaged Signal')

        self.heatmap4 = pg.ImageView(view= self.heatmapplot4)
        self.heatmap4.setPredefinedGradient('thermal')
        # self.heatmap4.autoLevels()

        if ut.which_mce[1] == 1 or ut.which_mce[2] == 1:
            self.heatmap4.setImage(h2)
            self.heatmap4.setLevels(np.mean(h2)-np.var(h2),np.mean(h2)+np.var(h2))
            self.h2_var = np.var(h2)
            self.h2_avg = np.mean(h2)

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
        self.fftlegend = pg.LegendItem()
        self.fftgraph.addItem(self.fftlegend)
        self.newgraphs.addWidget(self.fftgraph, stretch=1)

    def initkmirrordata(self):
        # start the kms QThread
        if self.tel_script == 'point_cross.py' :
            # do something to set KMS in specific position before starting KMS thread
            print('No KMS!')
        if self.kms_on_off == 2 or self.kms_on_off == 3:
            self.kms_updater = KMS_Thread(kms_on_off = self.kms_on_off)
            self.kms_updater.new_kms_data.connect(self.updatekmirrordata)
            self.kms_updater.start()
            print('kms should be 1',self.kms_on_off)

        #place holder data
        self.parallacticangle = 0.0
        self.positionalerror = 0.0
        self.kmsstatus = 'Normal'
        self.status = ' '
        self.time = 0.0
        self.enc = 0.0

        self.parallacticangletext = QtGui.QLabel('Parallactic Angle: %0.2f' %(self.parallacticangle))
        self.parallacticangletext.setAlignment(QtCore.Qt.AlignCenter)
        self.positionalerrortext = QtGui.QLabel('Positional Error: %s' %(self.positionalerror))
        self.positionalerrortext.setAlignment(QtCore.Qt.AlignCenter)
        self.kmsstatustext = QtGui.QLabel('KMS Status Flag: %s' %(self.kmsstatus))
        self.kmsstatustext.setAlignment(QtCore.Qt.AlignCenter)
        self.kmstitle = QtGui.QLabel('Kmirror System Position and Status')
        self.kmstitle.setAlignment(QtCore.Qt.AlignCenter)
        self.statustext = QtGui.QLabel('Tel Status: %s' %(self.status))
        self.statustext.setAlignment(QtCore.Qt.AlignCenter)
        self.kmstimetext = QtGui.QLabel('UTC Time: %0.2f' %(self.time))
        self.kmstimetext.setAlignment(QtCore.Qt.AlignCenter)
        self.enctext = QtGui.QLabel('Encoder Position: %0.3f' %(self.enc))
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
        self.kmsparams.addWidget(self.enctext)
        self.kmsparams.addWidget(self.timetext)
        self.kmsgui.setLayout(self.kmsparams)
        self.newgrid.addWidget(self.kmsgui, 4, 0, 2, 2)

    def inittelescope(self):

        # start the telescope QThread
        self.tel_updater = Tel_Thread(flags = self.flags, tel_script = self.tel_script, off = self.off, sec = self.sec, map_size = self.map_size,\
                                    map_len = self.map_len, map_angle = self.map_angle, coord1 = self.coord1, coord1_unit = self.coord1_unit,\
                                    coord2 = self.coord2, coord2_unit = self.coord2_unit, epoch = self.epoch,\
                                    object = self.object, step = self.step, coord_space = self.coord_space, map_size_unit = self.map_size_unit,\
                                    map_len_unit = self.map_len_unit, map_angle_unit = self.map_angle_unit, step_unit = self.step_unit,\
                                    num_loop = self.num_loop, kms_on_off = self.kms_on_off)
        self.tel_updater.new_tel_data.connect(self.updatetelescopedata)
        self.tel_updater.start()
        sys.stdout.flush()
        sys.stderr.flush()

        # initialize printouts of current tele values not plotted
        self.patext = QtGui.QLabel('PA: -')
        self.slewtext = QtGui.QLabel('Slew Flag: -')
        self.timetext = QtGui.QLabel('UTC Time: -')
        self.timetext.setAlignment(QtCore.Qt.AlignCenter)
        self.barlabel = QtGui.QLabel('Scan Progress (%) ')
        self.progressbar = QtGui.QProgressBar()
        self.progressbar.setRange(0,100)
        self.progressbar.setTextVisible(True)

        # create space for tele printout values
        self.telescopedata = QtGui.QVBoxLayout()
        self.telescopedata.addWidget(self.barlabel)
        self.telescopedata.addWidget(self.progressbar)
        self.telescopedata.addWidget(self.patext)
        self.telescopedata.addWidget(self.slewtext)
        self.telescopedata.addWidget(self.timetext)

        # create plot object for alt-az graph
        self.altazgraph = pg.PlotWidget()
        self.altazgraphdata = pg.ScatterPlotItem()
        self.altazlinedata1 = pg.PlotCurveItem()
        self.altazlinedata2 = pg.PlotCurveItem()
        self.altazlinedata3 = pg.PlotCurveItem()
        self.altazlinedata4 = pg.PlotCurveItem()
        self.altazgraph.addItem(self.altazgraphdata)
        self.altazgraph.addItem(self.altazlinedata1)
        self.altazgraph.addItem(self.altazlinedata2)
        self.altazgraph.addItem(self.altazlinedata3)
        self.altazgraph.addItem(self.altazlinedata4)
        self.altazgraph.showGrid(x=True, y=True)
        self.altazgraph.setTitle('Alt-Az Graph')
        self.altazgraph.setLabel('left', 'alt')
        self.altazgraph.setLabel('bottom', 'az')

        # create plot object for ra-dec graph
        self.radecgraph = pg.PlotWidget()
        self.radecgraphdata = pg.ScatterPlotItem()
        self.radeclinedata1 = pg.PlotCurveItem()
        self.radeclinedata2 = pg.PlotCurveItem()
        self.radeclinedata3 = pg.PlotCurveItem()
        self.radeclinedata4 = pg.PlotCurveItem()
        self.radecgraph.addItem(self.radecgraphdata)
        self.radecgraph.addItem(self.radeclinedata1)
        self.radecgraph.addItem(self.radeclinedata2)
        self.radecgraph.addItem(self.radeclinedata3)
        self.radecgraph.addItem(self.radeclinedata4)
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

        if self.off == False and self.inittel != 'No' and self.inittel != 'Tracker':
            box_leftx,box_lefty,box_rightx,box_righty,box_topx,box_topy,box_botx,box_boty =\
            draw_box(self.coord1,self.coord1_unit,self.coord2,self.coord2_unit,self.coord_space,\
                        self.map_size,self.map_size_unit,self.map_len,self.map_len_unit)

            if self.coord_space == 'ALT' or self.coord_space == 'AZ' :
                self.altazlinedata1.setData(box_leftx,box_lefty,brush=pg.mkBrush('g'))
                self.altazlinedata2.setData(box_rightx,box_righty,brush=pg.mkBrush('g'))
                self.altazlinedata3.setData(box_topx,box_topy,brush=pg.mkBrush('g'))
                self.altazlinedata4.setData(box_botx,box_boty,brush=pg.mkBrush('g'))

            else :
                self.radeclinedata1.setData(box_leftx,box_lefty,brush=pg.mkBrush('g'))
                self.radeclinedata2.setData(box_rightx,box_righty,brush=pg.mkBrush('g'))
                self.radeclinedata3.setData(box_topx,box_topy,brush=pg.mkBrush('g'))
                self.radeclinedata4.setData(box_botx,box_boty,brush=pg.mkBrush('g'))
            self.telescopewindow.show()

        else :
            pass
        self.repeat = False

        self.alt = []
        self.az = []
        self.ra = []
        self.dec = []

    def updatekmirrordata(self,pa,status,time,enc_pos):

        # error checking based on status flags from kmirror
        kms_error = [10,11,12,13]
        if (status in kms_error) and (self.repeat == False) :
            os.system("mpg123 " + directory.master_dir + "klaxon.mp3")
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
            self.enc = enc_pos

            self.enctext.setText('Encoder Position %0.3f' %(self.enc))
            self.parallacticangletext.setText('Parallactic Angle: %0.2f' % (self.parallacticangle))
            self.positionalerrortext.setText('Positonal Error: %s' % (self.positionalerror))
            self.statustext.setText('Tel Current Status: %s' %(self.status))
            self.kmstimetext.setText('UTC Time: %0.3f' %(self.time))

    def updatefftgraph(self):
        #self.y and self.x are defined in updateplot
        self.fftgraph.setXRange(self.index, self.index + 1, padding=0)

        if ut.which_mce[0] == 1 :

            self.fftdata1 = np.fft.fft(self.y1)
            self.fftdata1 = np.asarray(self.fftdata1, dtype=np.float32)
            self.fftdata1[0] = self.fftdata1[-1]
            self.fftgraphdata1.setData(self.x, self.fftdata1, brush=pg.mkBrush('r'))
            # self.fftlegend.setItem(self.fftgraphdata1,'mce0')

        if ut.which_mce[1] == 1 :

            self.fftdata2 = np.fft.fft(self.y2)
            self.fftdata2 = np.asarray(self.fftdata2, dtype=np.float32)
            self.fftdata2[0] = self.fftdata2[-1]
            self.fftgraphdata2.setData(self.x, self.fftdata2, brush=pg.mkBrush('w'))
            # self.fftlegend.setItem(self.fftgraphdata2,'mce1')

        if ut.which_mce[2] == 1 :

            self.fftdata1 = np.fft.fft(self.y1)
            self.fftdata1 = np.asarray(self.fftdata1, dtype=np.float32)
            self.fftdata1[0] = self.fftdata1[-1]
            self.fftgraphdata1.setData(self.x, self.fftdata1, brush=pg.mkBrush('r'))
            # self.fftlegend.setItem(self.fftgraphdata1,'mce0')

            self.fftdata2 = np.fft.fft(self.y2)
            self.fftdata2 = np.asarray(self.fftdata2, dtype=np.float32)
            self.fftdata2[0] = self.fftdata2[-1]
            self.fftgraphdata2.setData(self.x, self.fftdata2, brush=pg.mkBrush('w'))
            # self.fftlegend.setItem(self.fftgraphdata2,'mce1')

    def updatetelescopedata(self,progress,pa,slew,alt,az,ra,dec,time):
        # error checking based on status flags from telescope
        tel_error = [10,11,12]

        if (slew in tel_error) and (self.repeat == False) :
            # use afplay for mac testing
            os.system("mpg123 " + directory.master_dir + "klaxon.mp3")
            self.repeat = True
            ut.tel_exit.set()
            ut.mce_exit.set()
            ut.kms_exit.set()
            ut.hk_exit.set()
            self.warningbox(['tel',slew]) #slew will be replaced with tel status flag over socket

        elif slew == 'done' :
            os.system("mpg123 " + directory.master_dir + "finished.mp3")
            self.repeat = True
            ut.tel_exit.set()
            ut.mce_exit.set()
            ut.kms_exit.set()
            ut.hk_exit.set()
            self.warningbox(['tel_stop','done'])

        else :
            # update text on window to reflect new data
            tel_flags = [0,1,2,3,4]
            tel_names = ['Idle','TC','-RA','+RA','TAZ']
            for i in range(len(tel_flags)):
                if slew == tel_flags[i]:
                    self.slewtext.setText('Slew Flag: %s' %(tel_names[i]))
            self.patext.setText('PA: %s' %(round(float(pa),2)))
            self.timetext.setText('UTC Time: %.2f'%(round(float(time),2)))

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
            self.progressbar.setValue(progress)

    def setColumnCount(self, legend, columnCount):
        """change the orientation of all items of the legend
        """
        def _addItemToLayout(legend, sample, label):
            col = legend.layout.columnCount()
            row = legend.layout.rowCount()
            if row:
                row -= 1
            nCol = legend.columnCount * 2
            # FIRST ROW FULL
            if col == nCol:
                for col in range(0, nCol, 2):
                    # FIND RIGHT COLUMN
                    if not legend.layout.itemAt(row, col):
                        break
                if col + 2 == nCol:
                    # MAKE NEW ROW
                    col = 0
                    row += 1
            legend.layout.addItem(sample, row, col)
            legend.layout.addItem(label, row, col + 1)

        legend.columnCount = columnCount
        legend.rowCount = int(len(legend.items) / columnCount)
        for i in range(legend.layout.count() - 1, -1, -1):
            legend.layout.removeAt(i)  # clear layout
        for sample, label in legend.items:
            _addItemToLayout(legend, sample, label)
        legend.updateSize()


    def update_lc_plot(self, h1, h2, index):
        # print('looping')
        self.read_new_bias()
        self.index = index

        self.i1 = self.i2 = self.i3 = self.i4 = 0
        new_channel = False
        plot_flag = False
        temp_file = directory.temp_lc + 'temp_cur_x_%s.npy' % self.lc_indexer
        if os.path.exists(temp_file):

            # print(self.lc_indexer, temp_file, os.path.exists(temp_file))
            if self.lc_indexer > self.old_lc: #for debugging !
                print('new data loaded')
                self.lc_data_arr = np.load(directory.temp_lc + 'temp_cur_x_%s.npy' % self.lc_indexer, allow_pickle=True)
                #lc_data_arr structure
                # 0 - final_resistance
                # 1 - final_power
                # 2 - bias_current
                # 3 - response_current
                # opt_num     = np.load(directory.temp_lc + 'opt_num_%s.npy' % self.lc_indexer, allow_pickle=True)
                # transition  = np.load(directory.temp_lc + 'transitions_%s.npy' % self.lc_indexer, allow_pickle=True)

                self.old_lc = self.lc_indexer
                plot_flag = True
                read_queue = self.lc_queue.get()
                self.rser_cr = read_queue[0]
                self.lc_lower_limit = read_queue[1]
                self.lc_upper_limit = read_queue[2]

        if self.bias_ready:
            # rser_cr = self.lc_queue.get()[0]
            self.lc_indexer += 1

            self.lc_queue = mp.Queue()

            lc_p = mp.Process(name='append_data',target=self.loadcurve_thread, args=(self.lc_queue, self.lc_indexer, self.rser_cr, self.bias_0_vals, self.is_checked_0))
            lc_p.start()
            self.bias_ready = False

            # T = '293' #perhaps we want to make this an argument that can be passed through the GUI
            # #when the load curve flag is set we get an array of y and x values
            ut.which_mce[0] = 1
            ut.which_mce[1] = 0
            ut.which_mce[2] = 0
            plot_flag = True

        if self.oldch1 != self.channel1 or self.oldch2 != self.channel2:
            print('changing to channel %s' % self.channel1)
            new_channel = True
            self.oldch1 = self.channel1
            self.oldch2 = self.channel2
        n = 32 #number of rows
        color_arr = cm.rainbow(np.linspace(0, 1, n)) * 255
        colors = color_arr[:,0:3]

        #there is a slight inefficiency here we probably don't want to redraw everytime we get a new set of data this should just be on the first pass
        if plot_flag and self.lc_indexer==0: #
            # self.channel1 = 6
            print('making plots!')
            col_x = self.lc_data_arr[2,self.channel1,:,:]; col_y = self.lc_data_arr[3,self.channel1,:,:]
            low_lim = self.lc_lower_limit[self.channel1]
            up_lim = self.lc_upper_limit[self.channel1]
            # pen = pg.mkPen(color='w')
            # self.lower_plot0 = self.mcegraph1.plot([low_lim,low_lim], [np.nanmin(col_y), np.nanmax(col_y)], pen=pen)
            # pen = pg.mkPen(color='r')
            # self.upper_plot0 = self.mcegraph1.plot([up_lim, up_lim], [np.nanmin(col_y), np.nanmax(col_y)], pen=pen)
            for r in range(n):
                color = colors[r]
                pen = pg.mkPen(color=color)
                # self.mcegraph1.setXRange(np.nanmin(self.lc_data_arr[2,:,:,:]), np.nanmax(self.lc_data_arr[2,:,:,:])*1.4, padding=0)
                # self.mcegraph2.setXRange(np.nanmin(self.lc_data_arr[2,:,:,:]), np.nanmax(self.lc_data_arr[2,:,:,:])*1.4, padding=0)
                self.mcegraph1.setXRange(500, 600, padding=0)
                self.mcegraph2.setXRange(500, 600, padding=0)
                # self.mcegraph1.setYRange(np.nanmin(self.lc_data_arr[3,:,:,:]), np.nanmax(self.lc_data_arr[3,:,:,:])*1.4, padding=0)
                # self.mcegraph2.setYRange(np.nanmin(self.lc_data_arr[3,:,:,:]), np.nanmax(self.lc_data_arr[3,:,:,:])*1.4, padding=0)
                self.mcegraph1.setYRange(-20, 15, padding=0)
                self.mcegraph2.setYRange(-20, 15, padding=0)
                self.data_line_dict_1[r] =  self.mcegraph1.plot(col_x[r], col_y[r], pen=pen, name='row %s' % r)
                pen = pg.mkPen(color=color)
                self.data_line_dict_2[r] =  self.mcegraph2.plot(col_x[r], col_y[r], pen=pen, name='row %s' % r)

            self.setColumnCount(self.graph1legend, 5)
            self.setColumnCount(self.graph2legend, 5)
        if new_channel:
            col_x = self.lc_data_arr[2,self.channel1,:,:]; col_y = self.lc_data_arr[3,self.channel1,:,:]
            low_lim = self.lc_lower_limit[self.channel1]
            up_lim = self.lc_upper_limit[self.channel1]

            # self.lower_plot0.setData([low_lim, low_lim], [np.nanmin(col_y), np.nanmax(col_y)])
            # self.upper_plot0.setData([up_lim, up_lim], [np.nanmin(col_y), np.nanmax(col_y)])
            for r in range(n):
                self.data_line_dict_1[r].setData(col_x[r], col_y[r])
                self.data_line_dict_2[r].setData(col_x[r], col_y[r])
                # self.mcegraph1.setYRange(np.nanmin(col_y), np.nanmax(col_y)*1.4, padding=0)
                # self.mcegraph2.setYRange(np.nanmin(col_y), np.nanmax(col_y)*1.4, padding=0)

        # self.graph1legend.setColumns(5)
        # self.graph2legend.setColumns(5)


    def updateplot(self,h1,h2,index):

        self.index = index
        self.starttime = datetime.datetime.utcnow()

        # parsing mce array for graph data ========================
        if ut.which_mce[0] == 1 :

            y1 = np.asarray(h1)[self.row1,self.channel1,:]
            self.y1 = y1

        if ut.which_mce[1] == 1 :

            y2 = np.asarray(h2)[self.row2,self.channel2,:]
            self.y2 = y2

        if ut.which_mce[2] == 1 :

            y1 = np.asarray(h1)[self.row1,self.channel1,:]
            self.y1 = y1

            y2 = np.asarray(h2)[self.row2,self.channel2,:]
            self.y2 = y2



        #creates x values for current time interval and colors points based on current channel ===
        self.endtime = datetime.datetime.utcnow()
        self.timetaken = self.endtime - self.starttime

        x = np.linspace(self.index,self.index + 1,self.frameperfile)
        self.x = x

        syms = ['d','o','s','t','+','d','o'] #these are the actual symbols
        symbols = ['b','r','g','y','c','m','k','w'] #these represent colors
        # =====================================================================================
        # This handles the normal plot of MCE points
        # if not self.loadcurve_flag:
        # if self.loadcurve_flag:
        #
        #     if self.index != 0:
        #         #color keys
        #         self.pointcolor1 = []
        #
        #         color=cm.rainbow(np.linspace(0,1,32)) #32 is the number of rows
        #         for i in range(32): #iterate each row, might want to change the 32 to be dynamic if rows are missing
        #         #or they could just be nans in which case we do not care!
        #             self.pointcolor1.extend([pg.mkBrush(color[i]) for j in range(self.frameperfile)])
        #             self.pointcolor2.extend([pg.mkBrush(color[i]) for j in range(self.frameperfile)])

        if self.index != 0 :
            #picks color based on current channel =============================================
            self.pointcolor1 = []
            self.pointcolor1.extend([pg.mkBrush(symbols[self.i1]) for j in range(self.frameperfile)])
            self.pointcolor2 = []
            self.pointcolor2.extend([pg.mkBrush(symbols[self.i2]) for j in range(self.frameperfile)])
            # =================================================================================================================
            # changes symbols for viewing different RC cards on same plot =====================
            self.pointsymbol1 = []
            self.pointsymbol1.extend([syms[self.i3] for j in range(self.frameperfile)])
            self.pointsymbol2 = []
            self.pointsymbol2.extend([syms[self.i4] for j in range(self.frameperfile)])

        else :
            self.pointcolor1 = [pg.mkBrush(symbols[0]) for j in range(self.frameperfile)]
            self.pointcolor2 = [pg.mkBrush(symbols[0]) for j in range(self.frameperfile)]
            self.pointsymbol1 = [syms[0] for j in range(self.frameperfile)]
            self.pointsymbol2 = [syms[0] for j in range(self.frameperfile)]
            self.i1 = 0
            self.i2 = 0
            self.i3 = 0
            self.i4 = 0

        #============================================================================================================

        #creates graphdata item on first update
        if self.index == 0:
            self.mcegraph1.setXRange(self.index, self.index + self.totaltimeinterval - 1, padding=0)
            self.mcegraph2.setXRange(self.index, self.index + self.totaltimeinterval - 1, padding=0)
            self.updatefftgraph()

            self.data[0] = x

            if ut.which_mce[0] == 1 :
                self.data[1] = y1
                self.mcegraph1.addItem(self.mcegraphdata1)

            if ut.which_mce[1] == 1 :
                self.mcegraph2.addItem(self.mcegraphdata2)
                self.data[2] = y2

            if ut.which_mce[2] == 1 :
                self.data[1] = y1
                self.mcegraph1.addItem(self.mcegraphdata1)

                self.mcegraph2.addItem(self.mcegraphdata2)
                self.data[2] = y2

            if self.readoutcard == 'All':

                if ut.which_mce[0] == 1 :
                    self.mcegraphdata1.setData(x, y1, brush=self.pointcolor1, symbol=self.pointsymbol1)
                    # self.mcegraphdata1.setData(x,y1)
                if ut.which_mce[1] == 1 :
                    self.mcegraphdata2.setData(x, y2, brush=self.pointcolor2, symbol=self.pointsymbol2)
                    # self.mcegraphdata2.setData(x,y2)
                if ut.which_mce[2] == 1 :
                    self.mcegraphdata1.setData(x, y1, brush=self.pointcolor1, symbol=self.pointsymbol1)
                    self.mcegraphdata2.setData(x, y2, brush=self.pointcolor2, symbol=self.pointsymbol2)

            else:

                if ut.which_mce[0] == 1 :
                    self.mcegraphdata1.setData(x, y1, brush=self.pointcolor1)
                if ut.which_mce[1] == 1 :
                    self.mcegraphdata2.setData(x, y2, brush=self.pointcolor2)
                if ut.which_mce[2] == 1 :
                    self.mcegraphdata1.setData(x, y1, brush=self.pointcolor1)
                    self.mcegraphdata2.setData(x, y2, brush=self.pointcolor2)

            self.oldch1 = self.channel1
            self.oldch2 = self.channel2
            # updates oldgraph data
            self.data[0] = x

            if ut.which_mce[0] == 1 :
                self.data[1] = y1
            if ut.which_mce[1] == 1 :
                self.data[2] = y2
            if ut.which_mce[2] == 1 :
                self.data[1] = y1
                self.data[2] = y2

            self.n_interval += 1 # update to keep graph going
        # ===========================================================================================================
        #clears graphdata and updates old graph after the total time interval has passed
        elif self.n_interval == self.totaltimeinterval :
            # self.oldmcegraph.setXRange(self.index - self.frameperfile, self.index + self.totaltimeinterval - 1 - self.frameperfile, padding=0)
            self.mcegraph1.setXRange(self.index, self.index + self.totaltimeinterval - 1, padding=0)
            self.mcegraph2.setXRange(self.index, self.index + self.totaltimeinterval - 1, padding=0)
            self.data[0] = x

            if ut.which_mce[0] == 1 :
                self.data[1] = y1
                # self.oldmcegraphdata1.setData(self.data[0], self.data[1])
                self.mcegraphdata1.clear()

            if ut.which_mce[1] == 1 :
                self.data[2] = y2
                # self.oldmcegraphdata2.setData(self.data[0], self.data[2])
                self.mcegraphdata2.clear()

            if ut.which_mce[2] == 1 :
                self.data[1] = y1
                # self.oldmcegraphdata1.setData(self.data[0], self.data[1])
                self.mcegraphdata1.clear()

                self.data[2] = y2
                # self.oldmcegraphdata2.setData(self.data[0], self.data[2])
                self.mcegraphdata2.clear()

            if self.readoutcard == 'All':
                if ut.which_mce[0] == 1 :
                    self.mcegraphdata1.setData(x, y1, brush=self.pointcolor1, symbol=self.pointsymbol1)
                    # self.mcegraphdata1.setData(x,y1)
                if ut.which_mce[1] == 1 :
                    self.mcegraphdata2.setData(x, y2, brush=self.pointcolor2, symbol=self.pointsymbol2)
                    # self.mcegraphdata1.setData(x,y2)

            else:
                if ut.which_mce[0] == 1 :
                    self.mcegraphdata1.setData(x, y1, brush=self.pointcolor1)
                if ut.which_mce[1] == 1 :
                    self.mcegraphdata2.setData(x, y2, brush=self.pointcolor2)
                if ut.which_mce[2] == 1 :
                    self.mcegraphdata1.setData(x, y1, brush=self.pointcolor1)
                    self.mcegraphdata2.setData(x, y2, brush=self.pointcolor2)

            self.data = [0, 0, 0]
            # updates oldgraphdata after total time interval is reached
            self.data[0] = x

            if ut.which_mce[0] == 1 :
                self.data[1] = y1
            if ut.which_mce[1] == 1 :
                self.data[2] = y2
            if ut.which_mce[2] == 1 :
                self.data[1] = y1
                self.data[2] = y2
        #testf
            self.n_interval = 0 #reset counter
        # ==============================================================================================================
        #updates graph, if channel delete is set to yes will clear data first
        else:
            #TODO: fix
            if ut.which_mce[0] == 1 and ut.which_mce[1] == 1 :
                self.updateheatmap(h1,h2) # give first values for heatmap to create image scale
            elif ut.which_mce[0] == 1 :
                dummy = []
                self.updateheatmap(h1,dummy)
            elif ut.which_mce[2] == 1 :
                self.updateheatmap(h1,h2)
            else :
                dummy = []
                self.updateheatmap(dummy,h2)
            if not self.loadcurve_flag:

                self.updatefftgraph()

            if self.channeldelete == 'Yes' and self.oldch1 != self.channel1 and self.oldch2 != self.channel2:

                if ut.which_mce[0] == 1 :
                    self.mcegraphdata1.clear()
                if ut.which_mce[1] == 1 :
                    self.mcegraphdata2.clear()
                if ut.which_mce[2] == 1 :
                    self.mcegraphdata1.clear()
                    self.mcegraphdata2.clear()

                if self.readoutcard == 'All':
                    if ut.which_mce[0] == 1 :
                        self.mcegraphdata1.setData(x, y1, brush=self.pointcolor1, symbol=self.pointsymbol1)
                        # self.mcegraphdata1.setData(x,y1)
                    if ut.which_mce[1] == 1 :
                        self.mcegraphdata2.setData(x, y2, brush=self.pointcolor2, symbol=self.pointsymbol2)
                        # self.mcegraphdata1.setData(x,y2)
                    if ut.which_mce[2] == 1 :
                        self.mcegraphdata1.setData(x, y1, brush=self.pointcolor1, symbol=self.pointsymbol1)
                        self.mcegraphdata2.setData(x, y2, brush=self.pointcolor2, symbol=self.pointsymbol2)

                else:
                    if ut.which_mce[0] == 1 :
                        self.mcegraphdata1.setData(x, y1, brush=self.pointcolor1)
                    if ut.which_mce[1] == 1 :
                        self.mcegraphdata2.setData(x, y2, brush=self.pointcolor2)
                    if ut.which_mce[2] == 1 :
                        self.mcegraphdata1.setData(x, y1, brush=self.pointcolor1)
                        self.mcegraphdata2.setData(x, y2, brush=self.pointcolor2)

            else:
                if self.readoutcard == 'All':
                    if ut.which_mce[0] == 1 :
                        self.mcegraphdata1.addPoints(x, y1, brush=self.pointcolor1, symbol=self.pointsymbol1)
                        # self.mcegraphdata1.setData(x,y1)
                    if ut.which_mce[1] == 1 :
                        self.mcegraphdata2.addPoints(x, y2, brush=self.pointcolor2, symbol=self.pointsymbol2)
                        # self.mcegraphdata1.setData(x,y2)
                    if ut.which_mce[2] == 1 :
                        self.mcegraphdata1.addPoints(x, y1, brush=self.pointcolor1, symbol=self.pointsymbol1)
                        self.mcegraphdata2.addPoints(x, y2, brush=self.pointcolor2, symbol=self.pointsymbol2)

                else:
                    if ut.which_mce[0] == 1 :
                        self.mcegraphdata1.addPoints(x, y1, brush=self.pointcolor1)
                    if ut.which_mce[1] == 1 :
                        self.mcegraphdata2.addPoints(x, y2, brush=self.pointcolor2)
                    if ut.which_mce[2] == 1 :
                        self.mcegraphdata1.addPoints(x, y1, brush=self.pointcolor1)
                        self.mcegraphdata2.addPoints(x, y2, brush=self.pointcolor2)


            # updates old data for when graph resets
            np.append(self.data[0],x) # doesn't create a new array but adds to existing

            if ut.which_mce[0] == 1 :
                np.append(self.data[1],y1)
            if ut.which_mce[1] == 1 :
                np.append(self.data[2],y2)
            if ut.which_mce[2] == 1 :
                np.append(self.data[1],y1)
                np.append(self.data[2],y2)
            self.n_interval += 1
        # =================================================================================================================
        self.oldch1 = self.channel1
        self.oldch2 = self.channel2
        # =================================================================================================================

    def updateheatmap(self,h1,h2):

        if ut.which_mce[0] == 1 or ut.which_mce[2] == 1:

            m1 = np.empty([h1.shape[0],h1.shape[1]],dtype=np.float32)
            for b in range(h1.shape[0]):
                for c in range(h1.shape[1]):
                    z1 = np.std(h1[b,c,:])
                    if z1 != 0.0 :
                        m1[b][c] = np.log(z1)
                    else :
                        m1[b][c] = None
            b = 0
            c = 0

            d1 = np.empty([h1.shape[0],h1.shape[1]],dtype=np.float32)
            for b in range(h1.shape[0]):
                for c in range(h1.shape[1]):
                    d1[b][c] = (np.mean(h1[b,c,:],dtype=np.float32))

            b = 0
            c = 0
            # std = np.std(d1)
            # bad_dets = np.where(np.abs(d1) > std)[0]
            # d1[bad_dets] = 0


            self.heatmap1.setImage(m1)

            d1_avg = np.empty([33,32])

            for b in range(h1.shape[0]):
                for c in range(h1.shape[1]):
                    self.roll_avg_1[b][c] = ((1-self.alpha)*self.roll_avg_1[b][c]) + (self.alpha * d1[b][c])
                    d1_avg[b][c] = d1[b][c] - self.roll_avg_1[b][c]

            # std = np.std(d1_avg)
            # bad_dets = np.where(np.abs(d1_avg) > std)[0]
            # d1_avg[bad_dets] = np.nan

            self.heatmap3.setImage(d1_avg)
            # self.heatmap3.setLevels(self.h1_var - self.h1_avg , self.h1_var + self.h1_avg)
            # self.heatmap3.setLevels(-6 ,6)

        if ut.which_mce[1] == 1 or ut.which_mce[2] == 1:

            # ---------------------------------------------------------
            m2 = np.empty([h2.shape[0],h2.shape[1]],dtype=np.float32)
            for b in range(h2.shape[0]):
                for c in range(h2.shape[1]):
                    z2 = np.std(h2[b,c,:])
                    if z2 != 0.0 :
                        m2[b][c] = np.log(z2)
                    else :
                        m2[b][c] = None

            b = 0
            c = 0

            d2 = np.empty([h2.shape[0],h2.shape[1]],dtype=np.float32)
            for b in range(h2.shape[0]):
                for c in range(h2.shape[1]):
                    d2[b][c] = (np.mean(h2[b,c,:],dtype=np.float32))


            b = 0
            c = 0
            # ----------------------------------------------------------

            self.heatmap2.setImage(m2)

            d2_avg = np.empty([33,32],dtype=np.float32)

            for b in range(h2.shape[0]):
                for c in range(h2.shape[1]):
                    self.roll_avg_2[b][c] = ((1-self.alpha)*self.roll_avg_2[b][c]) + (self.alpha * d2[b][c])
                    d2_avg[b][c] = d2[b][c] - self.roll_avg_2[b][c]


            # std = np.std(d1_avg)
            # bad_dets = np.where(np.abs(d_avg) > std)[0]
            # d1_avg[bad_dets] = np.nan
            # self.heatmap3.setImage(d1_avg)
            self.heatmap4.setImage(d2_avg)
            # self.heatmap4.setLevels(self.h2_var - self.h2_avg , self.h2_var + self.h2_avg)


    def warningbox(self,message): # message is a tuple
        if message[0] == 'gui' :
            parameterwarning = QtGui.QMessageBox()
            parameterwarning.setIcon(QtGui.QMessageBox.Warning)
            parameterwarning.setText('Error %s: One or more parameters not entered correctly!' %(message[1]))
            parameterwarning.setStandardButtons(QtGui.QMessageBox.Ok)
            parameterwarning.setWindowTitle('Parameter Warning')
            parameterwarning.exec_()
        elif message[0] == 'rc_wrong' :
            parameterwarning = QtGui.QMessageBox()
            parameterwarning.setIcon(QtGui.QMessageBox.Warning)
            parameterwarning.setText('Error: %s entered incorrectly' %(message[1]))
            parameterwarning.setStandardButtons(QtGui.QMessageBox.Ok)
            parameterwarning.setWindowTitle('Parameter Warning')
            parameterwarning.exec_()
        elif message[0] == 'kms' :
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
        queue = mp.Queue()
        p = mp.Process(name='append_data',target=append_data.Time_Files(flags = self.flags, offset = self.offset).retrieve, args=(queue,self.netcdfdir,))
        # p2 = mp.Process(name='append_hk',target=append_hk.Time_Files(offset = self.offset).retrieve, args=(self.netcdfdir,))
        p.start()
        # p2.start()
        last_time = 0

        while not ut.mce_exit.is_set():

            time.sleep(0.01) # Rate limit

            if time.time() - last_time > 5:
                # print("MCEThread.run is still alive")
                last_time = time.time()

            if queue.empty():
                continue

            stuff = queue.get()
            if ut.which_mce[0] == 1 and ut.which_mce[1] == 1 :
                self.new_data.emit(stuff[0],stuff[1],stuff[2])
            elif ut.which_mce[0] == 1 :
                dummy = []
                self.new_data.emit(stuff[0],dummy,stuff[2])
            elif ut.which_mce[2] == 1 :
                self.new_data.emit(stuff[0],stuff[1],stuff[2])
            else :
                dummy = []
                self.new_data.emit(dummy,stuff[1],stuff[2])

        print("MCEThread.run is waiting for subprocesses to join")
        p.join()
        # ~ p2.join()

        print("MCEThread.run is exiting")
        sys.stdout.flush()

class Tel_Thread(QtCore.QThread):

    new_tel_data = QtCore.pyqtSignal(object,object,object,object,object,object,object,object)

    def __init__(self, flags, tel_script, off, sec, map_size, map_len, map_angle, coord1, coord1_unit, coord2,\
                    coord2_unit, epoch, object, step, coord_space, map_size_unit,\
                    map_len_unit, map_angle_unit, step_unit, num_loop, kms_on_off, parent = None):

        QtCore.QThread.__init__(self, parent)
        self.off = off
        self.tel_script = tel_script
        self.sec = sec
        self.map_size = map_size
        self.map_len = map_len
        self.map_angle = map_angle
        self.coord1 = coord1
        self.coord2 = coord2
        self.epoch = epoch
        self.object = object
        self.flags = flags
        self.step = step
        self.step_unit = step_unit
        self.map_angle_unit = map_angle_unit
        self.map_size_unit = map_size_unit
        self.map_len_unit = map_len_unit
        self.coord_space = coord_space
        self.coord1_unit = coord1_unit
        self.coord2_unit = coord2_unit
        self.numloop = num_loop
        self.kms_on_off = kms_on_off

    def __del__(self):
        ut.tel_exit.set()

    def run(self):
        if self.off == False :

            # turn on only the script that activates tracker and sends data packets
            # does not move the telescope

            if self.tel_script == 'Tracker':
                from tel_tracker import start_tracker, turn_on_tracker
                queue = mp.Queue()
                '''  This has been deprecated. Need access to socket for shutdown after scan finished.
                # p1 = mp.Process(name='turn_on_tracker',target = turn_on_tracker, args=(self.kms_on_off,))
                # p1.start()
                '''
                PORT = 1806
                s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
                s.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
                s.bind(('',6666))
                s.connect(('192.168.1.252',PORT))
                print('Socket Connected')

                s.send('TIME_START_TELEMETRY %s'.encode() %(kms_on_off))
                reply = s.recv(1024).decode("ascii")
                print(reply)


                time.sleep(0.1) # give tracker time to turn on before accepting packets
                p = mp.Process(name='start_tracker',target= start_tracker, args=(queue,))
                p.start()
                sys.stdout.flush()
                sys.stderr.flush()

                while True :
                    if not ut.tel_exit.is_set() :
                        time.sleep(0.01) # Rate limit
                        if queue.empty():
                            continue # No new data, don't block in recv()
                        tel_stuff = queue.get()
                        with self.flags.get_lock() :
                            self.flags[0] = int(tel_stuff[1]) #update flags passed to netcdf data
                        progress = 0.0
                        self.new_tel_data.emit(progress,tel_stuff[0],tel_stuff[1],tel_stuff[2],tel_stuff[3],tel_stuff[4],tel_stuff[5],tel_stuff[6])
                        time.sleep(0.01)
                        sys.stdout.flush()
                        sys.stderr.flush()

                    else :
                        self.new_tel_data.emit(0,0,'done',0,0,0,0,0)
                        if self.tel_script == 'Tracker':
                            # send shutdown sequence to close telemetry
                            s.send('TIME_START_TELEMETRY 0'.encode())
                            s.shutdown(1)
                            s.close()
                        print(colored('Telescope Scan Completed!','green'))
                        break

            # fake data is generated for both kmirror and telescope
            elif self.tel_script == 'Sim' :
                print(colored('TEL SIM STARTED','red'))
                tele_array = np.zeros((20,20),dtype=float)
                np.save(directory.temp_dir + 'tele_packet_off1.npy',tele_array)
                time.sleep(0.01)
                np.save(directory.temp_dir + 'tele_packet_off2.npy',tele_array)

                queue = mp.Queue()
                p = mp.Process(name='fake_tel.TIME_TELE().start_tel',target=fake_tel.TIME_TELE().start_tel, args=(queue,self.map_len,self.map_len_unit,self.map_size,self.map_size_unit,self.sec,\
                                                                            self.coord1,self.coord1_unit,self.coord2,self.coord2_unit,self.coord_space,\
                                                                            self.step,self.step_unit,self.numloop,self.kms_on_off))
                p.start()

                while True :
                    if not ut.tel_exit.is_set() :
                        time.sleep(0.01) # Rate limit
                        if queue.empty():
                            continue # No new data, don't block in recv()
                        tel_stuff = queue.get()
                        with self.flags.get_lock() :
                            self.flags[0] = int(tel_stuff[1]) #update flags passed to netcdf data
                        self.new_tel_data.emit(tel_stuff[0],tel_stuff[1],tel_stuff[2],tel_stuff[3],tel_stuff[4],tel_stuff[5],tel_stuff[6],tel_stuff[7])
                    else :
                        self.new_tel_data.emit(0,0,'done',0,0,0,0,0)
                        print(colored('Telescope Scan Completed!','green'))
                        break

            else :
                # this will start one of several movement scripts
                queue = mp.Queue() # this is for tracker
                queue2 = mp.Queue() # this is for pos_calculator
                p = mp.Process(name='self.tel_script.TIME_TELE().start_sock',target=self.tel_script.TIME_TELE().start_sock, args=(queue2,queue,self.sec,self.map_size,self.map_len,\
                                        self.map_angle,self.coord1,self.coord1_unit,self.coord2,self.coord2_unit,self.epoch,self.object,self.step,\
                                        self.coord_space,self.step_unit,self.map_size_unit,self.map_len_unit,self.map_angle_unit,self.numloop,self.kms_on_off))
                p.start()
                sys.stdout.flush()
                sys.stderr.flush()

                while True :
                    # grab data from tel_tracker.py
                    if not ut.tel_exit.is_set() :
                        time.sleep(0.01) # Rate limit
                        if (queue.empty() or queue2.empty()):
                            continue # No new data, don't block in recv()
                        tel_stuff = queue.get()
                        progress = queue2.get() # this could end up blocking if rate is different from tel_stuff
                        with self.flags.get_lock() :
                            self.flags[0] = int(tel_stuff[1]) #update flags passed to netcdf data
                        # pa,float(direction),el,az,map_ra,map_dec,ut
                        self.new_tel_data.emit(progress,tel_stuff[0],tel_stuff[1],tel_stuff[2],tel_stuff[3],tel_stuff[4],tel_stuff[5],tel_stuff[6])


                    else :
                        self.new_tel_data.emit(0,0,'done',0,0,0,0,0)
                        print(colored('Telescope Scan Completed!','green'))
                        break

        else :
            pass
            # from tel_tracker import start_tracker, turn_on_tracker
            # queue = mp.Queue()
            #
            # if True:
            #     time.sleep(0.1) # give tracker time to turn on before accepting packets
            #     p = mp.Process(name='start_tracker',target= start_tracker, args=(queue,))
            #     p.start()
            #     sys.stdout.flush()
            #     sys.stderr.flush()
            #
            #     while True :
            #         if not ut.tel_exit.is_set() :
            #             time.sleep(0.01) # Rate limit
            #             if queue.empty():
            #                 continue # No new data, don't block in recv()
            #             tel_stuff = queue.get()
            #             with self.flags.get_lock() :
            #                 self.flags[0] = int(tel_stuff[1]) #update flags passed to netcdf data
            #             progress = 0.0
            #             self.new_tel_data.emit(progress,tel_stuff[0],tel_stuff[1],tel_stuff[2],tel_stuff[3],tel_stuff[4],tel_stuff[5],tel_stuff[6])
            #             time.sleep(0.01)
            #             sys.stdout.flush()
            #             sys.stderr.flush()
            #
            #         else :
            #             self.new_tel_data.emit(0,0,'done',0,0,0,0,0)
            #             break
            #
            # else :
            #     # makes fake data for when we don't want to run the telescope
            #     tele_array = np.zeros((20,20),dtype=float)
            #     np.save(directory.temp_dir + 'tele_packet_off1.npy',tele_array)
            #     time.sleep(0.01)
            #     np.save(directory.temp_dir + 'tele_packet_off2.npy',tele_array)


class KMS_Thread(QtCore.QThread):

    new_kms_data = QtCore.pyqtSignal(object,object,object,object) # object 2 is status flag

    def __init__(self, kms_on_off, parent = None):
        QtCore.QThread.__init__(self, parent)
        self.kms_on_off = kms_on_off

    def __del__(self):
        ut.kms_exit.set()

    def run(self):
        if self.kms_on_off == 2 : #if the kms is starting without telescope, turn on tracker
            ''' This has been deprecated. Need access to socket for shutdown after scan finished.
            # from tel_tracker import turn_on_tracker
            # p1 = mp.Process(name='turn_on_tracker',target = turn_on_tracker, args=(self.kms_on_off,))
            # p1.start()
            '''
            PORT = 1806
            s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            s.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
            s.bind(('',6666))
            s.connect(('192.168.1.252',PORT))
            print('Socket Connected')

            s.send('TIME_START_TELEMETRY 2'.encode())
            reply = s.recv(1024).decode("ascii")
            print(reply)

        queue = mp.Queue()
        p = mp.Process(name='kms_socket.start_sock',target=kms_socket.start_sock , args=(queue,))
        p.start()

        while True :

            if not ut.kms_exit.is_set() :
                time.sleep(0.01) # Rate limit
                if queue.empty():
                    continue # No new data, don't block in recv()
                kms_stuff = queue.get() # pa , flags, time, encoder pos
                # send updated data to the gui
                # with self.flags.get_lock():
                #     self.flags[2] = int(kms_stuff[2])

                self.new_kms_data.emit(kms_stuff[0],kms_stuff[1],kms_stuff[2],kms_stuff[3]) #stuff 2 is status flag

            else :
                self.new_kms_data.emit('done','done','done','done')
                if self.kms_on_off == 2:
                    # send shutdown sequence to close telemetry
                    s.send('TIME_START_TELEMETRY 0'.encode())
                    s.shutdown(1)
                    s.close()
                    print(colored('Telescope Scan Completed!','green'))
                break

#activating the gui main window

if __name__ == '__main__':
    app = QtGui.QApplication(sys.argv)
    app.setApplicationName('TIME Data Visualization Suite')
    ex = MainWindow()
    sys.exit(app.exec_())
