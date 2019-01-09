# TIME_Software

*Read_Files.py Assumptions*

  1.) HK files indexer, self.n , only increments based on the timestamp contained within the file. This means that each sensor will only have one data value reported for each entry. This also means that the mce files are incremented differently in the same netcdf file. 

  2.) MCE indexing assumes both mces are spitting out the same number of files each time the directory is checked.
  
  3.) Both MCE and HK share the same unlimited time dimension within the netcdf file. Since HK is sampled first, it can build up the value of "t" to close to 20. When MCE data is appended afterwards, that value is reset back to 0, and then incremented again. This value is continually flip-flopped between the two, and may present problems with reading multiple files in as one data variable. This is necessary because the files for MCE and HK are not parsed synchronously, but one at a time. 

  4.) The same function is used to append data for both MCE and HK data. As such, it is necessary to save all data as class variables that can be accessed by the function in order to prevent problems with passing different numbers of variables for each case. 
  
  
