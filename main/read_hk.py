def hk_read(self,num_hk,hk):
    k = 0
    n = 0
    for i in range(num_hk -1):
        file = gzip.open(hk[i])
        name = []
        data = []
        time = []
        # print(colored("name %s" %(name),'red'))
        for line in file:
            fields = line.strip().split(",")
            t_type = str(fields[0])
            name1 = str(fields[2])
            name2 = str(fields[3])
            names = (name1 + "_" + name2).replace('"','')
            if t_type == 't': # want to keep exact sync box value
                sync = float(fields[1])
                tele_time = [float(fields[1]),names.replace(' ','_'),float(fields[4])]
            else :
                time.append(int(fields[1]))
                name.append(names.replace(' ','_'))
                data.append(float(fields[4]))
                tele_time = [0,'',0]

        #==============================================
        ''' Routine for Sorting Data by Time Index '''
        #==============================================
        sort_name = [x for _,x in sorted(zip(time,name))]
        sort_data = [x for _,x in sorted(zip(time,data))]
        sort_time = sorted(time)
        #==============================================
        print(len(time))
        # only want to append one line at a time to check for new variables
        for i in range(len(time)-1):
            time = sort_time[i]
            name = sort_name[i]
            data = sort_data[i]

            # only incremment index for a new timestamp,not for file num or for t =======
            if k == 0 :
                new_time = time
            if new_time == time:
                pass
            elif new_time != time :
                n += 1
                new_time = time
            k += 1

            self.append_data()
        k = 0
        print(colored("End of HK Files List",'yellow'))

        # remove the hk file that was just read
        subprocess.Popen(['rm %s' %(hk[i])], shell=True)
            #===============================================================
    return
