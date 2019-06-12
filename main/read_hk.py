import time as t
import gzip, os, sys, subprocess
import datetime as dt
from termcolor import colored
import numpy as np
import utils as ut
import init

class HK_Reader :

    def __init__(self,offset):
        self.dir = init.hk_dir
        self.dir2 = init.netcdf_dir
        self.name_dict = None
        self.n = 0
        self.bad_counter = 0
        self.time_tuple = [0,0]
        self.offset = offset

    def loop_files(self,queue3):
        while True : #force it to wait until files exist before continuing
            files = [self.dir + x for x in os.listdir(self.dir) if x.startswith("omnilog")]
            if len(files) != 0 :
                hk_file = min(files, key = os.path.getctime) # grab the oldest of the unparsed files
                a = int(hk_file.replace(self.dir,'').replace('omnilog.','').replace('.txt.gz',''))
                print(colored('HK starting file = %i' %(a),'green'))
                sys.stdout.flush()
                break
            else :
                t.sleep(0.01)

        while not ut.mce_exit.is_set():
            if os.path.exists(self.dir + "omnilog.%i.txt.gz" %(a+1)) : #wait to read new file until old file is complete
                hk_file = self.dir + 'omnilog.%i.txt.gz' % (a)
                a += 1
                mega_hk = self.hk_read(hk_file)
                queue3.send([mega_hk,self.time_tuple])
                subprocess.Popen(['rm %s' %(hk_file)], shell=True)
                self.n += 1
            else :
                t.sleep(0.01)

        print('Num of Bad HK Files: %s' %(self.bad_counter))
        sys.exit()

    def hk_read(self,hk):
        mega_hk = []
        name = []
        data = []
        time = []
        file = gzip.open(hk)
        try :
            for line in file:
                fields = line.strip().split(",")
                t_type = str(fields[0])
                time_stamp = float(fields[1])
                name1 = str(fields[2])
                name2 = str(fields[3])
                names = (name1 + "_" + name2).replace('"','')
                name.append(names.replace(' ','_'))
                # ============================================================================================
                if t_type == 't' and names != 'HKMBv1b0_SYNC_number' and names != 'HKMBv2b0_SYNC_number':

                    if self.offset.value != 0.0 :
                        sync_time = ut.utc_to_sync(time_stamp,self.offset) # check to see if offset has been set
                        time.append(float(sync_time))
                        data.append(float(fields[4]))
                    else :
                        time.append(float(time_stamp)) # this won't go into file anyway, so doesn't matter what it does
                        data.append(float(fields[4]))

                elif t_type == 't' and names == 'HKMBv1b0_SYNC_number':
                    time.append(float(fields[4])) # append sync number as timestamp, rather than network time
                    data.append(float(time_stamp))
                    with self.offset.get_lock():
                        self.offset.value = ut.timing(float(fields[1]),float(fields[4]))
                        print(colored((fields[1],fields[4]),'magenta'))
                        print(colored('Offset: %s , %s' %(float(fields[1]),self.offset.value),'red'))
                        sys.stdout.flush()
                    self.time_tuple[0] = time[-1]
                    self.time_tuple[1] = data[-1]

                elif t_type == 't' and names == 'HKMBv2b0_SYNC_number' :
                    time.append(float(fields[4]))
                    data.append(float(time_stamp))

                else :
                    time.append(float(time_stamp))
                    data.append(float(fields[4]))
                # ==============================================================================================

        except IOError:
            print(colored('HK FILE CORRUPT! %s' %(file),'red'))
            self.bad_counter += 1

        # makng dict entry for name as integer ====================================
        """
            Creating a Dictionary of HK Sensors
            :return: writes dictionary to file (.txt)
        """
        if self.n == 0 :
            if os.path.exists(self.dir2 + '/hk_dict.txt'): # if we already have a saved dictionary :
                f = open(self.dir2 + '/hk_dict.txt','r')
                dict_data = f.read()
                f.close()
                self.name_dict = eval(dict_data)
                for i in range(len(name)):
                    if name[i] not in self.name_dict.values():
                            self.name_dict.update({len(self.name_dict.keys())+1.0:name[i]})
            else :
                master_names = []
                for i in range(len(name)):
                    if name[i] not in master_names:
                        master_names.append(name[i])
                name_num = np.arange(0.0,len(master_names),1.0)
                self.name_dict = dict(zip(name_num,master_names))

        else :
            for i in range(len(name)):
                if name[i] not in self.name_dict.values():
                        self.name_dict.update({len(self.name_dict.keys())+1.0:name[i]})
        # =========================================================================
        f = open(self.dir2 + '/hk_dict.txt','w')
        f.write(str(self.name_dict))
        f.close()

        #==============================================
        '''
            Routine for Sorting Data by Time Index
            :return: mega_hk
        '''
        sort_name = [x for _,x in sorted(zip(time,name))]
        sort_data = [x for _,x in sorted(zip(time,data))]
        sort_time = sorted(time)
        #==============================================
        # loop through and append to final array until new time index is found
        l = 0
        for i in range(len(sort_time)-1):
            # change all hk sensor names to integers for storage
            # num = int(self.name_dict.keys()[self.name_dict.values().index(sort_name[i])])
            for k,v in self.name_dict.iteritems():
                if v == sort_name[i] :
                    num = int(k)
                    val = v
            sort_name[i] = float(num)

            # only incremment index for a new timestamp,not for file num or for t =======
            if l == 0 : # if start of a new time (or new file)
                new_time = sort_time[i]
                time2 =  np.zeros(500)
                names2 = np.zeros(500)
                data2 = np.zeros(500)
                time2[num] = sort_time[i]
                names2[num] = float(sort_name[i])
                data2[num] = sort_data[i]
                l += 1

            else :
                if new_time == sort_time[i]:
                    time2[num] = sort_time[i]
                    names2[num] = float(sort_name[i])
                    data2[num] = sort_data[i]

                else :
                    new_time = sort_time[i]
                    l = 0 # reset timer for new timestamp
                    # ==================================================================
                    if len(self.name_dict.keys()) <= 500 : # make sure num of sensors isn't over array limit
                        hk_data = np.array((time2,names2,data2)) # make monolithic array, only of one timestamp
                        mega_hk.append(hk_data)

                    else :
                        print(len(self.name_dict.keys()))
                        print(colored("Number of reported sensors over size limit!",'red'))

                    time2 = np.zeros(500)
                    names2 = np.zeros(500)
                    data2 = np.zeros(500)
                    time2[num] = sort_time[i]
                    names2[num] = float(sort_name[i])
                    data2[num] = sort_data[i]
                    # ==================================================================
        # send data to append_hk
        return mega_hk
        #===============================================================
