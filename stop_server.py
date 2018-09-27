import sys
sys.path.append('/home/pilot1/TIME_Software')
import readteledata

def main():
    readteledata.stop_sock()
    sys.stdout.write('I also did a thing')
if __name__==__main__:
    main()
