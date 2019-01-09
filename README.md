# TIME_Software

*Read_Files.py Assumptions*

  1.) HK files indexer, self.n , only increments based on the timestamp contained within the file. This means that each sensor will only have one data value reported for each entry. This also means that the mce files are incremented differently in the same netcdf file. 

  2.) MCE indexing assumes both mces are spitting out the same number of files each time the directory is checked.
