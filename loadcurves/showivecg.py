#!/usr/bin/env python3

# Plots raw IV curves, both per-channel and per-column.
# Takes a folder with the IV curves as an argument.
# Based on the B3 showiv.py

import sys, os

import numpy as np
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt

import mce_data as mce_data
import coordinates as coords
from colors import default_colors
import loadcurve as loadcurve
import calib.time202001 as calib


def showivecg(fn):
	#folder = sys.argv[1]
	# name = os.path.split(folder)[1]
	# fn = os.path.join(folder, folder)
	# print(fn)
	# fn = folder
	print(fn)
	# biasfn = '/home/time/time_analysis/py/timefpu/partial_load_test_5/partial_load_test_5_bias.npy'
	# biasfn = fn + '.bias'
	biasfn = fn + '_bias.npy'
	#biasfn = fn + '.bias'
	f = mce_data.MCEFile(fn)
	dname = os.path.split(fn)[0]
	bias = np.load(biasfn, allow_pickle=True)
	y = -1.0*f.Read(row_col=True, unfilter='DC').data
	return bias, y

if __name__ == '__main__':
	folder = sys.argv[1]
	bias, y = showivecg(folder)
	bias_x = bias
	bias_y = y
