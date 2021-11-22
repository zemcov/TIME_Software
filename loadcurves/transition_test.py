from __future__ import division, print_function
import sys,os
import numpy as np
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import matplotlib.cm as cm
from matplotlib.font_manager import FontProperties
from matplotlib.colors import ListedColormap
fontP = FontProperties()
fontP.set_size('xx-small')
from PIL import Image
#import calib.time202001 as calib
import coordinates as coords
import params as params
import loadcurve as loadcurve
import loadcurveecg as loadcurveecg
from scipy import interpolate
import pdb
from math import *
from termcolor import colored
import mce_data as mce_data
from showivecg import showivecg

def turn(y,x,bias_y,bias_x, mux_c, mux_r):

    x = x[~np.isnan(x)]
    y = y[~np.isnan(y)]
    bias_x = bias_x[~np.isnan(bias_x)]
    bias_y = bias_y[~np.isnan(bias_y)]

    if len(x)==0 or len(y)==0 or len(bias_x)==0 or len(bias_y)==0:
        x = np.zeros(20)
        y = np.zeros(20)
        bias_x = np.zeros(20)
        bias_y = np.zeros(20)

    if np.mean(y) != 0.0 and np.mean(bias_y) != 0.0 : #gets rid of unecessary data
        #finds what kind of slope is in the transition data
        z, cov = np.polyfit(list(bias_x), list(bias_y), 1, cov=True) # I want to know if my data is a line
        poly_func = np.poly1d(z)


        e = np.sqrt(np.diag(cov))
        intercept_error = e[1]
        print(intercept_error, 'intercept_error')
        slope_error = e[0]

        if intercept_error > 0.1: #the data is getting close to the transition here
        #As a note, this value may change, this intercept error value might not be good. (Check this later!)

            m = np.diff(y) #finding the slope
            out = np.where(np.logical_and(np.greater(m,0.0),np.less(m,0.06))) # where is the slope between those two numbers?
            out = [list(k) for k in out][0]

            if len(out) > 20 :
                print(out[0:19], 'slope')
                return out[0:19], None #trims data array to only 20 points
            else :
                print(out[0:19], 'slope')
                return out, None
        else :
            print('error with slope')
            return None, 4
    else :
        print('mean of zero')
        return None, 3

def find_mode_limits(xvals,yvals,cxvals,cyvals,col=None,temp=0):
    print(len(xvals))

    xvalues = []
    yvalues = []
    cxvalues = []
    cyvalues = []
    count = 0
    try:
        for i in range(len(xvals)):
            if np.mean(xvals[i]) == 0.0 :
                xvals[i][:] = np.nan
                yvals[i][:] = np.nan
                cxvals[i][:] = np.nan
                cyvals[i][:] = np.nan
            else:
                count += 1

        print('num of good det : ' ,count)
        if count == 0 :
            print('Error')
            return 0

        else :

            # removing outliers
            mean = np.nanmean(yvals)
            std = np.nanstd(yvals)
            dist_from_mean = abs(yvals - mean)
            max_dev = 1
            not_outlier = dist_from_mean < max_dev * std

            for k in range(len(yvals)):
                for l in range(len(yvals[1])):
                    if not_outlier[k,l] == False :
                        yvals[k,l] = np.nan
                        xvals[k,l] = np.nan

            x_sampler = np.linspace(np.nanmin(xvals),np.nanmax(xvals),num=100) #same data set just outliers removed

            modes = []
            maxcount = 0
            counts = [0]*100

            for j in range(len(x_sampler)):
                for l in range(len(xvals)):
                    if xvals[l][0] != np.nan:
                        if x_sampler[j] > np.nanmin(xvals[l]) and x_sampler[j] < np.nanmax(xvals[l]): #xvals[l] each detector
                            counts[j] += 1 #counting how many intersections
                        if counts[j] > maxcount:
                            maxcount = counts[j]

            for k in counts:
                if k == maxcount:
                     modes.append(k)

            min_x = np.nanmin(xvals)
            max_x = np.nanmax(xvals)

            num_det = np.max(counts)
            mask = np.where(counts == num_det)[0]
            limits = x_sampler[mask]
            n_mask = np.logical_and(xvals.flatten() < limits[-1],xvals.flatten() > limits[0]) # saves the indices from xvals that match the boolean statements
            n_mask = n_mask.reshape(33,20)
            cxvals = np.array(cxvals)[n_mask]
            cyvals = np.array(cyvals)[n_mask]

            opt_num = 3


            # opt_num = 0
            # for h in range(len(xvals)):
            #     if np.any(n_mask[h][:]) == True :
            #         opt_num += 1

            print ("Range of optimal values: " +  str(limits[0] ) + str(limits[-1]))
            print ("Optimal value: " + str(limits[-1]))
            # plotting the actual points as scatter plot

            plt.figure(4)
            plt.scatter(xvals, yvals, color = "m", marker = "o", s = 30)
            #creates region of optimal x values
            plt.axvspan(limits[0], limits[-1], alpha = 0.5)
            plt.axvline((limits[-1]), color = 'r')
            plt.xlabel('Resistance [ohm]')
            plt.ylabel('TES Power [pW]')
            plt.title('Optimal Transition Column %s' %(col))
            plt.savefig('plots/transition_tests_%s_%sK.png'%(col,temp))
            plt.clf()

            print(colored('opt_num: %s'%(opt_num), 'magenta'))
            return opt_num #powerx,powery,biasx,biasy

    except ValueError:
        print('Empty Arrays')
        return 0

