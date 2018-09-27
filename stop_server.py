import sys
sys.path.append('/home/pilot1/TIME_Software')
from readteledata import stop_sock
import settings as st
import readteledata
stop_sock(st.s)
sys.stdout.write('I also did a thing')
sys.exit()
