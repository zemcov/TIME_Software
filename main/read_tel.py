# this parses telescope data files
import numpy as np

dir = '/home/time/time-software-testing/TIME_Software/main/tempfiles/'

def loop_files(self,queue3):

    while not ut.mce_exit.is_set():
        files = [dir + x for x in os.listdir(dir) if x.startswith("tele_packet")]
        mega_tel = []

        if (dir + 'tele_packet_off') in files :
            tel_data = np.load(files[i])
            queue3.send([tel_data])

        else :
            for i in range(len(files)) :
                tel_data = np.load(files[i])
                mega_tel.append(tel_data)
                subprocess.Popen(['rm %s' %(files[i])],shell=True)

            queue3.send([mega_tel])

    sys.exit()