def size():
    bias_X = np.zeros((32,33,20))
    bias_Y = np.zeros((32,33,20))
    current_x = np.zeros((32,33,20))
    current_y = np.zeros((32,33,20))
    return bias_X, bias_Y, current_x, current_y


def transition_sizes(y,x,bias_y,bias_x, mux_c, mux_r):
    flags = []
    m_chng, err = turn(y,x,bias_y,bias_x, mux_c, mux_r) #grabs data where transition is
    if m_chng == None:
        xnew = np.zeros(20)
        ynew = np.zeros(20)
        cxnew = np.zeros(20)
        cynew = np.zeros(20)
    else:

        if len(m_chng) == 20 :
            #assigning each data point to its corresponding row and colum numbers
            xnew = x[m_chng]
            ynew = y[m_chng]
            cxnew = (bias_x)[m_chng]
            cynew = (bias_y)[m_chng]

        else :
            if len(m_chng) < 2 :
                print('not enough data to interpolate!')
                xnew = np.zeros(20)
                ynew = np.zeros(20)
                cxnew = np.zeros(20)
                cynew = np.zeros(20)
                flags.append(5)
            else :
                #fill in the data arrays if there are <20 data points
                f = interpolate.interp1d((x)[m_chng], (y)[m_chng])
                xnew = np.linspace((x)[m_chng][0],(x)[m_chng][-1] , num = 20)
                ynew = f(xnew)

                t = interpolate.interp1d((bias_x)[m_chng], (bias_y)[m_chng])
                cxnew = np.linspace((bias_x)[m_chng][0],(bias_x)[m_chng][-1] , num = 20)
                cynew = t(cxnew)

        if err != None :
            flags.append(err)


    return xnew, ynew, cxnew, cynew, flags

    #This function will take the turn function and return the transition region in the correct size

