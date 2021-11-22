from load_curve_netcdf import *
import numpy as np
import matplotlib.pyplot as plt
import math
import os, sys
import time
import pylab as pl
from pymce import MCE

class MCEWrap():
    def __init__(self):
        self.m = MCE()
    def read(self,x,y):
        v = self.m.read(x,y)
        print("rb %s %s = %s"%(x,y,str(v)))
        return v
    def write(self,x,y,v):
        print("wb %s %s %s"%(x,y,str(v)))
        if not DEBUG:
            self.m.write(x,y,v)

def generate_lc_data(d, temp, calib, input_bias, bias_cols, bias_start=2000, \
                        bias_step=2, bias_count=1001, zap_bias=30000, zap_time=1.0, settle_time=2000.0, \
                        bias_pause=0.1, bias_final=0, data_mode=1):
    '''
    Purpose: The purpose of this function is to replicate iv_curve_test where
    we bias the MCE's and save the results to a data file. The key difference
    here is that we are now saving the files into the more robust format of a netcdf
    Inputs: d (str) - the name of the output file
            temp (str) - temperature, this is a flag that gets saved to the output data file
                         name for book keeping later.
            calib (nd array) -
            input_bias (nd array) -
            bias_cols (nd array) - the columns that we want to bias
            bias_start (float) - where to start the biasing
            bias_step (float) - step size for the down biasing
            bias_count (int) -
            zap_bias (float) - bias level for zapping the detectors
            zap_time (float) - time in seconds to wait after zapping
            settle_time (float) - time to let the mce's settle after zapping
            bias_pause (float)
            bias_final (float) - final level for the bias to reach
    '''

    m = MCEWrap() #this is a wrapper for the MCE
    mas_data = os.environ['MAS_DATA']
    dname = os.path.join(mas_data, data_name)
    fname = os.path.join(dname, data_name)
    if not os.path.exists(dname):
        os.mkdir(dname)
        print('created directory ' + dname)
    else:
        raise Exception('directory already exists')
        exit(1)

    #save a log of the input parameters for book keeping
    flog = os.path.join(dname, 'lc_ramp_test_bias_log.txt')
    print('logging ramp parameters to '+flog)
    f = open(flog, 'w')
    f.write('Parameters for this run')
    f.write('\n')
    f.write("bias_start=%s" % bias_start)
    f.write('\n')
    f.write("bias_step=%s" % bias_step)
    f.write('\n')
    f.write("bias_count=%s" % bias_count)
    f.write('\n')
    f.write("zap_bias=%s" % zap_bias)
    f.write('\n')
    f.write("zap_time=%s" % zap_time)
    f.write('\n')
    f.write("settle_time=%s" % settle_time)
    f.write('\n')
    f.write("bias_pause=%s" % bias_pause)
    f.write('\n')
    f.write("bias_final=%s" % bias_final)
    f.write('\n')
    f.write("data_mode=%s" % data_mode)
    f.write('\n')
    f.close()

    #now we set up for the biasing
    print('setting up MCE mode')
    m.write('rca','data_mode',data_mode)
    m.write('rca','en_fb_jump',1)
    m.write('rca','flx_lp_init',1)
    ncol = len(m.read('tes','bias'))
    if bias_cols is None:
        bias_cols = np.arange(ncol, dtype=np.int32) #this implicitly assumes we want to bias all of the columns

    #mask bad columns
    bias_mask = np.zeros((ncol, dtype=np.int32))
    bias_mask[bias_cols] = 1 #convert bias_cols to a boolean array

    runfile = fname + '.run'
    biasfile = fname + '.bias'
    logfile = fname + '.log'

    #retrieve the mce status and put it in runfile
    os.system('mce_status > ' + runfile)

    #now we do the biasing
    os.system('frameacq_stamp %s %s %d >> %s'%('s',fname,bias_count,runfile))

    print('zapping')
    zap_arr = bias_mask * zap_bias
    m.write('tes', 'bias', bias_mask * bias_start)
    m.write('tes', 'bias', zap_arr)
    time.sleep(zap_time)
    print('settling')
    m.write('tes', 'bias', bias_mask * settle_bias)
    time.sleep(settle_time)

    m.write('tes','bias',bias_mask*bias_start)
    time.sleep(0.1)
    m.write('rca','flx_lp_init',1)
    time.sleep(0.1)

    bscript = os.path.join(dname,'bias_script.scr')
    b = open(bscript,'w')
    b.write('acq_config %s rcs' % fname)
    b.write('\n')

    bias_inc = np.zeros((ncols, bias_count))
    for j in range(ncols):
        bias_stop = bias_arr[j]
        bias_inc[j,:] = np.linspace(bias_start, bias_stop, bias_count)

    bias_inc = np.floor(bias_inc).astype(int)
    bf = open(biasfile, 'w')
    for bi in bias_inc:
        bf.write(str(bi) + ' \n')

    for i in range(bias_counts):
        bias = bias_inc[:,i] # grab every column for which step we are on
        bf.write(str(bias))
        bf.write('\n')
        bias_str = ' '.join([str(x) for x in bias*bias_mask])
        b.write('wb tes bias '+bias_str)
        b.write('\n')
        b.write('sleep %d'%(bias_pause*1e6)) #0.1 seconds * 1e6 = 100,000 so close to 3 hours!
        b.write('\n')
        b.write('acq_go 1')
        b.write('\n')

    bf.close()
    b.close()
    t0 = time.time()
    print('executing bias ramp')
    if not DEBUG:
        os.system('mce_cmd -qf '+bscript)
    t1 = time.time()
    print('ramp finished in %.2f seconds'%(t1-t0))

    m.write('tes','bias',bias_mask*bias_final)
    m.write('rca','flx_lp_init',1)

    identifier = d + '_' + temp
    #now save to a netcdf file
    nc_file = LcDataFile(identifier, dname)
    nc_file.data_append()
