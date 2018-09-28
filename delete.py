import subprocess, sys
sys.path.append('/home/pilot1/Desktop/time-data/')

subprocess.Popen(['ssh -T pilot2@timemce.rit.edu rm /data/cryo/current_data/temp*'],shell=True)
subprocess.Popen(['rm /home/pilot1/Desktop/time-data/mce1/temp*'],shell=True)
subprocess.Popen(['rm /home/pilot1/Desktop/time-data/netcdffiles/mce*'],shell=True)
