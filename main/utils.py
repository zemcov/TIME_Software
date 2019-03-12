# mp.event items live here
import multiprocessing as mp
import os, sys, datetime

mce_exit = mp.Event()
tel_exit = mp.Event()
kms_exit = mp.Event()
hk_exit = mp.Event()

flags = [1,1,1,1,1] # initialize flags with all green
frameperfile = 0
offset = 0
german_freq = 100.0 # units in Hz
epoch = 1552238365.0
time_zone = 7.0 * 60 * 60
utc_time = []
which_mce = [1,1] # [0] = mce0 , [1] = mce1
new_dir = ''

def timing(t,s):
    global offset
    b = float(t) - (float(s) / german_freq)
    offset = b
    return offset

# warning: if software is run for more than 500 days, then sync value will reset to 0

def sync_to_utc(s,off):
    utc_time = []
    for i in range(len(s)):
        utc = (float(off) + (float(s[i]) / german_freq))
        new_utc = datetime.datetime.utcfromtimestamp(utc)
        h = new_utc.hour
        m = new_utc.minute / 60.0
        sec = new_utc.second / 3600.0
        utc_time.append(h+m+sec)
    print(h+m+sec)
    return utc_time

def utc_to_sync(t,off):
    s = round((t - off.value) * german_freq)
    return s
