import time as t
import gzip, os
import datetime as dt
from termcolor import colored
import numpy as np
import utils as ut
import sys

dir = '/home/time/Desktop/time-data/netcdffiles/'
name_dict = None
print(colored('hk #-1','red'))
def loop_files(queue3):
    while not ut.mce_exit.is_set():
        files = [dir + x for x in os.listdir(dir) if x.startswith("omnilog")]
        for i in range(len(files)):
            print(colored('hk #0','red'))
            mega_data, name_dict = hk_read(files[i])
            queue3.send([mega_data])
            #remove the hk file that was just read
            subprocess.Popen(['rm %s' %(files[i])], shell=True)
            f = open(dir + '/hk_dict.txt','w')
            f.write(str(name_dict))
            f.close()
    sys.exit()

def hk_read(hk):
    k = 0
    n = 0
    mega_hk = []
    name = []
    data = []
    time = []
    print(colored('hk #1','red'))
    file = gzip.open(hk)

    for line in file:
        fields = line.strip().split(",")
        t_type = str(fields[0])
        name1 = str(fields[2])
        name2 = str(fields[3])
        names = (name1 + "_" + name2).replace('"','')
        time.append(float(fields[1]))
        name.append(names.replace(' ','_'))
        data.append(float(fields[4]))
        if names.replace(' ','_') == 'HKMBv1b0_SYNC_number' :
            ut.timing(time,data)
    print(colored('hk #2','red'))
    # makng dict entry for name as integer ====================================
    if os.path.exists(dir + '/hk_dict.txt'): # if we already have a saved dictionary
        f = open(dir + '/hk_dict.txt','r')
        dict_data = f.read()
        f.close()
        name_dict = eval(dict_data)
        for i in range(len(name)):
            if name[i] not in name_dict.values():
                    name_dict.update({len(name_dict)+1:name[i]})

    else :
        master_names = []
        for i in range(len(name)):
            if name[i] not in master_names:
                master_names.append(name[i])
        name_num = np.arange(0.0,len(master_names),1.0)
        name_dict = dict(zip(name_num,master_names))

    print(colored('hk #3','red'))
    # =========================================================================

    #==============================================
    ''' Routine for Sorting Data by Time Index '''
    #==============================================
    sort_name = [x for _,x in sorted(zip(time,name))]
    sort_data = [x for _,x in sorted(zip(time,data))]
    sort_time = sorted(time)
    #==============================================
    # loop through and append to final array until new time index is found
    for i in range(len(time)-1):
        # change all hk sensor names to integers for storage
        num = int(name_dict.keys()[name_dict.values().index(sort_name[i])])
        sort_name[i] = float(num)
        # only incremment index for a new timestamp,not for file num or for t =======
        if k == 0 : # if start of a new file...
            new_time = sort_time[i]
            time = [0]*215
            name = [0]*215
            data = [0]*215
            time[num] = sort_time[i]
            name[num] = sort_name[i]
            data[num] = sort_data[i]
            k += 1
            continue # makes it skip the rest of the if statements

        elif new_time == sort_time[i]:
            time[num] = sort_time[i]
            name[num] = sort_name[i]
            data[num] = sort_data[i]

        elif new_time != sort_time[i] :
            # append array to netcdf data if new timestamp is found
            new_time = sort_time[i]
            # ==================================================================
            if len(name_dict) <= 215 : # make sure num of sensors isn't over array limit
                hk_data = np.array((time,name,data)) # make monolithic array, only of one timestamp
                mega_hk.append(hk_data)
            else :
                print(colored("Number of reported sensors over size limit!",'red'))

            time = [0]*215
            name = [0]*215
            data = [0]*215
            time[num] = sort_time[i]
            name[num] = sort_name[i]
            data[num] = sort_data[i]
            n += 1
            # ==================================================================
    k = 0
    print(colored("End of HK Files List",'yellow'))

    # send data to append_data
    return mega_data, name_dict
        #===============================================================
