import sys
sys.path.append('/home/pilot2/TIME_Software')
import tel_sock

def main():
    tel_sock.stop_sock()
    print('I did a thing...')

if __name__==__main__:
    main()
