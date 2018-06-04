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
        self.init_ui()
        self.qt_connections()

    def init_ui(self):
        self.setWindowTitle('MCE TIME Data')
        hbox = QtGui.QVBoxLayout()
        self.setLayout(hbox)

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

        hbox.addLayout(self.parameters)

        self.quitbutton = QtGui.QPushButton('Quit')
        hbox.addWidget(self.quitbutton)

        self.setGeometry(10, 10, 1000, 600)
        self.show()

    def qt_connections(self):
        self.quitbutton.clicked.connect(self.on_quitbutton_clicked)
        self.submitbutton.clicked.connect(self.on_submitbutton_clicked)

    def on_quitbutton_clicked(self):
        print('Quitting Application')
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
        #print(self.observer)
        #print(self.datamode)
        #print(self.readoutcard)
        #print(self.framenumber)

def main():
    app = QtGui.QApplication(sys.argv)
    app.setApplicationName('MCE TIME Data')
    ex = mcegui()
    sys.exit(app.exec_())


if __name__ == '__main__':
    main()
