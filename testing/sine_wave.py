import numpy as np
import time
from multiprocessing import Pipe

def wave(queue,exit):
    Time = 0
    while not exit.is_set() :
        t1=time.clock()
        queue.send([t1,Time])
        time.sleep(1.0)
        Time += 1
        if Time == 50 :
            queue.send(['done','done'])
            queue.close()
            break
    print("Exit Is Set")
