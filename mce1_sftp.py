import os
<<<<<<< HEAD
import subprocess
import time
import shutil
import sys
import datetime as dt

def main():
    dir = '/data/cryo/current_data/'
    print '------- Starting Data Transfer -------'
    a = 0
    begin = dt.datetime.utcnow()
    end = dt.datetime.utcnow()
    while end - begin < dt.timedelta(seconds=5):
        if os.path.exists("/data/cryo/current_data/temp.%0.3i" %(a+1)) :
            mce_file_name = '/data/cryo/current_data/temp.%0.3i' %(a)
            if a == 0:
                subprocess.Popen(['scp', '/data/cryo/current_data/temp.run', 'pilot1@time.rit.edu:/home/pilot1/Desktop/time-data/mce1/temp.run']).wait()
                #subprocess.Popen(['rm %s' % ('/data/cryo/current_data/temp.run')],shell=True)
            if os.path.exists(mce_file_name):
                subprocess.Popen(['scp', mce_file_name, 'pilot1@time.rit.edu:/home/pilot1/Desktop/time-data/mce1/temp.%0.3i' % (a)]).wait()
                subprocess.Popen(['rm %s' % (mce_file_name)],shell=True)
                #print 'File Transfered :' , mce_file_name.replace(dir,'')
                a += 1
                begin = dt.datetime.utcnow()

            else :
                print "File Doesn't Exist"
        end = dt.datetime.utcnow()
    else :
        print 'File Transfer Stopped'
        #subprocess.Popen(['rm temp*'],shell=True)
        #subprocess.Popen(['rm /data/cryo/current_data/temp*'],shell=True)
        subprocess.Popen(["ssh -t pilot1@time.rit.edu 'pkill -f /home/pilot1/time-software/main/read_files.py'"],shell=True)
        print 'File Read Stopped'
        sys.exit()

if __name__ == '__main__':
    main()
=======
import subproces
import time
import shutil
import sys

def main(a, n_files):
    a = int(a)
    print('Hello!')
    while True:
        mce_file = os.path.exists("/data/cryo/current_data/temp.%0.3i" %(a+1)) #wait to read new file until old file is complete
        if mce_file:
            while mce_file:
                #shutil.move('/data/cryo/current_data/temp.%0.3i' % (a), 'pilot1@time.rit.edu:/home/pilot1/ssh_stuff/mce1/temp.%0.3i' % (a))
                print('sftp: %s' % (a))
                mce_file_name = '/data/cryo/current_data/temp.%0.3i' % (a)
                if os.path.exists(mce_file_name):
                    if a == 1:
                        subprocess.Popen(['scp', '/data/cryo/current_data/temp.run',  'pilot1@time.rit.edu:/home/pilot1/netcdf_stuff/mce1/temp.run']).wait()
                        delete_file = ['rm %s' % ('/data/cryo/current_data/temp.run')]
                        subprocess.Popen(delete_file,shell=True)
                    subprocess.Popen(['scp', mce_file_name,  'pilot1@time.rit.edu:/home/pilot1/netcdf_stuff/mce1/temp.%0.3i' % (a)]).wait()
                    delete_file = ['rm %s' % (mce_file_name)]
                    subprocess.Popen(delete_file,shell=True)
                    a += 1
                    mce_file = os.path.exists("/data/cryo/current_data/temp.%0.3i" %(a+1))
                else:
                    pass
            sys.exit(a)
        else:
            pass
'''
need some good way to stop this process from happening at the end of the gui
maybe put in a wait for 10 seconds timer and then if newfile isn't found, just give up on it
'''
if __name__ == '__main__':
    main(sys.argv[1], sys.argv[2])
>>>>>>> 90b20bd24383c06be5e1b1ad88a415c489224619