def main(T, dir, cols=32, rows=33):
    '''
    T - (float) : Temperature for the calibration data set options are 77k and 293k
    dir - (str) : Directory that the mce data is being stored in
    '''
    #for testing right now
    # dir = 'home/time_user/time_analysis/py/timefpu/'

    transition = False #initially set the transition flag as False

    init_bias = np.load(f'bias_list_{T}.npy',allow_pickle=True) #This file relies on read load curves being run at least once
    import calib.time202001 as calib
    bias_min = init_bias[:, 1]
    opt_num_fin = init_bias[:, 3]

    # this will have to be dynamic later on !
    fname = '/home/time_user/time_analysis/py/timefpu/partial_load_test_5/partial_load_test_5'
    folder = '/home/time_user/time_analysis/py/timefpu/partial_load_test_5'
    fname_full = '/home/time_user/time_analysis/py/timefpu/iv_45deg_pid330mk_294k_beammap0'
    # print(folder)
    # print(fname)
    # print(fname_full)
    i = 0
    while transition is False:
        if i != 0:
            bias_x, bias_y = showivecg(folder)
            bias_y = bias_y.swapaxes(0,1) #why do we swap axes here?

            partial_lc = loadcurveecg.load_loadcurves_muxcr(folder, calib, r_ser_override = rser_cr, partial=True)

            tes_p_masked = {}
            tes_r = {}
            for c in range(cols):
                for r in range(rows):
                    tes_p_masked[(c, r)] = partial_lc[c][r].tes_p_masked
                    tes_r[(c, r)] = partial_lc[c][r].tes_r

            final_res = np.zeros((cols,rows,20))
            final_p = np.zeros((cols,rows,20))
            current_x = np.zeros((cols,rows,20))
            current_y = np.zeros((cols,rows,20))
            opt_num_array = [] #this is a list not an array
            transition = True #Why are we forcing the script to stop ?

            for mux_c in range(cols): #detector position
                for mux_r in range(rows): #detector frequency

                    # use turn function to find detectors in transition
                    res_detect, p_detect, current_x_detect, current_y_detect, flags = transition_sizes(tes_p_masked[(mux_c, mux_r)]*1e12, tes_r[(mux_c, mux_r)], bias_y[mux_c, mux_r], bias_x[mux_c])
                    final_res[int(mux_c),int(mux_r),:] = res_detect
                    final_p[int(mux_c),int(mux_r),:] = p_detect
                    current_x[int(mux_c),int(mux_r),:] = current_x_detect
                    current_y[int(mux_c),int(mux_r),:] = current_y_detect

                opt_num = find_mode_limits(final_res, final_p, current_x, current_y, col = mux_c, temp = T)
                opt_num_array.append(opt_num)

                # if any column doesn't have equal to num working detector as test file
                # force the script to continue by setting transition to False again
                for k in range(cols):
                    if opt_num[k] < opt_num_fin[k]:
                        transition = False

                        # add something that spits out graph for given column so we can
                        # see where we are at in the transition
                        user_input = int(input(f'Provide new min bias for column {k}: '))
                        bias_min[k] = float(user_input)


        else:
            bias_x, bias_y = showivecg(fname)
            full_lc = loadcurve.load_loadcurves_muxcr(fname_full, calib)
            rser_cr = {}
            for c in range(cols):
                   for r in range(rows):
                         rser_cr[(c, r)] = full_lc[c][r].r_ser

            bias_y = bias_y.swapaxes(0,1) # why are we swapping axes here?
            partial_lc = loadcurveecg.load_loadcurves_muxcr(folder, calib, r_ser_override = rser_cr, partial=True)

            tes_p_masked = {}
            tes_r = {}
            for c in range(0, cols):
                for r in range(0, rows):
                         tes_p_masked[(c, r)] = partial_lc[c][r].tes_p_masked
                         tes_r[(c, r)] = partial_lc[c][r].tes_r


            colors = plt.cm.jet(np.linspace(0,1,rows))
            final_res = np.zeros((cols,rows,20))
            final_p = np.zeros((cols,rows,20))
            current_x = np.zeros((cols,rows,20))
            current_y = np.zeros((cols,rows,20))


            partial_lc = loadcurveecg.load_loadcurves_muxcr(folder, calib, r_ser_override = rser_cr, partial=True)

            #why are we redefining tes_p_masked before we even use the first version of it ?
            #what is the point of line 296-299
            tes_p_masked = {}
            tes_r = {}
            for c in range(cols):
                for r in range(rows):
                         tes_p_masked[(c, r)] = partial_lc[c][r].tes_p_masked
                         tes_r[(c, r)] = partial_lc[c][r].tes_r


            colors = plt.cm.jet(np.linspace(0,1,rows))
            final_res = np.zeros((cols,rows,20))
            final_p = np.zeros((cols,rows,20))
            current_x = np.zeros((cols,rows,20))
            current_y = np.zeros((cols,rows,20))
            opt_num_array = []
            transition = True # again why are we forcing it to stop here the script will just not execute
            for mux_c in range(cols): #detector position
                for mux_r in range(rows): #detector frequency
                    # use turn function to find detectors in transition
                    res_detect, p_detect, current_x_detect, current_y_detect, flags = transition_sizes(tes_p_masked[(mux_c, mux_r)]*1e12, tes_r[(mux_c, mux_r)], bias_y[mux_c, mux_r], bias_x[mux_c], mux_c, mux_r)
                    final_res[mux_c,mux_r,:] = res_detect
                    final_p[mux_c,mux_r,:] = p_detect
                    current_x[mux_c,mux_r,:] = current_x_detect
                    current_y[mux_c,mux_r,:] = current_y_detect

                opt_num = find_mode_limits(final_res, final_p, current_x, current_y, col = mux_c, temp = T)
                opt_num_array.append(opt_num)

            # if any column doesn't have equal to num working detector as test file
            # force the script to continue by setting transition to False again
            for k in range(cols):
                if opt_num_array[k] < opt_num_fin[k]:
                    transition = False
                    for i in range(rows):
                        plt.plot(current_x[k, i], current_y[k, i])
                        if np.mean(current_x[k, i,:]) != 0.0 :
                            plt.scatter(current_x[k, i,:], current_y[k, i,:], s=50.0, marker='*',color=colors[i],label='Det # %s'%(i))
                    plt.ylabel("TES Current [$\mu$A]")
                    plt.xlabel("Bias Current [$\mu$A]")
                    #fix this later so everything is not a nan...
                    #plt.xlim(np.nanmin(current_x)-15,np.nanmax(current_x)+15)
                    plt.xlim(500, 600)
                    plt.title('Column %s Detectors @ %s K (Bias)'%(k,T))
                    plt.legend(ncol=1, loc='upper left', bbox_to_anchor=(0.98, 1.03), labelspacing=0.0, prop=fontP, shadow=True)
                    plt.savefig('new_plots/bias_color_%s_%sK.png'%(k,T))
                    plt.clf()

                    user_input = int(input(f'Provide new min bias for column {k}: '))
                    bias_min[k] = float(user_input)
                else :
                    print('Bias min acceptable')
                    print(bias_min[k],opt_num_array[k],opt_num_fin[k])

        i += 1




