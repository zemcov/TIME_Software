import sys
sys.path.append('/home/pilot2/anaconda3/lib/python3.6/site-packages')
import pyforms
from pyforms import BaseWidget
from pyforms.controls import ControlText
from pyforms.controls import ControlButton

class SimpleExample1(BaseWidget):

    def __init__(self):
        super(SimpleExample1,self).__int__('Simple example 1')

        self._firstname = ControlText('First name', 'Default value')
        self._middlename = ControlText('Middle name')
        self._lastname = ControlText('Last name')
        self._fullname = ControlText('Full name')
        self._button = controlButton('Press this button')

if __name__ == '__main__':
    pyforms.start_app(SimpleExample1)
