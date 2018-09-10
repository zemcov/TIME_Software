#!/usr/bin/python
import pyforms
from pyforms import BaseWidget
from pyforms.Controls import ControlText
from pyforms.Controls import ControlButton

class CoolStuff(BaseWidget):
	def __init__(self):
	        super(SimpleExample1,self).__init__('CoolStuff')
                self._filename = ControlText('Filename')
                self._readcard = ControlText('Readout Card Number')
                self._frames = ControlText('Number of Frames')
                self._datamode = ControlText('Data Mode')
                self._button = ControlButton('Start Data Acquisition')
''' 
        def __buttonAction(self):
                #teaching the button to start data acquisition
                self._fullname.value =
'''

if __name__=="__main__": pyforms.start_app(CoolStuff)
