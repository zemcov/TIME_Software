###### Things with ###### are places where there obviously might need to be changes



import sys, os

import numpy as np
from scipy.optimize import curve_fit
from scipy import interpolate as interp
import netCDF4
from netCDF4 import MFDataset
import matplotlib.pyplot as plt

pi = np.pi

##### Directory with data
dir = '/Users/rpkeenan/Dropbox/4_research/TIME_analysis/'

# This function is to load the netcdf files and return
# Pointing and count information
def load(path):
    # Load in files
    files = [path + x for x in os.listdir(path) if x.endswith(".nc")]
    files = sorted(files, key = os.path.getctime)
    files = [s.replace(path,'') for s in files]
    f = MFDataset(files)

    # Extract sync time from MCE header
    nvar = 17
    time_ind = 0
    time_get_inds = [time_ind + i for i in np.arange(100)*nvar]
    mce_time = f.variables['mce0_header'][:,time_get_inds,0].flatten()
    print(mce_time.shape)

    # Extract counts from MCE data
##### this picks the right MCE to use [0 or 1]
    mce = 0
##### these reference the 33x32 elements of the MCE output
    detector_index_1 = 0   # [0 to 32]
    detector_index_2 = 0   # [0 to 31]
    mce_counts = f.variables['mce'+str(mce)+'_raw_data_all'][:,detector_index_1,detector_index_2,:].flatten()
    print(mce_counts.shape)

    # Extract time and pointing from telescope data
    time_ind = 4
    ra_ind = 9
    dec_ind = 10
    telescope_time = f.variables['tel_data'][:,:,time_ind]
    telescope_ra = f.variables['tel_data'][:,:,ra_ind]
    telescope_dec = f.variables['tel_data'][:,:,dec_ind]

    # Generate pointing spline for telescope
    ra_spline = interp.UnivariateSpline(telescope_time, telescope_ra, s=0)
    dec_spline = interp.UnivariateSpline(telescope_time, telescope_dec, s=0)

    # Get mapping from sync time to UTC (to match telescope)
    sync_time = f.variables['time'][:,1]
    utc_time = f.variables['time'][:,0]

    # Map MCE time to RA/Dec
    ra = ra_spline(utc_time)
    dec = dec_spline(utc_time)
    value = mce_counts

    return utc_time, ra, dec, value

