import os
import subprocess
import time
import shutil
import sys

def main():
    a = 0
    print("starting sftp")
    path = '/data/cryo/current_data/'
    time.sleep(1.0)
    while True:
        if os.path.exists(path + 'temp.run') :
            if a == 0 :
                subprocess.Popen(['scp', path + 'temp.run', 'time-master:~/time/Desktop/time-data/mce1/temp.run'])
            if os.path.exists('/data/cryo/current_data/temp.001') :
                a = 1
                subprocess.Popen(['scp', path + 'temp.%0.3i' %(a-1), 'time-master:~/time/Desktop/time-data/mce1/%s' %(path + 'temp.%0.3i' %(a-1))])
                subprocess.Popen(['rm' , x], shell=True)
            elif os.path.exists('/data/cryo/current_data/temp.%0.3i' %(a)) :
                subprocess.Popen(['scp', path + 'temp.%0.3i' %(a-1), 'time-master:~/time/Desktop/time-data/mce1/%s' %(path + 'temp.00%0.3i' %(a-1))])
                subprocess.Popen(['rm' , x], shell=True)
                a = a + 1
            else :
                pass
                print('waiting for new files')

        else :
            pass
            print('temp.run does not exist')

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
