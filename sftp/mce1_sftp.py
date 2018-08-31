import os
import subprocess
import time
import shutil
import sys

def main():
    a = 0
    l = 0
    print("starting sftp")
    path = '/data/cryo/current_data/'
    time.sleep(1.0)
    while a < 100:
        if os.path.exists(path + 'temp.run') :
            if a == 0 :
                subprocess.Popen(['scp', path + 'temp.run', 'time-master:~/time/Desktop/time-data/mce1/temp.run'])
                print('temp.run transfered')
            if os.path.exists('/data/cryo/current_data/temp.%0.3i' %(a)) :
                a = a + 1
                l = l + 1
                subprocess.Popen(['scp', path + 'temp.%0.3i' %(a-1), 'time-master:~/time/Desktop/time-data/mce1/%s' %(path + 'temp.%0.3i' %(a-1))])
                delete_file = ['rm %s' %(path + 'temp.%0.3i' %(a-1))]
                subprocess.Popen(delete_file, shell=True)
                print('files transfered')

            else :
                pass
                print('waiting for new files')
                l = l + 1

        else :
            pass
            print('temp.run does not exist')
            l = l + 1

# mce_file = os.path.exists("/data/cryo/current_data/temp.%0.3i" %(a+1)) #wait to read new file until old file is complete
# if mce_file:
#     print('sftp: %s' % (a))
#     mce_file_name = '/data/cryo/current_data/temp.%0.3i' % (a)
#     if a == 1:
#         subprocess.Popen(['scp', '/data/cryo/current_data/temp.run',  'time-master:/home/time/Desktop/time-data/mce1/temp.run'])
#         delete_file = ['rm %s' % ('/data/cryo/current_data/temp.run')]
#         subprocess.Popen(delete_file,shell=True)
#     subprocess.Popen(['scp', mce_file_name,  'time-master:/home/time/Desktop/time-data/mce1/temp.%0.3i' % (a)])
#     delete_file = ['rm %s' % (mce_file_name)]
#     subprocess.Popen(delete_file,shell=True)
#     a += 1

if __name__ == '__main__':
    main()