# class to hold data from telescope and produce fit
class dataset:
    def __init__(self, path):
        # load data from netcdf files in path
        if os.path.exists(path):
            self.time, self.ra, self.dec, self.counts = load(path)
        else:
            print('file not found')
            return

    # functional form to fit
    def form(self, x, A, m, s, a, b):
        offset = a*x + b
        return offset + A*np.exp(-.5*(x-m)**2/s**2)

    # this does all the fitting for the RA and Dec peaks
    def fit_data(self, spread_guess=.5):
        # Do fit for RA
        # Set fit parameters
        p0 = [1,0,spread_guess,0,0]
        bounds = ([0,np.amin(self.ra), .1, -np.inf, np.amin(self.counts)],
                  [np.amax(self.counts),np.amax(self.ra), 5, np.inf, np.amax(self.counts)])
        for i in range(len(p0)):
            if p0[i] < bounds[0][i]:
                p0[i] = bounds[0][i]

        # Fit - do over whole range of RA to make sure finding the correct peak
        check_cov = np.inf
        for i in np.linspace(np.amin(self.ra), np.amax(self.ra), int(round(np.ptp(self.ra)/spread_guess/4))):
            p0[1]=i
            try:
                fit, cov = curve_fit(self.form, self.ra.ravel(), self.counts.ravel(), bounds=bounds, p0=p0)
                if np.sum([cov[m,m]**2 for m in range(len(cov))]) < check_cov:
                    check_cov = np.sum([cov[m,m]**2 for m in range(len(cov))])
                    self.fit = fit
                    self.cov = cov
            except:
                pass

        self.A_ra = self.fit[0]
        self.m_ra = self.fit[1]
        self.s_ra = self.fit[2]
        self.a_ra = self.fit[3]
        self.b_ra = self.fit[4]

        # Do fit for dec
        # Set fit parameters
        p0 = [np.amax(self.dec),self.dec[np.argmax(self.counts)],spread_guess,0,0]
        bounds = ([0,np.amin(self.dec), .1, 0, np.amin(self.counts)],
                  [np.amax(self.counts),np.amax(self.dec), 5, 1e-10, np.amax(self.counts)])
        for i in range(len(p0)):
            if p0[i] < bounds[0][i]:
                p0[i] = bounds[0][i]

        # Fit - do over whole range of RA to make sure finding the correct peak
        check_cov = np.inf
        for i in np.linspace(np.amin(self.dec), np.amax(self.dec), int(round(np.ptp(self.dec)/spread_guess/4))):
            p0[1]=i
            try:
                fit, cov = curve_fit(self.form, self.dec.ravel(), self.counts.ravel(), bounds=bounds, p0=p0)
                if np.sum([cov[m,m]**2 for m in range(len(cov))]) < check_cov:
                    check_cov = np.sum([cov[m,m]**2 for m in range(len(cov))])
                    self.fit = fit
                    self.cov = cov
            except:
                pass

        self.A_dec = self.fit[0]
        self.m_dec = self.fit[1]
        self.s_dec = self.fit[2]
        self.a_dec = self.fit[3]
        self.b_dec = self.fit[4]

    # Define a fitting function for RA data - fitting_function_ra can be used to plot the fit
    def gaussian_fit_ra(self,x):
        return self.A_ra * np.exp(-.5*(x-self.m_ra)**2/self.s_ra**2)
    def background_fit_ra(self,x):
        return self.a_ra*x + self.b_ra
    def fitting_function_ra(self,x):
        return self.gaussian_fit_ra(x) + self.background_fit_ra(x)

    # Define a fitting function for Dec data
    def gaussian_fit_dec(self,x):
        return self.A_dec * np.exp(-.5*(x-self.m_dec)**2/self.s_dec**2)
    def background_fit_dec(self,x):
        return self.a_dec*x + self.b_dec
    def fitting_function_dec(self,x):
        return self.gaussian_fit_dec(x) + self.background_fit_dec(x)

    # This will plot the data (without the fit)
    def plot_data(self):
        fig = plt.figure(figsize=(10,5))
        ax = fig.add_subplot(121)
        ax.plot(self.ra,self.counts,'rx')
        ax.set(xlabel='RA', ylabel='Counts')
        ax = fig.add_subplot(122)
        ax.plot(self.dec,self.counts,'rx')
        ax.set(xlabel='Dec', ylabel='Counts')
        plt.show()

    # This will plot the data and the fit
    def plot_fit(self):
        plt.plot(self.ra,self.counts,'rx',label='RA data')
        x = np.linspace(np.amin(self.ra),np.amax(self.ra),1000)
        plt.plot(x,self.fitting_function_ra(x),label='fit')
        plt.show()
        plt.plot(self.dec,self.counts,'rx',label='Dec data')
        x = np.linspace(np.amin(self.dec),np.amax(self.dec),1000)
        plt.plot(x,self.fitting_function_dec(x),label='fit')
        plt.show()

    # Give this where you think the telescope is pointing, in ra_0, dec_0
    # it will return ra_peak - ra_0, and dec_peak - dec_0
    def offset(self, ra_0, dec_0):
        return self.m_ra - ra_0, self.m_dec - dec_0


# Gaussian class for fit - a gaussian of height A, center m, spread s,
# plus a linear background with slope a and intercept b
class gaussian:
    def __init__(self, A, m, s, a, b):
        self.m = m
        self.s = s
        self.a = a
        self.b = b

        self.max = A

    def gaussian_part(self,x):
        return self.max*np.exp(-.5*(x-self.m)**2/self.s**2)

    def linear_part(self, x):
        return self.a*x + self.b

    def function(self, x):
        return self.gaussian_part(x) + self.linear_part(x)

if __name__ == '__main__':
    data = dataset(dir)
    data.fit_data()
    data.plot_fit()
