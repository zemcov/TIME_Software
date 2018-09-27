import sys
sys.path.append('/home/pilot2/TIME_Software')
import tel_sock

def main():
    tel_sock.stop_sock()
    sys.stdout.write('I did a thing')

if __name__==__main__:
    main()
