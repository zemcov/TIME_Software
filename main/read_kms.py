# this parses kms data
import numpy as np
import subprocess, os
import directory
import utils as ut

dir = directory.temp_dir

def loop_files(queue4):
    """
    Purpose: idk
    Inputs: queue4 - idk
    Outputs: None
    Calls: queue4.send()
    """
    while not ut.mce_exit.is_set():
        files = [dir + x for x in os.listdir(dir) if x.startswith("kms_packet")]
        mega_kms = []

        # if (dir + 'tele_packet_off') in files :
        #     kms_data = np.load(files[i])
        #     queue4.send([kms_data])
        #
        # else :
        for i in range(len(files)) :
            kms_data = np.load(files[i])
            mega_kms.append(kms_data)
            os.remove(files[i])

        queue4.send([mega_kms])

    sys.exit()
