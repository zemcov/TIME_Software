import sys
import subprocess

command = ['sshpass -p "time-pilot2" ssh -o StrictHostKeyChecking=no\
   pilot2@timemce.rit.edu ; mce_cmd -x stop 2 ret_dat']
process = subprocess.Popen(command ,stdout=subprocess.PIPE, shell=True)
proc_stdout = process.communicate()[0].strip()
print(proc_stdout)
