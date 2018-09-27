import sys
sys.path.append('/home/pilot2/TIME_Software')
import tel_sock

tel_sock.stop_sock()
sys.stdout.write('I did a thing')
sys.exit()
