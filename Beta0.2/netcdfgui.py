from pyqtgraph import QtGui, QtCore
import numpy as np
import sys
import datetime
import os
import subprocess
import pyqtgraph as pg

class netgui(QtGui.QWidget):
    def __init__(self):
        super(netgui, self).__init__()
        self.init_ui()


    def init_ui(self):
        self.setWindowTitle('NETCDF TIME Data')
        self.getparameters()
        self.grid = QtGui.QGridLayout()
        self.grid.addLayout(self.parametersquit, 1, 1, 1, 1)
        self.setLayout(self.grid)
        self.setGeometry(10, 10, 1920, 1080)
        self.show()


    def getparameters(self):

        self.parametersquit = QtGui.QVBoxLayout()

        self.entertest = QtGui.QComboBox()
