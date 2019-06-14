#!/usr/bin/python
# use this to program the parameters in the software

tel_dict = {

"inittel":"No",
"tel_scan":"2D Raster",
"coord_space":"DEC",
"map_angle":"0",
"sec":"10",
"map_size":"1",
"map_size_unit":"deg",
"map_len":"1", #only need for 2D map
"map_len_unit":"deg",
"map_angle":"0",
"map_angle_unit":"deg",
"step":"0.05",
"step_unit":"deg",
"coord1":"2:00:00",
"coord1_unit":"RA",
"coord2":"15:00:00",
"coord2_unit":"DEC",
"epoch":"Apparent",
"object":"Mars"
}
# ===================================
mce_dict = {

"observer":"VLB",
"mceson":"MCE SIM",
"datamode":"Error",
"readoutcard":"All",
"framenumber":"1350000",
"alpha":"0.1",
"channeldelete":"No",
"timeinterval":"120",
"showmcedata":"Yes"

}


netcdf_dir = '/data/netcdffiles/%s" % (ut.new_dir)' #the directory for the netcdf files
master_dir = '/home/time/time-software-testing/TIME_Software/main/' # the main directory for the time software ex: path/to/TIME_Software/main/
mce0_dir = '/home/time_user/Desktop/time-data/mce1/' #the directory where you want to store mce0 data
mce1_dir = '/home/time_user/Desktop/time-data/mce2/' #the directory where you want to store mce1 data
temp_dir = '/home/time_user/TIME_Software/main/tempfiles/' #the directory for tempfiles ex: path/to/TIME_Software/main/tempfiles/ 
hk_dir = '/home/time_user/Desktop/time-data/hk/' #the directory where you want to store hk data
