import sys
sys.path.append('/home/pilot1/TIME_Software')
from readteledata import stop_sock
from settings import s
import readteledata
stop_sock(s)
sys.stdout.write('I also did a thing')
sys.exit()
