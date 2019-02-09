import subprocess, os, sys
import multiprocessing as mp

def main(readoutcard, framenumber, frameperfile, datarate, datamode):
    # set the data rate for both mces
    subprocess.Popen(['./mce0_cdr.sh %s' %(datarate)], shell = True)
    subprocess.Popen(['./mce1_cdr.sh %s' %(datarate)], shell = True)

    if readoutcard == 'All':
        subprocess.Popen(['./mce0_cdm.sh a %s' %(datamode)], shell = True)
        subprocess.Popen(['./mce1_cdm.sh a %s' %(datamode)], shell = True)
        subprocess.Popen(['./mce0_run.sh %s s %s &' %(framenumber, frameperfile)], shell = True)
        subprocess.Popen(['./mce1_run.sh %s s %s &' %(framenumber, frameperfile)], shell = True)
    else :
        subprocess.Popen(['./mce0_cdm.sh %s %s' %(readoutcard, datamode)], shell = True)
        subprocess.Popen(['./mce1_cdm.sh %s %s' %(readoutcard, datamode)], shell = True)
        subprocess.Popen(['./mce0_run.sh %s %s %s &' %(framenumber, readoutcard, frameperfile)], shell = True)
        subprocess.Popen(['./mce1_run.sh %s %s %s &' %(framenumber, readoutcard, frameperfile)], shell = True)

    subprocess.Popen(['ssh -T time-mce-0 python /home/time/time-software-testing/TIME_Software/sftp/mce0_sftp.py &'], shell=True)
    subprocess.Popen(['ssh -T time-mce-1 python /home/time/time-software-testing/TIME_Software/sftp/mce1_sftp.py &'], shell=True)

    dir = 'home/time/time-software-testing/TIME_Software/'
    if os.path.exists(dir + 'tempfiles/tempparameters.txt') :
        parafile = open(dir + 'tempfiles/tempparameters.txt', 'w')
        parafile.write(str(self.datamode)+' ')
        parafile.write(str(self.readoutcard)+' ')
        parafile.write(self.framenumber+' ')
        parafile.write(self.datarate+' ')
        parafile.close()

    subprocess.Popen(['python /home/time/time-software-testing/TIME_Software/main/start_gui.py %s %s %s %s %s &' %(readoutcard, framenumber, frameperfile, datarate, datamode)], shell=True)

if __name__ == '__main__':
    main(sys.argv[1],sys.argv[2],sys.argv[3],sys.argv[4],sys.argv[5])
