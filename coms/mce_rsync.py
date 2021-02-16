#!/usr/bin/env python3

import os
import subprocess
import time
import sys
import datetime as dt
import logging
import setproctitle

setproctitle.setproctitle('mce_rsync')

basefolder = '/data/cryo/current_data/'
assert os.path.exists(basefolder), "Error: Base folder not found (%s)" % basefolder

if (len(sys.argv) < 2):
	sys.exit("The transfer destination should be passed as the only argument (e.g. time@time-master:/home/time/Desktop/time-data/mce0/)")
transfer_dest = sys.argv[1]

# Configure logging
log_filename = basefolder + 'log_mce_rsync.txt'
APP_LOG_FORMAT = '[%(asctime)s] %(levelname)s: %(message)s'
logging.basicConfig(filename=log_filename, format=APP_LOG_FORMAT, level=logging.DEBUG)
screen_handler = logging.StreamHandler() 
screen_handler.setFormatter(logging.Formatter(APP_LOG_FORMAT))
logging.getLogger().addHandler(screen_handler)  # Print to screen as well

logging.info('----- Starting MCE Data Transfer -----')
logging.info('Transfer destination: ' + transfer_dest)
logging.info('Waiting for run file to be found...')

fname_template = basefolder + "temp.%0.3i"

file_index = -1
begin = dt.datetime.utcnow()
while True:
	
	time.sleep(0.05) # Rate limit to 20 Hz
	
	if not os.path.exists(basefolder + 'temp.run'):
		continue
	
	if file_index < 0:
		# Transfer the run file
		logging.info("Found run file!  Transferring...")
		subprocess.run('rsync -zv ' + basefolder + 'temp.run ' + transfer_dest, shell=True)
		logging.info("Run file transferred!")
		file_index = 0
	elif os.path.exists(fname_template %(file_index+1)):
		# File n+1 exists, so file n should be finalized and transfered
		mce_file_name = fname_template % (file_index)
		if os.path.exists(mce_file_name) :
			logging.info('Transferring file' + mce_file_name)
			subprocess.run('rsync -zv ' + mce_file_name + ' ' + transfer_dest, shell=True)
			subprocess.run('rm ' + mce_file_name, shell=True)
			file_index += 1
			begin = dt.datetime.utcnow()
		else:
			logging.info('File does not exist! (' + mce_file_name + ')')
	
	# Time out and kill the script if mce files stop being produced
	# (but do not time out when looking for the run file)
	if ((dt.datetime.utcnow() - begin) > dt.timedelta(seconds = 10)):
		logging.info("Timed out waiting for MCE file number " + str(file_index))
		break
	
logging.info('----- Exiting -----')

