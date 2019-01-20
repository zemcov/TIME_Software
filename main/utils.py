# mp.event items live here
import multiprocessing as mp

mce_exit = mp.Event()
tel_exit = mp.Event()
kms_exit = mp.Event()
hk_exit = mp.Event()

flags = [1,1,1] # initialize flags with all green
