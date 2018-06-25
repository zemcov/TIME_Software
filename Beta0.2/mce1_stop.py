import pyqtgui

def mce1_stop(commmand,readoutcard):
    process = subprocess.Popen(command %(readoutcard),stdout=subprocess.PIPE, shell=True)
    proc_stdout = process.communicate()[0].strip()
    print proc_stdout

mce1_stop('sshpass -p "time-pilot2" ssh -o StrictHostKeyChecking=no\
   pilot2@timemce.rit.edu;mce_cmd -x stop rc%s ret_dat',self.readoutcard)
