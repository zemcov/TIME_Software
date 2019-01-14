import numpy as np
import time
from multiprocessing import Pipe

def wave(queue):
    Time = 0
    while Time < 50 :
        t1=time.clock()
        queue.send([t1,Time])
        time.sleep(1.0)
        Time += 1
        if Time == 50 :
            queue.send(['done','done'])
            queue.close()
            break
