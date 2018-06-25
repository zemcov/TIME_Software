import pyqtgui

def mce1_start(commmand,framenumber,readoutcard,frameperfile):
    process = subprocess.Popen(command %(framenumber,frameperfile),stdout=subprocess.PIPE, shell=True)
    proc_stdout = process.communicate()[0].strip()
    print proc_stdout

mce1_start('sshpass -p "time-pilot2" ssh -o StrictHostKeyChecking=no\
   pilot2@timemce.rit.edu ; mce_run temp %s %s --sequence=%s',self.framenumber\
   self.readoutcard,self.frameperfile)
