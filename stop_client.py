import sys
sys.path.append('/home/pilot2/TIME_Software')
from tel_sock import stop_sock
stop_sock()
sys.stdout.write('I did a thing')
sys.exit()
