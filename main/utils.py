# mp.event items live here
import multiprocessing as mp

mce_exit = mp.Event()
tel_exit = mp.Event()
kms_exit = mp.Event()
hk_exit = mp.Event()

flags = [1,1,1,1,1] # initialize flags with all green
frameperfile = 0
offset = 0
german_freq = 100.0 # units in Hz

def timing(t,s):
    b = t - (s / german_freq)
    offset = b
# warning: if software is run for more than 500 days, then sync value will reset to 0

def sync_to_utc(s):
    utc_time = []
    for i in range(len(s)):
        utc_time.append(offset + (s[i] * german_freq))
    return utc_time
