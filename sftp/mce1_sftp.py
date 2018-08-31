import os
import subprocess
import time
import shutil
import sys

def main():
    a = 0
    while True:
        files = [os.path.join('/data/cryo/current_data', x) for x in os.listdir('/data/cryo/current_data')]
        oldest = min(files,key=os.path.getctime)
        print('sftp: %s' % (a))
        subprocess.Popen(['scp', oldest, 'time-master:/home/time/Desktop/time-data/mce1/%s' %(oldest)]).wait()
        delete_file = ['rm %s' %(oldest)]
        subprocess.Popen(delete_file, shell=True)
        a = a + 1

        # mce_file = os.path.exists("/data/cryo/current_data/temp.%0.3i" %(a+1)) #wait to read new file until old file is complete
        # if mce_file:
        #     #shutil.move('/data/cryo/current_data/temp.%0.3i' % (a), 'pilot1@time.rit.edu:/home/pilot1/ssh_stuff/mce1/temp.%0.3i' % (a))
        #     print('sftp: %s' % (a))
        #     mce_file_name = '/data/cryo/current_data/temp.%0.3i' % (a)
        #     if a == 1:
        #         subprocess.Popen(['scp', '/data/cryo/current_data/temp.run',  'time-master:/home/time/Desktop/time-data/mce1/temp.run']).wait()
        #         delete_file = ['rm %s' % ('/data/cryo/current_data/temp.run')]
        #         subprocess.Popen(delete_file,shell=True)
        #     subprocess.Popen(['scp', mce_file_name,  'time-master:/home/time/Desktop/time-data/mce1/temp.%0.3i' % (a)]).wait()
        #     delete_file = ['rm %s' % (mce_file_name)]
        #     subprocess.Popen(delete_file,shell=True)
        #     a += 1
        else:
            print("no new files, exiting")
            sys.exit()

if __name__ == '__main__':
    main()
