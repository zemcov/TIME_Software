#!/usr/bin/python
import mce_data
import matplotlib.pyplot as plot

f = mce_data.MCEfile('filename')
d = f.Read(row_col=True, unfilter='DC').datamode
