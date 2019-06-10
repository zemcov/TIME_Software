# this parses kms data
import numpy as np
import subprocess

dir = '/home/time_user/TIME_Software/main/tempfiles/'

def loop_files(self,queue4):

    while not ut.mce_exit.is_set():
        files = [dir + x for x in os.listdir(dir) if x.startswith("kms_packet")]
        mega_kms = []

        if (dir + 'tele_packet_off') in files :
            kms_data = np.load(files[i])
            queue4.send([kms_data])

        else :
            for i in range(len(files)) :
                kms_data = np.load(files[i])
                mega_kms.append(kms_data)
                subprocess.Popen(['rm %s' %(files[i])],shell=True)

            queue4.send([mega_tel])

    sys.exit()
