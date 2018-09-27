import sys
sys.path.append('/home/pilot1/TIME_Software')
import readteledata

readteledata.stop_sock()
sys.stdout.write('I also did a thing')
sys.exit()
