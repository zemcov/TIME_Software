import os
import subprocess

while True :
    if os.path.exists('/data/cryo/current_data/temp.*') :
        subprocess.Popen("./home/time/rit-software/TIME_Software/mce2_sftp.sh", shell=True)
    else :
        pass
'''
need some good way to stop this process from happening at the end of the gui
maybe put in a wait for 10 seconds timer and then if newfile isn't found, just give up on it
'''
