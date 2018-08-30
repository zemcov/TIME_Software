import os
import subprocess

while True :
    if os.path.exists('/data/cryo/current_data/temp.*') :
        subprocess.Popen("./home/pilot2/TIME_Software/mce1_sftp.sh", shell=True)
    else :
        pass
