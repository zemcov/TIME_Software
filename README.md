# TIME_Software

*Read_Files.py Assumptions*

  1.) There are 4 different time keepers within this file. <br>
    a) **self.a** is a general timekeeper which only increments after all of the currently found mce and hk files have been parsed. It is used in multiple locations to check for when the first instance of each function is being run, as many things need to be defined the first run through.<br>
    b) **self.p** is the mce file read timekeeper, and increments every time a mce0 and mce1 file have both been parsed. It is used to append data into the netcdf files in the correct array index location. For exampmle, if it is the first file appended, then all data pertaining to that read file while be placed in MCE0_Raw_Data_All[0;;;] = data, and self.p == 0. <br>
    c) **self.n** is the hk file read timekeeper, and increments only after a new HK timestamp has been detected. This provides a simulated timestream of data, where data is only appended in the order in which the sensors have reported. When data is read back, seconds will be empty where other values had been reported, but not that particular sensor. This is due to the varying frequencies of the different sensors. <br>
    d) **self.k** is used to keep track of when a new HK file is being read so that the timekeeper self.n may be reset. It is incremented in the HK_Read function after each line of data is appended. <br>

  2.) MCE indexing assumes both mces are spitting out the same number of files each time the directory is checked. <br>

  3.) Both MCE and HK share the same unlimited time dimension within the netcdf file. Since HK is sampled first, it can build up the value of "t" to close to 20. When MCE data is appended afterwards, that value is reset back to 0, and then incremented again. This value is continually flip-flopped between the two, and may present problems with reading multiple files in as one data variable. This is necessary because the files for MCE and HK are not parsed synchronously, but one at a time. <br>

  4.) The same function is used to append data for both MCE and HK data. As such, it is necessary to save all data as class variables that can be accessed by the function in order to prevent problems with passing different numbers of variables for each case. <br>

*Device Communication Scripts*
  **mce0_run.sh , mce1_run.sh**
      Activates either MCE0 or MCE1 by sending the name of the temporary files "temp" , how many readout cards to activate, how many frames to collect, and how many frames should be appended into each temp file.

  **mce0_del.sh , mce1_del.sh**
      Removes any built up temp files not transferred to GUI computer. These will always be located in /data/cryo/current_data. Typically called at the start and end of each GUI activation.

  **mce0_cdm.sh , mce1_cdm.sh**
      

*Data Transfer Scripts*
