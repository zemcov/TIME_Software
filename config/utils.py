# mp.event items live here
import multiprocessing as mp
import os, sys, datetime

mce_exit = mp.Event()
tel_exit = mp.Event()
kms_exit = mp.Event()
hk_exit = mp.Event()

mce0_onoff = []
mce1_onoff = []

flags = [1,1,1,1,1] # initialize flags with all green
frameperfile = 0
offset = 0
german_freq = 100.0 # units in Hz
epoch = 1552238365.0
time_zone = 7.0 * 60 * 60
utc_time = []
which_mce = [1,1,1] # [0] = mce0 , [1] = mce1 , [2] = sim data

def timing(t,s):
    b = float(t) - (float(s) / german_freq)
    return b

# warning: if software is run for more than 500 days, then sync value will reset to 0

def sync_to_utc(s,off):
    utc_time = []
    for i in range(len(s)):
        utc_time.append(float(off) + (float(s[i]) / german_freq))
    return utc_time

def utc_to_sync(t,off):
    s = round((t - off.value) * german_freq)
    return s
