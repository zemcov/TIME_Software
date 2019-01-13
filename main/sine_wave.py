import numpy as np
import time

def wave(queue):
    Time = 0
    while Time < 5 :
        t1=time.clock()
        queue.put(t1)
        time.sleep(1.0)
        Time += 1
        if Time == 5 :
            queue.put('done')
            break
        continue
