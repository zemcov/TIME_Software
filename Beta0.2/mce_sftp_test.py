import os
import subprocess

while True :
    if os.path.exists('/data/cryo/current_data/temp.*') :
        subprocess.call("mce_ssh.sh", shell=True)
    else :
        pass
