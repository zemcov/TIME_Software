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
        self.qt_connections()


    def init_ui(self):
        self.setWindowTitle('NETCDF TIME Data')
        self.getparameters()
        self.grid = QtGui.QGridLayout()
        self.grid.addLayout(self.parametersquit, 1, 1, 1, 1)
        self.setLayout(self.grid)
        self.setGeometry(10, 10, 1920, 1080)
        self.show()


    def qt_connections(self):
        self.quitbutton.clicked.connect(self.quitgui)


    def quitgui(self):
        print('Quitting Application')

        sys.exit()


    def getparameters(self):
        self.parametersquit = QtGui.QVBoxLayout()

        self.entertime = QtGui.QLineEdit()
        self.entertimeinterval = QtGui.QLineEdit()

        self.parameters = QtGui.QFormLayout()

        self.parameters.addRow('Time:', self.entertime)
        self.parameters.addRow('Time Interval:', self.entertimeinterval)

        self.parametersquit.addLayout(self.parameters)

        self.quitbutton = QtGui.QPushButton('Quit')

        self.parametersquit.addWidget(self.quitbutton)


def main():
    app = QtGui.QApplication(sys.argv)
    app.setApplicationName('NETCDF TIME Data')
    ex = netgui()
    sys.exit(app.exec_())


if __name__ == '__main__':
    main()