if __name__ == '__main__':
    # this is where your code starts running
    main('77', 'home/time_user/time_analysis/py/timefpu/', cols=32, rows=33)
    exit()
    transition = False

    print('Current options for calibration temperature: 77K and 293K')
    # T = user_input_T
    T = '77'
    i = 0

    init_bias = np.load(f'bias_list_{T}.npy',allow_pickle=True) #This file relies on read load curves being run at least once
    import calib.time202001 as calib
    #bias_min = init_bias[:,1] # = [good_count,bias_min,power_min,opt_num]
    bias_min = init_bias[:, 1]
    print("The optimal number of detectors in the transition range is", init_bias[:,3])
    opt_num_fin = init_bias[:, 3]
    #good_count = how many total working detectors in the column
    print("Total number of working detectors is", init_bias[:,0])
    # bias_min = starting bias
    # power_min = starting power


    fname = '/home/time_user/time_analysis/py/timefpu/partial_load_test_5/partial_load_test_5'
    folder = '/home/time_user/time_analysis/py/timefpu/partial_load_test_5'
    fname_full = '/home/time_user/time_analysis/py/timefpu/iv_45deg_pid330mk_294k_beammap0'


    while transition == False :
        print('Hi! im here to tell you that you are in the', i, 'loop')

        if i != 0 :

            if transition == False :

                ''' RERUN THE DETECTORS USING NEW BIAS MIN LIST'''

                bias, y = showivecg(folder)
                bias_x = bias
                bias_y = y
                bias_y = bias_y.swapaxes(0,1)

                ''' SWAP OUT FOLDER FOR DIRECTORY WITH NEW BIAS DATA WHEN RUNNING FOR REALZ '''
                partial_lc = loadcurveecg.load_loadcurves_muxcr(folder, calib, r_ser_override = rser_cr, partial=True)

                tes_p_masked = {}
                tes_r = {}
                for c in range(0, 31):
                    for r in range(0,32):
                             tes_p_masked[(c, r)] = partial_lc[c][r].tes_p_masked
                             tes_r[(c, r)] = partial_lc[c][r].tes_r

                final_res = np.zeros((32,33,20))
                final_p = np.zeros((32,33,20))
                current_x = np.zeros((32,33,20))
                current_y = np.zeros((32,33,20))
                opt_num_array = []
                transition = True # let's pretend the script will be able to stop
                for mux_c in range(0, 31): #detector position
                    for mux_r in range(0, 32): #detector frequency

                        # use turn function to find detectors in transition
                        res_detect, p_detect, current_x_detect, current_y_detect, flags = transition_sizes(tes_p_masked[(mux_c, mux_r)]*1e12, tes_r[(mux_c, mux_r)], bias_y[mux_c, mux_r], bias_x[mux_c])
                        final_res[int(mux_c),int(mux_r),:] = res_detect
                        final_p[int(mux_c),int(mux_r),:] = p_detect
                        current_x[int(mux_c),int(mux_r),:] = current_x_detect
                        current_y[int(mux_c),int(mux_r),:] = current_y_detect

                    opt_num = find_mode_limits(final_res, final_p, current_x, current_y, col = mux_c, temp = T)
                    opt_num_array.append(opt_num)
                    print(opt_num)

                # if any column doesn't have equal to num working detector as test file
                # force the script to continue by setting transition to False again
                for k in range(0, 31):
                    if opt_num[k] < opt_num_fin[k]:
                        transition = False
                        ''' add something that spits out graph for given column so we can
                            see where we are at in the transition
                        '''
                        user_input = int(input(f'Provide new min bias for column {k}: '))
                        bias_min[k] = float(user_input)
                    else :
                        print('Bias min acceptable')
                        print(bias_min[k],opt_num[k],opt_num_fin[k])



        else :
            print('Hey Im here to tell you that you are in the initial else statement')
            bias, y = showivecg(fname)


            full_lc = loadcurve.load_loadcurves_muxcr(fname_full, calib)
            rser_cr = {}
            for c in range(0,31):
                   for r in range(0, 32):
                             rser_cr[(c, r)] = full_lc[c][r].r_ser


            bias_x = bias
            bias_y = y

            bias_y = bias_y.swapaxes(0,1)
            partial_lc = loadcurveecg.load_loadcurves_muxcr(folder, calib, r_ser_override = rser_cr, partial=True)

            tes_p_masked = {}
            tes_r = {}
            for c in range(0, 31):
                for r in range(0, 32):
                         tes_p_masked[(c, r)] = partial_lc[c][r].tes_p_masked
                         tes_r[(c, r)] = partial_lc[c][r].tes_r


            colors = plt.cm.jet(np.linspace(0,1,33))
            final_res = np.zeros((32,33,20))
            final_p = np.zeros((32,33,20))
            current_x = np.zeros((32,33,20))
            current_y = np.zeros((32,33,20))


            partial_lc = loadcurveecg.load_loadcurves_muxcr(folder, calib, r_ser_override = rser_cr, partial=True)

            tes_p_masked = {}
            tes_r = {}
            for c in range(0, 31):
                for r in range(0, 32):
                         tes_p_masked[(c, r)] = partial_lc[c][r].tes_p_masked
                         tes_r[(c, r)] = partial_lc[c][r].tes_r


            colors = plt.cm.jet(np.linspace(0,1,33))
            final_res = np.zeros((32,33,20))
            final_p = np.zeros((32,33,20))
            current_x = np.zeros((32,33,20))
            current_y = np.zeros((32,33,20))
            opt_num_array = []
            transition = True # let's pretend the script will be able to stop
            for mux_c in range(0, 31): #detector position
                for mux_r in range(0, 32): #detector frequency

                    # use turn function to find detectors in transition
                    res_detect, p_detect, current_x_detect, current_y_detect, flags = transition_sizes(tes_p_masked[(mux_c, mux_r)]*1e12, tes_r[(mux_c, mux_r)], bias_y[mux_c, mux_r], bias_x[mux_c], mux_c, mux_r)
                    final_res[int(mux_c),int(mux_r),:] = res_detect
                    final_p[int(mux_c),int(mux_r),:] = p_detect
                    current_x[int(mux_c),int(mux_r),:] = current_x_detect
                    current_y[int(mux_c),int(mux_r),:] = current_y_detect

                opt_num = find_mode_limits(final_res, final_p, current_x, current_y, col = mux_c, temp = T)
                opt_num_array.append(opt_num)
                print(opt_num)

            # if any column doesn't have equal to num working detector as test file
            # force the script to continue by setting transition to False again
            for k in range(0, 31):
                if opt_num_array[k] < opt_num_fin[k]:
                    transition = False
                    for i in range(0, 32):
                        plt.plot(current_x[k, i], current_y[k, i])
                        if np.mean(current_x[i, k,:]) != 0.0 :
                            plt.scatter(current_x[i, k,:], current_y[i, k,:], s=50.0, marker='*',color=colors[i],label='Det # %s'%(i))
                    plt.ylabel("TES Current [$\mu$A]")
                    plt.xlabel("Bias Current [$\mu$A]")
                    '''CHANGE THESE NUMBERS LATER!!!!!'''
                    #fix this later so everything is not a nan...
                    #plt.xlim(np.nanmin(current_x)-15,np.nanmax(current_x)+15)
                    plt.xlim(500, 600)
                    plt.title('Column %s Detectors @ %s K (Bias)'%(k,T))
                    plt.legend(ncol=1, loc='upper left', bbox_to_anchor=(0.98, 1.03), labelspacing=0.0, prop=fontP, shadow=True)
                    plt.savefig('plots/bias_color_%s_%sK.png'%(k,T))
                    plt.clf()

                    user_input = int(input(f'Provide new min bias for column {k}: '))
                    bias_min[k] = float(user_input)
                else :
                    print('Bias min acceptable')
                    print(bias_min[k],opt_num_array[k],opt_num_fin[k])

        ''' ################ THIS IS JUST HERE FOR TESTING!!! #################'''
        transition = True
        ''' ################ REMOVE THAT WHEN YOU WANT TO RUN FOR REALZ #############'''
        i += 1
